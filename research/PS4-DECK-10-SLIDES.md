# PS4 — 10-Slide Idea Deck (content map)

Maps our proposal onto the official Hack2skill template. Default city: Bengaluru.
Visual slides (4,5,6,7) have a described diagram — I can generate these as images for the deck.

---

## Slide 1 — Title / Intro
- **Bharatiya Antariksh Hackathon 2026 — ISRO**
- **Problem Statement 4: Route Resilience** — Occlusion-Robust Road Extraction & Graph-Theoretic Criticality Analysis for Urban Mobility
- Team: **[team name]** · Members: [names + institutions]
- (Background visual: a city road network with a few intersections glowing red = critical.)

## Slide 2 — Brief about the idea
Indian cities can't build reliable road maps from satellite images because trees, shadows, and clouds hide the roads, leaving broken, unusable maps. **Our solution does two things competitors don't combine:** it extracts roads *through* the obstructions while keeping them connected, then turns the map into a network that pinpoints the intersections whose failure would cripple the city, with an interactive disaster-simulation dashboard.

## Slide 3 — Opportunity: how we're different
Most road-extraction solutions stop at a **pixel mask** — and that mask breaks wherever a tree or shadow hides the road. They're judged on "looks like a road." We go two steps further:
| Typical solution | Our solution |
|---|---|
| Pixel segmentation only | **Connectivity-preserving** extraction (clDice) that survives occlusion |
| Output = a broken image | Output = a **connected, routable graph** |
| No risk insight | **Resilience Index** + gatekeeper-node detection (the 50%-of-score half most teams skip) |
| Static map | **Interactive what-if** disaster dashboard |
> Our edge is the *graph-theoretic resilience layer* + connectivity-first CV — not just another segmentation model.

## Slide 4 — Features offered (with visual)
- 🛰️ Occlusion-robust road extraction (sees through trees, shadows, clouds)
- 🔗 Connectivity-preserving loss (clDice) — no broken roads
- 🧩 Automatic graph "healing" of gaps (MST + Disjoint-Set)
- 🚦 Gatekeeper-node detection (critical intersections)
- 🌊 Disaster stress-test + quantitative **Resilience Index**
- 🖱️ Interactive planner dashboard (click to disable a node → live rerouting)
- 🗺️ Generalises across urban / rural / forested terrain
- 🇮🇳 Uses indigenous ISRO satellites (Cartosat, LISS-IV)
- *(Visual: 3-panel strip — cloudy satellite image → clean extracted roads → graph with red/green criticality nodes.)*

## Slide 5 — Process flow diagram
`Satellite image` → `Road segmentation (U-Net + clDice)` → `Binary road mask` → `Skeletonize` → `Graph healing (MST/Disjoint-Set)` → `Connected road graph` → `Betweenness centrality` → `Node-ablation stress test` → `Resilience Index` → `Interactive dashboard`
*(Left-to-right flowchart; I'll render it.)*

## Slide 6 — Wireframe / mockup (optional)
Dashboard mockup: a city map with road segments colored by criticality (green→red heatmap); a side panel "Disable node ▢" toggle; a result card showing "Avg travel time +28%, 3 areas isolated" after a node is disabled.
*(I'll render a simple mockup.)*

## Slide 7 — Architecture diagram
Two parallel tracks converging on the dashboard:
- **Track A (CV):** Data (Sentinel-2 / LISS-IV / DeepGlobe) → preprocessing + occlusion augmentation → U-Net/attention model (clDice loss) → road mask.
- **Track B (Graph):** road mask → skeletonize → MST/Disjoint-Set healing → NetworkX (betweenness, ablation, Resilience Index).
- Both → **Streamlit + Leaflet.js dashboard**.
*(Boxed architecture diagram; I'll render it.)*

## Slide 8 — Technologies
- **Deep learning:** Python, PyTorch, segmentation-models-pytorch, Albumentations
- **Geospatial:** GDAL, Rasterio, QGIS, OpenCV
- **Graph:** Scikit-Image / FilFinder (skeletonize), NetworkX, OSMnx (+ PyTorch Geometric optional)
- **Visualization / UI:** Streamlit, Leaflet.js, Matplotlib
- **Data:** Sentinel-2, Resourcesat LISS-IV, Cartosat-3 (finale); SpaceNet, DeepGlobe, OpenSatMap, OpenStreetMap

## Slide 9 — Estimated implementation cost (optional)
- Software: **₹0** — fully open-source stack.
- Data: **₹0** — all datasets are free / ISRO-provided.
- Compute: GPU for model training — covered by **free Kaggle/Colab GPUs** or our own workstation (≈ cloud equivalent only if scaled). 
- **Total prototype cost ≈ ₹0**; scales cheaply because the heavy parts (graph + dashboard) run on CPU.

## Slide 10 — Team details + Thank you
- Team name, members, institutions, contact.
- (Optional) one-line each on who owns CV vs graph.
- "Thank you" + ISRO/BAH 2026 branding.

---

### What I need to build the actual .pptx
1. **Team names + institutions** (for slides 1 and 10).
2. Confirm you want me to **generate the 4 diagrams** (slides 4, 5, 6, 7) as images.
3. Then I build the deck as a .pptx (or PDF) matching this.
