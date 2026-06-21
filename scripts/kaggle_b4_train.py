"""Kaggle notebook runner for MiT-B4 training.

Paste this entire file as a single Kaggle cell, or run:
    !python /kaggle/working/SatMesh/scripts/kaggle_b4_train.py

Handles: clone-or-pull, dep install, B4 training, checkpoint save.
"""
import os
import shutil
import subprocess
import sys

REPO   = "https://github.com/SahilKumar75/SatMesh.git"
ROOT   = "/kaggle/working/SatMesh"
DATA   = "/kaggle/input/datasets/balraj98/deepglobe-road-extraction-dataset/train"
CKPT   = "checkpoints/segformer_b4"
OUT    = "/kaggle/working/segformer_b4_final.pth"

# ── 1. Clone or pull ──────────────────────────────────────────────────────────
if not os.path.exists(os.path.join(ROOT, ".git")):
    print("Cloning repo...")
    subprocess.run(["git", "clone", REPO, ROOT], check=True)
else:
    print("Repo exists, pulling latest...")
    subprocess.run(["git", "-C", ROOT, "pull", "origin", "main"], check=True)

os.chdir(ROOT)
print("CWD:", os.getcwd())

# ── 2. Install deps ───────────────────────────────────────────────────────────
print("Installing deps...")
subprocess.run([
    sys.executable, "-m", "pip", "install",
    "segmentation-models-pytorch", "rasterio", "albumentations", "-q",
], check=True)

# ── 3. Train B4 ───────────────────────────────────────────────────────────────
print("Starting B4 training (~6-7h on T4 x2)...")
subprocess.run([
    sys.executable, "scripts/train.py",
    "--deepglobe",      DATA,
    "--encoder",        "mit_b4",
    "--model",          "segformer",
    "--epochs",         "40",
    "--batch",          "4",
    "--grad-checkpoint",
    "--out",            CKPT,
], check=True)

# ── 4. Save checkpoint to /kaggle/working ─────────────────────────────────────
src = os.path.join(ROOT, CKPT, "segformer_india.pth")
shutil.copy(src, OUT)
print(f"Saved → {OUT}")
