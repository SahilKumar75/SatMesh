# Top-4 Head-to-Head — for a CV + Geospatial + AI/ML team

Your shortlist: **PS4 Route Resilience · PS8 Lunar Ice · PS10 Infrared colorization · PS11 Cross-Modal Retrieval**

Scored 1–5 (5 = best for you). "Pre-spec" high = lower design risk but harder to out-differentiate (you're benchmarked against the mentors' intended solution).

| Dimension | PS4 Route Resilience | PS8 Lunar Ice | PS10 Infrared | PS11 Cross-Modal |
|---|---|---|---|---|
| **Skill fit (your team)** | 4.5 — segmentation core + graph (learnable) | **2 — radar polarimetry, not CV** | 5 — pure CV | 4 — metric/representation learning |
| **Data accessibility** | 4 — Sentinel-2/LISS-IV/OSM public; Cartosat-3 at finale | 3 — given 1 crater's DFSAR at finale; specialized | **5 — Landsat + official GitHub repo** | 3 — needs paired optical/SAR; dataset not named |
| **Competition (thin=good)** | 3.5 — popular, but few do the graph half | **5 — thinnest crowd** | 2.5 — crowded (approachable CV) | 4 — thin-ish |
| **Differentiation ceiling** | 4.5 — graph half = 50% of score, your moat | 3.5 — high prestige, capped by radar gap | 3.5 — physics-informed + semantic bonus | 4 — cross-modal weighted higher |
| **30-hr finale feasibility** | **5 — mentors designed it for parallel 2-team workflow** | 2.5 — radar + path + volume in 30h is a lot | 5 — two known CV tasks | 4 — buildable if data sorted |
| **Demo "wow" for ISRO judges** | **5 — click a node, watch the city reroute** | 4.5 — Moon/ISRU narrative | 3.5 — before/after colorized tiles | 3 — retrieval ranking, less visual |
| **Hidden constraints** | Bring your own GPU | Needs SAR expertise | Website thinner than SAC deck | Must verify paired dataset exists |

## Ranking for your team
1. **PS4 Route Resilience** — best expected value.
2. **PS11 Cross-Modal Retrieval** — best if you want a thinner crowd.
3. **PS10 Infrared** — safest to finish; strong fallback / second-team project.
4. **PS8 Lunar Ice** — highest prestige, but skill-mismatched; only with a radar teammate.

## Recommendation: PS4 (Route Resilience)

[Likely] It wins on the combination that matters: **high skill fit + a built-in moat + a demo judges remember + a structure literally designed for 30 hours.**

- **The moat:** scoring is **50% road extraction / 50% graph-theoretic resilience**. Every CV team can do the segmentation half; almost none will do the graph half well. That's where you separate, and it's half the marks. The mentors even defined the **Resilience Index** (baseline ÷ perturbed shortest-path length) so the target is unambiguous.
- **Built for the finale:** the official text recommends a **parallel two-team workflow** — one builds the segmentation model while the other builds graph-healing + ablation on OSM/mock baselines. That de-risks the 30 hours more than any other pick.
- **The pitch:** an interactive Streamlit/Leaflet dashboard where a planner disables an intersection and instantly sees the city reroute and travel-time spike. National-impact framing is ready-made (NNRMS, MeitY, disaster response).

**The honest risk:** because the deck hands you the whole recipe, PS4 will be popular and judges benchmark against the intended pipeline. Your win condition is **execution quality on the graph half + a polished dashboard**, not a novel idea.

**If you'd rather avoid the crowd:** go **PS11**. Cross-modal is weighted more heavily than same-modal, **pretrained/foundation models + FAISS are explicitly allowed** (so a small team can lean on strong pretrained encoders and compete on retrieval quality + query speed), and fewer teams do shared-embedding retrieval well. The one thing to confirm first: that a paired optical–SAR–multispectral dataset is actually provided — the website says "may include" but names none.

## The tiebreaker action (do this before writing the proposal)
[Certain] Spend 30 minutes trying to load each finalist's primary data:
- **PS4** → load a Sentinel-2 tile + an OSM road-vector tile for the same area.
- **PS11** → find a real paired multi-modal dataset (e.g. SEN1-2, BigEarthNet-MM, or DFC2023). If you can't, PS11 drops.
- **PS10** → clone the official repo, produce one TIR1–RGB pair.

Whichever of PS4 / PS11 loads cleanly *and* has its dataset confirmed is your pick. On current information, **PS4 is the front-runner.**
