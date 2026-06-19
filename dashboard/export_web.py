"""
dashboard/export_web.py — export the healed graph + criticality into a single
JS data file the custom web dashboard loads (no server / CORS needed).

Usage:
    python dashboard/export_web.py
    python dashboard/export_web.py --graph outputs/trackb/healed_graph.gpickle \\
        --criticality outputs/trackb/criticality.json --out dashboard/web/data.js
"""

from __future__ import annotations
import argparse, base64, json, os, pickle, sys

import cv2
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
    ap.add_argument("--mask",        default=None,
                    help="road_mask.png from the pipeline — embedded as a Leaflet overlay")
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

    # ── Road mask overlay (embed as base64 RGBA PNG for Leaflet ImageOverlay) ──
    mask_path = args.mask
    if mask_path is None:
        # look for mask alongside the graph file
        mask_path = os.path.join(os.path.dirname(os.path.abspath(args.graph)), "road_mask.png")

    mask_image_b64 = None
    mask_bounds    = None
    if os.path.exists(mask_path):
        raw = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        if raw is not None:
            # Downscale to 256×256 to keep data.js size manageable (~10-20 KB base64)
            small = cv2.resize(raw, (256, 256), interpolation=cv2.INTER_NEAREST)
            # Render roads in iOS blue (#007AFF) on a transparent background
            rgba = np.zeros((256, 256, 4), dtype=np.uint8)
            road_px = small > 127
            rgba[:, :, 0][road_px] = 0
            rgba[:, :, 1][road_px] = 122
            rgba[:, :, 2][road_px] = 255
            rgba[:, :, 3][road_px] = 180   # semi-transparent
            _, buf = cv2.imencode(".png", rgba)
            mask_image_b64 = "data:image/png;base64," + base64.b64encode(buf).decode()
            # Derive geographic bounds from node lat/lon
            lats = [v[0] for v in geo.values()]
            lons = [v[1] for v in geo.values()]
            mask_bounds = [[min(lats), min(lons)], [max(lats), max(lons)]]
            print(f"  road mask embedded ({len(mask_image_b64)//1024} KB base64)")
    else:
        print(f"  road mask not found at {mask_path} — skipping overlay")

    lcc0 = len(max(nx.connected_components(G), key=len)) if G.number_of_nodes() else 0
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()
    n_syn   = sum(1 for _, _, d in G.edges(data=True) if d.get("synthetic"))

    # Track B rubric metrics derived from graph + ablation
    ri_after = {a["n_removed"]: a.get("resilience_index", 1.0) for a in ablation}
    eff0 = next((a.get("efficiency") for a in ablation if a["n_removed"] == 0), None)
    rubric = {
        "connectivity_ratio":   round(lcc0 / max(n_nodes, 1), 4),
        "resilience_index_0":   round(ri_after.get(0, 1.0), 4),
        "resilience_index_3":   round(ri_after[3], 4) if 3 in ri_after else None,
        "resilience_index_5":   round(ri_after[5], 4) if 5 in ri_after else None,
        "global_efficiency_0":  round(float(eff0), 6) if eff0 is not None else None,
        "gatekeeper_count":     len(gatekeepers),
        "synthetic_edges":      n_syn,
        "synthetic_edge_pct":   round(n_syn / max(n_edges, 1) * 100, 1),
        "lcc_baseline":         lcc0,
        "n_nodes":              n_nodes,
        "n_edges":              n_edges,
    }

    payload = {
        "meta": {
            "n_nodes": n_nodes,
            "n_edges": n_edges,
            "synthetic_edges": n_syn,
            "lcc_baseline": lcc0,
            "city": "Bengaluru",
            "center": list(CITY_CENTER),
            "mask_image":  mask_image_b64,   # base64 RGBA PNG or null
            "mask_bounds": mask_bounds,       # [[lat_sw, lon_sw], [lat_ne, lon_ne]] or null
        },
        "rubric": rubric,
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
