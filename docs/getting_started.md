# PS4 — Getting Started (data + research)

Study area (default): **Bengaluru** (the city the mentors named). Easy to swap.

The project has **two parallel tracks** — the mentors recommend one sub-team per track:
- **Track A (CV):** extract roads from satellite imagery, even under trees/shadows.
- **Track B (Graph):** turn roads into a network, find critical nodes, stress-test, dashboard.

---

## 1. Data check — DO THIS FIRST

### Track B data (graph) — already proven trivial
Run `ps4_data_check.py` (in this folder) on your own machine:
```
pip install osmnx networkx matplotlib
python ps4_data_check.py
```
It downloads Bengaluru's real road network from OpenStreetMap (free, no login), turns it into a graph, scores the critical intersections (betweenness centrality), runs a node-removal stress test, computes the Resilience Index, and saves a figure.
**If it prints numbers + a PNG, the entire graph half is de-risked.** (Couldn't run it inside Claude's sandbox — its network is locked to OSM servers — but it runs fine on a normal machine.)

### Track A data (CV) — the smart shortcut
**Do NOT start with Sentinel-2 (needs a Copernicus login and is fiddly).** Start with ready-made labeled road data so you can train a model on day 1:

- **DeepGlobe Road Extraction Dataset** — 6,226 RGB images (1024×1024, 50 cm), each with a road mask. Instant download, no special access:
  https://www.kaggle.com/datasets/balraj98/deepglobe-road-extraction-dataset
- **SpaceNet Roads** (road centerlines, cities incl. Mumbai): https://spacenet.ai/challenges/ — or via the `torchgeo` library.
- **OpenStreetMap road vectors** — your free "answer key" for any area (same source as `ps4_data_check.py`).

Train and prove your segmentation model on DeepGlobe first. **Only later** apply it to Indian imagery:
- **Sentinel-2** (10 m, free): via Copernicus Data Space Ecosystem — `openeo` or `sentinelhub` Python libs (needs a free account). https://dataspace.copernicus.eu/
- **Resourcesat LISS-IV (5.8 m)** for India: ISRO **Bhoonidhi** portal (free account).
- **Cartosat-3** (high-res): provided by ISRO **during the 30-hour finale** — don't block on it now.

---

## 2. Research — the build plan

### Track A: occlusion-robust road segmentation
- **Baseline (day 1):** **U-Net with a ResNet backbone** — the standard, fast-to-train road-segmentation model. Use `segmentation-models-pytorch` (one-line model creation, pretrained encoders).
- **Upgrade:** **DeepLabV3+**, then a **transformer/attention** model (e.g. SegFormer) for "seeing through" occlusions via long-range context. This upgrade is exactly what the 50%-CV score rewards.
- **Occlusion trick:** during training, **artificially paint occlusions** (tree/shadow patches) onto images so the model learns to fill gaps. Use **Albumentations** for this.
- **Loss:** combine **Dice + IoU + a boundary-aware loss** (mentors' spec); optionally a connectivity loss.
- **Libraries:** PyTorch, `segmentation-models-pytorch`, Albumentations, Rasterio, GDAL, OpenCV.

### Track B: graph healing + criticality (mostly proven by the script)
- **Skeletonize** the predicted road mask (Scikit-Image / FilFinder) → 1-pixel centerlines → nodes at intersections/endpoints, segments as edges.
- **Heal gaps** with **MST + Disjoint-Set (Union-Find)** using Euclidean distance + angular alignment so bridged roads follow a natural line.
- **Criticality:** `networkx.betweenness_centrality` → "gatekeeper nodes."
- **Stress test:** remove top nodes, recompute average shortest-path length → **Resilience Index = baseline / perturbed** (already in the script).
- **Libraries:** NetworkX (core), OSMnx, optionally PyTorch Geometric for GNN extensions.

### The dashboard (where you win presentation points)
- **Streamlit + Leaflet.js** (or pydeck): a map where the user clicks an intersection to "disable" it and instantly sees rerouting + travel-time increase, with a criticality heatmap overlay.

### Evaluation you're graded on (build to these)
- CV: IoU & Dice (esp. **occlusion-recall**), generalization across terrains, **relaxed IoU** (3–5 px tolerance buffer).
- Graph: connectivity ratio after MST healing, topological accuracy vs OSM (average path-length error).
- Scoring is **50% CV / 50% graph** — don't neglect either.

---

## 3. Week-1 plan (before the July 1 proposal)
1. **Both tracks:** run the two data checks above (OSM script + DeepGlobe download). ~half a day.
2. **Track A:** train a U-Net on DeepGlobe, get a rough road mask + one before/after occlusion example. Screenshot it.
3. **Track B:** run `ps4_data_check.py`, save the Bengaluru graph + Resilience Index + figure.
4. **Together:** these two screenshots become a mini proof-of-concept in the proposal — most teams submit idea-only, so this puts you ahead.
5. Write + submit the idea proposal (I'll draft it) before **1 July**.

## Sources
- [DeepGlobe Road Extraction Dataset (Kaggle)](https://www.kaggle.com/datasets/balraj98/deepglobe-road-extraction-dataset)
- [SpaceNet challenges](https://spacenet.ai/challenges/)
- [Copernicus Data Space Ecosystem (Sentinel-2)](https://dataspace.copernicus.eu/)
- [torchgeo SpaceNet loader](https://torchgeo.readthedocs.io/en/v0.6.1/_modules/torchgeo/datasets/spacenet.html)
