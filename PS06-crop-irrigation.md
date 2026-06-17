# PS6 — AI-Driven Automated Crop Type, Moisture Stress Detection and Irrigation Advisory Across Growth Stages Using Moderate Resolution Spectral Signatures (Optical & Microwave)

**Mentors:** Mohammed Ahamed Jeelani, Abhinav Kumar, Debashish Dash
**Explainer:** Video 1, 53:51–1:00:40
**Slides:** Only the title slide exists (mentor presented from audio, no content deck). Detail below is from the transcript.

## Title-slide thumbnail (target dashboard)
A mock dashboard with three map panels — **Crop Type Classification**, **Moisture Stress Detection**, **Irrigation Advisory Map** — over field parcels, plus a "Simulation / Recommendations" strip (recommended irrigation depth in mm, total irrigation volume, climate increase, and a circular **water-savings gauge** reading ~-12%). This is the deliverable's intended look: per-parcel crop type + stress + pixel-level irrigation advice in one view.

## Problem
Across a cropping season (Kharif/monsoon, summer) Indian crops are heterogeneous and cloud-affected. Goal: a satellite-based automated pipeline to (a) classify crop type, (b) detect moisture stress and the **phenological stage** at which it occurs, and (c) translate crop water deficit into **practical irrigation advisory** in near real time. Supports precision agriculture, drought monitoring, yield forecasting; aligns with Digital Agriculture Mission, PM-KISAN, PMFBY.

## Objectives (three)
1. **Crop type identification** for the current season using **multi-temporal spectral signatures (optical + microwave)** from the previous and current seasons. Previous-season ground truth (e.g., 2024/2025) provided for a pilot region to enable automated mapping.
2. **Phenologically-aware modeling** — identify the crop growth stage; then monitor **moisture stress** (crop under stress or not) using optical + microwave data.
3. **Satellite-based system to estimate crop water deficit** and generate an **irrigation advisory map** for a canal command area. Study area = a command area + tail-end **rainfed** regions outside it (represents both irrigated and rainfed crops).

## Expected outcomes
- Methodology + UI for automated high-resolution crop-type maps (open-source + Indian data, e.g., LISS-III).
- Dashboard-ready output: stress maps, crop growth-stage interpretation, pixel-level irrigation advisory.
- Scalable model (pilot → larger regions, multiple crops/seasons).

## Datasets
- Optical: LISS-III, Sentinel-2.
- Microwave (all-weather, key in cloudy Kharif): RISAT (EOS-04), Sentinel-1.
- Meteorology: rainfall, temperature.
- Command-area layers/boundaries, soil map, and **ground-truth crop labels** provided.

## Suggested tools
Google Earth Engine, R, MATLAB, Python; ML + DL models; cloud/deployment resources.

## Evaluation
- Must not only classify but also derive water-deficit and irrigation-advisory layers.
- **Crop classification accuracy target > 80–85%.**
- Moisture-stress classification must be growth-stage-specific and logically consistent with satellite indicators.

## Q&A note (1:29)
- Ground-truth validation via autonomous drone is **not** being sought right now (not part of the expected solution).

## Official description (website) — authoritative additions
- **Optical sources (expanded):** LISS-IV, LISS-III, **AWiFS**, Sentinel-2, Landsat, MODIS. **Microwave:** EOS-04, Sentinel-1, and **upcoming NISAR-SAR**. Access via Bhuvan / Bhoonidhi (ISRO) + open portals.
- **Objective 3 is specifically an 8-day crop water deficit** (ETc) → irrigation advisory maps for canal command areas.
- **Features:** vegetation indices NDVI, EVI, NDWI; SAR VV, VH, VH/VV ratio; GLCM texture; phenology metrics (Start of Season, Peak, Length of Growing Period). **Stress indices: Vegetation Condition Index (VCI), Soil Moisture Index (SMI).**
- **Models:** Random Forest, XGBoost (tabular/multi-temporal); LSTM / Temporal CNN (time series); U-Net (spatial).
- **Validation metrics:** Overall Accuracy, **Kappa coefficient**; crop classification target **>85%**.
- **Policy programs (impact framing):** PMKSY, Digital Agriculture Mission, NMSA, PMFBY.
- Water-deficit method is open: physical crop water balance OR crop-coefficient/empirical (ETc vs actual ET + rainfall) → irrigation status map.

## Our take
Good geospatial fit but another crowded "agri-ML" lane. The phenology-aware stress + command-area irrigation advisory is the part to nail for differentiation.
