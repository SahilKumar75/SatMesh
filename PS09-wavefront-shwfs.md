# PS9 — Developing and Optimizing Algorithms for Wavefront Reconstruction and Turbulence Characterization using Shack-Hartmann Wavefront Sensor (SH-WFS) Time-Series Data

**Org:** Physical Research Laboratory (PRL)
**Mentors:** Dr. Mudit Kumar Srivastava, Jay Chitroda
**Explainer:** Video 2, 7:36–14:10
**Slides:** Captured (the live slideshow froze, but the deck screenshots are now in hand).

## Title-slide thumbnail (target pipeline + performance)
Pipeline graphic: **SH-WFS time-series input** (lenslet spot-field grid) → **real-time processing pipeline** (iterative centroid estimation → iterative centroid estimation → zonal reconstruction) → **reconstructed wavefront** (3D surface plot). Performance targets shown on the mockup:
- **Latency: < 1 ms / frame**
- **Throughput: ~100 fps**
- **Stability metric: σ < 0.2 λ**

These numbers signal they want a **real-time-capable** reconstructor, not just an offline one.

## Problem domain
A fundamental problem of **wavefront sensing and phase retrieval**. **This PS focuses on adaptive optics for ground-based astronomy.**

## Applications (slide)
- Adaptive Optics in ground-based astronomy.
- Free-space optical communications.
- Deep-tissue imaging and ophthalmology research.
- (In the talk he also mentioned quantum key distribution; the slide lists the three above.)

## Background — adaptive optics loop (slide diagram)
Light from a star passes through **atmospheric turbulence** → **disturbed wave** at the telescope optics → a **wavefront corrector** (deformable mirror) driven by a **real-time controller** in a **control loop** reshapes it → **corrected wave** → **beam splitter** sends part to the **wavefront sensor** (feedback) and part to the **scientific CMOS camera** (sharp image). "With AO vs Without AO" images show the sharpening. (Diagram courtesy Kodai Yamamoto, Kyoto University.) You must know the distorted wavefront's shape before you can correct it → that's the WFS's job.

## Shack-Hartmann principle (slide)
- A camera behind an **array of lenslets** samples the incoming wavefront into a **spot field** on the CCD.
- (a) Plane wave → **regular spot field**.
- (b) Distorted wave → **spots displaced from their reference positions** (displacement Δx).
- Spot deviation → local slopes → reconstruct wavefront.
- **Reconstruction methods (slide):** Modal method, **Zonal method**, Direct gradient control, Machine learning / Deep learning. (Free to choose.)

## Expected solution / steps (slide)
1. For each WFS frameᵢ, **identify spot positions** (suitable centroiding algorithm).
2. **Calculate spot deviations.**
3. Utilize/optimize an existing technique **OR develop your own algorithm** to **reconstruct the wavefront**.
4. Use the reconstructed wavefront map to derive **turbulence characteristics** — coherence length (r₀) and coherence time (τ₀).
5. Use the **conjugate** of the reconstructed wavefront to derive an **actuator map** in terms of **actuator stroke lengths**, accounting for **inter-actuator coupling**.

> Note the slide says the *conjugate* of the reconstructed wavefront drives the actuator map (the mirror applies the inverse/negative of the distortion). Dataset = a provided time series of WFS frames.

## Q&A (1:07)
- **No hardware constraint.** Modern CPUs handle the image processing / matrix math; FPGA acceleration not necessary. Mentor suggested implementing in a **low-level language like C** for speed — consistent with the <1 ms/frame, 100 fps real-time targets above.

## Official description (website) — authoritative additions
- **Data format:** a time series of SH-WFS frames as **.bmp files**, captured a few ms apart by a science-grade camera. Provided metadata: pixel size + frame resolution; MLA size, number of lenslets, focal length; pupil size of the turbulated beam; DM info + **inter-actuator coupling** (dataset provided).
- **Fried geometry (key assumption):** the DM actuator grid and the MLA lenslet grid are arranged in **Fried geometry** — design your reconstruction around that.
- **Reconstruction:** derive the wavefront phase map W(xᵢ,yᵢ) and its **Zernike coefficients**; methods include zonal/modal (orthogonal polynomials) or direct integration. Then derive r₀ and τ₀, and an actuator map A(xᵢ,yᵢ) (conjugate of the wavefront) including inter-actuator coupling.
- **Real-time bar:** corrections must beat the atmosphere's ~10 ms coherence time → C strongly advised.
- **Evaluation:** phase maps that conform to turbulence stats; correct r₀/τ₀; **speed + computational efficiency**.

## Our take
Outside our CV/geospatial core — optics + numerical linear algebra (slope-to-phase reconstruction) on sensor time series, with a hard real-time bar (<1 ms/frame). Small, specialised field of competitors; PRL clearly wants an efficient classical reconstructor (C / zonal methods), though ML is allowed. Only viable with an optics/signal-processing teammate.
