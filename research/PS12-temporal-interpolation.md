# PS12 — Fill in the Frames Seamlessly: Enhancing Temporal Resolution of Satellite Imagery using AI/ML-Based Optical Flow

**Mentors:** Sushantini Muvvala, Ghansham Sangar
**Explainer:** Video 2, 25:30–32:04
**Slides:** Captured.
**Tags:** Remote Sensing · Deep Learning · Optical Flow. (Sample shown: INSAT-3DS IMG Thermal Infrared-1 @ 10.78 µm, L1B full disk.)

## Problem — the temporal-resolution gap (slide)
Geostationary satellites capture at fixed intervals — **30 min for INSAT-3DS**, **10 min for Himawari/GOES** — leaving critical gaps in monitoring fast-evolving phenomena:
- **Cyclones** — rapid intensification between frames goes undetected (example shown: Cyclone Ditwah captured by INSAT-3DS).
- **Wildfires** — thermal hotspots evolve faster than capture intervals.
- **Thunderstorms** — convective cells form and dissipate within minutes.
- **Floods** — rapid inundation changes are missed entirely.

## Approach (slide)
Build an end-to-end AI/ML pipeline that generates **high-fidelity intermediate frames**, effectively doubling or quadrupling temporal resolution **without additional hardware**.
1. **Optical Flow & Synthetic Frame Generation** — deep-learning optical-flow models to synthesize realistic intermediate frames; named examples: **RAFT, RIFE, Super SloMo**.
2. **Rigorous Validation** — evaluate against ground truth with **SSIM, MSE, PSNR, FSIM**.
3. **Temporal Upscaling** — improve resolution **30 min → 15 min → 7.5 min** for INSAT-3DS data.

## Datasets required (slide — with exact links)
TIR band (~10 µm) from geostationary satellites in **.nc or .h5** format.
- **GOES-19 ABI Channel 13** — NOAA GOES-19 AWS bucket; high-frequency (10 min) ground truth for training & validation: `https://noaa-goes19.s3.amazonaws.com/index.html#ABI-L1b-RadM/`
- **INSAT-3DS / 3DR TIR1** (product `3SIMG_L1B_STD`) — MOSDAC repository; **primary target dataset** for final interpolation at 15-min resolution: `https://mosdac.gov.in`
- **Other sources:** Himawari-8/9, Meteosat-12.
- **Libraries:** **PyTroll** for data processing.

## Expected outcomes & deliverables (slide)
1. **Trained model** — AI/ML optical flow + interpolation, trained on GOES-19 / Himawari-8 TIR data.
2. **Interpolated frames** — synthetic intermediate frames for INSAT-3DS at **15-min resolution in .h5**.
3. **Web dashboard** — interactive visualization with **ground-truth vs interpolated animation comparisons**.
4. **Validation report** — full metric analysis (SSIM, MSE, PSNR, FSIM) with plots and qualitative assessment.

**Impact:** near real-time monitoring of cyclones, fires, thunderstorms using existing satellite infrastructure — no new hardware.

## Q&A
- (1:02) Prioritize **thermal bands** (TIR1, TIR2, ~10 µm).
- (1:08) Metrics: MSE, RMSE, SSIM, and feature-based methods (FSIM).

## Official description (website) — authoritative additions
- **Motivation framing:** traditional optical-flow interpolation gives blurred images/artifacts and fails on fast, non-linear cloud motion → use **AI/ML optical flow**.
- **Models named:** **Super SloMo, RIFE** (DL video interpolation), trained/fine-tuned on the satellite data.
- **File format:** the model's **input and output files should be .nc (NetCDF)**. (The slide deck mentioned .h5 for the INSAT deliverable — support both; website emphasizes .nc.)
- **Concrete recipe:** Steps 1–3 on GOES-19 — e.g. take frames at 00:00 and 00:20, output 00:10, validate against the real 00:10. Step 4 — apply the best model to **INSAT-3DS/3DR** at **15-min** resolution. Datasets: GOES-19 ABI Ch-13 (NOAA AWS), INSAT-3DS/3DR TIR1 (MOSDAC), Himawari-8.
- **Deliverables:** frame interpolation + a **web dashboard** with time-lapse animations (ground-truth vs interpolated) + a metrics report (SSIM, MSE, PSNR, FSIM, and metrics that capture cloud movement).
- **Evaluation:** interpolation image quality (MSE/PSNR), web-GUI design, and visual quality of the INSAT-3DS interpolation.

## Our take
Strong CV fit — video frame interpolation (RAFT/RIFE/Super SloMo) on single-channel satellite IR, a well-defined supervised problem. The deck is generous: named models, exact dataset URLs (NOAA AWS + MOSDAC), and a clear train-on-GOES-19 → apply-to-INSAT-3DS recipe. Two differentiators: handling the **domain shift** from 10-min GOES training to the 30-min INSAT-3DS target (and pushing to 7.5 min), and the **web dashboard with side-by-side animations** (presentation points). Low data risk. Among the most tractable end-to-end builds for a 30-hour finale.
