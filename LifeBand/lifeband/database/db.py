"""
Database Connection and Initialization Manager
=============================================
Provides thread-safe SQLite connection handling, schema creation,
and sample hospital seeding for LifeBand demonstrations.
"""

import sqlite3
import os
from pathlib import Path
from config import Config

def get_db_connection():
    """Returns a SQLite connection with Row factory enabled for dictionary-like access."""
    # Ensure database folder exists
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Initializes the database using schema.sql and seeds initial demo hospitals."""
    conn = get_db_connection()
    try:
        with open(Config.SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema_script = f.read()
        conn.executescript(schema_script)
        conn.commit()
        
        # Check if hospitals are seeded; if not, seed realistic fictional sample hospitals
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM hospitals")
        count = cursor.fetchone()[0]
        if count == 0:
            seed_demo_hospitals(conn)
    finally:
        conn.close()

def seed_demo_hospitals(conn):
    """Populates the database with sample emergency care hospitals around standard coordinates."""
    sample_hospitals = [
        (
            "St. Jude Emergency & Trauma Institute (Demo)",
            "14 Healthcare Avenue, Tech Corridor, Central Zone",
            12.9725,
            77.5890,
            "+91 80 2299 1001 (Demo)",
            "Active 24/7 - Level 1 Trauma Ready",
            12,
            "Level 1 Trauma Center",
            "Emergency Cardiology, Neuro-trauma, Resuscitation Unit, Burn Care"
        ),
        (
            "Metro Apex Super Specialty Hospital (Demo)",
            "88 Ring Road, South Metro Sector",
            12.9635,
            77.5750,
            "+91 80 2650 2002 (Demo)",
            "Active 24/7 - Stroke & Cardiac Care",
            8,
            "Level 2 Emergency Facility",
            "Acute Stroke Intervention, Pediatric Emergency, Intensive Care"
        ),
        (
            "City LifeCare Emergency Hospital (Demo)",
            "102 Outer Ring Road, East Tech Park",
            12.9602,
            77.6430,
            "+91 80 4115 3003 (Demo)",
            "Active 24/7 - Advanced Resuscitation",
            15,
            "Level 1 Trauma Center",
            "Emergency Orthopedics, Cardiac Catheterization, Toxicology"
        ),
        (
            "Green Valley Medical Center (Demo)",
            "45 Bannerghatta Expressway, South Gate",
            12.8938,
            77.5975,
            "+91 80 2630 4004 (Demo)",
            "Active 24/7 - General Emergency",
            6,
            "Level 3 Emergency Care",
            "General Trauma, Asthma & Respiratory Care, Critical Care ICU"
        ),
        (
            "Fortis Healthcare Urgent Response (Demo)",
            "154 Opposite IIMB, Bannerghatta Corridor",
            12.8920,
            77.6010,
            "+91 80 6621 5005 (Demo)",
            "Active 24/7 - Super Specialty Emergency",
            10,
            "Level 1 Trauma Center",
            "Adult & Pediatric Emergency, Vascular Surgery, Polytrauma Unit"
        ),
        (
            "Columbia North Emergency Hospital (Demo)",
            "26/4 Brigade Gateway, North Sector",
            13.0125,
            77.5540,
            "+91 80 3989 6006 (Demo)",
            "Active 24/7 - Rapid Ambulance Dispatch",
            9,
            "Level 2 Emergency Facility",
            "Trauma Care, Dialysis, Emergency Toxicology, Poison Control"
        )
    ]
    
    conn.executemany("""
        INSERT INTO hospitals (
            name, address, latitude, longitude, contact_phone, 
            emergency_availability, icu_beds_available, trauma_level, specialties
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_hospitals)
    conn.commit()

def dict_from_row(row):
    """Helper to convert sqlite3.Row to a standard python dictionary."""
    if row is None:
        return None
    return {key: row[key] for key in row.keys()}
