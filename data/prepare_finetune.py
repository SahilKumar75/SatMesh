"""
data/prepare_finetune.py — rasterize OSM road centrelines to binary mask PNGs.

Creates a fine-tuning dataset from local satellite imagery + OSM ground truth,
ready to be consumed by track_a/road_segmentation.py.

Usage:
    python data/prepare_finetune.py \\
        --image_dir  /path/to/sat_tiles/   \\   # GeoTIFFs or georef JPEGs
        --out_dir    data/finetune/         \\
        --buffer_m   3.0                    \\   # road buffer width in metres
        --img_size   512

Output structure:
    data/finetune/
        train/
            <stem>_sat.jpg
            <stem>_mask.png   (binary, 255 = road)
        val/
            ...

Requirements:
    pip install rasterio pyproj osmnx geopandas shapely
"""

from __future__ import annotations
import argparse, os, glob, random, math
from pathlib import Path

import numpy as np
import cv2


def _require(pkg: str):
    try:
        return __import__(pkg)
    except ImportError:
        raise SystemExit(f"Missing dependency: pip install {pkg}")


def _bounds_from_tif(path: str):
    """Return (west, south, east, north) in WGS-84 from a georeferenced raster."""
    rasterio = _require("rasterio")
    from rasterio.crs import CRS
    from pyproj import Transformer

    with rasterio.open(path) as ds:
        b   = ds.bounds
        crs = ds.crs or CRS.from_epsg(4326)

    if crs.to_epsg() == 4326:
        return b.left, b.bottom, b.right, b.top

    to_wgs = Transformer.from_crs(crs, CRS.from_epsg(4326), always_xy=True)
    w, s = to_wgs.transform(b.left,  b.bottom)
    e, n = to_wgs.transform(b.right, b.top)
    return w, s, e, n


def _fetch_roads(west, south, east, north):
    """Download OSM road centrelines for a bounding box."""
    ox = _require("osmnx")
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        G = ox.graph_from_bbox(
            bbox=(north, south, east, west),
            network_type="drive",
            retain_all=False,
        )
    _, edges = ox.graph_to_gdfs(G)
    return edges.geometry  # GeoSeries of LineStrings


def _rasterize_roads(geoms, west, north, pixel_m: float, h: int, w: int,
                     buffer_m: float) -> np.ndarray:
    """Paint road centrelines (buffered) onto an HxW uint8 mask."""
    from shapely.geometry import mapping
    import pyproj
    from pyproj import Transformer

    # degrees-per-metre at this latitude
    lat_mid  = north - (north - (north - h * pixel_m / 111_320)) / 2
    deg_per_m_x = 1.0 / (111_320 * math.cos(math.radians(lat_mid)))
    deg_per_m_y = 1.0 / 111_320

    buf_deg_x = buffer_m * deg_per_m_x
    buf_deg_y = buffer_m * deg_per_m_y
    buf_deg   = (buf_deg_x + buf_deg_y) / 2

    mask = np.zeros((h, w), dtype=np.uint8)

    for geom in geoms:
        buffered = geom.buffer(buf_deg)
        coords_list = []
        if buffered.geom_type == "Polygon":
            coords_list = [list(buffered.exterior.coords)]
        elif buffered.geom_type == "MultiPolygon":
            coords_list = [list(p.exterior.coords) for p in buffered.geoms]

        for ring in coords_list:
            pts = []
            for lon, lat in ring:
                px = int((lon - west)  / (pixel_m * deg_per_m_x))
                py = int((north - lat) / (pixel_m * deg_per_m_y))
                pts.append([px, py])
            if len(pts) >= 3:
                cv2.fillPoly(mask, [np.array(pts, dtype=np.int32)], 255)

    return mask


def process_tile(tif_path: str, out_dir: str, img_size: int, buffer_m: float,
                 pixel_m: float = 0.5) -> bool:
    rasterio = _require("rasterio")
    stem = Path(tif_path).stem

    west, south, east, north = _bounds_from_tif(tif_path)

    # read + resize image
    with rasterio.open(tif_path) as ds:
        data = ds.read([1, 2, 3]) if ds.count >= 3 else np.stack([ds.read(1)] * 3)
    img = np.moveaxis(data, 0, -1).astype(np.uint8)
    img = cv2.resize(img, (img_size, img_size))

    # fetch OSM roads and rasterize
    try:
        roads = _fetch_roads(west, south, east, north)
    except Exception as e:
        print(f"  [skip] OSM fetch failed for {stem}: {e}")
        return False

    mask = _rasterize_roads(roads, west, north, pixel_m, img_size, img_size, buffer_m)

    if mask.sum() == 0:
        print(f"  [skip] no road pixels for {stem}")
        return False

    cv2.imwrite(os.path.join(out_dir, f"{stem}_sat.jpg"),
                cv2.cvtColor(img, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 95])
    cv2.imwrite(os.path.join(out_dir, f"{stem}_mask.png"), mask)
    return True


def main():
    ap = argparse.ArgumentParser(description="Prepare OSM fine-tune dataset from GeoTIFFs")
    ap.add_argument("--image_dir", required=True, help="Directory of input GeoTIFFs")
    ap.add_argument("--out_dir",   default="data/finetune", help="Output directory")
    ap.add_argument("--buffer_m",  type=float, default=3.0,
                    help="Road buffer width in metres for mask rasterization")
    ap.add_argument("--img_size",  type=int, default=512)
    ap.add_argument("--pixel_m",   type=float, default=0.5,
                    help="Ground-sample distance in metres/pixel")
    ap.add_argument("--val_split", type=float, default=0.15)
    ap.add_argument("--seed",      type=int, default=42)
    args = ap.parse_args()

    random.seed(args.seed)

    tifs = sorted(glob.glob(os.path.join(args.image_dir, "*.tif")) +
                  glob.glob(os.path.join(args.image_dir, "*.tiff")))
    if not tifs:
        raise SystemExit(f"No .tif files found in {args.image_dir}")

    random.shuffle(tifs)
    n_val  = max(1, int(len(tifs) * args.val_split))
    splits = {"val": tifs[:n_val], "train": tifs[n_val:]}

    for split, paths in splits.items():
        out = os.path.join(args.out_dir, split)
        os.makedirs(out, exist_ok=True)
        ok = fail = 0
        for p in paths:
            print(f"[{split}] {Path(p).name} … ", end="", flush=True)
            if process_tile(p, out, args.img_size, args.buffer_m, args.pixel_m):
                print("ok"); ok += 1
            else:
                fail += 1
        print(f"  → {split}: {ok} ok, {fail} skipped")

    print(f"\nDone. Fine-tune data written to {args.out_dir}/")
    print("Use with road_segmentation.py by pointing DATA_DIR at data/finetune/train/")


if __name__ == "__main__":
    main()
