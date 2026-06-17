# PS2 — Generative AI-Based Cloud Removal and Reconstruction for LISS-IV Satellite Imagery

**Org:** NRSC / NESC (ISRO)
**Mentors:** Dr. Avinash Chouhan, Rosly Lyngdoh
**Slide tag:** BAH_2026_PS_02
**Explainer:** Video 1, 17:36–25:35

## Title-slide thumbnail (sample imagery)
Top-left of the PS2 title slide showed **three side-by-side satellite tiles** illustrating the task on LISS-IV-style data:
- Left tile: scene with visible **cloud cover** (white/hazy patches over fields).
- Middle tile: a **clearer** optical view (urban + agricultural parcels).
- Right tile: a **vegetation/green-tinted** false-color view of field parcels.
- Takeaway: visual of cloudy → cloud-free → analysis-ready reconstruction across mixed agricultural/urban terrain. Decorative; no readable specs.

## What "cloud removal" is (Introduction slide)
- An **image-to-image translation** task (cloudy → cloud-free).
- **Dense relation mapping** (all pixels relate).
- Fundamentally **image synthesis** (generating new pixels).
- Two axes of categorization:
  - **Temporal:** single-frame vs multi-frame.
  - **Modality:** single-sensor vs multi-modal.
- Reference shown: Li et al. 2024 (visualization of cloud removal).

## Need
- Persistent cloud cover over much of India limits utility of optical sensors.
- Image synthesis for **gap filling** of cloud-occluded regions.
- Core question: can recent **generative-AI image-synthesis models** be used for automatic cloud removal on LISS-IV imagery?

## Objectives (slide)
- Develop a **Generative AI-based framework for automated cloud removal** in LISS-IV imagery.
- **Reconstruct cloud-covered regions** while preserving **spatial structures and spectral characteristics**.
- Generate **visually consistent and analysis-ready** cloud-free imagery.
- Evaluate reconstructed outputs using **quantitative and qualitative** assessment.
- Develop a **scalable workflow** for operational cloud-removal applications.
- (Teams validate internally; external validation done by ISRO.)

## Expected outcomes (slide)
- Automated cloud-free reconstruction of LISS-IV imagery.
- Improved usability of optical satellite data under persistent cloud cover.
- Enhanced spatial and spectral consistency in reconstructed outputs.
- Analysis-ready satellite products for downstream geospatial applications.
- A prototype framework for operational deployment.
- Comparative assessment of different Generative AI architectures for cloud reconstruction.

## Datasets (slide)
- **Primary:** LISS-IV satellite imagery — cloudy and cloud-free scenes — from **Bhoonidhi**.
- **Auxiliary (optional, public):** Sentinel-1 SAR, Sentinel-2 optical, temporal reference imagery, DEM data, any other datasets.
- Output must be generated **for LISS-IV**; auxiliary data may be used as additional conditioning.

## Suggested tools / technologies (slide)
- **Frameworks:** Python; PyTorch / TensorFlow.
- **Geospatial:** GDAL, Rasterio, QGIS, Google Earth Engine (optional).
- **Supporting libs:** OpenCV, NumPy, Scikit-image, Albumentations.

## Steps (slide; bold = required, rest optional)
1. **Collection and preprocessing of cloudy and cloud-free LISS-IV imagery.**
2. Preparation of cloud masks and co-registration of auxiliary datasets (optional).
3. Identification/reuse of suitable pre-trained DL or Generative AI models for transfer learning (optional).
4. Fine-tuning pre-trained models on LISS-IV for cloud reconstruction (optional).
5. Integration of temporal and/or multi-sensor information for improved quality (optional).
6. **Training, optimization, and validation of the developed deep learning model.**
7. **Generation of analysis-ready, cloud-free products.**
8. **Documentation and deployment of the developed workflow.**

Teams choose the learning paradigm: fully-supervised / semi-supervised / fine-tuned / unsupervised — and curate a dataset accordingly (small or large depending on approach).

## Evaluation (slide + talk)
- At testing, ISRO provides ~**20–25 cloudy images**; teams produce cloud-free outputs.
- **Visual consistency** of reconstructed regions (does output represent the ground truth).
- **Preservation of spatial textures and edges** / image features.
- Reference and **non-reference image quality assessment** metrics.
- Expert visual assessment.

## Transcript-only nuances (verification pass)
- Motivation framing: over the NE and "most parts of India" **persistent cloud cover** hinders/limits the utility of the optical sensor at those locations — the regional driver behind the PS.
- Output must carry **physical meaning**, not just look plausible: the mentor stressed spatial consistency + spectral consistency + "physical meaning" of reconstructed pixels (so a pretty but physically wrong fill fails).
- Teams **curate their own dataset** (small or large) depending on the chosen paradigm (supervised / semi-supervised / fine-tuned / unsupervised) — ISRO does not hand you a ready training set; only the ~20–25 image test set at evaluation.

## Q&A note (1:32)
- Both **generative** and **discriminative** AI are permitted for cloud removal.

## Official description (website) — authoritative additions
- **Region focus:** persistent cloud over **tropical/mountainous regions, esp. the North Eastern Region (NER) of India**; clouds + cloud shadows cripple LULC mapping, disaster monitoring, environmental + infrastructure analysis.
- **Approaches explicitly suggested:** diffusion models, GANs, transformer-based architectures, or **multi-modal fusion** using auxiliary Sentinel-1 SAR, Sentinel-2 optical, or temporal reference observations.
- Confirms: must leverage spatial + spectral + temporal information; preserve fine-scale detail and spectral consistency. (No new datasets beyond what's already listed.)

## Our take
Best-fit statement for our team. CV/generative is our core strength; LISS-IV from Bhoonidhi is ISRO-specific so there's no off-the-shelf solution to copy. **Critical de-risk: confirm we can actually download paired cloudy/cloud-free LISS-IV scenes from Bhoonidhi before committing.** Paired data is the whole game; SAR-to-optical (Sentinel-1 → LISS-IV) is a fallback if pairs are scarce.
