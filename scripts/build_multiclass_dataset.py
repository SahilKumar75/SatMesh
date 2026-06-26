#!/usr/bin/env python3
"""Build 4-class semantic segmentation dataset for occlusion-aware road training.

Output mask values (single-channel PNG, dtype uint8):
  0 = background
  1 = road       (OSM vectors — always wins, overrides occluders)
  2 = tree/canopy (RGB green-channel heuristic)
  3 = shadow     (HSV low-luminance Otsu heuristic)

Why 4 classes: teaches the model what occludes roads so it learns to infer
road continuity under canopy/shadow (PS4 Occlusion-Recall metric).

Reuses Esri tile fetching + OSM rasterization from build_highres_dataset.py.

Example:
    python scripts/build_multiclass_dataset.py --regions all --zoom 18 \\
        --windows 25 --out data/india_multiclass/train

    # inspect labels visually:
    python scripts/build_multiclass_dataset.py --regions bengaluru --windows 5 \\
        --out data/india_multiclass/check --save-color
"""
import argparse
import math
import random
import sys
import time
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.build_highres_dataset import (
    deg2tile, fetch_window, rasterize_window, resolve_regions,
)

# ── class IDs ────────────────────────────────────────────────────────────────
BG     = 0
ROAD   = 1
TREE   = 2
SHADOW = 3

# colormap for --save-color (BGR)
_COLOR = {
    BG:     (50,  50,  50),   # dark grey
    ROAD:   (255, 255, 255),  # white
    TREE:   (34, 139,  34),   # forest green
    SHADOW: (128, 128, 200),  # blue-grey
}


# ── occluder detectors ────────────────────────────────────────────────────────

def detect_tree_mask(rgb: np.ndarray) -> np.ndarray:
    """Binary uint8 mask of probable tree/canopy pixels from RGB.

    Heuristic: canopy pixels are green-dominant (G > R and G > B) with
    enough brightness to not be shadow, and enough green saturation.
    Tuned for Esri z18 Indian imagery (dense urban + forested terrain).
    """
    r = rgb[..., 0].astype(np.int16)
    g = rgb[..., 1].astype(np.int16)
    b = rgb[..., 2].astype(np.int16)
    tree = (
        (g - r > 10) &   # greener than red
        (g - b > 5)  &   # greener than blue
        (g > 40)     &   # bright enough (not shadow)
        (g < 220)        # not blown-out roof/cloud
    )
    return tree.astype(np.uint8) * 255


def detect_shadow_mask(rgb: np.ndarray) -> np.ndarray:
    """Binary uint8 mask of shadow pixels from RGB.

    Mirrors occlusion.py:detect_shadow_mask but accepts RGB (not BGR).
    Shadows: low V (Otsu), moderate S (retain colour, not washed out).
    """
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    v, s = hsv[..., 2], hsv[..., 1]
    _, dark = cv2.threshold(v, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    shadow = ((dark > 0) & (s > 30)).astype(np.uint8) * 255
    return shadow


# ── mask composition ──────────────────────────────────────────────────────────

def make_4class_mask(rgb: np.ndarray, road_binary: np.ndarray) -> np.ndarray:
    """Compose 4-class mask. Roads always win (painted last).

    Args:
        rgb:         H×W×3 uint8 Esri tile (RGB)
        road_binary: H×W uint8, 255=road from OSM rasterization

    Returns:
        H×W uint8 mask with values in {0,1,2,3}
    """
    h, w = rgb.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)

    shadow = detect_shadow_mask(rgb)
    tree   = detect_tree_mask(rgb)

    mask[shadow > 0] = SHADOW
    mask[tree   > 0] = TREE
    mask[road_binary > 127] = ROAD   # road wins over shadow/tree

    return mask


def colorize(mask: np.ndarray) -> np.ndarray:
    h, w = mask.shape
    out = np.zeros((h, w, 3), dtype=np.uint8)
    for cls, bgr in _COLOR.items():
        out[mask == cls] = bgr
    return out


# ── tiling + writing ──────────────────────────────────────────────────────────

def tile_and_write(rgb, mask, prefix, out_dir, tile=512,
                   min_road_frac=0.01, keep_empty=0.05, save_color=False):
    h, w = mask.shape
    n = 0
    for r in range(0, h - tile + 1, tile):
        for c in range(0, w - tile + 1, tile):
            m = mask[r:r+tile, c:c+tile]
            road_frac = (m == ROAD).mean()
            if road_frac < min_road_frac and random.random() > keep_empty:
                continue
            img = rgb[r:r+tile, c:c+tile]
            if img.shape[:2] != (tile, tile):
                continue
            stem = f"{prefix}_{r}_{c}"
            cv2.imwrite(str(out_dir / f"{stem}_sat.jpg"),
                        cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            cv2.imwrite(str(out_dir / f"{stem}_mask.png"), m)
            if save_color:
                cv2.imwrite(str(out_dir / f"{stem}_color.png"), colorize(m))
            n += 1
    return n


# ── per-region builder ────────────────────────────────────────────────────────

def build_region(cid, cfg, out_dir, z, grid, windows, tile,
                 buffer_px, min_road_frac, session, save_color):
    import geopandas as gpd
    import pandas as pd
    from src.data.mask_raster import fetch_osm_roads

    print(f"[{cid}] terrain={cfg.terrain} — fetching OSM roads...", flush=True)
    try:
        roads = fetch_osm_roads(cfg.bbox, network_type="drive")
        roads_merc = roads.to_crs("EPSG:3857") if len(roads) else None
    except Exception as e:
        print(f"[{cid}] OSM failed ({e}) — skipping")
        return 0

    if roads_merc is None or len(roads_merc) == 0:
        print(f"[{cid}] no roads found — skipping")
        return 0

    south, west, north, east = cfg.bbox
    xt0 = int(math.floor(min(deg2tile(north, west, z)[0], deg2tile(south, east, z)[0])))
    xt1 = int(math.floor(max(deg2tile(north, west, z)[0], deg2tile(south, east, z)[0])))
    yt0 = int(math.floor(min(deg2tile(north, west, z)[1], deg2tile(south, east, z)[1])))
    yt1 = int(math.floor(max(deg2tile(north, west, z)[1], deg2tile(south, east, z)[1])))

    n = 0
    for k in range(windows):
        rx = random.randint(xt0, max(xt0, xt1 - grid))
        ry = random.randint(yt0, max(yt0, yt1 - grid))
        rgb, bounds = fetch_window(rx, ry, grid, z, session)
        road_bin = rasterize_window(roads_merc, bounds, rgb.shape[:2], buffer_px)
        mask = make_4class_mask(rgb, road_bin)
        n += tile_and_write(rgb, mask, f"{cid}_{k}", out_dir, tile,
                            min_road_frac, save_color=save_color)

    print(f"[{cid}] wrote {n} tiles")
    return n


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--regions", default="all")
    ap.add_argument("--regions-file", default="data/train_regions.json")
    ap.add_argument("--zoom", type=int, default=18)
    ap.add_argument("--grid", type=int, default=4,
                    help="tile grid side (GxG Esri tiles per window)")
    ap.add_argument("--windows", type=int, default=25,
                    help="random windows sampled per region")
    ap.add_argument("--tile", type=int, default=512)
    ap.add_argument("--buffer-px", type=int, default=3,
                    help="road half-width in pixels for OSM rasterization")
    ap.add_argument("--min-road-frac", type=float, default=0.01)
    ap.add_argument("--out", default="data/india_multiclass/train")
    ap.add_argument("--save-color", action="store_true",
                    help="also save colorized mask PNGs for visual QA")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    import requests
    session = requests.Session()

    print(f"Output: {out_dir}")
    print(f"Classes: 0=bg  1=road  2=tree  3=shadow")
    print(f"Color QA: {'on' if args.save_color else 'off'}")
    print()

    total = 0
    for cid, cfg in resolve_regions(args.regions, args.regions_file).items():
        try:
            total += build_region(cid, cfg, out_dir, args.zoom, args.grid,
                                  args.windows, args.tile, args.buffer_px,
                                  args.min_road_frac, session, args.save_color)
        except Exception as e:
            print(f"[{cid}] FAILED: {e}")

    n_pairs = len(list(out_dir.glob("*_sat.jpg")))
    print(f"\nDone. {total} tiles this run | {n_pairs} total in {out_dir}")
    print("Next: train SegFormer v3 with num_classes=4 on this dataset.")


if __name__ == "__main__":
    main()
