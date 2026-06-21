"""Kaggle T4 x2 runner for SatMesh MiT-B4 training (both checkpoints).

Paste this whole file as one Kaggle cell, or run:
    !python /kaggle/working/SatMesh/scripts/kaggle_b4_train.py

Set MODE below, attach the matching Kaggle input datasets (right panel ->
"Add Input"), and set Accelerator -> GPU T4 x2 (sm_75). P100 (sm_60) fails for
stock torch — re-roll the GPU if you get one.

Two checkpoints (see ~/.claude/plans/glimmering-hatching-codd.md):
  MODE="highres"  Checkpoint B — DeepGlobe 0.5 m pretrain, strict-IoU target >=0.70
  MODE="india"    Checkpoint A — Sentinel-2 10 m fine-tune (dashboard), relaxed-IoU >=0.55

Kaggle kernels have NO internet by default, so the India fine-tune does NOT fetch
imagery live — it ingests a pre-uploaded India Sentinel-2 Roads Dataset. Building
new regions from Planetary Computer/OSM must be done off-Kaggle (see
scripts/prepare_india_dataset.py --regions).
"""
import os
import shutil
import subprocess
import sys

# ── CONFIG — edit these ───────────────────────────────────────────────────────
MODE = "india"   # "highres" (Checkpoint B) or "india" (Checkpoint A)

REPO = "https://github.com/SahilKumar75/SatMesh.git"
ROOT = "/kaggle/working/SatMesh"

# highres (Checkpoint B): DeepGlobe Kaggle dataset
DEEPGLOBE = "/kaggle/input/deepglobe-road-extraction-dataset/train"

# india (Checkpoint A): published India S2 Roads Dataset + a stage-1 base ckpt.
# Upload both as Kaggle datasets and fix these paths to match.
INDIA_DS    = "/kaggle/input/india-sentinel2-roads"          # the 5634-tile dataset folder
STAGE1_CKPT = "/kaggle/input/satmesh-stage1/segformer_india_v2.pth"  # resume base (= high-res ckpt)

OUT_DIR = "/kaggle/working"
# ──────────────────────────────────────────────────────────────────────────────


def run(cmd):
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


# 1. GPU sanity — fail fast on P100 / CPU.
import torch  # noqa: E402
assert torch.cuda.is_available(), "No GPU — set Accelerator to GPU T4 x2"
cap = torch.cuda.get_device_capability(0)
assert cap[0] >= 7, f"GPU sm_{cap[0]}{cap[1]} too old (need >=7.0, T4=sm_75). Re-roll GPU."
print(f"GPU OK: {torch.cuda.get_device_name(0)} sm_{cap[0]}{cap[1]} x{torch.cuda.device_count()}")

# 2. Clone or pull.
if not os.path.exists(os.path.join(ROOT, ".git")):
    run(["git", "clone", REPO, ROOT])
else:
    run(["git", "-C", ROOT, "pull", "origin", "main"])
os.chdir(ROOT)
print("CWD:", os.getcwd())

# 3. Deps.
run([sys.executable, "-m", "pip", "install", "-q",
     "segmentation-models-pytorch", "rasterio", "albumentations"])

# 4. Train.
if MODE == "highres":
    print("Checkpoint B — DeepGlobe high-res pretrain (T4 x2, ~few hours)")
    run([sys.executable, "scripts/train.py",
         "--deepglobe", DEEPGLOBE,
         "--encoder", "mit_b4", "--model", "segformer",
         "--img-size", "768", "--batch", "4", "--grad-checkpoint",
         "--epochs", "50",
         "--out", "checkpoints/b4_highres"])
    produced = "checkpoints/b4_highres/segformer_india.pth"
    final = os.path.join(OUT_DIR, "segformer_highres_v3.pth")

elif MODE == "india":
    print("Checkpoint A — Sentinel-2 10 m India fine-tune (with CLAHE)")
    # 4a. Ingest the pre-uploaded India dataset (no network needed).
    run([sys.executable, "scripts/prepare_india_dataset.py",
         "--published-dir", INDIA_DS, "--regions", "none",
         "--out", "data/sentinel2_india/train", "--tile", "512"])
    # 4b. Stage-2 resumes from {out}/stage1.pth — seed it with the high-res base.
    os.makedirs("checkpoints/b4_india", exist_ok=True)
    shutil.copy(STAGE1_CKPT, "checkpoints/b4_india/stage1.pth")
    # 4c. Fine-tune (stage-2 only). T4-sized batch.
    run([sys.executable, "scripts/train.py", "--skip-stage1",
         "--india-dir", "data/sentinel2_india/train",
         "--encoder", "mit_b4", "--model", "segformer",
         "--img-size", "512", "--batch2", "8", "--epochs2", "35", "--clahe",
         "--out", "checkpoints/b4_india"])
    produced = "checkpoints/b4_india/segformer_india.pth"
    final = os.path.join(OUT_DIR, "segformer_india_s2.pth")

else:
    raise SystemExit(f"unknown MODE={MODE!r}")

# 5. Save the checkpoint where Kaggle lets you download it.
shutil.copy(os.path.join(ROOT, produced), final)
print(f"Done. Download from Output panel: {final}")
