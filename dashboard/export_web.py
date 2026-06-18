"""
dashboard/export_web.py — export the healed graph + criticality into a single
JS data file the custom web dashboard loads (no server / CORS needed).

Usage:
    python dashboard/export_web.py
    python dashboard/export_web.py --graph outputs/trackb/healed_graph.gpickle \\
        --criticality outputs/trackb/criticality.json --out dashboard/web/data.js
"""

from __future__ import annotations
import argparse, json, os, pickle, sys

import numpy as np
import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CITY_CENTER = (12.9716, 77.5946)   # Bengaluru (matches the PS4 wireframe)
CITY_SPAN_DEG = 0.045              # ~5 km tile


def geo_project(G):
    nodes = list(G.nodes)
    lats = np.array([G.nodes[n].get("lat", np.nan) for n in nodes])
    if np.all(np.isfinite(lats)) and np.nanmax(np.abs(lats)) <= 90:
        return {n: (float(G.nodes[n]["lat"]), float(G.nodes[n]["lon"])) for n in nodes}
    rows = np.array([G.nodes[n].get("row", G.nodes[n].get("y", 0)) for n in nodes], float)
    cols = np.array([G.nodes[n].get("col", G.nodes[n].get("x", 0)) for n in nodes], float)
    r0, r1, c0, c1 = rows.min(), rows.max(), cols.min(), cols.max()
    rr = (rows - r0) / (r1 - r0 + 1e-9)
    cc = (cols - c0) / (c1 - c0 + 1e-9)
    lat = CITY_CENTER[0] + CITY_SPAN_DEG * (0.5 - rr)
    lon = CITY_CENTER[1] + CITY_SPAN_DEG * (cc - 0.5)
    return {n: (float(lat[i]), float(lon[i])) for i, n in enumerate(nodes)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph",       default="outputs/trackb/healed_graph.gpickle")
    ap.add_argument("--criticality", default="outputs/trackb/criticality.json")
    ap.add_argument("--out",         default="dashboard/web/data.js")
    args = ap.parse_args()

    with open(args.graph, "rb") as f:
        G = pickle.load(f)
    from track_b.criticality import compute_betweenness
    bc = compute_betweenness(G)
    geo = geo_project(G)

    nid = {n: i for i, n in enumerate(G.nodes)}
    nodes = [{
        "id": nid[n],
        "lat": round(geo[n][0], 6),
        "lon": round(geo[n][1], 6),
        "bc":  round(float(bc.get(n, 0.0)), 4),
        "deg": int(G.degree(n)),
    } for n in G.nodes]

    edges = [{
        "s": nid[u], "t": nid[v],
        "len": round(float(d.get("length", 1.0)), 2),
        "syn": bool(d.get("synthetic", False)),
    } for u, v, d in G.edges(data=True)]

    ranked = sorted(bc, key=bc.get, reverse=True)
    gatekeepers = [{"id": nid[n], "bc": round(float(bc[n]), 4)} for n in ranked[:12]]

    crit = {}
    if os.path.exists(args.criticality):
        with open(args.criticality) as f:
            crit = json.load(f)
    # remap ablation node_ids to the compact integer ids used here
    ablation = []
    for row in crit.get("ablation", []):
        r = dict(row)
        if r.get("node_id") is not None:
            # criticality.json node_id is the original graph node label
            orig = row["node_id"]
            r["node_id"] = nid.get(orig, orig)
        ablation.append(r)

    lcc0 = len(max(nx.connected_components(G), key=len)) if G.number_of_nodes() else 0
    payload = {
        "meta": {
            "n_nodes": G.number_of_nodes(),
            "n_edges": G.number_of_edges(),
            "synthetic_edges": sum(1 for _, _, d in G.edges(data=True) if d.get("synthetic")),
            "lcc_baseline": lcc0,
            "city": "Bengaluru",
            "center": list(CITY_CENTER),
        },
        "nodes": nodes,
        "edges": edges,
        "gatekeepers": gatekeepers,
        "ablation": ablation,
    }

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        f.write("window.SATMESH_DATA = ")
        json.dump(payload, f, separators=(",", ":"))
        f.write(";\n")
    print(f"wrote {args.out}: {len(nodes)} nodes, {len(edges)} edges, "
          f"{len(gatekeepers)} gatekeepers, {len(ablation)} ablation steps")


if __name__ == "__main__":
    main()
