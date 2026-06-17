# PS15 — Forecasting and/or Nowcasting of Solar Flares using Combined Soft and Hard X-ray Data from Aditya-L1

**Mentors:** Sarwade Abhilash Rajendra, Srikar Paavan Tadepalli, Kiran L
**Explainer:** Video 2, 46:50–54:17
**Slides:** Captured.

## Solar flares & space weather (slide)
- **Solar flares:** explosive release of magnetic energy.
- **The threat:** damage to power grids, GPS, satellites, etc. (ESA space-weather impact diagram shown — CMEs, solar energetic protons, single-event upsets, geomagnetically induced currents, etc.).
- **The goal:** real-time tracking (**nowcasting**) and advanced warning (**forecasting**).

## Aditya-L1 X-ray instruments (slide)
- **SoLEXS** (Solar Low Energy X-ray Spectrometer) — **soft X-rays**, measuring thermal heating of the plasma; **gradual** flux enhancement.
- **HEL1OS** (High Energy L1 Orbiting X-ray Spectrometer) — **hard X-rays**, measuring non-thermal particle acceleration; **impulsive** flux enhancement.
- (Aditya-L1 payload diagram: VELC, SUIT, HEL1OS, Magnetometer, PAPA, SoLEXS.)

## X-ray lightcurves (slide)
- **Multi-channel data** from soft + hard X-ray detectors. Energy channels span **2–3, 3–6, 6–10, 10–15, 15–25, 25–40, 40–55, 55–70, 70–125 keV** (soft channels gradual; harder channels impulsive/noisier).
- **Pre-flare activity:** early flux enhancements.
- **Quasi-periodic pulsations (QPPs):** oscillatory variations in hard X-rays.
- "No two solar flares look similar" → need an intelligent system to capture these fine structures.

## Objective 1 — detection / nowcasting (slide)
- Nowcasting = **detection and classification** of flares (plot marks **Start / Peak / Stop** on the flux curve).
- Handle the large **dynamic range** (big flares ~10⁻⁵ W/m² down to tiny near-background).
- **Milestone 1:** build detection algorithm for **SoLEXS & HEL1OS independently**.
- **Milestone 2:** generate a **unified Master Flare Catalog**.

## Objective 2 — prediction / forecasting (slide)
- Forecasting = prediction of flares. Plot shows observed flux up to **current time T=0**, a **15-min forecast window**, and **"precursor heating detected"** (red) just before a flare.
- **Milestone 1:** predict **probability of a flare in the next N minutes**.
- **Milestone 2:** **multi-class probabilities** for different flare classes (intensity/energy level).

## Outcomes & roadmap (slide)
- **Expected outcomes:** combined SoLEXS & HEL1OS **nowcasting catalog**; **forecasting system with quantifiable lead time**; **visual dashboard**.
- **Roadmap:** download data from **ISSDC portal** → characterize **SXR/HXR temporal structures** → nowcasting (build unified master catalog) → forecasting (train time-series for prediction).

## Resources & evaluation (slide)
- **Datasets:** Primary — **Aditya-L1 SoLEXS & HEL1OS (Level-1)**; Supplementary — any open-source data (e.g. magnetograms, mentioned in talk).
- **Evaluation:** flare detection accuracy across **low and high-class** flares; **high true-positive / low false-positive rate**; lead time for forecasting (slide labels it "low lead time"; in the talk the mentor said target **15–30 min** lead).

## Q&A
- (1:04) You **may use the GOES flare catalog** for training, but GOES is **less sensitive than SoLEXS** and misses many flares — fine as a starting point.
- (1:12) The **novelty** vs prior work: Aditya-L1 gives **simultaneous soft + hard X-ray** observation (not previously available at this sensitivity). Build a novel algorithm that **ingests both simultaneously** — the unexplored angle.

## Official description (website) — authoritative additions
- **Data:** Primary = **Aditya-L1 SoLEXS (Level-1) + HEL1OS (Level-1)** via the **ISSDC PRADAN** portal; any supplementary open-source data allowed.
- **Required deliverable:** an **interface that visualizes the X-ray light curves and triggers visual alerts** when a flare is nowcasted or forecasted (not just a catalog).
- **Method:** read light curves → understand soft/hard flare shapes → build **independent detection per instrument** → merge into a **master catalog** → train a time-series model for **P(flare in next N minutes)**.
- **Evaluation:** detection of low- and high-class flares; **high True Positive Rate + low False Alarm Rate**; **lead time = how many minutes before the flare peak** the alert triggers.

## Our take
Outside our imagery core (1-D X-ray time-series), but the cleanest "novelty" story of the 15: the mentor named the open research gap (joint soft+hard X-ray ingestion). Indian-pride angle (Aditya-L1) plays well with ISRO judges. Data is public via ISSDC. The two-part structure (build a detection catalog, then a forecaster) is well-defined. Pick only with a time-series-comfortable teammate; if so, high-ceiling.
