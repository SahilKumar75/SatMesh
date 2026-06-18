"""
track_b/criticality.py — betweenness-centrality analysis and resilience curves.

Usage:
    python track_b/criticality.py outputs/healed.gpickle outputs/ --max_removals 10
"""

from __future__ import annotations
import argparse, json, os, pickle
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


# ── Helpers ───────────────────────────────────────────────────────────────────

def _lcc(G: nx.Graph) -> nx.Graph:
    if G.number_of_nodes() == 0:
        return G
    comp = max(nx.connected_components(G), key=len)
    return G.subgraph(comp).copy()


def _avg_path(G: nx.Graph, weight: str = "length") -> float:
    H = _lcc(G)
    if H.number_of_nodes() < 2:
        return 0.0
    return nx.average_shortest_path_length(H, weight=weight)


def global_efficiency(G: nx.Graph, weight: str = "length") -> float:
    """
    Weighted global efficiency = mean over all ordered node pairs of 1/d(u,v),
    with disconnected pairs contributing 0. Unlike average-path-over-LCC this
    DROPS when the network fragments, so it correctly measures resilience under
    targeted attack (PS4: "recompute global efficiency after each node removal").
    """
    n = G.number_of_nodes()
    if n < 2:
        return 0.0
    total = 0.0
    for _, lengths in nx.all_pairs_dijkstra_path_length(G, weight=weight):
        for d in lengths.values():
            if d > 0:
                total += 1.0 / d
    return total / (n * (n - 1))


# ── Public API ────────────────────────────────────────────────────────────────

def compute_betweenness(
    G: nx.Graph,
    weight: str = "length",
    k: int | None = None,
) -> dict[Any, float]:
    """
    Normalised betweenness centrality. k caps the number of pivot nodes used
    for approximation (default: min(|V|, 500)).
    """
    k_eff = k if k is not None else min(len(G), 500)
    return nx.betweenness_centrality(
        G, weight=weight, k=k_eff, normalized=True, seed=42
    )


def ablation_curve(
    G: nx.Graph,
    bc: dict[Any, float] | None = None,
    max_removals: int = 10,
    weight: str = "length",
    adaptive: bool = True,
) -> list[dict]:
    """
    Adaptive targeted-attack ablation. At each step the highest-betweenness node
    in the CURRENT graph is removed and betweenness is recomputed (PS4 spec).

    resilience_index = efficiency(current) / efficiency(baseline): starts at 1.0
    and DECREASES toward 0 as the network degrades. Lower = more vulnerable.
    """
    total_nodes = G.number_of_nodes()
    base_eff = global_efficiency(G, weight)

    results: list[dict] = [{
        "n_removed":        0,
        "node_id":          None,
        "betweenness":      None,
        "lcc_size":         _lcc(G).number_of_nodes(),
        "lcc_fraction":     _lcc(G).number_of_nodes() / max(total_nodes, 1),
        "efficiency":       base_eff,
        "resilience_index": 1.0,
    }]

    G_work = G.copy()
    for step in range(1, max_removals + 1):
        if G_work.number_of_nodes() < 2:
            break
        # recompute betweenness on the current graph (adaptive attack)
        if adaptive or bc is None:
            cur_bc = compute_betweenness(G_work, weight=weight)
        else:
            cur_bc = {n: bc[n] for n in G_work if n in bc}
        if not cur_bc:
            break
        node = max(cur_bc, key=cur_bc.get)
        node_bc = float(cur_bc[node])
        G_work.remove_node(node)

        eff = global_efficiency(G_work, weight)
        lcc_sz = _lcc(G_work).number_of_nodes()
        results.append({
            "n_removed":        step,
            "node_id":          int(node) if isinstance(node, (int, np.integer)) else node,
            "betweenness":      node_bc,
            "lcc_size":         lcc_sz,
            "lcc_fraction":     lcc_sz / max(total_nodes, 1),
            "efficiency":       eff,
            "resilience_index": float(eff / base_eff) if base_eff > 0 else 0.0,
        })

    return results


def compute_reroute(
    G: nx.Graph,
    disabled_nodes: list[Any],
    src: Any,
    dst: Any,
    weight: str = "length",
) -> tuple[list, float]:
    """
    Find shortest path from src to dst with disabled_nodes removed.
    Returns (path_node_list, total_length) or ([], inf) if no path exists.
    """
    H = G.copy()
    for n in disabled_nodes:
        if H.has_node(n):
            H.remove_node(n)
    try:
        path   = nx.shortest_path(H, src, dst, weight=weight)
        length = nx.shortest_path_length(H, src, dst, weight=weight)
        return path, float(length)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return [], float("inf")


def plot_ablation_curve(results: list[dict], output_path: str) -> None:
    """Two-panel figure: Resilience Index and LCC fraction vs n_removed."""
    steps  = [r["n_removed"]       for r in results]
    ri     = [r["resilience_index"] for r in results]
    lcc_fr = [r["lcc_fraction"]    for r in results]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    ax1.plot(steps, ri, marker="o", color="#d62728", linewidth=2)
    ax1.set_ylim(0, 1.05)
    ax1.set_xlabel("Nodes removed (adaptive betweenness attack)")
    ax1.set_ylabel("Resilience Index (efficiency / baseline efficiency)")
    ax1.set_title("Resilience Index — lower = more degraded")
    ax1.grid(True, alpha=0.3)

    ax2.plot(steps, lcc_fr, marker="s", color="#1f77b4", linewidth=2)
    ax2.set_ylim(0, 1.05)
    ax2.set_xlabel("Nodes removed (adaptive betweenness attack)")
    ax2.set_ylabel("LCC fraction")
    ax2.set_title("Largest Connected Component")
    ax2.grid(True, alpha=0.3)

    fig.suptitle("Road Network Resilience — Targeted Node Removal", y=1.01)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"[criticality] curve saved → {output_path}")


def run_criticality(
    graph_path:   str,
    output_dir:   str,
    max_removals: int = 10,
    weight:       str = "length",
) -> dict:
    """
    Full pipeline: load → betweenness → ablation → plot → write JSON.
    Returns the results dict.
    """
    print(f"[criticality] loading {graph_path} ...")
    with open(graph_path, "rb") as f:
        G = pickle.load(f)
    print(f"[criticality] graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

    os.makedirs(output_dir, exist_ok=True)

    print("[criticality] computing betweenness centrality ...")
    bc = compute_betweenness(G, weight=weight)

    top10 = sorted(bc, key=bc.get, reverse=True)[:10]
    print("[criticality] top-10 gatekeeper nodes:")
    for i, n in enumerate(top10, 1):
        print(f"  {i:2d}. node {n}  BC={bc[n]:.4f}")

    print(f"[criticality] running ablation (max {max_removals} removals) ...")
    ablation = ablation_curve(G, bc, max_removals=max_removals)

    curve_path = os.path.join(output_dir, "resilience_curve.png")
    plot_ablation_curve(ablation, curve_path)

    out = {
        "betweenness": {
            str(k): round(v, 6) for k, v in
            sorted(bc.items(), key=lambda x: x[1], reverse=True)[:50]
        },
        "ablation": ablation,
    }
    json_path = os.path.join(output_dir, "criticality.json")
    with open(json_path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[criticality] results saved → {json_path}")
    return out


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="SatMesh criticality analysis")
    parser.add_argument("graph",        help="Healed graph .gpickle path")
    parser.add_argument("output_dir",   help="Directory for outputs")
    parser.add_argument("--max_removals", type=int, default=10,
                        help="Number of nodes to ablate")
    parser.add_argument("--weight",     default="length",
                        help="Edge weight attribute for path length")
    args = parser.parse_args()

    run_criticality(
        args.graph,
        args.output_dir,
        max_removals=args.max_removals,
        weight=args.weight,
    )


if __name__ == "__main__":
    main()
