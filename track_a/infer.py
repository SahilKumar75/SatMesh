"""
track_a/infer.py — standalone inference for SatMesh road segmentation.

Usage:
    python track_a/infer.py --checkpoint best_model.pth --input img.jpg
    python track_a/infer.py --checkpoint best_model.pth --input tiles/ --output_dir outputs/
"""

import argparse, os
import cv2
import numpy as np
import torch
import torch.nn as nn
import albumentations as A
from albumentations.pytorch import ToTensorV2
import segmentation_models_pytorch as smp


def _device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


def load_model(checkpoint_path: str, device: str, in_channels: int = 3) -> nn.Module:
    model = smp.Unet(
        encoder_name="resnet34",
        encoder_weights=None,
        in_channels=in_channels,
        classes=1,
    )
    model.load_state_dict(
        torch.load(checkpoint_path, map_location=device, weights_only=True)
    )
    return model.eval().to(device)


def _val_tf(img_size: int) -> A.Compose:
    return A.Compose([A.Resize(img_size, img_size), A.Normalize(), ToTensorV2()])


def predict_mask(
    model: nn.Module,
    image_path: str,
    device: str,
    img_size: int = 512,
    threshold: float = 0.5,
) -> np.ndarray:
    """Return a uint8 binary mask (0 / 255) at the original image resolution."""
    raw = cv2.imread(image_path)
    if raw is None:
        raise FileNotFoundError(image_path)
    h, w = raw.shape[:2]

    if raw.ndim == 2 or raw.shape[2] == 1:
        img = cv2.cvtColor(raw, cv2.COLOR_GRAY2RGB)
    else:
        img = cv2.cvtColor(raw, cv2.COLOR_BGR2RGB)

    tf = _val_tf(img_size)
    tensor = tf(image=img)["image"].unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(tensor)
        prob   = torch.sigmoid(logits)[0, 0].cpu().numpy()

    binary = (prob > threshold).astype(np.uint8) * 255
    if (h, w) != (img_size, img_size):
        binary = cv2.resize(binary, (w, h), interpolation=cv2.INTER_NEAREST)
    return binary


def postprocess_mask(mask: np.ndarray) -> np.ndarray:
    """Morphological cleanup: close sub-pixel gaps, remove isolated noise."""
    k_close = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    k_open  = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k_close)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  k_open)
    return mask


def _image_paths(input_path: str) -> list[str]:
    exts = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}
    if os.path.isfile(input_path):
        return [input_path]
    return [
        os.path.join(input_path, f)
        for f in sorted(os.listdir(input_path))
        if os.path.splitext(f)[1].lower() in exts
    ]


def main():
    parser = argparse.ArgumentParser(description="SatMesh road mask inference")
    parser.add_argument("--checkpoint",  required=True, help="Path to best_model.pth")
    parser.add_argument("--input",       required=True, help="Image file or directory")
    parser.add_argument("--output_dir",  default="outputs", help="Where to write masks")
    parser.add_argument("--img_size",    type=int,   default=512)
    parser.add_argument("--threshold",   type=float, default=0.5)
    parser.add_argument("--no_postproc", action="store_true",
                        help="Skip morphological post-processing")
    parser.add_argument("--in_channels", type=int, default=3,
                        help="1 for panchromatic (Cartosat-3), 3 for RGB")
    args = parser.parse_args()

    device = _device()
    print(f"Device: {device}")
    os.makedirs(args.output_dir, exist_ok=True)

    model  = load_model(args.checkpoint, device, args.in_channels)
    paths  = _image_paths(args.input)
    print(f"Running inference on {len(paths)} image(s)...")

    for path in paths:
        stem = os.path.splitext(os.path.basename(path))[0]
        mask = predict_mask(model, path, device, args.img_size, args.threshold)
        if not args.no_postproc:
            mask = postprocess_mask(mask)
        out = os.path.join(args.output_dir, f"{stem}_road_mask.png")
        cv2.imwrite(out, mask)
        print(f"  {path} → {out}")

    print("Done.")


if __name__ == "__main__":
    main()
