# BAH 2026 — Problem Statement Scorecard (for a CV + Geospatial + AI/ML team)

Scored 1–5 (5 = best for you). "Pre-spec" = how much the mentors already handed you the recipe — **high pre-spec cuts both ways**: lower design risk, but judges benchmark you against their intended solution, so differentiation is harder.

| PS | Skill fit | Data risk (5=safe) | Competition (5=thin) | Pre-spec | Ceiling | Notes |
|---|---|---|---|---|---|---|
| **10 IR super-res + colorization** | 5 | **5** | 2 | 4 | 4 | Public Landsat-9 + official GitHub repo. Physics-informed bonus to stand out. |
| **12 Frame interpolation** | 5 | **5** | 3 | 4 | 4 | NOAA AWS + MOSDAC URLs given. Dashboard deliverable rewards presentation. |
| **2 Cloud removal (LISS-IV)** | 5 | 3 | 2 | 3 | 4 | Your core. Risk: sourcing paired cloudy/clear LISS-IV from Bhoonidhi. |
| **4 Route resilience** | 4 | 4 | 3 | 5 | **5** | Graph-criticality half is where most CV teams have nothing. 50/50 scoring. |
| **11 Cross-modal retrieval** | 4 | 3 | **4** | 4 | 4 | Metric learning. Thin crowd. Risk: paired multi-modal data not named. |
| 1 Urban heat | 4 | 3 | 1 | 3 | 3 | Most crowded statement. Hard to stand out. |
| 3 Surface AQI + HCHO | 3 | 4 | 3 | 4 | 3 | Atmospheric science tilt; two separate objectives. |
| 6 Crop / irrigation | 4 | 4 | 2 | 3 | 3 | Crowded agri-ML lane; phenology stress is the differentiator. |
| 5 Climate digital twin | 3 | 5 | 3 | 4 | 3 | Tractable if scoped to one region; overscope trap otherwise. |
| 7 Exoplanet | 2 | 5 | 4 | 4 | 4 | Clean ML problem but 1-D time-series, not imagery. |
| 8 Lunar ice | 2 | 3 | **5** | 5 | 4 | SAR polarimetry. Highest novelty, hardest data. |
| 9 Wavefront (SH-WFS) | 2 | 4 | **5** | 4 | 3 | Optics + real-time (<1 ms) bar. Needs an optics person. |
| 13 MPLS copilot | 1 | 4 | 4 | 4 | 3 | Not space-tech; networking + offline LLM. Off-domain. |
| 14 Radiation forecast | 2 | 5 | 4 | 5 | 3 | Space-weather time-series. Fully spec'd, low design risk. |
| 15 Solar flare (Aditya-L1) | 2 | 5 | 4 | 4 | 4 | Best "novelty" story (joint soft+hard X-ray). Indian-pride angle. |

## If I had to pick

**Disagree-first:** the instinct for a CV team is to grab PS10 or PS12 because they're the safest end-to-end builds. They're the right *finishing* bets, but they're also the most crowded CV lanes, so a clean solution there lands you in a large pack. If your goal is to *win*, not just finish, the safe pick and the winning pick aren't the same.

**Safest strong choice — PS10 (IR super-res + colorization).** [Likely] Lowest execution risk of all 15: public data, an official repo that hands you the exact TIR1–RGB pairing, two well-trodden CV tasks. Win condition: nail the FID/hallucination bar and attempt the **physics-informed bonus** (tie RGB prediction to thermal-emission physics) — that's the part most teams skip, and BAH clearly rewards physics-informed framing (PS1 and PS10 both flag it).

**Highest ceiling for your skills — PS4 (route resilience).** [Likely] The segmentation half is routine for you; the **graph-criticality half is worth 50% of the score and is where most CV teams have nothing**. The deck hands you the architecture (transformer → MST/Disjoint-Set graph healing → betweenness centrality → Streamlit stress-test dashboard), so design risk is low while the differentiation ceiling is high. One hard constraint: **you must bring your own GPU** for the 30-hour finale.

**Wildcard if you want a thin crowd — PS11 (cross-modal retrieval).** [Guessing on competition] Fewer teams can do shared-embedding metric learning well, and the deck gives you the full framework. Gated on one unknown: whether paired optical–SAR–multispectral data is actually provided. Verify in the proposal before betting on it.

## The one action that should decide it
[Certain] Before committing, confirm you can actually **download and load the primary dataset today**:
- PS10 → run the GitHub repo, produce one TIR1–RGB pair.
- PS12 → pull one GOES-19 ABI Ch-13 granule from the NOAA AWS bucket + one INSAT-3DS TIR1 from MOSDAC.
- PS4 → load Sentinel-2 / LISS-IV + one OSM road-vector tile.
- PS2 → find paired cloudy/clear LISS-IV scenes on Bhoonidhi (the riskiest of the four).
- PS11 → check the proposal for a named paired multi-modal dataset.

Whichever of your top picks loads end-to-end fastest is the one to write the July-1 proposal around. A great idea on a dataset you can't open loses to a decent idea that runs by demo day.
