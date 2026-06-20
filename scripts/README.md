# Training on Lightning AI (L4 or better)

L4 (24 GB) ≈ 2× T4 and fits a larger batch — much faster than Kaggle.

## Steps

1. **Lightning AI → new Studio → GPU → L4** (or A10G/A100).
2. Open the Studio **Terminal**:

```bash
git clone https://github.com/SahilKumar75/SatMesh.git
cd SatMesh
pip install -q "segmentation-models-pytorch>=0.4" "albumentations>=2.0" pyyaml kagglehub
# torch is preinstalled on Lightning GPU Studios — don't reinstall it
```

3. **Kaggle auth** (for the DeepGlobe auto-download). Get a token at
   kaggle.com → Account → *Create New API Token* (downloads `kaggle.json`):

```bash
mkdir -p ~/.kaggle
# paste your kaggle.json into ~/.kaggle/kaggle.json, then:
chmod 600 ~/.kaggle/kaggle.json
export KAGGLE_USERNAME=... KAGGLE_KEY=...   # or rely on kaggle.json
```

4. **Train** (Stage 1, DeepGlobe — ~12–15 min on L4):

```bash
python scripts/train.py --batch 16 --epochs 30
```

   With prepared Indian tiles (adds Stage 2, 4-ch RGB+NIR):

```bash
python scripts/train.py --batch 16 --india-dir data/sentinel2_india/train
```

5. Output: `checkpoints/dlinknet_india.pth`. Download it from the Studio file
   browser, drop into `checkpoints/` locally → `POST /run?mock=false` runs live.

## Flags

| flag | default | note |
|---|---|---|
| `--batch` | 16 | stage-1 batch; L4 handles 16 @512, A100 up to 32 |
| `--epochs` | 30 | stage-1 |
| `--india-dir` | — | enables stage-2 fine-tune when it has `*_sat.jpg` |
| `--deepglobe` | auto | skip download, point at an existing `train/` dir |
| `--subset` | 5000 | stage-1 tile cap; raise for full DeepGlobe |
| `--skip-stage1` | off | resume straight to stage-2 |

## Speed knobs if still slow
- Drop `--img-size` to 384 (≈1.7× faster, small accuracy cost).
- Lower `--subset` to 2500 for a quick first checkpoint.
- A100 Studio + `--batch 32` if you have the credits.

## Known-unverified
Stage-2 **data generation** (`sentinel_dl.py` + `mask_raster.py`) is the one path
not yet run. Prefer attaching prepared Sentinel-2 India tiles via `--india-dir`.
The training + inference path itself is verified end-to-end.
