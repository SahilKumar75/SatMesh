"""
track_b/heal.py — skeleton extraction and gap healing for SatMesh.

Pipeline:
    road mask PNG
        → skeletonize (Zhang-Suen thinning)
        → extract intersection / endpoint nodes
        → trace edges along skeleton pixels
        → build NetworkX graph (edges have pixel-count length)
        → heal broken stubs (MST + Union-Find + angular alignment)
        → attach geo-coordinates
        → save as .gpickle

Usage:
    python track_b/heal.py outputs/img_road_mask.png outputs/healed.gpickle
    python track_b/heal.py outputs/img_road_mask.png outputs/healed.gpickle \\
        --pixel_m 0.25 --top_left_lat 12.98 --top_left_lon 77.58 \\
        --max_gap_m 100 --angular_threshold 0.5
"""

from __future__ import annotations
import argparse, os, pickle
import cv2
import numpy as np
import networkx as nx
from scipy.spatial import cKDTree
from scipy.ndimage import convolve
from skimage.morphology import skeletonize


# ── Union-Find ───────────────────────────────────────────────────────────────

class UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank   = [0] * n

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # path halving
            x = self.parent[x]
        return x

    def union(self, x: int, y: int) -> bool:
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True

    def same(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)


# ── Skeletonise ──────────────────────────────────────────────────────────────

def skeletonize_mask(mask_path: str) -> np.ndarray:
    """
    Load a binary road mask and return its 1-pixel-wide skeleton (uint8, 0/255).
    """
    raw = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    if raw is None:
        raise FileNotFoundError(mask_path)
    binary = (raw > 127)
    skel   = skeletonize(binary)
    return skel.astype(np.uint8) * 255


# ── Node extraction ──────────────────────────────────────────────────────────

_NEIGHBOUR_KERNEL = np.array([[1, 1, 1],
                               [1, 0, 1],
                               [1, 1, 1]], dtype=np.uint8)


def extract_nodes(skel: np.ndarray) -> np.ndarray:
    """
    Return (N, 2) array of [row, col] node positions.
    A skeleton pixel is a node if it is an endpoint (1 neighbour) or
    an intersection (3+ neighbours).
    """
    on_skel  = (skel > 0).astype(np.uint8)
    n_count  = convolve(on_skel, _NEIGHBOUR_KERNEL, mode="constant", cval=0)
    node_map = on_skel & ((n_count == 1) | (n_count >= 3))
    rows, cols = np.where(node_map)
    return np.column_stack([rows, cols])


# ── Edge tracing ─────────────────────────────────────────────────────────────

_8CONN = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]


def trace_edges(
    skel: np.ndarray,
    node_positions: np.ndarray,
) -> list[tuple[int, int, int]]:
    """
    DFS from each node along skeleton pixels to the next node.
    Returns list of (node_i, node_j, pixel_count) — undirected.
    """
    h, w    = skel.shape
    on_skel = skel > 0

    node_idx: dict[tuple[int, int], int] = {
        (int(r), int(c)): i for i, (r, c) in enumerate(node_positions)
    }

    edges: list[tuple[int, int, int]] = []
    visited_edges: set[tuple[int, int]] = set()

    def dfs(start_r: int, start_c: int, prev_r: int, prev_c: int,
            origin: int) -> None:
        r, c, length = start_r, start_c, 1
        while True:
            if (r, c) in node_idx and length > 1:
                dest = node_idx[(r, c)]
                key  = (min(origin, dest), max(origin, dest))
                if key not in visited_edges:
                    visited_edges.add(key)
                    edges.append((origin, dest, length))
                return
            found_next = False
            for dr, dc in _8CONN:
                nr, nc = r + dr, c + dc
                if 0 <= nr < h and 0 <= nc < w and on_skel[nr, nc]:
                    if nr == prev_r and nc == prev_c:
                        continue
                    prev_r, prev_c = r, c
                    r, c = nr, nc
                    length += 1
                    found_next = True
                    break
            if not found_next:
                return   # dead end with no destination node

    for i, (nr, nc) in enumerate(node_positions):
        nr, nc = int(nr), int(nc)
        for dr, dc in _8CONN:
            r2, c2 = nr + dr, nc + dc
            if 0 <= r2 < h and 0 <= c2 < w and on_skel[r2, c2]:
                if (r2, c2) not in node_idx:
                    dfs(r2, c2, nr, nc, i)

    return edges


# ── Build graph ───────────────────────────────────────────────────────────────

def build_skeleton_graph(
    node_positions: np.ndarray,
    edges: list[tuple[int, int, int]],
    pixel_size_m: float = 0.5,
) -> nx.Graph:
    G = nx.Graph()
    for i, (r, c) in enumerate(node_positions):
        G.add_node(i, row=int(r), col=int(c),
                   y=float(r) * pixel_size_m, x=float(c) * pixel_size_m)
    for ni, nj, px in edges:
        G.add_edge(ni, nj, length=float(px) * pixel_size_m, synthetic=False)
    return G


# ── Gap healing ───────────────────────────────────────────────────────────────

def _endpoint_heading(G: nx.Graph, node: int) -> np.ndarray:
    """Unit vector pointing from the node's single neighbour toward the node."""
    nbrs = list(G.neighbors(node))
    if not nbrs:
        return np.array([0.0, 0.0])
    nbr = nbrs[0]
    ny, nx_ = G.nodes[node]["y"], G.nodes[node]["x"]
    gy, gx  = G.nodes[nbr]["y"],  G.nodes[nbr]["x"]
    vec = np.array([ny - gy, nx_ - gx], dtype=float)
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else vec


def heal_gaps(
    G: nx.Graph,
    max_gap_m: float = 50.0,
    angular_threshold: float = 0.7,
) -> nx.Graph:
    """
    Bridge broken road stubs using MST ordering + Union-Find cycle check
    + angular alignment (dot product of outward headings).

    A bridge is added when:
    1. The two endpoints are NOT already in the same connected component.
    2. Their outward heading vectors have dot product < -angular_threshold
       (i.e. they point toward each other).
    """
    G = G.copy()
    endpoints = [n for n in G.nodes if G.degree(n) == 1]
    if len(endpoints) < 2:
        return G

    coords = np.array([[G.nodes[n]["y"], G.nodes[n]["x"]] for n in endpoints])
    tree   = cKDTree(coords)

    # initialise UF over all nodes
    node_list = list(G.nodes)
    node_to_idx = {n: i for i, n in enumerate(node_list)}
    uf = UnionFind(len(node_list))
    for u, v in G.edges():
        uf.union(node_to_idx[u], node_to_idx[v])

    pairs = tree.query_pairs(r=max_gap_m)
    # sort by distance (Kruskal ordering — shortest bridges first)
    sorted_pairs = sorted(
        pairs,
        key=lambda p: float(np.linalg.norm(coords[p[0]] - coords[p[1]]))
    )

    for pi, pj in sorted_pairs:
        ni, nj = endpoints[pi], endpoints[pj]
        if uf.same(node_to_idx[ni], node_to_idx[nj]):
            continue

        hi = _endpoint_heading(G, ni)
        hj = _endpoint_heading(G, nj)
        dot = float(np.dot(hi, hj))
        if dot > -angular_threshold:
            continue   # stubs do not point toward each other

        dist = float(np.linalg.norm(coords[pi] - coords[pj]))
        G.add_edge(ni, nj, length=dist, synthetic=True)
        uf.union(node_to_idx[ni], node_to_idx[nj])

    return G


# ── Geo-coordinates ───────────────────────────────────────────────────────────

def add_geo_coords(
    G: nx.Graph,
    top_left_lat: float,
    top_left_lon: float,
    pixel_size_deg: float = 0.0000045,
) -> nx.Graph:
    """
    Attach lat/lon to every node based on pixel row/col and image top-left corner.
    Default pixel_size_deg ≈ 0.5 m at equator.
    """
    for n, data in G.nodes(data=True):
        data["lat"] = top_left_lat - data["row"] * pixel_size_deg
        data["lon"] = top_left_lon + data["col"] * pixel_size_deg
    return G


# ── Pipeline runner ───────────────────────────────────────────────────────────

def run_heal_pipeline(
    mask_path:      str,
    output_path:    str,
    pixel_m:        float = 0.5,
    top_left_lat:   float = 0.0,
    top_left_lon:   float = 0.0,
    max_gap_m:      float = 50.0,
    angular_thr:    float = 0.7,
    return_skeleton: bool = False,
) -> "nx.Graph | tuple[nx.Graph, nx.Graph]":
    """
    Run the skeleton→heal pipeline.

    When return_skeleton=True returns (G_healed, G_skeleton) so callers can
    compute connectivity_ratio correctly (healed vs pre-heal skeleton).
    Default False keeps the old single-return signature for backwards compat.
    """
    print(f"[heal] skeletonising {mask_path} ...")
    skel  = skeletonize_mask(mask_path)
    nodes = extract_nodes(skel)
    print(f"[heal] {len(nodes)} nodes extracted")

    edges = trace_edges(skel, nodes)
    print(f"[heal] {len(edges)} edges traced")

    G_skeleton = build_skeleton_graph(nodes, edges, pixel_m)
    print(f"[heal] graph: {G_skeleton.number_of_nodes()} nodes, {G_skeleton.number_of_edges()} edges")

    lcc_before = max((len(c) for c in nx.connected_components(G_skeleton)), default=0)
    G_healed = heal_gaps(G_skeleton.copy(), max_gap_m=max_gap_m, angular_threshold=angular_thr)
    lcc_after  = max((len(c) for c in nx.connected_components(G_healed)), default=0)
    new_edges   = sum(1 for _, _, d in G_healed.edges(data=True) if d.get("synthetic"))
    print(f"[heal] {new_edges} synthetic edges added  "
          f"| LCC {lcc_before} → {lcc_after} nodes")

    if top_left_lat != 0.0 or top_left_lon != 0.0:
        G_healed = add_geo_coords(G_healed, top_left_lat, top_left_lon)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "wb") as f:
        pickle.dump(G_healed, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"[heal] saved → {output_path}")

    if return_skeleton:
        return G_healed, G_skeleton
    return G_healed


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="SatMesh skeleton heal pipeline")
    parser.add_argument("mask",        help="Input road mask PNG (0/255)")
    parser.add_argument("output",      help="Output .gpickle path")
    parser.add_argument("--pixel_m",         type=float, default=0.5,
                        help="Pixel size in metres (0.5 for DeepGlobe, 0.25 for Cartosat-3)")
    parser.add_argument("--top_left_lat",    type=float, default=0.0)
    parser.add_argument("--top_left_lon",    type=float, default=0.0)
    parser.add_argument("--max_gap_m",       type=float, default=50.0,
                        help="Max distance (m) to bridge between stub endpoints")
    parser.add_argument("--angular_threshold", type=float, default=0.7,
                        help="Dot-product threshold for angular alignment check")
    args = parser.parse_args()

    run_heal_pipeline(
        args.mask, args.output,
        pixel_m=args.pixel_m,
        top_left_lat=args.top_left_lat,
        top_left_lon=args.top_left_lon,
        max_gap_m=args.max_gap_m,
        angular_thr=args.angular_threshold,
    )


if __name__ == "__main__":
    main()
