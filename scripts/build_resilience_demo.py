#!/usr/bin/env python3
"""Build a REAL Bengaluru flood-resilience dataset for the dashboard demo.

No model, no GPU — this is the graph/resilience half (50% of PS4) on REAL data:
- real OSM drive network for central Bengaluru (osmnx)
- real per-node elevation from AWS Terrarium terrain tiles (free, no key)
- betweenness centrality = PS4 "Criticality Worth"
- flood simulation: water rises by elevation, low roads submerge, network fragments
  -> connectivity / global-efficiency / resilience curve
- gatekeeper + flood-critical nodes

Exports outputs/bengaluru_real/resilience.json for the dashboard (nodes carry
elevation + criticality so the front-end can run the flood slider live).

Run on a machine with internet:  python scripts/build_resilience_demo.py
"""
import io
import json
import math
import sys
from pathlib import Path

import numpy as np

# central Bengaluru — recognizable core (MG Road / Cubbon / Majestic / Lalbagh)
BBOX = [12.955, 77.560, 13.010, 77.620]   # south, west, north, east
OUT = Path("outputs/bengaluru_real")
TERRARIUM = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"


def deg2tile_frac(lat, lon, z):
    n = 2 ** z
    xt = (lon + 180.0) / 360.0 * n
    yt = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
    return xt, yt


def build_elevation_sampler(bbox, z=13):
    """Fetch + stitch Terrarium tiles for bbox; return sampler(lat,lon)->metres."""
    import urllib.request
    import cv2
    south, west, north, east = bbox
    x0, y0 = deg2tile_frac(north, west, z)
    x1, y1 = deg2tile_frac(south, east, z)
    xt0, xt1 = int(math.floor(min(x0, x1))), int(math.floor(max(x0, x1)))
    yt0, yt1 = int(math.floor(min(y0, y1))), int(math.floor(max(y0, y1)))
    tiles = {}
    for xt in range(xt0, xt1 + 1):
        for yt in range(yt0, yt1 + 1):
            try:
                data = urllib.request.urlopen(
                    TERRARIUM.format(z=z, x=xt, y=yt), timeout=25).read()
                bgr = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
                r = bgr[:, :, 2].astype(np.float64)
                g = bgr[:, :, 1].astype(np.float64)
                b = bgr[:, :, 0].astype(np.float64)
                tiles[(xt, yt)] = (r * 256 + g + b / 256) - 32768  # terrarium decode
            except Exception as e:
                print(f"  elev tile {xt},{yt} failed: {e}")
                tiles[(xt, yt)] = None

    def sample(lat, lon):
        xf, yf = deg2tile_frac(lat, lon, z)
        xt, yt = int(math.floor(xf)), int(math.floor(yf))
        t = tiles.get((xt, yt))
        if t is None:
            return None
        px = min(255, max(0, int((xf - xt) * 256)))
        py = min(255, max(0, int((yf - yt) * 256)))
        return float(t[py, px])
    return sample


def main():
    import osmnx as ox
    import networkx as nx
    OUT.mkdir(parents=True, exist_ok=True)
    south, west, north, east = BBOX

    print("Fetching real OSM drive network for central Bengaluru...")
    Gd = ox.graph_from_bbox(bbox=(west, south, east, north), network_type="drive")
    G = nx.Graph()  # undirected simple graph for analysis
    for n, d in Gd.nodes(data=True):
        G.add_node(n, lat=d["y"], lon=d["x"])
    for u, v, d in Gd.edges(data=True):
        ln = float(d.get("length", 1.0))
        if G.has_edge(u, v):
            if ln < G[u][v]["length"]:
                G[u][v]["length"] = ln
        else:
            geom = d.get("geometry")
            coords = ([[float(x), float(y)] for x, y in geom.coords] if geom is not None
                      else [[G.nodes[u]["lon"], G.nodes[u]["lat"]],
                            [G.nodes[v]["lon"], G.nodes[v]["lat"]]])
            G.add_edge(u, v, length=ln, coords=coords)
    # keep the largest connected component (clean baseline)
    G = G.subgraph(max(nx.connected_components(G), key=len)).copy()
    print(f"  graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    print("Sampling real elevation (Terrarium tiles)...")
    samp = build_elevation_sampler(BBOX)
    elevs = []
    for n, d in G.nodes(data=True):
        e = samp(d["lat"], d["lon"])
        d["elev"] = e if e is not None else 0.0
        elevs.append(d["elev"])
    elevs = np.array(elevs)
    print(f"  elevation range: {elevs.min():.0f}–{elevs.max():.0f} m")

    print("Computing betweenness centrality (Criticality Worth)...")
    bc = nx.betweenness_centrality(G, weight="length", k=min(400, G.number_of_nodes()),
                                   seed=42)
    bmax = max(bc.values()) or 1.0
    for n, d in G.nodes(data=True):
        d["crit"] = bc[n] / bmax

    n_total = G.number_of_nodes()

    # Global efficiency normalized by the ORIGINAL node set: pairs that become
    # unreachable after flooding contribute 0, so efficiency (and the resilience
    # ratio) decreases monotonically as the network fragments — the correct PS4
    # behaviour (lower R = more vulnerable). Averaging only over surviving pairs
    # would wrongly rise as the graph shrinks to its well-connected core.
    def efficiency(graph, n_full):
        if graph.number_of_nodes() < 2 or n_full < 2:
            return 0.0
        import random
        random.seed(1)
        nodes = list(graph.nodes())
        srcs = random.sample(nodes, min(120, len(nodes)))
        tot = 0.0
        for s in srcs:
            lengths = nx.single_source_dijkstra_path_length(graph, s, weight="length")
            tot += sum(1.0 / dist for t, dist in lengths.items() if t != s and dist > 0)
        return (tot / len(srcs)) / (n_full - 1)

    base_eff = efficiency(G, n_total)

    print("Running flood simulation (rising water by elevation)...")
    lo, hi = float(np.percentile(elevs, 2)), float(np.percentile(elevs, 85))
    levels = np.linspace(lo, hi, 14)
    flood_curve = []
    for lvl in levels:
        keep = [n for n, d in G.nodes(data=True) if d["elev"] > lvl]
        sub = G.subgraph(keep)
        if sub.number_of_nodes() == 0:
            lcc = 0
        else:
            lcc = len(max(nx.connected_components(sub), key=len, default=[]))
        flooded_frac = 1 - len(keep) / n_total
        lcc_frac = lcc / n_total
        eff = efficiency(sub, n_total) if sub.number_of_nodes() > 1 else 0.0
        resilience = eff / base_eff if base_eff else 0.0
        flood_curve.append({"level_m": round(float(lvl), 1),
                            "flooded_frac": round(flooded_frac, 3),
                            "lcc_frac": round(lcc_frac, 3),
                            "resilience": round(resilience, 3)})

    # gatekeepers + flood-critical (low elevation AND high criticality)
    nodes_sorted = sorted(G.nodes(data=True), key=lambda kv: kv[1]["crit"], reverse=True)
    gatekeepers = [n for n, _ in nodes_sorted[:12]]
    elev_thresh = float(np.percentile(elevs, 25))
    flood_critical = [n for n, d in G.nodes(data=True)
                      if d["elev"] <= elev_thresh and d["crit"] >= 0.4]

    nodes_out = [{"id": int(n), "lat": round(d["lat"], 6), "lon": round(d["lon"], 6),
                  "elev": round(d["elev"], 1), "crit": round(d["crit"], 4),
                  "gatekeeper": n in set(gatekeepers),
                  "flood_critical": n in set(flood_critical)}
                 for n, d in G.nodes(data=True)]
    edges_out = [{"s": int(u), "t": int(v), "len": round(d["length"], 1),
                  "coords": d["coords"]} for u, v, d in G.edges(data=True)]

    out = {
        "city": "Bengaluru (central core)",
        "bbox": BBOX,
        "source": "OpenStreetMap (drive network) + AWS Terrarium SRTM elevation",
        "metrics": {
            "n_nodes": n_total, "n_edges": G.number_of_edges(),
            "elev_min_m": round(float(elevs.min()), 1),
            "elev_max_m": round(float(elevs.max()), 1),
            "baseline_efficiency": round(base_eff, 6),
            "gatekeeper_count": len(gatekeepers),
            "flood_critical_count": len(flood_critical),
        },
        "flood_curve": flood_curve,
        "gatekeepers": [int(n) for n in gatekeepers],
        "nodes": nodes_out,
        "edges": edges_out,
    }
    path = OUT / "resilience.json"
    with open(path, "w") as f:
        json.dump(out, f)
    print(f"\nDONE -> {path}  ({path.stat().st_size//1024} KB)")
    print(f"  {n_total} real nodes, {G.number_of_edges()} real edges, "
          f"{len(flood_critical)} flood-critical, {len(gatekeepers)} gatekeepers")


if __name__ == "__main__":
    sys.exit(main())
