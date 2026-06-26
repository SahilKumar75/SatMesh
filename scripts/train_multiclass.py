#!/usr/bin/env python3
"""Train SegFormer for 4-class semantic segmentation on the multiclass dataset.

Classes:  0=background  1=road  2=tree  3=shadow

Built for Lightning AI (A10G / A100). No /kaggle/ paths.
Saves best checkpoint by road IoU (class 1) — the PS4 primary metric.

Example (Lightning AI Studio terminal):
    python scripts/train_multiclass.py \\
        --data data/india_multiclass/train \\
        --out  checkpoints/segformer_v3_multiclass.pth \\
        --encoder mit_b4 --epochs 40 --batch 8

Warm-start from binary checkpoint (skips head, transfers encoder+decoder):
    python scripts/train_multiclass.py \\
        --data  data/india_multiclass/train \\
        --out   checkpoints/segformer_v3_multiclass.pth \\
        --resume checkpoints/segformer_india_v2.pth \\
        --encoder mit_b4 --epochs 30 --batch 8
"""
import argparse
import random
import sys
from pathlib import Path

import albumentations as A
import cv2
import numpy as np
import torch
import torch.nn.functional as F
from albumentations.pytorch import ToTensorV2
from torch.utils.data import DataLoader, Dataset, Subset

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.model.segformer import build_segformer_multiclass
from src.model.train import CanopyOcclusionOnRoad   # reuse synthetic occlusion aug

NUM_CLASSES = 4
ROAD_CLASS  = 1

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD  = [0.229, 0.224, 0.225]


# ── dataset ───────────────────────────────────────────────────────────────────

class MulticlassRoadDS(Dataset):
    """Reads *_sat.jpg + *_mask.png (values 0-3) pairs from data_dir."""

    def __init__(self, data_dir, img_size=512, augment=True, subset=None):
        self.data_dir = Path(data_dir)
        self.augment  = augment
        self.canopy   = CanopyOcclusionOnRoad()

        sat_files = sorted(self.data_dir.glob("*_sat.jpg"))
        self.samples = [
            (f, self.data_dir / (f.stem.replace("_sat", "_mask") + ".png"))
            for f in sat_files
        ]
        self.samples = [(s, m) for s, m in self.samples if m.exists()]

        if subset and subset < len(self.samples):
            random.Random(42).shuffle(self.samples)
            self.samples = self.samples[:subset]

        self.train_tf = A.Compose([
            A.RandomResizedCrop(size=(img_size, img_size), scale=(0.5, 1.0)),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.RandomRotate90(p=0.5),
            A.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05, p=0.5),
            A.GaussianBlur(blur_limit=(3, 7), p=0.2),
            A.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
            ToTensorV2(),
        ])
        self.val_tf = A.Compose([
            A.Resize(img_size, img_size),
            A.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
            ToTensorV2(),
        ])

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sat_path, mask_path = self.samples[idx]

        img_bgr = cv2.imread(str(sat_path))
        if img_bgr is None:
            raise FileNotFoundError(sat_path)
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
        if mask is None:
            raise FileNotFoundError(mask_path)

        # synthetic canopy aug: operates on the image only, masks stay intact
        # (real shadow/tree labels already in mask; aug adds extra training diversity)
        if self.augment:
            road_binary = (mask == ROAD_CLASS).astype(np.uint8) * 255
            img_rgb = self.canopy(img_rgb, road_binary)

        tf = self.train_tf if self.augment else self.val_tf
        result = tf(image=img_rgb, mask=mask)
        # mask: H×W int64 with values 0-3
        return result["image"], result["mask"].long()


# ── loss ──────────────────────────────────────────────────────────────────────

def multiclass_loss(logits, targets):
    """CrossEntropy + road-class Dice.

    CE handles all 4 classes equally; road Dice focuses extra gradient on
    the primary PS4 metric (road IoU / Occlusion-Recall).
    """
    ce = F.cross_entropy(logits, targets)

    # road Dice (binary: class 1 vs rest)
    road_prob  = torch.softmax(logits, dim=1)[:, ROAD_CLASS]
    road_gt    = (targets == ROAD_CLASS).float()
    inter = (road_prob * road_gt).sum()
    dice  = 1.0 - (2 * inter + 1e-6) / (road_prob.sum() + road_gt.sum() + 1e-6)

    return 0.6 * ce + 0.4 * dice


# ── metrics ───────────────────────────────────────────────────────────────────

@torch.no_grad()
def compute_metrics(logits, targets):
    """Returns road_iou, road_recall, mean_iou (all 4 classes)."""
    preds = logits.argmax(dim=1)   # B×H×W

    # per-class IoU
    ious = []
    for c in range(NUM_CLASSES):
        p = (preds == c)
        t = (targets == c)
        inter = (p & t).float().sum()
        union = (p | t).float().sum()
        ious.append((inter + 1e-6) / (union + 1e-6))
    mean_iou = torch.stack(ious).mean().item()

    # road-specific
    road_p = (preds == ROAD_CLASS)
    road_t = (targets == ROAD_CLASS)
    road_iou = ious[ROAD_CLASS].item()
    road_recall = ((road_p & road_t).float().sum() /
                   (road_t.float().sum() + 1e-6)).item()

    return road_iou, road_recall, mean_iou


# ── train / val loops ─────────────────────────────────────────────────────────

def train_epoch(model, loader, optimizer, scaler, device):
    model.train()
    total = 0.0
    for imgs, masks in loader:
        imgs, masks = imgs.to(device), masks.to(device)
        optimizer.zero_grad()
        with torch.amp.autocast(device_type=device.type, enabled=(device.type == "cuda")):
            loss = multiclass_loss(model(imgs), masks)
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        total += loss.item()
    return total / len(loader)


@torch.no_grad()
def validate(model, loader, device):
    model.eval()
    total_loss = total_road_iou = total_recall = total_miou = 0.0
    for imgs, masks in loader:
        imgs, masks = imgs.to(device), masks.to(device)
        with torch.amp.autocast(device_type=device.type, enabled=(device.type == "cuda")):
            logits = model(imgs)
            total_loss += multiclass_loss(logits, masks).item()
        road_iou, recall, miou = compute_metrics(logits, masks)
        total_road_iou += road_iou
        total_recall   += recall
        total_miou     += miou
    n = len(loader)
    return total_loss/n, total_road_iou/n, total_recall/n, total_miou/n


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data",     required=True, help="path to india_multiclass/train")
    ap.add_argument("--out",      default="checkpoints/segformer_v3_multiclass.pth")
    ap.add_argument("--encoder",  default="mit_b4")
    ap.add_argument("--epochs",   type=int, default=40)
    ap.add_argument("--batch",    type=int, default=8)
    ap.add_argument("--lr",       type=float, default=6e-5)
    ap.add_argument("--img-size", type=int, default=512)
    ap.add_argument("--resume",   default=None,
                    help="binary 1-class checkpoint to warm-start encoder from")
    ap.add_argument("--resume-training", default=None, metavar="STATE",
                    help="training state file (.pt) saved by a previous interrupted run")
    ap.add_argument("--subset",   type=int, default=None,
                    help="limit training samples (for quick sanity checks)")
    args = ap.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"device={device}  encoder={args.encoder}  epochs={args.epochs}  batch={args.batch}")

    model = build_segformer_multiclass(
        num_classes=NUM_CLASSES,
        checkpoint_binary=args.resume,
        device=str(device),
        encoder_name=args.encoder,
    ).to(device)

    if torch.cuda.device_count() > 1:
        print(f"DataParallel across {torch.cuda.device_count()} GPUs")
        model = torch.nn.DataParallel(model)

    # 90/10 train/val split
    full_ds = MulticlassRoadDS(args.data, args.img_size, augment=True,  subset=args.subset)
    val_ds  = MulticlassRoadDS(args.data, args.img_size, augment=False, subset=args.subset)
    n = len(full_ds)
    indices = list(range(n))
    random.Random(42).shuffle(indices)
    split = max(1, int(n * 0.1))
    train_ds = Subset(full_ds, indices[split:])
    val_ds   = Subset(val_ds,  indices[:split])
    print(f"train={len(train_ds)}  val={len(val_ds)}")

    kw = dict(num_workers=4, pin_memory=True, persistent_workers=True, prefetch_factor=2)
    train_loader = DataLoader(train_ds, batch_size=args.batch, shuffle=True,  drop_last=True, **kw)
    val_loader   = DataLoader(val_ds,   batch_size=args.batch, shuffle=False, **kw)

    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=args.epochs, eta_min=args.lr * 0.01)
    scaler = torch.amp.GradScaler(device.type, enabled=(device.type == "cuda"))

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    best_road_iou = 0.0
    start_epoch   = 1
    state_path    = Path(args.out).with_suffix(".training_state.pt")

    # Resume interrupted training (optimizer + scheduler + epoch state)
    if args.resume_training and Path(args.resume_training).exists():
        ckpt = torch.load(args.resume_training, map_location=device, weights_only=False)
        m = model.module if hasattr(model, "module") else model
        m.load_state_dict(ckpt["model"])
        optimizer.load_state_dict(ckpt["optimizer"])
        scheduler.load_state_dict(ckpt["scheduler"])
        scaler.load_state_dict(ckpt["scaler"])
        best_road_iou = ckpt["best_road_iou"]
        start_epoch   = ckpt["epoch"] + 1
        print(f"[resume] epoch {start_epoch}  best_road_iou={best_road_iou:.4f}")

    for epoch in range(start_epoch, args.epochs + 1):
        train_loss = train_epoch(model, train_loader, optimizer, scaler, device)
        scheduler.step()
        val_loss, road_iou, road_recall, miou = validate(model, val_loader, device)

        print(f"ep {epoch:3d}/{args.epochs}  "
              f"train={train_loss:.4f}  val={val_loss:.4f}  "
              f"road_iou={road_iou:.4f}  occlusion_recall={road_recall:.4f}  miou={miou:.4f}")

        if road_iou > best_road_iou:
            best_road_iou = road_iou
            state = model.module.state_dict() if hasattr(model, "module") else model.state_dict()
            torch.save(state, args.out)
            print(f"  ↑ saved (road_iou={best_road_iou:.4f})")

        # Save full training state after every epoch for spot-instance resume
        torch.save({
            "epoch":         epoch,
            "model":         model.module.state_dict() if hasattr(model, "module") else model.state_dict(),
            "optimizer":     optimizer.state_dict(),
            "scheduler":     scheduler.state_dict(),
            "scaler":        scaler.state_dict(),
            "best_road_iou": best_road_iou,
        }, state_path)

    print(f"\nDone. best road_iou={best_road_iou:.4f}  checkpoint={args.out}")
    print("Next: run inference with src/model/infer.py, extract class-1 mask → heal.py → graph")


if __name__ == "__main__":
    main()
