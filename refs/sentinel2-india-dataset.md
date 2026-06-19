# Sentinel-2 Indian Roads Dataset

**Citation.** Sentinel-2 road-extraction dataset covering Indian regions with OSM-derived masks (PMC, 2025). Multi-region, 10 m multispectral, OSM centerline ground truth.

**Core claim.** Models trained on DeepGlobe (US/EU, sub-meter aerial RGB) transfer poorly to Indian roads (narrower, denser, heavy tree canopy, 10 m Sentinel-2 resolution); domain-matched Sentinel-2 + the **NIR band** are needed for usable accuracy on Indian cities.

## Key facts / formulas

- **Bands used (10 m):** B02 (blue), B03 (green), B04 (red), **B08 (NIR)**. NIR separates vegetation from pavement because chlorophyll reflects strongly in NIR while asphalt does not.

- **NDVI** (canopy detection, used to guide gap-healing under trees):
  ```
  NDVI = (NIR − Red) / (NIR + Red) = (B08 − B04) / (B08 + B04)
  ```
  High NDVI over a road-gap region → likely tree-occluded road → allow a longer healing bridge.

- **Resolution reality:** at 10 m/px a 2-lane road is ~1 px wide — extraction is genuinely hard and topology-preserving loss matters even more.

## What it changes in SatMesh

- `src/data/sentinel_dl.py` pulls B02/B03/B04/B08 from the Planetary Computer STAC API and extracts real lat/lon from the GeoTIFF CRS.
- Two-stage training (`src/model/train.py`): DeepGlobe pretrain → **Sentinel-2 India fine-tune**, where the NIR channel (dead-weight on RGB-only DeepGlobe) becomes live.
- `heal.py` accepts an `ndvi_mask` to double `max_gap_m` under canopy.

## Judge talking point

Training on DeepGlobe and demoing on India is the silent failure mode most teams will hit. We fine-tune on domain-matched Sentinel-2 *and* exploit Band 8 (NIR) — the single biggest free signal for separating tree canopy from road. RGB-only teams literally cannot see through the canopy the way our 4-channel model can.

See also [[dlinknet-cvpr2018]] (4-channel backbone) and [[flood-resilience-2023]] (NDVI-guided healing application).
