#!/usr/bin/env python3
"""Portable two-stage training launcher (Lightning AI / any CUDA box).

Stage 1 pretrains D-LinkNet on DeepGlobe (auto-downloaded via kagglehub).
Stage 2 fine-tunes on a Sentinel-2 India tile dir (RGB+NIR), if provided.

Examples
--------
    # Stage 1 only (DeepGlobe), L4-sized batch:
    python scripts/train.py --batch 16 --epochs 30

    # Both stages (attach prepared India tiles):
    python scripts/train.py --india-dir data/sentinel2_india/train

    # Point at an already-downloaded DeepGlobe train dir:
    python scripts/train.py --deepglobe /path/to/train
"""
import argparse
import glob
import os
import sys
from pathlib import Path

# repo root on path so `src` imports work no matter where this is run from
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.model import train as T  # noqa: E402


def find_deepglobe(explicit):
    if explicit:
        assert glob.glob(f"{explicit}/*_sat.jpg"), f"no *_sat.jpg in {explicit}"
        return explicit
    print("Downloading DeepGlobe via kagglehub (needs Kaggle auth)...")
    import kagglehub
    root = kagglehub.dataset_download("balraj98/deepglobe-road-extraction-dataset")
    cands = glob.glob(f"{root}/**/train", recursive=True)
    train = next((c for c in cands if glob.glob(f"{c}/*_sat.jpg")), None)
    assert train, f"no train/*_sat.jpg under {root}"
    return train


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deepglobe", default=None, help="DeepGlobe train dir (else auto-download)")
    ap.add_argument("--india-dir", default=None, help="Sentinel-2 India tile dir for stage 2")
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--epochs2", type=int, default=20)
    ap.add_argument("--batch", type=int, default=16, help="stage-1 batch (L4 handles 16 @512)")
    ap.add_argument("--batch2", type=int, default=8)
    ap.add_argument("--img-size", type=int, default=512)
    ap.add_argument("--subset", type=int, default=5000)
    ap.add_argument("--out", default="checkpoints")
    ap.add_argument("--skip-stage1", action="store_true")
    ap.add_argument("--model", default="segformer", choices=["segformer", "dlinknet"])
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    dg = find_deepglobe(args.deepglobe)
    print("DeepGlobe:", dg, "|", len(glob.glob(f"{dg}/*_sat.jpg")), "tiles")

    cfg = {
        "stage1": {"data_dir": dg, "epochs": args.epochs, "batch": args.batch,
                   "lr": 1e-3, "img_size": args.img_size, "subset": args.subset,
                   "use_nir": False, "model": args.model,
                   "checkpoint_out": f"{args.out}/stage1.pth"},
        "stage2": {"data_dir": args.india_dir or "data/sentinel2_india/train",
                   "epochs": args.epochs2, "batch": args.batch2, "lr": 2e-4,
                   "img_size": args.img_size, "subset": None, "use_nir": True,
                   "model": args.model,
                   "checkpoint_in": f"{args.out}/stage1.pth",
                   "checkpoint_out": f"{args.out}/{args.model}_india.pth"},
    }

    if not args.skip_stage1:
        T.run_stage(cfg, "stage1")

    if args.india_dir and glob.glob(f"{args.india_dir}/*_sat.jpg"):
        T.run_stage(cfg, "stage2")
    else:
        import shutil
        shutil.copy(cfg["stage1"]["checkpoint_out"], cfg["stage2"]["checkpoint_out"])
        print(f"No India data — stage1 (3-ch) saved as {args.model}_india.pth. "
              "Re-run with --india-dir for the 4-ch domain-adapted model.")

    print("Done. Checkpoint:", cfg["stage2"]["checkpoint_out"])


if __name__ == "__main__":
    main()
