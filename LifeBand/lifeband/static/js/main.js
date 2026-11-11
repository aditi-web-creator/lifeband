/**
 * LifeBand Main JavaScript Controller
 * Handles application shell, navigation, modals, toasts, and emergency actions.
 */

document.addEventListener("DOMContentLoaded", function () {
  initMobileNav();
  initEmergencyTriggers();
});

function initMobileNav() {
  const toggleBtn = document.getElementById("mobileNavToggle");
  const sidebar = document.getElementById("appSidebar");
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener("click", function () {
      sidebar.classList.toggle("open");
    });
  }
}

// Toast notification helper
function showToast(message, type = "info") {
  const container = document.getElementById("toastContainer") || createToastContainer();
  const toast = document.createElement("div");
  toast.className = `alert-banner alert-${type}`;
  toast.style.marginBottom = "10px";
  toast.style.boxShadow = "var(--shadow-lg)";
  toast.innerHTML = `
    <span>${message}</span>
    <button onclick="this.parentElement.remove()" style="background:none; border:none; color:inherit; cursor:pointer; font-weight:bold; margin-left:12px;">&times;</button>
  `;
  container.appendChild(toast);
  setTimeout(() => {
    if (toast.parentElement) toast.remove();
  }, 5000);
}

function createToastContainer() {
  const container = document.createElement("div");
  container.id = "toastContainer";
  container.style.position = "fixed";
  container.style.top = "85px";
  container.style.right = "24px";
  container.style.zIndex = "9999";
  container.style.maxWidth = "400px";
  container.style.width = "90%";
  document.body.appendChild(container);
  return container;
}

// Emergency Trigger & Resolution Logic
function initEmergencyTriggers() {
  const quickSosBtns = document.querySelectorAll(".btn-trigger-sos");
  quickSosBtns.forEach(btn => {
    btn.addEventListener("click", function () {
      openEmergencyConfirmModal();
    });
  });
}

function openEmergencyConfirmModal() {
  const modal = document.getElementById("sosConfirmModal");
  if (modal) {
    modal.style.display = "flex";
  } else {
    // If modal not present on page, trigger directly with confirmation
    if (confirm("ACTIVATE EMERGENCY SOS?\n\nThis will simulate GPS emergency dispatch and notify nearby trauma hospitals.")) {
      executeEmergencyTrigger("MANUAL_SOS");
    }
  }
}

function closeEmergencyConfirmModal() {
  const modal = document.getElementById("sosConfirmModal");
  if (modal) modal.style.display = "none";
}

async function executeEmergencyTrigger(triggerType = "MANUAL_SOS", customLat = null, customLon = null, hospitalId = null) {
  let lat = customLat;
  let lon = customLon;
  let locName = null;

  // Attempt real browser GPS if not provided
  if (!lat || !lon) {
    try {
      const pos = await getCurrentPositionAsync();
      lat = pos.coords.latitude;
      lon = pos.coords.longitude;
      locName = "Live Mobile GPS Coordinates";
    } catch (err) {
      console.log("Using calibrated fallback demo coordinates:", err.message);
      // Backend handles fallback automatically
    }
  }

  showToast("Transmitting Emergency SOS & hospital telemetry...", "info");

  try {
    const response = await fetch("/api/emergency/trigger", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        trigger_type: triggerType,
        latitude: lat,
        longitude: lon,
        location_name: locName,
        hospital_id: hospitalId
      })
    });

    const data = await response.json();
    if (data.success) {
      showToast("Emergency SOS Activated! Ambulance dispatched (Simulated).", "danger");
      setTimeout(() => {
        window.location.href = "/emergency";
      }, 800);
    } else {
      showToast("Trigger failed: " + data.message, "danger");
    }
  } catch (err) {
    showToast("Network error initiating SOS: " + err.message, "danger");
  }
}

function getCurrentPositionAsync() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error("Geolocation not supported"));
    } else {
      navigator.geolocation.getCurrentPosition(resolve, reject, {
        timeout: 4000,
        enableHighAccuracy: true
      });
    }
  });
}

async function resolveActiveEmergency(emergencyId = null) {
  if (!confirm("Are you sure you want to resolve this emergency incident?")) return;

  try {
    const res = await fetch("/api/emergency/resolve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ emergency_id: emergencyId })
    });
    const data = await res.json();
    if (data.success) {
      showToast("Emergency marked as RESOLVED.", "success");
      setTimeout(() => window.location.reload(), 800);
    } else {
      showToast("Error: " + data.message, "danger");
    }
  } catch (e) {
    showToast("Request failed: " + e.message, "danger");
  }
}

async function cancelActiveEmergency(emergencyId = null) {
  if (!confirm("Cancel emergency alert as false alarm?")) return;

  try {
    const res = await fetch("/api/emergency/cancel", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ emergency_id: emergencyId })
    });
    const data = await res.json();
    if (data.success) {
      showToast("Emergency alert CANCELLED.", "warning");
      setTimeout(() => window.location.reload(), 800);
    } else {
      showToast("Error: " + data.message, "danger");
    }
  } catch (e) {
    showToast("Request failed: " + e.message, "danger");
  }
}

async function loadDemoProfile() {
  showToast("Loading pre-calibrated demo patient profile...", "info");
  try {
    const res = await fetch("/api/profile/load-demo", { method: "POST" });
    const data = await res.json();
    if (data.success) {
      showToast("Sample patient 'Rahul Sharma' (B+) loaded with Blockchain Genesis Block!", "success");
      setTimeout(() => window.location.reload(), 1000);
    } else {
      showToast("Failed to load demo: " + data.message, "danger");
    }
  } catch (err) {
    showToast("Error: " + err.message, "danger");
  }
}
