# BAH 2026 — Idea Submission Draft
## Problem Statement 4: Route Resilience — Occlusion-Robust Road Extraction & Graph-Theoretic Criticality Analysis for Urban Mobility

> Draft content to paste into the official Hack2skill PPT/idea template. Fill the [bracketed] bits. Default pilot city: **Bengaluru**.

---

### Team
- **Team name:** [____]
- **Members (3–4):** [Name — Institution — role], [Name — Institution], [Name — Institution], [Name — Institution]
- **Suggested role split (mentors recommend two parallel sub-teams):**
  - Sub-team A — Computer Vision (road extraction model)
  - Sub-team B — Graph analysis (healing, criticality, dashboard)

---

### 1. Problem we are solving
Indian cities can't build a reliable digital road network from satellite imagery because **tree canopies, building shadows, and cloud cover hide road pixels** ("spectral blindness"). Standard segmentation produces *broken, disconnected* road masks that are useless for routing, disaster response, or traffic simulation. We propose an end-to-end system that (a) extracts roads *through* these occlusions, and (b) turns the result into a connected network that reveals the city's critical failure points.

Aligned with ISRO's **NNRMS** mandate to maximise the utility of indigenous EO satellites (Cartosat, Resourcesat LISS-IV), and with **MeitY** (GIS urban planning) and **Ministry of Consumer Affairs** (infrastructure/route verification) priorities.

### 2. Our idea (the brief)
A two-stage pipeline plus a decision-support dashboard:
1. **Occlusion-robust road extraction** — a connectivity-aware deep-learning model that "sees through" trees and shadows to recover topologically connected roads.
2. **Graph-theoretic resilience analysis** — convert the road map into a routable graph, identify "gatekeeper" intersections whose failure paralyses the city, and simulate disaster scenarios.
3. **Interactive dashboard** — a planner clicks an intersection to disable it (flood/accident) and instantly sees the city reroute, with travel-time impact.

**The differentiator:** most teams will do the road-tracing; few will do the graph half well, and it is **50% of the score**. Our novelty is the connectivity-preserving CV + the quantitative Resilience Index, not just a segmentation map.

### 3. Technical approach
**Stage A — Occlusion-robust extraction (CV):**
- Baseline: **U-Net + ResNet34 encoder**, pre-trained on **DeepGlobe / SpaceNet** (no manual labeling).
- Key innovation: train with **CP-clDice (connectivity-preserving centerline Dice) loss**, which penalises broken roads by comparing masks *and their skeletons* — directly optimising road continuity under occlusion.
- Occlusion-aware training: synthetic shadow/canopy augmentation so the model learns to bridge gaps.
- Advanced direction: attention-based topology reasoning (à la **URoadNet**'s connectivity + integrality attention) to recover roads through occluded regions.

**Stage B — Topological reconstruction (graph healing):**
- Skeletonise the predicted mask (Scikit-Image / FilFinder) → nodes at intersections/endpoints, segments as edges.
- Heal occlusion-induced gaps with **MST + Disjoint-Set**, bridging stubs by **Euclidean distance + angular alignment** (vector dot product ≈ −1 ⇒ segments face each other ⇒ connect).

**Stage C — Criticality & stress testing:**
- **Betweenness centrality** (NetworkX) → "gatekeeper nodes" / single points of failure.
- **Resilience Index** = avg shortest-path length (baseline) ÷ (after disabling critical nodes); lower ⇒ more vulnerable.
- **Streamlit + Leaflet.js** dashboard: criticality heatmap + click-to-disable node simulation with live rerouting + travel-time increase.

### 4. Novelty / USP
- **Connectivity-first CV:** CP-clDice optimises the exact thing judges measure (occlusion-recall / topological accuracy), not just pixel overlap.
- **Actionable resilience, not just maps:** a quantitative Resilience Index + what-if disaster simulation for planners.
- **Decision-maker UI:** non-technical planners interact directly — a memorable, demo-ready output.

### 5. Technology stack
Python; PyTorch + `segmentation-models-pytorch`; Albumentations, Rasterio, GDAL, OpenCV; Scikit-Image / FilFinder / OSMnx; NetworkX (+ PyTorch Geometric optional); Streamlit + Leaflet.js; QGIS/Matplotlib for figures.

### 6. Feasibility for the 30-hour finale
- **Parallel sub-teams** (CV + graph) work simultaneously; the graph track develops on OSM/mock baselines while the model trains.
- **Zero-manual-annotation data** (DeepGlobe/SpaceNet + OSM ground truth) removes preprocessing bottlenecks.
- **Compute:** graph + UI run on CPU; model training uses our own high-performance GPU workstation.
- **Time budget:** H0–6 baseline U-Net; H6–14 clDice + occlusion aug (graph track in parallel); H14–22 integrate mask→graph + Resilience Index; H22–30 dashboard + demo polish.

### 7. Datasets (all ISRO-listed)
Sentinel-2 (10 m), Resourcesat LISS-IV (5.8 m), Cartosat-3 (provided at finale); ground truth from SpaceNet, DeepGlobe, OpenSatMap, OpenStreetMap road vectors.

### 8. Expected outcomes / deliverables
- High-fidelity, connected, routable road graph from occluded imagery.
- Quantitative criticality map ("gatekeeper nodes").
- Predictive impact assessment + Resilience Index for disaster scenarios.
- Interactive planner dashboard.

### 9. Impact
Enables disaster-response routing, resilient urban planning, and infrastructure verification for rapidly growing Indian metros — turning ISRO satellite data into actionable city-resilience intelligence (pilot: Bengaluru; scalable to any city).

---

#### Notes for filling the template
- Lead with **innovation** (judges prefer innovative over merely scalable).
- Explicitly address **both halves** (the 50/50 scoring).
- Keep scope to **one pilot city** — don't overpromise.
- Use the **mandatory PPT template** from the dashboard; this text maps to its idea-brief / tech-stack / approach fields.
- If you run the two starter scripts, drop the **road-prediction image** and the **Bengaluru graph + Resilience Index** in as a mini proof-of-concept — most submissions are idea-only.
