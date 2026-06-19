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
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception as exc:
        st.error(f"Failed to load graph `{path}`: {exc}")
        st.stop()


@st.cache_resource
def load_criticality(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as exc:
        st.warning(f"Could not load criticality JSON `{path}`: {exc}")
        return {}


@st.cache_data
def compute_bc(_G: nx.Graph) -> dict:
    from track_b.criticality import compute_betweenness
    return compute_betweenness(_G)


# ── Geo projection ──────────────────────────────────────────────────────────────
# Leaflet needs real lat/lon. Pixel-grid graphs (row/col) are projected onto a
# placeholder city (Bengaluru, per the PS4 wireframe) so the network renders on a
# real basemap. If the graph already carries valid lat/lon, those are used as-is.

CITY_CENTER = (12.9716, 77.5946)   # Bengaluru
CITY_SPAN_DEG = 0.045              # ~5 km tile


@st.cache_data
def geo_project(_G: nx.Graph) -> dict:
    nodes = list(_G.nodes)
    lats = np.array([_G.nodes[n].get("lat", np.nan) for n in nodes])
    if np.all(np.isfinite(lats)) and np.nanmax(np.abs(lats)) <= 90:
        return {n: (float(_G.nodes[n]["lat"]), float(_G.nodes[n]["lon"])) for n in nodes}
    # project pixel row/col into a lat/lon box around the city centre
    rows = np.array([_G.nodes[n].get("row", _G.nodes[n].get("y", 0)) for n in nodes], float)
    cols = np.array([_G.nodes[n].get("col", _G.nodes[n].get("x", 0)) for n in nodes], float)
    r0, r1 = rows.min(), rows.max()
    c0, c1 = cols.min(), cols.max()
    rr = (rows - r0) / (r1 - r0 + 1e-9)
    cc = (cols - c0) / (c1 - c0 + 1e-9)
    lat = CITY_CENTER[0] + CITY_SPAN_DEG * (0.5 - rr)   # row increases southward
    lon = CITY_CENTER[1] + CITY_SPAN_DEG * (cc - 0.5)
    return {n: (float(lat[i]), float(lon[i])) for i, n in enumerate(nodes)}


# ── Colour: green (low) → red (high betweenness) ────────────────────────────────

def _bc_colour(v: float, vmax: float) -> str:
    # Green (low betweenness) -> amber -> red (gatekeeper). Tuned for legibility
    # on a dark CartoDB basemap: keep a green floor so low nodes stay visible.
    r = v / vmax if vmax > 0 else 0.0
    red = int(60 + 195 * r)
    grn = int(200 * (1 - r) + 40 * r)
    blu = int(70 * (1 - r))
    return f"#{red:02x}{grn:02x}{blu:02x}"


# ── Nearest-node lookup ─────────────────────────────────────────────────────────

@st.cache_data
def _node_arrays(_G: nx.Graph, _geo: dict):
    nodes = list(_G.nodes)
    coords = np.array([_geo[n] for n in nodes])
    return nodes, coords


def find_nearest_node(G, geo, lat, lon, max_dist):
    nodes, coords = _node_arrays(G, geo)
    tree = cKDTree(coords)
    dist, idx = tree.query([lat, lon])
    return nodes[idx] if dist <= max_dist else None


# ── Map ─────────────────────────────────────────────────────────────────────────

def build_map(G, geo, bc, disabled, reroute_path):
    bc_max = max(bc.values()) if bc else 1.0
    coords = np.array([geo[n] for n in G.nodes])
    centre = (coords[:, 0].mean(), coords[:, 1].mean()) if len(coords) else CITY_CENTER
    m = folium.Map(location=centre, zoom_start=15, tiles="CartoDB dark_matter",
                   control_scale=True)

    reroute_set = set(zip(reroute_path[:-1], reroute_path[1:]))
    for u, v, data in G.edges(data=True):
        ul = geo[u]; vl = geo[v]
        is_rr = (u, v) in reroute_set or (v, u) in reroute_set
        is_syn = data.get("synthetic", False)
        # On dark tiles: amber reroute, bright-green healed bridge, muted slate base.
        colour = "#f59e0b" if is_rr else ("#22c55e" if is_syn else "#475569")
        weight = 6 if is_rr else (3 if is_syn else 1.2)
        opacity = 0.95 if (is_rr or is_syn) else 0.55
        folium.PolyLine([ul, vl], color=colour, weight=weight, opacity=opacity).add_to(m)

    for n in sorted(bc, key=bc.get, reverse=True)[:500]:
        lat, lon = geo[n]
        off = n in disabled
        fill = "#1a0508" if off else _bc_colour(bc.get(n, 0), bc_max)
        ring = "#f43f5e" if off else fill
        folium.CircleMarker(
            location=(lat, lon),
            radius=11 if off else max(3, int(bc.get(n, 0) / bc_max * 9)),
            color=ring, weight=3 if off else 1,
            fill=True, fill_color=fill, fill_opacity=0.95,
            tooltip=f"Node {n} — betweenness {bc.get(n, 0):.3f}" + ("  ·  DISABLED" if off else ""),
        ).add_to(m)
    return m


# ── Helpers ─────────────────────────────────────────────────────────────────────

def _lcc(G):
    return len(max(nx.connected_components(G), key=len)) if G.number_of_nodes() else 0


def _inject_css():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600&display=swap');

        :root {
            --sm-bg:        #0a0f1a;
            --sm-surface:   #111a2b;
            --sm-surface-2: #16223a;
            --sm-border:    #1e2d47;
            --sm-text:      #e2e8f0;
            --sm-muted:     #7e8da6;
            --sm-accent:    #38bdf8;
            --sm-good:      #22c55e;
            --sm-bad:       #f43f5e;
            --sm-warn:      #f59e0b;
        }

        html, body, [class*="css"], .stApp, .stMarkdown, p, span, label, div {
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }
        .stApp { background: var(--sm-bg); }

        /* hide default Streamlit chrome for a cleaner product look */
        #MainMenu, header[data-testid="stHeader"], footer { visibility: hidden; }
        .block-container { padding-top: 1.4rem; padding-bottom: 2.5rem; max-width: 1500px; }

        /* ── App header / title bar ─────────────────────────────── */
        .sm-header {
            display: flex; align-items: center; gap: 16px;
            padding: 18px 22px; margin-bottom: 18px;
            background: linear-gradient(135deg, #101a2e 0%, #0c1322 100%);
            border: 1px solid var(--sm-border);
            border-radius: 12px;
            box-shadow: 0 1px 0 rgba(255,255,255,.03) inset, 0 8px 24px rgba(0,0,0,.35);
        }
        .sm-mark {
            width: 46px; height: 46px; flex: 0 0 46px;
            border-radius: 10px;
            background: linear-gradient(135deg, var(--sm-accent) 0%, #0ea5e9 60%, #2563eb 100%);
            display: flex; align-items: center; justify-content: center;
        }
        .sm-wordmark {
            font-size: 1.5rem; font-weight: 800; letter-spacing: .5px;
            color: var(--sm-text); line-height: 1.1;
        }
        .sm-wordmark .sm-accent { color: var(--sm-accent); }
        .sm-sub {
            font-size: .80rem; color: var(--sm-muted); margin-top: 2px;
            letter-spacing: .2px; font-weight: 500;
        }
        .sm-badge {
            margin-left: auto; align-self: flex-start;
            font-size: .68rem; font-weight: 600; letter-spacing: .8px;
            text-transform: uppercase;
            color: var(--sm-accent);
            border: 1px solid var(--sm-border);
            background: rgba(56,189,248,.08);
            padding: 5px 10px; border-radius: 6px;
        }

        /* ── Metric cards ───────────────────────────────────────── */
        .sm-card {
            background: var(--sm-surface);
            border: 1px solid var(--sm-border);
            border-radius: 11px;
            padding: 14px 16px;
            height: 100%;
            box-shadow: 0 4px 14px rgba(0,0,0,.25);
        }
        .sm-card .sm-label {
            font-size: .70rem; font-weight: 600; letter-spacing: .9px;
            text-transform: uppercase; color: var(--sm-muted);
        }
        .sm-card .sm-value {
            font-size: 1.9rem; font-weight: 700; color: var(--sm-text);
            font-variant-numeric: tabular-nums; line-height: 1.2; margin-top: 6px;
            font-feature-settings: "tnum" 1;
        }
        .sm-card .sm-delta {
            font-size: .80rem; font-weight: 600; margin-top: 4px;
            font-variant-numeric: tabular-nums;
        }
        .sm-delta.good { color: var(--sm-good); }
        .sm-delta.bad  { color: var(--sm-bad); }
        .sm-delta.flat { color: var(--sm-muted); }

        /* ── Section panels ─────────────────────────────────────── */
        .sm-panel {
            background: var(--sm-surface);
            border: 1px solid var(--sm-border);
            border-radius: 11px;
            padding: 4px 14px 10px 14px;
            margin-bottom: 14px;
        }
        .sm-panel-title {
            font-size: .80rem; font-weight: 700; letter-spacing: .6px;
            text-transform: uppercase; color: var(--sm-text);
            padding: 12px 2px 8px 2px;
            border-bottom: 1px solid var(--sm-border);
            margin-bottom: 8px;
        }
        .sm-panel-title .dot {
            display:inline-block; width:7px; height:7px; border-radius:50%;
            background: var(--sm-accent); margin-right:8px; vertical-align: middle;
        }

        /* map container framing */
        iframe { border-radius: 11px; border: 1px solid var(--sm-border); }

        /* dataframes */
        [data-testid="stDataFrame"] { border-radius: 9px; }

        /* sidebar */
        section[data-testid="stSidebar"] {
            background: #0c1322;
            border-right: 1px solid var(--sm-border);
        }
        .sm-side-head {
            font-size: .72rem; font-weight: 700; letter-spacing: 1px;
            text-transform: uppercase; color: var(--sm-accent);
            margin: 4px 0 2px 0;
        }
        section[data-testid="stSidebar"] .stButton button {
            border-radius: 8px; font-weight: 600;
            border: 1px solid var(--sm-border);
        }

        .sm-legend { font-size:.78rem; color: var(--sm-muted); margin: 4px 0 8px 0; }
        .sm-legend b { color: var(--sm-text); font-weight:600; }
        .sm-chip { display:inline-block; width:9px; height:9px; border-radius:2px;
                   margin: 0 5px 0 12px; vertical-align: middle; }
        </style>
        """,
        unsafe_allow_html=True,
    )


_SM_GLYPH = (
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" '
    'xmlns="http://www.w3.org/2000/svg">'
    '<circle cx="6" cy="6" r="2.2" fill="white"/>'
    '<circle cx="18" cy="7" r="2.2" fill="white"/>'
    '<circle cx="12" cy="17" r="2.2" fill="white"/>'
    '<path d="M6 6 L18 7 M6 6 L12 17 M18 7 L12 17" stroke="white" '
    'stroke-width="1.6" stroke-linecap="round"/></svg>'
)


def _metric_card(col, label, value, delta=None, good=None):
    cls = "flat" if good is None else ("good" if good else "bad")
    delta_html = f'<div class="sm-delta {cls}">{delta}</div>' if delta is not None else \
                 '<div class="sm-delta flat">&nbsp;</div>'
    col.markdown(
        f'<div class="sm-card"><div class="sm-label">{label}</div>'
        f'<div class="sm-value">{value}</div>{delta_html}</div>',
        unsafe_allow_html=True,
    )


def main():
    st.set_page_config(
        page_title="SatMesh — Route Resilience",
        page_icon="🛰️",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": None,
            "Report a bug": None,
            "About": "SatMesh · ISRO BAH 2026 PS4 · Occlusion-Robust Road Resilience",
        },
    )
    _inject_css()
    st.markdown(
        f'<div class="sm-header">'
        f'<div class="sm-mark">{_SM_GLYPH}</div>'
        f'<div><div class="sm-wordmark">Sat<span class="sm-accent">Mesh</span></div>'
        f'<div class="sm-sub">Occlusion-Robust Road Extraction &amp; Graph-Theoretic '
        f'Resilience Analysis &middot; ISRO BAH 2026 PS4</div></div>'
        f'<div class="sm-badge">Bengaluru &middot; Live Stress Test</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    args = _parse_args()
    with st.sidebar:
        st.markdown('<div class="sm-side-head">Data Sources</div>', unsafe_allow_html=True)
        graph_path = st.text_input("Healed graph (.gpickle)", value=args.graph)
        crit_path  = st.text_input("Criticality JSON", value=args.criticality)

    if not os.path.exists(graph_path):
        st.warning(f"Graph not found: `{graph_path}`. Run `track_b/run_trackb.py` first, "
                   "or point to a healed-graph pickle in the sidebar.")
        return

    G = load_graph(graph_path)
    with st.spinner("Computing betweenness centrality…"):
        bc = compute_bc(G)
    geo = geo_project(G)
    ranked = sorted(bc, key=bc.get, reverse=True)
    ntype = type(ranked[0]) if ranked else int
    crit = load_criticality(crit_path) if os.path.exists(crit_path) else None

    # click tolerance from the projected geo extent
    coords = np.array([geo[n] for n in G.nodes])
    span = max(np.ptp(coords[:, 0]), np.ptp(coords[:, 1]), 1e-6)
    click_tol = span * 0.04

    ss = st.session_state
    ss.setdefault("disabled", [])
    ss.setdefault("reroute_path", [])
    ss.setdefault("reroute_info", None)

    # ── Sidebar controls ──────────────────────────────────────────────────────
    with st.sidebar:
        st.divider()
        st.markdown('<div class="sm-side-head">Failure Simulation</div>', unsafe_allow_html=True)
        if st.button("▲  Disable top 3 gatekeepers", use_container_width=True,
                     type="primary",
                     help="Remove the 3 highest-betweenness intersections to simulate a catastrophic failure"):
            ss["disabled"] = [ranked[i] for i in range(min(3, len(ranked)))]
            ss["reroute_path"] = []; ss["reroute_info"] = None
            st.rerun()
        if st.button("Clear all", use_container_width=True,
                     help="Restore all disabled intersections"):
            ss["disabled"] = []; ss["reroute_path"] = []; ss["reroute_info"] = None
            st.rerun()

        st.divider()
        st.markdown('<div class="sm-side-head">Route Under Disruption</div>', unsafe_allow_html=True)
        node_opts = [str(n) for n in G.nodes]
        src = st.selectbox("From", node_opts, index=0)
        dst = st.selectbox("To", node_opts, index=min(len(node_opts) - 1, 20))
        if st.button("Compute reroute", use_container_width=True,
                     help="Find shortest path between these nodes under current failures"):
            if src == dst:
                st.error("Source and destination must be different nodes.")
            else:
                from track_b.criticality import compute_reroute
                try:
                    s, d = ntype(src), ntype(dst)
                    with st.spinner("Routing…"):
                        base_path, base_len = compute_reroute(G, [], s, d)
                        new_path,  new_len  = compute_reroute(G, ss["disabled"], s, d)
                    ss["reroute_path"] = new_path
                    if new_len == float("inf"):
                        ss["reroute_info"] = ("cut", base_len, None)
                    else:
                        inc = (new_len - base_len) / base_len * 100 if base_len > 0 else 0
                        ss["reroute_info"] = ("ok", base_len, (new_len, inc))
                except Exception as exc:
                    st.error(f"Reroute failed: {exc}")
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
    _metric_card(c1, "Intersections", f"{G.number_of_nodes():,}")
    _metric_card(c2, "Disabled", f"{len(disabled)}",
                 delta=(f"+{len(disabled)} failed" if disabled else None),
                 good=False if disabled else None)
    _metric_card(c3, "Connected reach", f"{retained:.0f}%",
                 delta=(f"{retained - 100:.0f} pts" if disabled else None),
                 good=False if disabled else None)
    _metric_card(c4, "Intersections isolated", f"{isolated:,}",
                 delta=(f"+{isolated:,} cut off" if disabled else None),
                 good=(isolated == 0) if disabled else None)
    _metric_card(c5, "Separate areas", f"{components}",
                 delta=("fragmented" if components > 1 else "intact"),
                 good=(components == 1))

    info = ss["reroute_info"]
    if info:
        st.write("")
        if info[0] == "cut":
            st.error(f"Route severed — destination is unreachable after the failure "
                     f"(baseline path was {info[1]:.0f} m).")
        else:
            base_len, (new_len, inc) = info[1], info[2]
            st.warning(f"Detour required: travel distance **{base_len:.0f} m → {new_len:.0f} m**, "
                       f"a **+{inc:.0f}%** increase in travel time.")

    # ── Onboarding hint ───────────────────────────────────────────────────────
    if not disabled:
        st.info(
            "**Try it:** click any intersection on the map to disable it, "
            "then use *Compute reroute* to see the detour — or hit "
            "*Disable top 3 gatekeepers* for a one-click stress test.",
            icon="ℹ️",
        )

    # ── Map + side panels ─────────────────────────────────────────────────────
    st.write("")
    map_col, side = st.columns([3, 1], gap="medium")
    with map_col:
        st.markdown(
            '<div class="sm-legend">'
            '<span class="sm-chip" style="background:#22c55e"></span><b>Low</b> betweenness'
            '<span class="sm-chip" style="background:#f59e0b"></span>rising'
            '<span class="sm-chip" style="background:#dd3030"></span><b>Gatekeeper</b>'
            '<span class="sm-chip" style="background:#0a0f1a;border:2px solid #f43f5e"></span><b>Disabled</b>'
            '<span class="sm-chip" style="background:#22c55e"></span>healed bridge'
            '<span class="sm-chip" style="background:#f59e0b"></span>reroute'
            '</div>',
            unsafe_allow_html=True,
        )
        with st.spinner("Rendering map…"):
            fmap = build_map(G, geo, bc, disabled, ss["reroute_path"])
        md = st_folium(fmap, width=None, height=560, key="map")
        clk = (md or {}).get("last_object_clicked")
        if clk and clk.get("lat") is not None:
            near = find_nearest_node(G, geo, clk["lat"], clk["lng"], click_tol)
            if near is not None and near not in disabled:
                ss["disabled"].append(near)
                ss["reroute_path"] = []; ss["reroute_info"] = None
                st.rerun()

    with side:
        st.markdown(
            '<div class="sm-panel-title"><span class="dot"></span>Top Gatekeeper Nodes</div>',
            unsafe_allow_html=True,
        )
        st.dataframe(
            pd.DataFrame([(str(n), round(bc[n], 3)) for n in ranked[:10]],
                         columns=["Node", "Betweenness"]).set_index("Node"),
            use_container_width=True,
        )
        if crit and "ablation" in crit:
            st.markdown(
                '<div class="sm-panel-title"><span class="dot"></span>Resilience Under Attack</div>',
                unsafe_allow_html=True,
            )
            abl = crit["ablation"]
            st.line_chart(
                pd.DataFrame({
                    "Resilience Index": [r["resilience_index"] for r in abl],
                    "Connected fraction": [r["lcc_fraction"] for r in abl],
                }, index=[r["n_removed"] for r in abl]),
                color=["#38bdf8", "#f59e0b"],
            )
            st.caption("Adaptive betweenness attack — both fall as gatekeepers are removed.")

    if crit and "ablation" in crit:
        with st.expander("Ablation detail (per-node removal)"):
            abl_df = pd.DataFrame(crit["ablation"]).set_index("n_removed")
            st.dataframe(abl_df, use_container_width=True)

        st.divider()
        dl1, dl2 = st.columns(2)
        with dl1:
            st.download_button(
                "⬇ Download ablation CSV",
                data=pd.DataFrame(crit["ablation"]).to_csv(index=False),
                file_name="satmesh_ablation.csv",
                mime="text/csv",
                use_container_width=True,
                help="Per-step resilience metrics (Resilience Index, LCC fraction, efficiency)",
            )
        with dl2:
            st.download_button(
                "⬇ Download criticality JSON",
                data=json.dumps(crit, indent=2),
                file_name="satmesh_criticality.json",
                mime="application/json",
                use_container_width=True,
                help="Full betweenness centrality + ablation data as JSON",
            )


if __name__ == "__main__":
    main()
