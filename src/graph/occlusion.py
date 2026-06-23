"""Occlusion priors for graph healing.

Cheap, deterministic detection of shadow regions in the satellite tile. Shadows
are a primary cause of broken road masks; flagging them lets `heal_gaps` treat a
gap that falls under a shadow as a likely occluded road and bridge it more
readily (an occlusion prior, not a hard rule).
"""
import cv2
import numpy as np


def detect_shadow_mask(image_bgr, dilate_px=5):
    """Binary mask (uint8 0/255) of probable building/tree shadow regions.

    Heuristic in HSV: shadows are low-luminance (Otsu on V) and retain moderate
    saturation (they darken rather than wash out). Dilated slightly so a gap whose
    midpoint sits just beside a shadow still counts as occluded.
    """
    if image_bgr is None or image_bgr.size == 0:
        return None
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    v = hsv[..., 2]
    s = hsv[..., 1]
    _, dark = cv2.threshold(v, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    shadow = ((dark > 0) & (s > 35)).astype(np.uint8) * 255
    if dilate_px > 0:
        shadow = cv2.dilate(shadow, np.ones((dilate_px, dilate_px), np.uint8))
    return shadow
