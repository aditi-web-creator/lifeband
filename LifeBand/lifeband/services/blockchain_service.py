"""
Blockchain Medical Record Integrity Service
============================================
Educational blockchain-style cryptographic hash chain implementation using SHA-256.
Ensures verifiable data integrity, version tracking, and tamper detection for
patient emergency medical records.

NOTE FOR FACULTY VIVA:
This implements a linear cryptographic hash chain (similar to Bitcoin/Ethereum block hashing),
where every revision contains the cryptographic hash of its predecessor. Any modification
to past medical history invalidates all subsequent hashes, providing cryptographic proof of tampering.
"""

import hashlib
import json
from datetime import datetime, timezone
from database.db import get_db_connection, dict_from_row

GENESIS_PREVIOUS_HASH = "0" * 64

def canonical_json(data: dict) -> str:
    """Returns deterministic canonical JSON string with sorted keys to ensure consistent hashing."""
    return json.dumps(data, sort_keys=True, separators=(',', ':'))

def calculate_hash(version: int, timestamp: str, patient_data: dict, previous_hash: str) -> str:
    """
    Computes a cryptographic SHA-256 digest of block contents.
    Formula: SHA-256(version || timestamp || canonical_json(patient_data) || previous_hash)
    """
    serialized_payload = f"{version}{timestamp}{canonical_json(patient_data)}{previous_hash}"
    return hashlib.sha256(serialized_payload.encode('utf-8')).hexdigest()

def record_profile_version(patient_id: int, patient_data: dict) -> dict:
    """
    Appends a new immutable revision block to the patient's medical record chain.
    If no previous blocks exist, initializes the Genesis block.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Retrieve the latest block for this patient
        cursor.execute("""
            SELECT version, current_hash 
            FROM medical_records_chain 
            WHERE patient_id = ? 
            ORDER BY version DESC 
            LIMIT 1
        """, (patient_id,))
        last_block = cursor.fetchone()
        
        now_iso = datetime.now(timezone.utc).isoformat()
        
        if last_block is None:
            # Genesis Block (Version 1)
            version = 1
            previous_hash = GENESIS_PREVIOUS_HASH
        else:
            version = last_block['version'] + 1
            previous_hash = last_block['current_hash']
            
        current_hash = calculate_hash(version, now_iso, patient_data, previous_hash)
        payload_json = canonical_json(patient_data)
        
        cursor.execute("""
            INSERT INTO medical_records_chain (
                patient_id, version, patient_data_json, previous_hash, current_hash, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (patient_id, version, payload_json, previous_hash, current_hash, now_iso))
        
        conn.commit()
        record_id = cursor.lastrowid
        
        return {
            "record_id": record_id,
            "patient_id": patient_id,
            "version": version,
            "previous_hash": previous_hash,
            "current_hash": current_hash,
            "timestamp": now_iso
        }
    finally:
        conn.close()

def get_record_chain(patient_id: int) -> list:
    """Fetches all history blocks in chronological order."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, patient_id, version, patient_data_json, previous_hash, current_hash, timestamp
            FROM medical_records_chain
            WHERE patient_id = ?
            ORDER BY version ASC
        """, (patient_id,))
        rows = cursor.fetchall()
        
        chain = []
        for row in rows:
            record = dict_from_row(row)
            try:
                record['patient_data'] = json.loads(record['patient_data_json'])
            except Exception:
                record['patient_data'] = {}
            chain.append(record)
        return chain
    finally:
        conn.close()

def verify_chain(patient_id: int) -> dict:
    """
    Performs complete cryptographic verification of the patient's medical hash chain.
    
    Verification criteria:
    1. Genesis block has previous_hash == '0'*64.
    2. Block's stored current_hash strictly matches recalculation using SHA-256.
    3. Block's previous_hash strictly matches previous block's current_hash.
    
    Returns structured audit report including tamper locations if detected.
    """
    chain = get_record_chain(patient_id)
    if not chain:
        return {
            "is_valid": True,
            "total_blocks": 0,
            "status": "EMPTY",
            "message": "No medical record blocks found for this patient.",
            "tampered_at_version": None,
            "audit_blocks": []
        }
        
    audit_blocks = []
    is_chain_intact = True
    tampered_at = None
    expected_previous_hash = GENESIS_PREVIOUS_HASH
    
    for idx, block in enumerate(chain):
        block_version = block['version']
        stored_prev_hash = block['previous_hash']
        stored_curr_hash = block['current_hash']
        patient_data = block['patient_data']
        timestamp = block['timestamp']
        
        # Recalculate hash from ground truth
        recalculated_hash = calculate_hash(block_version, timestamp, patient_data, stored_prev_hash)
        
        hash_integrity_valid = (stored_curr_hash == recalculated_hash)
        linkage_valid = (stored_prev_hash == expected_previous_hash)
        
        block_valid = hash_integrity_valid and linkage_valid
        
        if not block_valid and is_chain_intact:
            is_chain_intact = False
            tampered_at = block_version
            
        audit_blocks.append({
            "version": block_version,
            "timestamp": timestamp,
            "stored_previous_hash": stored_prev_hash,
            "expected_previous_hash": expected_previous_hash,
            "stored_current_hash": stored_curr_hash,
            "recalculated_hash": recalculated_hash,
            "hash_matches": hash_integrity_valid,
            "linkage_valid": linkage_valid,
            "is_valid": block_valid,
            "patient_data": patient_data
        })
        
        # For the next block in chain
        expected_previous_hash = stored_curr_hash
        
    return {
        "is_valid": is_chain_intact,
        "total_blocks": len(chain),
        "status": "VALID" if is_chain_intact else "TAMPERED",
        "message": "All cryptographic SHA-256 hashes and block linkages verified successfully." if is_chain_intact 
                   else f"Cryptographic integrity failed at Block Version {tampered_at}! Unauthorized modification detected.",
        "tampered_at_version": tampered_at,
        "latest_hash": chain[-1]['current_hash'] if chain else None,
        "audit_blocks": audit_blocks
    }

def simulate_tampering(patient_id: int) -> dict:
    """
    Demonstrates security vulnerability when raw database records are modified without cryptographic consensus.
    Alters a medical record in SQLite directly WITHOUT updating the SHA-256 hash.
    This provides an immediate demonstration during project presentation.
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # Find latest or target block
        cursor.execute("""
            SELECT id, version, patient_data_json, current_hash 
            FROM medical_records_chain 
            WHERE patient_id = ? 
            ORDER BY version DESC 
            LIMIT 1
        """, (patient_id,))
        block = cursor.fetchone()
        
        if not block:
            return {"success": False, "message": "No block found to tamper with."}
            
        data = json.loads(block['patient_data_json'])
        original_allergies = data.get("allergies", "None")
        
        # Inject malicious/unauthorized change: wipe allergies or modify blood group
        data["allergies"] = "NONE (TAMPERED: Critical allergies deleted by attacker!)"
        data["blood_group"] = "O- (TAMPERED)"
        tampered_json = canonical_json(data)
        
        # Update raw payload without altering the hash
        cursor.execute("""
            UPDATE medical_records_chain 
            SET patient_data_json = ? 
            WHERE id = ?
        """, (tampered_json, block['id']))
        conn.commit()
        
        return {
            "success": True,
            "tampered_version": block['version'],
            "original_allergies": original_allergies,
            "tampered_data": data,
            "message": f"Block Version {block['version']} content was altered directly in SQLite. Cryptographic hash remains unchanged. Run verification to demonstrate detection!"
        }
    finally:
        conn.close()

def restore_tampered_records(patient_id: int, original_data: dict) -> dict:
    """Restores the authentic data for the latest block to clear demo tampering."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, version, timestamp, previous_hash 
            FROM medical_records_chain 
            WHERE patient_id = ? 
            ORDER BY version DESC 
            LIMIT 1
        """, (patient_id,))
        block = cursor.fetchone()
        if not block:
            return {"success": False, "message": "No block found to restore."}
            
        correct_hash = calculate_hash(block['version'], block['timestamp'], original_data, block['previous_hash'])
        payload_json = canonical_json(original_data)
        
        cursor.execute("""
            UPDATE medical_records_chain 
            SET patient_data_json = ?, current_hash = ? 
            WHERE id = ?
        """, (payload_json, correct_hash, block['id']))
        conn.commit()
        return {"success": True, "message": f"Block Version {block['version']} restored with correct hash."}
    finally:
        conn.close()
