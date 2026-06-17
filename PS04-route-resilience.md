# PS4 — Route Resilience: Occlusion-Robust Road Extraction & Graph-Theoretic Criticality Analysis for Urban Mobility

**Mentors:** Pruthivi Raj Behera, G. Uday Kumar, Preet Mhaski, Mayukh Mukherjee
**Explainer:** Video 1, 37:29–44:34
**Slides:** Captured (the richest, most polished deck of PS1–8).

## One-liner
Leverage space-based insights + **AI + Graph Theory** to build resilient urban road networks.
Pipeline shown: **Satellite Image → Occlusion-Robust Road Extraction → Road Graph & Criticality Analysis** (criticality colorbar high→low).

Build solutions that enable:
- Resilient routing in the face of occlusions and disruptions.
- Identification of critical road links and vulnerable zones.
- Data-driven decisions for efficient, sustainable urban mobility.

## Overview — the dual challenge
- **Fragmentation:** tree canopies, building shadows, cloud cover cause "spectral blindness," producing broken road masks that lack topological connectivity — useless for disaster response or traffic simulation.
- **Stagnation:** legacy analytical methods can't keep pace with rapidly expanding Indian metropolises like **Bengaluru**, limiting actionable insight for planners.
- **Aligned with ISRO's NNRMS mandate:** maximises downstream utility of indigenous EO satellites — **Cartosat & Resourcesat LISS-IV** — supporting **MeitY** (GIS urban planning, e-governance) and **Ministry of Consumer Affairs** (infrastructure mapping, route verification).
- **The bridge (end-to-end pipeline):**
  1. **Context-Aware Deep Learning** — "see through" occlusions to recover continuous road masks under canopy, shadow, cloud.
  2. **Graph-Theoretic Modelling** — transform masks into a continuous weighted graph to identify bottlenecks and simulate urban collapse scenarios.
  - Output: automated occlusion-robust road mapping + predictive what-if simulations for disaster response & resilience planning.

## Four core objectives (slide)
1. **Occlusion-Aware Extraction** — Transformer-based architecture inferring road continuity under tree cover, vehicles, shadows, urban clutter; robust across illumination and seasonal conditions.
2. **Topological Reconstruction** — convert fragmented pixel masks into a unified, routable weighted vector graph using graph-theoretic **"healing" (MST, Disjoint Sets)**.
   - (In the talk the mentor also described using **vector dot products** between edges to decide connections, e.g. dot ≈ -1 → segments point at each other → connect. MST + Disjoint Sets is the slide's named method.)
3. **Structural Intelligence** — quantify urban vulnerability by identifying **"Gatekeeper Nodes" / bottlenecks** through centrality metrics.
4. **Simulated Stress Testing** — framework to predict the systemic impact of localised infrastructure failure (e.g. flooding or accidents).

## Expected outcomes (slide)
- **High-Fidelity Routable Topology** — a mathematically closed, connected vector network from high-resolution imagery; robust, generalisable model suited to urban, rural, and forested terrains.
- **Quantitative Criticality Map** — a spatial heatmap identifying high-betweenness intersections that act as single points of failure (the city's "Gatekeeper Nodes").
- **Predictive Impact Assessment** — a simulation framework producing a **Resilience Index**; planners disable nodes and instantly see rerouting effects and travel-time increases for disaster scenarios.

## Datasets required (slide)
**Primary imagery:**
| Source | Resolution / notes |
|---|---|
| Sentinel-2 | 10 m — openly available |
| Resourcesat **LISS-IV** | **5.8 m** — openly available |
| **Cartosat-3** | High resolution — **provided during the 30-hour hackathon** for challenge-specific experimentation |

**Ground truth & open datasets** (zero-manual-effort — no manual annotation bottleneck):
- **SpaceNet Roads Dataset** — model development & pre-training.
- **DeepGlobe Road Extraction Dataset** — model development & pre-training.
- **OpenSatMap** — model development & pre-training.
- **OpenStreetMap (OSM) road vectors** — auto-generated ground-truth masks for training, validation & inference assessment.

## Suggested tools & technologies (slide)
- **Libraries:** Albumentations, Rasterio, GDAL, OpenCV, NumPy.
- **Segmentation models:** U-Net (ResNet backbone), UNet++, DeepLabV3+, PyTorch; Transformer & attention-based models; generative models for reconstruction.
- **Skeletonization:** Scikit-Image, **FilFinder**, **OSMnx**.
- **Graph logic:** NetworkX; PyTorch Geometric (PyG) for advanced GNN approaches.
- **Centrality analysis:** Betweenness Centrality (NetworkX).
- **Visualization:** QGIS, Matplotlib, Streamlit, Leaflet.js.
- **Compute:** graph post-processing & UI run on standard CPU; training SOTA DL models within the 30-hour limit needs high-performance **GPU instances, sourced via local workstations** (i.e. bring your own GPU).

## Evaluation parameters (slide, page 10)
- **IoU & Dice Score** — segmentation accuracy with specific focus on **Occlusion-Recall** (recovery of roads under shadows).
- **Generalisation** — success rate across diverse terrains: dense urban, forested suburban, rural.
- **Connectivity Ratio** — % increase in the largest connected component after the **MST healing phase**.
- **Topological Accuracy** — compare final graph vs OSM benchmarks via **Average Path Length error** (shortest-path between random point pairs, ground truth vs model graph).
- **Length-Complete / Relaxed IoU** — a **3–5 pixel tolerance buffer**: predicted road pixels within the buffer of ground truth count as true positives, avoiding penalties for minor alignment shifts.
- (Q&A 1:31) Overall weighting: **50% road extraction / 50% graph-theoretic resilience analysis.**

## Official description (website) — authoritative additions
- **Resilience Index (defined):** ratio of average shortest-path length in the **baseline** network to that in the **perturbed** network (after removing high-centrality nodes). **Lower R = more vulnerable.** Recompute global efficiency after each node removal.
- **30-hour parallel-team workflow (their suggestion):** one sub-team builds/trains the context-aware segmentation model; the other simultaneously builds the topological-healing + network-ablation scripts on mock / open-source (OSM) vector baselines. Zero-manual-annotation pipeline removes preprocessing bottleneck.
- **Phased solution:** (I) occlusion-robust segmentation — tile, normalize, simulate occlusions; baseline U-Net/DeepLabV3+ → advanced Transformer/attention; **loss = Dice + IoU + boundary-aware (+ optional connectivity loss)**. (II) skeletonization (morphological thinning → nodes at intersections/endpoints, segments as edges) → MST + Disjoint-Set healing using Euclidean distance + angular alignment. (III) betweenness centrality → node-ablation stress tests → Resilience Index. (IV) Streamlit + Leaflet.js dashboard with criticality heatmap + click-to-disable node simulation showing rerouting + travel-time increase.

## Our take
Strongest differentiator pick for our skills. The deck is unusually specific — they've basically handed the architecture (transformer segmentation → MST/Disjoint-Set graph healing → betweenness centrality → Streamlit stress-test dashboard), named the exact datasets, and split scoring 50/50. The graph half is where most CV teams have nothing and it's half the marks. Note the compute reality: you must supply your own GPU for the 30-hour finale.
