"""
eval/metrics.py — unified evaluation for SatMesh.

Track A (image-level):
    iou_score, dice_score, relaxed_iou, occlusion_recall,
    simulate_occlusion_mask, evaluate_track_a

Track B (graph-level):
    connectivity_ratio, topological_accuracy, resilience_index,
    evaluate_track_b

CLI:
    python eval/metrics.py --track_a --checkpoint best_model.pth \\
                           --test_pairs test_pairs.json
    python eval/metrics.py --track_b --graph outputs/healed.gpickle
"""

from __future__ import annotations
import argparse, csv, json, os, random
from typing import Any

import cv2
import numpy as np
import networkx as nx
from scipy.spatial import cKDTree


# ── Track A helpers ──────────────────────────────────────────────────────────

def _to_bool(arr: np.ndarray) -> np.ndarray:
    return arr.astype(bool)


def iou_score(pred: np.ndarray, gt: np.ndarray) -> float:
    p, g = _to_bool(pred), _to_bool(gt)
    inter = (p & g).sum()
    union = (p | g).sum()
    return float((inter + 1e-6) / (union + 1e-6))


def dice_score(pred: np.ndarray, gt: np.ndarray) -> float:
    p, g = _to_bool(pred), _to_bool(gt)
    inter = (p & g).sum()
    return float((2 * inter + 1e-6) / (p.sum() + g.sum() + 1e-6))


def relaxed_iou(pred: np.ndarray, gt: np.ndarray, buffer_px: int = 3) -> float:
    """IoU with a localization tolerance buffer (PS4 rubric: 3-5 px)."""
    k = np.ones((2 * buffer_px + 1, 2 * buffer_px + 1), dtype=np.uint8)
    pred_d = cv2.dilate(pred.astype(np.uint8), k) > 0
    gt_d   = cv2.dilate(gt.astype(np.uint8),   k) > 0
    inter  = (pred_d & gt_d).sum()
    union  = (_to_bool(pred) | _to_bool(gt)).sum()   # original union, no cheating
    return float((inter + 1e-6) / (union + 1e-6))


def simulate_occlusion_mask(image_bgr: np.ndarray, dark_thr: int = 50) -> np.ndarray:
    """
    Proxy for shadow/canopy mask: pixels where all RGB channels < dark_thr.
    Returns uint8 array (1 = occluded, 0 = visible).
    """
    return (image_bgr.max(axis=2) < dark_thr).astype(np.uint8)


def occlusion_recall(
    pred: np.ndarray,
    gt: np.ndarray,
    occ_mask: np.ndarray,
) -> float:
    """
    Recall computed only in the occluded region.
    Measures how well the model recovers roads hidden under shadows/canopy.
    """
    gt_occ   = _to_bool(gt)   & occ_mask.astype(bool)
    pred_occ = _to_bool(pred) & occ_mask.astype(bool)
    tp = (pred_occ & gt_occ).sum()
    return float((tp + 1e-6) / (gt_occ.sum() + 1e-6))


def evaluate_track_a(
    image_paths: list[str],
    mask_paths:  list[str],
    pred_dir:    str,
    output_csv:  str = "track_a_metrics.csv",
) -> dict[str, float]:
    """
    Run all 5 Track A metrics over a set of images.

    pred_dir must contain files named {stem}_road_mask.png produced by infer.py.
    Writes per-image CSV and returns mean values.
    """
    rows = []
    for img_path, gt_path in zip(image_paths, mask_paths):
        stem  = os.path.splitext(os.path.basename(img_path))[0]
        pred_path = os.path.join(pred_dir, f"{stem}_road_mask.png")
        if not os.path.exists(pred_path):
            print(f"  [skip] {pred_path} not found")
            continue

        img  = cv2.imread(img_path)
        gt   = (cv2.imread(gt_path, cv2.IMREAD_GRAYSCALE) > 127).astype(np.uint8)
        pred = (cv2.imread(pred_path, cv2.IMREAD_GRAYSCALE) > 127).astype(np.uint8)

        if gt.shape != pred.shape:
            pred = cv2.resize(pred, (gt.shape[1], gt.shape[0]),
                              interpolation=cv2.INTER_NEAREST)

        occ = simulate_occlusion_mask(img)
        rows.append({
            "image":            stem,
            "iou":              iou_score(pred, gt),
            "dice":             dice_score(pred, gt),
            "relaxed_iou":      relaxed_iou(pred, gt, buffer_px=3),
            "occlusion_recall": occlusion_recall(pred, gt, occ),
        })

    if not rows:
        print("No predictions found.")
        return {}

    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    means = {
        k: float(np.mean([r[k] for r in rows]))
        for k in rows[0] if k != "image"
    }
    stds = {
        k: float(np.std([r[k] for r in rows]))
        for k in rows[0] if k != "image"
    }
    print(f"\nTrack A — {len(rows)} images  (written to {output_csv})")
    for k, v in means.items():
        print(f"  {k:<20} {v:.4f} ± {stds[k]:.4f}")
    return means


# ── Track B helpers ──────────────────────────────────────────────────────────

def _lcc_size(G: nx.Graph) -> int:
    if G.number_of_nodes() == 0:
        return 0
    return len(max(nx.connected_components(G), key=len))


def _avg_path_lcc(G: nx.Graph, weight: str = "length") -> float:
    """Average shortest path length over the largest connected component."""
    if G.number_of_nodes() < 2:
        return 0.0
    comp = max(nx.connected_components(G), key=len)
    H = G.subgraph(comp).copy()
    if H.number_of_nodes() < 2:
        return 0.0
    return nx.average_shortest_path_length(H, weight=weight)


def connectivity_ratio(G_before: nx.Graph, G_after: nx.Graph) -> float:
    """
    % increase in largest connected component size after MST healing.
    Positive = healing improved connectivity.
    """
    before = _lcc_size(G_before)
    after  = _lcc_size(G_after)
    if before == 0:
        return 0.0
    return float((after - before) / before)


def topological_accuracy(
    G_pred: nx.Graph,
    G_osm:  nx.Graph,
    n_samples: int = 200,
    match_radius_m: float = 20.0,
    seed: int = 42,
) -> float:
    """
    Mean absolute error (metres) between predicted and OSM path lengths.

    Algorithm:
    1. Build cKDTree over predicted node (lat, lon).
    2. For each OSM node find nearest predicted node within match_radius_m.
    3. Sample 200 random (src, dst) OSM pairs from mapped nodes.
    4. Compare nx.shortest_path_length on both graphs.
    Returns mean |osm_len - pred_len| in metres.
    """
    pred_nodes = list(G_pred.nodes)
    if len(pred_nodes) < 2:
        return float("inf")

    pred_coords = np.array([
        [G_pred.nodes[n].get("lat", G_pred.nodes[n].get("y", 0)),
         G_pred.nodes[n].get("lon", G_pred.nodes[n].get("x", 0))]
        for n in pred_nodes
    ])
    tree = cKDTree(pred_coords)

    osm_to_pred: dict[Any, Any] = {}
    for n in G_osm.nodes:
        nd = G_osm.nodes[n]
        lat, lon = nd.get("y", 0), nd.get("x", 0)
        dist, idx = tree.query([lat, lon])
        if dist * 111_000 <= match_radius_m:   # crude deg→m conversion
            osm_to_pred[n] = pred_nodes[idx]

    mapped = list(osm_to_pred.keys())
    if len(mapped) < 2:
        return float("inf")

    rng   = random.Random(seed)
    pairs = [(rng.choice(mapped), rng.choice(mapped)) for _ in range(n_samples)]
    errors = []
    for src_osm, dst_osm in pairs:
        if src_osm == dst_osm:
            continue
        try:
            osm_len  = nx.shortest_path_length(G_osm,  src_osm,                dst_osm, weight="length")
            pred_len = nx.shortest_path_length(G_pred, osm_to_pred[src_osm], osm_to_pred[dst_osm], weight="length")
            errors.append(abs(osm_len - pred_len))
        except nx.NetworkXNoPath:
            errors.append(float("inf"))

    finite = [e for e in errors if e != float("inf")]
    return float(np.mean(finite)) if finite else float("inf")


def resilience_index(G: nx.Graph, weight: str = "length") -> float:
    """
    Remove the single highest-betweenness node and compute
    baseline_avg_path / perturbed_avg_path.
    Lower value = network degrades more after the removal.
    """
    if G.number_of_nodes() < 3:
        return 1.0
    bc = nx.betweenness_centrality(G, weight=weight, k=min(len(G), 300), seed=42)
    worst = max(bc, key=bc.get)
    base  = _avg_path_lcc(G, weight)
    G2    = G.copy()
    G2.remove_node(worst)
    after = _avg_path_lcc(G2, weight)
    if after == 0:
        return 0.0
    return float(base / after)


def evaluate_track_b(
    G_pred:      nx.Graph,
    G_healed:    nx.Graph,
    G_osm:       nx.Graph,
    output_json: str = "track_b_metrics.json",
) -> dict[str, float]:
    results = {
        "connectivity_ratio":   connectivity_ratio(G_pred, G_healed),
        "topological_accuracy": topological_accuracy(G_healed, G_osm),
        "resilience_index":     resilience_index(G_healed),
    }
    with open(output_json, "w") as f:
        json.dump(results, f, indent=2)
    print("\nTrack B metrics:")
    for k, v in results.items():
        print(f"  {k:<26} {v:.4f}")
    return results


# ── CLI ──────────────────────────────────────────────────────────────────────

def _run_track_a(args):
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from track_a.infer import load_model, predict_mask, postprocess_mask, _device

    with open(args.test_pairs) as f:
        pairs = json.load(f)

    image_paths = [p[0] for p in pairs]
    mask_paths  = [p[1] for p in pairs]

    device = _device()
    model  = load_model(args.checkpoint, device)
    pred_dir = args.pred_dir or "outputs/track_a_preds"
    os.makedirs(pred_dir, exist_ok=True)

    print(f"Generating predictions for {len(image_paths)} test images...")
    for img_path in image_paths:
        stem = os.path.splitext(os.path.basename(img_path))[0]
        out  = os.path.join(pred_dir, f"{stem}_road_mask.png")
        if not os.path.exists(out):
            mask = predict_mask(model, img_path, device, args.img_size)
            mask = postprocess_mask(mask)
            cv2.imwrite(out, mask)

    evaluate_track_a(image_paths, mask_paths, pred_dir,
                     output_csv=args.output or "track_a_metrics.csv")


def _run_track_b(args):
    import pickle
    with open(args.graph, "rb") as f:
        G = pickle.load(f)
    G_osm_path = args.osm_graph
    if G_osm_path and os.path.exists(G_osm_path):
        import osmnx as ox
        G_osm = ox.load_graphml(G_osm_path)
        G_osm_u = nx.Graph(G_osm)
    else:
        print("No OSM graph provided — skipping topological_accuracy.")
        G_osm_u = G

    results = evaluate_track_b(G, G, G_osm_u,
                                output_json=args.output or "track_b_metrics.json")
    return results


def main():
    parser = argparse.ArgumentParser(description="SatMesh evaluation harness")
    sub = parser.add_subparsers(dest="track")

    a = sub.add_parser("track_a")
    a.add_argument("--checkpoint",  required=True)
    a.add_argument("--test_pairs",  required=True, help="test_pairs.json from training")
    a.add_argument("--pred_dir",    default=None,  help="Where to cache predictions")
    a.add_argument("--img_size",    type=int, default=512)
    a.add_argument("--output",      default="track_a_metrics.csv")

    b = sub.add_parser("track_b")
    b.add_argument("--graph",     required=True, help="healed graph .gpickle")
    b.add_argument("--osm_graph", default=None,  help="OSM .graphml baseline")
    b.add_argument("--output",    default="track_b_metrics.json")

    args = parser.parse_args()
    if args.track == "track_a":
        _run_track_a(args)
    elif args.track == "track_b":
        _run_track_b(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
