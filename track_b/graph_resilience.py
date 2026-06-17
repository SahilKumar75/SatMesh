"""
PS4 — Route Resilience: Day-1 data check + graph-half proof of concept.

What this does (run on your own machine with internet):
  1. Downloads a real road network for a city patch from OpenStreetMap (free, no login).
  2. Confirms it loads as a GRAPH: intersections = nodes, road segments = edges.
  3. Computes betweenness centrality -> the "critical intersection" score (PS4 objective 3).
  4. Runs a tiny node-removal "stress test" and a Resilience Index (PS4 objective 4).
  5. Saves a figure you can drop straight into the proposal.

This is the entire graph-theory half of PS4 in ~40 lines — proof it's tractable.
The CV half (extracting roads from satellite imagery) is the other, parallel track.

Setup (once):
    pip install osmnx networkx matplotlib
Run:
    python ps4_data_check.py
"""

import time
import osmnx as ox
import networkx as nx

# ---- 1. Pick a study area (Bengaluru city centre by default) ----
CITY_POINT = (12.9716, 77.5946)   # (lat, lon) — central Bengaluru
RADIUS_M = 1500                    # start small; increase once it works

print(f"Downloading drivable roads within {RADIUS_M} m of {CITY_POINT} ...")
t0 = time.time()
G = ox.graph_from_point(CITY_POINT, dist=RADIUS_M, network_type="drive")
print(f"  done in {time.time()-t0:.1f}s")

# ---- 2. Confirm graph structure ----
n_nodes = G.number_of_nodes()
n_edges = G.number_of_edges()
road_km = sum(d.get("length", 0) for _, _, d in G.edges(data=True)) / 1000
print(f"  intersections (nodes): {n_nodes}")
print(f"  road segments (edges): {n_edges}")
print(f"  total road length:     {road_km:.1f} km")

# ---- 3. Betweenness centrality = 'gatekeeper / critical intersection' score ----
print("Computing betweenness centrality (the critical-intersection score)...")
Gu = nx.Graph(G)  # undirected simplification for the demo
k = min(300, n_nodes)  # sample for speed on bigger graphs
bc = nx.betweenness_centrality(Gu, weight="length", k=k, seed=1)
top5 = sorted(bc.items(), key=lambda x: -x[1])[:5]
print("  Top 5 critical intersections (node : score : lat,lon):")
for nid, score in top5:
    nd = G.nodes[nid]
    print(f"    {nid}  {score:.3f}  ({nd['y']:.4f}, {nd['x']:.4f})")

# ---- 4. Stress test: remove the #1 critical node, measure the damage ----
def avg_shortest_path_len(graph):
    # average over the largest connected component
    comp = max(nx.connected_components(graph), key=len)
    H = graph.subgraph(comp)
    return nx.average_shortest_path_length(H, weight="length")

base = avg_shortest_path_len(Gu)
worst_node = top5[0][0]
Gcut = Gu.copy()
Gcut.remove_node(worst_node)
after = avg_shortest_path_len(Gcut)
resilience_index = base / after   # mentors' definition: baseline / perturbed
print("Stress test — disable the single most critical intersection:")
print(f"  avg trip length before: {base:.0f} m")
print(f"  avg trip length after:  {after:.0f} m")
print(f"  Resilience Index (baseline/perturbed): {resilience_index:.3f}  "
      f"(<1 means the network got worse)")

# ---- 5. Save a figure for the proposal ----
out = "ps4_bengaluru_roadgraph.png"
fig, ax = ox.plot_graph(
    G, node_size=5, edge_linewidth=0.6, show=False, close=True,
    bgcolor="white", node_color="#1f77b4", edge_color="#999999",
)
fig.savefig(out, dpi=150, bbox_inches="tight")
print(f"Saved figure: {out}")
print("\nIf you see numbers and a PNG, the graph half is GO. "
      "Next: the CV half — load a Sentinel-2 tile of the same area.")
