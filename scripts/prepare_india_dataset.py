#!/usr/bin/env python3
"""Build ``data/sentinel2_india/train`` for stage-2 (Checkpoint A) fine-tuning.

Two sources, combined into one flat dir of ``*_sat.jpg`` / ``*_mask.png`` pairs
(the layout ``src.model.train.RoadDS`` expects):

  1. ``--published-dir`` : the published *India Sentinel-2 Roads Dataset*
     (Data in Brief 2025; 5634 tiles, 256x256, 10 m, OSM masks). Ingested and
     renamed to our convention. Pass the folder you downloaded/unzipped.
  2. ``--regions``       : ``cities.json`` regions. For each, pull Sentinel-2
     true-colour RGB via Microsoft Planetary Computer (``src.data.sentinel_dl``)
     and rasterize OSM roads to a mask (``src.data.mask_raster``), then tile.

Network is required for source 2 (Planetary Computer STAC + OSM Overpass) — run
on a box with outbound internet (Lightning AI), NOT inside a sandbox.

Examples
--------
    # Both sources, all 13 regions, 512 px tiles:
    python scripts/prepare_india_dataset.py \
        --published-dir ~/Downloads/sentinel2_india_roads \
        --regions all --out data/sentinel2_india/train

    # Only ingest the published dataset:
    python scripts/prepare_india_dataset.py \
        --published-dir ~/Downloads/sentinel2_india_roads --regions none

    # Only build the terrain regions (skip metros):
    python scripts/prepare_india_dataset.py \
        --regions terrain_himalaya,terrain_thar,terrain_konkan,terrain_ne_forest
"""
import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def _stretch_to_uint8(band, lo_pct=2, hi_pct=98):
    """Percentile contrast stretch a single reflectance band to uint8."""
    import numpy as np
    valid = band[np.isfinite(band)]
    if valid.size == 0:
        return np.zeros(band.shape, dtype=np.uint8)
    lo, hi = np.percentile(valid, [lo_pct, hi_pct])
    if hi <= lo:
        hi = lo + 1.0
    out = np.clip((band - lo) / (hi - lo), 0, 1) * 255
    return out.astype(np.uint8)


def _load_rgb(paths):
    """Read the red/green/blue single-band tifs into an HxWx3 uint8 RGB image."""
    import numpy as np
    import rasterio
    bands = []
    for key in ("red", "green", "blue"):
        with rasterio.open(paths[key]) as src:
            bands.append(src.read(1).astype("float32"))
    rgb = np.dstack([_stretch_to_uint8(b) for b in bands])
    return rgb


def _tile_and_write(rgb, mask, prefix, out_dir, tile=512, min_road_frac=0.004,
                    keep_empty_frac=0.1):
    """Cut RGB+mask into non-overlapping tiles, write pairs that contain road.

    Tiles below ``min_road_frac`` road pixels are dropped (a small fraction of
    empties is kept as negatives). Returns the number of pairs written.
    """
    import random
    import cv2
    import numpy as np

    h, w = mask.shape[:2]
    written = 0
    for r in range(0, h - tile + 1, tile):
        for c in range(0, w - tile + 1, tile):
            m = mask[r:r + tile, c:c + tile]
            frac = float((m > 127).mean())
            if frac < min_road_frac and random.random() > keep_empty_frac:
                continue
            img = rgb[r:r + tile, c:c + tile]
            if img.shape[0] != tile or img.shape[1] != tile:
                continue
            stem = f"{prefix}_{r}_{c}"
            cv2.imwrite(str(out_dir / f"{stem}_sat.jpg"),
                        cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            cv2.imwrite(str(out_dir / f"{stem}_mask.png"), m)
            written += 1
    return written


def ingest_published(src_dir, out_dir):
    """Copy a published dataset into our *_sat.jpg/_mask.png flat layout.

    Tolerant matcher: pairs an image with the mask whose stem shares the same
    numeric/base id. Looks for masks via common tokens (mask/label/gt/road) or a
    sibling ``masks/`` dir; everything else is treated as an image.
    """
    src = Path(src_dir).expanduser()
    if not src.exists():
        print(f"[published] {src} does not exist — skipping")
        return 0

    exts = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}
    files = [p for p in src.rglob("*") if p.suffix.lower() in exts]
    mask_tokens = ("mask", "label", "gt", "road", "_y", "seg")

    def is_mask(p):
        s = p.stem.lower()
        return any(t in s for t in mask_tokens) or "mask" in p.parent.name.lower()

    masks = {}
    for p in files:
        if is_mask(p):
            key = p.stem.lower()
            for t in mask_tokens:
                key = key.replace(t, "")
            key = key.strip("_-")
            masks[key] = p

    written = 0
    for p in files:
        if is_mask(p):
            continue
        key = p.stem.lower()
        for t in ("sat", "image", "img", "rgb", "_x"):
            key = key.replace(t, "")
        key = key.strip("_-")
        mpath = masks.get(key)
        if mpath is None:
            continue
        stem = f"pub_{key}"
        _copy_as(p, out_dir / f"{stem}_sat.jpg")
        _copy_as(mpath, out_dir / f"{stem}_mask.png")
        written += 1

    print(f"[published] ingested {written} pairs from {src}")
    return written


def _copy_as(src, dst):
    """Copy/convert an image to dst (re-encodes if extension differs)."""
    import cv2
    if src.suffix.lower() == dst.suffix.lower():
        shutil.copy(src, dst)
        return
    img = cv2.imread(str(src), cv2.IMREAD_UNCHANGED)
    if img is None:
        shutil.copy(src, dst)  # last resort: raw copy
        return
    cv2.imwrite(str(dst), img)


def ingest_paired(images_dir, masks_dir, out_dir):
    """Pair an images folder with a masks folder by identical file stem.

    Fits the Zenodo India S2 layout (zenodo.15765738): separate folders where
    image ``N.png`` matches mask ``N.png``. Use the plain (non-enhanced) images
    folder so the model's own CLAHE step isn't double-applied.
    """
    img_dir, msk_dir = Path(images_dir).expanduser(), Path(masks_dir).expanduser()
    if not img_dir.exists() or not msk_dir.exists():
        print(f"[paired] missing {img_dir} or {msk_dir} — skipping")
        return 0

    exts = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}
    masks = {p.stem: p for p in msk_dir.rglob("*") if p.suffix.lower() in exts}
    written = 0
    for p in img_dir.rglob("*"):
        if p.suffix.lower() not in exts:
            continue
        mpath = masks.get(p.stem)
        if mpath is None:
            continue
        stem = f"pub_{p.stem}"
        _copy_as(p, out_dir / f"{stem}_sat.jpg")
        _copy_as(mpath, out_dir / f"{stem}_mask.png")
        written += 1
    print(f"[paired] ingested {written} pairs ({img_dir.name} + {msk_dir.name})")
    return written


def build_region(city_id, cfg, out_dir, tile, min_road_frac):
    """Download Sentinel-2 RGB + rasterize OSM roads for one region, then tile."""
    from src.data import sentinel_dl, mask_raster

    work = out_dir / "_scenes" / city_id
    work.mkdir(parents=True, exist_ok=True)

    print(f"[{city_id}] terrain={cfg.terrain} bbox={cfg.bbox} — fetching Sentinel-2...")
    meta = sentinel_dl.download_city(city_id, cfg.bbox, str(work))
    rgb = _load_rgb(meta["paths"])
    h, w = rgb.shape[:2]

    print(f"[{city_id}] rasterizing OSM roads to {h}x{w} mask...")
    roads = mask_raster.fetch_osm_roads(cfg.bbox)
    mask = mask_raster.rasterize_to_mask(roads, cfg.bbox, (h, w))

    n = _tile_and_write(rgb, mask, city_id, out_dir, tile=tile,
                        min_road_frac=min_road_frac)
    print(f"[{city_id}] wrote {n} tiles")
    return n


def resolve_regions(spec):
    from src.data.city_config import load_all
    cities = load_all()
    if spec in (None, "", "none"):
        return {}
    if spec == "all":
        return cities
    out = {}
    for cid in [s.strip() for s in spec.split(",") if s.strip()]:
        if cid not in cities:
            raise KeyError(f"region '{cid}' not in cities.json")
        out[cid] = cities[cid]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--published-dir", default=None,
                    help="folder of a token-named published dataset (mask/label in names)")
    ap.add_argument("--images-dir", default=None,
                    help="Zenodo-style images folder (paired by stem with --masks-dir)")
    ap.add_argument("--masks-dir", default=None,
                    help="Zenodo-style masks folder (paired by stem with --images-dir)")
    ap.add_argument("--regions", default="all",
                    help="'all' (default), 'none', or comma-separated cities.json ids")
    ap.add_argument("--out", default="data/sentinel2_india/train",
                    help="output dir for *_sat.jpg / *_mask.png pairs")
    ap.add_argument("--tile", type=int, default=512, help="tile size in px")
    ap.add_argument("--min-road-frac", type=float, default=0.004,
                    help="drop tiles with fewer than this fraction of road pixels")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    if args.published_dir:
        total += ingest_published(args.published_dir, out_dir)
    if args.images_dir and args.masks_dir:
        total += ingest_paired(args.images_dir, args.masks_dir, out_dir)

    regions = resolve_regions(args.regions)
    for cid, cfg in regions.items():
        try:
            total += build_region(cid, cfg, out_dir, args.tile, args.min_road_frac)
        except Exception as e:  # one bad region must not kill the whole build
            print(f"[{cid}] FAILED: {e}")

    n_pairs = len(list(out_dir.glob("*_sat.jpg")))
    print(f"\nDone. {total} new pairs this run; {n_pairs} total in {out_dir}")
    print("Train Checkpoint A:  python scripts/train.py --skip-stage1 "
          f"--india-dir {out_dir} --encoder mit_b4 --img-size {args.tile} "
          "--batch 28 --clahe")


if __name__ == "__main__":
    main()
