"""Convert per-city Sentinel-2 GeoTIFFs → RoadDS *_sat.jpg / *_nir.tif / *_mask.png.

Run once after gather_all_data.py, before train.py --india-dir.

Usage:
    python scripts/prep_sentinel_tiles.py
"""
import numpy as np
import cv2
import rasterio
from pathlib import Path

CITIES = ["bengaluru", "delhi", "mumbai", "hyderabad", "chennai"]
TILE = 512
SENTINEL_ROOT = Path("data/raw/sentinel")
TRAIN_DIR = Path("data/sentinel2_india/train")
EVAL_DIR_BASE = Path("data/sentinel2_india/eval")

# Mask encoding: 0/255 (confirmed gather_all_data.py:232 `rasterize(...) * 255`).
# Skip tiles with <2% road coverage: 0.02 * 255 = 5.1
ROAD_MASK_THRESHOLD = 5.1


def _percentile_stretch(arr, lo=2, hi=98):
    """Robust 2-98 percentile stretch → uint8 (no fixed divisor)."""
    p_lo, p_hi = np.percentile(arr, [lo, hi])
    return np.clip((arr - p_lo) / (p_hi - p_lo + 1e-6) * 255, 0, 255).astype(np.uint8)


def export_city(city_id: str) -> None:
    cdir = SENTINEL_ROOT / city_id

    # Load full bands into memory
    def _read(name):
        with rasterio.open(str(cdir / f"{name}.tif")) as s:
            return s.read(1).astype(np.float32)

    r_full   = _read("red")
    H, W     = r_full.shape
    g_full   = _read("green")
    b_full   = _read("blue")
    nir_full = _read("nir")

    with rasterio.open(str(cdir / "osm_road_mask.tif")) as s:
        m_full = s.read(1)

    # Resize mask to band dims — OSM mask may differ due to prior CRS bug
    if m_full.shape != (H, W):
        m_full = cv2.resize(m_full, (W, H), interpolation=cv2.INTER_NEAREST)

    tiles = []
    for row in range(0, H - TILE + 1, TILE):
        for col in range(0, W - TILE + 1, TILE):
            m = m_full[row:row+TILE, col:col+TILE]
            if m.mean() < ROAD_MASK_THRESHOLD:
                continue
            tiles.append((row, col,
                           r_full[row:row+TILE, col:col+TILE],
                           g_full[row:row+TILE, col:col+TILE],
                           b_full[row:row+TILE, col:col+TILE],
                           nir_full[row:row+TILE, col:col+TILE],
                           m))

    n_train = n_eval = 0
    for i, (row, col, r, g, b, nir, m) in enumerate(tiles):
        is_eval = (i % 5 == 0)
        out_dir = (EVAL_DIR_BASE / city_id) if is_eval else TRAIN_DIR
        out_dir.mkdir(parents=True, exist_ok=True)
        stem = f"{city_id}_{row:04d}_{col:04d}"

        rgb = np.stack([_percentile_stretch(r), _percentile_stretch(g), _percentile_stretch(b)], axis=-1)
        cv2.imwrite(str(out_dir / f"{stem}_sat.jpg"), cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))

        with rasterio.open(
            str(out_dir / f"{stem}_nir.tif"), "w",
            driver="GTiff", height=TILE, width=TILE, count=1, dtype="float32",
        ) as dst:
            dst.write(nir, 1)

        cv2.imwrite(str(out_dir / f"{stem}_mask.png"), (m > 0).astype(np.uint8) * 255)

        if is_eval:
            n_eval += 1
        else:
            n_train += 1

    print(f"  {city_id}: {len(tiles)} road tiles → {n_train} train, {n_eval} eval")


def main():
    TRAIN_DIR.mkdir(parents=True, exist_ok=True)
    print("Converting Sentinel-2 tiles → RoadDS format")
    print("=" * 50)
    for city in CITIES:
        red_tif = SENTINEL_ROOT / city / "red.tif"
        if red_tif.exists():
            export_city(city)
        else:
            print(f"  {city}: no sentinel data, skipping")
    print("Done.")
    print(f"  Train dir: {TRAIN_DIR}")
    print(f"  Eval dirs: {EVAL_DIR_BASE}/<city>/")


if __name__ == "__main__":
    main()
