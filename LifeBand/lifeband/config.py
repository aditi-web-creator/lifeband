"""
LifeBand System Configuration
=============================
Authoritative configuration for LifeBand Emergency Medical Identification
and Hospital Alert System.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    """Application configuration parameters."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "lifeband-secure-emergency-secret-key-2026")
    
    # SQLite Database configuration
    DB_FOLDER = BASE_DIR / "database"
    DATABASE_PATH = str(DB_FOLDER / "lifeband.db")
    SCHEMA_PATH = str(DB_FOLDER / "schema.sql")
    
    # IoT / Fall Detection defaults
    DEFAULT_FALL_THRESHOLD = 25.0  # Total acceleration in m/s² (~2.55 g)
    FALL_COUNTDOWN_SECONDS = 10     # Grace period before auto-triggering SOS
    
    # Geolocation & Hospital Dispatch defaults
    # Fictional/Sample default coordinates (Bengaluru / City Tech Hub)
    DEFAULT_LATITUDE = 12.9715987
    DEFAULT_LONGITUDE = 77.5945627
    DEFAULT_LOCATION_NAME = "Bengaluru City Central / Tech Corridor (Demo Coordinates)"
    
    # Emergency Response Simulation parameters
    AVERAGE_AMBULANCE_SPEED_KMPH = 35.0  # Urban emergency vehicle response average speed
    
    # System metadata
    APP_NAME = "LifeBand"
    APP_TAGLINE = "Smart Emergency Medical Identification & Hospital Alert System"
    VERSION = "1.0.0"
    DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1")
