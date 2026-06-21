import json
import numpy as np
import networkx as nx


def classify_zones(G: nx.Graph, bc: dict) -> dict:
    """Rank-based zoning: top 10% by betweenness = critical, next 30% =
    vulnerable, bottom 60% = resilient. Rank (not raw percentile thresholds)
    keeps all three zones present even when betweenness values are tied/degenerate
    (e.g. many leaf nodes with bc=0), which a >=percentile cutoff collapses."""
    nodes = list(G.nodes)
    n = len(nodes)
    if n == 0:
        return {}
    # Sort ascending by betweenness; ties broken by node id for determinism.
    order = sorted(nodes, key=lambda x: (bc.get(x, 0.0), x))
    crit_cut = int(round(n * 0.90))   # top 10%
    vuln_cut = int(round(n * 0.60))   # next 30%
    zones = {}
    for rank, node in enumerate(order):
        if rank >= crit_cut:
            zones[node] = "critical"
        elif rank >= vuln_cut:
            zones[node] = "vulnerable"
        else:
            zones[node] = "resilient"
    return zones


def zones_to_geojson(G: nx.Graph, zones: dict, bc: dict) -> dict:
    features = []
    for n, data in G.nodes(data=True):
        lat = data.get("lat", 0.0)
        lon = data.get("lon", 0.0)
        feat = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {
                "id": int(n),
                "zone": zones.get(n, "resilient"),
                "betweenness": round(float(bc.get(n, 0.0)), 6),
                "degree": int(G.degree(n)),
                "elevation_m": float(data.get("elevation_m", 0.0)),
                "flood_vulnerable": bool(data.get("flood_vulnerable", False)),
                "flood_critical": bool(
                    data.get("flood_vulnerable", False) and zones.get(n) == "critical"
                ),
            },
        }
        features.append(feat)

    edge_features = []
    for u, v, edata in G.edges(data=True):
        u_lat = G.nodes[u].get("lat", 0.0)
        u_lon = G.nodes[u].get("lon", 0.0)
        v_lat = G.nodes[v].get("lat", 0.0)
        v_lon = G.nodes[v].get("lon", 0.0)
        crit = round(float((bc.get(u, 0.0) + bc.get(v, 0.0)) / 2.0), 6)
        edge_features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": [[u_lon, u_lat], [v_lon, v_lat]]},
            "properties": {
                "u": int(u),
                "v": int(v),
                "length_m": round(float(edata.get("length", 0.0)), 2),
                "synthetic": bool(edata.get("synthetic", False)),
                "criticality_score": crit,
            },
        })

    return {
        "type": "FeatureCollection",
        "features": features + edge_features,
    }
