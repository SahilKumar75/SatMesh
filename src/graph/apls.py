import numpy as np
import networkx as nx
from scipy.spatial import cKDTree


def align_graphs(G_pred, G_osm, match_radius_m=20.0):
    pred_nodes = [n for n, d in G_pred.nodes(data=True) if "lat" in d]
    osm_nodes  = [n for n, d in G_osm.nodes(data=True)]

    pred_coords = np.array([[G_pred.nodes[n]["lat"], G_pred.nodes[n]["lon"]] for n in pred_nodes])
    osm_coords  = np.array([[G_osm.nodes[n].get("y", 0), G_osm.nodes[n].get("x", 0)] for n in osm_nodes])

    if len(pred_coords) == 0 or len(osm_coords) == 0:
        return {}

    tree = cKDTree(pred_coords)
    radius_deg = match_radius_m / 111_000.0
    alignment = {}
    for i, on in enumerate(osm_nodes):
        dist, idx = tree.query(osm_coords[i], distance_upper_bound=radius_deg)
        if dist < radius_deg:
            alignment[on] = pred_nodes[idx]
    return alignment


def _path_length(G, src, dst, weight="length"):
    try:
        return nx.shortest_path_length(G, src, dst, weight=weight)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None


def compute_apls(G_pred, G_osm, n_samples=200, seed=42):
    rng = np.random.default_rng(seed)
    alignment = align_graphs(G_pred, G_osm)
    if len(alignment) < 2:
        return 0.0

    osm_nodes = list(alignment.keys())
    if len(osm_nodes) < 2:
        return 0.0

    pairs = []
    osm_arr = np.array(osm_nodes)
    for _ in range(n_samples):
        i, j = rng.choice(len(osm_arr), size=2, replace=False)
        pairs.append((osm_arr[i], osm_arr[j]))

    scores = []
    for s, t in pairs:
        gt_len = _path_length(G_osm, s, t, weight="length")
        if gt_len is None or gt_len == 0:
            continue
        ps, pt = alignment.get(s), alignment.get(t)
        if ps is None or pt is None:
            scores.append(0.0)
            continue
        pred_len = _path_length(G_pred, ps, pt, weight="length")
        if pred_len is None:
            scores.append(0.0)
        else:
            scores.append(max(0.0, 1.0 - abs(gt_len - pred_len) / gt_len))

    return float(np.mean(scores)) if scores else 0.0
