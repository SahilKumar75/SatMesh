# SatMesh

Road extraction and network resilience analysis from satellite imagery.

Built for ISRO Bharatiya Antariksh Hackathon 2026, Problem Statement 4 — Route Resilience.

---

## Problem

Urban road networks extracted from satellite imagery suffer from two compounding failures. First, tree canopy, building shadows, and cloud cover produce fragmented road masks that are topologically disconnected and unusable for routing or disaster planning. Second, even complete road maps rarely quantify which intersections are structural bottlenecks — the single points whose removal would most damage the network.

SatMesh addresses both: an occlusion-robust segmentation model produces continuous road masks, and a graph-theoretic pipeline identifies critical nodes and measures network resilience under simulated failure.

---

## Repository layout

```
track_a/
    road_segmentation.py     U-Net road segmentation with clDice loss
track_b/
    graph_resilience.py      Betweenness centrality + resilience stress test
docs/
    problem_statement.md     Full PS4 specification
    approach.md              Technical approach and build plan
    getting_started.md       Data sources and week-1 checklist
research/                    Background notes and proposal drafts
requirements.txt
```

---

## Track A — Road Segmentation

**Model.** U-Net with a pretrained ResNet-34 encoder (`segmentation-models-pytorch`). Trained on the DeepGlobe Road Extraction Dataset (6,226 RGB images at 50 cm/px with pixel-level road masks).

**Loss.** Combined Dice (0.4) + BCE (0.3) + clDice (0.3).

The clDice term (Shit et al., CVPR 2021) computes Dice on the soft skeleton of the prediction rather than on the mask itself. Because the skeleton collapses to centerlines, the loss directly penalises broken road segments — which is exactly what the PS4 rubric measures as Occlusion-Recall.

**Augmentation.** `CoarseDropout` and `RandomShadow` are applied during training to simulate tree canopy occlusion and building shadow. This forces the model to learn gap-bridging rather than pixel matching.

**Optimiser.** AdamW with a one-cycle LR schedule. Best checkpoint (by validation IoU) is saved to `best_model.pth`.

### Running on Kaggle (recommended, free GPU)

1. Open the [DeepGlobe dataset](https://www.kaggle.com/datasets/balraj98/deepglobe-road-extraction-dataset).
2. Click **New Notebook** → Settings → Accelerator → GPU T4.
3. Paste `track_a/road_segmentation.py` into a cell and run.
4. Outputs: `ps4_predictions.png` (satellite / ground truth / prediction grid) and `best_model.pth`.

Typical runtime: 12 minutes for 8 epochs on a T4 with `SUBSET = 800`.

### Running locally

```bash
pip install -r requirements.txt
# Set DATA_DIR in road_segmentation.py to your DeepGlobe train/ folder.
python track_a/road_segmentation.py
```

---

## Track B — Graph Resilience

Takes a road network (from OSM or a predicted mask) and computes:

1. **Betweenness centrality** — identifies gatekeeper intersections whose removal most disrupts routing.
2. **Node-ablation stress test** — removes the top node, recomputes average shortest-path length.
3. **Resilience Index** — `baseline_avg_path / perturbed_avg_path`. Values below 1 indicate the network degraded after the removal.

The default study area is central Bengaluru (lat 12.9716, lon 77.5946, 1500 m radius). Change `CITY_POINT` and `RADIUS_M` for any other city.

```bash
pip install osmnx networkx matplotlib
python track_b/graph_resilience.py
```

Outputs: printed centrality scores + Resilience Index, and `ps4_bengaluru_roadgraph.png`.

---

## Evaluation targets (PS4 rubric)

| Metric | Track | Notes |
|---|---|---|
| IoU / Dice | A | Measured on DeepGlobe val split |
| Occlusion-Recall | A | clDice loss targets this directly |
| Connectivity Ratio | A → B | % increase in largest connected component after MST healing |
| Topological Accuracy | B | Average path-length error vs OSM ground truth |
| Resilience Index | B | Baseline / perturbed avg shortest path |

Scoring is 50% Track A / 50% Track B.

---

## Data sources

| Dataset | Use | Access |
|---|---|---|
| DeepGlobe Road Extraction | Track A training | [Kaggle](https://www.kaggle.com/datasets/balraj98/deepglobe-road-extraction-dataset) |
| SpaceNet Roads | Additional pretraining | [spacenet.ai](https://spacenet.ai/challenges/) |
| OpenStreetMap | Graph baseline + ground truth masks | `osmnx` (no account needed) |
| Resourcesat LISS-IV | Indian imagery inference | [Bhoonidhi portal](https://bhoonidhi.nrsc.gov.in/) |
| Cartosat-3 | High-res challenge data | Provided by ISRO during the finale |

---

## Dependencies

```
torch >= 2.0
segmentation-models-pytorch >= 0.3
albumentations >= 1.3
opencv-python >= 4.8
osmnx >= 1.9
networkx >= 3.2
```

Full list in `requirements.txt`.
