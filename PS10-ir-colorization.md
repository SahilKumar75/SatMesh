# PS10 — Infrared Image Colorization and Enhancement for Improved Object Interpretation

**Org:** Space Applications Centre (SAC), ISRO
**Mentors:** Ashutosh Gupta, Hemant K. Lalwani, Jugal Patel
**Explainer:** Video 2, 15:07–22:13 (slide date: 16 June 2026)
**Slides:** Captured.
**Official GitHub (dataset prep):** https://github.com/jugal-sac/IR-colorization-BAH2026

## Problem statement (slide)
Develop an **end-to-end framework** that **super-resolves structural details** and predicts **realistic colorization (RGB translation)** for Thermal Infrared (TIR) satellite images.
- TIR images are vital for Earth observation but have **low resolution** vs visible bands.
- They're **difficult for humans and AI to interpret** with traditional pipelines.

## Objective (slide)
- **Super-Resolution:** improve the resolution of TIR inputs.
- **Colorization:** map TIR features to realistic RGB representations **using generative AI methods**.
- **Preserve structural and spectral integrity.**

## Resolution context (slide)
- Landsat-9 imagery at 30 m: RGB is crisp (buildings, roads visible); **TIR-1 actual sensor resolution is 100 m** (blurry, can't resolve structures).

## Dataset & workflow (slide — 4 steps)
1. **Input:** TIR satellite imagery @ **200 m**.
2. **Super-resolve** → @ **100 m**.
3. **Colorize** → RGB @ **100 m**.
4. **Compare** the output against original TIR @ 100 m and **RGB reference imagery**.

## Expected output (slide)
- An end-to-end **trained deep-learning pipeline**.
- **Input:** single-channel TIR image @ 200 m.
- **Output:** (1) high-resolution TIR @ 100 m; (2) colorized RGB @ 100 m.

## Dataset & tech stack (slide)
- **Dataset:** Landsat-9 (USGS) processed **TIR1–RGB pairs** prepared using the team's GitHub instructions.
- **Framework:** Python end-to-end.
- **Models:** GANs / Diffusion models / SoTA image-to-image models.
- **Libraries:** GDAL, Rasterio, **tifffile**, OpenCV.

## Workflow summary (slide flowchart)
Start (data source) → **Download Landsat-9 bands B2, B3, B4, B10** → three branches:
- **B2+B3+B4 → merge into RGB** → downscale RGB by 3.3× (→100 m) → create image patches.
- **TIR B10 → downscale by 3.3× (→100 m)** → create image patches (this is the SR target).
- **TIR B10 → downscale by 6.7× (→200 m)** → create image patches (this is the SR input).
→ **Super-resolution model** (back to 100 m original size) → **IR image colorization** → End: colorized IR image.

> Downscale factors are relative to the 30 m product grid: 30 m × 3.3 ≈ 100 m, 30 m × 6.7 ≈ 200 m. (B10's native sensor resolution is 100 m but USGS distributes it resampled to 30 m.)

## Evaluation parameters (slide)
- **Image quality:** PSNR, SSIM, FID.
- **Qualitative:** visual inspection to prevent **hallucinations**.
- **Preferred:** low **inference time per tile**.
- **Bonus:** "Can you design and implement **physics-informed modeling** for the task?" (NOT diffusion — diffusion is just one allowed model choice; the bonus is physics-informed modeling.)

## Official description (website) — authoritative additions
> The website version is **more generic** than the live SAC deck above. Where they differ, the SAC deck (200 m→100 m factors, the GitHub repo, the physics-informed bonus) is the detailed spec; the website adds the points below. Read both.
- **Why IR:** captured at night / in bad weather, but monochrome, low-contrast, lacking RGB semantic texture.
- **Models named:** **CycleGAN, Pix2Pix**, or other SoTA image-to-image translation architectures.
- **Semantic-integrity constraint (new):** incorporate a **semantic mask or pre-trained land-cover classifier** so IR signatures map to the *correct* colors (water→blue, forest→green) and don't hallucinate.
- **Downstream goal:** outputs should measurably **improve subsequent object detection / segmentation**.
- **Evaluation:** PSNR, SSIM, FID; inference time per tile; visual inspection for hallucinations.

## Our take
Strongest pure-CV fit alongside PS2. **Lowest data risk of any statement** — public Landsat-9 via USGS plus an official GitHub repo that hands you the exact TIR1–RGB pairing pipeline. The work is two well-trodden CV tasks (super-resolution + image-to-image colorization). Where teams separate: (1) the FID/hallucination bar, since colorizing thermal data is ill-posed (many plausible colors); (2) the **physics-informed modeling bonus** — tying RGB prediction to thermal-emission physics is the differentiator most teams won't attempt. Note the recurring BAH theme: PS1 and PS10 both reward "physics-informed" framing.
