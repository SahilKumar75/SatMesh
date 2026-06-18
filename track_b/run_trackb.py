"""
track_b/run_trackb.py — end-to-end Track B demo from a trained gym checkpoint.

Loads a model (default: the DADE arm), predicts a road mask on a dense-urban
test tile, heals it into a routable graph, and runs the criticality / resilience
analysis. Pixel-grid coordinates (no geo-referencing) — proves the whole Track B
pipeline and produces the Resilience Index + gatekeeper outputs.

Usage:
    python track_b/run_trackb.py                         # DADE checkpoint, auto-pick tile
    python track_b/run_trackb.py --ckpt dade_best.pth --arm dade
    python track_b/run_trackb.py --image data/deepglobe/train/100034_sat.jpg
"""

from __future__ import annotations
import argparse, os, sys
import cv2
import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from track_a.model_gym import build_model, ARMS, discover_pairs, make_tfs, DEVICE
from track_a.infer import postprocess_mask
from track_b.heal import run_heal_pipeline
from track_b.criticality import run_criticality


def pick_dense_tile(n_scan=40):
    """From the held-out test split, pick the tile with the most road content."""
    pairs = discover_pairs()
    test = pairs[2700:3000]
    best, best_frac = None, -1.0
    for sp, mp in test[:n_scan]:
        g = cv2.imread(mp, cv2.IMREAD_GRAYSCALE)
        if g is None:
            continue
        frac = (g > 127).mean()
        if frac > best_frac:
            best, best_frac = (sp, mp), frac
    return best, best_frac


@torch.no_grad()
def predict_mask(model, image_path, img=384, threshold=0.5):
    raw = cv2.imread(image_path)
    h, w = raw.shape[:2]
    rgb = cv2.cvtColor(raw, cv2.COLOR_BGR2RGB)
    _, val_tf = make_tfs(img, occ_aug=False)
    t = val_tf(image=rgb)["image"].unsqueeze(0).to(DEVICE)
    with torch.autocast(device_type="cuda", enabled=(DEVICE == "cuda")):
        prob = torch.sigmoid(model(t))[0, 0].float().cpu().numpy()
    mask = (prob > threshold).astype(np.uint8) * 255
    if (h, w) != (img, img):
        mask = cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST)
    return postprocess_mask(mask)


def main():
    ap = argparse.ArgumentParser(description="SatMesh Track B end-to-end demo")
    ap.add_argument("--ckpt", default="dade_best.pth")
    ap.add_argument("--arm", default="dade", help="architecture of the checkpoint")
    ap.add_argument("--image", default=None, help="specific tile; default auto-picks densest")
    ap.add_argument("--img", type=int, default=384)
    ap.add_argument("--threshold", type=float, default=0.5)
    ap.add_argument("--pixel_m", type=float, default=0.5)
    ap.add_argument("--max_gap_m", type=float, default=50.0)
    ap.add_argument("--out", default="outputs/trackb")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    print(f"Device: {DEVICE}")

    # 1. model
    model = build_model(ARMS[args.arm]).to(DEVICE)
    model.load_state_dict(torch.load(args.ckpt, map_location=DEVICE, weights_only=True))
    model.eval()
    print(f"[trackb] loaded {args.ckpt} ({args.arm})")

    # 2. pick / load tile
    if args.image:
        image_path = args.image
    else:
        (image_path, _), frac = pick_dense_tile()
        print(f"[trackb] auto-picked tile {os.path.basename(image_path)} (road frac {frac:.3f})")

    # 3. predict mask
    mask = predict_mask(model, image_path, args.img, args.threshold)
    mask_path = os.path.join(args.out, "road_mask.png")
    cv2.imwrite(mask_path, mask)
    print(f"[trackb] mask -> {mask_path}  (road px {np.mean(mask>127):.3f})")

    # 4. heal into a graph (pixel grid)
    graph_path = os.path.join(args.out, "healed_graph.gpickle")
    G = run_heal_pipeline(mask_path, graph_path, pixel_m=args.pixel_m,
                          max_gap_m=args.max_gap_m)

    # 5. criticality / resilience
    if G.number_of_nodes() < 3:
        print("[trackb] graph too small for criticality — try a denser tile or lower threshold")
        return
    results = run_criticality(graph_path, args.out, max_removals=10)

    # 6. summary
    abl = results.get("ablation", [])
    print("\n=== Track B summary ===")
    print(f"  graph:        {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    synth = sum(1 for _, _, d in G.edges(data=True) if d.get('synthetic'))
    print(f"  healed edges: {synth} synthetic bridges added")
    if abl:
        last = abl[-1]
        print(f"  after removing top {last['n_removed']} gatekeeper nodes:")
        print(f"     LCC fraction      {last['lcc_fraction']:.3f}")
        print(f"     Resilience Index  {last['resilience_index']:.3f}  (lower = more vulnerable)")
    print(f"\n  outputs in {args.out}/: road_mask.png, healed_graph.gpickle, "
          f"resilience_curve.png, criticality.json")


if __name__ == "__main__":
    main()
