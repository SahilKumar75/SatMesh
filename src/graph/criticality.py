import networkx as nx
import numpy as np


def _lcc(G):
    if len(G) == 0:
        return G
    comp = max(nx.connected_components(G), key=len)
    return G.subgraph(comp).copy()


def global_efficiency(G, weight="length", norm_n=None):
    """Average inverse shortest-path length. Pass norm_n to normalize by a fixed
    node count (e.g. the original network size) so that comparing a damaged
    subgraph against the baseline yields a ratio bounded in [0, 1] — without it,
    removing peripheral nodes can shrink the denominator faster than the numerator
    and produce a misleading efficiency > baseline."""
    nodes = list(G.nodes)
    n = len(nodes)
    if n < 2:
        return 0.0

    total = 0.0
    for src in nodes:
        lengths = nx.single_source_dijkstra_path_length(G, src, weight=weight)
        for dst, d in lengths.items():
            if dst != src and d > 0:
                total += 1.0 / d

    denom_n = norm_n if norm_n is not None else n
    if denom_n < 2:
        return 0.0
    return total / (denom_n * (denom_n - 1))


def compute_betweenness(G, weight="length", k=None):
    n = len(G)
    if n == 0:
        return {}
    k_actual = min(n, 500) if k is None else k
    return nx.betweenness_centrality(G, k=k_actual, weight=weight, normalized=True)


def ablation_curve(G, bc=None, max_removals=10, weight="length", adaptive=True):
    G = G.copy()
    if bc is None:
        bc = compute_betweenness(G, weight=weight)

    n_total = len(G)
    lcc0 = _lcc(G)
    eff0 = global_efficiency(lcc0, weight=weight, norm_n=n_total)

    results = []
    removed = []

    for step in range(max_removals):
        if len(G) == 0:
            break

        if adaptive or step == 0:
            bc = compute_betweenness(G, weight=weight)

        if not bc:
            break

        target = max(bc, key=bc.get)
        bc_val = bc[target]
        bc.pop(target, None)

        G.remove_node(target)
        removed.append(target)

        lcc_now = _lcc(G)
        lcc_size = len(lcc_now)
        eff_now = global_efficiency(lcc_now, weight=weight, norm_n=n_total)

        results.append({
            "n_removed": step + 1,
            "node_id": int(target),
            "betweenness": float(bc_val),
            "lcc_size": lcc_size,
            "lcc_fraction": lcc_size / n_total if n_total > 0 else 0.0,
            "efficiency": eff_now,
            "resilience_index": eff_now / eff0 if eff0 > 0 else 0.0,
        })

    return results


def compute_reroute(G, disabled_nodes, src, dst, weight="length"):
    view = nx.graphviews.subgraph_view(
        G,
        filter_node=lambda n: n not in disabled_nodes,
    )
    try:
        path = nx.shortest_path(view, src, dst, weight=weight)
        length = nx.shortest_path_length(view, src, dst, weight=weight)
        return path, float(length)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return [], float("inf")
