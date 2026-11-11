"""
Medical Profile Management Service
==================================
Handles patient demographic and clinical information storage in SQLite with
automatic cryptographic chaining in the blockchain verification module.
"""

from typing import Dict, Optional, Tuple
from database.db import get_db_connection, dict_from_row
from services.blockchain_service import record_profile_version, get_record_chain

def get_active_patient() -> Optional[Dict]:
    """Retrieves the primary active patient profile."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients ORDER BY id ASC LIMIT 1")
        row = cursor.fetchone()
        return dict_from_row(row) if row else None
    finally:
        conn.close()

def get_patient_by_id(patient_id: int) -> Optional[Dict]:
    """Fetches patient profile by ID."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        row = cursor.fetchone()
        return dict_from_row(row) if row else None
    finally:
        conn.close()

def save_patient_profile(profile_data: Dict, patient_id: Optional[int] = None) -> Tuple[Dict, Dict]:
    """
    Saves or updates patient medical profile.
    Automatically creates a new cryptographic version in the blockchain hash chain.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        full_name = profile_data.get("full_name", "").strip()
        age = int(profile_data.get("age", 20))
        blood_group = profile_data.get("blood_group", "").strip().upper()
        allergies = profile_data.get("allergies", "").strip()
        chronic_diseases = profile_data.get("chronic_diseases", "").strip()
        previous_surgeries = profile_data.get("previous_surgeries", "").strip()
        current_medications = profile_data.get("current_medications", "").strip()
        emergency_contact_name = profile_data.get("emergency_contact_name", "").strip()
        emergency_contact_phone = profile_data.get("emergency_contact_phone", "").strip()
        
        if not full_name:
            raise ValueError("Full Name is required.")
        if not blood_group:
            raise ValueError("Blood Group is required.")
        if not emergency_contact_name or not emergency_contact_phone:
            raise ValueError("Emergency contact name and phone are required.")
            
        if patient_id:
            cursor.execute("""
                UPDATE patients SET
                    full_name = ?,
                    age = ?,
                    blood_group = ?,
                    allergies = ?,
                    chronic_diseases = ?,
                    previous_surgeries = ?,
                    current_medications = ?,
                    emergency_contact_name = ?,
                    emergency_contact_phone = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                full_name, age, blood_group, allergies, chronic_diseases,
                previous_surgeries, current_medications, emergency_contact_name,
                emergency_contact_phone, patient_id
            ))
            actual_patient_id = patient_id
        else:
            cursor.execute("""
                INSERT INTO patients (
                    full_name, age, blood_group, allergies, chronic_diseases,
                    previous_surgeries, current_medications, emergency_contact_name,
                    emergency_contact_phone
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                full_name, age, blood_group, allergies, chronic_diseases,
                previous_surgeries, current_medications, emergency_contact_name,
                emergency_contact_phone
            ))
            actual_patient_id = cursor.lastrowid
            
        conn.commit()
    finally:
        conn.close()
        
    updated_profile = get_patient_by_id(actual_patient_id)
    
    # Cryptographic immutability payload
    clean_payload = {
        "full_name": updated_profile["full_name"],
        "age": updated_profile["age"],
        "blood_group": updated_profile["blood_group"],
        "allergies": updated_profile["allergies"],
        "chronic_diseases": updated_profile["chronic_diseases"],
        "previous_surgeries": updated_profile["previous_surgeries"],
        "current_medications": updated_profile["current_medications"],
        "emergency_contact_name": updated_profile["emergency_contact_name"],
        "emergency_contact_phone": updated_profile["emergency_contact_phone"]
    }
    
    # Append to blockchain ledger
    block_info = record_profile_version(actual_patient_id, clean_payload)
    
    return updated_profile, block_info

def load_demo_patient_profile() -> Tuple[Dict, Dict]:
    """
    Loads an authentic, realistic demo patient profile suitable for faculty demonstration.
    Configures clinical flags for allergies (Penicillin, Aspirin) and chronic conditions (Asthma).
    """
    existing = get_active_patient()
    patient_id = existing["id"] if existing else None
    
    demo_data = {
        "full_name": "Rahul Sharma",
        "age": 21,
        "blood_group": "B+",
        "allergies": "Penicillin, Aspirin",
        "chronic_diseases": "Mild Bronchial Asthma",
        "previous_surgeries": "Appendectomy (2022)",
        "current_medications": "Albuterol Inhaler (PRN), Multivitamins",
        "emergency_contact_name": "Priya Sharma (Mother)",
        "emergency_contact_phone": "+91 98765 43210"
    }
    
    return save_patient_profile(demo_data, patient_id=patient_id)

def calculate_profile_completion(profile: Optional[Dict]) -> int:
    """Calculates profile completion percentage based on clinical fields filled."""
    if not profile:
        return 0
    fields = [
        profile.get("full_name"),
        profile.get("age"),
        profile.get("blood_group"),
        profile.get("allergies"),
        profile.get("chronic_diseases"),
        profile.get("previous_surgeries"),
        profile.get("current_medications"),
        profile.get("emergency_contact_name"),
        profile.get("emergency_contact_phone")
    ]
    filled = sum(1 for f in fields if f is not None and str(f).strip() != "")
    return int((filled / len(fields)) * 100)
