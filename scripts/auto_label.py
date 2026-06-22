#!/usr/bin/env python3
"""Auto-label road tiles with a trained model (self-training / pseudo-labeling).

Breaks past OSM's coverage gaps: run a trained SegFormer over fresh Esri tiles,
keep only high-confidence road predictions, and (recommended) FUSE them with OSM
so OSM anchors the truth while the model only *adds* roads it's confident about
(e.g. gullies OSM never mapped). Output is *_sat.jpg / *_mask.png pairs you append
to the training set and retrain on.

Modes:
  --mode fuse    (default) mask = OSM-all  OR  (model prob > conf). Safe: OSM anchor.
  --mode pseudo  mask = (model prob > conf) only. Use for regions with no OSM;
                 higher confirmation-bias risk, so use a high --conf.

Needs internet (Esri tiles + OSM) and the trained 3-ch checkpoint.

Example:
    python scripts/auto_label.py \
        --checkpoint checkpoints/b4_hr/segformer_india.pth \
        --regions all --mode fuse --conf 0.6 \
        --out data/india_highres/train_auto
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# reuse the Esri/geo machinery from the dataset builder
from scripts.build_highres_dataset import (  # noqa: E402
    deg2tile, tile_merc_bounds, fetch_window, rasterize_window, resolve_regions,
)

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)


def load_model(checkpoint, encoder="mit_b4"):
    import torch
    from src.model.segformer import build_segformer
    device = "cuda" if torch.cuda.is_available() else (
        "mps" if torch.backends.mps.is_available() else "cpu")
    model = build_segformer(pretrained=False, in_channels=3, encoder_name=encoder)
    model.load_state_dict(torch.load(checkpoint, map_location=device))
    return model.to(device).eval(), device


def predict_prob(model, rgb, tile, device):
    """Sliding-window road-probability map over an RGB mosaic (HxWx3 uint8)."""
    import numpy as np
    import torch
    mean = np.array(IMAGENET_MEAN, np.float32)
    std = np.array(IMAGENET_STD, np.float32)
    h, w = rgb.shape[:2]
    prob = np.zeros((h, w), np.float32)
    for r in range(0, h - tile + 1, tile):
        for c in range(0, w - tile + 1, tile):
            patch = rgb[r:r + tile, c:c + tile].astype(np.float32) / 255.0
            patch = (patch - mean) / std
            t = torch.from_numpy(patch).permute(2, 0, 1).unsqueeze(0).to(device)
            with torch.no_grad():
                p = torch.sigmoid(model(t))[0, 0].float().cpu().numpy()
            prob[r:r + tile, c:c + tile] = p
    return prob


def write_tiles(rgb, mask, prefix, out_dir, tile, min_road_frac, keep_empty=0.03):
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
            s = f"auto_{prefix}_{r}_{c}"
            cv2.imwrite(str(out_dir / f"{s}_sat.jpg"), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            cv2.imwrite(str(out_dir / f"{s}_mask.png"), m)
            n += 1
    return n


def label_region(cid, cfg, model, device, out_dir, z, grid, windows, tile,
                 buffer_px, conf, mode, min_road_frac, session):
    import random
    import numpy as np

    osm_merc = None
    if mode == "fuse":
        from src.data.mask_raster import fetch_osm_roads
        try:
            roads = fetch_osm_roads(cfg.bbox, network_type="all")
            if len(roads):
                osm_merc = roads.to_crs("EPSG:3857")
        except Exception as e:
            print(f"[{cid}] OSM fetch failed ({e}) — falling back to pseudo for this region")

    south, west, north, east = cfg.bbox
    xt0 = int(min(deg2tile(north, west, z)[0], deg2tile(south, east, z)[0]))
    xt1 = int(max(deg2tile(north, west, z)[0], deg2tile(south, east, z)[0]))
    yt0 = int(min(deg2tile(north, west, z)[1], deg2tile(south, east, z)[1]))
    yt1 = int(max(deg2tile(north, west, z)[1], deg2tile(south, east, z)[1]))

    n = 0
    for k in range(windows):
        rx = random.randint(xt0, max(xt0, xt1 - grid))
        ry = random.randint(yt0, max(yt0, yt1 - grid))
        rgb, bounds = fetch_window(rx, ry, grid, z, session)
        prob = predict_prob(model, rgb, tile, device)
        model_mask = (prob > conf).astype(np.uint8) * 255
        if osm_merc is not None:
            osm_mask = rasterize_window(osm_merc, bounds, rgb.shape[:2], buffer_px)
            mask = np.maximum(osm_mask, model_mask)   # OSM anchor + model additions
        else:
            mask = model_mask
        n += write_tiles(rgb, mask, f"{cid}_{k}", out_dir, tile, min_road_frac)
    print(f"[{cid}] auto-labeled {n} tiles (mode={mode}, conf={conf})")
    return n


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--checkpoint", required=True, help="trained 3-ch SegFormer .pth")
    ap.add_argument("--encoder", default="mit_b4")
    ap.add_argument("--regions", default="all")
    ap.add_argument("--regions-file", default="data/train_regions.json")
    ap.add_argument("--mode", choices=["fuse", "pseudo"], default="fuse")
    ap.add_argument("--conf", type=float, default=0.6,
                    help="keep model roads with prob above this (use higher for pseudo)")
    ap.add_argument("--zoom", type=int, default=18)
    ap.add_argument("--grid", type=int, default=4)
    ap.add_argument("--windows", type=int, default=20)
    ap.add_argument("--tile", type=int, default=512)
    ap.add_argument("--buffer-px", type=int, default=3)
    ap.add_argument("--min-road-frac", type=float, default=0.01)
    ap.add_argument("--out", default="data/india_highres/train_auto")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    model, device = load_model(args.checkpoint, args.encoder)
    print(f"model on {device}, mode={args.mode}, conf={args.conf}")

    import requests
    session = requests.Session()

    total = 0
    for cid, cfg in resolve_regions(args.regions, args.regions_file).items():
        try:
            total += label_region(cid, cfg, model, device, out_dir, args.zoom,
                                   args.grid, args.windows, args.tile, args.buffer_px,
                                   args.conf, args.mode, args.min_road_frac, session)
        except Exception as e:
            print(f"[{cid}] FAILED: {e}")

    n_pairs = len(list(out_dir.glob("*_sat.jpg")))
    print(f"\nDone. {total} auto-labeled pairs; {n_pairs} total in {out_dir}")
    print("Append to your training set and retrain to grow coverage past OSM.")


if __name__ == "__main__":
    main()
