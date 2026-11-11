"""
LifeBand Automated Test Suite
=============================
Validates all core computational, cryptographic, clinical, and data services:
1. Haversine distance & ETA calculation
2. SQLite schema creation & hospital lookup
3. SHA-256 blockchain hashing & chain verification
4. Tamper detection demonstration
5. AI First-Aid condition-aware warning logic
6. Emergency SOS orchestration and lifecycle
"""

import unittest
import os
import tempfile
import json
from pathlib import Path

# Configure test environment
os.environ["SECRET_KEY"] = "test-secret-key-lifeband"

from config import Config
from database.db import get_db_connection, init_db
from services.gps_service import haversine_distance, calculate_ambulance_eta, validate_coordinates
from services.hospital_service import get_all_hospitals, find_nearest_hospitals
from services.blockchain_service import (
    calculate_hash, record_profile_version, get_record_chain, verify_chain,
    simulate_tampering, restore_tampered_records, GENESIS_PREVIOUS_HASH
)
from services.medical_service import save_patient_profile, load_demo_patient_profile, get_active_patient
from services.ai_assistant import generate_emergency_guidance, analyze_allergies, analyze_chronic_conditions
from services.emergency_service import trigger_emergency, get_active_emergency, resolve_emergency, cancel_emergency

class TestLifeBandServices(unittest.TestCase):
    """Comprehensive test case for LifeBand system services."""
    
    @classmethod
    def setUpClass(cls):
        """Set up temporary database for testing."""
        cls.test_db_dir = tempfile.TemporaryDirectory()
        cls.test_db_path = os.path.join(cls.test_db_dir.name, "test_lifeband.db")
        Config.DATABASE_PATH = cls.test_db_path
        init_db()

    @classmethod
    def tearDownClass(cls):
        """Cleanup temporary files."""
        cls.test_db_dir.cleanup()

    def test_01_haversine_distance_calculation(self):
        """Verifies mathematical accuracy of Haversine formula calculation."""
        # Known distance between Bengaluru Central (12.9716, 77.5946) and Kempegowda Airport (13.1986, 77.7066) ~27-28 km
        dist = haversine_distance(12.9716, 77.5946, 13.1986, 77.7066)
        self.assertGreater(dist, 25.0)
        self.assertLess(dist, 32.0)
        
        # Zero distance check
        self.assertEqual(haversine_distance(12.9716, 77.5946, 12.9716, 77.5946), 0.0)
        
        # ETA calculation check
        eta = calculate_ambulance_eta(distance_km=7.0, speed_kmph=35.0)
        # (7 / 35) * 60 + 2 = 12 + 2 = 14 mins
        self.assertEqual(eta, 14)

    def test_02_coordinate_validation(self):
        """Verifies terrestrial GPS coordinate boundaries."""
        self.assertTrue(validate_coordinates(12.9716, 77.5946))
        self.assertTrue(validate_coordinates(-45.0, 120.0))
        self.assertFalse(validate_coordinates(95.0, 77.0))  # Lat > 90
        self.assertFalse(validate_coordinates(12.0, 200.0))  # Lon > 180

    def test_03_hospital_seeding_and_ranking(self):
        """Tests that demo hospitals are populated and ranked by distance."""
        hospitals = get_all_hospitals()
        self.assertGreaterEqual(len(hospitals), 4)
        
        # Find nearest from Central Demo location
        ranked = find_nearest_hospitals(Config.DEFAULT_LATITUDE, Config.DEFAULT_LONGITUDE, limit=3)
        self.assertEqual(len(ranked), 3)
        self.assertTrue(ranked[0]["is_nearest"])
        self.assertLessEqual(ranked[0]["distance_km"], ranked[1]["distance_km"])

    def test_04_medical_profile_and_blockchain_genesis(self):
        """Tests patient creation and Genesis Block generation in blockchain hash chain."""
        patient, block = load_demo_patient_profile()
        self.assertIsNotNone(patient)
        self.assertEqual(patient["blood_group"], "B+")
        self.assertEqual(block["version"], 1)
        self.assertEqual(block["previous_hash"], GENESIS_PREVIOUS_HASH)
        self.assertEqual(len(block["current_hash"]), 64)

    def test_05_blockchain_immutability_and_chaining(self):
        """Tests updating patient profile appends Version 2 block correctly chained to Version 1."""
        patient = get_active_patient()
        update_data = {
            "full_name": patient["full_name"],
            "age": 22,
            "blood_group": "B+",
            "allergies": "Penicillin, Aspirin, Sulfa",
            "chronic_diseases": patient["chronic_diseases"],
            "previous_surgeries": patient["previous_surgeries"],
            "current_medications": patient["current_medications"],
            "emergency_contact_name": patient["emergency_contact_name"],
            "emergency_contact_phone": patient["emergency_contact_phone"]
        }
        updated_patient, block_v2 = save_patient_profile(update_data, patient_id=patient["id"])
        self.assertEqual(block_v2["version"], 2)
        
        # Chain verification
        audit = verify_chain(patient["id"])
        self.assertTrue(audit["is_valid"])
        self.assertIsNone(audit["tampered_at_version"])
        self.assertEqual(audit["total_blocks"], 2)

    def test_06_blockchain_tamper_detection(self):
        """Tests that unauthorized SQLite modification causes immediate cryptographic verification failure."""
        patient = get_active_patient()
        
        # 1. Execute simulated tamper
        tamper_res = simulate_tampering(patient["id"])
        self.assertTrue(tamper_res["success"])
        
        # 2. Run verification -> Must fail!
        audit_failed = verify_chain(patient["id"])
        self.assertFalse(audit_failed["is_valid"])
        self.assertEqual(audit_failed["status"], "TAMPERED")
        self.assertIsNotNone(audit_failed["tampered_at_version"])
        
        # 3. Restore chain
        restore_res = restore_tampered_records(patient["id"], {
            "full_name": patient["full_name"],
            "age": 22,
            "blood_group": "B+",
            "allergies": "Penicillin, Aspirin, Sulfa",
            "chronic_diseases": patient["chronic_diseases"],
            "previous_surgeries": patient["previous_surgeries"],
            "current_medications": patient["current_medications"],
            "emergency_contact_name": patient["emergency_contact_name"],
            "emergency_contact_phone": patient["emergency_contact_phone"]
        })
        self.assertTrue(restore_res["success"])
        
        # 4. Re-verify -> Must pass!
        audit_restored = verify_chain(patient["id"])
        self.assertTrue(audit_restored["is_valid"])

    def test_07_ai_first_aid_condition_aware_warnings(self):
        """Tests that the AI Assistant detects patient allergies and cautions responders against contraindicated drugs."""
        sample_patient = {
            "full_name": "Rahul Sharma",
            "blood_group": "B+",
            "allergies": "Penicillin, Aspirin",
            "chronic_diseases": "Mild Asthma",
            "current_medications": "Albuterol Inhaler"
        }
        
        # Chest Pain scenario
        guidance = generate_emergency_guidance("CARDIAC_CHEST_PAIN", sample_patient)
        self.assertEqual(guidance["scenario"], "CARDIAC_CHEST_PAIN")
        
        # Allergy warning must explicitly mention Aspirin contraindication
        allergy_alerts = " ".join(guidance["allergy_warnings"])
        self.assertIn("ASPIRIN", allergy_alerts.upper())
        
        # Condition warning must mention asthma posture
        condition_alerts = " ".join(guidance["condition_warnings"])
        self.assertIn("ASTHMA", condition_alerts.upper())

    def test_08_emergency_trigger_and_resolution_cycle(self):
        """Tests the end-to-end emergency SOS dispatch and resolution workflow."""
        patient = get_active_patient()
        
        # 1. Trigger SOS
        event = trigger_emergency(
            patient_id=patient["id"],
            trigger_type="FALL_DETECTION",
            latitude=Config.DEFAULT_LATITUDE,
            longitude=Config.DEFAULT_LONGITUDE
        )
        self.assertEqual(event["status"], "ACTIVE")
        self.assertEqual(event["trigger_type"], "FALL_DETECTION")
        self.assertIsNotNone(event["emergency_id"])
        self.assertIsNotNone(event["assigned_hospital"])
        
        # 2. Query active emergency
        active = get_active_emergency()
        self.assertIsNotNone(active)
        self.assertEqual(active["id"], event["emergency_id"])
        
        # 3. Resolve emergency
        resolved = resolve_emergency(active["id"], notes="Faculty demonstration complete.")
        self.assertTrue(resolved)
        
        # 4. Active emergency should now be None
        active_after = get_active_emergency()
        self.assertIsNone(active_after)

if __name__ == "__main__":
    unittest.main()
