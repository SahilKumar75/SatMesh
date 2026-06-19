from __future__ import annotations
import argparse
import csv
import os
import numpy as np
import cv2


def iou_score(pred: np.ndarray, target: np.ndarray) -> float:
    p = pred > 127
    t = target > 127
    inter = (p & t).sum()
    union = (p | t).sum()
    return float(inter / (union + 1e-6))


def dice_score(pred: np.ndarray, target: np.ndarray) -> float:
    p = pred > 127
    t = target > 127
    return float(2 * (p & t).sum() / (p.sum() + t.sum() + 1e-6))


def relaxed_iou(pred: np.ndarray, target: np.ndarray, buffer_px: int = 3) -> float:
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*buffer_px+1, 2*buffer_px+1))
    t_buf = cv2.dilate((target > 127).astype(np.uint8), kernel)
    p_buf = cv2.dilate((pred > 127).astype(np.uint8), kernel)
    p = pred > 127
    t = target > 127
    tp = (p.astype(bool) & t_buf.astype(bool)).sum()
    fp = (p.astype(bool) & ~t_buf.astype(bool)).sum()
    fn = (t.astype(bool) & ~p_buf.astype(bool)).sum()
    return float(tp / (tp + fp + fn + 1e-6))


def simulate_occlusion_mask(image: np.ndarray) -> np.ndarray:
    return (image.max(axis=-1) < 50).astype(np.uint8) * 255


def occlusion_recall(pred: np.ndarray, target: np.ndarray, image: np.ndarray) -> float:
    occ = simulate_occlusion_mask(image) > 0
    road_under_occ = (target > 127) & occ
    if road_under_occ.sum() == 0:
        return 1.0
    pred_recall = (pred > 127) & road_under_occ
    return float(pred_recall.sum() / road_under_occ.sum())


def evaluate_track_a(pairs: list, pred_dir: str, output_csv: str) -> dict:
    rows = []
    for sat_path, mask_path in pairs:
        stem = os.path.splitext(os.path.basename(sat_path))[0].replace("_sat", "")
        pred_path = os.path.join(pred_dir, f"{stem}_pred.png")
        if not os.path.exists(pred_path):
            continue
        pred   = cv2.imread(pred_path, cv2.IMREAD_GRAYSCALE)
        target = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        image  = cv2.cvtColor(cv2.imread(sat_path), cv2.COLOR_BGR2RGB)
        if pred is None or target is None:
            continue
        rows.append({
            "stem": stem,
            "iou": round(iou_score(pred, target), 4),
            "dice": round(dice_score(pred, target), 4),
            "relaxed_iou": round(relaxed_iou(pred, target), 4),
            "occlusion_recall": round(occlusion_recall(pred, target, image), 4),
        })

    if output_csv and rows:
        with open(output_csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    if not rows:
        return {}
    return {
        "mean_iou": round(np.mean([r["iou"] for r in rows]), 4),
        "mean_dice": round(np.mean([r["dice"] for r in rows]), 4),
        "mean_relaxed_iou": round(np.mean([r["relaxed_iou"] for r in rows]), 4),
        "mean_occlusion_recall": round(np.mean([r["occlusion_recall"] for r in rows]), 4),
        "n_images": len(rows),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sat_dir", required=True)
    ap.add_argument("--mask_dir", required=True)
    ap.add_argument("--pred_dir", required=True)
    ap.add_argument("--output_csv", default="eval/results_track_a.csv")
    args = ap.parse_args()

    import glob
    sat_files = sorted(glob.glob(os.path.join(args.sat_dir, "*_sat.jpg")))
    pairs = [(s, os.path.join(args.mask_dir, os.path.basename(s).replace("_sat.jpg", "_mask.png")))
             for s in sat_files]
    pairs = [(s, m) for s, m in pairs if os.path.exists(m)]

    results = evaluate_track_a(pairs, args.pred_dir, args.output_csv)
    import json
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
