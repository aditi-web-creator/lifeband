"""
LifeBand Flask Route & API Test Suite
=====================================
Verifies all web pages render correctly (HTTP 200) and all JSON API endpoints
return valid responses without template errors or runtime exceptions.
"""

import unittest
from app import app
from database.db import init_db

class TestLifeBandRoutes(unittest.TestCase):
    """Verifies all Flask web routes and JSON endpoints."""
    
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        with app.app_context():
            init_db()
        cls.client = app.test_client()

    def test_pages_render_status_200(self):
        """Tests that all major UI pages load cleanly with HTTP 200."""
        routes = [
            "/",
            "/dashboard",
            "/profile",
            "/medical-card",
            "/emergency",
            "/fall-detection",
            "/hospitals",
            "/ai-assistant",
            "/blockchain",
            "/presentation"
        ]
        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 200, f"Route {route} failed to render.")
                self.assertIn(b"LifeBand", response.data)

    def test_api_load_demo_profile(self):
        """Tests API endpoint to load sample profile."""
        res = self.client.post("/api/profile/load-demo")
        self.assertEqual(res.status_code, 200)
        json_data = res.get_json()
        self.assertTrue(json_data["success"])
        self.assertEqual(json_data["patient"]["full_name"], "Rahul Sharma")

    def test_api_emergency_lifecycle(self):
        """Tests emergency trigger and resolution endpoints."""
        # 1. Trigger
        trigger_res = self.client.post("/api/emergency/trigger", json={
            "trigger_type": "MANUAL_SOS",
            "latitude": 12.9716,
            "longitude": 77.5946
        })
        self.assertEqual(trigger_res.status_code, 200)
        event_data = trigger_res.get_json()
        self.assertTrue(event_data["success"])
        emergency_id = event_data["event"]["emergency_id"]

        # 2. Check status
        status_res = self.client.get("/api/emergency/status")
        self.assertEqual(status_res.status_code, 200)
        self.assertTrue(status_res.get_json()["active"])

        # 3. Resolve
        resolve_res = self.client.post("/api/emergency/resolve", json={
            "emergency_id": emergency_id
        })
        self.assertEqual(resolve_res.status_code, 200)
        self.assertTrue(resolve_res.get_json()["success"])

    def test_api_blockchain_operations(self):
        """Tests blockchain verification and tampering endpoints."""
        # Verification
        v_res = self.client.post("/api/blockchain/verify")
        self.assertEqual(v_res.status_code, 200)
        self.assertTrue(v_res.get_json()["success"])

        # Tampering simulation
        t_res = self.client.post("/api/blockchain/tamper")
        self.assertEqual(t_res.status_code, 200)
        self.assertTrue(t_res.get_json()["success"])

        # Re-verify -> should fail
        v2_res = self.client.post("/api/blockchain/verify")
        self.assertFalse(v2_res.get_json()["audit"]["is_valid"])

        # Restore
        r_res = self.client.post("/api/blockchain/restore")
        self.assertEqual(r_res.status_code, 200)
        self.assertTrue(r_res.get_json()["success"])

if __name__ == "__main__":
    unittest.main()
