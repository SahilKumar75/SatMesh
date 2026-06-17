"""
PS4 — Track A: Road segmentation baseline on the DeepGlobe dataset.
=================================================================
This is your "the CV half works" proof of concept. It trains a U-Net to turn a
satellite image into a road map, then shows image vs. predicted roads + an IoU score.

HOW TO RUN (easiest = no download, free GPU):
  1. Open the DeepGlobe dataset on Kaggle:
     https://www.kaggle.com/datasets/balraj98/deepglobe-road-extraction-dataset
  2. Click "New Notebook" (the dataset is auto-attached under /kaggle/input/).
  3. In the notebook: Settings -> Accelerator -> GPU (T4).
  4. Paste this whole file into one cell and Run. ~10-15 min for a quick result.

You can also run locally if you downloaded the data — just set DATA_DIR below.
"""

# ---------------------------------------------------------------
# 0. Install the one library Kaggle doesn't ship (torch/albumentations are preinstalled)
# ---------------------------------------------------------------
import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                "segmentation-models-pytorch"], check=False)

import os, glob, random
import numpy as np
import cv2
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import albumentations as A
from albumentations.pytorch import ToTensorV2
import segmentation_models_pytorch as smp
import matplotlib.pyplot as plt

random.seed(1); np.random.seed(1); torch.manual_seed(1)
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print("Device:", DEVICE)

# ---------------------------------------------------------------
# 1. Find the data and build the list of (image, mask) pairs
#    DeepGlobe 'train' has pairs:  <id>_sat.jpg  and  <id>_mask.png
# ---------------------------------------------------------------
# Auto-locate the train folder under /kaggle/input (or set DATA_DIR yourself)
DATA_DIR = None
for root, dirs, files in os.walk("/kaggle/input"):
    if root.endswith("train") and any(f.endswith("_sat.jpg") for f in files):
        DATA_DIR = root; break
if DATA_DIR is None:
    DATA_DIR = "deepglobe/train"   # <- local fallback: change to your path
print("Train folder:", DATA_DIR)

sat_paths = sorted(glob.glob(os.path.join(DATA_DIR, "*_sat.jpg")))
pairs = [(p, p.replace("_sat.jpg", "_mask.png")) for p in sat_paths
         if os.path.exists(p.replace("_sat.jpg", "_mask.png"))]
print(f"Found {len(pairs)} image/mask pairs.")

# Use a subset for a fast demo (plenty to prove it works). Raise later for accuracy.
SUBSET = 800
random.shuffle(pairs)
pairs = pairs[:SUBSET]
split = int(0.8 * len(pairs))
train_pairs, val_pairs = pairs[:split], pairs[split:]
print(f"train: {len(train_pairs)}  val: {len(val_pairs)}")

# ---------------------------------------------------------------
# 2. Dataset: read image + mask, resize, normalize
# ---------------------------------------------------------------
IMG = 256  # image size; 256 is fast, 512 is sharper but slower

train_tf = A.Compose([
    A.Resize(IMG, IMG),
    A.HorizontalFlip(p=0.5),
    A.RandomRotate90(p=0.5),
    A.Normalize(),            # ImageNet mean/std
    ToTensorV2(),
])
val_tf = A.Compose([A.Resize(IMG, IMG), A.Normalize(), ToTensorV2()])

class RoadDS(Dataset):
    def __init__(self, items, tf): self.items, self.tf = items, tf
    def __len__(self): return len(self.items)
    def __getitem__(self, i):
        sp, mp = self.items[i]
        img = cv2.cvtColor(cv2.imread(sp), cv2.COLOR_BGR2RGB)
        msk = cv2.imread(mp, cv2.IMREAD_GRAYSCALE)
        msk = (msk > 127).astype("float32")          # road=1, background=0
        a = self.tf(image=img, mask=msk)
        return a["image"], a["mask"].unsqueeze(0)     # mask -> (1,H,W)

train_dl = DataLoader(RoadDS(train_pairs, train_tf), batch_size=8, shuffle=True,  num_workers=2)
val_dl   = DataLoader(RoadDS(val_pairs,   val_tf),   batch_size=8, shuffle=False, num_workers=2)

# ---------------------------------------------------------------
# 3. Model: U-Net with a pretrained ResNet34 encoder
# ---------------------------------------------------------------
model = smp.Unet("resnet34", encoder_weights="imagenet", in_channels=3, classes=1).to(DEVICE)
dice_loss = smp.losses.DiceLoss(mode="binary")
bce_loss  = nn.BCEWithLogitsLoss()
opt = torch.optim.Adam(model.parameters(), lr=1e-3)

def iou_score(logits, target, thr=0.5):
    pred = (torch.sigmoid(logits) > thr).float()
    inter = (pred * target).sum((1, 2, 3))
    union = ((pred + target) > 0).float().sum((1, 2, 3))
    return ((inter + 1e-6) / (union + 1e-6)).mean().item()

# ---------------------------------------------------------------
# 4. Train
# ---------------------------------------------------------------
EPOCHS = 6
for ep in range(1, EPOCHS + 1):
    model.train(); tl = 0
    for x, y in train_dl:
        x, y = x.to(DEVICE), y.to(DEVICE)
        opt.zero_grad()
        out = model(x)
        loss = dice_loss(out, y) + bce_loss(out, y)
        loss.backward(); opt.step()
        tl += loss.item()
    # validate
    model.eval(); ious = []
    with torch.no_grad():
        for x, y in val_dl:
            x, y = x.to(DEVICE), y.to(DEVICE)
            ious.append(iou_score(model(x), y))
    print(f"epoch {ep:2d}  train_loss {tl/len(train_dl):.3f}  val_IoU {np.mean(ious):.3f}")

# ---------------------------------------------------------------
# 5. Show results: image | ground-truth roads | predicted roads
#    (this figure is your proof-of-concept screenshot for the proposal)
# ---------------------------------------------------------------
model.eval()
x, y = next(iter(val_dl))
with torch.no_grad():
    pred = (torch.sigmoid(model(x.to(DEVICE))) > 0.5).float().cpu()

mean = np.array([0.485, 0.456, 0.406]); std = np.array([0.229, 0.224, 0.225])
fig, ax = plt.subplots(3, 3, figsize=(11, 11))
for r in range(3):
    img = x[r].permute(1, 2, 0).numpy() * std + mean
    ax[r, 0].imshow(np.clip(img, 0, 1));      ax[r, 0].set_title("satellite image")
    ax[r, 1].imshow(y[r, 0], cmap="gray");    ax[r, 1].set_title("real roads (ground truth)")
    ax[r, 2].imshow(pred[r, 0], cmap="gray"); ax[r, 2].set_title("predicted roads (model)")
    for c in range(3): ax[r, c].axis("off")
plt.tight_layout()
plt.savefig("/kaggle/working/ps4_predictions.png", dpi=140, bbox_inches="tight")
plt.show()
print("Saved /kaggle/working/ps4_predictions.png  <- download this for the proposal")
print("\nDone. If the right column roughly matches the middle column, the CV half works.")
print("Next: feed a predicted road mask into the Track B graph script (ps4_data_check.py).")
