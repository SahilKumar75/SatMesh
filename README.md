# SatMesh

Occlusion-robust road extraction and network-resilience analysis from satellite imagery.

Built for the **ISRO Bharatiya Antariksh Hackathon 2026, Problem Statement 4 — Route Resilience.**

---

## Problem

Urban road networks extracted from satellite imagery suffer two compounding failures. First, tree canopy, building shadows, and cloud cover produce fragmented road masks that are topologically disconnected and unusable for routing or disaster planning. Second, even complete road maps rarely quantify which intersections are structural bottlenecks — the single points whose removal most damages the network.

SatMesh addresses both: an occlusion-robust **SegFormer** segmentation model produces continuous road masks, and a **graph-theoretic** pipeline heals the gaps, identifies critical "gatekeeper" nodes, and measures network resilience under simulated failure. A web dashboard runs the whole pipeline per city and visualises the result.

---

## Pipeline

```
satellite tile ──▶ SegFormer (road mask) ──▶ skeletonise ──▶ MST gap-healing
   (Esri / Sentinel-2)                                         (occlusion-aware,
                                                                extended-line)
        │                                                            │
        └────────────────────────────────────────────────┐         ▼
                                                  betweenness criticality
                                                  + node-ablation stress test
                                                  + Resilience Index + APLS
```

The same trained model feeds both the offline evaluation and the live dashboard.

---

## Repository layout

```
src/
  model/
    segformer.py        SegFormer MiT-B4 (3-ch RGB and 4-ch RGB+NIR builders)
    loss.py             Dice + weighted-BCE + soft-clDice (topology) loss
    train.py            two-stage trainer, RoadDS, occlusion augmentation
    infer.py            mask prediction (CUDA / MPS / CPU)
  graph/
    skeleton.py         mask -> nodes/edges graph
    heal.py             MST gap-healing with extended-line (occlusion-aware) bridging
    criticality.py      betweenness centrality + node-ablation curve
    zones.py            critical / vulnerable / resilient zone classification
    apls.py             Average Path Length Score vs OSM
    dem.py              SRTM elevation + flood-vulnerable node marking
  data/
    sentinel_dl.py      Sentinel-2 download (Microsoft Planetary Computer STAC)
    mask_raster.py      OSM road fetch + rasterise to masks
    city_config.py      cities.json loader
  pipeline.py           end-to-end: mask -> graph -> criticality -> APLS

scripts/
  build_highres_dataset.py   Esri World Imagery (~0.6 m) + OSM masks, 29 regions
  prepare_india_dataset.py   Sentinel-2 (10 m) tiles + published India dataset ingest
  auto_label.py              self-training pseudo-labels fused with OSM
  train.py                   training launcher (stage-1 pretrain, stage-2 fine-tune)
  kaggle_b4_train.py         Kaggle T4 runner

api/
  main.py             FastAPI: cities, run (SSE), metrics, graph, reroute/scenario
  pipeline_runner.py  streams pipeline progress
  graph_api.py        rerouting / node-disable / stress scenarios
dashboard/web/        MapLibre GL dashboard (graph / heatmap / mask / satellite)

cities.json           dashboard cities (bbox, center, flood threshold)
data/train_regions.json   29 training regions (metros, rural, terrains)
eval/                 track_a.py, apls_eval.py, full_eval.py
docs/                 problem_statement.md, approach.md, getting_started.md
checkpoints/          segformer_india_v1.pth, segformer_india_v2.pth
```

---

## Segmentation model

**Architecture.** True SegFormer (`smp.Segformer`, MiT-B4 encoder) — a transformer whose global self-attention provides the long-range context needed to infer roads under canopy and shadow.

**Resolution matters.** Road width is the hard constraint:
- **High-res (~0.3–0.6 m)** — Esri World Imagery, DeepGlobe, Cartosat-3. Dense urban lanes/gullies are visible; strict IoU > 70 % is achievable.
- **Sentinel-2 (10 m)** — roads are 1–2 px / sub-pixel; only major arterials resolve. Use relaxed-IoU.

So SatMesh trains per target resolution. The primary path is **high-res Esri + OSM** (`build_highres_dataset.py`).

**Loss.** `Dice (0.4) + weighted-BCE (0.3) + soft-clDice (0.3)`. The clDice term (Shit et al., CVPR 2021) is a bidirectional topology loss on soft skeletons — it penalises both broken and hallucinated roads, directly targeting connectivity under occlusion. Runs every epoch (stable).

**Occlusion augmentation.** `CanopyOcclusionOnRoad` paints green tree canopy and dark building shadows over road pixels across a wide size range, so the model learns to bridge gaps of varying length (per the Chesapeake-RSC "Seeing Roads Through Trees" finding that recall falls with gap distance).

**Auto-labelling.** `auto_label.py` runs the trained model over fresh tiles and fuses confident predictions with OSM (`mask = OSM ∪ confident-model`), growing label coverage past OSM's gaps without removing verified roads.

---

## Graph resilience

From a predicted mask, `pipeline.py`:
1. **Skeletonises** the mask into a node/edge graph.
2. **Heals gaps** — MST bridging gated by distance, stub angle, and an **extended-line mask check**: a road broken by shadow still leaves faint road pixels along the connector, while a bridge over open background does not.
3. **Scores criticality** — betweenness centrality finds gatekeeper intersections; node-ablation removes the top nodes and recomputes global efficiency.
4. **Resilience Index** — baseline vs perturbed average shortest-path; lower = more vulnerable.
5. **APLS** vs the OSM graph for topological accuracy.

A cache guard stages each run in `outputs/<city>/run_<ts>/` and only promotes it if the graph is non-degenerate, so a bad inference can't overwrite known-good outputs.

---

## Running the dashboard

```bash
pip install -r requirements.txt
uvicorn api.main:app --port 8011 --reload
# open http://localhost:8011
```

Pick a city, click **Run Pipeline** (streams progress via SSE), then explore the
graph / criticality heatmap / road mask / satellite views, run flood/seismic/
gatekeeper-collapse stress tests, and compute reroutes.

---

## Training

Two checkpoints, multi-resolution (see `~/.claude/plans/` / `docs/approach.md`):

```bash
# Checkpoint B — high-res 0.5 m base (DeepGlobe), strict-IoU target
python scripts/train.py --encoder mit_b4 --img-size 768 --batch 14 \
    --grad-checkpoint --epochs 50

# Build the India high-res dataset (Esri + OSM, 29 regions) — needs internet
python scripts/build_highres_dataset.py --regions all --zoom 18 --windows 30 \
    --out data/india_highres/train

# Checkpoint A — fine-tune the 3-ch base on high-res India RGB
python scripts/train.py --skip-stage1 --no-nir \
    --india-dir data/india_highres/train \
    --encoder mit_b4 --img-size 512 --batch2 4 --epochs2 30 --grad-checkpoint
```

`--clahe` enables CLAHE+gamma enhancement (recommended for the 10 m Sentinel-2 path).

---

## Evaluation targets (PS4 rubric)

| Metric | Stage | Notes |
|---|---|---|
| IoU / Dice | segmentation | strict on high-res; relaxed (3–5 px) on 10 m |
| Occlusion-Recall | segmentation | clDice + occlusion augmentation target this |
| Connectivity Ratio | graph | largest connected component after MST healing |
| Topological Accuracy | graph | APLS vs OSM ground truth |
| Resilience Index | graph | baseline / perturbed average shortest path |

Scoring is **50 % segmentation / 50 % graph-theoretic resilience.**

---

## Data sources

| Dataset | Use | Access |
|---|---|---|
| Esri World Imagery | high-res training imagery (~0.6 m) | XYZ tiles (no key) |
| OpenStreetMap | auto-generated masks + graph baseline | `osmnx` (ODbL) |
| DeepGlobe Road Extraction | 0.5 m pretraining | [Kaggle](https://www.kaggle.com/datasets/balraj98/deepglobe-road-extraction-dataset) |
| Sentinel-2 (Planetary Computer) | 10 m India inference/training | STAC API |
| India Sentinel-2 Roads | 10 m India fine-tune (5634 tiles) | [Zenodo 15765738](https://zenodo.org/records/15765738) |
| PMGSY GeoSadak / MoRTH / Bhuvan | govt road vectors (`--road-vectors`) | open-government |
| Resourcesat LISS-IV / Cartosat-3 | Indian imagery (5.8 m / high-res) | [Bhoonidhi](https://bhoonidhi.nrsc.gov.in/) / ISRO finale |

---

## Dependencies

```
torch >= 2.0          segmentation-models-pytorch >= 0.3
albumentations >= 1.3 opencv-python >= 4.8
osmnx >= 2.0          networkx >= 3.2
rasterio              geopandas
fastapi               uvicorn
```

Full list in `requirements.txt`.
