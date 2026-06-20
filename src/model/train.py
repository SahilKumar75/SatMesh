import os
import random
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import albumentations as A
from albumentations.pytorch import ToTensorV2
import yaml

from .dlinknet import build_dlinknet
from .segformer import build_segformer, build_segformer_4ch
from .loss import combined_loss


DEFAULT_CONFIG = {
    "stage1": {
        "data_dir": "data/deepglobe/train",
        "epochs": 30,
        "batch": 8,
        "lr": 1e-3,
        "img_size": 512,
        "subset": None,
        "use_nir": False,
        "encoder_name": "mit_b0",
        "grad_checkpoint": False,
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
        "encoder_name": "mit_b0",
        "grad_checkpoint": False,
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
            # Deterministic shuffle so a separate val instance picks the SAME
            # ordering — otherwise an independent random.shuffle here leaks train
            # samples into the val split.
            random.Random(1234).shuffle(self.samples)
            self.samples = self.samples[:subset]

        # NIR path already scales the 4-ch image to [0,1] in __getitem__, so
        # Normalize must treat it as [0,1] (max_pixel_value=1.0). The 3-ch path
        # passes a uint8 [0,255] image, so the default 255 scaling applies.
        norm_max = 1.0 if use_nir else 255.0
        mean = [0.485, 0.456, 0.406, 0.4] if use_nir else [0.485, 0.456, 0.406]
        std = [0.229, 0.224, 0.225, 0.2] if use_nir else [0.229, 0.224, 0.225]

        # ColorJitter/GaussianBlur assume 3-channel RGB; skip them on the 4-ch
        # (RGB+NIR) tensor where they would error or corrupt the NIR band.
        photometric = [] if use_nir else [
            A.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05, p=0.5),
            A.GaussianBlur(blur_limit=(3, 7), p=0.2),
        ]
        self.train_tf = A.Compose([
            A.RandomResizedCrop(size=(img_size, img_size), scale=(0.5, 1.0)),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.RandomRotate90(p=0.5),
            *photometric,
            A.Normalize(mean=mean, std=std, max_pixel_value=norm_max),
            ToTensorV2(),
        ])
        self.val_tf = A.Compose([
            A.Resize(img_size, img_size),
            A.Normalize(mean=mean, std=std, max_pixel_value=norm_max),
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


def _relaxed_iou(pred_bin, target, r=3):
    k, pad = 2 * r + 1, r
    t_dil = F.max_pool2d(target.float(), k, stride=1, padding=pad) > 0
    p_dil = F.max_pool2d(pred_bin.float(), k, stride=1, padding=pad) > 0
    inter = (p_dil & target).float().sum()
    union = (p_dil | t_dil).float().sum()
    return (inter + 1e-6) / (union + 1e-6)


def train_one_epoch(model, loader, optimizer, scaler, device, epoch=0):
    model.train()
    use_skelrecall = (epoch >= 10)
    total_loss = 0.0
    for imgs, masks in loader:
        imgs, masks = imgs.to(device), masks.to(device)
        optimizer.zero_grad()
        with torch.amp.autocast(device_type=device.type, enabled=(device.type == "cuda")):
            logits = model(imgs)
            loss = combined_loss(logits, masks, use_skelrecall=use_skelrecall)
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        total_loss += loss.item()
    return total_loss / len(loader)


@torch.no_grad()
def validate(model, loader, device):
    model.eval()
    total_loss = total_iou = total_dice = total_relaxed = 0.0
    for imgs, masks in loader:
        imgs, masks = imgs.to(device), masks.to(device)
        with torch.amp.autocast(device_type=device.type, enabled=(device.type == "cuda")):
            logits = model(imgs)
            loss = combined_loss(logits, masks, use_skelrecall=False)
        pred_bin = (torch.sigmoid(logits) > 0.5)
        target_bin = (masks > 0.5)
        total_loss += loss.item()
        total_iou += _iou(pred_bin, target_bin).item()
        total_dice += _dice_coef(pred_bin, target_bin).item()
        total_relaxed += _relaxed_iou(pred_bin, target_bin).item()
    n = len(loader)
    return total_loss / n, total_iou / n, total_dice / n, total_relaxed / n


def run_stage(config, stage):
    cfg = config[stage]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    in_channels = 4 if cfg["use_nir"] else 3
    model_type = cfg.get("model", "dlinknet")
    encoder_name = cfg.get("encoder_name", "mit_b0")

    if stage == "stage2" and "checkpoint_in" in cfg and os.path.exists(cfg["checkpoint_in"]):
        if model_type == "segformer":
            model = build_segformer_4ch(cfg["checkpoint_in"], device=str(device),
                                        encoder_name=encoder_name)
        else:
            model = build_dlinknet(pretrained=False, in_channels=in_channels)
            state = torch.load(cfg["checkpoint_in"], map_location=device, weights_only=True)
            ckpt_conv1 = state.pop("base.encoder.conv1.weight", None)
            model.load_state_dict(state, strict=False)
            if ckpt_conv1 is not None:
                with torch.no_grad():
                    tgt = model.base.encoder.conv1.weight
                    shared = min(tgt.shape[1], ckpt_conv1.shape[1])
                    tgt[:, :shared] = ckpt_conv1[:, :shared]
                    if tgt.shape[1] > ckpt_conv1.shape[1]:
                        tgt[:, ckpt_conv1.shape[1]:] = ckpt_conv1.mean(1, keepdim=True)
    else:
        if model_type == "segformer":
            model = build_segformer(pretrained=True, in_channels=in_channels,
                                    encoder_name=encoder_name)
        else:
            model = build_dlinknet(pretrained=True, in_channels=in_channels)

    model = model.to(device)

    if cfg.get("grad_checkpoint", False):
        try:
            model.encoder.set_grad_checkpointing(True)
            print(f"[{stage}] gradient checkpointing enabled")
        except AttributeError:
            pass

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

    if stage == "stage2":
        # Stage-2: encoder already pretrained — keep it slow to avoid catastrophic
        # forgetting while the NIR patch_embed and decoder adapt.
        encoder_params = [p for n, p in model.named_parameters()
                          if "encoder" in n and "patch_embed1" not in n]
        other_params = [p for n, p in model.named_parameters()
                        if not ("encoder" in n and "patch_embed1" not in n)]
        optimizer = torch.optim.AdamW([
            {"params": encoder_params, "lr": cfg["lr"] * 0.1},
            {"params": other_params,   "lr": cfg["lr"]},
        ], weight_decay=1e-4)
    else:
        optimizer = torch.optim.AdamW(model.parameters(), lr=cfg["lr"], weight_decay=1e-4)
    # CosineAnnealingLR: step per epoch, decays LR smoothly to eta_min
    # Replaces OneCycleLR which was incorrectly stepped once/epoch instead of once/batch
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=cfg["epochs"], eta_min=cfg["lr"] * 0.01,
    )
    scaler = torch.amp.GradScaler(device.type, enabled=(device.type == "cuda"))

    os.makedirs(os.path.dirname(cfg["checkpoint_out"]), exist_ok=True)
    best_relaxed = 0.0

    for epoch in range(1, cfg["epochs"] + 1):
        train_loss = train_one_epoch(model, train_loader, optimizer, scaler, device, epoch=epoch)
        scheduler.step()
        val_loss, val_iou, val_dice, val_relaxed = validate(model, val_loader, device)

        skel_flag = "skel+" if epoch >= 10 else "skel-"
        print(f"[{stage}] epoch {epoch:3d}/{cfg['epochs']}  {skel_flag}  "
              f"train_loss={train_loss:.4f}  val_loss={val_loss:.4f}  "
              f"iou={val_iou:.4f}  dice={val_dice:.4f}  relaxed_iou={val_relaxed:.4f}")

        if val_relaxed > best_relaxed:
            best_relaxed = val_relaxed
            torch.save(model.state_dict(), cfg["checkpoint_out"])

    print(f"[{stage}] best relaxed_iou={best_relaxed:.4f}  saved to {cfg['checkpoint_out']}")
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
