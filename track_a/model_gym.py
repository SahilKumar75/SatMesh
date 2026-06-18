"""
track_a/model_gym.py — controlled ablation gym for SatMesh Track A.

Goal: answer ONE question the PS4 judges care about —
    which lever most improves Occlusion-Recall (roads recovered under shadow)?

Arms (each trained identically, only the named lever changes):
    baseline     U-Net + ResNet34, Dice+BCE loss,        no occlusion aug
    cldice       U-Net + ResNet34, Dice+BCE+clDice loss,  occlusion aug
    transformer  SegFormer (MiT-b0), Dice+BCE+clDice,     occlusion aug   [PS4 Objective 1]
    eo_pretrained (optional) U-Net + EO-pretrained encoder, clDice, occ aug

Speed: AMP mixed precision + lean "gym config" (IMG 384, batch 8, 15 epochs,
       1500 train imgs) → ~8-10 min/arm on an L4, vs ~30 min full-fat.

Evaluation: held-out test split (never seen in training), scored on
    IoU, Dice, Relaxed-IoU (3px), and Occlusion-Recall.
Outputs: gym_results.csv + gym_results.md (the ablation table for the proposal).

Usage:
    python track_a/model_gym.py                      # run baseline + cldice + transformer
    python track_a/model_gym.py --arms baseline cldice
    python track_a/model_gym.py --epochs 12 --train_n 1200 --img 384
"""

from __future__ import annotations
import argparse, json, os, glob, random, time
from dataclasses import dataclass

import numpy as np
import cv2
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import albumentations as A
from albumentations.pytorch import ToTensorV2
import segmentation_models_pytorch as smp

# reuse the judge metrics so the gym and eval/metrics.py never disagree
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from eval.metrics import (
    iou_score, dice_score, relaxed_iou,
    simulate_occlusion_mask, occlusion_recall,
)

SEED = 42
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)

DEVICE = "cuda" if torch.cuda.is_available() else (
    "mps" if torch.backends.mps.is_available() else "cpu")


# ── clDice loss (differentiable soft skeleton) ────────────────────────────────

def _soft_erode(x):  return -F.max_pool2d(-x, 3, 1, 1)
def _soft_dilate(x): return  F.max_pool2d( x, 3, 1, 1)

def soft_skel(x, iters=3):
    skel = F.relu(x - _soft_dilate(_soft_erode(x)))
    for _ in range(iters - 1):
        x = _soft_erode(x)
        d = F.relu(x - _soft_dilate(_soft_erode(x)))
        skel = skel + F.relu(d - skel * d)
    return skel

def cl_dice_loss(logits, target, iters=3, smooth=1.0):
    pred = torch.sigmoid(logits)
    sp, st = soft_skel(pred, iters), soft_skel(target, iters)
    tp = ((sp * target).sum() + smooth) / (sp.sum() + smooth)
    ts = ((st * pred).sum()   + smooth) / (st.sum()   + smooth)
    return 1.0 - 2.0 * tp * ts / (tp + ts)


# ── Data ──────────────────────────────────────────────────────────────────────

def discover_pairs():
    data_dir = None
    for root, _, files in os.walk("."):
        if any(f.endswith("_sat.jpg") for f in files):
            data_dir = root; break
    if data_dir is None:
        raise FileNotFoundError("No *_sat.jpg found under current dir (run from SatMesh root)")
    sat = sorted(glob.glob(os.path.join(data_dir, "*_sat.jpg")))
    pairs = [(p, p.replace("_sat.jpg", "_mask.png")) for p in sat
             if os.path.exists(p.replace("_sat.jpg", "_mask.png"))]
    random.Random(SEED).shuffle(pairs)
    return pairs


def make_tfs(img, occ_aug: bool):
    base = [A.Resize(img, img), A.HorizontalFlip(p=0.5), A.VerticalFlip(p=0.3),
            A.RandomRotate90(p=0.5)]
    if occ_aug:
        base += [
            A.RandomShadow(p=0.4),
            A.CoarseDropout(num_holes_range=(2, 12), hole_height_range=(8, 40),
                            hole_width_range=(8, 40), fill=0, p=0.5),
            A.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1, p=0.4),
        ]
    train_tf = A.Compose(base + [A.Normalize(), ToTensorV2()])
    val_tf   = A.Compose([A.Resize(img, img), A.Normalize(), ToTensorV2()])
    return train_tf, val_tf


class RoadDS(Dataset):
    def __init__(self, items, tf):
        self.items, self.tf = items, tf
    def __len__(self):
        return len(self.items)
    def __getitem__(self, i):
        sp, mp = self.items[i]
        img = cv2.cvtColor(cv2.imread(sp), cv2.COLOR_BGR2RGB)
        msk = (cv2.imread(mp, cv2.IMREAD_GRAYSCALE) > 127).astype("float32")
        a = self.tf(image=img, mask=msk)
        return a["image"], a["mask"].unsqueeze(0)


# ── Arm definition ─────────────────────────────────────────────────────────────

@dataclass
class Arm:
    name: str
    arch: str          # "unet" | "segformer"
    encoder: str       # e.g. "resnet34", "mit_b0"
    use_cldice: bool
    occ_aug: bool
    encoder_weights: str = "imagenet"


ARMS = {
    "baseline":    Arm("baseline",    "unet",      "resnet34", use_cldice=False, occ_aug=False),
    "cldice":      Arm("cldice",      "unet",      "resnet34", use_cldice=True,  occ_aug=True),
    "transformer": Arm("transformer", "segformer", "mit_b0",   use_cldice=True,  occ_aug=True),
    # eo_pretrained is filled in after NotebookLM picks a remote-sensing encoder
}


def build_model(arm: Arm) -> nn.Module:
    kw = dict(encoder_name=arm.encoder, encoder_weights=arm.encoder_weights,
              in_channels=3, classes=1)
    if arm.arch == "segformer":
        return smp.Segformer(**kw)
    return smp.Unet(**kw)


# ── Train + evaluate one arm ───────────────────────────────────────────────────

def train_arm(arm: Arm, train_pairs, val_pairs, img, batch, epochs, cldice_iters):
    train_tf, val_tf = make_tfs(img, arm.occ_aug)
    pin = (DEVICE == "cuda")
    train_dl = DataLoader(RoadDS(train_pairs, train_tf), batch_size=batch,
                          shuffle=True, num_workers=2, pin_memory=pin, drop_last=True)
    val_dl   = DataLoader(RoadDS(val_pairs, val_tf), batch_size=batch,
                          shuffle=False, num_workers=2, pin_memory=pin)

    model = build_model(arm).to(DEVICE)
    dice_loss = smp.losses.DiceLoss(mode="binary")
    bce_loss  = nn.BCEWithLogitsLoss()
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.OneCycleLR(
        opt, max_lr=1e-3, steps_per_epoch=len(train_dl), epochs=epochs)
    scaler = torch.cuda.amp.GradScaler(enabled=(DEVICE == "cuda"))

    best_iou, best_state = 0.0, None
    for ep in range(1, epochs + 1):
        model.train()
        for x, y in train_dl:
            x, y = x.to(DEVICE), y.to(DEVICE)
            opt.zero_grad()
            with torch.autocast(device_type="cuda", enabled=(DEVICE == "cuda")):
                out = model(x)
                loss = 0.4 * dice_loss(out, y) + 0.3 * bce_loss(out, y)
                if arm.use_cldice:
                    loss = loss + 0.3 * cl_dice_loss(out.float(), y, iters=cldice_iters)
            scaler.scale(loss).backward()
            scaler.step(opt); scaler.update(); sched.step()

        # quick val IoU
        model.eval(); ious = []
        with torch.no_grad():
            for x, y in val_dl:
                x, y = x.to(DEVICE), y.to(DEVICE)
                p = (torch.sigmoid(model(x)) > 0.5).float()
                inter = (p * y).sum((1, 2, 3))
                union = ((p + y) > 0).float().sum((1, 2, 3))
                ious.append(((inter + 1e-6) / (union + 1e-6)).mean().item())
        vi = float(np.mean(ious))
        print(f"    [{arm.name}] ep {ep:2d}/{epochs}  val_IoU {vi:.4f}")
        if vi > best_iou:
            best_iou = vi
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}

    if best_state:
        model.load_state_dict(best_state)
    return model, best_iou


@torch.no_grad()
def eval_on_test(model, test_pairs, img, threshold=0.5):
    """Score on the held-out test set with the PS4 judge metrics."""
    model.eval()
    _, val_tf = make_tfs(img, occ_aug=False)
    rows = {"iou": [], "dice": [], "relaxed_iou": [], "occlusion_recall": []}
    for sp, mp in test_pairs:
        raw = cv2.imread(sp)
        gt  = (cv2.imread(mp, cv2.IMREAD_GRAYSCALE) > 127).astype(np.uint8)
        rgb = cv2.cvtColor(raw, cv2.COLOR_BGR2RGB)
        t = val_tf(image=rgb)["image"].unsqueeze(0).to(DEVICE)
        with torch.autocast(device_type="cuda", enabled=(DEVICE == "cuda")):
            prob = torch.sigmoid(model(t))[0, 0].float().cpu().numpy()
        pred = (prob > threshold).astype(np.uint8)
        if pred.shape != gt.shape:
            pred = cv2.resize(pred, (gt.shape[1], gt.shape[0]), interpolation=cv2.INTER_NEAREST)
        occ = simulate_occlusion_mask(raw)
        rows["iou"].append(iou_score(pred, gt))
        rows["dice"].append(dice_score(pred, gt))
        rows["relaxed_iou"].append(relaxed_iou(pred, gt, buffer_px=3))
        rows["occlusion_recall"].append(occlusion_recall(pred, gt, occ))
    return {k: float(np.mean(v)) for k, v in rows.items()}


# ── Gym runner ─────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="SatMesh model gym")
    ap.add_argument("--arms", nargs="+", default=["baseline", "cldice", "transformer"],
                    help="which arms to run")
    ap.add_argument("--img", type=int, default=384)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--epochs", type=int, default=15)
    ap.add_argument("--train_n", type=int, default=1500, help="training images per arm")
    ap.add_argument("--cldice_iters", type=int, default=3)
    ap.add_argument("--out", default="gym_results")
    args = ap.parse_args()

    print(f"Device: {DEVICE}")
    if DEVICE == "cuda":
        print(f"GPU: {torch.cuda.get_device_name(0)}")

    pairs = discover_pairs()
    # deterministic split — test set matches the main training run (shuffled[2700:3000])
    test_pairs  = pairs[2700:3000]
    val_pairs   = pairs[2400:2700]
    train_pairs = pairs[:args.train_n]
    print(f"train {len(train_pairs)}  val {len(val_pairs)}  test {len(test_pairs)}")

    results = []
    for name in args.arms:
        if name not in ARMS:
            print(f"  ! unknown arm '{name}', skipping"); continue
        arm = ARMS[name]
        print(f"\n=== arm: {arm.name}  ({arm.arch}/{arm.encoder}, "
              f"clDice={arm.use_cldice}, occ_aug={arm.occ_aug}) ===")
        t0 = time.time()
        model, best_val = train_arm(arm, train_pairs, val_pairs,
                                    args.img, args.batch, args.epochs, args.cldice_iters)
        metrics = eval_on_test(model, test_pairs, args.img)
        dt = time.time() - t0
        row = {"arm": arm.name, "val_iou": round(best_val, 4),
               **{k: round(v, 4) for k, v in metrics.items()},
               "minutes": round(dt / 60, 1)}
        results.append(row)
        print(f"    test: IoU {row['iou']}  Dice {row['dice']}  "
              f"RelaxedIoU {row['relaxed_iou']}  OccRecall {row['occlusion_recall']}  "
              f"({row['minutes']} min)")

    # write CSV + markdown table
    if results:
        import csv
        keys = ["arm", "iou", "dice", "relaxed_iou", "occlusion_recall", "val_iou", "minutes"]
        with open(f"{args.out}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(results)
        with open(f"{args.out}.md", "w") as f:
            f.write("# SatMesh Model Gym — Track A Ablation\n\n")
            f.write("Held-out test set. Headline metric: **Occlusion-Recall** "
                    "(roads recovered under shadow).\n\n")
            f.write("| Arm | IoU | Dice | Relaxed IoU | **Occlusion-Recall** | val IoU | min |\n")
            f.write("|---|---|---|---|---|---|---|\n")
            for r in results:
                f.write(f"| {r['arm']} | {r['iou']} | {r['dice']} | {r['relaxed_iou']} "
                        f"| **{r['occlusion_recall']}** | {r['val_iou']} | {r['minutes']} |\n")
        print(f"\nWrote {args.out}.csv and {args.out}.md")
        print("\nGym summary:")
        for r in results:
            print(f"  {r['arm']:<12} OccRecall={r['occlusion_recall']}  "
                  f"RelaxedIoU={r['relaxed_iou']}  IoU={r['iou']}")


if __name__ == "__main__":
    main()
