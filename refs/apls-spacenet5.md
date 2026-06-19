# APLS — Average Path Length Similarity (SpaceNet 5)

**Citation.** Van Etten, A., et al. *The SpaceNet Roads Dataset / SpaceNet 5 Challenge — APLS metric.* CosmiQ Works / SpaceNet, 2018–2020.

**Core claim.** Pixel IoU rewards a map that *looks* right; routing needs a map that *connects* right. APLS scores a predicted road graph by how closely shortest-path **distances** between matched node pairs reproduce the ground-truth graph — directly measuring usefulness for navigation.

## Key equations

- For a sampled set of origin–destination pairs, compare path length in prediction (`G`) vs ground truth (`G*`):
  ```
  APLS = 1 − (1/N) Σ  min( 1, |L(a,b) − L*(a*,b*)| / L*(a*,b*) )
  ```
  where `L` is shortest-path length, `(a*,b*)` are the nodes in `G` nearest to `(a,b)` in `G*`, and a missing/unroutable pair contributes the maximal penalty `1`.

- Score ∈ `[0, 1]`; `1` = perfect topological + metric match. Snapping radius (e.g. 20 m) bounds node matching.

## What it changes in SatMesh

`src/graph/apls.py` implements `align_graphs` (nearest-node matching within `match_radius_m`) and `compute_apls` (samples O–D pairs, Dijkstra on both graphs, averages the relative-difference penalty). `eval/apls_eval.py` is the CLI for batch scoring a city's healed graph against its OSM reference. APLS is reported in `summary.json` and shown as the dashboard hero metric.

**Hard requirement it forces:** APLS needs real lat/lon on every node. That is why the pipeline carries geo-coordinates from the GeoTIFF CRS (`add_geo_coords`) instead of fake pixel grids — without real coordinates APLS is meaningless.

## Judge talking point

APLS is the metric SpaceNet 5 judged on and the one remote-sensing reviewers recognize instantly. A model can hit decent IoU and still score terribly on APLS if its topology is wrong. Reporting APLS proves our extracted *network* — not just our pixels — matches reality, tying Track A accuracy to Track B routing in one number.

See also [[cldice-cvpr2021]] (loss that optimizes for this) and [[betweenness-urban-vulnerability]] (what we compute once the graph is verified).
