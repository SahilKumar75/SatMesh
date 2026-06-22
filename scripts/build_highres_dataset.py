#!/usr/bin/env python3
"""Build a HIGH-RES Indian road dataset: Esri World Imagery + OSM masks.

Unlike prepare_india_dataset.py (10 m Sentinel-2, where lanes are sub-pixel), this
fetches ~0.3-0.6 m Esri World Imagery XYZ tiles where dense urban streets, colony
lanes and gullies ARE visible, and rasterizes OSM road vectors (all classes) into
pixel-aligned masks. Output: *_sat.jpg / *_mask.png pairs for fine-tuning the
0.5 m DeepGlobe model (v2). Everything is auto-labelled (no manual annotation).

How alignment works: Esri tiles are Web-Mercator (EPSG:3857). For each sampled
window we know its exact Mercator bounds, so OSM roads (fetched in lat/lon,
reprojected to 3857) rasterize pixel-perfectly onto the image.

Full cities at z18 would be millions of tiles, so we sample K random windows per
region (each a GxG tile block) and fetch OSM once per region.

Needs internet (Esri tiles + OSM Overpass) — run on Colab / Kaggle-with-internet.

Example:
    python scripts/build_highres_dataset.py --regions all --zoom 18 \
        --windows 25 --out data/india_highres/train
"""
import argparse
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

ESRI = ("https://server.arcgisonline.com/ArcGIS/rest/services/"
        "World_Imagery/MapServer/tile/{z}/{y}/{x}")
ORIGIN = 20037508.342789244  # half the Web-Mercator extent, metres


def deg2tile(lat, lon, z):
    """lat/lon -> fractional XYZ tile coords at zoom z."""
    n = 2 ** z
    xt = (lon + 180.0) / 360.0 * n
    yt = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
    return xt, yt


def tile_merc_bounds(rx, ry, g, z):
    """Mercator bounds (w,s,e,n) of a gxg tile block whose top-left is (rx,ry)."""
    tm = 2 * ORIGIN / (2 ** z)
    return (-ORIGIN + rx * tm, ORIGIN - (ry + g) * tm,
            -ORIGIN + (rx + g) * tm, ORIGIN - ry * tm)


def fetch_window(rx, ry, g, z, session, pause=0.03):
    """Download + stitch a gxg Esri tile block; return (rgb HxWx3 uint8, merc_bounds)."""
    import numpy as np
    import cv2
    mosaic = np.zeros((g * 256, g * 256, 3), np.uint8)
    hdr = {"User-Agent": "SatMesh/1.0 (BAH2026 research)"}
    for j in range(g):
        for i in range(g):
            url = ESRI.format(z=z, x=rx + i, y=ry + j)
            for _ in range(3):
                try:
                    r = session.get(url, timeout=20, headers=hdr)
                    if r.ok and r.content:
                        arr = cv2.imdecode(np.frombuffer(r.content, np.uint8),
                                           cv2.IMREAD_COLOR)
                        if arr is not None:
                            mosaic[j*256:(j+1)*256, i*256:(i+1)*256] = \
                                cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
                        break
                except Exception:
                    time.sleep(0.5)
            time.sleep(pause)
    return mosaic, tile_merc_bounds(rx, ry, g, z)


def rasterize_window(roads_merc, merc_bounds, shape, buffer_px=3):
    """Rasterize pre-reprojected OSM roads onto a mask aligned to the window."""
    import numpy as np
    from rasterio.features import rasterize
    from rasterio.transform import from_bounds
    from shapely.geometry import mapping
    h, w = shape
    mw, ms, me, mn = merc_bounds
    px_m = (me - mw) / w                      # metres per pixel in this window
    buffered = roads_merc.buffer(buffer_px * px_m)
    transform = from_bounds(mw, ms, me, mn, w, h)
    geoms = [mapping(g) for g in buffered if not g.is_empty]
    if not geoms:
        return np.zeros((h, w), np.uint8)
    return rasterize(geoms, out_shape=(h, w), transform=transform,
                     fill=0, default_value=255, dtype="uint8")


def tile_and_write(rgb, mask, prefix, out_dir, tile=512, min_road_frac=0.01,
                   keep_empty=0.05):
    import random
    import cv2
    h, w = mask.shape
    n = 0
    for r in range(0, h - tile + 1, tile):
        for c in range(0, w - tile + 1, tile):
            m = mask[r:r + tile, c:c + tile]
            if (m > 127).mean() < min_road_frac and random.random() > keep_empty:
                continue
            img = rgb[r:r + tile, c:c + tile]
            if img.shape[:2] != (tile, tile):
                continue
            s = f"{prefix}_{r}_{c}"
            cv2.imwrite(str(out_dir / f"{s}_sat.jpg"),
                        cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            cv2.imwrite(str(out_dir / f"{s}_mask.png"), m)
            n += 1
    return n


def build_region(cid, cfg, out_dir, z, grid, windows, tile, buffer_px,
                 min_road_frac, session, extra_roads=None):
    import random
    import geopandas as gpd
    import pandas as pd
    from src.data.mask_raster import fetch_osm_roads

    print(f"[{cid}] terrain={cfg.terrain} bbox={cfg.bbox} — OSM roads (all)...", flush=True)
    parts = []
    try:
        # network_type="all" includes service/residential/track/path/footway —
        # i.e. colony lanes and gullies, not just car-drivable roads
        roads = fetch_osm_roads(cfg.bbox, network_type="all")
        if len(roads):
            parts.append(roads.to_crs("EPSG:4326"))
    except Exception as e:
        print(f"[{cid}] OSM fetch failed ({e}) — relying on --road-vectors if any")
    if extra_roads is not None:
        south, west, north, east = cfg.bbox
        clip = extra_roads.cx[west:east, south:north]   # govt/ISRO vectors in this bbox
        if len(clip):
            print(f"[{cid}] + {len(clip)} road features from --road-vectors")
            parts.append(clip)
    if not parts:
        print(f"[{cid}] no roads from any source — skipping")
        return 0
    allroads = gpd.GeoSeries(pd.concat(parts, ignore_index=True), crs="EPSG:4326")
    roads_merc = allroads.to_crs("EPSG:3857")

    south, west, north, east = cfg.bbox
    xt0 = int(math.floor(deg2tile(north, west, z)[0]))
    xt1 = int(math.floor(deg2tile(south, east, z)[0]))
    yt0 = int(math.floor(deg2tile(north, west, z)[1]))
    yt1 = int(math.floor(deg2tile(south, east, z)[1]))
    xt0, xt1 = min(xt0, xt1), max(xt0, xt1)
    yt0, yt1 = min(yt0, yt1), max(yt0, yt1)

    n = 0
    for k in range(windows):
        rx = random.randint(xt0, max(xt0, xt1 - grid))
        ry = random.randint(yt0, max(yt0, yt1 - grid))
        rgb, bounds = fetch_window(rx, ry, grid, z, session)
        mask = rasterize_window(roads_merc, bounds, rgb.shape[:2], buffer_px)
        n += tile_and_write(rgb, mask, f"{cid}_{k}", out_dir, tile, min_road_frac)
    print(f"[{cid}] wrote {n} tiles")
    return n


def _load_regions_file(path):
    """Load a {id: {name, bbox, terrain}} JSON into objects with .bbox/.terrain."""
    import json
    from types import SimpleNamespace
    with open(path) as f:
        raw = json.load(f)
    return {k: SimpleNamespace(bbox=v["bbox"], terrain=v.get("terrain", "urban"),
                               name=v.get("name", k)) for k, v in raw.items()}


def resolve_regions(spec, regions_file=None):
    if regions_file:
        src = _load_regions_file(regions_file)
    else:
        from src.data.city_config import load_all
        src = load_all()
    if spec in (None, "", "none"):
        return {}
    if spec == "all":
        return src
    out = {}
    for cid in [s.strip() for s in spec.split(",") if s.strip()]:
        if cid not in src:
            raise KeyError(f"region '{cid}' not in region source")
        out[cid] = src[cid]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--regions", default="all",
                    help="'all', 'none', or comma-separated region ids")
    ap.add_argument("--regions-file", default="data/train_regions.json",
                    help="JSON of {id:{name,bbox,terrain}}; default = rich 28-region set")
    ap.add_argument("--zoom", type=int, default=18,
                    help="XYZ zoom (18~0.6m, 17~1.2m, 19~0.3m)")
    ap.add_argument("--grid", type=int, default=4, help="tiles per window side (GxG)")
    ap.add_argument("--windows", type=int, default=25, help="random windows per region")
    ap.add_argument("--tile", type=int, default=512, help="output tile size px")
    ap.add_argument("--buffer-px", type=int, default=3, help="road half-width in px")
    ap.add_argument("--road-vectors", default=None,
                    help="comma-separated shapefile/GeoJSON/Parquet of extra road "
                         "lines (e.g. PMGSY GeoSadak, NHAI, Bhuvan) merged with OSM")
    ap.add_argument("--min-road-frac", type=float, default=0.01,
                    help="drop tiles with fewer than this fraction of road pixels")
    ap.add_argument("--out", default="data/india_highres/train")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    import requests
    session = requests.Session()

    extra_roads = None
    if args.road_vectors:
        import geopandas as gpd
        import pandas as pd
        gs = []
        for p in args.road_vectors.split(","):
            g = gpd.read_file(p.strip())
            if g.crs is None:
                g = g.set_crs("EPSG:4326")
            gs.append(g.to_crs("EPSG:4326").geometry)
        extra_roads = gpd.GeoSeries(pd.concat(gs, ignore_index=True), crs="EPSG:4326")
        print(f"loaded {len(extra_roads)} extra road features from {args.road_vectors}")

    total = 0
    for cid, cfg in resolve_regions(args.regions, args.regions_file).items():
        try:
            total += build_region(cid, cfg, out_dir, args.zoom, args.grid,
                                   args.windows, args.tile, args.buffer_px,
                                   args.min_road_frac, session, extra_roads)
        except Exception as e:
            print(f"[{cid}] FAILED: {e}")

    n_pairs = len(list(out_dir.glob("*_sat.jpg")))
    print(f"\nDone. {total} new pairs this run; {n_pairs} total in {out_dir}")
    print("These are 3-channel high-res (RGB) tiles — fine-tune the 3-ch v2 model "
          "(not the 4-ch NIR stage-2 path).")


if __name__ == "__main__":
    main()
