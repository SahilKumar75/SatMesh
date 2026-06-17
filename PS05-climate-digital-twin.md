# PS5 — AI-Powered Digital Twin of India's Climate using India's National Data

**Org:** NRSC / ISRO
**Mentors:** Dr. Kandula V Subrahmanyam (Sci/Eng-SF, NRSC/ISRO), Mr. Syed Shadab (Sci/Eng-SF, NRSC/ISRO), Mr. C. Sarat (Sci/Eng-SC, NRSC/ISRO)
**Explainer:** Video 1, 45:43–53:12
**Slides:** Captured.

## Title-slide thumbnail
India map layered with **Temperature (°C), Rainfall (mm), Humidity (%)** fields — the multi-variable climate state the twin should represent.

## Description (slide)
- An "AI-powered Digital Twin of India's Climate using national datasets" = a **high-fidelity, dynamic virtual replica** of India's climate system that continuously evolves using real-time and historical observations.
- Hard because weather systems operate across **highly complex, multidimensional scales**.
- Uses AI, ML, and **Data Assimilation** to fuse heterogeneous datasets into near-real-time climate states and predictive scenarios; aims to capture **monsoon variability, extremes, drought evolution** with better accuracy than conventional models.
- Explicit pivot **away from traditional numerical physics models** toward a **purely data-driven framework** tailored to the Indian subcontinent.

## Reference platform
EU **Destination Earth (DestinE)** — https://platform.destine.eu/ — "Climate DT (Gen 2)", global 2m temperature with IFS-NEMO model, 2015–2050 timeline. Use as the analogue/inspiration for what a climate digital twin looks like.

## Objectives (slide)
1. Design & develop a **scalable framework** for an AI-driven digital twin of India's climate using national datasets (satellite, ground observations, reanalysis).
2. Demonstrate a **Proof of Concept (PoC)** for key climate variables **rainfall and temperature**, generating high-resolution analyses + **short-term predictions over a selected pilot region**.
3. **Interactive geospatial visualization** on a map dashboard.
4. A **"What-if" simulation module** showing impacts of temperature or rainfall changes.

## Expected outcomes (slide)
- Proof-of-Concept of the digital twin.
- AI-based prediction capability.
- Visualization dashboard.
- Scenario simulation capability.
- Scalable framework for national deployment.

## Datasets (slide — with exact links)
IMD provides high-resolution gridded rainfall & temperature (long-term historical, consistent spatial/temporal coverage) — good for training and forecast validation. Integrate IMD gridded data with INSAT satellite obs for a surface + atmospheric framework.

**IMD data links:**
- Rainfall: https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_Bin.html (and NetCDF: https://imdpune.gov.in/cmpg/Griddata/Rainfall_25_NetCDF.html)
- Max temp: https://imdpune.gov.in/cmpg/Griddata/Max_1_Bin.html
- Min temp: https://imdpune.gov.in/cmpg/Griddata/Min_1_Bin.html

**Product table:**
| Parameter | Product / source |
|---|---|
| INSAT Land Surface Temperature (LST) | `3RIMG_L2B_LST` — https://www.mosdac.gov.in/ |
| INSAT Sea Surface Temperature (SST) | `3RIMG_L2B_SST` — https://www.mosdac.gov.in/ |
| INSAT Rainfall | `3RIMG_L2B_IMC` — https://www.mosdac.gov.in/ |
| Ground gridded rainfall (IMD) | Gridded Rainfall **0.25° × 0.25°** — IMD link above |
| Ground gridded temperature (IMD) | Max Temperature **1.0° × 1.0°** — IMD link above |

**Coverage notes:** IMD daily gridded rainfall 0.25° spans **1901–2024** (~124 years, 135×129 grid). Daily min/max temperature 1.0° spans **1951–2025** (31×31 grid). Cite Pai et al. 2014 (rainfall), Srivastava et al. 2009 (temperature).

## Suggested tools (slide)
AI/ML/DL frameworks (TensorFlow, PyTorch); visualization: **CesiumJS 3D, Streamlit, Leaflet**, etc.

## Workflow (slide — PoC pipeline)
**Problem Definition** (select region & variable) → **Data Ingestion** (rainfall & temperature) → **Data Pre-processing** (spatial masking, normalization, zone segmentation, interpolation) → **Model Development** (suitable DL/ML model or ensemble generating **T+1 forecast**; training & validation) → **Visualization & Interactive Dashboard** (Streamlit, CesiumJS 3D) → **What-If simulations**.

## Evaluation criteria (slide)
Problem understanding & clarity; data usage & pre-processing; model development & technical approach; prediction performance & validation; digital-twin concept implementation; visualization & UI; innovation & creativity; presentation & communication. (Talk: target accuracy ~**80–85%** on test data.)

## Official description (website) — authoritative additions
- **ISRO platforms named:** integrate national datasets from **Bhuvan, MOSDAC, NICES** and EO missions (**INSAT, Oceansat**), plus IMD ground networks, reanalysis, and hydrological datasets. Framed around **Atmanirbhar Bharat** / indigenous climate intelligence.
- A climate digital twin (per the description) should integrate **several climate models to handle uncertainty**, include applications for climate-sensitive sectors, and provide interfaces to configure simulations/output — but the **PoC scope stays narrow: rainfall + temperature over one pilot region** with short-term prediction, dashboard, and what-if module.

## Our take
Overscope risk is real but the slides quietly narrow it: the PoC only needs **rainfall + temperature over one pilot region with a T+1 forecast**, plus a dashboard and a what-if slider. That's a tractable build. Differentiation comes from a clean DestinE-style 3D dashboard and a credible data-assimilation story, not from modeling all of India. Datasets are fully specified and downloadable now — low data risk.
