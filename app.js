/* ===== CarIQ India — Frontend Logic ===== */

let capturedImageData = null;
let uploadedImageData = null;
let cameraStream = null;
let activeFeaturesTab = 'safety';
let currentFeaturesData = null;

// ─── Tab Switching ───────────────────────────────────────────────────────────
function switchTab(tab) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
  document.getElementById(`panel-${tab}`).classList.add('active');

  // Stop camera when leaving camera tab
  if (tab !== 'camera' && cameraStream) {
    stopCamera();
  }
}

// ─── Text Search ─────────────────────────────────────────────────────────────
function quickSearch(query) {
  document.getElementById('textInput').value = query;
  searchByText();
}

async function searchByText() {
  const query = document.getElementById('textInput').value.trim();
  if (!query) {
    shakeBorder('panel-text');
    return;
  }
  await analyzeWithAPI('/api/analyze/text', { query });
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('textInput').addEventListener('keydown', e => {
    if (e.key === 'Enter') searchByText();
  });
});

// ─── File Upload ─────────────────────────────────────────────────────────────
function handleDragOver(e) {
  e.preventDefault();
  document.getElementById('dropZone').style.borderColor = 'var(--accent)';
}

function handleDrop(e) {
  e.preventDefault();
  document.getElementById('dropZone').style.borderColor = '';
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith('image/')) processFile(file);
}

function handleFileSelect(e) {
  const file = e.target.files[0];
  if (file) processFile(file);
}

function processFile(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    uploadedImageData = e.target.result;
    const previewWrap = document.getElementById('previewWrap');
    const previewImg = document.getElementById('previewImg');
    previewImg.src = uploadedImageData;
    previewWrap.style.display = 'block';
    document.querySelector('.drop-icon').style.display = 'none';
    document.querySelector('.drop-title').style.display = 'none';
    document.querySelector('.drop-sub').style.display = 'none';
    document.getElementById('analyzeUploadBtn').style.display = 'flex';
  };
  reader.readAsDataURL(file);
}

function clearImage(e) {
  e.stopPropagation();
  uploadedImageData = null;
  document.getElementById('previewWrap').style.display = 'none';
  document.querySelector('.drop-icon').style.display = 'block';
  document.querySelector('.drop-title').style.display = 'block';
  document.querySelector('.drop-sub').style.display = 'block';
  document.getElementById('analyzeUploadBtn').style.display = 'none';
  document.getElementById('fileInput').value = '';
}

async function analyzeUploadedImage() {
  if (!uploadedImageData) return;
  await analyzeWithAPI('/api/analyze/image', { image: uploadedImageData });
}

// ─── Camera ──────────────────────────────────────────────────────────────────
async function startCamera() {
  try {
    cameraStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } }
    });
    const video = document.getElementById('cameraVideo');
    video.srcObject = cameraStream;
    document.getElementById('startCamBtn').style.display = 'none';
    document.getElementById('snapBtn').style.display = 'flex';
    document.getElementById('cameraWrap').style.display = 'block';
  } catch (err) {
    alert('Camera access denied or unavailable. Please use file upload instead.');
  }
}

function capturePhoto() {
  const video = document.getElementById('cameraVideo');
  const canvas = document.getElementById('cameraCanvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);
  capturedImageData = canvas.toDataURL('image/jpeg', 0.92);

  // Show captured image
  document.getElementById('capturedImg').src = capturedImageData;
  document.getElementById('cameraWrap').style.display = 'none';
  document.getElementById('cameraCaptured').style.display = 'block';
  document.getElementById('snapBtn').style.display = 'none';
  document.getElementById('analyzeCamBtn').style.display = 'flex';

  stopCamera();
}

function retakePhoto() {
  capturedImageData = null;
  document.getElementById('cameraCaptured').style.display = 'none';
  document.getElementById('analyzeCamBtn').style.display = 'none';
  document.getElementById('startCamBtn').style.display = 'flex';
  document.getElementById('cameraWrap').style.display = 'block';
  startCamera();
}

function stopCamera() {
  if (cameraStream) {
    cameraStream.getTracks().forEach(t => t.stop());
    cameraStream = null;
  }
}

async function analyzeCaptured() {
  if (!capturedImageData) return;
  await analyzeWithAPI('/api/analyze/image', { image: capturedImageData });
}

// ─── API Call ─────────────────────────────────────────────────────────────────
async function analyzeWithAPI(endpoint, payload) {
  showLoading();

  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const result = await response.json();

    if (!response.ok || !result.success) {
      throw new Error(result.error || 'Analysis failed');
    }

    hideLoading();
    renderResults(result.data);
  } catch (err) {
    hideLoading();
    showError(err.message);
  }
}

// ─── Loading ─────────────────────────────────────────────────────────────────
const loadingMessages = [
  'Identifying your car...',
  'Scanning Indian market prices...',
  'Fetching variants & colors...',
  'Pulling specs & features...',
  'Preparing your CarIQ report...'
];
let loadingTimer = null;

function showLoading() {
  const overlay = document.getElementById('loadingOverlay');
  overlay.style.display = 'flex';
  let i = 0;
  document.getElementById('loadingMsg').textContent = loadingMessages[0];
  loadingTimer = setInterval(() => {
    i = (i + 1) % loadingMessages.length;
    document.getElementById('loadingMsg').textContent = loadingMessages[i];
  }, 1800);
}

function hideLoading() {
  clearInterval(loadingTimer);
  document.getElementById('loadingOverlay').style.display = 'none';
}

// ─── Error ────────────────────────────────────────────────────────────────────
function showError(msg) {
  alert('CarIQ Error: ' + msg);
}

// ─── Render Results ──────────────────────────────────────────────────────────
function renderResults(data) {
  // Hide hero, show results
  document.getElementById('hero').style.display = 'none';
  document.getElementById('resultsSection').style.display = 'block';
  window.scrollTo({ top: 0, behavior: 'smooth' });

  renderHeroBanner(data);
  renderPricing(data);
  renderSpecs(data);
  renderColors(data);
  renderFeatures(data);
  renderInterior(data);
  renderProscons(data);
  renderCompetitors(data);
  renderVerdict(data);
}

function renderHeroBanner(data) {
  // Badge: brand + body type
  document.getElementById('carBadge').textContent = (data.brand || '') + ' · ' + (data.body_type || '');
  document.getElementById('carHeroName').textContent = data.car_name || data.model || 'Unknown Car';
  document.getElementById('carHeroTagline').textContent = data.tagline || '';
  document.getElementById('metaBodyType').textContent = data.body_type || '';
  document.getElementById('metaYearRange').textContent = data.year_range || '';
  const priceFrom = data.pricing?.base_variant || '';
  const priceTo = data.pricing?.top_variant || '';
  document.getElementById('metaPriceRange').textContent = priceFrom && priceTo ? `${priceFrom} – ${priceTo}` : priceFrom || '';

  // Initials for placeholder
  const name = data.car_name || data.model || '?';
  const initials = name.split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase();
  document.getElementById('carInitials').textContent = initials;
}

function renderPricing(data) {
  const p = data.pricing || {};
  const rangeDiv = document.getElementById('pricingRange');
  if (p.base_variant || p.top_variant) {
    rangeDiv.innerHTML = `
      <div class="price-from-to">${p.base_variant || ''}${p.base_variant && p.top_variant ? ' – ' + p.top_variant : p.top_variant || ''}</div>
      <div class="price-label">Starting Price · Ex-showroom Delhi</div>
    `;
  }

  const variants = p.variants || [];
  const list = document.getElementById('variantsList');
  list.innerHTML = variants.map(v => `
    <div class="variant-row">
      <span class="variant-name">${escHtml(v.name || '')}</span>
      <span class="variant-fuel fuel-${(v.fuel || '').toLowerCase()}">${escHtml(v.fuel || '')}</span>
      <span class="variant-price">${escHtml(v.price || '')}</span>
    </div>
  `).join('');
}

function renderSpecs(data) {
  const s = data.specifications || {};
  const specsMap = [
    { label: 'Engine', key: 'engine' },
    { label: 'Power', key: 'power' },
    { label: 'Torque', key: 'torque' },
    { label: 'Transmission', key: 'transmission' },
    { label: 'Mileage (ARAI)', key: 'mileage_arai' },
    { label: '0–100 km/h', key: '0_to_100' },
    { label: 'Fuel Tank', key: 'fuel_tank' },
    { label: 'Boot Space', key: 'boot_space' }
  ];
  const grid = document.getElementById('specsGrid');
  grid.innerHTML = specsMap
    .filter(item => s[item.key])
    .map(item => `
      <div class="spec-item">
        <div class="spec-label">${item.label}</div>
        <div class="spec-value">${escHtml(s[item.key])}</div>
      </div>
    `).join('');
}

function renderColors(data) {
  const colors = data.colors || [];
  const grid = document.getElementById('colorsGrid');
  grid.innerHTML = colors.map(c => `
    <div class="color-swatch">
      <div class="swatch-circle ${c.type || ''}" style="background:${escHtml(c.hex || '#888')}" title="${escHtml(c.name || '')}"></div>
      <span class="swatch-name">${escHtml(c.name || '')}</span>
    </div>
  `).join('');
}

function renderFeatures(data) {
  currentFeaturesData = data.features || {};
  renderFeaturesTab('safety');
  const tabsDiv = document.getElementById('featuresTabs');
  const categories = ['safety', 'comfort', 'technology', 'infotainment'];
  tabsDiv.innerHTML = categories
    .filter(cat => currentFeaturesData[cat] && currentFeaturesData[cat].length)
    .map(cat => `
      <button class="feature-tab ${cat === 'safety' ? 'active' : ''}" onclick="renderFeaturesTab('${cat}', this)">
        ${cat.charAt(0).toUpperCase() + cat.slice(1)}
      </button>
    `).join('');
}

function renderFeaturesTab(category, btn) {
  if (btn) {
    document.querySelectorAll('.feature-tab').forEach(t => t.classList.remove('active'));
    btn.classList.add('active');
  }
  const features = (currentFeaturesData && currentFeaturesData[category]) || [];
  const list = document.getElementById('featuresList');
  list.innerHTML = features.map(f => `
    <div class="feature-item">
      <div class="feature-dot"></div>
      <span>${escHtml(f)}</span>
    </div>
  `).join('');
}

function renderInterior(data) {
  const interior = data.interior || {};
  const qualityClass = (interior.quality || 'average').toLowerCase();
  const container = document.getElementById('interiorInfo');

  const stats = [
    { label: 'Quality', value: `<span class="quality-badge quality-${qualityClass}">${interior.quality || 'N/A'}</span>` },
    { label: 'Seating', value: interior.seating || 'N/A' },
    { label: 'Screen Size', value: interior.screen_size || 'N/A' },
    { label: 'Upholstery', value: interior.upholstery || 'N/A' }
  ];

  container.innerHTML = stats.map(s => `
    <div class="interior-stat">
      <span class="int-label">${s.label.toUpperCase()}</span>
      <span class="int-value">${s.value}</span>
    </div>
  `).join('');

  if (interior.highlights && interior.highlights.length) {
    container.innerHTML += `<div class="interior-highlights">` +
      interior.highlights.map(h => `
        <div class="feature-item">
          <div class="feature-dot"></div>
          <span>${escHtml(h)}</span>
        </div>
      `).join('') + `</div>`;
  }
}

function renderProscons(data) {
  const pros = data.pros || [];
  const cons = data.cons || [];
  const grid = document.getElementById('prosConsGrid');
  grid.innerHTML = `
    <div class="pros-col">
      <div class="pros-head">PROS</div>
      ${pros.map(p => `<div class="pro-item"><span class="pro-icon">✓</span><span>${escHtml(p)}</span></div>`).join('')}
    </div>
    <div class="cons-col">
      <div class="cons-head">CONS</div>
      ${cons.map(c => `<div class="con-item"><span class="con-icon">✗</span><span>${escHtml(c)}</span></div>`).join('')}
    </div>
  `;
}

function renderCompetitors(data) {
  const comps = data.competitors || [];
  const list = document.getElementById('competitorsList');
  list.innerHTML = comps.map(c => `
    <div class="competitor-card">
      <div class="comp-top">
        <span class="comp-name">${escHtml(c.name || '')}</span>
        <span class="comp-price">${escHtml(c.price_range || '')}</span>
      </div>
      <div class="comp-reason">${escHtml(c.advantage || '')}</div>
    </div>
  `).join('');
}

function renderVerdict(data) {
  const container = document.getElementById('verdictContent');
  container.innerHTML = `
    ${data.best_variant_pick ? `
      <div class="verdict-pick">
        <div class="verdict-pick-label">BEST VARIANT PICK</div>
        <div class="verdict-pick-text">${escHtml(data.best_variant_pick)}</div>
      </div>
    ` : ''}
    ${data.target_buyer ? `
      <div class="target-row">
        <span class="target-label">IDEAL FOR</span>
        <span class="target-text">${escHtml(data.target_buyer)}</span>
      </div>
    ` : ''}
  `;

  const facts = data.interesting_facts || [];
  const factsList = document.getElementById('factsList');
  factsList.innerHTML = facts.map((f, i) => `
    <div class="fact-item">
      <span class="fact-num">0${i + 1}</span>
      <span>${escHtml(f)}</span>
    </div>
  `).join('');
}

// ─── Utilities ────────────────────────────────────────────────────────────────
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function shakeBorder(panelId) {
  const panel = document.getElementById(panelId);
  panel.style.animation = 'none';
  panel.offsetHeight; // reflow
  panel.style.animation = 'shakeBorder 0.4s ease';
  setTimeout(() => panel.style.animation = '', 500);
}

function resetApp() {
  document.getElementById('hero').style.display = 'block';
  document.getElementById('resultsSection').style.display = 'none';
  document.getElementById('textInput').value = '';
  clearImage({ stopPropagation: () => {} });
  capturedImageData = null;
  uploadedImageData = null;
  switchTab('text');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
