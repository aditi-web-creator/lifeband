/**
 * LifeBand Geolocation & Hospital Proximity Controller
 * Manages browser coordinates, preset demo locations, and dynamic Haversine updates.
 */

document.addEventListener("DOMContentLoaded", function () {
  initLocationSelector();
});

function initLocationSelector() {
  const selectElem = document.getElementById("demoLocationSelect");
  if (selectElem) {
    selectElem.addEventListener("change", function (e) {
      const selectedVal = e.target.value;
      if (!selectedVal) return;

      const [lat, lon] = selectedVal.split(",").map(Number);
      if (!isNaN(lat) && !isNaN(lon)) {
        updateActiveLocation(lat, lon, e.target.options[e.target.selectedIndex].text);
      }
    });
  }
}

async function requestLiveBrowserLocation() {
  showToast("Requesting device GPS coordinates...", "info");

  if (!navigator.geolocation) {
    showToast("Browser does not support Geolocation API.", "warning");
    return;
  }

  navigator.geolocation.getCurrentPosition(
    position => {
      const lat = position.coords.latitude;
      const lon = position.coords.longitude;
      const accuracy = position.coords.accuracy;
      showToast(`GPS Acquired: ${lat.toFixed(4)}, ${lon.toFixed(4)} (±${Math.round(accuracy)}m)`, "success");
      updateActiveLocation(lat, lon, "Live Device GPS");
    },
    error => {
      let msg = "Could not obtain live GPS: ";
      switch (error.code) {
        case error.PERMISSION_DENIED:
          msg += "User denied location access. Using calibrated demo coordinates.";
          break;
        case error.POSITION_UNAVAILABLE:
          msg += "Location information is unavailable.";
          break;
        case error.TIMEOUT:
          msg += "Location request timed out.";
          break;
        default:
          msg += error.message;
      }
      showToast(msg, "warning");
    },
    { enableHighAccuracy: true, timeout: 6000, maximumAge: 10000 }
  );
}

function updateActiveLocation(lat, lon, label) {
  const latDisplay = document.getElementById("currentLatDisplay");
  const lonDisplay = document.getElementById("currentLonDisplay");
  const nameDisplay = document.getElementById("currentLocationName");

  if (latDisplay) latDisplay.textContent = lat.toFixed(5);
  if (lonDisplay) lonDisplay.textContent = lon.toFixed(5);
  if (nameDisplay) nameDisplay.textContent = label;

  // Refresh hospital list view if on hospitals page
  const hospitalContainer = document.getElementById("hospitalListContainer");
  if (hospitalContainer) {
    fetchNearestHospitals(lat, lon);
  }
}

async function fetchNearestHospitals(lat, lon) {
  try {
    const res = await fetch(`/api/hospitals/nearest?lat=${lat}&lon=${lon}`);
    const data = await res.json();
    if (data.success && data.hospitals) {
      renderHospitalCards(data.hospitals);
    }
  } catch (err) {
    console.error("Failed to fetch nearest facilities:", err);
  }
}

function renderHospitalCards(hospitals) {
  const container = document.getElementById("hospitalListContainer");
  if (!container) return;

  container.innerHTML = "";
  hospitals.forEach((h, index) => {
    const isNearest = index === 0;
    const item = document.createElement("div");
    item.className = `hospital-item ${isNearest ? "nearest" : ""}`;
    item.innerHTML = `
      <div style="flex:1;">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
          <h4 style="font-weight:700; color:var(--text-primary); font-size:1.05rem;">${h.name}</h4>
          ${isNearest ? '<span class="badge badge-teal">Closest Facility</span>' : ""}
        </div>
        <p style="font-size:0.85rem; color:var(--text-secondary); margin-bottom:6px;">${h.address}</p>
        <div style="display:flex; gap:16px; font-size:0.8rem; color:var(--text-muted);">
          <span><strong>ICU Beds:</strong> ${h.icu_beds_available}</span>
          <span><strong>Rating:</strong> ${h.trauma_level}</span>
          <span><strong>Emergency:</strong> ${h.emergency_availability}</span>
        </div>
      </div>
      <div style="text-align:right; margin-left:20px;">
        <div style="font-size:1.4rem; font-weight:800; color:var(--teal-primary); font-family:var(--font-mono);">${h.distance_km} km</div>
        <div style="font-size:0.8rem; color:var(--text-muted); margin-bottom:8px;">ETA ~${h.estimated_eta_mins} mins</div>
        <button class="btn btn-sm btn-outline-teal" onclick="selectHospitalForEmergency(${h.id})">Select Facility</button>
      </div>
    `;
    container.appendChild(item);
  });
}

function selectHospitalForEmergency(hospitalId) {
  if (confirm("Send emergency alert to this specific hospital?")) {
    executeEmergencyTrigger("MANUAL_SOS", null, null, hospitalId);
  }
}
