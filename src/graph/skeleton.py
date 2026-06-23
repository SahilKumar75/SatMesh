import numpy as np
import networkx as nx
import cv2
from scipy.ndimage import convolve
from skimage.morphology import skeletonize

_NEIGHBOUR_KERNEL = np.array([[1,1,1],[1,0,1],[1,1,1]], dtype=np.uint8)
_8CONN = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]


def skeletonize_mask(mask_path: str) -> np.ndarray:
    raw = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    if raw is None:
        raise FileNotFoundError(mask_path)
    return skeletonize(raw > 127).astype(np.uint8) * 255


def _node_labels(skel: np.ndarray):
    """Label clusters of junction/endpoint pixels. skeletonize leaves multi-pixel
    blobs at junctions, so adjacent node-pixels are merged into one node via 8-conn
    connected components. Returns (labels, num); labels>0 marks node pixels and the
    node index is label-1."""
    on = (skel > 0).astype(np.uint8)
    nc = convolve(on, _NEIGHBOUR_KERNEL, mode="constant", cval=0)
    nm = (on & ((nc == 1) | (nc >= 3))).astype(np.uint8)
    num, labels = cv2.connectedComponents(nm, connectivity=8)
    return labels, num


def extract_nodes(skel: np.ndarray) -> np.ndarray:
    """One node per junction/endpoint cluster, positioned at the cluster centroid.
    Order matches cluster label order so indices align with trace_edges."""
    labels, num = _node_labels(skel)
    centroids = []
    for lab in range(1, num):
        rs, cs = np.where(labels == lab)
        centroids.append((int(round(rs.mean())), int(round(cs.mean()))))
    return np.array(centroids, dtype=int).reshape(-1, 2)


def trace_edges(skel, node_positions=None):
    """Trace skeleton arms between node clusters. node_positions is accepted for
    API compatibility but clustering is recomputed from skel so edge indices line
    up with extract_nodes. Adjacent clusters (touching, no arm between) are linked
    directly so dense junctions stay connected."""
    h, w = skel.shape
    on = skel > 0
    labels, num = _node_labels(skel)
    nodepix = labels > 0

    edges = []
    seen = set()

    def add_edge(a, b, length):
        if a == b:
            return
        key = (min(a, b), max(a, b))
        if key not in seen:
            seen.add(key)
            edges.append((a, b, length))

    def walk(r, c, pr, pc, origin):
        """Walk along non-node skeleton pixels until reaching another cluster."""
        length = 1
        local = {(r, c)}
        while True:
            node_hit = None
            cont = None
            for dr, dc in _8CONN:
                nr, nc_ = r + dr, c + dc
                if not (0 <= nr < h and 0 <= nc_ < w) or not on[nr, nc_]:
                    continue
                if (nr, nc_) == (pr, pc):
                    continue
                if nodepix[nr, nc_]:
                    node_hit = (nr, nc_)
                    break
                if (nr, nc_) not in local and cont is None:
                    cont = (nr, nc_)
            if node_hit is not None:
                add_edge(origin, labels[node_hit] - 1, length + 1)
                return
            if cont is None:
                return
            pr, pc = r, c
            r, c = cont
            local.add((r, c))
            length += 1

    rows, cols = np.where(nodepix)
    for r, c in zip(rows.tolist(), cols.tolist()):
        origin = labels[r, c] - 1
        for dr, dc in _8CONN:
            nr, nc_ = r + dr, c + dc
            if not (0 <= nr < h and 0 <= nc_ < w) or not on[nr, nc_]:
                continue
            if nodepix[nr, nc_]:
                add_edge(origin, labels[nr, nc_] - 1, 1)   # touching clusters
            else:
                walk(nr, nc_, r, c, origin)
    return edges


def build_skeleton_graph(node_positions, edges, pixel_m=0.5):
    G = nx.Graph()
    for i, (r, c) in enumerate(node_positions):
        G.add_node(i, row=int(r), col=int(c),
                   y=float(r)*pixel_m, x=float(c)*pixel_m)
    for ni, nj, px in edges:
        G.add_edge(ni, nj, length=float(px)*pixel_m, synthetic=False)
    return G


def tag_node_roles(G):
    """Tag each node by its topological role from its degree, so the graph carries
    explicit "where a road joins / ends" labels (a PS4 expected output):
      endpoint = degree 1 (road termination), junction = degree >= 3 (intersection),
      through  = degree 2 (mid-segment). Call after healing so synthetic bridges count.
    """
    for n in G.nodes:
        d = G.degree(n)
        G.nodes[n]["role"] = "endpoint" if d == 1 else ("junction" if d >= 3 else "through")
    return G
