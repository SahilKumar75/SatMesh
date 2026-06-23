# PS4 PPT Strategy — Deep Research (verified) for the Idea Round

> Goal: an idea-submission deck that ISRO scientists trust. Differentiation = depth
> + real-world grounding in ISRO's OWN data, not a generic "SegFormer + betweenness"
> pipeline. Every data source below is verified accessible. Sources at the bottom.

---

## 0. The core thesis (what makes a scientist trust us)

Most teams will treat PS4 as: segment roads → betweenness → remove a node → "resilience".
That is abstract and arbitrary. **We ground every stage in real, observed, indigenous
data and real disaster events.** A scientist trusts a system that *reproduces what they
have already observed* (e.g. the 2015 Chennai flood footprint NRSC captured via RISAT)
and that uses *their own* data products (Bhuvan flood hazard, Cartosat, LISS-IV, NDEM).

Three honesty signals that separate us from AI-generated decks:
1. **Resolution physics** — a 4 m road is sub-pixel at 10 m Sentinel-2; we say so and
   design a multi-sensor pipeline instead of claiming impossible IoU.
2. **Real-event grounding** — we replay observed floods, not random node removals.
3. **Named the hard parts** — seasonal occlusion, OSM gaps, sub-pixel limit (a slide
   admitting open problems; scientists distrust "it's solved").

---

## 1. Our weak areas → existing solutions → what works → innovation

### Weakness A — "Creating data was tough, so we made our own"
**Reframe as a strength** (PS4 explicitly praises "zero-manual-effort automation").
- *Existing solution we built*: `build_highres_dataset.py` — Esri World Imagery
  (~0.6 m) + OSM masks, auto-aligned in Web Mercator, **29 regions** (metros, rural,
  9 terrains incl. forested). No manual annotation.
- *What works*: geo-referenced image+OSM pairing is pixel-exact and legal (ODbL).
- *Innovation angle*: a **resolution-adaptive, multi-terrain auto-dataset** — most
  teams use only DeepGlobe (US). We generate India-specific dense + rural + forested.

### Weakness B — "We lack labelling"
**Fix with verified SOTA auto-labeling (2024–25):**
- *Existing solutions*: **SAM-based auto-labeling** — ALPS (SAM auto-label + pretrain),
  SAM2-ELNet (label enhancement/auto-annotation), **TPP-SAM** (trajectory-point-prompted
  SAM for *zero-shot road extraction*), GeoSAM (SAM for mobility infrastructure).
- *What we already have*: `auto_label.py` — confidence-gated self-training **fused with
  OSM** (OSM anchors truth, model adds gullies OSM missed).
- *What works best for us / 30 h*: **OSM-anchored fusion** (low risk) + optional
  **SAM label-enhancement** to sharpen edges. Pure pseudo-label = confirmation bias;
  fusion avoids it. Add **govt vectors** (PMGSY GeoSadak rural, NHAI, Bhuvan) for the
  rural gaps OSM lacks.
- *Innovation angle*: a **3-tier labeling stack** — OSM-all → govt vectors → model
  self-labeling — that *grows past* OSM's coverage. Honest, legal, novel.

### Weakness C — "We lack real road-network simulation"
**This is the biggest opportunity.** Fix by grounding the graph in real hazard +
exposure data (all verified below). Turn "remove a node" into "replay a real flood and
watch the city fragment." Detailed in §2–§3.

---

## 2. Real-world data layers (all verified accessible)

| Layer | Source (verified) | What it gives | Access |
|---|---|---|---|
| **Flood hazard** | NRSC/Bhuvan **NDEM** Flood Hazard Zonation + Flood Affected Area Atlas + National Flood Vulnerability Assessment (grid-level rainfall/runoff/vulnerability) | Where India actually floods, incl. observed event footprints (2015 Chennai via RISAT) | ndem.nrsc.gov.in/hydrological_fhz.php ; bhuvan-app1.nrsc.gov.in/disaster |
| **Flood provenance** | **DEM flow-accumulation** (we have SRTM DEM) via pysheds/richdem | "Where the water comes from" — upstream catchment, flow paths, low points that flood first | computed locally, CPU |
| **Seismic** | **BIS seismic zonation** (Zones II–V/VI), Himalayan faults (MCT/MBT/MFT), NCS | Per-city quake risk weight | data.gov.in/resource/shape-file-seismic-zones |
| **Population exposure** | **WorldPop** (1 km grid GeoTIFF, per year) / **GHSL** (EC JRC) / Kontur 400 m H3 | People served by / stranded behind each road | hub.worldpop.org ; HDX |
| **Rainfall (event truth)** | **IMD gridded daily rainfall** 0.25°, 1901–2024, NetCDF | Validate against real events (Chennai 2015, Bengaluru 2022) | imdpune.gov.in ; github.com/prajeeshag/imddata |
| **Road importance** | OSM road hierarchy (motorway→residential) + **betweenness** | Legal proxy for "busiest" road (real traffic data is proprietary/ToS-locked) | osmnx |

> Note on "peak-time / busiest road / cab data": real-time traffic is Google/Ola/
> proprietary (ToS-blocked for us). The **legal, defensible proxy** = OSM road class +
> graph betweenness + WorldPop density. State this honestly in the deck.

---

## 3. The differentiator — "Resilience Intelligence Stack" (how layers sync)

Every layer is geo-referenced (lat/lon) → they overlay on one map → graph nodes inherit
hazard + population attributes by **spatial join**. One coherent system, not 6 demos.

```
L1  Imagery (resolution-adaptive)  Sentinel-2/LISS-IV wide  +  Cartosat-3 on critical corridors
        │
L2  Road extraction (SegFormer, occlusion-robust)  ──▶  road mask
        │
L3  Topology (skeleton + MST/extended-line healing)  ──▶  routable graph
        │
L4  HAZARD + EXPOSURE join (the innovation):
        • Flood:   NRSC flood-hazard + DEM flow-accumulation  → flood ORDER of each road
        • Seismic: BIS zone                                   → structural risk weight
        • People:  WorldPop                                   → population served per road
        │
L5  Composite criticality = betweenness × population-served × hazard-exposure
        (not betweenness alone — this is the new metric)
        │
L6  Simulation:
        • REAL-EVENT REPLAY: load 2015 Chennai / 2022 Bengaluru flood footprint
          → progressively remove roads by rising water level (DEM) → watch fragmentation
        • Cascading failure (percolation): flood rises by elevation, roads close in
          elevation order, traffic reroutes, neighbors overload → collapse curve
        │
L7  Decision dashboard: which gatekeeper, how many people stranded, surviving
        evacuation route, travel-time increase
```

**Named contributions to coin in the deck** (named ideas read as research):
- **Blind-Spot Index** = criticality × model-uncertainty → the critical road we're least
  sure exists (where to send a survey/Cartosat-3 tasking).
- **Flood-Percolation Collapse Curve** = connectivity vs rising flood elevation.
- **Composite Criticality** = betweenness × population × hazard (vs plain betweenness).

---

## 4. Why an ISRO scientist trusts this (the trust checklist)

1. **Uses ISRO's own products** — Cartosat-3, LISS-IV, Bhuvan flood hazard, NRSC NDEM,
   RISAT footprints. Direct **NNRMS mandate** alignment (PS4's framing).
2. **Reproduces observed reality** — replays the 2015 Chennai flood that NRSC captured,
   not an invented scenario.
3. **Multi-hazard, exposure-weighted** — exactly how NRSC does real risk assessment
   (hazard × exposure × vulnerability), not toy node removal.
4. **Honest about limits** — sub-pixel resolution, OSM gaps, proprietary traffic data.
5. **Multi-sensor tasking economics** — spends scarce Cartosat-3 high-res only on
   high-criticality corridors (how ISRO actually operates).
6. **Validated** — checks the flood-order prediction against IMD rainfall + observed
   footprints for real events.

---

## 5. 30-hour feasibility (be explicit in the deck — judges check this)

| Component | Effort | Why feasible |
|---|---|---|
| Segmentation model | **pre-trained before finale** | only inference on Cartosat-3 at event |
| Hazard/exposure layers | **download static rasters** | WorldPop, seismic shp, flood hazard, IMD = ready files, overlay on CPU |
| DEM flow-accumulation | minutes | pysheds/richdem, standard, CPU |
| Composite criticality + percolation | CPU, fast | NetworkX on a city graph |
| Real-event replay | load 1 footprint + elevation sort | lightweight |
| Dashboard | already built | FastAPI + MapLibre |

The heavy ML is done beforehand; the finale work is **lightweight geospatial overlay +
graph analysis on CPU** — exactly what PS4 says runs on standard CPU. Feasible.

---

## 6. PS4 requirements we MUST cover (don't miss what they asked)

From `ps4_official_description.md`:
- ✅ Transformer architecture (SegFormer) — explicitly required.
- ✅ MST + Disjoint-Set healing with Euclidean + angular alignment — we have it.
- ✅ Betweenness, node ablation, Resilience Index (baseline/perturbed avg path).
- ✅ Connectivity loss (clDice), occlusion augmentation, multi-scale.
- ⚠️ **Seasonal + illumination robustness** — explicitly named. Cover via multi-temporal
  fusion (leaf-on/leaf-off, different sun angles) — uses ISRO revisit. Few teams do this.
- ⚠️ **Forested terrain** — heaviest occlusion; in our 29-region set; call it out.
- ⚠️ **Generative reconstruction / inpainting** — named "optional"; mention as an
  innovation lever for extreme occlusion.
- ⚠️ **Disaster realism** — floods/accidents named; our hazard-grounded simulation is
  the answer (vs arbitrary removal).

---

## 7. Honest gaps to acknowledge in the deck (builds trust)
- 10 m can't resolve lanes — multi-sensor + Cartosat-3 for detail.
- OSM incomplete in slums/rural — govt vectors + self-labeling.
- No real-time traffic (proprietary) — structural proxies (betweenness + population).
- Seasonal model not yet trained — design presented, validation pending.

---

## Sources (verified)
- NRSC/Bhuvan disaster & flood hazard: https://bhuvan-app1.nrsc.gov.in/disaster/disaster.php ; https://ndem.nrsc.gov.in/hydrological_fhz.php
- Flow accumulation (flood provenance): https://atlas.co/gis-use-cases/flow-accumulation/
- BIS seismic zones (open shapefile): https://www.data.gov.in/resource/shape-file-seismic-zones ; https://en.wikipedia.org/wiki/Earthquake_zones_of_India
- WorldPop India density: https://hub.worldpop.org/geodata/summary?id=41746 ; GHSL: https://human-settlement.emergency.copernicus.eu/ghs_pop.php
- IMD gridded rainfall 1901–2024: https://www.imdpune.gov.in/cmpg/Griddata/Rainfall_25_NetCDF.html ; tool: https://github.com/prajeeshag/imddata
- SAM auto-labeling: ALPS https://arxiv.org/pdf/2406.10855 ; SAM2-ELNet https://arxiv.org/pdf/2503.12404 ; GeoSAM https://arxiv.org/pdf/2311.11319
- Hackathon-winning strategy: see separate research (SIH winners, NASA Space Apps).
