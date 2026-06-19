"""
pipeline/run.py — end-to-end SatMesh runner.

Usage:
    # Manual lat/lon:
    python pipeline/run.py \\
        --image     img.jpg \\
        --checkpoint best_model.pth \\
        --pixel_m   0.5 \\
        --top_left_lat 12.98 --top_left_lon 77.58 \\
        --output_dir outputs/

    # Auto-georef from Bhoonidhi GeoTIFF (overrides --top_left_lat/lon):
    python pipeline/run.py \\
        --image     img.jpg \\
        --checkpoint best_model.pth \\
        --bhoonidhi_tif bengaluru_tile.tif \\
        --output_dir outputs/

Produces:
    outputs/
        road_mask.png
        healed_graph.gpickle
        resilience_curve.png
        criticality.json
        track_a_metrics.csv   (only if --test_pairs provided)
        track_b_metrics.json
        summary.json
"""

from __future__ import annotations
import argparse, json, os, sys, time


def _lat_lon_from_tif(tif_path: str) -> tuple[float, float]:
    """Extract top-left (lat, lon) from a georeferenced GeoTIFF via rasterio."""
    try:
        import rasterio
        from rasterio.crs import CRS
        from pyproj import Transformer
    except ImportError:
        raise SystemExit(
            "rasterio and pyproj are required for --bhoonidhi_tif. "
            "Run: pip install rasterio pyproj"
        )
    with rasterio.open(tif_path) as ds:
        tf = ds.transform
        # top-left pixel centre in the dataset CRS
        x_tl, y_tl = tf.c, tf.f
        src_crs = ds.crs or CRS.from_epsg(4326)
    if src_crs.to_epsg() == 4326:
        return float(y_tl), float(x_tl)
    to_wgs84 = Transformer.from_crs(src_crs, CRS.from_epsg(4326), always_xy=True)
    lon, lat = to_wgs84.transform(x_tl, y_tl)
    return float(lat), float(lon)

# allow running from repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _import_osmnx():
    try:
        import osmnx as ox
        return ox
    except ImportError:
        return None


def run_pipeline(
    input_image:   str,
    checkpoint:    str,
    output_dir:    str,
    pixel_m:       float = 0.5,
    max_gap_m:     float = 50.0,
    top_left_lat:  float = 0.0,
    top_left_lon:  float = 0.0,
    img_size:      int   = 512,
    threshold:     float = 0.5,
    max_removals:  int   = 10,
    test_pairs:    str | None = None,
    osm_graphml:   str | None = None,
) -> dict:
    """
    Run the full Track A + Track B pipeline for a single satellite image.
    Returns a summary dict with all output paths and metric values.
    """
    os.makedirs(output_dir, exist_ok=True)
    t0 = time.time()
    summary: dict = {"input_image": input_image, "outputs": {}, "metrics": {}}

    # ── Step 1: Road segmentation ─────────────────────────────────────────────
    print("\n[pipeline] Step 1 — Road segmentation")
    from track_a.infer import load_model, predict_mask, postprocess_mask, _device

    device = _device()
    print(f"  device: {device}")
    if not os.path.exists(checkpoint):
        raise FileNotFoundError(
            f"Checkpoint not found: {checkpoint}\n"
            "  Train the model first (track_a/road_segmentation.py) or point --checkpoint "
            "to an existing best_model.pth file."
        )
    model = load_model(checkpoint, device, in_channels=3)

    mask = predict_mask(model, input_image, device, img_size=img_size,
                        threshold=threshold)
    mask = postprocess_mask(mask)

    import cv2
    from track_a.infer import canopy_uncertainty_mask
    mask_path = os.path.join(output_dir, "road_mask.png")
    cv2.imwrite(mask_path, mask)
    summary["outputs"]["road_mask"] = mask_path
    print(f"  saved → {mask_path}")

    raw_img = cv2.imread(input_image)
    if raw_img is not None:
        canopy_path = os.path.join(output_dir, "canopy_uncertainty.png")
        cv2.imwrite(canopy_path, canopy_uncertainty_mask(raw_img))
        summary["outputs"]["canopy_uncertainty"] = canopy_path
        print(f"  saved → {canopy_path}")

    # ── Step 2: Skeleton extraction + gap healing ─────────────────────────────
    print("\n[pipeline] Step 2 — Skeleton extraction + gap healing")
    from track_b.heal import run_heal_pipeline

    graph_path = os.path.join(output_dir, "healed_graph.gpickle")
    G_healed, G_skeleton = run_heal_pipeline(
        mask_path, graph_path,
        pixel_m=pixel_m,
        top_left_lat=top_left_lat,
        top_left_lon=top_left_lon,
        max_gap_m=max_gap_m,
        return_skeleton=True,
    )
    summary["outputs"]["healed_graph"] = graph_path

    # ── Step 3: Criticality analysis ─────────────────────────────────────────
    print("\n[pipeline] Step 3 — Criticality analysis")
    from track_b.criticality import run_criticality

    crit = run_criticality(graph_path, output_dir, max_removals=max_removals)
    summary["outputs"]["criticality_json"]    = os.path.join(output_dir, "criticality.json")
    summary["outputs"]["resilience_curve"]    = os.path.join(output_dir, "resilience_curve.png")

    if crit["ablation"]:
        last = crit["ablation"][-1]
        summary["metrics"]["resilience_index"] = last["resilience_index"]
        summary["metrics"]["lcc_fraction_after_ablation"] = last["lcc_fraction"]

    # ── Step 4: OSM baseline + Track B metrics ────────────────────────────────
    print("\n[pipeline] Step 4 — Track B metrics")
    import networkx as nx
    from eval.metrics import evaluate_track_b

    ox = _import_osmnx()
    G_osm = None
    if osm_graphml and os.path.exists(osm_graphml):
        print(f"  loading OSM graph from {osm_graphml}")
        G_osm = nx.Graph(ox.load_graphml(osm_graphml))
    elif ox and top_left_lat != 0.0 and top_left_lon != 0.0:
        # best-effort OSM download for the area covered by the image
        print("  downloading OSM road graph …")
        try:
            center = (top_left_lat - 0.005, top_left_lon + 0.005)
            G_osm_raw = ox.graph_from_point(center, dist=600, network_type="drive")
            G_osm = nx.Graph(G_osm_raw)
            osm_save = os.path.join(output_dir, "osm_baseline.graphml")
            ox.save_graphml(G_osm_raw, osm_save)
            summary["outputs"]["osm_graphml"] = osm_save
            print(f"  OSM graph saved → {osm_save}")
        except Exception as e:
            print(f"  OSM download failed ({e}), topological_accuracy will be skipped")
            G_osm = None
    else:
        print("  no OSM reference — topological_accuracy skipped "
              "(pass --top_left_lat/lon to enable OSM download)")
        G_osm = None

    tb_path = os.path.join(output_dir, "track_b_metrics.json")
    # G_skeleton (pre-heal) vs G_healed: gives the true connectivity_ratio
    tb_metrics = evaluate_track_b(G_skeleton, G_healed, G_osm, output_json=tb_path)
    summary["outputs"]["track_b_metrics"] = tb_path
    summary["metrics"].update(tb_metrics)

    # ── Step 5: Track A metrics (optional) ───────────────────────────────────
    if test_pairs and os.path.exists(test_pairs):
        print("\n[pipeline] Step 5 — Track A evaluation")
        from eval.metrics import evaluate_track_a
        import json as _json

        with open(test_pairs) as f:
            pairs = _json.load(f)
        image_paths = [p[0] for p in pairs]
        mask_paths  = [p[1] for p in pairs]

        # generate predictions into output_dir/track_a_preds/
        pred_dir = os.path.join(output_dir, "track_a_preds")
        os.makedirs(pred_dir, exist_ok=True)
        print(f"  generating predictions for {len(image_paths)} test images …")
        for ip in image_paths:
            stem = os.path.splitext(os.path.basename(ip))[0]
            out  = os.path.join(pred_dir, f"{stem}_road_mask.png")
            if not os.path.exists(out):
                m = predict_mask(model, ip, device, img_size=img_size,
                                 threshold=threshold)
                m = postprocess_mask(m)
                cv2.imwrite(out, m)

        ta_csv = os.path.join(output_dir, "track_a_metrics.csv")
        ta_metrics = evaluate_track_a(image_paths, mask_paths, pred_dir,
                                      output_csv=ta_csv)
        summary["outputs"]["track_a_metrics"] = ta_csv
        summary["metrics"].update({f"track_a_{k}": v for k, v in ta_metrics.items()})
    else:
        print("\n[pipeline] Step 5 — Track A evaluation skipped (no --test_pairs)")

    # ── Finalise ──────────────────────────────────────────────────────────────
    summary["elapsed_s"] = round(time.time() - t0, 1)
    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n[pipeline] done in {summary['elapsed_s']}s — summary → {summary_path}")
    return summary


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="SatMesh end-to-end pipeline")
    p.add_argument("--image",          required=True, help="Input satellite image")
    p.add_argument("--checkpoint",     required=True, help="best_model.pth")
    p.add_argument("--output_dir",     default="outputs")
    p.add_argument("--pixel_m",        type=float, default=0.5)
    p.add_argument("--max_gap_m",      type=float, default=50.0)
    p.add_argument("--top_left_lat",   type=float, default=0.0)
    p.add_argument("--top_left_lon",   type=float, default=0.0)
    p.add_argument("--bhoonidhi_tif",  default=None,
                   help="Georeferenced GeoTIFF from bhoonidhi.nrsc.gov.in — "
                        "top-left lat/lon extracted automatically via rasterio "
                        "(overrides --top_left_lat/lon)")
    p.add_argument("--img_size",       type=int,   default=512)
    p.add_argument("--threshold",      type=float, default=0.5)
    p.add_argument("--max_removals",   type=int,   default=10)
    p.add_argument("--test_pairs",     default=None,
                   help="test_pairs.json for Track A evaluation")
    p.add_argument("--osm_graphml",    default=None,
                   help="Pre-downloaded OSM .graphml for Track B baseline")
    args = p.parse_args()

    top_left_lat, top_left_lon = args.top_left_lat, args.top_left_lon
    if args.bhoonidhi_tif:
        top_left_lat, top_left_lon = _lat_lon_from_tif(args.bhoonidhi_tif)
        print(f"[georef] extracted from TIF → lat={top_left_lat:.6f}, lon={top_left_lon:.6f}")

    run_pipeline(
        input_image=args.image,
        checkpoint=args.checkpoint,
        output_dir=args.output_dir,
        pixel_m=args.pixel_m,
        max_gap_m=args.max_gap_m,
        top_left_lat=top_left_lat,
        top_left_lon=top_left_lon,
        img_size=args.img_size,
        threshold=args.threshold,
        max_removals=args.max_removals,
        test_pairs=args.test_pairs,
        osm_graphml=args.osm_graphml,
    )


if __name__ == "__main__":
    main()
