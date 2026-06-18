"""
dashboard/app.py — SatMesh interactive road-network resilience dashboard.

PS4 deliverable: Streamlit + Leaflet criticality heatmap with click-to-disable
node simulation showing rerouting, travel-time increase, areas isolated, and a
live Resilience Index — the "what-if disaster simulator" the problem statement asks for.

Launch (defaults to the Track B outputs):
    streamlit run dashboard/app.py
    streamlit run dashboard/app.py -- --graph outputs/trackb/healed_graph.gpickle \\
        --criticality outputs/trackb/criticality.json
"""

from __future__ import annotations
import argparse, json, os, pickle, sys

import folium
import networkx as nx
import numpy as np
import pandas as pd
import streamlit as st
from scipy.spatial import cKDTree
from streamlit_folium import st_folium

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DEFAULT_GRAPH = "outputs/trackb/healed_graph.gpickle"
DEFAULT_CRIT  = "outputs/trackb/criticality.json"


# ── Args ───────────────────────────────────────────────────────────────────────

def _parse_args():
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--graph",       default=DEFAULT_GRAPH)
    p.add_argument("--criticality", default=DEFAULT_CRIT)
    try:
        idx = sys.argv.index("--")
        args, _ = p.parse_known_args(sys.argv[idx + 1:])
    except ValueError:
        args, _ = p.parse_known_args([])
    return args


# ── Loading / caching ───────────────────────────────────────────────────────────

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


# ── Colour: green (low) → red (high betweenness) ────────────────────────────────

def _bc_colour(v: float, vmax: float) -> str:
    r = v / vmax if vmax > 0 else 0.0
    red, grn = int(255 * r), int(180 * (1 - r))
    return f"#{red:02x}{grn:02x}20"


def _node_xy(G, n):
    d = G.nodes[n]
    return d.get("lat", d.get("y", 0)), d.get("lon", d.get("x", 0))


# ── Nearest-node lookup ─────────────────────────────────────────────────────────

@st.cache_data
def _node_arrays(_G: nx.Graph):
    nodes = list(_G.nodes)
    coords = np.array([_node_xy(_G, n) for n in nodes])
    return nodes, coords


def find_nearest_node(G, lat, lon, max_dist):
    nodes, coords = _node_arrays(G)
    tree = cKDTree(coords)
    dist, idx = tree.query([lat, lon])
    return nodes[idx] if dist <= max_dist else None


# ── Map ─────────────────────────────────────────────────────────────────────────

def build_map(G, bc, disabled, reroute_path):
    bc_max = max(bc.values()) if bc else 1.0
    coords = np.array([_node_xy(G, n) for n in G.nodes])
    centre = (coords[:, 0].mean(), coords[:, 1].mean()) if len(coords) else (0, 0)
    span = max(coords[:, 0].ptp(), coords[:, 1].ptp(), 1e-6) if len(coords) else 1
    zoom = 15 if span < 0.02 else 13
    m = folium.Map(location=centre, zoom_start=zoom, tiles="CartoDB positron")

    reroute_set = set(zip(reroute_path[:-1], reroute_path[1:]))
    for u, v, data in G.edges(data=True):
        ul = _node_xy(G, u); vl = _node_xy(G, v)
        is_rr = (u, v) in reroute_set or (v, u) in reroute_set
        is_syn = data.get("synthetic", False)
        colour = "#ff7f0e" if is_rr else ("#2ca02c" if is_syn else "#bbbbbb")
        weight = 6 if is_rr else (3 if is_syn else 1.5)
        folium.PolyLine([ul, vl], color=colour, weight=weight, opacity=0.85).add_to(m)

    for n in sorted(bc, key=bc.get, reverse=True)[:500]:
        lat, lon = _node_xy(G, n)
        off = n in disabled
        colour = "#000000" if off else _bc_colour(bc.get(n, 0), bc_max)
        folium.CircleMarker(
            location=(lat, lon),
            radius=10 if off else max(3, int(bc.get(n, 0) / bc_max * 9)),
            color=colour, weight=3 if off else 1,
            fill=True, fill_color=colour, fill_opacity=0.9,
            tooltip=f"Node {n} — BC {bc.get(n, 0):.3f}" + ("  (DISABLED)" if off else ""),
        ).add_to(m)
    return m


# ── Helpers ─────────────────────────────────────────────────────────────────────

def _lcc(G):
    return len(max(nx.connected_components(G), key=len)) if G.number_of_nodes() else 0


def main():
    st.set_page_config(page_title="SatMesh — Route Resilience", layout="wide")
    st.title("SatMesh — Urban Road Network Resilience")
    st.caption("Click a red intersection on the map to simulate its failure "
               "(flood / accident) and watch the network degrade.")

    args = _parse_args()
    with st.sidebar:
        st.header("Data")
        graph_path = st.text_input("Healed graph (.gpickle)", value=args.graph)
        crit_path  = st.text_input("Criticality JSON", value=args.criticality)

    if not os.path.exists(graph_path):
        st.warning(f"Graph not found: `{graph_path}`. Run `track_b/run_trackb.py` first, "
                   "or point to a healed-graph pickle in the sidebar.")
        return

    G = load_graph(graph_path)
    bc = compute_bc(G)
    ranked = sorted(bc, key=bc.get, reverse=True)
    ntype = type(ranked[0]) if ranked else int
    crit = load_criticality(crit_path) if os.path.exists(crit_path) else None

    # coordinate scale → click tolerance (geo lat/lon vs pixel-metre grids differ hugely)
    coords = np.array([_node_xy(G, n) for n in G.nodes])
    span = max(coords[:, 0].ptp(), coords[:, 1].ptp(), 1.0)
    click_tol = span * 0.04

    ss = st.session_state
    ss.setdefault("disabled", [])
    ss.setdefault("reroute_path", [])
    ss.setdefault("reroute_info", None)

    # ── Sidebar controls ──────────────────────────────────────────────────────
    with st.sidebar:
        st.divider(); st.header("Failure simulation")
        if st.button("⚡ Disable top 3 gatekeepers", use_container_width=True):
            ss["disabled"] = [ranked[i] for i in range(min(3, len(ranked)))]
            ss["reroute_path"] = []; ss["reroute_info"] = None
            st.rerun()
        if st.button("Clear all", use_container_width=True):
            ss["disabled"] = []; ss["reroute_path"] = []; ss["reroute_info"] = None
            st.rerun()

        st.divider(); st.header("Route under disruption")
        node_opts = [str(n) for n in G.nodes]
        src = st.selectbox("From", node_opts, index=0)
        dst = st.selectbox("To", node_opts, index=min(len(node_opts) - 1, 20))
        if st.button("Compute reroute", use_container_width=True):
            from track_b.criticality import compute_reroute
            s, d = ntype(src), ntype(dst)
            base_path, base_len = compute_reroute(G, [], s, d)
            new_path,  new_len  = compute_reroute(G, ss["disabled"], s, d)
            ss["reroute_path"] = new_path
            if new_len == float("inf"):
                ss["reroute_info"] = ("cut", base_len, None)
            else:
                inc = (new_len - base_len) / base_len * 100 if base_len > 0 else 0
                ss["reroute_info"] = ("ok", base_len, (new_len, inc))
            st.rerun()

    disabled = [ntype(n) for n in ss["disabled"]]
    G_active = G.copy()
    G_active.remove_nodes_from([n for n in disabled if G_active.has_node(n)])

    lcc_base, lcc_act = _lcc(G), _lcc(G_active)
    isolated = lcc_base - lcc_act
    components = nx.number_connected_components(G_active) if G_active.number_of_nodes() else 0
    retained = lcc_act / lcc_base * 100 if lcc_base else 0

    # ── Impact readout ────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Intersections", G.number_of_nodes())
    c2.metric("Disabled", len(disabled))
    c3.metric("Connected reach", f"{retained:.0f}%",
              delta=f"{retained - 100:.0f}%" if disabled else None,
              delta_color="inverse")
    c4.metric("Intersections isolated", isolated, delta=isolated if disabled else None,
              delta_color="inverse")
    c5.metric("Separate areas", components)

    info = ss["reroute_info"]
    if info:
        if info[0] == "cut":
            st.error(f"🚧 Route severed — destination is unreachable after the failure "
                     f"(baseline was {info[1]:.0f} m).")
        else:
            base_len, (new_len, inc) = info[1], info[2]
            st.warning(f"↪ Detour required: travel distance **{base_len:.0f} m → {new_len:.0f} m**, "
                       f"a **+{inc:.0f}%** increase in travel time.")

    # ── Map + side panels ─────────────────────────────────────────────────────
    map_col, side = st.columns([3, 1])
    with map_col:
        st.caption("Node colour = betweenness (green low → red gatekeeper) · "
                   "black = disabled · green lines = healed bridges · orange = reroute")
        fmap = build_map(G, bc, disabled, ss["reroute_path"])
        md = st_folium(fmap, width=None, height=560, key="map")
        clk = (md or {}).get("last_object_clicked")
        if clk and clk.get("lat") is not None:
            near = find_nearest_node(G, clk["lat"], clk["lng"], click_tol)
            if near is not None and near not in disabled:
                ss["disabled"].append(near)
                ss["reroute_path"] = []; ss["reroute_info"] = None
                st.rerun()

    with side:
        st.subheader("Top Gatekeeper Nodes")
        st.dataframe(
            pd.DataFrame([(str(n), round(bc[n], 3)) for n in ranked[:10]],
                         columns=["node", "betweenness"]).set_index("node"),
            use_container_width=True,
        )
        if crit and "ablation" in crit:
            st.subheader("Resilience under attack")
            abl = crit["ablation"]
            st.line_chart(
                pd.DataFrame({
                    "Resilience Index": [r["resilience_index"] for r in abl],
                    "Connected fraction": [r["lcc_fraction"] for r in abl],
                }, index=[r["n_removed"] for r in abl])
            )
            st.caption("Adaptive betweenness attack — both fall as gatekeepers are removed.")

    if crit and "ablation" in crit:
        with st.expander("Ablation detail (per-node removal)"):
            st.dataframe(pd.DataFrame(crit["ablation"]).set_index("n_removed"),
                         use_container_width=True)


if __name__ == "__main__":
    main()
