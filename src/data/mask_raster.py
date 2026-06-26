import numpy as np
import cv2
from pathlib import Path


def fetch_osm_roads(bbox, network_type="drive"):
    import osmnx as ox
    ox.settings.timeout = 90
    south, west, north, east = bbox
    G = ox.graph_from_bbox((west, south, east, north), network_type=network_type)
    return ox.graph_to_gdfs(G, nodes=False)["geometry"]


def rasterize_to_mask(roads, bounds, shape, buffer_m=3.0):
    from rasterio.features import rasterize as rio_rasterize
    from rasterio.transform import from_bounds
    import geopandas as gpd
    from shapely.geometry import mapping

    south, west, north, east = bounds
    h, w = shape
    transform = from_bounds(west, south, east, north, w, h)

    buffered = roads.to_crs("EPSG:32643").buffer(buffer_m).to_crs("EPSG:4326")
    geoms = [mapping(g) for g in buffered if not g.is_empty]
    if not geoms:
        return np.zeros((h, w), dtype=np.uint8)

    mask = rio_rasterize(geoms, out_shape=(h, w), transform=transform,
                         fill=0, default_value=255, dtype=np.uint8)
    return mask


def build_dataset(city_id: str, bbox: list, shape: tuple, out_dir: str, sat_path: str = None):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    mask_path = out_dir / f"{city_id}_mask.png"
    if not mask_path.exists():
        roads = fetch_osm_roads(bbox)
        mask = rasterize_to_mask(roads, bbox, shape)
        cv2.imwrite(str(mask_path), mask)

    return {"mask": str(mask_path)}
