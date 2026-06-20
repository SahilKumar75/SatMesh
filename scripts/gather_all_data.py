"""
Master data gathering script — pulls ALL training data sources:

  1. DeepGlobe Road Extraction  (Kaggle)
  2. SpaceNet Roads SN3          (Kaggle)
  3. Sentinel-2 tiles            (Microsoft Planetary Computer) — 5 Indian cities
  4. OSM road masks              (osmnx) — paired with Sentinel-2

Run on Lightning AI:
    pip install kaggle osmnx rasterio geopandas planetary-computer pystac-client albumentations

    # Set Kaggle creds first:
    export KAGGLE_USERNAME=your_username
    export KAGGLE_KEY=your_api_key

    python scripts/gather_all_data.py

Output structure:
    data/
      raw/
        deepglobe/          ← DeepGlobe images + masks
        spacenet/           ← SpaceNet images + masks
        sentinel/
          bengaluru/        ← red/green/blue GeoTIFFs + osm_road_mask.tif
          delhi/
          mumbai/
          hyderabad/
          chennai/
      tiles/                ← 512x512 .npy paired tiles ready for training
        images/
        masks/
"""

import argparse
import json
import os
import shutil
import sys
import zipfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

DATA_RAW   = ROOT / "data" / "raw"
DATA_TILES = ROOT / "data" / "tiles"

CITIES = {
    "bengaluru": {"bbox": [12.85, 77.50, 13.05, 77.70], "name": "Bengaluru"},
    "delhi":     {"bbox": [28.45, 76.85, 28.75, 77.35], "name": "Delhi"},
    "mumbai":    {"bbox": [18.89, 72.77, 19.27, 72.98], "name": "Mumbai"},
    "hyderabad": {"bbox": [17.28, 78.30, 17.55, 78.60], "name": "Hyderabad"},
    "chennai":   {"bbox": [12.90, 80.15, 13.15, 80.35], "name": "Chennai"},
}


# ─────────────────────────────────────────────
# 1. DeepGlobe
# ─────────────────────────────────────────────

def download_deepglobe(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    done_flag = out_dir / ".done"
    if done_flag.exists():
        print("[DeepGlobe] already downloaded, skipping")
        return

    print("[DeepGlobe] downloading via Kaggle API...")
    _check_kaggle_creds()

    import subprocess
    result = subprocess.run([
        "kaggle", "datasets", "download",
        "-d", "balraj98/deepglobe-road-extraction-dataset",
        "-p", str(out_dir), "--unzip"
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"  [ERROR] {result.stderr}")
        print("  → Get API key from https://www.kaggle.com/settings → API → Create Token")
        print("  → Set: export KAGGLE_USERNAME=xxx  export KAGGLE_KEY=xxx")
        return

    done_flag.touch()
    print(f"[DeepGlobe] done → {out_dir}")
    _report_deepglobe(out_dir)


def _report_deepglobe(out_dir: Path):
    images = list(out_dir.rglob("*_sat.jpg"))
    masks  = list(out_dir.rglob("*_mask.png"))
    print(f"  Images: {len(images)}  Masks: {len(masks)}")


# ─────────────────────────────────────────────
# 2. SpaceNet SN3
# ─────────────────────────────────────────────

def download_spacenet(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    done_flag = out_dir / ".done"
    if done_flag.exists():
        print("[SpaceNet] already downloaded, skipping")
        return

    print("[SpaceNet] downloading via Kaggle API...")
    _check_kaggle_creds()

    import subprocess
    result = subprocess.run([
        "kaggle", "datasets", "download",
        "-d", "selfishgene/urban-roads",
        "-p", str(out_dir), "--unzip"
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"  [ERROR] {result.stderr}")
        print("  → SpaceNet SN3 requires AWS access; skipping. DeepGlobe+OSM sufficient.")
        return

    done_flag.touch()
    print(f"[SpaceNet] done → {out_dir}")


# ─────────────────────────────────────────────
# 3. Sentinel-2 (Microsoft Planetary Computer)
# ─────────────────────────────────────────────

def download_sentinel_city(city_id: str, bbox: list, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    meta_path = out_dir / "sentinel_meta.json"
    if meta_path.exists():
        print(f"  [Sentinel-2/{city_id}] already downloaded, skipping")
        return

    print(f"  [Sentinel-2/{city_id}] downloading...")
    try:
        import requests, rasterio
        from rasterio.windows import from_bounds

        STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1/search"
        south, west, north, east = bbox[0], bbox[1], bbox[2], bbox[3]
        payload = {
            "collections": ["sentinel-2-l2a"],
            "bbox": [west, south, east, north],
            "query": {"eo:cloud_cover": {"lt": 20}},
            "sortby": [{"field": "properties.eo:cloud_cover", "direction": "asc"}],
            "limit": 5,
        }
        r = requests.post(STAC_URL, json=payload, timeout=30)
        r.raise_for_status()
        features = r.json().get("features", [])
        if not features:
            print(f"  [ERROR] No Sentinel-2 tiles found for {city_id}")
            return

        item = features[0]
        band_keys = {"B04": "red", "B03": "green", "B02": "blue", "B08": "nir"}
        paths = {}
        for band, label in band_keys.items():
            href = item["assets"][band]["href"]
            # sign asset
            sr = requests.get(
                f"https://planetarycomputer.microsoft.com/api/sas/v1/sign?href={href}",
                timeout=15)
            if sr.ok:
                href = sr.json().get("href", href)
            out_path = out_dir / f"{label}.tif"
            if not out_path.exists():
                with rasterio.open(href) as src:
                    window = from_bounds(west, south, east, north, src.transform)
                    data = src.read(1, window=window)
                    transform = src.window_transform(window)
                    profile = src.profile.copy()
                    profile.update({"width": data.shape[1], "height": data.shape[0],
                                    "transform": transform, "count": 1})
                    with rasterio.open(out_path, "w", **profile) as dst:
                        dst.write(data, 1)
            paths[label] = str(out_path)

        with rasterio.open(paths["red"]) as src:
            t = src.transform
            meta = {"width": src.width, "height": src.height, "paths": paths,
                    "top_left_lat": float(t.f), "top_left_lon": float(t.c)}

        import json
        with open(out_dir / "sentinel_meta.json", "w") as f:
            json.dump(meta, f, indent=2)
        print(f"  done: {meta['width']}x{meta['height']} px")
    except Exception as e:
        print(f"  [ERROR] {e}")


# ─────────────────────────────────────────────
# 4. OSM road masks
# ─────────────────────────────────────────────

def download_osm_mask(city_id: str, bbox: list, out_dir: Path):
    import osmnx as ox
    import rasterio
    from rasterio.transform import from_bounds
    from rasterio.features import rasterize
    from shapely.geometry import mapping

    mask_path  = out_dir / "osm_road_mask.tif"
    graph_path = out_dir / "osm_graph.graphml"

    if mask_path.exists() and graph_path.exists():
        print(f"  [OSM/{city_id}] already downloaded, skipping")
        return

    south, west, north, east = bbox[0], bbox[1], bbox[2], bbox[3]
    print(f"  [OSM/{city_id}] downloading road graph...")

    try:
        G = ox.graph_from_bbox(north, south, east, west, network_type="drive")
        ox.save_graphml(G, graph_path)

        H, W = 512, 512
        transform = from_bounds(west, south, east, north, W, H)
        edges = ox.graph_to_gdfs(G, nodes=False)

        # buffer roads by ~5m for better mask coverage
        edges_proj = edges.to_crs("EPSG:32643")
        edges_proj["geometry"] = edges_proj.geometry.buffer(5)
        edges_reproj = edges_proj.to_crs("EPSG:4326")

        shapes = [(mapping(geom), 1) for geom in edges_reproj.geometry if geom is not None]
        mask = rasterize(shapes, out_shape=(H, W), transform=transform,
                         fill=0, dtype="uint8") * 255

        profile = {
            "driver": "GTiff", "dtype": "uint8",
            "width": W, "height": H, "count": 1,
            "crs": "EPSG:4326", "transform": transform,
        }
        with rasterio.open(mask_path, "w", **profile) as dst:
            dst.write(mask, 1)

        road_px = int((mask > 0).sum())
        print(f"  done: {road_px} road pixels / {H*W} total ({100*road_px/(H*W):.1f}%)")

    except Exception as e:
        print(f"  [ERROR] OSM download failed: {e}")


# ─────────────────────────────────────────────
# 5. Tile everything into training pairs
# ─────────────────────────────────────────────

def tile_sentinel_city(city_id: str, city_dir: Path, tile_dir: Path, tile_size=512):
    import rasterio
    from rasterio.windows import Window

    img_paths = {b: city_dir / f"{b}.tif" for b in ["red", "green", "blue"]}
    mask_path = city_dir / "osm_road_mask.tif"

    if not all(p.exists() for p in img_paths.values()):
        print(f"  [tile/{city_id}] Sentinel bands missing, skipping")
        return
    if not mask_path.exists():
        print(f"  [tile/{city_id}] OSM mask missing, skipping")
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
            for b in ["red", "green", "blue"]:
                with rasterio.open(img_paths[b]) as src:
                    data = src.read(1, window=window).astype(np.float32)
                    data = np.clip(data / 3000.0 * 255, 0, 255).astype(np.uint8)
                    bands.append(data)
            rgb = np.stack(bands, axis=0)

            with rasterio.open(mask_path) as src:
                mask = src.read(1, window=window)

            prefix = f"sentinel_{city_id}_{row:04d}_{col:04d}"
            np.save(img_dir / f"{prefix}.npy", rgb)
            np.save(msk_dir / f"{prefix}.npy", mask)
            count += 1

    print(f"  [tile/{city_id}] {count} tiles created")


def tile_deepglobe(deepglobe_dir: Path, tile_dir: Path, tile_size=512):
    """Convert DeepGlobe JPG/PNG pairs to .npy tiles."""
    import cv2

    images = sorted(deepglobe_dir.rglob("*_sat.jpg"))
    if not images:
        print("  [tile/deepglobe] no images found, skipping")
        return

    img_dir = tile_dir / "images"
    msk_dir = tile_dir / "masks"
    img_dir.mkdir(parents=True, exist_ok=True)
    msk_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for img_path in images:
        stem = img_path.stem.replace("_sat", "")
        mask_path = img_path.parent / f"{stem}_mask.png"
        if not mask_path.exists():
            continue

        img  = cv2.imread(str(img_path))
        mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
        if img is None or mask is None:
            continue

        img  = cv2.resize(img,  (tile_size, tile_size))
        mask = cv2.resize(mask, (tile_size, tile_size), interpolation=cv2.INTER_NEAREST)
        rgb  = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).transpose(2, 0, 1)  # (3,H,W)
        binary_mask = (mask > 127).astype(np.uint8) * 255

        prefix = f"deepglobe_{stem}"
        np.save(img_dir / f"{prefix}.npy", rgb)
        np.save(msk_dir / f"{prefix}.npy", binary_mask)
        count += 1

    print(f"  [tile/deepglobe] {count} tiles created")


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _check_kaggle_creds():
    u = os.environ.get("KAGGLE_USERNAME")
    k = os.environ.get("KAGGLE_KEY")
    if not u or not k:
        # try ~/.kaggle/kaggle.json
        kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
        if kaggle_json.exists():
            return
        print("\n[ERROR] Kaggle credentials not found.")
        print("  Option 1: export KAGGLE_USERNAME=xxx  KAGGLE_KEY=xxx")
        print("  Option 2: place kaggle.json at ~/.kaggle/kaggle.json")
        print("  Get token: https://www.kaggle.com/settings → API → Create New Token\n")
        sys.exit(1)


def print_summary():
    total_img = len(list((DATA_TILES / "images").rglob("*.npy"))) if (DATA_TILES / "images").exists() else 0
    total_msk = len(list((DATA_TILES / "masks").rglob("*.npy")))  if (DATA_TILES / "masks").exists()  else 0
    print("\n" + "=" * 55)
    print("DATA SUMMARY")
    print("=" * 55)
    print(f"  Training tiles (images): {total_img}")
    print(f"  Training tiles (masks):  {total_msk}")
    print(f"\n  Raw data:  {DATA_RAW}")
    print(f"  Tiles:     {DATA_TILES}")
    print("\nNext step:")
    print("  python scripts/train.py --data data/tiles")


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Download all training data")
    parser.add_argument("--skip-deepglobe",  action="store_true")
    parser.add_argument("--skip-spacenet",   action="store_true")
    parser.add_argument("--skip-sentinel",   action="store_true")
    parser.add_argument("--skip-osm",        action="store_true")
    parser.add_argument("--skip-tiling",     action="store_true")
    parser.add_argument("--cities", default="all",
                        help="comma-separated city ids or 'all'")
    args = parser.parse_args()

    selected_cities = list(CITIES.keys()) if args.cities == "all" \
                      else [c.strip() for c in args.cities.split(",")]

    print("=" * 55)
    print("BAH-2026 DATA GATHER — ALL SOURCES")
    print("=" * 55)

    # ── DeepGlobe ──
    if not args.skip_deepglobe:
        print("\n[1/4] DeepGlobe Road Extraction Dataset")
        download_deepglobe(DATA_RAW / "deepglobe")
    else:
        print("\n[1/4] DeepGlobe — SKIPPED")

    # ── SpaceNet ──
    if not args.skip_spacenet:
        print("\n[2/4] SpaceNet Roads Dataset")
        download_spacenet(DATA_RAW / "spacenet")
    else:
        print("\n[2/4] SpaceNet — SKIPPED")

    # ── Sentinel-2 + OSM ──
    print(f"\n[3/4] Sentinel-2 + OSM masks ({len(selected_cities)} cities)")
    for city_id in selected_cities:
        if city_id not in CITIES:
            print(f"  [warn] unknown city: {city_id}")
            continue
        city = CITIES[city_id]
        city_dir = DATA_RAW / "sentinel" / city_id
        city_dir.mkdir(parents=True, exist_ok=True)

        if not args.skip_sentinel:
            download_sentinel_city(city_id, city["bbox"], city_dir)
        if not args.skip_osm:
            download_osm_mask(city_id, city["bbox"], city_dir)

    # ── Tiling ──
    if not args.skip_tiling:
        print("\n[4/4] Tiling all data → training pairs")

        if (DATA_RAW / "deepglobe").exists():
            tile_deepglobe(DATA_RAW / "deepglobe", DATA_TILES)

        for city_id in selected_cities:
            if city_id not in CITIES:
                continue
            city_dir = DATA_RAW / "sentinel" / city_id
            tile_sentinel_city(city_id, city_dir, DATA_TILES)
    else:
        print("\n[4/4] Tiling — SKIPPED")

    print_summary()


if __name__ == "__main__":
    main()
