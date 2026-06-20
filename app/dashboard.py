"""PS4 Route Resilience — Interactive Streamlit Dashboard.

Usage:
    streamlit run app/dashboard.py

Dependencies:
    pip install streamlit folium streamlit-folium geopandas networkx
"""
from __future__ import annotations

import io
import pickle
import sys
import tempfile
from pathlib import Path

import networkx as nx
import streamlit as st

# repo root on sys.path so src.* and api.* imports work
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from src.graph.criticality import compute_betweenness, global_efficiency
from src.graph.zones import classify_zones, zones_to_geojson
from api.graph_api import GraphAPI

# ── constants ────────────────────────────────────────────────────────────────
ZONE_COLOR = {"critical": "#e63946", "vulnerable": "#f4a261", "resilient": "#2a9d8f"}
MAX_MAP_NODES = 5000  # cap for Folium rendering performance

# ── helpers ──────────────────────────────────────────────────────────────────

def _available_cities() -> list[str]:
    out = _ROOT / "outputs"
    if not out.exists():
        return []
    return sorted(p.parent.name for p in out.glob("*/healed_graph.gpickle"))


@st.cache_resource(show_spinner="Computing betweenness centrality…")
def _compute_analysis(graph_key: str, n_nodes: int):
    """Cache-friendly: recompute only when graph identity changes."""
    G = st.session_state["G"]
    bc = compute_betweenness(G, k=min(n_nodes, 300))
    zones = classify_zones(G, bc)
    eff = global_efficiency(G)
    lcc_size = max(len(c) for c in nx.connected_components(G)) if G.number_of_nodes() else 0
    return bc, zones, eff, lcc_size


def _load_graph_from_city(city_id: str) -> nx.Graph:
    p = _ROOT / "outputs" / city_id / "healed_graph.gpickle"
    with open(p, "rb") as f:
        return pickle.load(f)


def _load_graph_from_bytes(data: bytes) -> nx.Graph:
    return pickle.loads(data)


def _build_folium_map(G: nx.Graph, zones: dict, bc: dict,
                      disabled_nodes: set | None = None) -> "folium.Map":
    import folium

    lats = [d.get("lat", 0) for _, d in G.nodes(data=True) if d.get("lat")]
    lons = [d.get("lon", 0) for _, d in G.nodes(data=True) if d.get("lon")]
    if not lats:
        return folium.Map(location=[20.5937, 78.9629], zoom_start=5)

    cx, cy = sum(lats) / len(lats), sum(lons) / len(lons)
    m = folium.Map(location=[cx, cy], zoom_start=13, tiles="CartoDB positron")

    # Edges
    for u, v, edata in G.edges(data=True):
        u_d, v_d = G.nodes[u], G.nodes[v]
        if u_d.get("lat") and v_d.get("lat"):
            color = "#adb5bd" if not edata.get("synthetic") else "#74c0fc"
            folium.PolyLine(
                [[u_d["lat"], u_d["lon"]], [v_d["lat"], v_d["lon"]]],
                color=color, weight=1.5, opacity=0.6,
            ).add_to(m)

    # Nodes (capped for performance)
    nodes_to_draw = list(G.nodes(data=True))
    if len(nodes_to_draw) > MAX_MAP_NODES:
        st.warning(f"Graph has {len(nodes_to_draw):,} nodes — displaying {MAX_MAP_NODES:,} for performance.")
        nodes_to_draw = nodes_to_draw[:MAX_MAP_NODES]

    for n, d in nodes_to_draw:
        lat, lon = d.get("lat"), d.get("lon")
        if not lat:
            continue
        zone = zones.get(n, "resilient")
        is_disabled = disabled_nodes and n in disabled_nodes
        color = "#6c757d" if is_disabled else ZONE_COLOR[zone]
        radius = 6 if zone == "critical" else 4
        popup_html = (
            f"<b>Node {n}</b><br>"
            f"Zone: <b style='color:{color}'>{zone}</b><br>"
            f"Betweenness: {bc.get(n, 0):.5f}<br>"
            f"Degree: {G.degree(n)}<br>"
            f"Elevation: {d.get('elevation_m', 'N/A')}m"
        )
        folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            popup=folium.Popup(popup_html, max_width=220),
            tooltip=f"{zone} | bc={bc.get(n, 0):.4f}",
        ).add_to(m)

    # Legend
    legend_html = """
    <div style="position:fixed;bottom:30px;left:30px;z-index:1000;background:white;
                padding:10px 14px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,.2);font-size:13px">
      <b>Criticality Zone</b><br>
      <span style="color:#e63946">&#9679;</span> Critical (top 10%)<br>
      <span style="color:#f4a261">&#9679;</span> Vulnerable (next 30%)<br>
      <span style="color:#2a9d8f">&#9679;</span> Resilient (bottom 60%)<br>
      <span style="color:#74c0fc">&#9135;</span> Synthetic (healed) edge
    </div>"""
    m.get_root().html.add_child(folium.Element(legend_html))
    return m


# ── page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PS4 Route Resilience",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🛣️ Route Resilience: Road Network Criticality Dashboard")
st.caption("BAH-2026 · PS4 · Track B · Interactive graph analysis")

# ── sidebar: graph loading ───────────────────────────────────────────────────
with st.sidebar:
    st.header("Load Graph")
    cities = _available_cities()
    load_mode = st.radio("Source", ["Select city", "Upload .gpickle"], horizontal=True)

    graph_key = None
    if load_mode == "Select city" and cities:
        city_id = st.selectbox("City", cities)
        if st.button("Load", type="primary"):
            with st.spinner(f"Loading {city_id}…"):
                st.session_state["G"] = _load_graph_from_city(city_id)
                st.session_state["graph_key"] = city_id
                st.session_state["city_id"] = city_id
                st.success(f"Loaded: {city_id}")
    elif load_mode == "Select city":
        st.info("No cities found in `outputs/`. Run the pipeline first or upload a file.")

    if load_mode == "Upload .gpickle":
        up = st.file_uploader("Upload healed_graph.gpickle", type=["gpickle", "pkl", "pickle"])
        if up:
            with st.spinner("Parsing graph…"):
                st.session_state["G"] = _load_graph_from_bytes(up.read())
                st.session_state["graph_key"] = up.name
                st.session_state["city_id"] = up.name.replace(".gpickle", "").replace(".pkl", "")
                st.success(f"Loaded: {up.name}")

    if "G" not in st.session_state:
        st.stop()

    G: nx.Graph = st.session_state["G"]
    city_id: str = st.session_state.get("city_id", "unknown")
    graph_key: str = st.session_state["graph_key"]

    st.divider()
    st.metric("Nodes", f"{G.number_of_nodes():,}")
    st.metric("Edges", f"{G.number_of_edges():,}")
    comps = list(nx.connected_components(G))
    st.metric("Components", len(comps))
    st.metric("LCC size", f"{max(len(c) for c in comps):,}" if comps else "0")

# ── analysis (cached) ────────────────────────────────────────────────────────
bc, zones, base_eff, base_lcc = _compute_analysis(graph_key, G.number_of_nodes())

n_critical = sum(1 for z in zones.values() if z == "critical")
n_vuln = sum(1 for z in zones.values() if z == "vulnerable")

# ── tabs ─────────────────────────────────────────────────────────────────────
tab_map, tab_scenario, tab_disable, tab_metrics = st.tabs(
    ["🗺️ Criticality Map", "⚠️ Scenarios", "🚫 Node Disable", "📊 Metrics"]
)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: Criticality Map
# ─────────────────────────────────────────────────────────────────────────────
with tab_map:
    col1, col2, col3 = st.columns(3)
    col1.metric("Critical nodes", n_critical, help="Top 10% by betweenness centrality")
    col2.metric("Vulnerable nodes", n_vuln, help="Next 30% by betweenness centrality")
    col3.metric("Global efficiency", f"{base_eff:.4f}")

    st.markdown("Node size and colour reflect criticality zone. Hover for details.")
    try:
        from streamlit_folium import folium_static
        m = _build_folium_map(G, zones, bc)
        folium_static(m, width=1200, height=600)
    except ImportError:
        st.error("Install `streamlit-folium`: `pip install streamlit-folium`")

    with st.expander("Export GeoJSON"):
        gj = zones_to_geojson(G, zones, bc)
        import json
        st.download_button(
            "Download criticality_zones.geojson",
            data=json.dumps(gj),
            file_name=f"{city_id}_criticality_zones.geojson",
            mime="application/geo+json",
        )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: Scenario Simulation
# ─────────────────────────────────────────────────────────────────────────────
with tab_scenario:
    st.subheader("Disaster Scenario Simulation")
    st.markdown(
        "Simulate infrastructure damage and measure **Resilience Index** "
        "(ratio of post-event global efficiency to baseline)."
    )

    scenario = st.selectbox("Scenario type", ["flood", "earthquake", "collapse"])
    api = GraphAPI()
    # GraphAPI._load uses outputs/{city}; inject directly for uploaded graphs
    api._cache[city_id] = G

    params: dict = {}
    if scenario == "flood":
        params["elevation_threshold_m"] = st.slider(
            "Flood elevation threshold (m)", 1, 50, 10,
            help="Nodes below this elevation are inundated"
        )
    elif scenario == "earthquake":
        st.markdown("Set epicentre and damage radius:")
        c1, c2, c3 = st.columns(3)
        node_lats = [d.get("lat", 20.5) for _, d in G.nodes(data=True) if d.get("lat")]
        node_lons = [d.get("lon", 78.9) for _, d in G.nodes(data=True) if d.get("lon")]
        default_lat = sum(node_lats) / len(node_lats) if node_lats else 20.5
        default_lon = sum(node_lons) / len(node_lons) if node_lons else 78.9
        params["lat"] = c1.number_input("Epicentre lat", value=round(default_lat, 4), format="%.4f")
        params["lon"] = c2.number_input("Epicentre lon", value=round(default_lon, 4), format="%.4f")
        params["radius_m"] = c3.slider("Damage radius (m)", 100, 5000, 500)
    elif scenario == "collapse":
        top_crit = sorted(
            [(n, bc.get(n, 0)) for n, z in zones.items() if z == "critical"],
            key=lambda x: -x[1],
        )[:20]
        n_remove = st.slider("Number of critical nodes to collapse", 1, min(20, len(top_crit)), 5)
        params["node_ids"] = [n for n, _ in top_crit[:n_remove]]

    if st.button("Run scenario", type="primary"):
        with st.spinner("Simulating…"):
            try:
                result = api.run_scenario(city_id, scenario, params)
                ri = result["resilience_index"]
                ri_delta = ri - 1.0

                r1, r2, r3, r4 = st.columns(4)
                r1.metric("Resilience Index", f"{ri:.4f}",
                          delta=f"{ri_delta:+.4f}", delta_color="inverse")
                r2.metric("LCC fraction", f"{result['lcc_fraction']:.4f}")
                r3.metric("Components", result["components"])
                r4.metric("Nodes disabled", result["nodes_disabled"])

                if ri >= 0.90:
                    st.success(f"Network robust: RI={ri:.3f} ≥ 0.90")
                elif ri >= 0.70:
                    st.warning(f"Moderate damage: RI={ri:.3f} — rerouting possible")
                else:
                    st.error(f"Severe disruption: RI={ri:.3f} — major connectivity loss")

                if result.get("flood_critical_nodes"):
                    st.info(f"{result['flood_critical_nodes']} critical nodes are flood-vulnerable.")

                # Show damaged map
                try:
                    from streamlit_folium import folium_static
                    disabled_set = set(result.get("disabled_ids", []))
                    m2 = _build_folium_map(G, zones, bc, disabled_nodes=disabled_set)
                    st.markdown("**Disabled nodes shown in grey:**")
                    folium_static(m2, width=1200, height=500)
                except ImportError:
                    pass

            except Exception as e:
                st.error(f"Scenario error: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: Node Disable
# ─────────────────────────────────────────────────────────────────────────────
with tab_disable:
    st.subheader("Single-Node Knockout Analysis")
    st.markdown(
        "Remove one node and measure the resulting LCC fraction — "
        "identifies **gatekeeper nodes** whose removal most fragments the network."
    )

    node_ids = sorted(G.nodes())
    selected_node = st.selectbox("Select node to disable", node_ids)

    if st.button("Disable node", type="primary"):
        api2 = GraphAPI()
        api2._cache[city_id] = G
        result = api2.disable_node(city_id, selected_node)

        if "error" in result:
            st.error(result["error"])
        else:
            lcc_before = base_lcc / max(G.number_of_nodes(), 1)
            lcc_after = result["lcc_fraction"]
            delta_lcc = lcc_after - lcc_before

            c1, c2, c3 = st.columns(3)
            c1.metric("LCC fraction (before)", f"{lcc_before:.4f}")
            c2.metric("LCC fraction (after)", f"{lcc_after:.4f}",
                      delta=f"{delta_lcc:+.4f}", delta_color="inverse")
            c3.metric("Components after", result["components_after"])

            zone_label = zones.get(selected_node, "resilient")
            bc_val = bc.get(selected_node, 0)
            st.info(
                f"Node **{selected_node}** | Zone: **{zone_label}** | "
                f"Betweenness: **{bc_val:.5f}** | Degree: **{G.degree(selected_node)}**"
            )

            if abs(delta_lcc) > 0.05:
                st.error("High-impact node: removal drops LCC by >5%")
            elif abs(delta_lcc) > 0.02:
                st.warning("Moderate-impact node")
            else:
                st.success("Low-impact node")

    st.divider()
    st.subheader("Top-10 Gatekeeper Nodes")
    st.caption("Nodes with highest betweenness centrality — most likely to fragment network if removed.")

    import pandas as pd
    top10 = sorted(bc.items(), key=lambda x: -x[1])[:10]
    df_top = pd.DataFrame([
        {
            "Node": n,
            "Betweenness": round(v, 6),
            "Zone": zones.get(n, "resilient"),
            "Degree": G.degree(n),
            "Lat": round(G.nodes[n].get("lat", 0), 5),
            "Lon": round(G.nodes[n].get("lon", 0), 5),
        }
        for n, v in top10
    ])
    st.dataframe(df_top, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4: Metrics
# ─────────────────────────────────────────────────────────────────────────────
with tab_metrics:
    st.subheader("Network Health Summary")

    import pandas as pd

    lcc_frac = base_lcc / max(G.number_of_nodes(), 1)
    avg_degree = sum(d for _, d in G.degree()) / max(G.number_of_nodes(), 1)
    n_synthetic = sum(1 for _, _, d in G.edges(data=True) if d.get("synthetic"))

    metrics_df = pd.DataFrame([
        {"Metric": "Global efficiency", "Value": f"{base_eff:.4f}", "Target": ">0.05 (connected)"},
        {"Metric": "LCC fraction", "Value": f"{lcc_frac:.4f}", "Target": ">0.90"},
        {"Metric": "Critical nodes", "Value": str(n_critical), "Target": "Minimise"},
        {"Metric": "Vulnerable nodes", "Value": str(n_vuln), "Target": "Minimise"},
        {"Metric": "Avg degree", "Value": f"{avg_degree:.2f}", "Target": ">2 (no dead ends)"},
        {"Metric": "Synthetic (healed) edges", "Value": str(n_synthetic), "Target": "Low"},
        {"Metric": "Total nodes", "Value": f"{G.number_of_nodes():,}", "Target": "—"},
        {"Metric": "Total edges", "Value": f"{G.number_of_edges():,}", "Target": "—"},
    ])
    st.dataframe(metrics_df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("PS4 Target Checklist")
    st.caption("Segmentation metrics require running eval/full_eval.py separately.")

    checks = {
        "LCC fraction > 0.90": lcc_frac > 0.90,
        "Global efficiency > 0": base_eff > 0,
        "Critical nodes < 15% of total": n_critical / max(G.number_of_nodes(), 1) < 0.15,
        "Healed edges present (gap bridging)": n_synthetic > 0,
        "Graph has ≥2 nodes": G.number_of_nodes() >= 2,
    }
    for label, passed in checks.items():
        icon = "✅" if passed else "❌"
        st.markdown(f"{icon} {label}")

    st.divider()
    st.subheader("Zone Distribution")
    zone_counts = {"critical": 0, "vulnerable": 0, "resilient": 0}
    for z in zones.values():
        zone_counts[z] = zone_counts.get(z, 0) + 1

    zone_df = pd.DataFrame([
        {"Zone": k, "Count": v, "Pct": f"{100*v/max(sum(zone_counts.values()),1):.1f}%"}
        for k, v in zone_counts.items()
    ])
    st.dataframe(zone_df, use_container_width=True, hide_index=True)
