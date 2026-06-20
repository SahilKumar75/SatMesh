import os
import numpy as np
import requests
from pathlib import Path


STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1/search"


def _search_stac(bbox, max_cloud=20):
    payload = {
        "collections": ["sentinel-2-l2a"],
        "bbox": bbox,
        "query": {"eo:cloud_cover": {"lt": max_cloud}},
        "sortby": [{"field": "properties.eo:cloud_cover", "direction": "asc"}],
        "limit": 5,
    }
    r = requests.post(STAC_URL, json=payload, timeout=30)
    r.raise_for_status()
    return r.json().get("features", [])


def _sign_asset(href):
    r = requests.get(
        f"https://planetarycomputer.microsoft.com/api/sas/v1/sign?href={href}",
        timeout=15,
    )
    if r.ok:
        return r.json().get("href", href)
    return href


def download_city(city_id: str, bbox: list, out_dir: str) -> dict:
    import rasterio
    from rasterio.windows import from_bounds
    from rasterio.transform import from_bounds as tfrom_bounds

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    meta_path = out_dir / "sentinel_meta.json"
    if meta_path.exists():
        import json
        with open(meta_path) as f:
            return json.load(f)

    south, west, north, east = bbox[0], bbox[1], bbox[2], bbox[3]
    stac_bbox = [west, south, east, north]

    features = _search_stac(stac_bbox)
    if not features:
        raise RuntimeError(f"No Sentinel-2 tiles found for {city_id} bbox={bbox}")

    item = features[0]
    assets = item["assets"]
    band_keys = {"B04": "red", "B03": "green", "B02": "blue", "B08": "nir"}
    paths = {}

    for band, label in band_keys.items():
        href = _sign_asset(assets[band]["href"])
        out_path = out_dir / f"{label}.tif"
        if not out_path.exists():
            with rasterio.open(href) as src:
                window = from_bounds(west, south, east, north, src.transform)
                data = src.read(1, window=window)
                transform = src.window_transform(window)
                profile = src.profile.copy()
                profile.update({"width": data.shape[1], "height": data.shape[0],
                                "transform": transform, "count": 1})
                with rasterio.open(out_path, "w", **profile) as dst:
                    dst.write(data, 1)
        paths[label] = str(out_path)

    with rasterio.open(paths["red"]) as src:
        t = src.transform
        meta = {
            "top_left_lat": float(t.f),
            "top_left_lon": float(t.c),
            "pixel_size_deg": float(abs(t.e)),
            "width": src.width,
            "height": src.height,
            "paths": paths,
        }

    import json
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    return meta
