"""
Data gathering script for Lightning AI.
Downloads: Sentinel-2 tiles (5 Indian cities) + OSM road masks.
Run once before training.

Usage:
    python scripts/gather_data.py [--cities all] [--out data/raw]
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.data.city_config import load_all
from src.data.sentinel_dl import download_city


def download_osm_mask(city_id: str, bbox: list, out_dir: Path):
    """Download OSM road graph and rasterize to binary mask GeoTIFF."""
    import osmnx as ox
    import numpy as np
    import rasterio
    from rasterio.transform import from_bounds
    from rasterio.features import rasterize
    from shapely.geometry import mapping

    mask_path = out_dir / "osm_road_mask.tif"
    graph_path = out_dir / "osm_graph.graphml"

    if mask_path.exists() and graph_path.exists():
        print(f"  [skip] OSM already downloaded for {city_id}")
        return

    south, west, north, east = bbox[0], bbox[1], bbox[2], bbox[3]

    print(f"  Downloading OSM graph for {city_id}...")
    G = ox.graph_from_bbox(north, south, east, west, network_type="drive")
    ox.save_graphml(G, graph_path)

    # Rasterize roads to 512x512 binary mask
    H, W = 512, 512
    transform = from_bounds(west, south, east, north, W, H)

    edges = ox.graph_to_gdfs(G, nodes=False)
    shapes = [(mapping(geom), 1) for geom in edges.geometry]

    mask = rasterize(
        shapes,
        out_shape=(H, W),
        transform=transform,
        fill=0,
        dtype="uint8",
    )

    profile = {
        "driver": "GTiff",
        "dtype": "uint8",
        "width": W,
        "height": H,
        "count": 1,
        "crs": "EPSG:4326",
        "transform": transform,
    }
    with rasterio.open(mask_path, "w", **profile) as dst:
        dst.write(mask, 1)

    print(f"  OSM mask saved: {mask_path}  (road pixels: {mask.sum()})")


def tile_for_training(city_id: str, city_dir: Path, tile_dir: Path, tile_size=512):
    """Slice sentinel RGB + OSM mask into paired tiles for training."""
    import numpy as np
    import rasterio
    from rasterio.windows import Window

    img_paths = {
        "red":   city_dir / "red.tif",
        "green": city_dir / "green.tif",
        "blue":  city_dir / "blue.tif",
    }
    mask_path = city_dir / "osm_road_mask.tif"

    if not all(p.exists() for p in img_paths.values()):
        print(f"  [skip tiling] Sentinel bands missing for {city_id}")
        return
    if not mask_path.exists():
        print(f"  [skip tiling] OSM mask missing for {city_id}")
        return

    img_dir = tile_dir / "images"
    msk_dir = tile_dir / "masks"
    img_dir.mkdir(parents=True, exist_ok=True)
    msk_dir.mkdir(parents=True, exist_ok=True)

    with rasterio.open(img_paths["red"]) as src:
        H, W = src.height, src.width

    count = 0
    for row in range(0, H - tile_size + 1, tile_size):
        for col in range(0, W - tile_size + 1, tile_size):
            window = Window(col, row, tile_size, tile_size)
            bands = []
            for band in ["red", "green", "blue"]:
                with rasterio.open(img_paths[band]) as src:
                    data = src.read(1, window=window).astype(np.float32)
                    # normalize to 0-255
                    data = np.clip(data / 3000.0 * 255, 0, 255).astype(np.uint8)
                    bands.append(data)

            rgb = np.stack(bands, axis=0)  # (3, H, W)

            with rasterio.open(mask_path) as src:
                mask = src.read(1, window=window)

            prefix = f"{city_id}_{row:04d}_{col:04d}"
            np.save(img_dir / f"{prefix}.npy", rgb)
            np.save(msk_dir / f"{prefix}.npy", mask)
            count += 1

    print(f"  Tiled {city_id}: {count} tiles → {tile_dir}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cities", default="all", help="comma-separated city ids or 'all'")
    parser.add_argument("--out", default="data/raw", help="output base directory")
    parser.add_argument("--tiles", default="data/tiles", help="tiled training data dir")
    parser.add_argument("--skip-sentinel", action="store_true")
    parser.add_argument("--skip-osm", action="store_true")
    parser.add_argument("--skip-tiling", action="store_true")
    args = parser.parse_args()

    out_base = ROOT / args.out
    tile_base = ROOT / args.tiles

    all_cities = load_all()

    if args.cities == "all":
        selected = list(all_cities.keys())
    else:
        selected = [c.strip() for c in args.cities.split(",")]

    print(f"Cities: {selected}")
    print(f"Output: {out_base}")
    print("-" * 50)

    for city_id in selected:
        if city_id not in all_cities:
            print(f"[warn] Unknown city: {city_id}, skipping")
            continue

        city = all_cities[city_id]
        city_dir = out_base / city_id
        city_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n[{city_id.upper()}] {city.name}")

        if not args.skip_sentinel:
            print(f"  Downloading Sentinel-2...")
            try:
                meta = download_city(city_id, city.bbox, str(city_dir))
                print(f"  Sentinel-2 done: {meta['width']}x{meta['height']} px")
            except Exception as e:
                print(f"  [ERROR] Sentinel-2 failed: {e}")

        if not args.skip_osm:
            try:
                download_osm_mask(city_id, city.bbox, city_dir)
            except Exception as e:
                print(f"  [ERROR] OSM failed: {e}")

        if not args.skip_tiling:
            tile_for_training(city_id, city_dir, tile_base / city_id)

    print("\n" + "=" * 50)
    print("Data gathering complete.")
    print(f"Training tiles at: {tile_base}")
    print("\nNext step:")
    print("  python scripts/train.py --data data/tiles")


if __name__ == "__main__":
    main()
