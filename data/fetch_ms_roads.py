"""
data/fetch_ms_roads.py — download Microsoft ML Road Detections for India
and clip to a bounding box (e.g. Bengaluru core).

Microsoft releases ML-detected road segments from Bing satellite imagery
as open GeoJSON for many countries including India. These cover narrow
Indian lanes and informal roads that OSM often misses.

Source: https://github.com/microsoft/RoadDetections

Usage:
    python data/fetch_ms_roads.py
    python data/fetch_ms_roads.py --bbox 12.85,77.50,13.05,77.70 --out data/ms_roads_bengaluru.geojson
    python data/fetch_ms_roads.py --list-regions   # show available download URLs
"""

from __future__ import annotations
import argparse, json, os, sys, time, urllib.request, zipfile, io

# Microsoft Road Detections — India tiles
# These are the actual URLs from the Microsoft RoadDetections GitHub release.
MS_ROAD_URLS = {
    "India": "https://minedbuildings.blob.core.windows.net/road-detections/India.zip",
    "India_alt": "https://github.com/microsoft/RoadDetections/releases/download/v1.0/India.zip",
}

BENGALURU_BBOX = (12.85, 77.50, 13.05, 77.70)  # south, west, north, east


def download_with_progress(url: str, dest: str) -> bool:
    print(f"[MS Roads] Downloading: {url}")
    print(f"[MS Roads] Destination: {dest}")
    try:
        def _reporthook(count, block, total):
            mb = count * block / 1_000_000
            tot = total / 1_000_000 if total > 0 else "?"
            print(f"\r  {mb:.1f} / {tot} MB", end="", flush=True)
        urllib.request.urlretrieve(url, dest, reporthook=_reporthook)
        print()
        return True
    except Exception as e:
        print(f"\n[MS Roads] Download failed: {e}")
        return False


def clip_geojson_to_bbox(
    geojson_path: str,
    south: float, west: float, north: float, east: float,
    out_path: str,
) -> int:
    """Filter GeoJSON LineString features to those intersecting the bbox."""
    print(f"[MS Roads] Clipping to bbox ({south},{west}) → ({north},{east})")
    kept = []
    with open(geojson_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                feat = json.loads(line)
            except json.JSONDecodeError:
                continue
            coords = feat.get("geometry", {}).get("coordinates", [])
            if not coords:
                continue
            # Check if any coordinate falls within bbox
            for lon, lat in coords:
                if south <= lat <= north and west <= lon <= east:
                    kept.append(feat)
                    break

    fc = {"type": "FeatureCollection", "features": kept}
    with open(out_path, "w") as f:
        json.dump(fc, f)
    print(f"[MS Roads] Kept {len(kept)} road segments → {out_path}")
    return len(kept)


def geojson_to_training_mask_lines(geojson_path: str, out_dir: str,
                                    tile_bbox: tuple, tile_size: int = 512) -> None:
    """
    Convert MS road GeoJSON to rasterized binary mask PNGs for training.
    Each road line is drawn with a configurable width to match U-Net input.

    Requires: opencv-python, numpy
    """
    try:
        import cv2
        import numpy as np
    except ImportError:
        print("[MS Roads] opencv / numpy not available — skipping mask rasterization")
        return

    south, west, north, east = tile_bbox
    lat_span = north - south
    lon_span = east - west

    with open(geojson_path) as f:
        fc = json.load(f)

    mask = np.zeros((tile_size, tile_size), dtype=np.uint8)
    for feat in fc.get("features", []):
        coords = feat.get("geometry", {}).get("coordinates", [])
        pts = []
        for lon, lat in coords:
            col = int((lon - west)  / lon_span * tile_size)
            row = int((north - lat) / lat_span * tile_size)
            pts.append((col, row))
        if len(pts) >= 2:
            for i in range(len(pts) - 1):
                cv2.line(mask, pts[i], pts[i + 1], 255, thickness=3)

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "ms_roads_mask.png")
    cv2.imwrite(out_path, mask)
    print(f"[MS Roads] Mask saved → {out_path}  ({mask.sum()//255} road pixels)")


def main():
    ap = argparse.ArgumentParser(description="Download Microsoft ML Road Detections for India")
    ap.add_argument("--bbox",  default="12.85,77.50,13.05,77.70",
                    help="south,west,north,east for clipping (default: Bengaluru core)")
    ap.add_argument("--out",   default="data/ms_roads_bengaluru.geojson")
    ap.add_argument("--cache-dir", default="data/cache", help="Dir to cache downloaded zip")
    ap.add_argument("--list-regions", action="store_true")
    ap.add_argument("--rasterize", action="store_true",
                    help="Also produce a binary mask PNG for the bbox")
    args = ap.parse_args()

    if args.list_regions:
        print("Available download URLs:")
        for k, v in MS_ROAD_URLS.items():
            print(f"  {k}: {v}")
        return

    bbox = tuple(float(x) for x in args.bbox.split(","))
    assert len(bbox) == 4, "bbox must be south,west,north,east"
    south, west, north, east = bbox

    os.makedirs(args.cache_dir, exist_ok=True)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    zip_path = os.path.join(args.cache_dir, "India_ms_roads.zip")
    geojson_cache = os.path.join(args.cache_dir, "India_ms_roads.geojson")

    # Download zip if not cached
    if not os.path.exists(zip_path):
        success = False
        for name, url in MS_ROAD_URLS.items():
            if download_with_progress(url, zip_path):
                success = True
                break
        if not success:
            print("\n[MS Roads] All download URLs failed.")
            print("Manual steps:")
            print("  1. Visit: https://github.com/microsoft/RoadDetections")
            print("  2. Download the India release zip")
            print(f"  3. Place it at: {zip_path}")
            print("  4. Re-run this script")
            sys.exit(1)
    else:
        print(f"[MS Roads] Using cached zip: {zip_path}")

    # Extract GeoJSON from zip
    if not os.path.exists(geojson_cache):
        print("[MS Roads] Extracting zip...")
        with zipfile.ZipFile(zip_path) as zf:
            names = zf.namelist()
            print(f"  Contents: {names[:5]}")
            geojson_name = next((n for n in names if n.endswith(".geojson")), None)
            if not geojson_name:
                print(f"[MS Roads] No .geojson found in zip. Contents: {names}")
                sys.exit(1)
            zf.extract(geojson_name, args.cache_dir)
            extracted = os.path.join(args.cache_dir, geojson_name)
            os.rename(extracted, geojson_cache)
        print(f"[MS Roads] Extracted → {geojson_cache}")
    else:
        print(f"[MS Roads] Using cached GeoJSON: {geojson_cache}")

    # Clip to bbox
    n_kept = clip_geojson_to_bbox(geojson_cache, south, west, north, east, args.out)

    if args.rasterize and n_kept > 0:
        mask_dir = os.path.join(os.path.dirname(args.out), "ms_masks")
        geojson_to_training_mask_lines(args.out, mask_dir, bbox)

    print(f"\n[MS Roads] Done. Road segments for bbox: {n_kept}")
    print(f"Output: {args.out}")
    print("\nNext steps:")
    print("  python data/prepare_finetune.py --ms-roads", args.out)


if __name__ == "__main__":
    main()
