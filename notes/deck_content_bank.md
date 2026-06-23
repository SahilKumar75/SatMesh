# PS4 Deck Content Bank — everything for building the PPT

> Consolidated from research + strategy responses. Companions:
> `ps4_official_description.md` (the spec) and `ppt_strategy_research.md` (data layers).
> This file = winner playbook + the innovation gold + deck structure.

---

## A. How hackathon WINNERS differ (researched: SIH + NASA Space Apps)

- **Think like the judge / target the rubric.** Winners "clearly considered the judging
  criteria"; losers shoehorn an idea. PS4 is 50% extraction / 50% graph — own the graph
  half (most teams are weak there).
- **Solve a REAL pain.** Judges smell forced use-cases. Frame as disaster routing for
  Indian cities, ISRO-mission-aligned (NNRMS).
- **Strategic problem pick.** SIH 2022 winner filtered 530+ statements, avoided ones with
  weak data. Winnability over coolness.
- **Ground in a real domain expert (out-of-the-box).** SIH winner consulted a *lawyer*
  for a court-search project. Equivalent for us: real disaster/urban-planning grounding
  (Chennai 2015, Bengaluru 2022 floods).
- **Specialized roles + one presenter.** ML / backend / frontend / a dedicated deck owner.
- **Storytelling + visual-first.** NASA storytelling winner fused data + narrative +
  illustration. Narrate problem → solution → method → impact as one arc.

### The decisive insight for a PPT-only round
> **"Judges form their opinion based on the PPT *before* the prototype demo."** The deck
> carries the verdict.
> **Idea-round warning:** "Pasting a screenshot of the frontend you made can lead to
> elimination" — at the idea stage judges grade **approach + innovation**, not finished
> work. So show *how it works* (diagrams, reasoning), not a polished app screenshot.

---

## B. Winning deck structure (text + visual rules)

**Timing rule (finale):** 4 min problem · 4 min demo · 2 min impact. Most time on
problem + what it does; least on architecture.

**Idea-round deck:** ~6 slides (Hack2skill template = 10), points not paragraphs,
visual-first.

**Slide flow:**
1. Title + PS ID + Team
2. **Problem** (one para: who suffers, how often, what it costs)
3. **One-line solution** (elevator pitch)
4. **Value metrics** (what we improve, by how much)
5. **How it works** — pipeline diagram (idea round) / **demo hero shot** (finale)
6. **Architecture** — data-flow diagram
7. **Key algorithm + tradeoffs** (one each)
8. **Results / experiments**
9. **Impact + ISRO alignment + feasibility**

**Text rules:** one idea per slide; bullets/diagrams, never paragraphs; a judge gets
each slide in 5 seconds; text = captions to a self-explaining visual.

**Visual rules:** charts/diagrams/infographics > text blocks. Reuse PS4's own visual
language — green→red criticality colorbar + the 3-panel pipeline (Satellite → Extraction
→ Criticality) so the deck "speaks PS4."

---

## C. The reframe (build the whole deck on this)

> **A road under canopy is not in the pixels.** A 4 m road is sub-pixel at 10 m
> Sentinel-2 — occlusion is *information loss*, not a detection bug. Everyone else fights
> it with a bigger model. We *recover the lost information* (multi-sensor + temporal +
> topology + hazard grounding).

Claiming "92% IoU on Sentinel-2" exposes a team that doesn't understand the physics. The
team that states the limit and designs around it wins trust.

---

## D. The 5 out-of-the-box innovations (the gold)

1. **Temporal multi-pass occlusion recovery** — shadows/canopy move; ISRO satellites
   revisit. Fuse passes (different sun angles, leaf-on/leaf-off seasons) to see through
   occlusion. *Directly answers PS4's required "varying illumination and seasonal
   conditions." Uses ISRO's constellation as a time machine — few teams think of it.*

2. **Blind-Spot Index** = criticality × model-uncertainty (MC-dropout/ensemble). The
   critical road we're *least sure* exists → where to send a survey team / task
   Cartosat-3. A new, named, disaster-actionable metric.

3. **Flood-Percolation Collapse Curve** — disaster = cascade, not one node. Flood rises
   by elevation (DEM), roads close in elevation order, traffic reroutes, neighbors
   overload → collapse. Output connectivity-vs-flood-level curve. Graduate network
   science, beyond plain betweenness.

4. **Resolution-adaptive multi-sensor fusion** — Sentinel-2/LISS-IV wide for coverage;
   Cartosat-3 sub-meter only on high-criticality corridors. Designed around ISRO's real
   tasking economics.

5. **Self-improving system** — model flags low-confidence regions → priority list for
   OSM/ground verification → retrain. A living EO product, not a frozen model.

Plus **Composite Criticality** = betweenness × population-served (WorldPop) × hazard
(NRSC flood + BIS seismic) — vs betweenness alone.

---

## E. Real-world grounding = trust (the killer demo idea)

**Replay a real event:** load the observed **2015 Chennai flood footprint** (NRSC/RISAT)
→ progressively remove roads as water rises by DEM elevation → show the real network
fragment + which evacuation routes survive + people stranded (WorldPop). Reproducing
something ISRO *already observed* = instant credibility.

Layers in sync (all geo-referenced, spatial-join onto graph nodes):
imagery → road extraction → topology → **hazard+exposure join** (flood/seismic/population)
→ composite criticality → simulation (real replay + percolation) → decision dashboard.

---

## F. ISRO-scientist trust checklist
1. Uses ISRO's own products (Cartosat-3, LISS-IV, Bhuvan flood, NRSC NDEM, RISAT) — NNRMS aligned.
2. Reproduces observed reality (real flood replay).
3. Multi-hazard, exposure-weighted (how NRSC actually assesses risk).
4. Honest about limits (sub-pixel, OSM gaps, no real-time traffic).
5. Multi-sensor tasking economics.
6. Validated against IMD rainfall + observed footprints.

---

## G. PS4 requirements checklist (must visibly cover)
- ✅ Transformer (SegFormer), MST+Disjoint-Set healing (Euclid + angular), betweenness,
  node ablation, Resilience Index (baseline/perturbed avg path), connectivity loss
  (clDice), occlusion augmentation, "Criticality Worth" heatmap, click-to-disable +
  travel-time toggle.
- ⚠️ Address explicitly: **seasonal + illumination robustness**, **forested terrain**,
  **generative inpainting (optional)**, **disaster realism** (hazard-grounded).
- Eval metrics to report (official): IoU/Dice w/ Occlusion-Recall, Generalisation across
  terrains, Connectivity Ratio (post-MST), Topological Accuracy (APLS vs OSM),
  Length-Complete/Relaxed IoU (3–5 px).

---

## H. 30-hour feasibility (state it in the deck)
Heavy ML pre-trained before finale; hazard/exposure layers are downloadable static
rasters (WorldPop, BIS seismic shp, NRSC flood, IMD) → lightweight CPU overlay; DEM
flow-accumulation via pysheds (minutes); composite criticality + percolation on CPU;
dashboard already built. Matches PS4's "graph + UI run on standard CPU."

---

## I. Honest gaps to show (anti-AI-slop trust slide)
10 m can't resolve lanes (→ multi-sensor); OSM incomplete in slums/rural (→ govt vectors
+ self-labeling); no real-time traffic, it's proprietary (→ structural proxies:
betweenness + population); seasonal model designed, validation pending.
