import argparse
import pickle
import json
import networkx as nx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", required=True, help="healed_graph.gpickle")
    ap.add_argument("--city_id", required=True)
    ap.add_argument("--n_samples", type=int, default=200)
    args = ap.parse_args()

    with open(args.graph, "rb") as f:
        G_pred = pickle.load(f)

    import osmnx as ox
    from src.data.city_config import load_city
    from src.graph.apls import compute_apls

    cfg = load_city(args.city_id)
    south, west, north, east = cfg.bbox[0], cfg.bbox[1], cfg.bbox[2], cfg.bbox[3]
    G_osm = ox.graph_from_bbox(north, south, east, west, network_type="drive")
    G_osm_u = nx.Graph(G_osm)

    score = compute_apls(G_pred, G_osm_u, n_samples=args.n_samples)
    print(json.dumps({"apls": round(score, 4), "city": args.city_id, "n_samples": args.n_samples}, indent=2))


if __name__ == "__main__":
    main()
