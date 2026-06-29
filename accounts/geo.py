import math
from typing import Optional


def haversine_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """Great-circle distance between two WGS84 points, in kilometers."""
    earth_radius_km = 6371.0
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(
        math.radians,
        (lat1, lon1, lat2, lon2),
    )
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    return earth_radius_km * (2 * math.asin(math.sqrt(min(1.0, a))))


def parse_coordinate(value: Optional[str], name: str) -> float:
    try:
        coord = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f'Invalid {name}.') from exc
    if name == 'lat' and not (-90 <= coord <= 90):
        raise ValueError('lat must be between -90 and 90.')
    if name == 'lon' and not (-180 <= coord <= 180):
        raise ValueError('lon must be between -180 and 180.')
    return coord
