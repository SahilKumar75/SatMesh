"""
dashboard/app.py — SatMesh interactive resilience dashboard.

Launch:
    streamlit run dashboard/app.py -- --graph outputs/healed_graph.gpickle
    streamlit run dashboard/app.py -- --graph outputs/healed_graph.gpickle \\
        --criticality outputs/criticality.json
"""

from __future__ import annotations
import argparse, json, os, pickle, sys

import folium
import networkx as nx
import numpy as np
import streamlit as st
from scipy.spatial import cKDTree
from streamlit_folium import st_folium

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ── Argument parsing (passed after "--" in streamlit run) ─────────────────────

def _parse_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--graph",       default=None)
    parser.add_argument("--criticality", default=None)
    # streamlit injects its own args before "--"; slice them off
    try:
        idx = sys.argv.index("--")
        args, _ = parser.parse_known_args(sys.argv[idx + 1:])
    except ValueError:
        args, _ = parser.parse_known_args([])
    return args


# ── Graph loading / caching ───────────────────────────────────────────────────

@st.cache_resource
def load_graph(path: str) -> nx.Graph:
    with open(path, "rb") as f:
        return pickle.load(f)


@st.cache_resource
def load_criticality(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


@st.cache_data
def compute_bc(_G: nx.Graph) -> dict:
    from track_b.criticality import compute_betweenness
    return compute_betweenness(_G)


# ── Colour helpers ────────────────────────────────────────────────────────────

def _bc_colour(bc_val: float, bc_max: float) -> str:
    """Blue (low) → Red (high) interpolation."""
    ratio = bc_val / bc_max if bc_max > 0 else 0.0
    r = int(255 * ratio)
    b = int(255 * (1 - ratio))
    return f"#{r:02x}00{b:02x}"


# ── Nearest node lookup ────────────────────────────────────────────────────────

def _build_node_tree(G: nx.Graph):
    nodes  = list(G.nodes)
    coords = np.array([
        [G.nodes[n].get("lat", G.nodes[n].get("y", 0)),
         G.nodes[n].get("lon", G.nodes[n].get("x", 0))]
        for n in nodes
    ])
    return nodes, coords, cKDTree(coords)


def find_nearest_node(G: nx.Graph, lat: float, lon: float) -> int | None:
    nodes, _, tree = _build_node_tree(G)
    dist, idx = tree.query([lat, lon])
    if dist > 0.01:      # ~1 km sanity cap
        return None
    return nodes[idx]


# ── Folium map builder ────────────────────────────────────────────────────────

def build_folium_map(
    G: nx.Graph,
    bc: dict,
    disabled_nodes: list,
    reroute_path: list,
) -> folium.Map:
    bc_max = max(bc.values()) if bc else 1.0

    # centre on graph centroid
    lats = [G.nodes[n].get("lat", G.nodes[n].get("y", 0)) for n in G.nodes]
    lons = [G.nodes[n].get("lon", G.nodes[n].get("x", 0)) for n in G.nodes]
    centre = (np.mean(lats) if lats else 0.0, np.mean(lons) if lons else 0.0)

    m = folium.Map(location=centre, zoom_start=15, tiles="CartoDB positron")

    # draw edges
    reroute_set = set(zip(reroute_path[:-1], reroute_path[1:]))
    for u, v, data in G.edges(data=True):
        u_lat = G.nodes[u].get("lat", G.nodes[u].get("y", 0))
        u_lon = G.nodes[u].get("lon", G.nodes[u].get("x", 0))
        v_lat = G.nodes[v].get("lat", G.nodes[v].get("y", 0))
        v_lon = G.nodes[v].get("lon", G.nodes[v].get("x", 0))

        is_reroute  = (u, v) in reroute_set or (v, u) in reroute_set
        is_synth    = data.get("synthetic", False)
        colour = "#ff7f00" if is_reroute else ("#2ca02c" if is_synth else "#aaaaaa")
        weight = 5 if is_reroute else (3 if is_synth else 1.5)

        folium.PolyLine(
            [(u_lat, u_lon), (v_lat, v_lon)],
            color=colour, weight=weight, opacity=0.8,
        ).add_to(m)

    # draw nodes (only top-500 by centrality to keep it snappy)
    top_nodes = sorted(bc, key=bc.get, reverse=True)[:500]
    for n in top_nodes:
        lat = G.nodes[n].get("lat", G.nodes[n].get("y", 0))
        lon = G.nodes[n].get("lon", G.nodes[n].get("x", 0))
        is_disabled = n in disabled_nodes
        colour = "#ff0000" if is_disabled else _bc_colour(bc.get(n, 0), bc_max)
        radius = 8 if is_disabled else max(3, int(bc.get(n, 0) / bc_max * 8))

        folium.CircleMarker(
            location=(lat, lon),
            radius=radius,
            color=colour,
            fill=True, fill_color=colour, fill_opacity=0.8,
            tooltip=f"Node {n}<br>BC={bc.get(n, 0):.4f}",
        ).add_to(m)

    return m


# ── Quick metrics ─────────────────────────────────────────────────────────────

def _lcc_size(G: nx.Graph) -> int:
    if G.number_of_nodes() == 0:
        return 0
    return len(max(nx.connected_components(G), key=len))


def _resilience_index(G: nx.Graph, bc: dict) -> float:
    if G.number_of_nodes() < 3:
        return 1.0
    from eval.metrics import resilience_index
    return resilience_index(G)


# ── Streamlit app ─────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="SatMesh — Road Network Resilience",
        layout="wide",
    )
    st.title("SatMesh — Road Network Resilience Dashboard")

    args = _parse_args()

    # sidebar — graph loading
    with st.sidebar:
        st.header("Data")
        graph_path = st.text_input("Graph (.gpickle)", value=args.graph or "")
        crit_path  = st.text_input("Criticality JSON (optional)",
                                   value=args.criticality or "")
        load_btn   = st.button("Load")

    if not graph_path or (not os.path.exists(graph_path) and not load_btn):
        st.info("Enter a healed graph path in the sidebar and click **Load**.")
        return

    if not os.path.exists(graph_path):
        st.error(f"File not found: {graph_path}")
        return

    G  = load_graph(graph_path)
    bc = compute_bc(G)
    bc_sorted_nodes = sorted(bc, key=bc.get, reverse=True)

    crit_data = None
    if crit_path and os.path.exists(crit_path):
        crit_data = load_criticality(crit_path)

    # initialise session state
    if "disabled_nodes" not in st.session_state:
        st.session_state["disabled_nodes"] = []
    if "reroute_path" not in st.session_state:
        st.session_state["reroute_path"] = []
    if "reroute_len" not in st.session_state:
        st.session_state["reroute_len"] = None

    # ── Sidebar controls ──────────────────────────────────────────────────────
    with st.sidebar:
        st.header("Node Controls")
        top10 = [str(n) for n in bc_sorted_nodes[:10]]
        selected_disable = st.multiselect(
            "Disable nodes (top-10 by centrality pre-loaded)",
            options=[str(n) for n in bc_sorted_nodes[:50]],
            default=st.session_state["disabled_nodes"]
                   if st.session_state["disabled_nodes"] else [],
        )
        if st.button("Apply selection"):
            st.session_state["disabled_nodes"] = selected_disable
            st.session_state["reroute_path"]   = []
            st.session_state["reroute_len"]    = None
            st.rerun()

        if st.button("Clear disabled nodes"):
            st.session_state["disabled_nodes"] = []
            st.session_state["reroute_path"]   = []
            st.session_state["reroute_len"]    = None
            st.rerun()

        st.divider()
        st.header("Routing")
        node_strs = [str(n) for n in G.nodes]
        src_str   = st.selectbox("Source node",      options=node_strs, index=0)
        dst_str   = st.selectbox("Destination node", options=node_strs,
                                 index=min(len(node_strs) - 1, 5))
        if st.button("Compute reroute"):
            from track_b.criticality import compute_reroute
            disabled = [type(list(G.nodes)[0])(n)
                        for n in st.session_state["disabled_nodes"]
                        if n]
            src = type(list(G.nodes)[0])(src_str)
            dst = type(list(G.nodes)[0])(dst_str)
            path, length = compute_reroute(G, disabled, src, dst)
            st.session_state["reroute_path"] = path
            st.session_state["reroute_len"]  = length
            st.rerun()

    # ── Metric bar ────────────────────────────────────────────────────────────
    disabled_ids = st.session_state["disabled_nodes"]
    G_active = G.copy()
    for n in disabled_ids:
        try:
            G_active.remove_node(type(list(G.nodes)[0])(n))
        except Exception:
            pass

    lcc_base   = _lcc_size(G)
    lcc_active = _lcc_size(G_active)
    ri = None
    if G.number_of_nodes() >= 3:
        try:
            from eval.metrics import resilience_index
            ri = resilience_index(G)
        except Exception:
            pass

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total nodes",    G.number_of_nodes())
    col2.metric("LCC (baseline)", lcc_base)
    col3.metric("LCC (active)",   lcc_active,
                delta=lcc_active - lcc_base if disabled_ids else None)
    col4.metric("Resilience Index", f"{ri:.3f}" if ri is not None else "–")

    if st.session_state["reroute_len"] is not None:
        rlen = st.session_state["reroute_len"]
        st.info(
            f"Reroute: {len(st.session_state['reroute_path'])} nodes, "
            f"length = {'∞' if rlen == float('inf') else f'{rlen:.1f} m'}"
        )

    # ── Map + charts ──────────────────────────────────────────────────────────
    map_col, chart_col = st.columns([3, 1])

    with map_col:
        st.subheader("Network Map")
        st.caption(
            "Gray = road edge  |  Green = healed/synthetic  |  Orange = reroute path  "
            "| Red node = disabled  |  Blue→Red = low→high betweenness"
        )
        fmap = build_folium_map(
            G, bc,
            [type(list(G.nodes)[0])(n) for n in disabled_ids if n],
            st.session_state["reroute_path"],
        )
        map_data = st_folium(fmap, width=None, height=550, key="main_map")

        # click-to-disable
        clicked = map_data.get("last_object_clicked")
        if clicked:
            lat = clicked.get("lat")
            lon = clicked.get("lng")
            if lat is not None and lon is not None:
                nearest = find_nearest_node(G, lat, lon)
                if nearest is not None:
                    n_str = str(nearest)
                    if n_str not in st.session_state["disabled_nodes"]:
                        st.session_state["disabled_nodes"].append(n_str)
                        st.session_state["reroute_path"] = []
                        st.session_state["reroute_len"]  = None
                        st.rerun()

    with chart_col:
        st.subheader("Centrality")
        import pandas as pd
        top15 = [(str(n), bc[n]) for n in bc_sorted_nodes[:15]]
        df_bc = pd.DataFrame(top15, columns=["node", "BC"])
        df_bc = df_bc.set_index("node")
        st.bar_chart(df_bc)

        if crit_data and "ablation" in crit_data:
            st.subheader("Resilience Curve")
            abl   = crit_data["ablation"]
            df_ri = pd.DataFrame({
                "n_removed":       [r["n_removed"]        for r in abl],
                "resilience_index": [r["resilience_index"] for r in abl],
            }).set_index("n_removed")
            st.line_chart(df_ri)

    # ── Raw ablation table ────────────────────────────────────────────────────
    if crit_data and "ablation" in crit_data:
        with st.expander("Ablation detail"):
            import pandas as pd
            st.dataframe(
                pd.DataFrame(crit_data["ablation"]).set_index("n_removed"),
                use_container_width=True,
            )


if __name__ == "__main__":
    main()
