"""Cartosat-3 / LISS-IV / any GeoTIFF → uint8 RGB for inference pipeline."""
import rasterio
import numpy as np
import cv2

# Band order inferred from ISRO product documentation — not verified against real data.
# On hackathon day, confirm first:
#   python -c "import rasterio; s=rasterio.open('tile.tif'); print(s.count, s.descriptions)"
# Cartosat-3 MS: Blue=1, Green=2, Red=3, NIR=4  (ISRO Cartosat-3 Data Users Handbook)
# LISS-IV MX:   Green=1, Red=2, NIR=3
# Cartosat-3 PAN: 1 panchromatic band (no color variance — grayscale RGB output)

_SENSOR_RGB_BANDS = {
    "cartosat3_ms": (3, 2, 1),  # (R_idx, G_idx, B_idx) — 1-based
    "lissiv":       (2, 1, 1),  # no blue; duplicate green
}
_SENSOR_NIR_BAND = {
    "cartosat3_ms": 4,
    "lissiv": 3,
}


def _percentile_stretch(arr, lo=2, hi=98):
    p_lo, p_hi = np.percentile(arr, [lo, hi])
    return np.clip((arr - p_lo) / (p_hi - p_lo + 1e-6) * 255, 0, 255).astype(np.uint8)


def load_geotiff_as_rgb(path: str, sensor: str = "auto", out_size: int = 512):
    """Load any GeoTIFF → (uint8 RGB H×W×3, affine transform, crs).

    transform and crs must be propagated to zones.geojson for correct map coordinates.
    """
    with rasterio.open(path) as src:
        data = src.read().astype(np.float32)
        transform = src.transform
        crs = src.crs
        n_bands = src.count

    if sensor == "auto":
        sensor = {1: "cartosat3_pan", 3: "lissiv"}.get(n_bands, "cartosat3_ms")

    if sensor == "cartosat3_pan":
        ch = data[0]
        bands = [ch, ch, ch]
    elif sensor in _SENSOR_RGB_BANDS:
        ri, gi, bi = _SENSOR_RGB_BANDS[sensor]
        bands = [data[ri - 1], data[gi - 1], data[bi - 1]]
    else:
        bands = [data[i] for i in range(min(3, n_bands))]

    rgb = np.stack(bands, axis=-1)
    rgb = np.stack([_percentile_stretch(rgb[..., c]) for c in range(3)], axis=-1)
    return cv2.resize(rgb, (out_size, out_size)), transform, crs


def load_geotiff_nir(path: str, sensor: str = "auto", out_size: int = 512):
    """Return NIR band as float32 [0,1], or None if the sensor has no NIR band."""
    with rasterio.open(path) as src:
        n_bands = src.count
        if sensor == "auto":
            sensor = {1: "cartosat3_pan", 3: "lissiv"}.get(n_bands, "cartosat3_ms")
        nir_idx = _SENSOR_NIR_BAND.get(sensor)
        if nir_idx is None or nir_idx > n_bands:
            return None
        nir = src.read(nir_idx).astype(np.float32)
    lo, hi = np.percentile(nir, [2, 98])
    nir = np.clip((nir - lo) / (hi - lo + 1e-6), 0.0, 1.0)
    return cv2.resize(nir, (out_size, out_size))
