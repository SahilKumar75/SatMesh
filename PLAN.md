# SatMesh (PS4) — Full Multi-Discipline Scorecard & Roadmap to 100/100
**ISRO Bharatiya Antariksh Hackathon 2026 · PS4 Route Resilience**
Reviewed by: GeoAI/ML Engineer · Spatial Data Engineer · Software Architect · Product Manager
Last updated: 2026-06-19

---

## Current Score: ~52 / 100

| Metric | Weight | Current | Score | Gap driver |
|---|---|---|---|---|
| IoU & Dice | 15% | 0.60 / 0.65 on DeepGlobe val | 7/15 | US/European domain, no Indian fine-tune |
| Occlusion-Recall | 10% | Unknown (never tested on shadow/canopy tiles) | 4/10 | CoarseDropout is rectangular black, not canopy-shaped |
| Relaxed-IoU / Generalisation | 25% | Partial (urban only, no Bengaluru tile) | 11/25 | No Sentinel-2, no terrain diversity |
| Connectivity Ratio | 12% | 0.775 (bug fixed) | 7/12 | Fixed; not yet optimised |
| Topological Accuracy vs OSM | 15% | Pixel grid ≠ real streets | 4/15 | **Single biggest miss — fake coordinates** |
| Gatekeeper Nodes | 10% | 12 identified | 7/10 | Present but unvalidated on real street network |
| Resilience Index | 13% | 1.000 → 0.784 after 3 removals | 12/13 | Strongest metric — logic is correct |

**Estimated total: 52 / 100**

---

## What 100 / 100 Requires

| Metric | Threshold for full marks |
|---|---|
| IoU & Dice | IoU ≥ 0.78, Dice ≥ 0.84 on Indian urban + rural tiles |
| Occlusion-Recall | Roads recovered under tree canopy, shadow, cloud — measurable via masked evaluation |
| Relaxed-IoU / Generalisation | 3–5 px buffer metric ≥ 0.85 across all three terrain types |
| Connectivity Ratio | Measurable LCC % increase after MST healing on real georeferenced graph |
| Topological Accuracy | Average Path Length error vs OSM/MapmyIndia < 15% on N random O-D pairs |
| Gatekeeper Nodes | Betweenness nodes align with real street bottlenecks on georeferenced graph |
| Resilience Index | Correct formula, reproducible, demonstrable in dashboard with real tile |

---

## Three Highest-Leverage Actions

| # | Action | Points gained | Effort |
|---|---|---|---|
| 1 | **Fix georeferencing** (wire real `top_left_lat/lon` from Bhoonidhi tile into pipeline) | +12 | Sprint 3, multi-day |
| 2 | **Bengaluru fine-tune** on Kaggle T4 (Sentinel-2 + OSM labels) | +8 | Sprint 4, 30 min training |
| 3 | **Canopy occlusion augmentation** (elliptical green blobs over road pixels) | +5 | 1 hour, no retraining |

---

## Track A Roadmap (ML Pipeline)

### Fix 1 — Canopy Occlusion Augmentation ⏱ 1 hour · +5 pts
**File:** `track_a/road_segmentation.py` lines 93-101 AND `kaggle/satmesh_train.ipynb` cell-3

Replace current `CoarseDropout` with a `CanopyOcclusionOnRoad` custom transform that places
elliptical green-toned blobs specifically over **known road pixels** in the mask.
The key insight: current rectangular black patches teach the model to handle pixel blackouts,
not spectrally complex tree canopy (which has NDVI signal, not zero).

```python
# Add this class before train_tf in both files:
class CanopyOcclusionOnRoad(DualTransform):
    """Elliptical canopy-coloured blobs placed over known road pixels."""
    def __init__(self, n_blobs=(2, 8), size=(20, 80), p=0.5):
        super().__init__(p=p)
        self.n_blobs = n_blobs; self.size = size

    def apply(self, img, blobs=None, **params):
        img = img.copy()
        for (cx, cy, a, b, color) in blobs:
            cv2.ellipse(img, (cx, cy), (a, b), 0, 0, 360, color, -1)
        return img

    def apply_to_mask(self, mask, **params):
        return mask   # ground truth unchanged — roads still exist under canopy

    def get_params_dependent_on_data(self, params, data):
        img = data["image"]
        h, w = img.shape[:2]
        n = np.random.randint(*self.n_blobs)
        blobs = []
        for _ in range(n):
            cx, cy = np.random.randint(0, w), np.random.randint(0, h)
            a = np.random.randint(*self.size) // 2
            b = np.random.randint(*self.size) // 2
            color = (np.random.randint(20,60), np.random.randint(60,120), np.random.randint(20,50))
            blobs.append((cx, cy, a, b, color))
        return {"blobs": blobs}

    def get_transform_init_args_names(self): return ("n_blobs", "size")
```

Also strengthen existing shadow aug:
```python
A.RandomShadow(shadow_roi=(0,0,1,1), num_shadows_lower=1, num_shadows_upper=3,
               shadow_dimension=6, p=0.5),
```

Score: **22 → 27 / 50**

---

### Fix 2 — Bengaluru Fine-Tune ⏱ 2h setup + 30min Kaggle T4 · +8 pts
**File:** `kaggle/satmesh_train.ipynb` cells 2 + 4

Add fine-tune mode in cell-2 (pair discovery) — load existing DeepGlobe checkpoint,
oversample Bengaluru pairs 3× to overcome DeepGlobe dominance, reduce LR to 2e-4:

```python
FINETUNE = True
FINETUNE_DIR = "/kaggle/input/bengaluru-sentinel2-osm/train"

if FINETUNE and os.path.isdir(FINETUNE_DIR):
    ft_pairs = [(sp, sp.replace("_sat.jpg","_mask.png"))
                for root,_,files in os.walk(FINETUNE_DIR)
                for sp in [os.path.join(root,f)] if f.endswith("_sat.jpg")
                if os.path.exists(sp.replace("_sat.jpg","_mask.png"))]
    pairs = pairs[:2000] + ft_pairs * 3
    random.shuffle(pairs)

# In cell-4 — load pre-trained weights:
if FINETUNE:
    model.load_state_dict(torch.load("/kaggle/input/satmesh-checkpoint/best_model.pth",
                                      map_location=DEVICE))
    opt = torch.optim.AdamW(model.parameters(), lr=2e-4, weight_decay=1e-4)
```

Data preparation: `python data/prepare_finetune.py --bbox 12.85,77.50,13.05,77.70`
(Downloads Sentinel-2 + OSM labels for Bengaluru bbox → image/mask pairs)

Score: **27 → 35 / 50**

---

### Fix 3 — Switch to DADE Bottleneck ⏱ 30min code + 35min Kaggle · +5 pts
**File:** `kaggle/satmesh_train.ipynb` cell-4

The DADE arm already exists in `track_a/model_gym.py`. Validate it first
(15 epochs, ~10 min on T4), then promote to main notebook if it beats baseline:

```python
# Quick validation run in model_gym.py:
# python track_a/model_gym.py --arms dade --epochs 15

# If DADE wins, replace cell-4 model line:
from track_a.model_gym import build_model, Arm
arm = Arm("dade", "unet_dade", "resnet34", use_cldice=True, occ_aug=True)
model = build_model(arm).to(DEVICE)
BATCH = 3  # ResNet50 uses more VRAM
```

Dilated rates 1, 3, 5, 9 at bottleneck give 60+ px effective receptive field
vs ResNet34's ~7px — critical for tracing roads under wide canopy gaps.

Score: **35 → 40 / 50**

---

### Fix 4 — NDVI as 4th Input Channel ⏱ 3h code + 35min Kaggle · +4 pts
**File:** `track_a/road_segmentation.py` `RoadDS.__getitem__`, `kaggle/satmesh_train.ipynb` cell-3/4

Approximate NDVI from visible bands for DeepGlobe (RGB-only):
```python
g, r = img[:,:,1]/255.0, img[:,:,0]/255.0
ndvi = ((g - r) / (g + r + 1e-6)).astype(np.float32)
img_t = torch.cat([a["image"], torch.from_numpy(ndvi).unsqueeze(0)], 0)
```

Patch first conv to accept 4 channels while keeping ImageNet weights:
```python
model = smp.Unet("resnet34", encoder_weights="imagenet", in_channels=3, classes=1)
old = model.encoder.conv1
new = nn.Conv2d(4, old.out_channels, old.kernel_size, old.stride, old.padding, bias=False)
new.weight.data[:,:3] = old.weight.data
new.weight.data[:,3] = old.weight.data.mean(1)
model.encoder.conv1 = new
```

Score: **40 → 44 / 50**

---

## Track B Roadmap (Graph / Resilience)

### Fix 1 — Real Georeferencing ⏱ Multi-day · +9 pts (Topological Accuracy)
**This is the highest-impact single fix in the entire project.**

Steps:
1. Download Bengaluru Sentinel-2 L2A tile from **Bhoonidhi** (bhoonidhi.nrsc.gov.in)
   - Register → Data Catalog → Search "Bengaluru" → Sentinel-2 Level-2A → Download `.SAFE`
2. Extract real affine transform with rasterio:
```python
import rasterio
with rasterio.open("T43PGM_B04.tif") as src:
    transform = src.transform   # pixel → CRS
    crs = src.crs               # EPSG:32643 for Bengaluru
    # top-left corner in WGS84:
    from pyproj import Transformer
    t = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
    lon0, lat0 = t.transform(transform.c, transform.f)
```
3. Pass `--top_left_lat lat0 --top_left_lon lon0` to `pipeline/run.py`
4. Regenerate `data.js` — nodes now have real coordinates aligned to basemap

Without this, the OSM comparison in `run.py` is already wired but produces garbage
because pixel coordinates ≠ real metres.

Score: **24 → 37 / 50**

---

### Fix 2 — MapmyIndia APL Benchmark ⏱ 3h · +2 pts (Topological Accuracy)
**File:** `data/fetch_mapmyindia_paths.py` (new)

Sample N random O-D pairs from healed graph → query Mappls Route API for real driving
distance → compute Average Path Length error vs your graph's Dijkstra distances.
This is the exact scored metric.

```python
# Free tier: 1000 req/day. API key from mappls.com/api
import requests
def mappls_route(api_key, lat1, lon1, lat2, lon2):
    url = f"https://apis.mapmyindia.com/advancedmaps/v1/{api_key}/route_adv/driving/{lon1},{lat1};{lon2},{lat2}"
    r = requests.get(url).json()
    return r["routes"][0]["distance"]  # metres
```

Score: **37 → 39 / 50**

---

### Fix 3 — NDVI-Guided Healing Zones ⏱ 2h · +2 pts (Connectivity Ratio)
**File:** `track_b/heal.py` `heal_gaps()` signature

Angular continuity check **already exists** in heal.py (dot product gate at line ~228).
What's missing is adaptive `max_gap_m` based on NDVI:

```python
def heal_gaps(G, max_gap_m=50.0, angular_threshold=0.7,
              ndvi_mask=None, ndvi_gap_multiplier=2.0):
    # Inside the pair loop, after angular check:
    if ndvi_mask is not None:
        mid_r = int((G.nodes[ni]["row"] + G.nodes[nj]["row"]) / 2)
        mid_c = int((G.nodes[ni]["col"] + G.nodes[nj]["col"]) / 2)
        is_canopy = ndvi_mask[np.clip(mid_r,0,ndvi_mask.shape[0]-1),
                               np.clip(mid_c,0,ndvi_mask.shape[1]-1)]
        effective_max = max_gap_m * ndvi_gap_multiplier if is_canopy else max_gap_m
    else:
        effective_max = max_gap_m
```

Score: **39 → 41 / 50**

---

### Fix 4 — OSM GPS Traces for Betweenness Validation ⏱ 2h · +1 pt
GPS traces from planet.osm.org give anonymised movement density — NOT road geometry.
Use to validate that your top-betweenness nodes match real movement bottlenecks.
Bin traces into a 2D density grid, overlay on graph → sanity check only, not a scored metric directly.

Score: **41 → 42 / 50**

---

## Dashboard Roadmap

### Current scores (Software Architect review)
- Demo-ability: **7/10** — full-screen Leaflet, all PS4 features present
- Architecture soundness: **6/10** — two disconnected dashboards, fake coordinates paper over geo issue

### Fix 1 — Before/After Occlusion Recovery Slider ⏱ 3-4h · High judge impact
**THE single most impressive thing not yet built.** Split the satellite tile into two panels:
left = raw broken road mask, right = healed graph on same tile. CSS clip-path wipe slider.
Tells the entire PS4 story ("spectral blindness → topological healing") in one visual.
No other CV team is likely to have this.

**File:** `dashboard/web/index.html` + `dashboard/web/app.js`

```javascript
// Two L.imageOverlay layers + CSS clip slider
const rawOverlay   = L.imageOverlay(rawMaskUrl, bounds).addTo(map);
const healedOverlay = L.imageOverlay(healedMaskUrl, bounds).addTo(map);
// Slider input controls clip-path on rawOverlay's container div
sliderEl.addEventListener("input", e => {
    rawOverlay.getElement().style.clipPath = `inset(0 ${100 - e.target.value}% 0 0)`;
});
```

---

### Fix 2 — OSM Road Overlay Layer ⏱ 2-4h (after georeferencing)
Fetch OSM road vectors for current viewport via osmnx → render as gray Leaflet GeoJSON layer.
Lets judges visually compare model-detected roads vs OSM ground truth in one frame.

---

### Fix 3 — GeoJSON Export of Healed Graph ⏱ 1-2h
Add to Streamlit sidebar:
```python
import json
edges_geojson = {
    "type": "FeatureCollection",
    "features": [{
        "type": "Feature",
        "geometry": {"type": "LineString",
                     "coordinates": [[geo[u][1], geo[u][0]], [geo[v][1], geo[v][0]]]},
        "properties": {"length": d.get("length",1), "synthetic": d.get("synthetic",False)}
    } for u,v,d in G.edges(data=True)]
}
st.download_button("⬇ Download road graph GeoJSON",
    json.dumps(edges_geojson), "satmesh_roads.geojson", "application/geo+json")
```
Lets judges open in QGIS (explicitly listed as suggested tool in PS4 deck).

---

## Data Sources

| Source | URL | Use | Priority |
|---|---|---|---|
| **Bhoonidhi (ISRO)** | bhoonidhi.nrsc.gov.in | Bengaluru LISS-IV/Cartosat tile with real coordinates | P0 |
| **Microsoft ML Roads India** | github.com/microsoft/RoadDetections | Extra Indian road geometries for training labels | P1 |
| **OSM via osmnx** | automatic | Real-time road graph any city, any zoom | P1 |
| **MapmyIndia (Mappls) API** | mappls.com/api | APL ground truth for Topological Accuracy metric | P2 |
| **OSM GPS traces** | planet.osm.org/gps-points | Validate betweenness against real movement density | P3 |
| **DeepGlobe** | Kaggle | Base pre-training (current, already done) | Done |

### Why no per-city retraining at runtime
User pans map → OSM graph via API (<1s) + model inference on tile (~0.5s) → real-time.
Fine-tuning is only done once offline on Kaggle. The model is frozen at runtime.

---

## Sprint Backlog

### ✅ Sprint 0 — Backend correctness (DONE)
- connectivity_ratio bug fixed (G_skeleton vs G_healed)
- G_osm self-comparison fixed → None
- FileNotFoundError on missing checkpoint
- SVG glyph invisible fix, disabled node fill fix

### ✅ Sprint 1 — UX polish (DONE)
- Keyboard nav, ARIA, focus rings, CartoDB attribution

### ✅ Sprint 2 — PS4 rubric strip + exports (DONE)
- Track B chip → 6 rubric metric cards in web dashboard
- Streamlit download buttons (ablation CSV + criticality JSON)
- src == dst reroute guard

### 🔲 Sprint 3 — Georeferencing + OSM live layer (NEXT — highest ROI)
**Acceptance criteria:**
- [ ] Bhoonidhi tile downloaded for Bengaluru bbox, real lat/lon extracted with rasterio
- [ ] `pipeline/run.py --top_left_lat X --top_left_lon Y` produces graph with real coordinates
- [ ] `data.js` regenerated — nodes visually align with OSM road network in browser
- [ ] `data/fetch_osm_live.py` working: any bbox → instant NetworkX graph
- [ ] OSM road overlay layer added to web dashboard (gray, toggleable)

### 🔲 Sprint 4 — Bengaluru fine-tune + occlusion aug (Kaggle)
**Acceptance criteria:**
- [ ] `data/prepare_finetune.py` generates Sentinel-2 + OSM label pairs for Bengaluru
- [ ] CanopyOcclusionOnRoad augmentation added to `road_segmentation.py` + Kaggle notebook
- [ ] Fine-tune run on Kaggle T4 x2: ≥20 epochs, IoU ≥ 0.68 on Bengaluru val
- [ ] `best_model.pth` saved to Google Drive (never depend on Kaggle during hackathon)
- [ ] DADE arm validated via model_gym.py before promoting to main notebook

### 🔲 Sprint 5 — Hackathon day prep
**Acceptance criteria:**
- [ ] Before/after occlusion recovery slider in web dashboard
- [ ] GeoJSON export button in Streamlit
- [ ] MapmyIndia APL benchmark script (`data/fetch_mapmyindia_paths.py`)
- [ ] Cartosat-3 quick-inference script (histogram-match → run pipeline → 2 min total)
- [ ] Slide deck updated with real metrics
- [ ] Demo rehearsed: every team member can explain each number

---

## Hackathon Day Critical Path (30 hours)

```
Hour 0–2   [ML]         Receive Cartosat-3 tile. Run pipeline/run.py immediately.
                        Fetch OSM graph for same bbox. Confirm map alignment. GATE.
Hour 2–6   [ML+Data]   Fine-tune 10 epochs on judge tile bbox (Kaggle T4, ~15 min).
           [Dashboard] Confirm all 7 metric cards populate. Test download buttons.
Hour 6–10  [All]       Merge model roads + OSM. Recompute Connectivity + Topo Accuracy.
                        Lock final metric numbers for slide deck.
Hour 10–24 [Dashboard] Polish demo flow. Run ablation stress tests on judge tile.
           [ML]        Record before/after occlusion visuals.
Hour 24–28 [All]       Slide deck with actual numbers. Demo rehearsal.
Hour 28–30 [All]       Push to GitHub. Submit report + video. Done.
```

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation | Contingency |
|---|---|---|---|---|
| Georeferencing still broken on hackathon day | Medium | -12 pts (3 Track B metrics) | Complete Sprint 3 and test against known Bengaluru tile pre-hackathon | Fall back to OSM-only graph — still demonstrates graph logic + resilience |
| Kaggle T4 quota exhausted during hackathon | Low-Medium | -8 pts (stuck at 0.60 IoU) | Run fine-tune this week. Save `best_model.pth` to Google Drive. Never retrain during event | Use existing 0.60 IoU model; focus on Track B which is already stronger |
| Cartosat-3 tile has different radiometry (sensor mismatch) | High | IoU drop on judge tile | Add histogram-match preprocessing in `pipeline/run.py` normalise judge tile to Sentinel-2 stats | Add `RandomBrightness/Contrast` aug now so model is sensor-agnostic |
| Demo crashes during judge review | Medium | Catastrophic demo loss | Static screenshots + pre-recorded video as backup | Always have ablation CSV + metrics JSON ready to show as fallback |
| OSM data sparse for judge tile area | Low | Topological Accuracy unscored | Use MapmyIndia API as alternative ground truth | Report connectivity ratio and RI which need no OSM |

---

## GPU Constraint
Azure for Students cannot get GPU quota.
**Use Kaggle T4 x2 (free, 30 GPU h/week).**
Fine-tune estimate: 20 epochs on T4 x2 ≈ 30 min.
DADE validation run: 15 epochs ≈ 10 min.
Never run training during the hackathon — pre-train everything and commit weights.

---

## Score Projection

| After | Score |
|---|---|
| Current | 52/100 |
| + Canopy aug (1h) | 57/100 |
| + Bengaluru fine-tune (Kaggle) | 65/100 |
| + Georeferencing (Sprint 3) | 77/100 |
| + DADE bottleneck + NDVI channel | 82/100 |
| + MapmyIndia APL + GeoJSON export | 85/100 |
| + Occlusion slider + OSM overlay | 90/100 |
| + Perfect Cartosat-3 inference on judge tile | **95/100** |
