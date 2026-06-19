'use strict';

// disaster.js — flood / earthquake / collapse scenarios + reroute.
// Adds its own MapLibre overlays (affected nodes, route line) above app.js layers.
// Relies on globals from app.js: map, currentCity, graphData, disabledNodes.

function ensureOverlays() {
  if (!map.getSource('scenario-affected')) {
    map.addSource('scenario-affected', { type: 'geojson', data: emptyFC() });
    map.addLayer({
      id: 'scenario-affected-layer', type: 'circle', source: 'scenario-affected',
      paint: { 'circle-radius': 6, 'circle-color': '#1d4ed8', 'circle-stroke-width': 1.5, 'circle-stroke-color': '#93c5fd', 'circle-opacity': 0.95 },
    });
  }
  if (!map.getSource('route')) {
    map.addSource('route', { type: 'geojson', data: emptyFC() });
    map.addLayer({
      id: 'route-layer', type: 'line', source: 'route',
      paint: { 'line-color': '#f59e0b', 'line-width': 4, 'line-opacity': 0.9 },
    });
  }
}

function emptyFC() { return { type: 'FeatureCollection', features: [] }; }

function nodeCoord(id) {
  if (!graphData) return null;
  const f = graphData.features.find(x => x.geometry.type === 'Point' && x.properties.id === id);
  return f ? f.geometry.coordinates : null;
}

function paintAffected(ids) {
  ensureOverlays();
  const feats = ids.map(nodeCoord).filter(Boolean)
    .map(c => ({ type: 'Feature', geometry: { type: 'Point', coordinates: c }, properties: {} }));
  map.getSource('scenario-affected').setData({ type: 'FeatureCollection', features: feats });
}

function clearOverlays() {
  if (map.getSource('scenario-affected')) map.getSource('scenario-affected').setData(emptyFC());
  if (map.getSource('route')) map.getSource('route').setData(emptyFC());
}

function toast(msg, kind) {
  const t = document.getElementById('scenario-toast');
  if (!t) return;
  t.textContent = msg;
  t.className = 'toast show' + (kind ? ' ' + kind : '');
  clearTimeout(toast._t);
  toast._t = setTimeout(() => { t.className = 'toast'; }, 5000);
}

async function runScenario(type, params) {
  if (!currentCity) return;
  try {
    const res = await fetch(`/cities/${currentCity.id}/scenario`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type, params }),
    });
    const r = await res.json();
    if (r.error) { toast('Scenario error: ' + r.error, 'bad'); return; }
    paintAffected(r.disabled_ids || []);
    const ri = (r.resilience_index * 100).toFixed(0);
    let msg = `${type.toUpperCase()}: ${r.nodes_disabled} nodes down · resilience ${ri}% · LCC ${(r.lcc_fraction * 100).toFixed(0)}% · ${r.components} fragments`;
    if (type === 'flood') msg += ` · ${r.flood_critical_nodes} flood-critical`;
    toast(msg, r.resilience_index < 0.6 ? 'bad' : 'ok');
  } catch (e) { toast('Scenario request failed — is the pipeline run?', 'bad'); }
}

function topGatekeeperIds(n) {
  if (!graphData) return [];
  return graphData.features.filter(f => f.geometry.type === 'Point')
    .sort((a, b) => b.properties.betweenness - a.properties.betweenness)
    .slice(0, n).map(f => f.properties.id);
}

async function computeRoute() {
  if (!currentCity) return;
  const src = parseInt(document.getElementById('sel-from').value, 10);
  const dst = parseInt(document.getElementById('sel-to').value, 10);
  if (isNaN(src) || isNaN(dst)) return;
  try {
    const res = await fetch(`/cities/${currentCity.id}/reroute`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ src, dst, disabled_nodes: disabledNodes }),
    });
    const r = await res.json();
    ensureOverlays();
    if (!r.reachable || !r.path || r.path.length === 0) {
      map.getSource('route').setData(emptyFC());
      toast('Route severed — no path with current disabled nodes', 'bad');
      return;
    }
    const coords = r.path.map(nodeCoord).filter(Boolean);
    map.getSource('route').setData({
      type: 'FeatureCollection',
      features: [{ type: 'Feature', geometry: { type: 'LineString', coordinates: coords }, properties: {} }],
    });
    toast(`Route: ${r.path.length} hops · ${(r.length_m / 1000).toFixed(2)} km`, 'ok');
  } catch (e) { toast('Reroute failed', 'bad'); }
}

function wireDisasterControls() {
  const on = (id, fn) => { const el = document.getElementById(id); if (el) el.addEventListener('click', fn); };

  on('sc-flood', () => {
    const thr = parseFloat(document.getElementById('sc-flood-thr').value) || 900;
    runScenario('flood', { elevation_threshold_m: thr });
  });
  on('sc-quake', () => {
    const c = map.getCenter();
    runScenario('earthquake', { lat: c.lat, lon: c.lng, radius_m: 1500 });
  });
  on('sc-collapse', () => runScenario('collapse', { node_ids: topGatekeeperIds(3) }));
  on('sc-reset', () => { disabledNodes.length = 0; clearOverlays(); toast('Network restored', 'ok'); });
  on('btn-route', computeRoute);
}

window.addEventListener('DOMContentLoaded', wireDisasterControls);
