import logging
import warnings

import numpy as np

logger = logging.getLogger(__name__)

_OPENTOPO_URL = (
    "https://portal.opentopography.org/API/globaldem"
    "?demtype=SRTMGL1&south={south}&north={north}&west={west}&east={east}&outputFormat=GTiff"
)


def fetch_srtm_dem(bbox, out_path):
    """bbox: [south, west, north, east]. Downloads SRTM 30m GeoTIFF.
    Returns (array, geotransform) or (zeros_array, None) on failure."""
    import requests
    import rasterio

    south, west, north, east = bbox
    url = _OPENTOPO_URL.format(south=south, north=north, west=west, east=east)

    try:
        resp = requests.get(url, timeout=60, stream=True)
        resp.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
    except Exception as exc:
        logger.warning("OpenTopography unavailable (%s). Elevation set to zero.", exc)
        dummy = np.zeros((1, 1), dtype=np.float32)
        return dummy, None

    try:
        with rasterio.open(out_path) as ds:
            arr = ds.read(1).astype(np.float32)
            gt = ds.transform
            geotransform = (gt.c, gt.a, 0.0, gt.f, 0.0, gt.e)
        return arr, geotransform
    except Exception as exc:
        logger.warning("Failed to read DEM file (%s). Elevation set to zero.", exc)
        dummy = np.zeros((1, 1), dtype=np.float32)
        return dummy, None


def attach_elevation(G, dem_array, geotransform):
    if geotransform is None or dem_array is None:
        for n in G.nodes:
            G.nodes[n]["elevation_m"] = 0.0
        return G

    x_origin, x_res, _, y_origin, _, y_res = geotransform
    h, w = dem_array.shape

    for n, data in G.nodes(data=True):
        lat = data.get("lat", 0.0)
        lon = data.get("lon", 0.0)
        col = int((lon - x_origin) / x_res)
        row = int((lat - y_origin) / y_res)
        if 0 <= row < h and 0 <= col < w:
            data["elevation_m"] = float(dem_array[row, col])
        else:
            data["elevation_m"] = 0.0

    return G


def mark_flood_nodes(G, threshold_m):
    flagged = set()
    for n, data in G.nodes(data=True):
        elev = data.get("elevation_m", 0.0)
        if elev <= threshold_m:
            data["flood_vulnerable"] = True
            flagged.add(n)
        else:
            data.setdefault("flood_vulnerable", False)
    return flagged


def flood_scenario(G, threshold_m):
    flagged = set()
    for n, data in G.nodes(data=True):
        if data.get("elevation_m", 0.0) <= threshold_m:
            flagged.add(n)
    return G.copy().subgraph([n for n in G.nodes if n not in flagged]).copy()
