import numpy as np
import networkx as nx
from itertools import combinations

from .skeleton import skeletonize_mask, extract_nodes, trace_edges, build_skeleton_graph


class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True

    def same(self, x, y):
        return self.find(x) == self.find(y)


def _endpoint_heading(G, node):
    nbrs = list(G.neighbors(node))
    if not nbrs:
        return np.array([0.0, 0.0])
    nbr = nbrs[0]
    ny, nx_ = G.nodes[node]["y"], G.nodes[node]["x"]
    gy, gx  = G.nodes[nbr]["y"],  G.nodes[nbr]["x"]
    vec = np.array([ny - gy, nx_ - gx], dtype=float)
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec


def heal_gaps(G, max_gap_m=50.0, angular_threshold=0.3, ndvi_mask=None):
    stubs = [n for n in G.nodes if G.degree(n) == 1]
    uf = UnionFind(max(G.nodes) + 1 if G.nodes else 1)
    for n in G.nodes:
        for nbr in G.neighbors(n):
            uf.union(n, nbr)

    G = G.copy()
    added = []

    for a, b in combinations(stubs, 2):
        if uf.same(a, b):
            continue

        ay, ax = G.nodes[a]["y"], G.nodes[a]["x"]
        by, bx = G.nodes[b]["y"], G.nodes[b]["x"]
        dy, dx = by - ay, bx - ax
        dist = float(np.hypot(dy, dx))

        effective_max_gap = max_gap_m
        if ndvi_mask is not None:
            mid_row = (G.nodes[a].get("row", ay) + G.nodes[b].get("row", by)) / 2.0
            mid_col = (G.nodes[a].get("col", ax) + G.nodes[b].get("col", bx)) / 2.0
            mr, mc = int(mid_row), int(mid_col)
            if (0 <= mr < ndvi_mask.shape[0] and 0 <= mc < ndvi_mask.shape[1]
                    and ndvi_mask[mr, mc] > 0):
                effective_max_gap = max_gap_m * 2.0

        if dist > effective_max_gap:
            continue

        ha = _endpoint_heading(G, a)
        hb = _endpoint_heading(G, b)
        bridge_dir = np.array([dy, dx], dtype=float)
        bn = np.linalg.norm(bridge_dir)
        if bn > 0:
            bridge_dir /= bn

        dot = float(np.dot(ha, bridge_dir))
        if dot > -angular_threshold:
            continue

        G.add_edge(a, b, length=dist, synthetic=True)
        uf.union(a, b)
        added.append((a, b))

    return G


def add_geo_coords(G, top_left_lat, top_left_lon, pixel_size_deg=0.0000045):
    for n, data in G.nodes(data=True):
        data["lat"] = top_left_lat - data["row"] * pixel_size_deg
        data["lon"] = top_left_lon + data["col"] * pixel_size_deg
    return G


def run_heal_pipeline(mask_path, pixel_m, top_left_lat, top_left_lon,
                      max_gap_m, angular_thr, ndvi_mask_path=None):
    import cv2

    skel = skeletonize_mask(mask_path)
    nodes = extract_nodes(skel)
    edges = trace_edges(skel, nodes)
    G_skel = build_skeleton_graph(nodes, edges, pixel_m=pixel_m)

    ndvi_mask = None
    if ndvi_mask_path is not None:
        raw = cv2.imread(ndvi_mask_path, cv2.IMREAD_GRAYSCALE)
        if raw is not None:
            ndvi_mask = raw

    G_healed = heal_gaps(G_skel, max_gap_m=max_gap_m,
                         angular_threshold=angular_thr, ndvi_mask=ndvi_mask)
    G_healed = add_geo_coords(G_healed, top_left_lat, top_left_lon)

    return G_healed, G_skel
