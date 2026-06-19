'use strict';

const API = '';

let map, currentCity = null, graphData = null, disabledNodes = [];

const ZONE_COLORS = ['match', ['get', 'zone'],
  'critical', '#ef4444',
  'vulnerable', '#f97316',
  'resilient', '#22c55e',
  '#94a3b8'
];

const DARK_STYLE = {
  version: 8,
  sources: {
    osm: {
      type: 'raster',
      tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
      tileSize: 256,
      attribution: '© OpenStreetMap'
    }
  },
  layers: [
    { id: 'bg', type: 'background', paint: { 'background-color': '#0a0c10' } },
    {
      id: 'osm',
      type: 'raster',
      source: 'osm',
      paint: {
        'raster-brightness-max': 0.12,
        'raster-saturation': -1,
        'raster-contrast': 0.1
      }
    }
  ]
};

function initMap(center, zoom) {
  map = new maplibregl.Map({
    container: 'map',
    style: DARK_STYLE,
    center: [center[1], center[0]],
    zoom: zoom || 13,
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

  map.addLayer({
    id: 'edges-layer',
    type: 'line',
    source: 'edges',
    filter: ['==', '$type', 'LineString'],
    paint: {
      'line-color': ['case', ['boolean', ['get', 'synthetic'], false], '#a78bfa', '#475569'],
      'line-width': ['case', ['boolean', ['get', 'synthetic'], false], 1.5, 1],
      'line-opacity': 0.7,
    }
  });

  map.addLayer({
    id: 'nodes-layer',
    type: 'circle',
    source: 'nodes',
    filter: ['==', '$type', 'Point'],
    paint: {
      'circle-radius': [
        'case',
        ['==', ['get', 'zone'], 'critical'], 7,
        ['==', ['get', 'zone'], 'vulnerable'], 5,
        3
      ],
      'circle-color': ZONE_COLORS,
      'circle-opacity': 0.9,
      'circle-stroke-width': ['case', ['boolean', ['get', 'flood_critical'], false], 2, 0],
      'circle-stroke-color': '#3b82f6',
    }
  });
}

async function loadCityGraph(city_id) {
  try {
    const res = await fetch(`${API}/cities/${city_id}/graph`);
    if (!res.ok) return;
    graphData = await res.json();
    const nodes = {
      type: 'FeatureCollection',
      features: graphData.features.filter(f => f.geometry.type === 'Point')
    };
    const edges = {
      type: 'FeatureCollection',
      features: graphData.features.filter(f => f.geometry.type === 'LineString')
    };
    map.getSource('nodes').setData(nodes);
    map.getSource('edges').setData(edges);
    if (typeof updatePanels === 'function') updatePanels();
  } catch (e) {
    console.warn('graph load failed', e);
  }
}

async function onNodeClick(e) {
  const feat = e.features[0];
  const nodeId = feat.properties.id;
  const zone = feat.properties.zone;

  try {
    const res = await fetch(`${API}/cities/${currentCity.id}/disable`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ node_id: nodeId }),
    });
    const data = await res.json();
    disabledNodes.push(nodeId);

    const statusText = document.getElementById('status-text');
    if (statusText) {
      statusText.textContent =
        `Node ${nodeId} (${zone}) disabled — LCC: ${(data.lcc_fraction * 100).toFixed(1)}% — Components: ${data.components_after}`;
    }
  } catch (e) {
    console.warn('disable node failed', e);
  }
}

function ensureMaskLayer() {
  if (!currentCity || map.getSource('road-mask')) return;
  // bbox = [south, west, north, east]; image corners are TL, TR, BR, BL.
  const [s, w, n, e] = currentCity.bbox;
  map.addSource('road-mask', {
    type: 'image',
    url: `${API}/cities/${currentCity.id}/mask`,
    coordinates: [[w, n], [e, n], [e, s], [w, s]],
  });
  map.addLayer({ id: 'road-mask-layer', type: 'raster', source: 'road-mask', paint: { 'raster-opacity': 0.85 } });
}

function setLayerMode(mode) {
  document.querySelectorAll('.layer-btn').forEach(b => b.classList.remove('active'));
  const active = document.querySelector(`.layer-btn[data-mode="${mode}"]`);
  if (active) active.classList.add('active');
  if (!map) return;

  const show = (id, v) => { if (map.getLayer(id)) map.setLayoutProperty(id, 'visibility', v); };
  if (mode === 'mask') ensureMaskLayer();

  // satellite: raw basemap only; mask: mask raster only; graph: nodes+edges over basemap.
  show('nodes-layer', mode === 'graph' ? 'visible' : 'none');
  show('edges-layer', mode === 'graph' ? 'visible' : 'none');
  show('road-mask-layer', mode === 'mask' ? 'visible' : 'none');
}

function connectSSE(city_id, mock) {
  const bar = document.getElementById('progress-fill');
  const label = document.getElementById('progress-label');
  const barWrap = document.querySelector('.progress-bar');
  const runBtn = document.getElementById('run-btn');

  if (barWrap) barWrap.style.display = 'block';
  if (runBtn) runBtn.disabled = true;

  const url = `${API}/cities/${city_id}/run?mock=${mock}`;

  fetch(url, { method: 'POST' }).then(res => {
    const reader = res.body.getReader();
    const decoder = new TextDecoder();

    function read() {
      reader.read().then(({ done, value }) => {
        if (done) {
          if (runBtn) runBtn.disabled = false;
          if (barWrap) barWrap.style.display = 'none';
          loadCityGraph(city_id);
          updateStatusDot('ready');
          return;
        }
        const text = decoder.decode(value);
        const lines = text.split('\n').filter(l => l.startsWith('data:'));
        for (const line of lines) {
          try {
            const ev = JSON.parse(line.slice(5));
            if (bar) bar.style.width = ev.pct + '%';
            if (label) label.textContent = ev.step.replace(/_/g, ' ');
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
    console.warn('SSE connect failed', err);
    if (runBtn) runBtn.disabled = false;
    if (barWrap) barWrap.style.display = 'none';
  });
}

function updateStatusDot(status) {
  const dot = document.getElementById('status-dot');
  if (!dot) return;
  dot.className = 'status-dot ' + status;
}

async function init() {
  let cities = [];

  try {
    const res = await fetch(`${API}/cities`);
    cities = await res.json();
  } catch (e) {
    console.warn('Could not reach /cities — API offline or no cities.json', e);
    const statusText = document.getElementById('status-text');
    if (statusText) statusText.textContent = 'API offline — start uvicorn to load city data';
    cities = [];
  }

  const sel = document.getElementById('city-select');
  if (cities.length === 0) {
    const opt = document.createElement('option');
    opt.textContent = 'No cities configured';
    sel.appendChild(opt);
    initMap([12.9716, 77.5946], 12);
    return;
  }

  cities.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c.id;
    opt.textContent = `${c.name} [${c.status}]`;
    sel.appendChild(opt);
  });

  currentCity = cities[0];
  updateStatusDot(currentCity.status);
  initMap(currentCity.center, currentCity.zoom);

  sel.addEventListener('change', async () => {
    const cid = sel.value;
    currentCity = cities.find(c => c.id === cid);
    disabledNodes = [];
    updateStatusDot(currentCity.status);
    map.flyTo({
      center: [currentCity.center[1], currentCity.center[0]],
      zoom: currentCity.zoom
    });
    loadCityGraph(cid);

    try {
      const metrics_res = await fetch(`${API}/cities/${cid}/metrics`);
      if (metrics_res.ok) {
        const m = await metrics_res.json();
        if (typeof updateMetrics === 'function') updateMetrics(m);
      }
    } catch (_) {}
  });

  document.getElementById('run-btn').addEventListener('click', () => {
    const liveToggle = document.getElementById('live-toggle');
    const mock = liveToggle ? !liveToggle.checked : true;
    if (!currentCity) return;
    updateStatusDot('running');
    connectSSE(currentCity.id, mock);
  });

  document.querySelectorAll('.layer-btn').forEach(btn => {
    btn.addEventListener('click', () => setLayerMode(btn.dataset.mode));
  });

  if (cities[0].status === 'ready') {
    try {
      const metrics_res = await fetch(`${API}/cities/${cities[0].id}/metrics`);
      if (metrics_res.ok) {
        const m = await metrics_res.json();
        if (typeof updateMetrics === 'function') updateMetrics(m);
      }
    } catch (_) {}
  }
}

function getCurrentCity() { return currentCity; }
function getGraphData() { return graphData; }

window.addEventListener('DOMContentLoaded', init);
