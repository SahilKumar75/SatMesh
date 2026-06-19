# SatMesh — Kaggle training

Produces `dlinknet_india.pth` (the Track A checkpoint the live pipeline needs).

## Run via the Kaggle UI (recommended)

1. New Notebook → File → **Upload** `satmesh_train.ipynb`.
2. **Settings → Accelerator → GPU T4 x2** (single T4 also works).
3. **Settings → Internet → On**.
4. **+ Add Input → Datasets →** search `deepglobe-road-extraction-dataset` (balraj98) → Add.
5. (Optional, for Stage 2) Add a Sentinel-2 India dataset whose tiles are named
   `*_sat.jpg` + `*_mask.png` (+ optional `*_nir.tif`). Without it, Stage 1 still
   yields a usable 3-channel model.
6. **Run All**. Stage 1 ≈ 25 min, Stage 2 ≈ 20 min on T4.
7. **Output** tab → download `checkpoints/dlinknet_india.pth`.
8. Locally: `cp dlinknet_india.pth checkpoints/` so `POST /run?mock=false` runs live.

## Run via CLI (alternative)

```bash
pip install kaggle
# edit kernel-metadata.json "id" to <your-kaggle-username>/satmesh-dlinknet-train
kaggle kernels push -p kaggle/
```

## Targets (from PLAN.md)
- Stage 1: IoU ≥ 0.73 on DeepGlobe val.
- Stage 2: IoU ≥ 0.68 on Bengaluru Sentinel-2 val.

## Notes / known-unverified
- `src/model/train.py` + `infer.py` are verified end-to-end on CPU (synthetic data):
  model builds (3-ch & 4-ch), two-stage transfer works, `predict_mask` produces a
  binary mask. Real accuracy depends on the run.
- The Stage-2 **data generation** branch (`sentinel_dl.py` + `mask_raster.py`) is the
  one path not yet executed — prefer attaching a prepared Sentinel-2 India dataset.
  STAC download + OSM rasterization on Kaggle is slow and untested.
