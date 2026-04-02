/* ═══════════════════════════════════════════════════════════
   AMRAVATI DELIVERY — Global JS Utilities
   ═══════════════════════════════════════════════════════════ */

// ── Dark mode ────────────────────────────────────────────────
(function initTheme() {
  const saved = localStorage.getItem('theme') || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
  const icon = document.getElementById('themeIcon');
  if (icon) icon.textContent = saved === 'dark' ? '🌙' : '☀️';
})();

function toggleTheme() {
  const html  = document.documentElement;
  const curr  = html.getAttribute('data-theme') || 'dark';
  const next  = curr === 'dark' ? 'light' : 'dark';
  html.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
  const icon = document.getElementById('themeIcon');
  if (icon) icon.textContent = next === 'dark' ? '🌙' : '☀️';
}

// ── Global Loader ─────────────────────────────────────────────
function showLoader(msg = 'Processing…') {
  const el = document.getElementById('globalLoader');
  const txt = document.getElementById('loaderText');
  if (el)  el.classList.add('active');
  if (txt) txt.textContent = msg;
}
function hideLoader() {
  const el = document.getElementById('globalLoader');
  if (el) el.classList.remove('active');
}

// ── Toast notifications ───────────────────────────────────────
function showToast(message, type = 'info', duration = 3500) {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `<span class="toast-icon">${icons[type] || 'ℹ️'}</span>
                     <span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = '.3s';
    setTimeout(() => toast.remove(), 350);
  }, duration);
}

// ── Fetch helper ──────────────────────────────────────────────
async function apiFetch(url, options = {}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// ── Format helpers ────────────────────────────────────────────
function fmtKm(km)  { return parseFloat(km).toFixed(2) + ' km'; }
function fmtMin(m)  {
  m = parseFloat(m);
  if (m < 60) return Math.round(m) + ' min';
  return Math.floor(m/60) + 'h ' + Math.round(m%60) + 'm';
}
function fmtRs(r)   { return '₹' + parseFloat(r).toFixed(0); }
function fmtNodes(n){ return parseInt(n).toLocaleString(); }

// ── Animate number counter ────────────────────────────────────
function animateCounter(el, from, to, unit = '', duration = 900) {
  if (!el) return;
  const start = performance.now();
  function step(ts) {
    const p = Math.min((ts - start) / duration, 1);
    const ease = 1 - Math.pow(1 - p, 3); // ease-out cubic
    el.textContent = parseFloat((from + (to - from) * ease).toFixed(2)) + unit;
    if (p < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

// ── Leaflet map helper: animated polyline ─────────────────────
function animatePolyline(map, coords, color, weight = 5, onDone) {
  if (!coords || !coords.length) return null;
  const poly = L.polyline([], { color, weight, opacity: .9, lineJoin: 'round' }).addTo(map);
  let i = 0;
  const step = () => {
    if (i >= coords.length) { if (onDone) onDone(poly); return; }
    poly.addLatLng(coords[i++]);
    requestAnimationFrame(step);
  };
  step();
  return poly;
}

// ── Deep-merge objects ────────────────────────────────────────
function merge(target, source) {
  for (const k of Object.keys(source)) {
    if (source[k] && typeof source[k] === 'object' && !Array.isArray(source[k])) {
      target[k] = merge(target[k] || {}, source[k]);
    } else {
      target[k] = source[k];
    }
  }
  return target;
}

// ── Chart.js global defaults ──────────────────────────────────
if (typeof Chart !== 'undefined') {
  Chart.defaults.color = '#b0bec5';
  Chart.defaults.borderColor = 'rgba(0,229,255,.1)';
  Chart.defaults.font.family = 'DM Sans, sans-serif';
  Chart.defaults.plugins.legend.labels.usePointStyle = true;
  Chart.defaults.plugins.legend.labels.pointStyleWidth = 10;
}
