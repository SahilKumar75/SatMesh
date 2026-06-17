"""
PS4 — Track A: Occlusion-Robust Road Segmentation  (SatMesh / BAH 2026)
========================================================================
Upgrades over the starter script
  • CP_clDice loss   — soft-skeleton Dice that directly penalises broken
    centerlines and maps to the Occlusion-Recall metric judges score.
    Ref: Shit et al., "clDice — a Novel Topology-Preserving Loss Function
    for Tubular Structure Segmentation", CVPR 2021.
  • Occlusion augmentation — CoarseDropout + RandomShadow train the model
    to "see through" tree canopy and building shadows.
  • One-cycle LR schedule — converges faster within a 30-hour GPU budget.
  • Best-checkpoint saving — download best_model.pth after the run.
  • Dice score logged alongside IoU every epoch.
  • 80/10/10 train/val/test split; test_pairs.json written alongside checkpoint.
  • best_model_meta.json records training config for reproducibility.

HOW TO RUN (free GPU — no local setup needed):
  1. https://www.kaggle.com/datasets/balraj98/deepglobe-road-extraction-dataset
  2. New Notebook → Settings → Accelerator → GPU T4 → OK
  3. Paste this file into one cell and click Run All.  (~25 min for 20 epochs)

Local (Apple Silicon or CUDA):
  pip install -r requirements.txt
  # set DATA_DIR to your DeepGlobe train/ folder below, then:
  python track_a/road_segmentation.py
"""

# ── 0. Install if needed ─────────────────────────────────────────────────────
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                "segmentation-models-pytorch"], check=False)

import json, os, glob, random
import numpy as np
import cv2
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import albumentations as A
from albumentations.pytorch import ToTensorV2
import segmentation_models_pytorch as smp
import matplotlib.pyplot as plt

SEED = 42
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)

# MPS (Apple Silicon) support
if torch.cuda.is_available():
    DEVICE = "cuda"
elif torch.backends.mps.is_available():
    DEVICE = "mps"
else:
    DEVICE = "cpu"
print("Device:", DEVICE)

# ── 1. Locate data ───────────────────────────────────────────────────────────
DATA_DIR = None
for root, dirs, files in os.walk("/kaggle/input"):
    if root.endswith("train") and any(f.endswith("_sat.jpg") for f in files):
        DATA_DIR = root; break
if DATA_DIR is None:
    DATA_DIR = "data/deepglobe/train"   # ← change to your local path
print("Train folder:", DATA_DIR)

sat_paths = sorted(glob.glob(os.path.join(DATA_DIR, "*_sat.jpg")))
pairs = [(p, p.replace("_sat.jpg", "_mask.png")) for p in sat_paths
         if os.path.exists(p.replace("_sat.jpg", "_mask.png"))]
print(f"Found {len(pairs)} image/mask pairs.")

SUBSET = 3000
random.shuffle(pairs)
pairs = pairs[:SUBSET]

n = len(pairs)
train_pairs = pairs[:int(0.8 * n)]
val_pairs   = pairs[int(0.8 * n):int(0.9 * n)]
test_pairs  = pairs[int(0.9 * n):]
print(f"train: {len(train_pairs)}  val: {len(val_pairs)}  test: {len(test_pairs)}")

# ── 2. Dataset with occlusion augmentation ───────────────────────────────────
IMG   = 512
BATCH = 4 if DEVICE == "cuda" else 2

train_tf = A.Compose([
    A.Resize(IMG, IMG),
    A.HorizontalFlip(p=0.5),
    A.VerticalFlip(p=0.3),
    A.RandomRotate90(p=0.5),
    A.Affine(scale=(0.9, 1.1), translate_percent=0.1, rotate=(-15, 15), p=0.4),
    # occlusion simulation: shadows + rectangular canopy blackouts
    A.RandomShadow(p=0.4),
    A.CoarseDropout(num_holes_range=(2, 12), hole_height_range=(8, 40),
                    hole_width_range=(8, 40), fill=0, p=0.5),
    # colour / noise jitter
    A.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1, p=0.4),
    A.RandomGamma(gamma_limit=(80, 120), p=0.3),
    A.GaussNoise(std_range=(0.01, 0.05), p=0.3),
    A.Normalize(),
    ToTensorV2(),
])
val_tf = A.Compose([A.Resize(IMG, IMG), A.Normalize(), ToTensorV2()])


class RoadDS(Dataset):
    def __init__(self, items, tf):
        self.items, self.tf = items, tf

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        sp, mp = self.items[i]
        img = cv2.cvtColor(cv2.imread(sp), cv2.COLOR_BGR2RGB)
        msk = cv2.imread(mp, cv2.IMREAD_GRAYSCALE)
        msk = (msk > 127).astype("float32")
        a = self.tf(image=img, mask=msk)
        return a["image"], a["mask"].unsqueeze(0)


# pin_memory only works on CUDA — disabled for MPS and CPU
pin = (DEVICE == "cuda")
train_dl = DataLoader(RoadDS(train_pairs, train_tf), batch_size=BATCH,
                      shuffle=True,  num_workers=2, pin_memory=pin)
val_dl   = DataLoader(RoadDS(val_pairs,   val_tf),   batch_size=BATCH,
                      shuffle=False, num_workers=2, pin_memory=pin)

# ── 3. CP_clDice loss ────────────────────────────────────────────────────────
# Soft skeleton via iterative morphological min/max pooling (differentiable).
# clDice = 2 · Tprec · Tsens / (Tprec + Tsens)  where
#   Tprec = |skel(pred) ∩ target| / |skel(pred)|   (skeleton precision)
#   Tsens = |skel(target) ∩ pred| / |skel(target)| (skeleton sensitivity)
# Penalising broken centerlines directly optimises Occlusion-Recall.

def _soft_erode(x: torch.Tensor) -> torch.Tensor:
    return -F.max_pool2d(-x, kernel_size=3, stride=1, padding=1)


def _soft_dilate(x: torch.Tensor) -> torch.Tensor:
    return F.max_pool2d(x, kernel_size=3, stride=1, padding=1)


def soft_skel(x: torch.Tensor, iters: int = 5) -> torch.Tensor:
    """Differentiable soft skeleton via iterative opening subtraction."""
    skel = F.relu(x - _soft_dilate(_soft_erode(x)))
    for _ in range(iters - 1):
        x     = _soft_erode(x)
        delta = F.relu(x - _soft_dilate(_soft_erode(x)))
        skel  = skel + F.relu(delta - skel * delta)
    return skel


def cl_dice_loss(pred_logits: torch.Tensor, target: torch.Tensor,
                 iters: int = 5, smooth: float = 1.0) -> torch.Tensor:
    pred      = torch.sigmoid(pred_logits)
    skel_pred = soft_skel(pred,   iters)
    skel_true = soft_skel(target, iters)

    t_prec = ((skel_pred * target).sum() + smooth) / (skel_pred.sum() + smooth)
    t_sens = ((skel_true * pred).sum()   + smooth) / (skel_true.sum() + smooth)

    return 1.0 - 2.0 * t_prec * t_sens / (t_prec + t_sens)


# ── 4. Model ─────────────────────────────────────────────────────────────────
model     = smp.Unet("resnet34", encoder_weights="imagenet",
                     in_channels=3, classes=1).to(DEVICE)
dice_loss = smp.losses.DiceLoss(mode="binary")
bce_loss  = nn.BCEWithLogitsLoss()

ALPHA, BETA, GAMMA = 0.4, 0.3, 0.3   # Dice, BCE, clDice

EPOCHS = 20
opt = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
scheduler = torch.optim.lr_scheduler.OneCycleLR(
    opt, max_lr=1e-3, steps_per_epoch=len(train_dl), epochs=EPOCHS)


def batch_metrics(logits, target, thr=0.5):
    pred  = (torch.sigmoid(logits) > thr).float()
    inter = (pred * target).sum((1, 2, 3))
    union = ((pred + target) > 0).float().sum((1, 2, 3))
    iou   = ((inter + 1e-6) / (union + 1e-6)).mean().item()
    dice  = ((2 * inter + 1e-6) /
             (pred.sum((1, 2, 3)) + target.sum((1, 2, 3)) + 1e-6)).mean().item()
    return iou, dice


# ── 5. Training loop ─────────────────────────────────────────────────────────
out_dir   = "/kaggle/working" if os.path.isdir("/kaggle/working") else "."
best_path = os.path.join(out_dir, "best_model.pth")
meta_path = os.path.join(out_dir, "best_model_meta.json")
test_path = os.path.join(out_dir, "test_pairs.json")
best_iou  = 0.0

# save test split alongside checkpoint so eval/metrics.py can load it
with open(test_path, "w") as f:
    json.dump(test_pairs, f)
print(f"Test split saved → {test_path}")

for ep in range(1, EPOCHS + 1):
    model.train(); train_loss = 0.0
    for x, y in train_dl:
        x, y = x.to(DEVICE), y.to(DEVICE)
        opt.zero_grad()
        out  = model(x)
        loss = (ALPHA * dice_loss(out, y)
                + BETA  * bce_loss(out, y)
                + GAMMA * cl_dice_loss(out, y))
        loss.backward(); opt.step(); scheduler.step()
        train_loss += loss.item()

    model.eval(); all_iou, all_dice = [], []
    with torch.no_grad():
        for x, y in val_dl:
            x, y = x.to(DEVICE), y.to(DEVICE)
            iou, dice = batch_metrics(model(x), y)
            all_iou.append(iou); all_dice.append(dice)

    mean_iou  = float(np.mean(all_iou))
    mean_dice = float(np.mean(all_dice))
    print(f"epoch {ep:2d}  loss {train_loss/len(train_dl):.3f}  "
          f"val_IoU {mean_iou:.3f}  val_Dice {mean_dice:.3f}  "
          f"lr {scheduler.get_last_lr()[0]:.2e}")

    if mean_iou > best_iou:
        best_iou = mean_iou
        torch.save(model.state_dict(), best_path)
        with open(meta_path, "w") as f:
            json.dump({
                "best_val_iou": round(best_iou, 4),
                "epoch": ep,
                "img_size": IMG,
                "subset": SUBSET,
                "loss_weights": {"dice": ALPHA, "bce": BETA, "cldice": GAMMA},
                "device": DEVICE,
            }, f, indent=2)
        print(f"         ✓ new best — saved {best_path}")

print(f"\nBest val IoU: {best_iou:.3f}")

# ── 6. Visualise predictions ─────────────────────────────────────────────────
model.load_state_dict(torch.load(best_path, map_location=DEVICE, weights_only=True))
model.eval()
x, y = next(iter(val_dl))
with torch.no_grad():
    pred = (torch.sigmoid(model(x.to(DEVICE))) > 0.5).float().cpu()

MEAN = np.array([0.485, 0.456, 0.406])
STD  = np.array([0.229, 0.224, 0.225])

fig, ax = plt.subplots(3, 3, figsize=(11, 11))
for r in range(3):
    img_vis = x[r].permute(1, 2, 0).numpy() * STD + MEAN
    ax[r, 0].imshow(np.clip(img_vis, 0, 1)); ax[r, 0].set_title("satellite image")
    ax[r, 1].imshow(y[r, 0],    cmap="gray"); ax[r, 1].set_title("ground truth")
    ax[r, 2].imshow(pred[r, 0], cmap="gray"); ax[r, 2].set_title("SatMesh prediction")
    for c in range(3):
        ax[r, c].axis("off")

fig.suptitle(f"SatMesh — Road Segmentation  (val IoU {best_iou:.3f})", fontsize=13)
plt.tight_layout()
fig_path = os.path.join(out_dir, "ps4_predictions.png")
plt.savefig(fig_path, dpi=140, bbox_inches="tight")
plt.show()
print(f"Saved {fig_path}")
print("Next: python track_a/infer.py --checkpoint best_model.pth --input <image>")
