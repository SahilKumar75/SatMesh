# PS7 — AI-Enabled Detection of Exoplanets from Noisy Astronomical Light Curves

**Org:** Physical Research Laboratory (PRL), Ahmedabad
**Team / mentors:** Rishikesh Sharma, Churchil Dwivedi, Neelam JSSV Prasad, Kapil Kumar Bharadwaj
**Explainer:** Video 1, 1:01:22–1:08:11
**Slides:** Captured.

## Concept — transit photometry (slide)
A planet crossing its star dips the star's brightness periodically.
**Key parameters:**
- **Event Depth** ≈ (R_planet / R_star)² → planet size.
- **Event Duration** → time to cross the star.
- **Orbital Period** → spacing between consecutive dips.

**Dedicated space missions** (observe millions of stars for periodic transit signals): **TESS, Kepler, K2**. This PS uses **TESS**.

## Problem statement — five steps (slide)
1. **Detrending** — remove noise and systematic variations from the raw stellar light-curve data to reveal underlying signals.
2. **Identification** — spot periodic dips in light curves that could indicate astrophysical phenomena.
3. **Characterization** — measure/estimate key parameters (transit depth, period, duration) for detected events.
4. **Classification** — develop a framework to categorize dips into **transits, eclipses, blends, or other astrophysical signals**.
5. **Statistical Significance** — provide **signal-to-noise ratios and formal significance levels** for all identified findings.

**Dataset provided:**
- **TESS raw light curves** (target / unknown data).
- A **curated dataset** for different classifiers to train the AI model.

## Step detail (slides)
- **01 Detrending:** raw curve has a ramp/trend (shown in red) → detrended flat curve (blue); axes = Normalized Flux vs Elapsed Observation Time (days). Trends are instrument/systematic, not physical.
- **02 Identifying events:** **Orbital Period = interval between two consecutive transit events** in the light curve; a single transit is examined **zoomed & phase-folded** (flux vs hours from transit midpoint).
- **03 Transit shape fitting:** fit a trapezoid (best-fit transit model with ingress/egress markers). Example **estimated parameters** from the slide:
  - Baseline Flux (f₀): 1.000259
  - Transit Depth: 1.4619% (14618.6 ppm)
  - Total Duration (T_tot): 2.633 hours
  - Ingress/Egress (T_in): 0.444 hours
  - Flat-Bottom Duration: 1.745 hours
  - (U-shape vs V-shape distinguishes planet vs eclipsing binary.)

## Further steps & expectations (slide)
4. **Develop the AI classifier** based on the transit shape parameters and train it with the given known datasets.
5. **Apply it to the provided unknown datasets**; identify and classify the events.
6. **Provide the basic parameters with the significance level.**

## Evaluation
- Robustness of the AI-driven classifier.
- Quality of recovered planetary/stellar transit signatures.
- Accuracy of final predicted parameters + significance levels.
- (Q&A 1:30) All sub-tasks matter: noise removal, transit detection, and distinguishing exoplanets from eclipsing binaries.

## Tools
- Pure **Python** (NumPy / Pandas to access the data). **No specialized software** required. (Note: real-world toolkits like `lightkurve`, `astropy`, BLS periodograms map directly onto steps 1–3, though not named on the slide.)

## Official description (website) — authoritative additions
- **Contamination sources** in crowded fields: stellar blending by foreground/background sources in the aperture, plus detector-response noise. Brightness dips can come from a **transiting planet, an eclipsing binary, or starspots** — disentangling these in noisy data is the core difficulty.
- **Classify dips into:** transits, eclipses, **blends**, and other astrophysical categories; give **SNR / significance**; for transits estimate **depth, period, duration**.
- **Data:** TESS raw light curves from **https://archive.stsci.edu/tess/tic_ctl.html** — download one sector's high-cadence data (~**20–30k light curves**). A **curated labeled training set** (known exoplanets, false positives, eclipsing binaries) will also be provided.
- **Required deliverable not on the slides:** a **report (max 3 pages)** covering methodology, assumptions, tools/libraries, and how uncertainties are estimated. Plus light-curve visualization with the detected/classified signal and a confidence level.
- **Evaluation:** detection+classification accuracy, parameter accuracy, methods/approach, visualization clarity.

## Our take
Different skillset from our CV/geospatial core — 1-D time-series, not imagery. But the slides make the pipeline very concrete (detrend → BLS-style period search → trapezoid fit → train classifier on labeled set → run on unknown set), and the field of strong competitors is thinner. The clean part: ISRO hands you both a labeled training set and an unknown test set, so it's a well-posed ML problem. Only pick if a teammate is comfortable with signal processing.
