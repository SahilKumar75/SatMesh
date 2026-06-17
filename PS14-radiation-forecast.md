# PS14 — Forecasting Energetic Particle Radiation Environment for ISRO's Geostationary Satellites

**Org:** Space Physics Laboratory (SPL), Vikram Sarabhai Space Centre (VSSC), Trivandrum
**Mentors:** Dr. Ankush Bhaskar (Tukaram), Mr. Pritesh Meshram
**Explainer:** Video 2, 38:11–45:08
**Slides:** Captured.
**Tags:** Space Technology · AI/ML · Radiation Science.
**Headline targets (title slide):** **30–45 min** advance warning · **6–12 hr** forecast window · **>2 MeV** electron flux.

## Science background (slide)
- **Van Allen radiation belts** trap high-energy charged particles. **Inner belt: protons (stable). Outer belt: electrons (highly dynamic).**
- **GEO orbit (~35,786 km) sits within the outer belt.** Relativistic electrons (**>2 MeV**) cause spacecraft anomalies.
- **Solar-wind drivers:** solar wind **speed** (main driver of outer-belt dynamics); **IMF** (southward **Bz** enhances particle energisation); solar wind **density** (compresses the magnetosphere).
- Solar storms inject and accelerate electrons to relativistic speeds → **"killer electrons"** that damage satellites.

## Objective (slide)
Develop an algorithm for **reading, processing, visualization, and real-time forecasting of energetic electron fluxes at geosynchronous orbit** (specifically for Indian longitude).

## Datasets (slide — three sources, with roles)
| Source | Span | Contents / role |
|---|---|---|
| **GOES satellite** (NOAA) | **11 years** | **>2 MeV electron fluxes** + satellite position, in **CDF format**, at geostationary orbit → the **target** variable |
| **Wind spacecraft** (CDAWeb) | **11 years** | Solar wind speed (Vsw), IMF components (Bz), particle density (Nsw) at interplanetary space → the **input features** |
| **GRASP / GSAT** (PRADAN/ISSDC) | **~2 years** | ISRO payload data, **Indian-longitude fluxes** → **validation & comparison** at Indian-longitude GEO |

> Resolves the earlier audio ambiguity: the Indian validation source is **GRASP/GSAT** (sample shown: GRASP 5-min averaged electron+proton flux, April 2018).

**Exact data links (slide):**
- Electron flux (GOES): https://www.ngdc.noaa.gov/stp/satellite/goes/index.html
- Solar wind: https://cdaweb.gsfc.nasa.gov/
- GRASP: https://pradan1.issdc.gov.in/grasp/

## Methodology — AI/ML pipeline (slide)
1. **Read & visualize** — CDF parsing, data exploration.
2. **Preprocess** — remove spikes, interpolate gaps.
3. **Feature select** — solar-wind variables, correlation analysis.
4. **Train AI/ML** — LSTM, Transformer, time-series forecast.
5. **Validate & test** — 30–45 min ahead (nowcast) + 6 h & 12 h forecast.

## Expected outcomes (slide)
- **AI/ML forecasting algorithm** — 30–45 min, 6 h, and 12 h ahead electron-flux predictions at GEO.
- **Data pipeline & visualization** — CDF reader, preprocessing tools, and a **real-time-style flux dashboard**.
- **Validation using ISRO satellite data** — cross-validated with **GRASP/GSAT** at Indian longitude.
- Target UI: a **"Space Weather Dashboard"** (real-time + forecast) showing solar wind (DSCOVR current), current **>2 MeV electron flux** in **pfu**, a 24-hour forecast curve, and a **predicted-risk** indicator (Low → Elevated → High).

## Q&A
- (1:02) Algorithm choice open, but **history matters** → memory networks (LSTM). Evaluate with **RMSE** vs ground truth.
- (1:04) **Finale:** test on **real-time solar-wind data** (ACE/Wind via SDA/CDAWeb), forecast fluxes, validate against **real-time GOES fluxes** (NOAA). Train on the **11-year** solar-wind dataset first, then use for real-time validation.

## Official description (website) — authoritative additions
- Confirms the data split: **11 years GOES + 11 years Wind + 1–2 years GRASP/GSAT (Indian-longitude validation)**, all **CDF format**.
- Forecast horizons: **≥30–45 min advance + reasonable 6 h and 12 h ahead**.
- **Evaluation explicitly weights science understanding:** grasp of solar wind + radiation belts; correct reading/visualization of the data; AI/ML identification + optimization; accuracy of predicted fluxes at GEO. (So domain reasoning in the writeup counts, not just RMSE.)

## Our take
Adjacent to PS15 (both space-weather time-series). Outside our imagery core — multivariate sequence forecasting (solar wind → electron flux) with LSTM/Transformer. The deck fully specifies data, URLs, pipeline, and a polished dashboard target, so design risk is low; the differentiator is feature engineering + magnetosphere domain knowledge. Pick only with a time-series/physics-comfortable teammate.
