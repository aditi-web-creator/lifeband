# LifeBand – Smart Emergency Medical Identification & Hospital Alert System

> **B.Tech Computer Science & Engineering (IoT & Blockchain Specialization)**  
> **Academic Prototype & Faculty Demonstration System**  
> *Developed with Python 3, Flask, SQLite3, Cryptographic SHA-256 Hashing, Browser Geolocation API, and Browser DeviceMotion API.*

---

## 1. Executive Summary & Project Objective

**LifeBand** is an emergency medical assistance application designed to bridge the critical "Golden Hour" gap during sudden health crises, vehicular crashes, and accidental falls. 

In real-world trauma events, unconscious or disoriented patients cannot communicate their blood type, life-threatening allergies, or medical history to emergency responders. Administering contraindicated medications (such as Aspirin during hemorrhages or Penicillin to allergic individuals) can be fatal. Furthermore, emergency dispatchers often face delays identifying the optimal trauma facility equipped with ICU capabilities.

**LifeBand solves these challenges through four integrated pillars:**
1. **IoT & Sensor Layer:** Real-time 3-axis accelerometer processing (`DeviceMotion` API) with dynamic shock thresholding and automated 10-second fail-safe emergency countdown.
2. **Blockchain & Cryptographic Layer:** Local SHA-256 linear hash chain verifying medical record immutability and instant tamper detection against unauthorized database changes.
3. **Geospatial & Hospital Triage Layer:** Python-powered spherical Haversine formula calculating exact great-circle distance to emergency hospitals, estimating ambulance arrival time (ETA), and preparing simulated hospital triage telemetry.
4. **Condition-Aware AI First-Aid Engine:** Deterministic clinical reasoning module that cross-references patient allergies and pre-existing illnesses to deliver safe immediate first-aid directives and alert responders against contraindicated drugs.

---

## 2. Technology Stack

- **Backend:** Python 3.12, Flask 3.1, Werkzeug, Jinja2
- **Database:** SQLite3 with Foreign Key constraints and parameterized queries
- **Cryptography:** Standard Library `hashlib` (SHA-256), deterministic canonical JSON serialization
- **Frontend:** Responsive Semantic HTML5, Custom CSS3 Design System (Deep Navy `#0A1128`, Teal `#06B6D4`, Emerald, Rose), Vanilla JavaScript (ES6+)
- **Browser Web APIs:**
  - `DeviceMotionEvent` (Hardware Accelerometer magnitude vector calculation $|a| = \sqrt{a_x^2 + a_y^2 + a_z^2}$)
  - `Geolocation API` (`navigator.geolocation.getCurrentPosition` with high accuracy and offline demo fallback)
  - `Web Audio API` (Synthesizer tone generator for emergency countdown beeps)
- **Testing:** Python `unittest` test suite covering calculations, cryptographic hash chaining, tampering, and Flask HTTP routes.

---

## 3. Architecture & Project File Structure

```text
lifeband/
├── app.py                      # Main Flask application entry point & route controllers
├── config.py                   # Central system configuration parameters
├── requirements.txt            # Python dependencies (Flask, etc.)
├── README.md                   # Complete academic documentation & viva guide
├── database/
│   ├── __init__.py             # Database module exports
│   ├── db.py                   # SQLite connection manager & demo hospital seeder
│   └── schema.sql              # Database DDL with foreign keys and indexes
├── services/
│   ├── __init__.py             # Services module exports
│   ├── medical_service.py      # Patient profile management & blockchain auto-minting
│   ├── emergency_service.py    # SOS trigger, fall escalation, dispatch lifecycle
│   ├── gps_service.py          # Haversine formula, ETA model, coordinate validator
│   ├── hospital_service.py     # Nearest hospital ranking & simulated dispatch payload
│   ├── ai_assistant.py         # Condition-aware first-aid reasoning & contraindications
│   └── blockchain_service.py   # SHA-256 cryptographic hash chain & tamper detection
├── templates/
│   ├── base.html               # Master layout, navigation sidebar, active emergency banner
│   ├── dashboard.html          # Command center: metrics, SOS button, hospital preview
│   ├── profile.html            # Medical profile management form & revision history
│   ├── medical_card.html       # Printable/scannable emergency medical passport
│   ├── emergency.html          # Emergency dispatch status, AI precautions, telemetry
│   ├── fall_detection.html     # IoT accelerometer sensor visualizer & countdown
│   ├── hospitals.html          # Hospital finder, Haversine formula explanation
│   ├── ai_assistant.html       # Interactive condition-aware first-aid explorer
│   ├── blockchain.html         # SHA-256 ledger viewer, live tamper demo button
│   └── presentation.html       # Faculty presentation guide & viva defense sheet
├── static/
│   ├── css/
│   │   └── style.css           # Premium dark navy medical technology design system
│   └── js/
│       ├── main.js             # Shell controller, modals, toasts, SOS triggers
│       ├── fall_detection.js   # DeviceMotion sensor logic & Web Audio beeper
│       ├── geolocation.js      # GPS coordinate acquisition & demo presets
│       └── blockchain.js       # SHA-256 verification and tamper simulation AJAX
└── tests/
    ├── __init__.py
    ├── test_services.py        # Automated unit tests for all mathematical and crypto services
    └── test_routes.py          # Automated HTTP route and endpoint validation tests
```

---

## 4. Installation & Local Execution (Windows / Mac / Linux)

### Prerequisites
- Python 3.10, 3.11, or 3.12 installed on your machine.
- Git (optional, for version control).

### Step 1: Open Terminal in the Project Directory
```powershell
# Navigate to the project root
cd C:\Users\nigam\.gemini\antigravity\scratch\lifeband
```

### Step 2: Create and Activate Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```
*(If PowerShell restricts script execution, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

**On Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Automated Test Suite
Ensure that all mathematical, cryptographic, and route tests pass:
```bash
python -m unittest discover tests
```
*Expected output: `Ran 12 tests in 0.35s ... OK`*

### Step 5: Start the LifeBand Application
```bash
python app.py
```
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 5. Database Schema & Parameterized Queries

The database schema (`database/schema.sql`) uses SQLite3 with foreign keys enabled (`PRAGMA foreign_keys = ON;`) and strictly parameterized queries (`?`) to prevent SQL injection vulnerabilities:

1. **`patients`**: Stores primary patient demographics, blood group, allergies, chronic illnesses, and emergency contacts.
2. **`medical_records_chain`**: Stores immutable cryptographic revisions of the medical profile. Fields: `id`, `patient_id`, `version`, `patient_data_json`, `previous_hash`, `current_hash`, `timestamp`.
3. **`hospitals`**: Pre-seeded sample trauma care hospitals with geographic coordinates, ICU bed availability, and trauma level ratings.
4. **`emergency_events`**: Logs every emergency trigger (`MANUAL_SOS`, `FALL_DETECTION`, `SIMULATED_TEST`), coordinates, assigned hospital, distance in km, ambulance ETA, condition-aware AI guidance, and lifecycle status (`ACTIVE`, `RESOLVED`, `CANCELLED`).

---

## 6. Major Python Modules Explained

### A. `services/blockchain_service.py` (Blockchain Angle)
Implements an educational linear cryptographic hash chain. Every time a patient updates their profile, a canonical JSON snapshot is created with sorted keys:
$$\text{CurrentHash} = \text{SHA256}(\text{Version} \parallel \text{Timestamp} \parallel \text{CanonicalJSON}(\text{Profile}) \parallel \text{PreviousHash})$$
- For Block #1 (Genesis Block), `previous_hash` is $64$ zeros (`0000...0000`).
- For Block $N$, `previous_hash` must match Block $N-1$'s `current_hash`.
- **Tamper Simulation (`simulate_tampering`)**: Directly alters a patient's allergy field in the database without recalculating the hash. When `verify_chain()` runs, it recomputes SHA-256 for each block, instantly flags the hash mismatch, and pinpoints the exact block where tampering took place.

### B. `services/gps_service.py` & `hospital_service.py` (GPS & Triage Angle)
Implements the spherical **Haversine formula** to compute exact great-circle distance between two geographic coordinates $(\phi_1, \lambda_1)$ and $(\phi_2, \lambda_2)$:
$$a = \sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)$$
$$c = 2 \cdot \text{atan2}\left(\sqrt{a}, \sqrt{1-a}\right)$$
$$d = R \cdot c \quad (R = 6371.0\text{ km})$$
- Sorts medical facilities by distance to find the closest trauma facility.
- Computes realistic ambulance ETA based on urban emergency response speed ($35\text{ km/h}$) + $2$-minute dispatch triage buffer.
- Generates a simulated HL7 / JSON clinical pre-arrival dispatch notification packet.

### C. `services/ai_assistant.py` (AI Decision Support Angle)
Implements a condition-aware medical rule engine:
- Reads patient allergies (e.g. Penicillin, Aspirin, Sulfa, Latex).
- Reads chronic conditions (e.g. Asthma, Diabetes, Hypertension, Epilepsy).
- Scans emergency scenarios (Fall Trauma, Cardiac Chest Pain, Asthma Distress, Fainting, Severe Bleeding).
- **Safety Filtering:** If a patient with an Aspirin allergy experiences acute chest pain, the engine automatically issues a high-priority warning: *"DO NOT administer Aspirin or NSAIDs; severe allergic contraindication!"*
- Distinguishes emergency first-aid stabilization from medical diagnosis with an ethical disclaimer.

### D. `services/emergency_service.py` (Emergency Orchestration)
Manages the end-to-end incident lifecycle: GPS acquisition $\rightarrow$ nearest hospital lookup $\rightarrow$ AI precaution generation $\rightarrow$ database logging $\rightarrow$ simulated ambulance dispatch $\rightarrow$ incident resolution.

---

## 7. 11-Step Faculty Demonstration Workflow

Follow this sequence during your practical exam or presentation:

1. **Baseline Setup:** Open the web app at `http://127.0.0.1:5000` and click **"Load Demo Patient"**. This seeds patient *"Rahul Sharma"* ($21$, Blood: $B+$, Allergies: *Penicillin & Aspirin*, Chronic: *Mild Asthma*).
2. **Medical Profile & Blockchain Minting:** Navigate to **Medical Profile** and show that saving the profile created **Block #1 (Genesis Block)** with SHA-256 seal.
3. **Emergency ID Card:** Open **Emergency ID Card** to display the high-contrast medical passport designed for paramedics.
4. **IoT Fall Detection Simulation:** Go to **Fall Detection (IoT)**. Explain the 3-axis accelerometer formula $|a| = \sqrt{a_x^2 + a_y^2 + a_z^2}$.
5. **Impact Trigger & Audio Countdown:** Click **"Simulate Sudden Fall Impact"**. Observe the peak acceleration jump ($34.8\text{ m/s}^2$), the audible warning beeps, and the 10-second countdown overlay with the "I AM OK" button.
6. **Auto-Escalation to Emergency SOS:** Let the countdown reach 0. The app automatically triggers Emergency SOS!
7. **Emergency Command Dashboard:** The dashboard displays CODE RED ACTIVE status, patient profile, locked GPS coordinates, and assigned hospital (*St. Jude Trauma Center*).
8. **Haversine Distance & ETA:** Point out the calculated distance ($0.85\text{ km}$) and ambulance ETA ($\sim 4\text{ mins}$).
9. **Condition-Aware AI Guidance:** Show that the AI Assistant explicitly flags: *"PATIENT ALLERGIC TO NSAIDs/ASPIRIN - Under no circumstances administer Aspirin!"*
10. **Simulate Blockchain Tampering:** Go to **Blockchain Integrity** and click **"Simulate Record Tampering"**. Explain that an attacker modified SQLite directly. Click **"Re-verify Cryptographic Hashes"** $\rightarrow$ the system flags a bright red **TAMPER DETECTED AT BLOCK V1** error!
11. **Resolve & Restore:** Click **"Restore & Re-sign Ledger"** to restore cryptographic consistency, then click **"Mark Emergency Resolved"** to finish the demo.

---

## 8. Technical Viva Voce Questions & Answers

### Q1: How does the Fall Detection algorithm work? (IoT)
**Answer:** It processes linear acceleration along 3 orthogonal spatial axes ($a_x, a_y, a_z$) sampled from the device accelerometer via the browser `DeviceMotion` API. The total resultant acceleration vector is computed as $|a| = \sqrt{a_x^2 + a_y^2 + a_z^2}$. When $|a|$ exceeds a calibrated threshold ($25.0\text{ m/s}^2$, $\sim 2.55g$) followed by immobility, an impact is inferred. A 10-second fail-safe countdown gives conscious users time to cancel false alarms.

### Q2: How does the blockchain hash chain protect medical records? (Blockchain)
**Answer:** Each record revision contains the SHA-256 cryptographic digest of its predecessor. Because SHA-256 is collision-resistant and possesses the avalanche effect, altering even a single character (e.g. changing blood group from $B+$ to $O-$ or deleting an allergy) produces a completely different hash. This creates a mismatch between the recalculated hash and stored hash, cryptographically proving tampering.

### Q3: Why is the Haversine formula necessary for GPS? (Mathematics)
**Answer:** The Earth is a sphere, so planar Euclidean distance ($d = \sqrt{\Delta x^2 + \Delta y^2}$) introduces significant distortion because meridians of longitude converge at the poles. The spherical Haversine formula computes the true great-circle distance across the Earth's curved surface ($R = 6371.0\text{ km}$), maintaining accuracy within $0.5\%$.

### Q4: Why use deterministic Python logic instead of a pure cloud LLM for AI first-aid? (AI / Safety)
**Answer:** Emergency medicine requires zero hallucination and ultra-low latency. An unconstrained generative LLM might hallucinate contraindicated medications or fail without an internet connection. A deterministic rule engine guarantees immediate, 100% predictable, condition-aware guidance, while keeping the application fully functional offline without requiring paid API keys.

---

## 9. Limitations & Future Scope

### Current Prototype Limitations
1. **Simulation Scope:** Emergency alerts and hospital telemetry are simulated locally within SQLite and do not place real-world 112/911 emergency dispatch calls.
2. **Local Blockchain:** Operates as a local single-node cryptographic hash chain rather than a globally distributed multi-node consensus network.

### Future Enhancements
1. **Wearable IoT Hardware:** Integration with ESP32 / Arduino microcontrollers and dedicated MPU6050 accelerometer sensors via Bluetooth Low Energy (BLE).
2. **Cellular GSM/SMS Fallback:** Hardware GSM module for sending SMS alerts with GPS coordinates even when mobile data/Wi-Fi is unavailable.
3. **Decentralized Blockchain Consortium:** Anchoring record hashes onto Ethereum or Hyperledger Fabric smart contracts for verifiable cross-hospital health record exchange.
