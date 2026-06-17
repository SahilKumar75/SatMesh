# PS4 — Technical approach (research findings → build plan)

Source: NotebookLM synthesis over road-extraction papers (URoadNet, SC-RoadDeepNet, D3FNet, shadow-detection, Vision Transformers, etc.) + my pragmatic adjustments for a 30-hour build. This is the backbone of the proposal's "approach" section.

## Track A — Occlusion-robust road extraction (CV, 50% of score)
**Plan: ship reliable, cite ambitious.**
1. **Baseline (build first):** U-Net + ResNet34 encoder via `segmentation-models-pytorch`. Pretrain on **DeepGlobe / SpaceNet** (no manual labeling).
2. **The key upgrade — connectivity loss:** train with **CP_clDice (connectivity-preserving centerline Dice)** instead of plain Dice/BCE. It intersects the mask *and its skeleton*, so it directly penalizes broken roads under shadows — i.e. it optimizes the "occlusion-recall" the judges measure. Highest value-to-effort change. (Public `clDice` PyTorch implementations exist; drop it in.)
3. **Occlusion training trick:** paint synthetic tree/shadow patches over training images (Albumentations) so the model learns to bridge gaps.
4. **Advanced direction (cite, don't over-promise):** **URoadNet (Dual Sparse Attentive U-Net)** — uses *Connectivity Attention* (fine intra-road detail) + *Integrality Attention* (global topology to reason through occlusions), with linear-complexity sparse attention (efficient). Describe it as the architecture direction; only attempt a full build if a clean public implementation exists. Otherwise an attention-augmented U-Net + clDice gets ~80% of the benefit at 20% of the risk.
   - **Risk note:** do NOT plan to reimplement a SOTA paper from scratch in 30h. A working U-Net+clDice demo beats a half-finished URoadNet.

## Track B — Topological reconstruction & graph healing
1. **Skeletonize** the predicted binary mask (Scikit-Image / FilFinder) → 1-px centerlines → nodes at intersections/endpoints, segments as edges.
2. **Heal gaps** (occlusions fragment the skeleton) with **MST + Disjoint-Set (Union-Find)**.
3. **Connection logic:** bridge broken segments using **Euclidean distance + angular alignment** — compute vector dot products between edge directions; ≈ -1 means two stubs point at each other → safe to connect.

## Track B (cont.) — Structural intelligence & stress testing
1. **Gatekeeper nodes:** `NetworkX` **betweenness centrality** → high-traffic intersections = single points of failure.
2. **Resilience Index:** systematically disable top nodes (simulate flood/accident), recompute global efficiency. **Index = avg shortest-path length (baseline) ÷ (perturbed)**; lower = more vulnerable.
3. **Dashboard (presentation points):** Streamlit + Leaflet.js criticality heatmap; judge clicks a node to disable it and sees rerouting + travel-time increase live.

## Finale time-budget (rough)
- H0–6: baseline U-Net training on DeepGlobe + data loaders.
- H6–14: add clDice loss + occlusion augmentation; (parallel team) skeletonize→graph→betweenness on OSM mock baseline.
- H14–22: integrate predicted mask → graph; node-ablation + Resilience Index.
- H22–30: Streamlit/Leaflet dashboard, polish, slides, demo rehearsal.

## Sources (from NotebookLM's gathered set — cite these in the proposal)
- URoadNet: Dual Sparse Attentive U-Net for multiscale road extraction
- SC-RoadDeepNet: shape & connectivity (origin of CP_clDice idea)
- D3FNet: Differential Attention Fusion Network for road extraction
- "Building Shadow detection using Aerial Imagery"
- "Intriguing Properties of Vision Transformers" (occlusion robustness of ViTs)
- Road Topology Extraction from Satellite images
- DeepGlobe / SpaceNet (training data)
