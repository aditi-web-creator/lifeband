"""
AI First-Aid Emergency Assistant Service
========================================
Condition-Aware First-Aid Guidance Engine.
Cross-references patient medical profiles (allergies, chronic illnesses, medications)
with clinical emergency scenarios to provide cautious, personalized, and safe
immediate-care instructions while emergency services are en route.

ETHICAL MEDICAL NOTICE:
This module provides rule-based decision support for educational and simulation purposes.
It does NOT provide medical diagnosis or replace licensed emergency responders.
"""

from typing import Dict, List, Optional

def analyze_allergies(allergies_text: str) -> List[str]:
    """Extracts known clinical allergy alerts from user input."""
    if not allergies_text:
        return []
    text = allergies_text.lower()
    alerts = []
    
    if any(k in text for k in ["aspirin", "nsaid", "ibuprofen"]):
        alerts.append("PATIENT ALLERGIC TO NSAIDs/ASPIRIN: Under no circumstances administer Aspirin or Ibuprofen during chest pain or trauma.")
    if any(k in text for k in ["penicillin", "amoxicillin", "antibiotic"]):
        alerts.append("ANTIBIOTIC WARNING: Severe penicillin/beta-lactam allergy recorded in profile.")
    if any(k in text for k in ["sulfa", "sulfonamide"]):
        alerts.append("SULFA ALLERGY ALERT: Avoid all sulfonamide-based medical preparations.")
    if "latex" in text:
        alerts.append("LATEX SENSITIVITY: Ensure responding EMTs use non-latex, nitrile protective gear.")
    if any(k in text for k in ["peanut", "nut", "shellfish", "egg"]):
        alerts.append("SEVERE FOOD/ANAPHYLAXIS ALLERGY: Watch for airway constriction; check for personal Epinephrine auto-injector.")
        
    return alerts

def analyze_chronic_conditions(chronic_text: str, medications_text: str = "") -> List[str]:
    """Generates condition-specific emergency precautions."""
    alerts = []
    c_text = (chronic_text or "").lower()
    m_text = (medications_text or "").lower()
    
    # Respiratory / Asthma
    if any(k in c_text for k in ["asthma", "copd", "bronchitis"]):
        alerts.append("ASTHMA / RESPIRATORY CONDITION: Keep patient seated upright to ease breathing. Check if patient has their prescribed rescue inhaler (e.g. Albuterol). Never force them to lie flat.")
        
    # Diabetes / Hypoglycemia
    if any(k in c_text for k in ["diabetes", "diabetic", "hypoglycemia", "insulin"]):
        alerts.append("DIABETES PROTOCOL: Altered mental state may indicate acute hypoglycemia or ketoacidosis. If patient is conscious and can swallow, provide fast-acting glucose (fruit juice/honey). If unconscious, DO NOT put liquids in mouth.")
        
    # Cardiovascular / Hypertension
    if any(k in c_text for k in ["hypertension", "blood pressure", "cardiac", "heart", "angina"]):
        alerts.append("CARDIOVASCULAR HISTORY: Keep patient completely calm. Avoid sudden positional changes or physical exertion. Loosen tight clothing around chest and neck.")
        
    # Epilepsy / Seizures
    if any(k in c_text for k in ["epilepsy", "seizure", "convulsion"]):
        alerts.append("SEIZURE PRECAUTION: Clear sharp objects around patient. Do NOT restrain limbs or insert anything into the mouth. Place in recovery position after seizing stops.")
        
    # Anticoagulants / Blood thinners
    if any(k in m_text for k in ["warfarin", "aspirin", "clopidogrel", "heparin", "blood thinner", "apixaban"]):
        alerts.append("HEMORRHAGE RISK (ANTICOAGULANTS): Patient is on blood-thinning medication. Any external bleeding will take significantly longer to clot; apply continuous firm direct pressure with sterile dressing.")

    return alerts

def generate_emergency_guidance(scenario: str, patient_profile: Optional[Dict] = None) -> Dict:
    """
    Main AI reasoning entry point.
    Generates situation-specific immediate actions, critical contraindications,
    and profile-specific cautions.
    """
    profile = patient_profile or {}
    allergies = profile.get("allergies", "")
    chronic = profile.get("chronic_diseases", "")
    meds = profile.get("current_medications", "")
    
    allergy_warnings = analyze_allergies(allergies)
    condition_warnings = analyze_chronic_conditions(chronic, meds)
    
    scenario_clean = (scenario or "GENERAL_SOS").upper()
    
    # 1. Fall Detection / Impact Trauma
    if "FALL" in scenario_clean or "IMPACT" in scenario_clean:
        title = "Fall & Impact Trauma Protocol"
        steps = [
            "Assess Consciousness & Breathing: Gently call the patient's name and check if chest rises regularly.",
            "Suspected Spinal / Head Injury: DO NOT move the patient unless there is an immediate environmental hazard (e.g., fire). Keep the head, neck, and spine aligned in neutral position.",
            "Check for Severe Hemorrhage: Look for active bleeding. If found, apply direct, firm pressure using clean cloth or dressing.",
            "Monitor Pupil & Neurological Response: Check for disorientation, slurred speech, or pupil asymmetry.",
            "Comfort & Temperature: Cover the patient with a blanket or coat to prevent hypothermia and clinical shock."
        ]
        contraindications = [
            "DO NOT forcefully pull the patient up to their feet immediately.",
            "DO NOT shake the patient or twist their neck.",
            "DO NOT remove helmets or protective gear if a neck injury is suspected, unless airway is obstructed.",
            "DO NOT offer food, drink, or pain medications orally until EMT evaluation."
        ]
        
    # 2. Cardiac / Chest Pain
    elif "CARDIAC" in scenario_clean or "CHEST" in scenario_clean:
        title = "Acute Chest Discomfort & Cardiac Protocol"
        aspirin_safe = not any("aspirin" in a.lower() for a in allergy_warnings)
        
        steps = [
            "Seat Patient in 'W' Position: Sit the patient on the floor, leaning back against a wall or knees bent, to reduce heart workload.",
            "Loosen Constrictive Clothing: Unbutton collar, loosen tie, and unfasten tight belts.",
            "Prescribed Nitroglycerin: If patient has doctor-prescribed heart medication, assist them in taking it as directed.",
            "CPR Preparedness: If patient becomes unresponsive and stops breathing, immediately initiate chest compressions at 100-120 bpm (depth ~5 cm).",
            "Maintain Calm Atmosphere: Minimise bystander noise and panic."
        ]
        
        contraindications = [
            "DO NOT let the patient walk or exert themselves.",
            "DO NOT give Aspirin if patient is allergic to NSAIDs/Aspirin or has bleeding disorders.",
            "DO NOT dismiss chest pain as simple indigestion or muscle cramp."
        ]
        
    # 3. Unconscious / Fainting
    elif "UNCONSCIOUS" in scenario_clean or "FAINT" in scenario_clean:
        title = "Unresponsiveness & Fainting Protocol"
        steps = [
            "Verify Airway, Breathing, Circulation (ABC): Tilt head gently back, lift chin, and check breathing for 10 seconds.",
            "Recovery Position: If breathing normally, roll patient onto their side (recovery position) to keep airway open and prevent choking from vomit.",
            "Elevate Legs (If simple faint without trauma): Elevate legs 12 inches (30 cm) to restore cerebral perfusion.",
            "Fresh Air & Ventilation: Ensure adequate air circulation around patient."
        ]
        contraindications = [
            "DO NOT slap the patient's face or splash cold water.",
            "DO NOT administer oral liquids, food, or tablets to an unconscious individual.",
            "DO NOT place a pillow under the patient's head while unconscious as it can kink the airway."
        ]
        
    # 4. Respiratory / Asthma
    elif "ASTHMA" in scenario_clean or "BREATH" in scenario_clean:
        title = "Acute Respiratory Distress Protocol"
        steps = [
            "Position Upright: Sit patient leaning slightly forward on a table or chair.",
            "Locate Rescue Inhaler: Assist with 2 to 4 puffs of their prescribed bronchodilator (via spacer if available).",
            "Slow, Paced Breathing: Coach the patient to breathe in through the nose and out through pursed lips.",
            "Emergency Escalation: If lips or fingertips turn blue/cyanotic, inform dispatcher of severe hypoxia immediately."
        ]
        contraindications = [
            "DO NOT force the patient to lie down.",
            "DO NOT crowd the patient; maintain open airflow."
        ]
        
    # 5. Default Universal Emergency SOS
    else:
        title = "Universal Emergency First-Aid Protocol"
        steps = [
            "Ensure Scene Safety: Verify that you and the patient are safe from electrical, traffic, or falling hazards.",
            "Check Vital Responses: Ask loud questions ('Are you okay? Can you hear me?').",
            "Control Visible Bleeding: Apply continuous direct compression over wounds.",
            "Prevent Shock: Keep patient lying flat, warm, and reassured.",
            "Prepare for Responders: Clear entry doors and corridors for arriving paramedics."
        ]
        contraindications = [
            "DO NOT leave patient unattended.",
            "DO NOT administer prescription medication unless explicitly guided by physician.",
            "DO NOT move patient unnecessarily if trauma is possible."
        ]
        
    return {
        "scenario": scenario_clean,
        "title": title,
        "immediate_actions": steps,
        "contraindications": contraindications,
        "allergy_warnings": allergy_warnings,
        "condition_warnings": condition_warnings,
        "patient_context": {
            "name": profile.get("full_name", "Anonymous Patient"),
            "blood_group": profile.get("blood_group", "Unknown"),
            "recorded_allergies": allergies or "None",
            "recorded_conditions": chronic or "None"
        },
        "disclaimer": "OFFICIAL LIFEBAND FIRST-AID ASSISTANCE: Guidance is condition-aware and deterministic. It does NOT substitute for professional medical practitioners. Nearby hospital and EMS units have been alerted."
    }
