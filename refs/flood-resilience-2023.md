# Rainstorm-Waterlogging Road-Network Resilience

**Citation.** *Resilience assessment of urban road networks under rainstorm waterlogging.* ScienceDirect, 2023. (Transportation/urban-resilience literature.)

**Core claim.** Flood impact on a road network is not "how many roads flood" but "how much routing function is lost" — and the worst nodes are those that are simultaneously **low-lying** (flood-exposed) and **structurally central** (high betweenness). Resilience is the ratio of post-event to pre-event network efficiency.

## Key equations

- **Network efficiency** (global):
  ```
  E(G) = 1 / (n(n-1)) · Σ_{i≠j} 1 / d(i, j)
  ```
  where `d(i,j)` is shortest-path distance; unreachable pairs contribute `0`.

- **Resilience index** under a flood scenario `F` that disables a node set:
  ```
  R = E(G_after) / E(G_before)        R ∈ [0, 1]
  ```
  Critically, **both efficiencies must be normalized by the original node count** `n`, or removing peripheral nodes can spuriously raise `E` above baseline.

## What it changes in SatMesh

- `src/graph/dem.py` attaches SRTM elevation to each node and `flood_scenario(G, threshold_m)` removes sub-threshold nodes.
- `src/graph/criticality.py:global_efficiency(G, norm_n=...)` and the API scenario normalize by the **original** `n` so `R` stays in `[0,1]` — a bug we explicitly guard against (otherwise a flood that disables 46 % of nodes reported "130 % resilience").
- The compound marker `flood_critical = (zone == critical) AND flood_vulnerable` is the paper's central insight made actionable.

## Judge talking point

Anyone can shade low-elevation roads blue. The actionable question for disaster planning is *"which flooded road severs the city's routing?"* — the intersection of low elevation and high betweenness. We compute that single set of nodes and quantify the efficiency drop. That's the flood differentiator no RGB-only, OSM-pulling team can produce.

See also [[betweenness-urban-vulnerability]] (the centrality half of the compound marker).
