import random
import cv2
import numpy as np
import albumentations as A
from albumentations.pytorch import ToTensorV2


class CanopyOcclusionOnRoad:
    def __init__(self, num_blobs=(4, 20), blob_r=(10, 50), p=0.5):
        self.num_blobs = num_blobs
        self.blob_r = blob_r
        self.p = p

    def __call__(self, image: np.ndarray, mask_u8: np.ndarray) -> np.ndarray:
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


def make_train_transform(img_size: int = 512, use_nir: bool = False) -> A.Compose:
    additional_targets = {"nir": "image"} if use_nir else {}
    return A.Compose([
        A.Resize(img_size, img_size),
        A.HorizontalFlip(p=0.5),
        A.VerticalFlip(p=0.3),
        A.RandomRotate90(p=0.5),
        A.Affine(scale=(0.9, 1.1), translate_percent=0.1, rotate=(-15, 15), p=0.4),
        A.RandomShadow(p=0.4),
        A.CoarseDropout(num_holes_range=(2, 12), hole_height_range=(8, 40),
                        hole_width_range=(8, 40), fill=0, p=0.5),
        A.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1, p=0.4),
        A.RandomGamma(gamma_limit=(80, 120), p=0.3),
        A.GaussNoise(std_range=(0.01, 0.05), p=0.3),
        A.Normalize(),
        ToTensorV2(),
    ], additional_targets=additional_targets)


def make_val_transform(img_size: int = 512, use_nir: bool = False) -> A.Compose:
    additional_targets = {"nir": "image"} if use_nir else {}
    return A.Compose([
        A.Resize(img_size, img_size),
        A.Normalize(),
        ToTensorV2(),
    ], additional_targets=additional_targets)
