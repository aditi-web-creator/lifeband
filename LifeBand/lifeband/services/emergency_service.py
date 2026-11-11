"""
Emergency SOS & Event Management Service
========================================
Coordinates emergency trigger workflows, GPS resolution, nearest hospital selection,
AI first-aid generation, simulated ambulance dispatching, and emergency status lifecycle.
"""

import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
from database.db import get_db_connection, dict_from_row
from services.hospital_service import find_nearest_hospitals, get_hospital_by_id, create_simulated_dispatch_payload
from services.gps_service import validate_coordinates, haversine_distance, calculate_ambulance_eta
from services.ai_assistant import generate_emergency_guidance
from services.medical_service import get_active_patient, get_patient_by_id
from config import Config

def trigger_emergency(
    patient_id: Optional[int] = None,
    trigger_type: str = "MANUAL_SOS",
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    location_name: Optional[str] = None,
    hospital_id: Optional[int] = None,
    notes: Optional[str] = None
) -> Dict:
    """
    Core emergency orchestration workflow:
    1. Validates or resolves GPS coordinates (falls back to calibrated demo coordinates).
    2. Identifies nearest or assigned emergency facility via Haversine calculation.
    3. Generates condition-aware AI first-aid directives matching patient's profile.
    4. Logs active emergency record in SQLite database.
    5. Dispatches simulated telemetry payload to hospital.
    """
    # 1. Resolve Patient
    patient = None
    if patient_id:
        patient = get_patient_by_id(patient_id)
    if not patient:
        patient = get_active_patient()
        
    if not patient:
        # Auto-create demo profile if none exists so emergency demo never breaks!
        from services.medical_service import load_demo_patient_profile
        patient, _ = load_demo_patient_profile()
        
    resolved_patient_id = patient["id"]
    
    # 2. Resolve Coordinates
    if latitude is None or longitude is None or not validate_coordinates(latitude, longitude):
        lat = Config.DEFAULT_LATITUDE
        lon = Config.DEFAULT_LONGITUDE
        loc_desc = location_name or Config.DEFAULT_LOCATION_NAME
    else:
        lat = float(latitude)
        lon = float(longitude)
        loc_desc = location_name or f"GPS: {lat:.5f}, {lon:.5f} (Device Sensor)"
        
    # 3. Resolve Hospital & ETA
    if hospital_id:
        target_hospital = get_hospital_by_id(hospital_id)
        if target_hospital:
            dist = haversine_distance(lat, lon, target_hospital["latitude"], target_hospital["longitude"])
            eta = calculate_ambulance_eta(dist)
            target_hospital["distance_km"] = dist
            target_hospital["estimated_eta_mins"] = eta
        else:
            nearest_list = find_nearest_hospitals(lat, lon, limit=1)
            target_hospital = nearest_list[0] if nearest_list else None
    else:
        nearest_list = find_nearest_hospitals(lat, lon, limit=1)
        target_hospital = nearest_list[0] if nearest_list else None
        
    hosp_id = target_hospital["id"] if target_hospital else None
    hosp_name = target_hospital["name"] if target_hospital else "Central EMS Response (Demo)"
    dist_km = target_hospital.get("distance_km", 2.5) if target_hospital else 2.5
    eta_mins = target_hospital.get("estimated_eta_mins", 6) if target_hospital else 6
    
    # 4. Generate AI First-Aid Guidance
    ai_guidance = generate_emergency_guidance(trigger_type, patient)
    ai_json = json.dumps(ai_guidance)
    
    # 5. Insert Record into SQLite
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Deactivate any lingering active emergencies first for clean single-incident demo
        cursor.execute("""
            UPDATE emergency_events 
            SET status = 'RESOLVED', resolved_at = CURRENT_TIMESTAMP 
            WHERE status = 'ACTIVE' AND patient_id = ?
        """, (resolved_patient_id,))
        
        cursor.execute("""
            INSERT INTO emergency_events (
                patient_id, trigger_type, status, latitude, longitude,
                location_name, assigned_hospital_id, hospital_name,
                distance_km, estimated_eta_mins, ai_guidance_json, notes
            ) VALUES (?, ?, 'ACTIVE', ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            resolved_patient_id, trigger_type, lat, lon, loc_desc,
            hosp_id, hosp_name, dist_km, eta_mins, ai_json, notes or ""
        ))
        conn.commit()
        emergency_id = cursor.lastrowid
    finally:
        conn.close()
        
    # 6. Build Simulated Dispatch Packet
    simulated_dispatch = create_simulated_dispatch_payload(
        target_hospital or {"id": 1, "name": hosp_name, "trauma_level": "Level 1 Trauma Center"},
        patient,
        emergency_id,
        trigger_type
    )
    
    return {
        "emergency_id": emergency_id,
        "patient": patient,
        "trigger_type": trigger_type,
        "status": "ACTIVE",
        "latitude": lat,
        "longitude": lon,
        "location_name": loc_desc,
        "assigned_hospital": target_hospital,
        "distance_km": dist_km,
        "estimated_eta_mins": eta_mins,
        "ai_guidance": ai_guidance,
        "simulated_dispatch": simulated_dispatch,
        "dispatched_at": datetime.now(timezone.utc).isoformat()
    }

def get_active_emergency() -> Optional[Dict]:
    """Retrieves current active emergency event if one is in progress."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.*, p.full_name, p.blood_group, p.allergies, p.chronic_diseases,
                   p.emergency_contact_name, p.emergency_contact_phone
            FROM emergency_events e
            JOIN patients p ON e.patient_id = p.id
            WHERE e.status = 'ACTIVE'
            ORDER BY e.id DESC
            LIMIT 1
        """)
        row = cursor.fetchone()
        if not row:
            return None
            
        event = dict_from_row(row)
        try:
            event["ai_guidance"] = json.loads(event["ai_guidance_json"]) if event.get("ai_guidance_json") else {}
        except Exception:
            event["ai_guidance"] = {}
            
        return event
    finally:
        conn.close()

def resolve_emergency(emergency_id: int, notes: str = "Resolved by clinical/demo operator") -> bool:
    """Marks an active emergency as resolved."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE emergency_events
            SET status = 'RESOLVED',
                resolved_at = CURRENT_TIMESTAMP,
                notes = ?
            WHERE id = ?
        """, (notes, emergency_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def cancel_emergency(emergency_id: int, reason: str = "False alarm cancelled by user") -> bool:
    """Cancels an accidental trigger."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE emergency_events
            SET status = 'CANCELLED',
                resolved_at = CURRENT_TIMESTAMP,
                notes = ?
            WHERE id = ?
        """, (reason, emergency_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()

def get_emergency_history(limit: int = 15) -> List[Dict]:
    """Fetches past emergency events for timeline review."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT e.*, p.full_name
            FROM emergency_events e
            JOIN patients p ON e.patient_id = p.id
            ORDER BY e.id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        
        history = []
        for row in rows:
            event = dict_from_row(row)
            try:
                event["ai_guidance"] = json.loads(event["ai_guidance_json"]) if event.get("ai_guidance_json") else {}
            except Exception:
                event["ai_guidance"] = {}
            history.append(event)
        return history
    finally:
        conn.close()
