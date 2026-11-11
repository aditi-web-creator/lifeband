"""
GPS Location & Haversine Distance Calculation Service
=====================================================
Calculates accurate orthodromic (great-circle) distances between geographic coordinates
using the spherical Haversine formula.

Formula:
    a = sin²(Δφ/2) + cos(φ₁) * cos(φ₂) * sin²(Δλ/2)
    c = 2 * atan2(√a, √(1−a))
    d = R * c
Where:
    φ is latitude, λ is longitude (in radians),
    R is Earth's mean radius (6371.0 km).
"""

import math
from typing import Tuple, Optional
from config import Config

EARTH_RADIUS_KM = 6371.0

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes distance in kilometers between two GPS points using the Haversine formula.
    Accurate to within 0.5% for typical terrestrial distances.
    """
    # Convert degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    # Haversine core equation
    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    
    # Angular distance in radians
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
    
    distance_km = EARTH_RADIUS_KM * c
    return round(distance_km, 2)

def calculate_ambulance_eta(distance_km: float, speed_kmph: float = Config.AVERAGE_AMBULANCE_SPEED_KMPH) -> int:
    """
    Estimates emergency vehicle arrival time in minutes.
    Includes a realistic 2-minute baseline dispatch preparation factor.
    Minimum ETA is capped at 2 minutes.
    """
    if distance_km <= 0:
        return 2
    travel_time_hours = distance_km / max(10.0, speed_kmph)
    travel_time_minutes = travel_time_hours * 60.0
    total_eta = round(travel_time_minutes + 2.0)
    return max(2, total_eta)

def validate_coordinates(lat: float, lon: float) -> bool:
    """Validates whether coordinates lie within valid terrestrial ranges."""
    try:
        return (-90.0 <= float(lat) <= 90.0) and (-180.0 <= float(lon) <= 180.0)
    except (ValueError, TypeError):
        return False

def get_demo_locations() -> list:
    """Returns a curated list of sample/demo coordinates for live classroom demonstration."""
    return [
        {
            "id": "demo-central",
            "name": "City Tech Park / Central Hub (Default Demo)",
            "latitude": Config.DEFAULT_LATITUDE,
            "longitude": Config.DEFAULT_LONGITUDE,
            "description": "Standard college campus / central demo benchmark location."
        },
        {
            "id": "demo-north",
            "name": "North Metro Campus Zone",
            "latitude": 13.0280,
            "longitude": 77.5670,
            "description": "Closer to Columbia North Emergency Hospital (~1.8 km)."
        },
        {
            "id": "demo-south",
            "name": "South Cyber Gateway",
            "latitude": 12.8950,
            "longitude": 77.5990,
            "description": "Within immediate proximity of Fortis Emergency Care (~0.4 km)."
        },
        {
            "id": "demo-east",
            "name": "East Tech Corridor (Whitefield Zone)",
            "latitude": 12.9690,
            "longitude": 77.6520,
            "description": "Proximity to City LifeCare Hospital (~1.3 km)."
        }
    ]
