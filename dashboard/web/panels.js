'use strict';

// panels.js — metric cards, ablation chart, gatekeeper list, zone legend.
// Relies on globals from app.js: graphData, currentCity, map, disabledNodes.

let ablationChart = null;

const $ = (id) => document.getElementById(id);

function fmtPct(x) { return (x == null) ? '—' : (x * 100).toFixed(1) + '%'; }
function fmtNum(x) { return (x == null) ? '—' : x.toLocaleString(); }

// Called by app.js when a summary.json (metrics) is available.
function updateMetrics(s) {
  if (!s) return;
  $('m-apls').textContent = (s.apls != null) ? s.apls.toFixed(3) : '—';
  $('m-connectivity').textContent = fmtPct(s.connectivity_ratio);
  $('m-resilience').textContent = (s.resilience_index_3 != null) ? s.resilience_index_3.toFixed(2) : '—';
  $('m-gatekeepers').textContent = fmtNum(s.gatekeeper_count);
  $('m-floodcrit').textContent = fmtNum(s.flood_critical_count);
  $('m-nodes').textContent = fmtNum(s.n_nodes);
  $('m-synthetic').textContent = fmtNum(s.synthetic_edges);
  if (Array.isArray(s.ablation)) buildAblationChart(s.ablation);
}

function buildAblationChart(ablation) {
  const canvas = $('ablation-chart');
  if (!canvas || typeof Chart === 'undefined') return;
  const labels = ablation.map(d => d.n_removed);
  const ri = ablation.map(d => d.resilience_index);
  const frac = ablation.map(d => d.lcc_fraction);

  if (ablationChart) ablationChart.destroy();
  ablationChart = new Chart(canvas, {
    type: 'line',
    data: {
      labels,
      datasets: [
        { label: 'Resilience index', data: ri, borderColor: '#22c55e', backgroundColor: 'rgba(34,197,94,.15)', tension: 0.3, fill: true, pointRadius: 2 },
        { label: 'Connected fraction', data: frac, borderColor: '#f97316', backgroundColor: 'rgba(249,115,22,.10)', tension: 0.3, fill: true, pointRadius: 2 },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { title: { display: true, text: 'nodes removed', color: '#64748b' }, ticks: { color: '#64748b' }, grid: { color: 'rgba(148,163,184,.08)' } },
        y: { min: 0, max: 1, ticks: { color: '#64748b' }, grid: { color: 'rgba(148,163,184,.08)' } },
      },
    },
  });
}

// Called by app.js after a graph (zones.geojson) loads.
function updatePanels() {
  if (!graphData) return;
  const nodes = graphData.features.filter(f => f.geometry.type === 'Point');

  // Zone legend counts
  const counts = { critical: 0, vulnerable: 0, resilient: 0, flood: 0 };
  nodes.forEach(f => {
    const z = f.properties.zone;
    if (counts[z] != null) counts[z]++;
    if (f.properties.flood_critical) counts.flood++;
  });
  $('z-critical').textContent = counts.critical;
  $('z-vulnerable').textContent = counts.vulnerable;
  $('z-resilient').textContent = counts.resilient;
  $('z-flood').textContent = counts.flood;

  // Top gatekeepers by betweenness
  const top = [...nodes].sort((a, b) => b.properties.betweenness - a.properties.betweenness).slice(0, 10);
  const maxBc = top.length ? top[0].properties.betweenness || 1 : 1;
  const list = $('gk-list');
  list.innerHTML = '';
  top.forEach((f, i) => {
    const p = f.properties;
    const row = document.createElement('div');
    row.className = 'gk-row';
    row.dataset.id = p.id;
    const w = maxBc > 0 ? (p.betweenness / maxBc * 100) : 0;
    row.innerHTML =
      `<span class="gk-rank">${i + 1}</span>` +
      `<span class="gk-id">#${p.id}</span>` +
      `<span class="gk-bar"><i style="width:${w.toFixed(0)}%;background:${zoneColor(p.zone)}"></i></span>` +
      `<span class="gk-val">${(p.betweenness || 0).toFixed(3)}</span>`;
    row.addEventListener('click', () => flyToNode(p.id));
    list.appendChild(row);
  });

  populateRerouteSelects(nodes);
}

function zoneColor(z) {
  return z === 'critical' ? '#ef4444' : z === 'vulnerable' ? '#f97316' : '#22c55e';
}

function flyToNode(id) {
  if (!graphData || !map) return;
  const f = graphData.features.find(x => x.geometry.type === 'Point' && x.properties.id === id);
  if (f) map.flyTo({ center: f.geometry.coordinates, zoom: 15 });
}

function populateRerouteSelects(nodes) {
  const from = $('sel-from'), to = $('sel-to');
  if (!from || !to) return;
  // Prefer high-betweenness endpoints so the demo route is meaningful.
  const pick = [...nodes].sort((a, b) => b.properties.betweenness - a.properties.betweenness).slice(0, 40);
  const opts = pick.map(f => `<option value="${f.properties.id}">#${f.properties.id} (${f.properties.zone})</option>`).join('');
  from.innerHTML = opts;
  to.innerHTML = opts;
  if (pick.length > 1) to.selectedIndex = pick.length - 1;
}
