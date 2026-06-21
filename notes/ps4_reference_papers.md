# PS4 Reference Papers

Papers relevant to Route Resilience (PS4) — road extraction, graph topology, satellite imagery.

## Road Graph Extraction

### DeH4R — Decoupled Hybrid Road Network Graph Extraction
- **arxiv:** https://arxiv.org/abs/2508.13669
- **Published:** Aug 2025 (most recent SOTA)
- **Relevance:** Hybrid graph-generate + graph-grow approach. Beats SAM-Road++ on topology fidelity and spatial consistency. Evaluated on CityScale, SpaceNet, RNGDet++.
- **Why it matters:** Could replace our skeleton→heal→graph pipeline with a learned extractor. No public code yet.

### SAM-Road++ — SAM for Road Graph Extraction (v2)
- **arxiv:** https://arxiv.org/abs/2411.16733
- **Published:** Nov 2024
- **Relevance:** Fine-tunes SAM ViT encoder for road graph extraction. Adds node-guided resampling + extended-line strategy to handle occlusions. ~0.75+ IoU on DeepGlobe.
- **Why it matters:** Our deferred upgrade path (needs A100, 307M params). See `notes/sam_road_plus_plus.md`.

### SAM-Road — SAM + GNN for Road Graph (v1)
- **arxiv:** https://arxiv.org/abs/2403.16051
- **Published:** Mar 2024
- **Relevance:** Fine-tuned SAM image encoder + transformer-based GNN predicts graph vertices and edge probabilities directly — no skeletonization step. City-scale dataset.
- **Why it matters:** Simpler than SAM-Road++, lighter implementation if A100 unavailable.

## Datasets

### OpenSatMap — Fine-grained High-Resolution Satellite Dataset
- **arxiv:** https://arxiv.org/abs/2410.23278
- **Published:** Oct 2024
- **Relevance:** Instance-level road annotations from high-res satellite imagery. Designed for large-scale map construction and autonomous driving tasks.
- **Why it matters:** PS4 mentions generalisation across terrains — OpenSatMap annotations could supplement DeepGlobe for India-like diversity.

## Currently Implemented

| Component | Status | File |
|---|---|---|
| SegFormer MiT-B4 segmentation | ✅ training | `src/model/segformer.py` |
| Skeleton Recall Loss | ✅ | `src/model/loss.py` |
| Skeleton → graph | ✅ | `src/graph/skeleton.py` |
| MST gap healing | ✅ | `src/graph/heal.py` |
| Betweenness / criticality | ✅ | `src/graph/criticality.py` |
| APLS vs OSM | ✅ | `src/graph/apls.py` |
| Streamlit + Folium dashboard | ✅ | `app/dashboard.py` |
| SAM-Road++ | ⏳ deferred | `notes/sam_road_plus_plus.md` |
| DeH4R | ⏳ no code yet | — |
