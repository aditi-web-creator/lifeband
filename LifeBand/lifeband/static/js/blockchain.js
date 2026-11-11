/**
 * LifeBand Blockchain Integrity Controller
 * Demonstrates SHA-256 hash-chain verification, tamper simulation, and ledger recovery.
 */

async function runBlockchainVerification() {
  showToast("Recomputing SHA-256 digests across entire block chain...", "info");
  try {
    const res = await fetch("/api/blockchain/verify", { method: "POST" });
    const data = await res.json();
    if (data.success) {
      if (data.audit.is_valid) {
        showToast("Integrity Verified: All SHA-256 hashes match cryptographic ground truth!", "success");
      } else {
        showToast(`CRITICAL TAMPER ALERT: Verification failed at Block v${data.audit.tampered_at_version}!`, "danger");
      }
      setTimeout(() => window.location.reload(), 1000);
    }
  } catch (err) {
    showToast("Verification error: " + err.message, "danger");
  }
}

async function simulateRecordTampering() {
  if (!confirm("SIMULATE ATTACKER TAMPERING?\n\nThis will maliciously edit patient data directly in SQLite without updating the cryptographic SHA-256 hash.")) return;

  showToast("Injecting unauthorized modification into SQLite record...", "warning");
  try {
    const res = await fetch("/api/blockchain/tamper", { method: "POST" });
    const data = await res.json();
    if (data.success) {
      showToast(data.message, "danger");
      setTimeout(() => window.location.reload(), 1200);
    } else {
      showToast("Tamper simulation failed: " + data.message, "warning");
    }
  } catch (err) {
    showToast("Error: " + err.message, "danger");
  }
}

async function restoreBlockchainChain() {
  showToast("Re-synchronizing authentic state and re-hashing chain...", "info");
  try {
    const res = await fetch("/api/blockchain/restore", { method: "POST" });
    const data = await res.json();
    if (data.success) {
      showToast("Blockchain integrity restored successfully!", "success");
      setTimeout(() => window.location.reload(), 1000);
    }
  } catch (err) {
    showToast("Error: " + err.message, "danger");
  }
}

function copyHashToClipboard(hash) {
  navigator.clipboard.writeText(hash).then(() => {
    showToast("Cryptographic hash copied to clipboard!", "info");
  });
}
