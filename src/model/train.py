import os
import random
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import albumentations as A
from albumentations.pytorch import ToTensorV2
import yaml

from .dlinknet import build_dlinknet
from .loss import combined_loss


DEFAULT_CONFIG = {
    "stage1": {
        "data_dir": "data/deepglobe/train",
        "epochs": 30,
        "batch": 8,
        "lr": 1e-3,
        "img_size": 512,
        "subset": 5000,
        "use_nir": False,
        "checkpoint_out": "checkpoints/stage1.pth",
    },
    "stage2": {
        "data_dir": "data/sentinel2_india/train",
        "epochs": 20,
        "batch": 4,
        "lr": 2e-4,
        "img_size": 512,
        "subset": None,
        "use_nir": True,
        "checkpoint_in": "checkpoints/stage1.pth",
        "checkpoint_out": "checkpoints/dlinknet_india.pth",
    },
}


class CanopyOcclusionOnRoad:
    def __init__(self, num_blobs=(4, 20), blob_r=(10, 50), p=0.5):
        self.num_blobs = num_blobs
        self.blob_r = blob_r
        self.p = p

    def __call__(self, image, mask_u8):
        if random.random() > self.p:
            return image
        ys, xs = np.where(mask_u8 > 127)
        if len(ys) == 0:
            return image
        out = image.copy()
        n = random.randint(*self.num_blobs)
        idx = np.random.choice(len(ys), size=min(n, len(ys)), replace=True)
        for i in idx:
            cx, cy = int(xs[i]), int(ys[i])
            rx = random.randint(*self.blob_r)
            ry = random.randint(*self.blob_r)
            color = (
                random.randint(20, 65),
                random.randint(75, 155),
                random.randint(15, 60),
            )
            cv2.ellipse(out, (cx, cy), (rx, ry), random.uniform(0, 180), 0, 360, color, -1)
        return out


class RoadDS(Dataset):
    def __init__(self, data_dir, img_size=512, use_nir=False, subset=None, augment=True):
        self.data_dir = Path(data_dir)
        self.img_size = img_size
        self.use_nir = use_nir
        self.augment = augment
        self.canopy_aug = CanopyOcclusionOnRoad()

        sat_files = sorted(self.data_dir.glob("*_sat.jpg"))
        if not sat_files:
            sat_files = sorted(self.data_dir.glob("*_sat.png"))
        self.samples = [(f, self.data_dir / (f.stem.replace("_sat", "_mask") + ".png"))
                        for f in sat_files]
        self.samples = [(s, m) for s, m in self.samples if m.exists()]

        if subset is not None and subset < len(self.samples):
            random.shuffle(self.samples)
            self.samples = self.samples[:subset]

        self.train_tf = A.Compose([
            A.RandomResizedCrop(img_size, img_size, scale=(0.5, 1.0)),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.RandomRotate90(p=0.5),
            A.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05, p=0.5),
            A.GaussianBlur(blur_limit=(3, 7), p=0.2),
            A.Normalize(
                mean=[0.485, 0.456, 0.406, 0.4] if use_nir else [0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225, 0.2] if use_nir else [0.229, 0.224, 0.225],
            ),
            ToTensorV2(),
        ])
        self.val_tf = A.Compose([
            A.Resize(img_size, img_size),
            A.Normalize(
                mean=[0.485, 0.456, 0.406, 0.4] if use_nir else [0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225, 0.2] if use_nir else [0.229, 0.224, 0.225],
            ),
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

        if self.augment:
            img_rgb = self.canopy_aug(img_rgb, mask)

        if self.use_nir:
            nir_path = sat_path.parent / (sat_path.stem.replace("_sat", "_nir") + ".tif")
            if nir_path.exists():
                import rasterio
                with rasterio.open(str(nir_path)) as src:
                    nir = src.read(1).astype(np.float32)
                if nir.max() > 1.0:
                    nir = nir / 10000.0
                nir = cv2.resize(nir, (img_rgb.shape[1], img_rgb.shape[0]))
            else:
                r = img_rgb[..., 0].astype(np.float32) / 255.0
                g = img_rgb[..., 1].astype(np.float32) / 255.0
                b = img_rgb[..., 2].astype(np.float32) / 255.0
                nir = np.clip(2 * g - r - b, 0.0, 1.0)
            image = np.concatenate([img_rgb, nir[..., None]], axis=-1).astype(np.float32)
            image[..., :3] = image[..., :3] / 255.0
        else:
            image = img_rgb

        mask_f = (mask > 127).astype(np.float32)

        tf = self.train_tf if self.augment else self.val_tf
        result = tf(image=image, mask=mask_f)
        return result["image"], result["mask"].unsqueeze(0)


def _make_loader(cfg, augment):
    ds = RoadDS(
        data_dir=cfg["data_dir"],
        img_size=cfg["img_size"],
        use_nir=cfg["use_nir"],
        subset=cfg.get("subset"),
        augment=augment,
    )
    return DataLoader(
        ds,
        batch_size=cfg["batch"],
        shuffle=augment,
        num_workers=4,
        pin_memory=True,
        drop_last=augment,
    )


def _iou(pred_bin, target):
    inter = (pred_bin & target).float().sum()
    union = (pred_bin | target).float().sum()
    return (inter + 1e-6) / (union + 1e-6)


def _dice_coef(pred_bin, target):
    inter = (pred_bin & target).float().sum()
    return (2 * inter + 1e-6) / (pred_bin.float().sum() + target.float().sum() + 1e-6)


def train_one_epoch(model, loader, optimizer, scaler, device):
    model.train()
    total_loss = 0.0
    for imgs, masks in loader:
        imgs, masks = imgs.to(device), masks.to(device)
        optimizer.zero_grad()
        with torch.cuda.amp.autocast():
            logits = model(imgs)
            loss = combined_loss(logits, masks)
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        total_loss += loss.item()
    return total_loss / len(loader)


@torch.no_grad()
def validate(model, loader, device):
    model.eval()
    total_loss = total_iou = total_dice = 0.0
    for imgs, masks in loader:
        imgs, masks = imgs.to(device), masks.to(device)
        with torch.cuda.amp.autocast():
            logits = model(imgs)
            loss = combined_loss(logits, masks)
        pred_bin = (torch.sigmoid(logits) > 0.5)
        target_bin = (masks > 0.5)
        total_loss += loss.item()
        total_iou += _iou(pred_bin, target_bin).item()
        total_dice += _dice_coef(pred_bin, target_bin).item()
    n = len(loader)
    return total_loss / n, total_iou / n, total_dice / n


def run_stage(config, stage):
    cfg = config[stage]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    in_channels = 4 if cfg["use_nir"] else 3

    if stage == "stage2" and "checkpoint_in" in cfg and os.path.exists(cfg["checkpoint_in"]):
        model = build_dlinknet(pretrained=False, in_channels=4)
        state = torch.load(cfg["checkpoint_in"], map_location=device, weights_only=True)
        model.load_state_dict(state, strict=False)
        if in_channels == 3:
            old = model.base.encoder.conv1
            new = nn.Conv2d(3, old.out_channels, old.kernel_size, old.stride, old.padding, bias=False)
            with torch.no_grad():
                new.weight[:] = old.weight[:, :3]
            model.base.encoder.conv1 = new
    else:
        model = build_dlinknet(pretrained=True, in_channels=in_channels)

    model = model.to(device)

    n = len(RoadDS(cfg["data_dir"], cfg["img_size"], cfg["use_nir"], cfg.get("subset"), augment=False))
    split = max(1, int(n * 0.1))
    train_size = n - split

    full_ds = RoadDS(cfg["data_dir"], cfg["img_size"], cfg["use_nir"], cfg.get("subset"), augment=True)
    val_ds = RoadDS(cfg["data_dir"], cfg["img_size"], cfg["use_nir"], cfg.get("subset"), augment=False)

    from torch.utils.data import Subset
    indices = list(range(len(full_ds)))
    random.shuffle(indices)
    train_ds = Subset(full_ds, indices[:train_size])
    val_subset = Subset(val_ds, indices[train_size:])

    train_loader = DataLoader(train_ds, batch_size=cfg["batch"], shuffle=True,
                              num_workers=4, pin_memory=True, drop_last=True)
    val_loader = DataLoader(val_subset, batch_size=cfg["batch"], shuffle=False,
                            num_workers=4, pin_memory=True)

    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg["lr"], weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.OneCycleLR(
        optimizer, max_lr=cfg["lr"],
        steps_per_epoch=len(train_loader),
        epochs=cfg["epochs"],
        pct_start=0.3,
    )
    scaler = torch.cuda.amp.GradScaler()

    os.makedirs(os.path.dirname(cfg["checkpoint_out"]), exist_ok=True)
    best_iou = 0.0

    for epoch in range(1, cfg["epochs"] + 1):
        train_loss = train_one_epoch(model, train_loader, optimizer, scaler, device)
        scheduler.step()
        val_loss, val_iou, val_dice = validate(model, val_loader, device)

        print(f"[{stage}] epoch {epoch:3d}/{cfg['epochs']}  "
              f"train_loss={train_loss:.4f}  val_loss={val_loss:.4f}  "
              f"iou={val_iou:.4f}  dice={val_dice:.4f}")

        if val_iou > best_iou:
            best_iou = val_iou
            torch.save(model.state_dict(), cfg["checkpoint_out"])

    print(f"[{stage}] best val iou={best_iou:.4f}  saved to {cfg['checkpoint_out']}")
    return model


def main():
    config = DEFAULT_CONFIG.copy()

    if len(sys.argv) > 1:
        cfg_path = sys.argv[1]
        with open(cfg_path) as f:
            user_cfg = yaml.safe_load(f)
        for stage in ("stage1", "stage2"):
            if stage in user_cfg:
                config[stage].update(user_cfg[stage])

    run_stage(config, "stage1")
    run_stage(config, "stage2")


if __name__ == "__main__":
    main()
