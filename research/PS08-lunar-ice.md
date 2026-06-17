# PS8 — Detection & Characterization of Subsurface Ice in Lunar South Polar Regions Using Chandrayaan-2 Radar & Imagery Data for Landing Site and Rover Traverse Planning

**Org:** Physical Research Laboratory (PRL), Ahmedabad
**Mentors:** Dr. Rishitosh Sinha, Dr. Rajiv R. Bharti
**Explainer:** Video 1, 1:08:46–1:21:13
**Slides:** Captured.

## Framing (slide)
"Can you discover hidden lunar ice deposits and design India's future robotic exploration strategy around them?"
You have Chandrayaan-2 radar + imagery data → find subsurface ice, select a landing site, plan a rover route, estimate ice volume.
**Workflow:** DFSAR + OHRC data → Detect Subsurface Ice → Select Landing Site → Design Rover Traverse → **Estimate Ice Volume (top 0–5 m)**.

Questions to answer: where exactly is subsurface ice; how to distinguish ice from rocky terrain; which sites are safe for landing; how a rover reaches the target efficiently; how much ice may exist.

## Why it's hard — key gap areas in polar ice detection (slide)
- Ambiguity in radar-based detection.
- Poor constraints on ice depth and volume.
- Incomplete understanding of micro-environments.
- Ice formation and delivery mechanisms.
- Surface vs subsurface discrimination.
- Spatial heterogeneity.

## Doubly shadowed craters (DPSRs) — the science focus (slides)
- A point is **doubly shadowed** if it is permanently shadowed AND has no direct line of sight to any non-permanently-shadowed surface. The crater rim shields the interior from scattered light + thermal emission off the periodically illuminated rim of the larger crater.
- DPSRs are among the **coldest places in the inner solar system, ~25 K** (minimum possible lunar surface temperature).
- Cause: Moon's N–S axis is nearly perpendicular to the ecliptic, so crater rims block sunlight from reaching crater floors.
- Largest DPSRs concentrate in/near **Faustini, Haworth, Shoemaker, Nobile, Sverdrup, de Gerlache, Slater, Bosch** craters (Table from O'Brien & Byrne, 2022; example shown within Faustini PSR). Reference evidence maps: Shearer et al. 2024; ice-bearing pixels from M3/LOLA/LAMP (Li et al. 2018); anomalous high-CPR craters (Spudis et al. 2013).

## The mentors' own published work (the template to beat)
- **Paper:** "Subsurface ice in doubly shadowed craters as revealed by Chandrayaan-2 dual frequency synthetic aperture radar," **npj Space Exploration, vol 2, article 22 (2026)**, open access, published **6 May 2026**. Authors: Rishitosh K. Sinha, Rajiv R. Bharti, Kinsuk Acharyya, Sanjay K. Mishra, Neeraj Srivastava, Anil Bhardwaj.
- Abstract specifics: full-polarimetric **L- and S-band DFSAR**; investigated **nine doubly shadowed craters** in Faustini, Haworth, Shoemaker; **four craters show CPR > 1**.
- Also covered on the ISRO website (27 May 2026) and Times of India ("PRL study sheds new light on Moon's icy secrets"). Read the paper — it defines the exact method, criteria, and craters they expect you to work with.

## Detection criteria (slide — important, these are the numbers)
- **Circular Polarization Ratio (CPR) > 1**, AND
- **Degree of Polarization (DOP) < 0.13**
→ indicates volumetric scattering potentially associated with subsurface ice (vs surface roughness). Also look for **lobate-rim morphology** (flow/lobed appearance suggesting the impact penetrated subsurface ice). Example: a ~1.1 km crater in Faustini.

## Expected solution / steps (slide)
1. Map permanently shadowed regions + identify **doubly shadowed craters** using illumination models + OHRC imagery.
2. Analyze **DFSAR** data → compute CPR and DOP; apply refined criteria (**CPR > 1, DOP < 0.13**) to flag potential subsurface-ice signatures.
3. Study crater morphology, slopes, boulder distribution, surface roughness using **OHRC** data.
4. Evaluate terrain safety + proximity to ice-bearing regions.
5. Design an **optimal and safe rover path** considering terrain hazards and **solar power constraints**.
6. Use **radar backscatter models + dielectric assumptions** to estimate ice concentration and volume within the **top 5 metres**.

> "Think like mission planners": move from orbital observations to an actionable strategy — where to land, drive, excavate, and how much ice is available.

## Expected outcomes (slide)
- Identification of high-probability subsurface-ice regions in doubly shadowed craters.
- A validated radar-based detection framework for subsurface ice.
- A feasible landing site near scientifically relevant targets.
- An optimized rover traverse path.
- Quantitative estimates of subsurface ice volume.

## Suggested tools (slide)
- GIS: **QGIS / ArcGIS**.
- Programming: Python (NumPy, SciPy, GDAL, rasterio).
- Image processing: **ENVI**.
- **DFSAR processing: MIDAS** (downloadable from the data portal).
- Terrain analysis: DEM tools.
- Path planning: optimization algorithms / AI-based navigation models.
- Visualization: QGIS / ArcGIS / MATLAB / Python plotting.

## Data & software source (slide)
**ISRO Science Data Archive (ISDA), Chandrayaan-2:** https://pradan.issdc.gov.in/ch2/ — use MapBrowse, select DFSAR / OHRC instrument, download data + MIDAS software. (Q&A: DFSAR = polarization signatures; OHRC is imagery not elevation, but a DTM can be derived from OHRC stereo pairs; high-res DTM supplied if required.)

## Official description (website) — authoritative additions
- Confirms the detection criteria **CPR > 1 and DOP < 0.13**, ice volume within the **top ~5 m of regolith** via **radar backscatter models + dielectric assumptions**.
- **You're handed the crater:** participants are supplied **Chandrayaan-2 DFSAR data of one doubly shadowed crater** in the south polar region (during the 30-hour finale) — your job is to characterize *that* crater's subsurface ice, then design a safe rover traverse to it considering terrain hazards + solar-power constraints.
- **Impact framing (good for proposal):** identifies in-situ resource utilization (ISRU) sites, informs landing-mission planning, advances planetary radar remote sensing.
- **Evaluation:** scientific robustness of ice detection, analysis accuracy/clarity, landing-site feasibility, rover-traverse efficiency/safety, methodology innovation, documentation clarity.

## Our take
Different skillset (planetary radar polarimetry + path planning), smallest field of strong competitors, highest novelty. The mentors handed you their own 2026 paper as the method — CPR > 1 and DOP < 0.13 in nine named craters — which lowers research risk but means judges will benchmark against their published result. Strongest only if a teammate is comfortable with SAR polarimetry; the CV/geospatial half (OHRC morphology, terrain safety, rover path) overlaps with our skills but the radar core does not.
