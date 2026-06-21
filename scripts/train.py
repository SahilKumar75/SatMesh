#!/usr/bin/env python3
"""Portable two-stage training launcher (Lightning AI / any CUDA box).

Stage 1 pretrains D-LinkNet on DeepGlobe (auto-downloaded via kagglehub).
Stage 2 fine-tunes on a Sentinel-2 India tile dir (RGB+NIR), if provided.

Two target checkpoints (multi-resolution strategy)
---------------------------------------------------
    # Checkpoint B — high-res 0.5m (DeepGlobe/SpaceNet), strict-IoU target >=0.70.
    # H200: mit_b4 @768px, bf16 + grad-checkpoint. No --india-dir => stage2 skipped,
    # stage1 weights saved as the high-res checkpoint.
    python scripts/train.py --encoder mit_b4 --img-size 768 --batch 14 \
        --grad-checkpoint --epochs 50

    # Checkpoint A — Sentinel-2 10m India (dashboard), relaxed-IoU target >=0.55.
    # Resume from a high-res stage1.pth, fine-tune on India tiles with CLAHE.
    python scripts/train.py --skip-stage1 \
        --india-dir data/sentinel2_india/train \
        --encoder mit_b4 --img-size 512 --batch 28 --clahe

Other examples
--------------
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
    ap.add_argument("--epochs", type=int, default=40)
    ap.add_argument("--epochs2", type=int, default=20)
    ap.add_argument("--batch", type=int, default=4, help="stage-1 batch size")
    ap.add_argument("--batch2", type=int, default=4)
    ap.add_argument("--img-size", type=int, default=512)
    ap.add_argument("--subset", type=int, default=None, help="tile subset cap (None = full dataset)")
    ap.add_argument("--out", default="checkpoints")
    ap.add_argument("--skip-stage1", action="store_true")
    ap.add_argument("--model", default="segformer", choices=["segformer", "dlinknet"])
    ap.add_argument("--encoder", default="mit_b0",
                    choices=["mit_b0", "mit_b2", "mit_b3", "mit_b4"],
                    help="MiT encoder variant (mit_b4 recommended for 70%%+ IoU)")
    ap.add_argument("--grad-checkpoint", action="store_true",
                    help="enable gradient checkpointing (required for B3/B4 on 16GB GPU)")
    ap.add_argument("--clahe", action="store_true",
                    help="CLAHE+gamma enhance inputs (recommended for 10m Sentinel-2 stage-2)")
    ap.add_argument("--no-nir", action="store_true",
                    help="stage-2 trains 3-ch RGB (high-res Esri tiles, resumes 3-ch v2); "
                         "default uses 4-ch synth-NIR for 10m Sentinel-2")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    # Only resolve DeepGlobe when stage-1 will run. With --skip-stage1 the
    # auto-download (kagglehub) must not fire — it needs internet, which is off
    # on Kaggle kernels and would crash the india-only fine-tune path.
    if args.skip_stage1:
        dg = args.deepglobe or ""
        print("Stage-1 skipped — not resolving DeepGlobe")
    else:
        dg = find_deepglobe(args.deepglobe)
        print("DeepGlobe:", dg, "|", len(glob.glob(f"{dg}/*_sat.jpg")), "tiles")

    cfg = {
        "stage1": {"data_dir": dg, "epochs": args.epochs, "batch": args.batch,
                   "lr": 1e-3, "img_size": args.img_size, "subset": args.subset,
                   "use_nir": False, "model": args.model,
                   "encoder_name": args.encoder,
                   "grad_checkpoint": args.grad_checkpoint,
                   "use_clahe": False,
                   "checkpoint_out": f"{args.out}/stage1.pth"},
        "stage2": {"data_dir": args.india_dir or "data/sentinel2_india/train",
                   "epochs": args.epochs2, "batch": args.batch2, "lr": 5e-5,
                   "img_size": args.img_size, "subset": args.subset,
                   "use_nir": not args.no_nir,
                   "model": args.model,
                   "encoder_name": args.encoder,
                   "grad_checkpoint": args.grad_checkpoint,
                   "use_clahe": args.clahe,
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
