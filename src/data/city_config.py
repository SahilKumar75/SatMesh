import json
from dataclasses import dataclass
from pathlib import Path
from typing import List

_CITIES_JSON = Path(__file__).parent.parent.parent / "cities.json"


@dataclass
class CityConfig:
    city_id: str
    name: str
    bbox: List[float]
    pixel_m: float
    dem_source: str
    center: List[float]
    zoom: int
    flood_threshold_m: float
    terrain: str = "urban"


def load_all() -> dict:
    with open(_CITIES_JSON) as f:
        raw = json.load(f)
    return {k: CityConfig(city_id=k, **v) for k, v in raw.items()}


def load_city(city_id: str) -> CityConfig:
    cities = load_all()
    if city_id not in cities:
        raise KeyError(f"City '{city_id}' not found in cities.json")
    return cities[city_id]
