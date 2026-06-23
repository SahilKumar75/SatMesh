# PS4 — Official Description (verbatim from portal screenshots)

> Authoritative source for the deck. Transcribed from the official BAH-2026 PS4
> description page. Use this for exact wording / requirements when writing the PPT.

## Title
**Route Resilience: Occlusion-Robust Road Extraction & Graph-Theoretic Criticality
Analysis for Urban Mobility**

## Overview
Modern urban centres, particularly rapidly expanding Indian metropolises (e.g.,
Bengaluru), face a dual challenge in spatial modelling: **fragmentation and
stagnation**. This challenge sits squarely within the mandate of ISRO's **National
Natural Resources Management System (NNRMS)**, which seeks to maximise the
downstream utility of indigenous remote sensing EO satellites such as **Cartosat
and Resourcesat LISS-4**.

Standard satellite-based road extraction often fails due to **"spectral blindness"**
caused by tree canopies, building shadows, and cloud cover. These "broken" masks
are useless for real-world applications like disaster response or traffic
simulation because they lack topological connectivity. The need for robust,
automated road asset mapping has been specifically highlighted in recent National
Meets — by the **Ministry of Electronics and Information Technology (MeitY)** for
GIS-based urban planning and e-governance decision support, and by the **Ministry
of Consumer Affairs, Food and Public Distribution** for infrastructure mapping,
facility layout, and route verification.

This solution bridges that gap with an **end-to-end pipeline**: first, using
context-aware Deep Learning to "see through" occlusions, and second, transforming
those masks into a mathematically continuous, weighted graph to identify systemic
bottlenecks and simulate urban collapse scenarios. By transitioning from legacy
analytical methods to modern Deep Learning and graph-theoretic modelling, the
framework provides automated, occlusion-robust road asset mapping for urban
planning, while its predictive "what-if" simulations offer actionable decision
support for disaster response, structural resilience, and facility distribution
across dynamic Indian metropolises.

The proposed problem statement is well-suited for a **30-hour hackathon** through a
parallel team workflow: while one sub-team builds and trains the context-aware
segmentation model, the other can simultaneously develop the topological healing
and network ablation scripts using mock or open-source vector baselines. By
eliminating complex manual preprocessing bottlenecks, the team can focus entirely
on Deep Learning optimisation, graph healing, and the UI dashboard.

## Objective
- **Occlusion-Aware Extraction** — Develop a Transformer-based deep learning
  architecture to infer road continuity under heavy tree cover, vehicles, shadows,
  and urban clutter, **across varying illumination and seasonal conditions**.
- **Topological Reconstruction** — Convert fragmented pixel masks into a unified,
  routable weighted vector graph using graph-theoretic "healing" (MST, Disjoint Sets).
- **Structural Intelligence** — Quantify urban vulnerability by identifying
  "Gatekeeper Nodes"/bottlenecks through centrality metrics.
- **Simulated Stress Testing** — Build a framework to predict the systemic impact
  of localised infrastructure failure (e.g., flooding or accidents).

## Expected Outcomes
- **High-Fidelity Routable Topology** — A mathematically closed, connected vector
  network derived from high-resolution imagery, far surpassing standard pixel-based
  segmentation; a robust, generalizable model that suits different terrains
  (**urban, rural, forested**).
- **Quantitative Criticality Map (Bottleneck Identification)** — A spatial heatmap
  identifying high-betweenness intersections that act as single points of failure
  ("Gatekeeper Nodes").
- **Predictive Impact Assessment for Disaster Scenarios** — A simulation framework
  that quantifies the systemic "cost" of losing specific network nodes. By
  systematically disabling high-centrality nodes (e.g., simulating floods,
  accidents, or construction), the project will produce a **Resilience Index** — a
  tool for planners to disable nodes and instantly see rerouting effects and travel
  time increases.

## Dataset Required
**Primary imagery**
| Source | Resolution / notes |
|---|---|
| Sentinel-2 | 10 m spatial resolution — openly available |
| Resourcesat LISS-IV | 5.8 m spatial resolution — openly available |
| Cartosat-3 | High resolution — provided to participants during the 30-hour hackathon for challenge-specific experimentation and evaluation |

**Ground Truth & Open Datasets** (zero-manual-effort automation pipeline that pairs
open-source ground truth with multi-resolution satellite feeds):
- **SpaceNet Roads Dataset** — for model development and pre-training
- **DeepGlobe Road Extraction Dataset** — for model development and pre-training
- **OpenSatMap** — for model development and pre-training
- **OpenStreetMap (OSM) road vector layers** — ground-truth road masks generated
  automatically and used as reference annotations for training, validation, and
  performance assessment

## Recommended Stack
| Area | Tools |
|---|---|
| Libraries | Albumentations (augmentation), Rasterio, GDAL (geospatial), OpenCV, NumPy |
| Segmentation Model | U-Net with ResNet Backbone, UNet++, DeepLabV3+, PyTorch; Transformer-based models, Attention mechanisms (spatial + channel); Generative models (optional for reconstruction) |
| Skeletonization | Scikit-Image / FilFinder / OSMnx |
| Graph Logic | NetworkX; PyTorch Geometric (PyG) for advanced GNN approach |
| Centrality Analysis | Betweenness Centrality (NetworkX) |
| Visualization | QGIS / Matplotlib / Streamlit / Leaflet.js |

## Compute Requirements
Graph-theoretic post-processing and UI execution are lightweight and run on
standard CPU architecture. Training state-of-the-art Deep Learning models within
the 30-hour limit will require access to high-performance GPU instances, which can
be sourced via local workstations.

## Expected Solution / Steps

**Phase I: Occlusion-Robust Segmentation (The Foundation)**
- *Data Preprocessing* — Tile images, normalize/enhance contrast, simulate
  occlusions, and balance dataset with occluded roads.
- *Baseline Model Development* — Train a U-Net/DeepLabV3+ model, evaluate on occluded
  regions, and identify failure cases.
- *Advanced Model Design* — Implement context-aware architectures (Transformer,
  attention), focusing on long-range dependencies.
- *Loss Function Engineering* — Use combined Dice, IoU, and boundary-aware losses,
  with optional connectivity loss.
- *Occlusion Handling Strategy* — Use context-based inference and multi-scale
  feature fusion, with optional inpainting.

**Phase II: Graph Skeletonization & Healing**
- *Thinning* — Apply morphological skeletonization to reduce binary masks into
  1-pixel-wide centerlines. Nodes are generated at intersections and line endpoints,
  while road segments are represented as edges.
- *Topological Healing* — Use a Minimum Spanning Tree (MST) and Disjoint Set
  algorithm to bridge gaps caused by extreme occlusions. The algorithm evaluates
  logical gaps based on **Euclidean distance and angular alignment** to ensure the
  "healed" road follows a natural trajectory.

**Phase III: Network Analysis & Stress Testing**
- *Centrality Calculation* — Apply Betweenness Centrality to identify nodes that lie
  on the shortest paths across the city. A high centrality score indicates a critical
  bottleneck.
- *Node Ablation Simulation* — Perform "Network Stress Tests" to quantify
  vulnerability by systematically removing highest-betweenness nodes (e.g., severe
  flooding or structural failure).
- *Resilience Index Calculation* — Recalculate global network efficiency after each
  removal. **Resilience Index = ratio of average shortest-path length in the baseline
  network to that in the perturbed network. Lower R = more vulnerable.**

**Phase IV (Advanced): Interactive Dashboard** (verbatim)
The final stage is a web-based visualisation tool (using Streamlit and Leaflet.js)
to make the graph data actionable for non-technical planners:
- *Heatmap Overlay* — A dynamic map layer that colors road segments based on their
  **"Criticality Worth"**, allowing planners to see the city's "weakest links" at a glance.
- *Simulation Toggle* — An interactive feature where a user can manually click a node
  to "disable" it. The dashboard instantly updates to show the rerouted paths and the
  estimated increase in travel time across the affected sector.

> Official term to use in the deck: **"Criticality Worth"** for the per-road criticality score.

## Evaluation Parameters — Core Technical Metrics (verbatim, OFFICIAL)
| Metric | Description |
|---|---|
| **IoU & Dice Score** | Segmentation accuracy with specific focus on **Occlusion-Recall** (recovery of roads under shadows). |
| **Generalisation** | Success rate across diverse terrains — dense urban, forested suburban, and rural landscapes. |
| **Connectivity Ratio** | Percentage increase in the largest connected component after the MST healing phase. |
| **Topological Accuracy** | Comparison of the final graph against OpenStreetMap (OSM) benchmarks using Average Path Length error. Run shortest-path between random point pairs on ground-truth OSM vs model graph and calculate error. |
| **Length-Complete / Relaxed IoU** | Introduces a tolerance buffer (3–5 pixels). If the predicted road pixel falls within the buffer zone of the ground-truth road, it counts as a true positive. Prevents penalising minor alignment shifts. |

- Overall weighting (from video/Q&A): **50% road extraction / 50% graph-theoretic resilience.**
- Mentor guidance: **lead with innovation (judges prefer innovative over scalable)**;
  the graph half is where most teams are weak.

## Official PS4 banner visual (for deck styling reference)
The official PS4 hero image — useful to mirror the visual language judges already associate with PS4:
- Tagline strip: **"INNOVATE · IMAGINE · INSPIRE"**; closing line **"FROM SPACE INSIGHTS TO STRONGER CITIES."**
- 3-panel pipeline strip (top-right): **Satellite Image → Occlusion-Robust Road Extraction → Road Graph & Criticality Analysis**, with a **criticality colorbar High (red) → Low (green)**.
- Big-city aerial with roads colored green→amber→red by criticality; red ⚠ markers on the most critical intersections; transit/hospital icons.
- "Build solutions that enable": resilient routing under occlusions/disruptions; identification of critical road links + vulnerable zones; data-driven decisions for efficient, sustainable urban mobility.
- 5 pillars (bottom): **Space Data** (satellite imagery & open datasets) · **AI/ML** (deep learning for robust extraction) · **Graph Theory** (network modeling & criticality) · **Urban Impact** (resilient, efficient, inclusive mobility) · rocket → "stronger cities".
- *Deck tip:* reuse the green→red criticality colorbar and the 3-panel pipeline motif so our deck visually "speaks PS4."

## Requirements we may NOT have addressed yet (gap check)
- **Seasonal robustness** — the spec explicitly says "across varying illumination
  and SEASONAL conditions." Multi-temporal handling is named, rarely done.
- **Forested terrain** — explicitly listed; heaviest occlusion case.
- **Generative reconstruction / inpainting** — named as optional; an innovation lever.
- **Disaster realism** — floods/accidents named; needs real hazard grounding
  (where floods/earthquakes actually originate), not arbitrary node removal.
