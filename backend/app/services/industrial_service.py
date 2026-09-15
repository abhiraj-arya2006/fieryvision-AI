from typing import List, Dict, Any, Optional, Tuple
from app.core.geo import haversine_distance_m
from app.core.config import settings

# Pre-populated Giaspura Industrial Facilities (Ludhiana, Punjab)
GIASPURA_FACILITIES: List[Dict[str, Any]] = [
    {
        "id": "IND-GIAS-01",
        "name": "Giaspura Industrial Focal Point Cluster A",
        "site_type": "Auto Components & Forging",
        "latitude": 30.876210,
        "longitude": 75.899120,
        "address": "Focal Point Phase VI, Giaspura, Ludhiana",
        "operating_status": "active"
    },
    {
        "id": "IND-GIAS-02",
        "name": "Ludhiana Textile Dyeing & Processing Plant",
        "site_type": "Textile Dyeing & Boiler Unit",
        "latitude": 30.874100,
        "longitude": 75.897250,
        "address": "Giaspura Road near Sua Road, Ludhiana",
        "operating_status": "active"
    },
    {
        "id": "IND-GIAS-03",
        "name": "Punjab Cycle Heavy Stamping & Electroplating",
        "site_type": "Electroplating & Metal Finishing",
        "latitude": 30.878500,
        "longitude": 75.901500,
        "address": "Opposite Dhandari Kalan Railway Colony, Giaspura",
        "operating_status": "active"
    },
    {
        "id": "IND-GIAS-04",
        "name": "Giaspura Boiler & Casting Works",
        "site_type": "Industrial Boiler Plant",
        "latitude": 30.872800,
        "longitude": 75.895100,
        "address": "Giaspura Canal Road, Ludhiana",
        "operating_status": "active"
    },
    {
        "id": "IND-GIAS-05",
        "name": "Dhandari Kalan Freight & Warehousing Hub",
        "site_type": "Logistics & Material Storage",
        "latitude": 30.881000,
        "longitude": 75.905000,
        "address": "Dhandari Kalan Industrial Zone, Ludhiana",
        "operating_status": "active"
    },
    {
        "id": "IND-GIAS-06",
        "name": "Giaspura Metal Heat Treatment Facility",
        "site_type": "Furnace & Heat Treatment",
        "latitude": 30.876900,
        "longitude": 75.896800,
        "address": "Street No. 4, Giaspura Industrial Belt",
        "operating_status": "active"
    }
]

def get_all_facilities() -> List[Dict[str, Any]]:
    """Return cached industrial facilities in the Giaspura study area."""
    return GIASPURA_FACILITIES

def find_nearest_facility(lat: float, lon: float) -> Tuple[Optional[Dict[str, Any]], float]:
    """
    Find the nearest industrial facility to given coordinates.
    Returns (facility_dict, distance_in_meters).
    """
    if not GIASPURA_FACILITIES:
        return None, float("inf")

    nearest_facility = None
    min_distance = float("inf")

    for fac in GIASPURA_FACILITIES:
        dist = haversine_distance_m(lat, lon, fac["latitude"], fac["longitude"])
        if dist < min_distance:
            min_distance = dist
            nearest_facility = fac

    return nearest_facility, min_distance

def is_inside_industrial_zone(lat: float, lon: float, threshold_m: float = 800.0) -> bool:
    """
    Check if coordinates fall within 800 meters of a known Giaspura industrial facility.
    """
    _, dist = find_nearest_facility(lat, lon)
    return dist <= threshold_m

def get_landcover_context(lat: float, lon: float) -> str:
    """
    Determine landcover classification based on distance to Giaspura industrial hub vs surrounding belt.
    """
    fac, dist = find_nearest_facility(lat, lon)
    if dist <= 1200.0:
        return "Industrial & Built-up Land (Giaspura Industrial Area)"
    elif dist <= 3000.0:
        return "Mixed Urban / Light Industrial Zone"
    else:
        return "Agricultural / Semi-Urban Buffer Zone"
