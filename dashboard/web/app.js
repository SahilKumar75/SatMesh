'use strict';

const API = '';

let map, currentCity = null, graphData = null, disabledNodes = [];
let activePopup = null;

/* ── Basemap styles ─────────────────────────────────────────── */
const DARK_STYLE = {
  version: 8,
  sources: {
    osm: {
      type: 'raster',
      tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
      tileSize: 256,
      attribution: '© OpenStreetMap contributors',
    },
  },
  layers: [
    { id: 'bg', type: 'background', paint: { 'background-color': '#08090a' } },
    {
      id: 'osm-dark', type: 'raster', source: 'osm',
      paint: {
        'raster-brightness-max': 0.10,
        'raster-saturation': -1,
        'raster-contrast': 0.18,
        'raster-opacity': 0.88,
      },
    },
  ],
};

const ZONE_COLORS = ['match', ['get', 'zone'],
  'critical',   '#c45a5a',
  'vulnerable', '#c09145',
  'resilient',  '#4d8a5c',
  '#3a3f45',
];

/* ── Clock ──────────────────────────────────────────────────── */
function startClock() {
  function tick() {
    const el = document.getElementById('tele-clock');
    if (el) el.textContent = new Date().toUTCString().slice(17, 25) + ' UTC';
  }
  tick();
  setInterval(tick, 1000);
}

/* ── Map ────────────────────────────────────────────────────── */
function initMap(center, zoom) {
  map = new maplibregl.Map({
    container: 'map',
    style: DARK_STYLE,
    center: [center[1], center[0]],
    zoom: zoom || 13,
    attributionControl: { compact: true },
  });

  map.on('load', () => {
    addGraphSources();
    if (currentCity) loadCityGraph(currentCity.id);
  });

  map.on('click', 'nodes-layer', onNodeClick);
  map.on('mouseenter', 'nodes-layer', () => { map.getCanvas().style.cursor = 'pointer'; });
  map.on('mouseleave', 'nodes-layer', () => { map.getCanvas().style.cursor = ''; });
}

function addGraphSources() {
  map.addSource('edges', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } });
  map.addSource('nodes', { type: 'geojson', data: { type: 'FeatureCollection', features: [] } });

  // Edges: natural roads slate-blue, synthetic/healed violet
  map.addLayer({
    id: 'edges-layer', type: 'line', source: 'edges',
    filter: ['==', '$type', 'LineString'],
    paint: {
      'line-color': ['case',
        ['boolean', ['get', 'synthetic'], false], '#8b5cf6',
        '#2d3f5c',
      ],
      'line-width': ['case',
        ['boolean', ['get', 'synthetic'], false], 2.5, 1.8,
      ],
      'line-opacity': 0.88,
    },
  });

  // Nodes: radius by criticality, color by zone, ring for flood-critical
  map.addLayer({
    id: 'nodes-layer', type: 'circle', source: 'nodes',
    filter: ['==', '$type', 'Point'],
    paint: {
      'circle-radius': ['case',
        ['==', ['get', 'zone'], 'critical'],   8,
        ['==', ['get', 'zone'], 'vulnerable'], 5,
        3.5,
      ],
      'circle-color': ZONE_COLORS,
      'circle-opacity': 0.93,
      'circle-stroke-width': ['case',
        ['boolean', ['get', 'flood_critical'], false], 2.5,
        ['==', ['get', 'zone'], 'critical'], 1.5,
        0,
      ],
      'circle-stroke-color': ['case',
        ['boolean', ['get', 'flood_critical'], false], '#4a6fa0',
        '#a87070',
      ],
    },
  });
}

async function loadCityGraph(city_id) {
  try {
    const res = await fetch(`${API}/cities/${city_id}/graph`);
    if (!res.ok) return;
    graphData = await res.json();
    const pts  = graphData.features.filter(f => f.geometry.type === 'Point');
    const lns  = graphData.features.filter(f => f.geometry.type === 'LineString');
    map.getSource('nodes').setData({ type: 'FeatureCollection', features: pts });
    map.getSource('edges').setData({ type: 'FeatureCollection', features: lns });
    if (typeof updatePanels === 'function') updatePanels();
  } catch (e) {
    console.warn('graph load failed', e);
  }
}

/* ── Node click popup ───────────────────────────────────────── */
function onNodeClick(e) {
  const p = e.features[0].properties;
  const coord = e.features[0].geometry.coordinates;

  if (activePopup) { activePopup.remove(); activePopup = null; }

  const zoneClass = p.zone || 'resilient';
  const zoneColor = p.zone === 'critical' ? '#c45a5a'
                  : p.zone === 'vulnerable' ? '#c09145' : '#4d8a5c';

  const floodBadge = p.flood_critical
    ? `<div class="np-stat"><span class="np-val" style="color:#4a6fa0">●</span><span class="np-lbl">Flood risk</span></div>`
    : '';

  const html = `
    <div class="node-popup">
      <div class="np-head">
        <span class="np-id">Node #${p.id}</span>
        <span class="np-zone ${zoneClass}">${(p.zone || 'UNKNOWN').toUpperCase()}</span>
      </div>
      <div class="np-stats">
        <div class="np-stat">
          <span class="np-val" style="color:${zoneColor}">${(p.betweenness || 0).toFixed(3)}</span>
          <span class="np-lbl">Betweenness</span>
        </div>
        <div class="np-stat">
          <span class="np-val">${p.degree != null ? p.degree : '—'}</span>
          <span class="np-lbl">Degree</span>
        </div>
        ${floodBadge}
      </div>
      <button class="np-action" onclick="window.disableNodeById(${p.id})">Simulate Failure</button>
    </div>`;

  activePopup = new maplibregl.Popup({ closeButton: true, maxWidth: '230px' })
    .setLngLat(coord)
    .setHTML(html)
    .addTo(map);
}

/* Accessible from popup button (inline onclick) */
window.disableNodeById = async function(nodeId) {
  if (!currentCity) return;
  try {
    const res = await fetch(`${API}/cities/${currentCity.id}/disable`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ node_id: nodeId }),
    });
    const data = await res.json();
    disabledNodes.push(nodeId);
    const st = document.getElementById('status-text');
    if (st) st.textContent =
      `Node #${nodeId} disabled · LCC: ${(data.lcc_fraction * 100).toFixed(1)}% · Fragments: ${data.components_after}`;
    if (activePopup) { activePopup.remove(); activePopup = null; }
  } catch (e) { console.warn('disable node failed', e); }
};

/* ── Road mask overlay ──────────────────────────────────────── */
function ensureMaskLayer() {
  if (!currentCity || map.getSource('road-mask')) return;
  const [s, w, n, e] = currentCity.bbox;
  map.addSource('road-mask', {
    type: 'image',
    url: `${API}/cities/${currentCity.id}/mask`,
    coordinates: [[w, n], [e, n], [e, s], [w, s]],
  });
  map.addLayer({ id: 'road-mask-layer', type: 'raster', source: 'road-mask',
    paint: { 'raster-opacity': 0.88 } });
}

/* ── Satellite overlay ──────────────────────────────────────── */
function ensureSatLayer() {
  if (map.getSource('esri-sat')) return;
  map.addSource('esri-sat', {
    type: 'raster',
    tiles: ['https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'],
    tileSize: 256,
    attribution: '© Esri, Maxar, Earthstar Geographics',
  });
  map.addLayer({ id: 'sat-layer', type: 'raster', source: 'esri-sat' }, 'osm-dark');
}

/* ── Layer mode ─────────────────────────────────────────────── */
function setLayerMode(mode) {
  document.querySelectorAll('.layer-btn').forEach(b => b.classList.remove('active'));
  const active = document.querySelector(`.layer-btn[data-mode="${mode}"]`);
  if (active) active.classList.add('active');
  if (!map) return;

  if (mode === 'mask')      ensureMaskLayer();
  if (mode === 'satellite') ensureSatLayer();

  const show = (id, v) => { if (map.getLayer(id)) map.setLayoutProperty(id, 'visibility', v ? 'visible' : 'none'); };
  show('nodes-layer',    mode === 'graph');
  show('edges-layer',    mode === 'graph');
  show('road-mask-layer', mode === 'mask');
  show('sat-layer',      mode === 'satellite');
  show('osm-dark',       mode !== 'satellite');
}

/* ── SSE pipeline stream ────────────────────────────────────── */
const PIPELINE_STEPS = ['loading_model','segmenting','skeletonizing','healing',
                        'elevation','criticality','zones','apls','eval'];

function connectSSE(city_id, mock) {
  const fill   = document.getElementById('progress-fill');
  const label  = document.getElementById('progress-label');
  const pane   = document.getElementById('pipeline-pane');
  const steps  = document.getElementById('pipeline-steps');
  const runBtn = document.getElementById('run-btn');

  if (pane)   pane.style.display = 'flex';
  if (runBtn) runBtn.disabled = true;

  const done = new Set();

  fetch(`${API}/cities/${city_id}/run?mock=${mock}`, { method: 'POST' }).then(res => {
    const reader  = res.body.getReader();
    const decoder = new TextDecoder();

    function read() {
      reader.read().then(({ done: finished, value }) => {
        if (finished) {
          if (runBtn) runBtn.disabled = false;
          setTimeout(() => { if (pane) pane.style.display = 'none'; }, 1400);
          loadCityGraph(city_id);
          updateStatusDot('ready');
          return;
        }

        const lines = decoder.decode(value).split('\n').filter(l => l.startsWith('data:'));
        for (const line of lines) {
          try {
            const ev = JSON.parse(line.slice(5));
            if (fill)  fill.style.width = ev.pct + '%';
            if (label) label.textContent = ev.step.replace(/_/g, ' ');
            if (steps && ev.step !== 'done') {
              done.add(ev.step);
              renderSteps(steps, ev.step, done);
            }
            if (ev.step === 'done' && ev.summary && typeof updateMetrics === 'function') {
              updateMetrics(ev.summary);
            }
          } catch (_) {}
        }
        read();
      });
    }
    read();
  }).catch(err => {
    console.warn('SSE failed', err);
    if (runBtn) runBtn.disabled = false;
    if (pane)   pane.style.display = 'none';
  });
}

function renderSteps(container, current, doneSet) {
  container.innerHTML = '';
  PIPELINE_STEPS.forEach(s => {
    const el = document.createElement('span');
    el.className = 'ps-step' +
      (doneSet.has(s) && s !== current ? ' done' : '') +
      (s === current ? ' running' : '');
    el.textContent = s.replace(/_/g, ' ');
    container.appendChild(el);
  });
}

/* ── Status dot + label ─────────────────────────────────────── */
function updateStatusDot(status) {
  const dot = document.getElementById('status-dot');
  const lbl = document.getElementById('status-lbl');
  if (dot) dot.className = 'status-dot ' + status;
  if (lbl) lbl.textContent = { ready: 'LIVE', running: 'RUNNING', not_run: 'OFFLINE' }[status] || 'OFFLINE';
}

/* ── Bootstrap ──────────────────────────────────────────────── */
async function init() {
  startClock();
  let cities = [];

  try {
    cities = await fetch(`${API}/cities`).then(r => r.json());
  } catch (e) {
    console.warn('Could not reach /cities', e);
    const st = document.getElementById('status-text');
    if (st) st.textContent = 'API offline — run: uvicorn api.main:app --reload';
  }

  const sel = document.getElementById('city-select');

  if (!cities.length) {
    const opt = document.createElement('option');
    opt.textContent = 'No cities configured';
    sel.appendChild(opt);
    initMap([12.9716, 77.5946], 12);
    return;
  }

  cities.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c.id;
    opt.textContent = c.name;
    sel.appendChild(opt);
  });

  currentCity = cities[0];
  updateStatusDot(currentCity.status);
  initMap(currentCity.center, currentCity.zoom);

  sel.addEventListener('change', async () => {
    currentCity = cities.find(c => c.id === sel.value);
    disabledNodes = [];
    if (activePopup) { activePopup.remove(); activePopup = null; }
    updateStatusDot(currentCity.status);
    map.flyTo({ center: [currentCity.center[1], currentCity.center[0]], zoom: currentCity.zoom });
    loadCityGraph(currentCity.id);
    try {
      const m = await fetch(`${API}/cities/${currentCity.id}/metrics`);
      if (m.ok && typeof updateMetrics === 'function') updateMetrics(await m.json());
    } catch (_) {}
  });

  document.getElementById('run-btn').addEventListener('click', () => {
    if (!currentCity) return;
    const mock = !document.getElementById('live-toggle').checked;
    updateStatusDot('running');
    connectSSE(currentCity.id, mock);
  });

  document.querySelectorAll('.layer-btn').forEach(btn =>
    btn.addEventListener('click', () => setLayerMode(btn.dataset.mode)));

  // Auto-load metrics if city already has results
  if (cities[0].status === 'ready') {
    try {
      const m = await fetch(`${API}/cities/${cities[0].id}/metrics`);
      if (m.ok && typeof updateMetrics === 'function') updateMetrics(await m.json());
    } catch (_) {}
  }
}

function getCurrentCity() { return currentCity; }
function getGraphData()   { return graphData;   }

window.addEventListener('DOMContentLoaded', init);
