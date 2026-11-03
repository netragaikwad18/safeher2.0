const AppState = {
  token: localStorage.getItem('safety_token') || '',
  user: JSON.parse(localStorage.getItem('safety_user') || 'null'),
  currentLocation: { lat: 12.9716, lon: 77.5946, accuracy: 10 },
  activeAlert: null,
  socket: null,
  shakeDetectorActive: false,
  voiceRecognitionActive: false,
  offlineQueue: JSON.parse(localStorage.getItem('safety_offline_queue') || '[]')
};

function checkAuth(requireAuth = true, requireAdmin = false) {
  if (requireAuth && !AppState.token) {
    window.location.href = '/login.html';
    return false;
  }
  if (requireAdmin && (!AppState.user || AppState.user.role !== 'admin')) {
    alert('Access restricted to Safety Cell Administrators.');
    window.location.href = '/dashboard.html';
    return false;
  }
  return true;
}

async function apiFetch(endpoint, options = {}) {
  const headers = options.headers || {};
  if (AppState.token) {
    headers['Authorization'] = `Bearer ${AppState.token}`;
  }
  if (!(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  try {
    const response = await fetch(endpoint, { credentials: 'omit', ...options, headers });
    if (response.status === 401) {
      localStorage.removeItem('safety_token');
      localStorage.removeItem('safety_user');
      window.location.href = '/login.html';
      return null;
    }
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || data.message || 'Request failed');
    }
    return data;
  } catch (err) {
    console.error('API Error:', err);
    throw err;
  }
}

function renderNavUser() {
  const userElem = document.getElementById('nav-user-name');
  if (userElem && AppState.user) {
    userElem.textContent = AppState.user.full_name || 'Safe User';
  }
  const adminLinks = document.querySelectorAll('.admin-only');
  adminLinks.forEach(el => {
    el.style.display = (AppState.user && AppState.user.role === 'admin') ? 'block' : 'none';
  });
}

function setupHardwareMonitors() {
  if ('getBattery' in navigator) {
    navigator.getBattery().then(battery => {
      function updateBattery() {
        const level = Math.round(battery.level * 100);
        const elem = document.getElementById('device-battery-badge');
        if (elem) {
          elem.innerHTML = `<i class="bi bi-battery-charging"></i> ${level}%`;
          elem.className = level <= 20 ? 'badge bg-danger text-white' : 'badge bg-secondary text-white';
        }
      }
      updateBattery();
      battery.addEventListener('levelchange', updateBattery);
    });
  }

  function updateNetworkStatus() {
    const isOnline = navigator.onLine;
    const elem = document.getElementById('device-network-badge');
    if (elem) {
      if (isOnline) {
        elem.innerHTML = `<i class="bi bi-wifi"></i> Online`;
        elem.className = 'badge bg-success text-white';
        flushOfflineQueue();
      } else {
        elem.innerHTML = `<i class="bi bi-wifi-off"></i> Offline (Cached)`;
        elem.className = 'badge bg-warning text-dark';
      }
    }
  }
  window.addEventListener('online', updateNetworkStatus);
  window.addEventListener('offline', updateNetworkStatus);
  updateNetworkStatus();
}

async function flushOfflineQueue() {
  if (!navigator.onLine || AppState.offlineQueue.length === 0) return;
  const queue = [...AppState.offlineQueue];
  AppState.offlineQueue = [];
  localStorage.setItem('safety_offline_queue', JSON.stringify([]));

  for (const item of queue) {
    try {
      await apiFetch('/api/location/update', {
        method: 'POST',
        body: JSON.stringify({ ...item, is_offline_sync: true })
      });
    } catch (e) {}
  }
}

function initGeolocation() {
  if ('geolocation' in navigator) {
    navigator.geolocation.watchPosition(
      pos => {
        AppState.currentLocation = {
          lat: pos.coords.latitude,
          lon: pos.coords.longitude,
          accuracy: pos.coords.accuracy,
          speed: pos.coords.speed || 0,
          heading: pos.coords.heading || 0
        };
        if (AppState.token) {
          if (navigator.onLine) {
            apiFetch('/api/location/update', {
              method: 'POST',
              body: JSON.stringify({
                latitude: pos.coords.latitude,
                longitude: pos.coords.longitude,
                speed: pos.coords.speed || 0,
                heading: pos.coords.heading || 0
              })
            }).catch(() => {});
          } else {
            AppState.offlineQueue.push({
              latitude: pos.coords.latitude,
              longitude: pos.coords.longitude,
              speed: pos.coords.speed || 0,
              heading: pos.coords.heading || 0
            });
            localStorage.setItem('safety_offline_queue', JSON.stringify(AppState.offlineQueue));
          }
        }
      },
      err => {},
      { enableHighAccuracy: true, maximumAge: 5000, timeout: 10000 }
    );
  }
}

function initWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws/live-tracking?token=global`;
  try {
    AppState.socket = new WebSocket(wsUrl);
    AppState.socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.event === 'SOS_TRIGGERED') {
          showFloatingAlert(`🚨 EMERGENCY SOS TRIGGERED by ${data.user_name}! Check live tracking.`);
        }
      } catch (e) {}
    };
  } catch (err) {}
}

function showFloatingAlert(message) {
  const toastContainer = document.getElementById('toast-container');
  if (!toastContainer) return;
  const div = document.createElement('div');
  div.className = 'toast align-items-center text-white bg-danger border-0 show mb-2';
  div.setAttribute('role', 'alert');
  div.innerHTML = `
    <div class="d-flex">
      <div class="toast-body fw-bold">${message}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>
  `;
  toastContainer.appendChild(div);
  setTimeout(() => div.remove(), 7000);
}

function triggerFakeCall(callerName = 'Mom (Emergency Contact)', delaySeconds = 3) {
  setTimeout(() => {
    const modalElem = document.getElementById('fakeCallModal');
    if (!modalElem) return;
    document.getElementById('fake-caller-name').textContent = callerName;
    const modal = new bootstrap.Modal(modalElem);
    modal.show();

    try {
      const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(440, audioCtx.currentTime);
      osc.frequency.setValueAtTime(480, audioCtx.currentTime + 0.1);
      gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      setTimeout(() => osc.stop(), 3000);
    } catch (e) {}
  }, delaySeconds * 1000);
}

let lastX, lastY, lastZ;
let shakeCount = 0;
let lastShakeTime = 0;

function setupShakeDetection(onShakeTriggered) {
  if (typeof DeviceMotionEvent !== 'undefined' && typeof DeviceMotionEvent.requestPermission === 'function') {
    DeviceMotionEvent.requestPermission()
      .then(response => {
        if (response === 'granted') {
          window.addEventListener('devicemotion', handleMotion);
        }
      })
      .catch(console.error);
  } else if ('ondevicemotion' in window) {
    window.addEventListener('devicemotion', handleMotion);
  }

  function handleMotion(event) {
    const acc = event.accelerationIncludingGravity;
    if (!acc || acc.x === null) return;

    const curTime = Date.now();
    if ((curTime - lastShakeTime) > 100) {
      const diffTime = curTime - lastShakeTime;
      lastShakeTime = curTime;
      const speed = Math.abs(acc.x + acc.y + acc.z - (lastX || 0) - (lastY || 0) - (lastZ || 0)) / diffTime * 10000;
      if (speed > 800) {
        shakeCount++;
        if (shakeCount >= 3) {
          shakeCount = 0;
          if (onShakeTriggered) onShakeTriggered();
        }
      } else if (curTime - lastShakeTime > 2000) {
        shakeCount = 0;
      }
      lastX = acc.x;
      lastY = acc.y;
      lastZ = acc.z;
    }
  }
}

function setupVoiceDetection(onVoiceTriggered) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) return null;

  const recognition = new SpeechRecognition();
  recognition.continuous = true;
  recognition.interimResults = false;
  recognition.lang = 'en-US';

  const triggerPhrases = ['help', 'help me', 'save me', 'emergency', 'danger', 'ಕಾಪಾಡಿ', 'ಸಹಾಯ ಮಾಡಿ'];

  recognition.onresult = (event) => {
    const lastResult = event.results[event.results.length - 1][0].transcript.toLowerCase().trim();
    const matched = triggerPhrases.some(phrase => lastResult.includes(phrase));
    if (matched && onVoiceTriggered) {
      onVoiceTriggered(lastResult);
    }
  };

  return recognition;
}

document.addEventListener('DOMContentLoaded', () => {
  renderNavUser();
  setupHardwareMonitors();
  initGeolocation();
  initWebSocket();
});
