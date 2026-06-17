# PS3 — Development of Surface AQI & Identification of HCHO Hotspots over India using Satellite Data

**Mentors:** Mahesh, Mahalakshmi, Kanchana, Hareef Baba Shaeb K (HCHO objective spoken by "Mrs. Kima" in talk — likely one of these)
**Explainer:** Video 1, 26:18–36:41
**Slides:** Captured.

> Two separate objectives, evaluated separately (confirmed in Q&A): (A) surface AQI maps, (B) HCHO hotspot detection.

## Title-slide thumbnail
India map color-coded by AQI (deep **red over the north / Indo-Gangetic Plain**, yellow through the centre, **green over the south**), flanked by small time-series line plots — i.e. surface-AQI spatial map + temporal trends is the target output style.

## Objective A — Surface AQI maps
- AQI quantifies air pollution from **surface** concentrations of PM2.5, PM10, NO2, SO2, CO, O3.
- **Core problem:** satellites measure **columnar** concentrations, not surface. Convert columnar → surface.
- Inputs:
  - INSAT-3D product: Aerosol Optical Thickness/Depth (columnar aerosol burden).
  - Sentinel-5P **TROPOMI**: columnar NO2, SO2, CO, O3.
  - Surface ground truth: **CPCB** (Central Pollution Control Board) measured PM2.5 etc. — publicly available.
  - Meteorology: temperature, relative humidity, wind speed (control surface concentration).
- Method: AI/ML / deep learning (CNN, LSTM, etc.) to map columnar → surface; validate against CPCB with statistical accuracy metrics; produce India-wide **surface AQI maps** (color-coded green=good → red=bad).
- Motivation: CPCB stations are concentrated in cities; satellites can estimate AQI in regions ~100 km from stations.

## Objective B — HCHO (formaldehyde) hotspots
- HCHO matters for ozone chemistry; a VOC observable from satellites.
- Satellite sources for HCHO: GOME, SCIAMACHY (mentioned as NASA-adjacent), OMI (Ozone Monitoring Instrument), TROPOMI.
- Biomass burning (agricultural residue burning, forest fires) releases large HCHO → can be monitored.
- Sub-objectives:
  - High-resolution maps of HCHO hotspots during biomass-burning seasons + identify major source regions (e.g., Indo-Gangetic Plain, forest-fire zones, industrial/anthropogenic sources).
  - Extract biomass-burning periods using **fire-count datasets** (MODIS, VIIRS high-res).
  - Correlate fire activity with HCHO levels; assess transport influence using wind / reanalysis data.

## Slide: workflow diagrams ("Image representing problem statement")

**Objective-1 pipeline:**
- Inputs (three boxes): Multi-Pollutant Concentrations (**columnar satellite data**) + Multi-Pollutant Concentrations (**CPCB surface data**) + Meteorological data (**IMDAA / ERA5 / MERRA-2**)
- → **Deep Learning Model (CNN-LSTM)**
- → **Spatial maps of surface AQI**

**Objective-2 pipeline:**
- Input Data: **Remote Sensing Data** + **Fire Data (MODIS / VIIRS)** + **Re-analysis Meteorological data**
- → **Processing using Python, MATLAB & Google Earth Engine**
- → Outcomes: high-resolution maps of HCHO hotspots during biomass-burning seasons over India; identification of major source regions (e.g. Indo-Gangetic Plain, forest-fire zones); temporal evolution of HCHO during burning events; correlation between fire counts and HCHO enhancement.

> Note the named reanalysis met products: **IMDAA, ERA5, MERRA-2** (Objective-1) — use one of these for the met inputs.

## Datasets
- INSAT-3D AOD; Sentinel-5P TROPOMI (NO2/SO2/CO/O3/HCHO); CPCB ground data; MODIS/VIIRS fire data; reanalysis met (IMDAA/ERA5/MERRA-2). Download links on the website.
- Tools: Python, MATLAB, Google Earth Engine, or any feasible.

## Expected outcomes
- Spatial surface AQI maps for India.
- High-resolution HCHO hotspot maps during biomass-burning seasons + major source regions.
- Spatiotemporal HCHO maps + case-study correlation of fire activity vs HCHO enhancement.

## Official description (website) — authoritative additions
- **Policy context (good for the proposal's "impact" framing):** National Clean Air Programme (NCAP, 20–40% reduction in non-attainment cities), SDG target **11.6**, Chintan Shivir 2.0. Note: >half the global population lives >100 km from an air-quality monitor — the gap satellites fill.
- **Obj-1 specifics:** INSAT-3D **AOD → deduce surface PM2.5**; combine columnar satellite + CPCB surface + reanalysis met (IMDAA/ERA5/MERRA-2) into a CNN/LSTM/CNN-LSTM.
- **Exact dataset URLs:**
  - INSAT-3D AOD: https://www.mosdac.gov.in/insat-3d-data-products
  - Sentinel-5P TROPOMI (NO2/SO2/CO/O3/HCHO): GEE catalog + https://download.geoservice.dlr.de/S5P_TROPOMI/files/L3/
  - CPCB ground data: https://airquality.cpcb.gov.in/ccr/
  - MODIS/VIIRS fire (FIRMS): https://firms.modaps.eosdis.nasa.gov/active_fire/
  - Reanalysis: ERA5 (CDS), IMDAA (ncmrwf), MERRA-2 (GES DISC)
- **Evaluation — Obj-1:** RMSE, R, MAE vs CPCB. **Obj-2:** hotspot detection accuracy/clarity, multi-source integration, scientific interpretation, visualization quality, methodology innovation.

## Evaluation (slide bullets)
- Model performance vs ground-based CPCB values (statistical parameters, closeness to ground truth).
- **Integration of multi-source datasets.**
- **Scientific interpretation of results.**
- **Visualization quality** (spatial maps over Indian region, time series).
- **Innovation in methodology.**
