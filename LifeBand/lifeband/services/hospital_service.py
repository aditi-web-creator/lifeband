"""
Hospital Finder & Emergency Dispatch Simulation Service
=======================================================
Identifies nearest trauma and emergency healthcare facilities based on
real-time or simulated GPS coordinates, estimates emergency vehicle arrival times,
and generates simulated clinical dispatch notifications.
"""

import random
from typing import List, Dict, Optional
from database.db import get_db_connection, dict_from_row
from services.gps_service import haversine_distance, calculate_ambulance_eta
from config import Config

def get_all_hospitals() -> List[Dict]:
    """Retrieves all registered demo medical facilities."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, address, latitude, longitude, contact_phone, 
                   emergency_availability, icu_beds_available, trauma_level, specialties
            FROM hospitals
            ORDER BY id ASC
        """)
        return [dict_from_row(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_hospital_by_id(hospital_id: int) -> Optional[Dict]:
    """Fetches full facility profile by hospital ID."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hospitals WHERE id = ?", (hospital_id,))
        row = cursor.fetchone()
        return dict_from_row(row) if row else None
    finally:
        conn.close()

def find_nearest_hospitals(user_lat: float, user_lon: float, limit: int = 5) -> List[Dict]:
    """
    Ranks facilities by geometric distance from user's current GPS position using the Haversine formula.
    Computes expected ambulance transit ETA for each facility.
    """
    hospitals = get_all_hospitals()
    ranked = []
    
    for hosp in hospitals:
        dist_km = haversine_distance(user_lat, user_lon, hosp['latitude'], hosp['longitude'])
        eta_mins = calculate_ambulance_eta(dist_km)
        
        hosp_info = dict(hosp)
        hosp_info['distance_km'] = dist_km
        hosp_info['estimated_eta_mins'] = eta_mins
        ranked.append(hosp_info)
        
    ranked.sort(key=lambda h: h['distance_km'])
    
    # Mark the nearest facility
    if ranked:
        ranked[0]['is_nearest'] = True
        for h in ranked[1:]:
            h['is_nearest'] = False
            
    return ranked[:limit]

def create_simulated_dispatch_payload(hospital: Dict, patient_profile: Dict, emergency_id: int, trigger_type: str) -> Dict:
    """
    Constructs a simulated clinical pre-arrival notification payload for hospital ER display.
    Clearly designated as a demo telemetry packet.
    """
    dispatch_ref = f"LB-DISP-{random.randint(10000, 99999)}"
    
    return {
        "dispatch_id": dispatch_ref,
        "emergency_id": emergency_id,
        "is_simulation": True,
        "hospital_id": hospital['id'],
        "hospital_name": hospital['name'],
        "trauma_level": hospital.get('trauma_level', 'Level 1 Trauma Center'),
        "triage_code": "CODE_RED_CRITICAL",
        "trigger_source": trigger_type,
        "patient": {
            "name": patient_profile.get("full_name", "Unknown Patient"),
            "age": patient_profile.get("age", "N/A"),
            "blood_group": patient_profile.get("blood_group", "Unknown"),
            "critical_allergies": patient_profile.get("allergies") or "None Reported",
            "chronic_conditions": patient_profile.get("chronic_diseases") or "None Reported",
            "emergency_contact": f"{patient_profile.get('emergency_contact_name')} ({patient_profile.get('emergency_contact_phone')})"
        },
        "eta_minutes": hospital.get('estimated_eta_mins', 5),
        "assigned_bay": f"Trauma Bay {random.randint(1, 4)}",
        "status": "DISPATCH_ACCEPTED_EN_ROUTE",
        "telemetry_message": f"Pre-arrival alert acknowledged by {hospital['name']}. ER triage team prepared."
    }
