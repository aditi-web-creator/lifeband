"""
LifeBand – Smart Emergency Medical Identification & Hospital Alert System
========================================================================
Main Flask Application Entry Point.
Academic Prototype & Live Demonstration System for CSE (IoT & Blockchain).

Author: CSE Student (IoT & Blockchain)
Platform: Python 3 / Flask / SQLite / SHA-256 / Geolocation & DeviceMotion APIs
"""

import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from config import Config
from database.db import init_db
from services.medical_service import (
    get_active_patient, save_patient_profile, load_demo_patient_profile,
    calculate_profile_completion, get_patient_by_id
)
from services.blockchain_service import (
    verify_chain, get_record_chain, simulate_tampering, restore_tampered_records
)
from services.gps_service import (
    haversine_distance, calculate_ambulance_eta, get_demo_locations, validate_coordinates
)
from services.hospital_service import (
    get_all_hospitals, find_nearest_hospitals, get_hospital_by_id
)
from services.ai_assistant import generate_emergency_guidance
from services.emergency_service import (
    trigger_emergency, get_active_emergency, resolve_emergency, cancel_emergency,
    get_emergency_history
)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database and seed sample hospitals upon startup
with app.app_context():
    init_db()

@app.context_processor
def inject_global_template_vars():
    """Injects common metadata across all templates."""
    active_patient = get_active_patient()
    active_emergency = get_active_emergency()
    completion = calculate_profile_completion(active_patient)
    
    return {
        "app_name": Config.APP_NAME,
        "app_tagline": Config.APP_TAGLINE,
        "version": Config.VERSION,
        "active_patient": active_patient,
        "active_emergency": active_emergency,
        "profile_completion": completion,
        "default_lat": Config.DEFAULT_LATITUDE,
        "default_lon": Config.DEFAULT_LONGITUDE,
        "default_location_name": Config.DEFAULT_LOCATION_NAME,
        "demo_locations": get_demo_locations()
    }

# ==========================================
# PAGE ROUTES (UI VIEWS)
# ==========================================

@app.route("/")
@app.route("/dashboard")
def dashboard():
    """Landing dashboard page displaying patient health summary, emergency status, and quick actions."""
    patient = get_active_patient()
    active_emer = get_active_emergency()
    history = get_emergency_history(limit=5)
    
    # Nearest hospitals from default coordinates
    hospitals = find_nearest_hospitals(Config.DEFAULT_LATITUDE, Config.DEFAULT_LONGITUDE, limit=3)
    
    # Blockchain integrity summary
    blockchain_report = verify_chain(patient["id"]) if patient else {"is_valid": True, "total_blocks": 0}
    
    return render_template(
        "dashboard.html",
        active_tab="dashboard",
        patient=patient,
        active_emergency=active_emer,
        emergency_history=history,
        nearest_hospitals=hospitals,
        blockchain_report=blockchain_report
    )

@app.route("/profile", methods=["GET", "POST"])
def profile():
    """Medical Profile Management: view and update patient clinical records."""
    patient = get_active_patient()
    
    if request.method == "POST":
        try:
            profile_data = {
                "full_name": request.form.get("full_name"),
                "age": request.form.get("age"),
                "blood_group": request.form.get("blood_group"),
                "allergies": request.form.get("allergies"),
                "chronic_diseases": request.form.get("chronic_diseases"),
                "previous_surgeries": request.form.get("previous_surgeries"),
                "current_medications": request.form.get("current_medications"),
                "emergency_contact_name": request.form.get("emergency_contact_name"),
                "emergency_contact_phone": request.form.get("emergency_contact_phone"),
            }
            
            patient_id = patient["id"] if patient else None
            updated_patient, block_info = save_patient_profile(profile_data, patient_id=patient_id)
            flash(f"Medical profile saved! Cryptographic Hash Block v{block_info['version']} generated.", "success")
            return redirect(url_for("profile"))
        except Exception as e:
            flash(f"Error saving profile: {str(e)}", "danger")
            
    chain = get_record_chain(patient["id"]) if patient else []
    return render_template("profile.html", active_tab="profile", patient=patient, chain=chain)

@app.route("/medical-card")
def medical_card():
    """Emergency Medical Card: high-contrast, instantly accessible clinical summary for first responders."""
    patient = get_active_patient()
    if not patient:
        patient, _ = load_demo_patient_profile()
        
    chain = get_record_chain(patient["id"])
    latest_hash = chain[-1]["current_hash"] if chain else "UNVERIFIED"
    
    return render_template(
        "medical_card.html",
        active_tab="medical-card",
        patient=patient,
        latest_hash=latest_hash
    )

@app.route("/emergency", methods=["GET"])
def emergency_view():
    """Emergency SOS Page: interactive emergency trigger, live dispatch overview, and AI precautions."""
    patient = get_active_patient()
    active_emer = get_active_emergency()
    history = get_emergency_history(limit=10)
    hospitals = find_nearest_hospitals(Config.DEFAULT_LATITUDE, Config.DEFAULT_LONGITUDE, limit=5)
    
    return render_template(
        "emergency.html",
        active_tab="emergency",
        patient=patient,
        active_emergency=active_emer,
        history=history,
        hospitals=hospitals
    )

@app.route("/fall-detection")
def fall_detection():
    """Fall Detection IoT Simulation: accelerometer sensor processing, impact thresholding, and countdown timer."""
    patient = get_active_patient()
    return render_template(
        "fall_detection.html",
        active_tab="fall-detection",
        patient=patient,
        default_threshold=Config.DEFAULT_FALL_THRESHOLD,
        countdown_seconds=Config.FALL_COUNTDOWN_SECONDS
    )

@app.route("/hospitals")
def hospitals_view():
    """Hospital Finder: Haversine distance calculations, ICU readiness, and emergency facilities."""
    lat = request.args.get("lat", default=Config.DEFAULT_LATITUDE, type=float)
    lon = request.args.get("lon", default=Config.DEFAULT_LONGITUDE, type=float)
    
    ranked_hospitals = find_nearest_hospitals(lat, lon, limit=10)
    
    return render_template(
        "hospitals.html",
        active_tab="hospitals",
        hospitals=ranked_hospitals,
        current_lat=lat,
        current_lon=lon
    )

@app.route("/ai-assistant")
def ai_assistant_view():
    """AI First-Aid Guidance: condition-aware first aid protocols and contraindication warnings."""
    patient = get_active_patient()
    scenario = request.args.get("scenario", "GENERAL_SOS")
    guidance = generate_emergency_guidance(scenario, patient)
    
    return render_template(
        "ai_assistant.html",
        active_tab="ai-assistant",
        patient=patient,
        guidance=guidance,
        selected_scenario=scenario
    )

@app.route("/blockchain")
def blockchain_view():
    """Blockchain Medical Record Integrity: SHA-256 hash chain explorer, tamper demonstration, and verification."""
    patient = get_active_patient()
    if not patient:
        patient, _ = load_demo_patient_profile()
        
    chain_audit = verify_chain(patient["id"])
    
    return render_template(
        "blockchain.html",
        active_tab="blockchain",
        patient=patient,
        audit=chain_audit
    )

@app.route("/presentation")
def presentation_guide():
    """Interactive Faculty Presentation and Viva Guide for B.Tech project defense."""
    return render_template("presentation.html", active_tab="presentation")

# ==========================================
# REST API ENDPOINTS (FOR AJAX / JSON INTERACTION)
# ==========================================

@app.route("/api/profile/load-demo", methods=["POST"])
def api_load_demo():
    """Loads realistic sample patient profile with clinical history for live presentation."""
    try:
        patient, block = load_demo_patient_profile()
        return jsonify({
            "success": True,
            "message": "Demo profile loaded successfully with Genesis Block created in Blockchain ledger.",
            "patient": patient,
            "blockchain_block": block
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/emergency/trigger", methods=["POST"])
def api_trigger_emergency():
    """Triggers an emergency incident (Manual SOS, Fall Sensor, or Test)."""
    data = request.get_json() or {}
    try:
        trigger_type = data.get("trigger_type", "MANUAL_SOS")
        lat = data.get("latitude")
        lon = data.get("longitude")
        loc_name = data.get("location_name")
        hospital_id = data.get("hospital_id")
        notes = data.get("notes")
        
        event = trigger_emergency(
            trigger_type=trigger_type,
            latitude=lat,
            longitude=lon,
            location_name=loc_name,
            hospital_id=hospital_id,
            notes=notes
        )
        return jsonify({"success": True, "event": event})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/emergency/status", methods=["GET"])
def api_emergency_status():
    """Returns current active emergency details."""
    active = get_active_emergency()
    return jsonify({"active": active is not None, "event": active})

@app.route("/api/emergency/resolve", methods=["POST"])
def api_resolve_emergency():
    """Resolves an active emergency."""
    data = request.get_json() or {}
    emergency_id = data.get("emergency_id")
    notes = data.get("notes", "Resolved successfully by demo operator.")
    
    if not emergency_id:
        active = get_active_emergency()
        if active:
            emergency_id = active["id"]
        else:
            return jsonify({"success": False, "message": "No active emergency found to resolve."}), 400
            
    success = resolve_emergency(emergency_id, notes=notes)
    return jsonify({"success": success, "message": "Emergency marked as RESOLVED."})

@app.route("/api/emergency/cancel", methods=["POST"])
def api_cancel_emergency():
    """Cancels a false alarm."""
    data = request.get_json() or {}
    emergency_id = data.get("emergency_id")
    reason = data.get("reason", "Cancelled by user (False alarm).")
    
    if not emergency_id:
        active = get_active_emergency()
        if active:
            emergency_id = active["id"]
        else:
            return jsonify({"success": False, "message": "No active emergency found to cancel."}), 400
            
    success = cancel_emergency(emergency_id, reason=reason)
    return jsonify({"success": success, "message": "Emergency alert cancelled."})

@app.route("/api/hospitals/nearest", methods=["GET"])
def api_nearest_hospitals():
    """API endpoint to find nearest hospitals using Haversine formula."""
    try:
        lat = float(request.args.get("lat", Config.DEFAULT_LATITUDE))
        lon = float(request.args.get("lon", Config.DEFAULT_LONGITUDE))
        hospitals = find_nearest_hospitals(lat, lon, limit=5)
        return jsonify({"success": True, "count": len(hospitals), "hospitals": hospitals})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route("/api/blockchain/verify", methods=["POST"])
def api_verify_blockchain():
    """Runs complete cryptographic SHA-256 verification of the medical ledger."""
    patient = get_active_patient()
    if not patient:
        patient, _ = load_demo_patient_profile()
        
    audit = verify_chain(patient["id"])
    return jsonify({"success": True, "audit": audit})

@app.route("/api/blockchain/tamper", methods=["POST"])
def api_tamper_blockchain():
    """Simulates unauthorized record tampering to demonstrate cryptographic failure."""
    patient = get_active_patient()
    if not patient:
        patient, _ = load_demo_patient_profile()
        
    res = simulate_tampering(patient["id"])
    return jsonify(res)

@app.route("/api/blockchain/restore", methods=["POST"])
def api_restore_blockchain():
    """Restores the blockchain ledger to an intact, verified state."""
    patient = get_active_patient()
    if not patient:
        patient, _ = load_demo_patient_profile()
        
    # Reload demo profile data to restore consistency
    load_demo_patient_profile()
    return jsonify({"success": True, "message": "Record restored and re-hashed into valid blockchain state."})

@app.route("/api/ai/guidance", methods=["POST"])
def api_ai_guidance():
    """Generates situation and condition-aware first-aid guidance."""
    data = request.get_json() or {}
    scenario = data.get("scenario", "GENERAL_SOS")
    patient = get_active_patient()
    guidance = generate_emergency_guidance(scenario, patient)
    return jsonify({"success": True, "guidance": guidance})

# ==========================================
# APPLICATION BOOTSTRAP
# ==========================================

if __name__ == "__main__":
    # Ensure database is initialized
    init_db()
    
    # Auto-load demo patient if empty for turnkey faculty demonstration
    if not get_active_patient():
        load_demo_patient_profile()
        print("[LifeBand] Initialized demo patient profile 'Rahul Sharma' (B+).")
        
    print(f"\n=======================================================")
    print(f" {Config.APP_NAME} v{Config.VERSION} – Healthcare Emergency System")
    print(f" Server active at: http://127.0.0.1:5000")
    print(f"=======================================================\n")
    
    app.run(host="0.0.0.0", port=5000, debug=Config.DEBUG)
