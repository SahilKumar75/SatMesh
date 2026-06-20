"""Unified PS4 evaluation — all metrics in one run.

Combines Track A segmentation metrics (IoU, Dice, Relaxed IoU, Occlusion Recall,
Connectivity Ratio) with Track B graph metric (APLS vs OSM ground truth).

Usage
-----
# Fast (no graph metrics):
python eval/full_eval.py \\
  --sat_dir data/sentinel2_india/eval/bengaluru \\
  --mask_dir data/sentinel2_india/eval/bengaluru \\
  --pred_dir preds/bengaluru \\
  --city_id bengaluru

# With connectivity ratio (slow, ~2-5s per tile):
python eval/full_eval.py ... --connectivity --pixel_m 10.0

# With APLS (requires healed graph pickle):
python eval/full_eval.py ... --graph results/bengaluru_healed.gpickle --city_id bengaluru

PS4 targets:
  strict_iou > 0.68  |  relaxed_iou > 0.80  |  occlusion_recall > 0.65
  connectivity_ratio > 30%  |  apls > 0.70
"""
from __future__ import annotations
import argparse
import glob
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eval.track_a import evaluate_track_a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sat_dir",  required=True)
    ap.add_argument("--mask_dir", required=True)
    ap.add_argument("--pred_dir", required=True)
    ap.add_argument("--city_id",  default=None,
                    help="city identifier for APLS OSM lookup (e.g. bengaluru)")
    ap.add_argument("--graph",    default=None,
                    help="path to healed graph .gpickle for APLS computation")
    ap.add_argument("--connectivity", action="store_true",
                    help="compute connectivity ratio via graph healing (slow)")
    ap.add_argument("--pixel_m", type=float, default=0.5,
                    help="metres per pixel (0.5=DeepGlobe, 10.0=Sentinel-2)")
    ap.add_argument("--n_samples", type=int, default=200,
                    help="random path pairs for APLS computation")
    ap.add_argument("--out", default=None,
                    help="write results to JSON file (optional)")
    args = ap.parse_args()

    # ── Track A: segmentation metrics ──────────────────────────────────────
    sat_files = sorted(glob.glob(os.path.join(args.sat_dir, "*_sat.jpg")))
    pairs = [
        (s, os.path.join(args.mask_dir,
                         os.path.basename(s).replace("_sat.jpg", "_mask.png")))
        for s in sat_files
    ]
    pairs = [(s, m) for s, m in pairs if os.path.exists(m)]

    csv_out = args.out.replace(".json", "_track_a.csv") if args.out else None
    results = evaluate_track_a(
        pairs, args.pred_dir, csv_out,
        compute_connectivity=args.connectivity,
        pixel_m=args.pixel_m,
    )

    # ── Track B: APLS ──────────────────────────────────────────────────────
    if args.graph and os.path.exists(args.graph):
        import pickle
        import networkx as nx
        import osmnx as ox
        from src.data.city_config import load_city
        from src.graph.apls import compute_apls

        with open(args.graph, "rb") as f:
            G_pred = pickle.load(f)

        if args.city_id:
            cfg = load_city(args.city_id)
            s, w, n, e = cfg.bbox
            G_osm = ox.graph_from_bbox(n, s, e, w, network_type="drive")
            G_osm_u = nx.Graph(G_osm)
            apls = compute_apls(G_pred, G_osm_u, n_samples=args.n_samples)
            results["apls"] = round(apls, 4)
        else:
            print("WARN: --graph provided but --city_id missing; skipping APLS")
    elif args.graph:
        print(f"WARN: graph file not found: {args.graph}")

    # ── Print + write ───────────────────────────────────────────────────────
    print(json.dumps(results, indent=2))

    # PS4 target assessment
    checks = {
        "strict_iou > 0.68":           results.get("mean_iou", 0) > 0.68,
        "relaxed_iou > 0.80":          results.get("mean_relaxed_iou", 0) > 0.80,
        "occlusion_recall > 0.65":     results.get("mean_occlusion_recall", 0) > 0.65,
        "connectivity_ratio > 30%":    results.get("mean_connectivity_ratio", 0) > 30,
        "apls > 0.70":                 results.get("apls", 0) > 0.70,
    }
    print("\nPS4 target checks:")
    for k, v in checks.items():
        print(f"  {'✓' if v else '✗'}  {k}")

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        with open(args.out, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved → {args.out}")


if __name__ == "__main__":
    main()
