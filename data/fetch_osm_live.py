"""
data/fetch_osm_live.py — fetch a live OSM road graph for any bounding box.

This is the real-time layer: any city, any zoom, <1 second. No training needed.
Used by the pipeline and dashboard to get an instant baseline road graph.

Usage:
    python data/fetch_osm_live.py --city "Bengaluru, India" --out outputs/osm_bengaluru.graphml
    python data/fetch_osm_live.py --bbox 12.92,77.55,13.02,77.65 --out outputs/osm_bbox.graphml
    python data/fetch_osm_live.py --bbox 12.92,77.55,13.02,77.65 --format geojson --out outputs/osm.geojson
"""

from __future__ import annotations
import argparse, json, os, sys, time

def _require_osmnx():
    try:
        import osmnx as ox
        return ox
    except ImportError:
        print("osmnx not installed. Run: pip install osmnx")
        sys.exit(1)


def fetch_by_city(city: str, network_type: str = "drive") -> "nx.MultiDiGraph":
    ox = _require_osmnx()
    print(f"[OSM] Fetching road graph for: {city}")
    t0 = time.time()
    G = ox.graph_from_place(city, network_type=network_type)
    print(f"[OSM] {G.number_of_nodes()} nodes, {G.number_of_edges()} edges — {time.time()-t0:.1f}s")
    return G


def fetch_by_bbox(
    south: float, west: float, north: float, east: float,
    network_type: str = "drive",
) -> "nx.MultiDiGraph":
    ox = _require_osmnx()
    print(f"[OSM] Fetching road graph for bbox ({south:.4f},{west:.4f}) → ({north:.4f},{east:.4f})")
    t0 = time.time()
    G = ox.graph_from_bbox(north, south, east, west, network_type=network_type)
    print(f"[OSM] {G.number_of_nodes()} nodes, {G.number_of_edges()} edges — {time.time()-t0:.1f}s")
    return G


def osm_to_networkx_simple(G_ox) -> "nx.Graph":
    """
    Convert osmnx MultiDiGraph to a simple undirected NetworkX Graph
    with lat/lon attributes and length edge weights — compatible with
    the SatMesh heal + criticality pipeline.
    """
    import networkx as nx
    G = nx.Graph()
    for node, data in G_ox.nodes(data=True):
        G.add_node(node, lat=data["y"], lon=data["x"])
    for u, v, data in G_ox.edges(data=True):
        length = data.get("length", 1.0)
        existing = G.get_edge_data(u, v)
        if existing is None or length < existing.get("length", float("inf")):
            G.add_edge(u, v, length=float(length), synthetic=False)
    return G


def save_geojson(G_ox, out_path: str) -> None:
    ox = _require_osmnx()
    edges = ox.graph_to_gdfs(G_ox, nodes=False)
    edges.to_file(out_path, driver="GeoJSON")
    print(f"[OSM] GeoJSON saved → {out_path}")


def save_graphml(G_ox, out_path: str) -> None:
    ox = _require_osmnx()
    ox.save_graphml(G_ox, out_path)
    print(f"[OSM] GraphML saved → {out_path}")


def save_pickle(G_simple, out_path: str) -> None:
    import pickle
    with open(out_path, "wb") as f:
        pickle.dump(G_simple, f)
    print(f"[OSM] Pickle saved → {out_path}")


def save_meta(G_ox, bbox, out_dir: str) -> None:
    import networkx as nx
    meta = {
        "n_nodes": G_ox.number_of_nodes(),
        "n_edges": G_ox.number_of_edges(),
        "bbox": {"south": bbox[0], "west": bbox[1], "north": bbox[2], "east": bbox[3]},
        "crs": "EPSG:4326",
        "source": "OpenStreetMap via osmnx",
    }
    path = os.path.join(out_dir, "osm_meta.json")
    with open(path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"[OSM] Meta saved → {path}")


def main():
    ap = argparse.ArgumentParser(description="Fetch OSM road graph for any city or bounding box")
    ap.add_argument("--city",    help='City name e.g. "Bengaluru, India"')
    ap.add_argument("--bbox",    help="south,west,north,east in decimal degrees e.g. 12.92,77.55,13.02,77.65")
    ap.add_argument("--out",     default="outputs/osm_graph.graphml", help="Output file path")
    ap.add_argument("--format",  choices=["graphml", "geojson", "pickle", "all"], default="all")
    ap.add_argument("--network", default="drive", choices=["drive", "walk", "bike", "all"])
    args = ap.parse_args()

    if not args.city and not args.bbox:
        print("Defaulting to Bengaluru core bbox")
        args.bbox = "12.92,77.55,13.02,77.65"

    out_dir = os.path.dirname(args.out) or "outputs"
    os.makedirs(out_dir, exist_ok=True)

    if args.city:
        G_ox = fetch_by_city(args.city, args.network)
        nodes = list(G_ox.nodes(data=True))
        lats = [d["y"] for _, d in nodes]
        lons = [d["x"] for _, d in nodes]
        bbox = (min(lats), min(lons), max(lats), max(lons))
    else:
        parts = [float(x) for x in args.bbox.split(",")]
        assert len(parts) == 4, "bbox must be south,west,north,east"
        bbox = tuple(parts)
        G_ox = fetch_by_bbox(*bbox, network_type=args.network)

    stem = os.path.splitext(args.out)[0]

    if args.format in ("graphml", "all"):
        save_graphml(G_ox, stem + ".graphml")

    if args.format in ("geojson", "all"):
        try:
            save_geojson(G_ox, stem + ".geojson")
        except Exception as e:
            print(f"[OSM] GeoJSON export skipped: {e}")

    if args.format in ("pickle", "all"):
        G_simple = osm_to_networkx_simple(G_ox)
        save_pickle(G_simple, stem + "_simple.gpickle")

    save_meta(G_ox, bbox, out_dir)
    print(f"\n[OSM] Done. Files in {out_dir}/")


if __name__ == "__main__":
    main()
