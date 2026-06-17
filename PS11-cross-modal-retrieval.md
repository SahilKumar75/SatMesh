# PS11 — Cross-Modal Satellite Image Retrieval Using Multi-Sensor Remote Sensing Data

**Mentors:** Aminur Hossain, Sanjay K. Singh
**Explainer:** Video 2, 55:20–59:41 (presented last — mic issues during the live talk)
**Slides:** Captured (a 4-slide "Problem Statement Summary" deck).

## Objective (slide)
Retrieve **semantically similar regions across optical, SAR, and multispectral imagery**. (Example shown: a query image → top-ranked retrieved neighbors, with SAR tiles on top row and optical tiles on bottom.)

## Why cross-modal retrieval is needed (slide)
Different sensors observe the same Earth surface through different physical signatures.
1. **Multi-sensor archives** — optical, multispectral, SAR, and **elevation (DEM)** data capture different physical cues.
2. **Search gap** — metadata alone may miss similar regions across seasons, acquisition conditions, or sensors.
3. **Common embedding space** — learn descriptors where similar land-cover / scene content stays close **across modalities**.

## Retrieval modes to support (slide)
- **Same-modal:** optical→optical, SAR→SAR, multispectral→multispectral.
- **Cross-modal:** optical↔SAR, optical↔multispectral.
- **Core requirement:** rank **top-5 and top-10** relevant images with **low average query time**.

## Solution pipeline (slide — "Multi-Sensor Satellite Image Retrieval Evaluation Framework")
**Query image** (optical / SAR / multispectral) → **embedding model** (shared feature representation) → branches into **same-modal retrieval** (top-5/top-10) and **cross-modal retrieval** (top-5/top-10) → **evaluation metrics** (F1-score@5, F1-score@10, retrieval time/query).

**Key steps:** prepare paired/associated data → preprocess each modality → extract embeddings → compute similarity → return top-5/top-10.

## Expected outcome & evaluation (slide)
- **Outputs:** a ranked list for each query — top-5 and top-10 results.
- **Metrics:** **F1-score@5 / @10** for both same-modal and cross-modal retrieval.
- **Efficiency:** average **retrieval time per query** (lower is preferred).

## Official description (website) — authoritative additions
- **Modalities include hyperspectral** too (optical, multispectral, hyperspectral, SAR, elevation).
- **Approaches named:** CNNs, Vision Transformers, **Siamese / triplet networks**, metric learning, contrastive learning, self-supervised learning, multi-modal representation learning, **foundation-model feature extraction (pretrained models allowed)**, and **FAISS** for efficient vector search.
- **Dataset:** two or more aligned / semantically-associated modalities (optical RGB, multispectral, SAR, optional land-cover/land-use labels); each sample = same or nearby geo-location across sensors. Relevance judged by semantic class / geographic correspondence / predefined labels.
- **Cross-modal retrieval is weighted more heavily** (harder than same-modal).
- **Evaluation:** F1@5 and F1@10 for **both** same-modal and cross-modal, plus average retrieval time per query (lower preferred).

## Our take
Strong fit for our DL skills — this is representation / metric learning (a CLIP-style shared encoder across modalities, contrastive/triplet losses), not image generation. The deck hands you the exact framework (shared embedding → top-k retrieval → F1@5/@10 + query-time scoring). The one real risk is **paired multi-modal data** (optical–SAR–multispectral covering the same scene): the slide says "prepare paired/associated data" but names no dataset, so confirm what's provided in the official proposal before committing. Thinner competition than the segmentation statements. Note: weakest live explanation (mic failed), so lean on this deck + the proposal, not the audio.
