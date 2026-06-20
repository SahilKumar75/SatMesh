from __future__ import annotations
import json
import os
import pickle
import time
from pathlib import Path
from typing import Generator


def run_pipeline(
    city_id: str,
    checkpoint: str,
    cities_path: str = "cities.json",
    force_rerun: bool = False,
    model_type: str = "segformer",
) -> Generator[dict, None, None]:
    import torch
    from src.data.city_config import load_city
    from src.model.infer import load_model, predict_mask
    from src.graph.skeleton import skeletonize_mask, extract_nodes, trace_edges, build_skeleton_graph
    from src.graph.heal import heal_gaps, add_geo_coords
    from src.graph.dem import fetch_srtm_dem, attach_elevation, mark_flood_nodes
    from src.graph.criticality import compute_betweenness, ablation_curve
    from src.graph.zones import classify_zones, zones_to_geojson
    from src.graph.apls import compute_apls

    cfg = load_city(city_id)
    out_dir = Path("outputs") / city_id
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_path = out_dir / "summary.json"
    if summary_path.exists() and not force_rerun:
        with open(summary_path) as f:
            yield {"step": "done", "pct": 100, "cached": True, "summary": json.load(f)}
        return

    device = "cuda" if torch.cuda.is_available() else "cpu"
    log = []

    def emit(step, pct, **extra):
        ev = {"step": step, "pct": pct, "ts": time.time(), **extra}
        log.append(ev)
        yield ev

    yield from emit("loading_model", 0)
    model = load_model(checkpoint, device, model_type=model_type, in_channels=4)

    yield from emit("segmenting", 10)
    sat_path = str(out_dir / "satellite.jpg")
    nir_path = str(out_dir / "nir.tif") if (out_dir / "nir.tif").exists() else None
    mask = predict_mask(model, sat_path, device, nir_path=nir_path)
    mask_path = str(out_dir / "road_mask.png")
    import cv2
    cv2.imwrite(mask_path, mask)

    yield from emit("skeletonizing", 25)
    skel = skeletonize_mask(mask_path)
    nodes = extract_nodes(skel)
    edges = trace_edges(skel, nodes)
    G_skel = build_skeleton_graph(nodes, edges, cfg.pixel_m)

    yield from emit("healing", 38)
    pixel_size_deg = cfg.pixel_m / 111_000.0
    G_healed = heal_gaps(G_skel, max_gap_m=50.0, angular_threshold=0.3)
    G_healed = add_geo_coords(G_healed, cfg.center[0], cfg.center[1],
                               pixel_size_deg=pixel_size_deg)

    lcc_before = max((len(c) for c in __import__("networkx").connected_components(G_skel)), default=0)
    lcc_after  = max((len(c) for c in __import__("networkx").connected_components(G_healed)), default=0)
    connectivity_ratio = lcc_after / max(G_healed.number_of_nodes(), 1)

    yield from emit("elevation", 48)
    dem_path = str(out_dir / "dem.tif")
    try:
        dem_arr, gt = fetch_srtm_dem(cfg.bbox, dem_path)
        G_healed = attach_elevation(G_healed, dem_arr, gt)
        flood_nodes = mark_flood_nodes(G_healed, cfg.flood_threshold_m)
    except Exception:
        flood_nodes = set()

    yield from emit("criticality", 58)
    bc = compute_betweenness(G_healed)
    ablation = ablation_curve(G_healed, bc, max_removals=10)

    graph_path = str(out_dir / "healed_graph.gpickle")
    with open(graph_path, "wb") as f:
        pickle.dump(G_healed, f, protocol=pickle.HIGHEST_PROTOCOL)

    yield from emit("zones", 75)
    zones = classify_zones(G_healed, bc)
    geojson = zones_to_geojson(G_healed, zones, bc)
    geojson_path = out_dir / "zones.geojson"
    with open(geojson_path, "w") as f:
        json.dump(geojson, f)

    yield from emit("apls", 85)
    apls_score = 0.0
    try:
        import osmnx as ox
        import networkx as nx
        south, west, north, east = cfg.bbox[0], cfg.bbox[1], cfg.bbox[2], cfg.bbox[3]
        G_osm = ox.graph_from_bbox(north, south, east, west, network_type="drive")
        G_osm_u = nx.Graph(G_osm)
        apls_score = compute_apls(G_healed, G_osm_u, n_samples=200)
    except Exception:
        pass

    ri3 = ablation[3]["resilience_index"] if len(ablation) > 3 else 0.0
    ri5 = ablation[5]["resilience_index"] if len(ablation) > 5 else 0.0
    n_critical = sum(1 for z in zones.values() if z == "critical")

    summary = {
        "city_id": city_id,
        "n_nodes": G_healed.number_of_nodes(),
        "n_edges": G_healed.number_of_edges(),
        "synthetic_edges": sum(1 for _, _, d in G_healed.edges(data=True) if d.get("synthetic")),
        "lcc_before_heal": lcc_before,
        "lcc_after_heal": lcc_after,
        "connectivity_ratio": round(connectivity_ratio, 4),
        "apls": round(apls_score, 4),
        "resilience_index_3": round(ri3, 4),
        "resilience_index_5": round(ri5, 4),
        "gatekeeper_count": n_critical,
        "flood_critical_count": sum(
            1 for n, d in G_healed.nodes(data=True)
            if d.get("flood_vulnerable") and zones.get(n) == "critical"
        ),
        "ablation": ablation,
    }

    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    log_path = out_dir / "pipeline_log.jsonl"
    with open(log_path, "w") as f:
        for ev in log:
            f.write(json.dumps(ev) + "\n")

    yield from emit("done", 100, summary=summary)
