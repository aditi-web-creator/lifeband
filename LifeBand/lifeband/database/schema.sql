-- LifeBand Database Schema
-- SQLite3 with Foreign Keys enabled

PRAGMA foreign_keys = ON;

-- 1. Patients Table: Current active medical profiles
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    age INTEGER NOT NULL,
    blood_group TEXT NOT NULL,
    allergies TEXT DEFAULT '',
    chronic_diseases TEXT DEFAULT '',
    previous_surgeries TEXT DEFAULT '',
    current_medications TEXT DEFAULT '',
    emergency_contact_name TEXT NOT NULL,
    emergency_contact_phone TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Blockchain Medical Records Chain Table
-- Stores an immutable hash chain of patient medical profile revisions
CREATE TABLE IF NOT EXISTS medical_records_chain (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    version INTEGER NOT NULL,
    patient_data_json TEXT NOT NULL,
    previous_hash TEXT NOT NULL,
    current_hash TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

-- 3. Hospitals Table: Pre-populated sample/fictional facilities for demo
CREATE TABLE IF NOT EXISTS hospitals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    contact_phone TEXT NOT NULL,
    emergency_availability TEXT NOT NULL,
    icu_beds_available INTEGER NOT NULL DEFAULT 8,
    trauma_level TEXT NOT NULL DEFAULT 'Level 1 Trauma Center',
    specialties TEXT NOT NULL
);

-- 4. Emergency Events Table: Logs SOS activations, fall detections, and resolutions
CREATE TABLE IF NOT EXISTS emergency_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    trigger_type TEXT NOT NULL, -- 'MANUAL_SOS', 'FALL_DETECTION', 'SIMULATED_TEST'
    status TEXT NOT NULL DEFAULT 'ACTIVE', -- 'ACTIVE', 'CANCELLED', 'RESOLVED'
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    location_name TEXT DEFAULT 'GPS Coordinates Locked',
    assigned_hospital_id INTEGER,
    hospital_name TEXT,
    distance_km REAL,
    estimated_eta_mins INTEGER,
    ai_guidance_json TEXT,
    dispatched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (assigned_hospital_id) REFERENCES hospitals(id)
);

-- Indices for rapid querying
CREATE INDEX IF NOT EXISTS idx_records_patient ON medical_records_chain(patient_id);
CREATE INDEX IF NOT EXISTS idx_emergency_status ON emergency_events(status);
