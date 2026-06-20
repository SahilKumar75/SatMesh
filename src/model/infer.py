import cv2
import numpy as np
import torch

from .dlinknet import build_dlinknet


def stack_nir(rgb_bgr, nir_band8):
    rgb = cv2.cvtColor(rgb_bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    nir = nir_band8.astype(np.float32)
    if nir.max() > 1.0:
        nir = nir / 10000.0
    return np.concatenate([rgb, nir[..., None]], axis=-1)


def approximate_nir(rgb_bgr):
    rgb = rgb_bgr.astype(np.float32) / 255.0
    r = rgb[..., 2]
    g = rgb[..., 1]
    b = rgb[..., 0]
    excess_green = 2 * g - r - b
    nir_approx = np.clip(excess_green * 0.5 + 0.3, 0.0, 1.0)
    return np.concatenate([cv2.cvtColor(rgb_bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0,
                           nir_approx[..., None]], axis=-1)


def load_dlinknet(checkpoint_path, device, in_channels=4):
    model = build_dlinknet(pretrained=False, in_channels=in_channels).to(device)
    state = torch.load(checkpoint_path, map_location=device, weights_only=True)
    model.load_state_dict(state)
    model.eval()
    return model


def postprocess_mask(mask):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    return cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel2)


_MEAN = np.array([0.485, 0.456, 0.406, 0.4], dtype=np.float32)
_STD  = np.array([0.229, 0.224, 0.225, 0.2], dtype=np.float32)


def predict_mask(model, image_path, device, nir_path=None, img_size=512, threshold=0.5):
    raw = cv2.imread(image_path)
    if raw is None:
        raise FileNotFoundError(image_path)
    h, w = raw.shape[:2]

    if nir_path is not None:
        import rasterio
        with rasterio.open(nir_path) as src:
            nir = src.read(1).astype(np.float32)
        img4 = stack_nir(raw, nir)
    else:
        img4 = approximate_nir(raw)

    img4 = cv2.resize(img4, (img_size, img_size))
    img4 = (img4 - _MEAN) / _STD
    tensor = torch.from_numpy(img4.transpose(2, 0, 1)).unsqueeze(0).float().to(device)

    with torch.no_grad():
        prob = torch.sigmoid(model(tensor))[0, 0].float().cpu().numpy()

    mask = (prob > threshold).astype(np.uint8) * 255
    if (h, w) != (img_size, img_size):
        mask = cv2.resize(mask, (w, h), interpolation=cv2.INTER_NEAREST)
    return postprocess_mask(mask)


def load_model(checkpoint_path, device, model_type="segformer", in_channels=4):
    if model_type == "segformer":
        from .segformer import build_segformer
        model = build_segformer(pretrained=False, in_channels=in_channels).to(device)
    else:
        model = build_dlinknet(pretrained=False, in_channels=in_channels).to(device)
    state = torch.load(checkpoint_path, map_location=device, weights_only=True)
    model.load_state_dict(state)
    model.eval()
    return model


if __name__ == "__main__":
    import argparse
    import glob
    import os

    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--model", default="segformer", choices=["segformer", "dlinknet"])
    ap.add_argument("--sat_dir", required=True)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--img_size", type=int, default=512)
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(args.checkpoint, device, args.model)

    sat_files = sorted(glob.glob(f"{args.sat_dir}/*_sat.jpg"))
    if not sat_files:
        sat_files = sorted(glob.glob(f"{args.sat_dir}/*_sat.png"))

    for f in sat_files:
        stem = os.path.basename(f).replace("_sat.jpg", "").replace("_sat.png", "")
        nir_path = f.replace("_sat.jpg", "_nir.tif").replace("_sat.png", "_nir.tif")
        nir_path = nir_path if os.path.exists(nir_path) else None
        mask = predict_mask(model, f, device, nir_path=nir_path, img_size=args.img_size)
        cv2.imwrite(f"{args.out_dir}/{stem}_pred.png", mask)

    print(f"Saved {len(sat_files)} predictions → {args.out_dir}")
