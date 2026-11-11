/**
 * LifeBand Fall Detection Simulation & Sensor Module (IoT Layer)
 * Listens for DeviceMotion accelerometer updates and provides simulated fall testing.
 */

let fallDetectionActive = true;
let fallThreshold = 25.0; // Default acceleration threshold m/s² (~2.55 g)
let countdownTimer = null;
let countdownRemaining = 10;
let audioCtx = null;

document.addEventListener("DOMContentLoaded", function () {
  initFallSensors();
  initThresholdSlider();
});

function initThresholdSlider() {
  const slider = document.getElementById("thresholdSlider");
  const valueDisplay = document.getElementById("thresholdValue");
  if (slider && valueDisplay) {
    slider.addEventListener("input", function (e) {
      fallThreshold = parseFloat(e.target.value);
      valueDisplay.textContent = fallThreshold.toFixed(1) + " m/s²";
    });
  }
}

function initFallSensors() {
  const statusBadge = document.getElementById("sensorStatusBadge");
  const axVal = document.getElementById("valAccX");
  const ayVal = document.getElementById("valAccY");
  const azVal = document.getElementById("valAccZ");
  const gForceVal = document.getElementById("valTotalG");

  if (!window.DeviceMotionEvent) {
    if (statusBadge) {
      statusBadge.textContent = "Sensor Emulation Active (Desktop / Non-IMU Device)";
      statusBadge.className = "badge badge-teal";
    }
    return;
  }

  // Handle mobile permission if required (iOS 13+)
  if (typeof DeviceMotionEvent.requestPermission === "function") {
    const permBtn = document.getElementById("btnRequestSensorPerm");
    if (permBtn) permBtn.style.display = "inline-flex";
  }

  window.addEventListener("devicemotion", function (event) {
    if (!fallDetectionActive) return;

    const acc = event.accelerationIncludingGravity || event.acceleration;
    if (!acc) return;

    const x = acc.x || 0;
    const y = acc.y || 0;
    const z = acc.z || 0;

    // Total resultant Euclidean acceleration vector magnitude
    const magnitude = Math.sqrt(x * x + y * y + z * z);

    if (axVal) axVal.textContent = x.toFixed(2);
    if (ayVal) ayVal.textContent = y.toFixed(2);
    if (azVal) azVal.textContent = z.toFixed(2);
    if (gForceVal) gForceVal.textContent = magnitude.toFixed(1);

    if (statusBadge) {
      statusBadge.textContent = "Hardware Accelerometer Online (Active)";
      statusBadge.className = "badge badge-verified";
    }

    // Impact detection condition
    if (magnitude >= fallThreshold && !countdownTimer) {
      triggerFallAlert("Hardware Sensor Impact Triggered (" + magnitude.toFixed(1) + " m/s²)");
    }
  });
}

function requestSensorAccess() {
  if (typeof DeviceMotionEvent.requestPermission === "function") {
    DeviceMotionEvent.requestPermission()
      .then(response => {
        if (response === "granted") {
          showToast("Motion sensors granted access!", "success");
          initFallSensors();
        } else {
          showToast("Sensor permission denied. Using manual simulator.", "warning");
        }
      })
      .catch(err => {
        showToast("Sensor error: " + err.message, "danger");
      });
  }
}

// Simulated Fall Impact Trigger (For Laptop/Demonstrations)
function simulateFallImpact() {
  const gForceVal = document.getElementById("valTotalG");
  const simulatedAcc = 34.8; // Peak impact shock
  if (gForceVal) gForceVal.textContent = simulatedAcc.toFixed(1);

  showToast("Simulating sudden impact deceleration...", "warning");
  setTimeout(() => {
    triggerFallAlert("Simulated Impact Event (34.8 m/s² shock)");
  }, 400);
}

// Fall Alert & Countdown Workflow
function triggerFallAlert(reason) {
  if (countdownTimer) return; // Already running

  const overlay = document.getElementById("fallCountdownOverlay");
  const countDisplay = document.getElementById("countdownNumber");
  const reasonDisplay = document.getElementById("fallReasonText");

  countdownRemaining = 10;
  if (overlay) overlay.style.display = "flex";
  if (countDisplay) countDisplay.textContent = countdownRemaining;
  if (reasonDisplay) reasonDisplay.textContent = reason;

  playEmergencyBeep(880, 0.2); // Start beep

  countdownTimer = setInterval(() => {
    countdownRemaining -= 1;
    if (countDisplay) countDisplay.textContent = countdownRemaining;

    // Beep every second
    playEmergencyBeep(700 + (10 - countdownRemaining) * 40, 0.15);

    if (countdownRemaining <= 0) {
      clearInterval(countdownTimer);
      countdownTimer = null;
      if (overlay) overlay.style.display = "none";
      
      // Auto-escalate to emergency SOS!
      executeEmergencyTrigger("FALL_DETECTION");
    }
  }, 1000);
}

function cancelFallCountdown() {
  if (countdownTimer) {
    clearInterval(countdownTimer);
    countdownTimer = null;
  }
  const overlay = document.getElementById("fallCountdownOverlay");
  if (overlay) overlay.style.display = "none";

  showToast("Fall alert cancelled. User confirmed safe.", "success");
}

// Web Audio API Emergency Alert Tone
function playEmergencyBeep(freq = 800, duration = 0.2) {
  try {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;
    if (!audioCtx) audioCtx = new AudioContext();

    if (audioCtx.state === "suspended") {
      audioCtx.resume();
    }

    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();

    osc.type = "sine";
    osc.frequency.setValueAtTime(freq, audioCtx.currentTime);

    gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + duration);

    osc.connect(gain);
    gain.connect(audioCtx.destination);

    osc.start();
    osc.stop(audioCtx.currentTime + duration);
  } catch (e) {
    // Audio context may be restricted by autoplay policy
  }
}
