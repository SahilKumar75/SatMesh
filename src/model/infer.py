import cv2
import numpy as np
import torch
import torch.nn.functional as F

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


def histogram_match(src_bgr: np.ndarray, ref_bgr: np.ndarray) -> np.ndarray:
    """Match src radiometry to ref (e.g. Cartosat-3 → Sentinel-2 stats).

    Call before predict_mask when sensor radiometry differs from training data.
    Both arrays must be uint8 BGR from cv2.imread.
    """
    from skimage.exposure import match_histograms
    src_rgb = cv2.cvtColor(src_bgr, cv2.COLOR_BGR2RGB).astype(np.float32)
    ref_rgb = cv2.cvtColor(ref_bgr, cv2.COLOR_BGR2RGB).astype(np.float32)
    matched = match_histograms(src_rgb, ref_rgb, channel_axis=-1)
    return cv2.cvtColor(np.clip(matched, 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR)


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


_MEAN4 = np.array([0.485, 0.456, 0.406, 0.4], dtype=np.float32)
_STD4  = np.array([0.229, 0.224, 0.225, 0.2], dtype=np.float32)
_MEAN3 = np.array([0.485, 0.456, 0.406], dtype=np.float32)
_STD3  = np.array([0.229, 0.224, 0.225], dtype=np.float32)


def predict_mask(model, image_path, device, nir_path=None, img_size=512,
                 threshold=0.5, in_channels=4, tta=False, scales=None,
                 ref_bgr=None):
    raw = cv2.imread(image_path)
    if raw is None:
        raise FileNotFoundError(image_path)
    if ref_bgr is not None:
        raw = histogram_match(raw, ref_bgr)
    h, w = raw.shape[:2]

    if in_channels == 3:
        rgb = cv2.cvtColor(raw, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        img = cv2.resize(rgb, (img_size, img_size))
        img = (img - _MEAN3) / _STD3
    else:
        if nir_path is not None:
            import rasterio
            with rasterio.open(nir_path) as src:
                nir = src.read(1).astype(np.float32)
            img = stack_nir(raw, nir)
        else:
            img = approximate_nir(raw)
        img = cv2.resize(img, (img_size, img_size))
        img = (img - _MEAN4) / _STD4

    tensor = torch.from_numpy(img.transpose(2, 0, 1)).unsqueeze(0).float().to(device)

    def _run(t):
        with torch.no_grad():
            return torch.sigmoid(model(t))[0, 0].float().cpu()

    if scales:
        probs = []
        for s in scales:
            t_s = F.interpolate(tensor, size=(s, s), mode="bilinear", align_corners=False)
            p = _run(t_s)
            p = F.interpolate(p.unsqueeze(0).unsqueeze(0), size=(img_size, img_size),
                              mode="bilinear", align_corners=False)[0, 0]
            probs.append(p)
        prob = torch.stack(probs).mean(0).numpy()
    elif tta:
        p0 = _run(tensor)
        p1 = _run(tensor.flip(-1)).flip(-1)
        p2 = _run(tensor.flip(-2)).flip(-2)
        p3 = _run(tensor.rot90(1, [-2, -1])).rot90(-1, [-2, -1])
        prob = torch.stack([p0, p1, p2, p3]).mean(0).numpy()
    else:
        prob = _run(tensor).numpy()

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
    ap.add_argument("--in_channels", type=int, default=4, choices=[3, 4])
    ap.add_argument("--tta", action="store_true",
                    help="4-aug TTA: original+hflip+vflip+rot90, average sigmoids")
    ap.add_argument("--scales", type=int, nargs="+", default=None,
                    help="multi-scale sizes e.g. --scales 512 768 (use instead of --tta)")
    ap.add_argument("--ref_img", default=None,
                    help="reference image for histogram matching (use a Sentinel-2 tile "
                         "when running inference on Cartosat-3 tiles)")
    args = ap.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = load_model(args.checkpoint, device, args.model, in_channels=args.in_channels)

    sat_files = sorted(glob.glob(f"{args.sat_dir}/*_sat.jpg"))
    if not sat_files:
        sat_files = sorted(glob.glob(f"{args.sat_dir}/*_sat.png"))

    ref_bgr = cv2.imread(args.ref_img) if args.ref_img else None
    if args.ref_img and ref_bgr is None:
        print(f"WARN: could not read --ref_img {args.ref_img}; skipping histogram match")

    for f in sat_files:
        stem = os.path.basename(f).replace("_sat.jpg", "").replace("_sat.png", "")
        nir_path = f.replace("_sat.jpg", "_nir.tif").replace("_sat.png", "_nir.tif")
        nir_path = nir_path if (args.in_channels == 4 and os.path.exists(nir_path)) else None
        mask = predict_mask(model, f, device, nir_path=nir_path,
                            img_size=args.img_size, in_channels=args.in_channels,
                            tta=args.tta, scales=args.scales, ref_bgr=ref_bgr)
        cv2.imwrite(f"{args.out_dir}/{stem}_pred.png", mask)

    print(f"Saved {len(sat_files)} predictions → {args.out_dir}")
