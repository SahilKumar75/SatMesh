'use strict';

// panels.js — metrics binding, ablation chart, gatekeeper list, zone legend.
// Globals from app.js: graphData, map, disabledNodes.

let ablationChart = null;
const $  = id => document.getElementById(id);
const pct = x => x == null ? '—' : (x * 100).toFixed(1) + '%';
const num = x => x == null ? '—' : x.toLocaleString();

/* ── Metrics binding ────────────────────────────────────────── */
function updateMetrics(s) {
  if (!s) return;

  // Track A — may not exist in summary until model run
  $('m-iou').textContent        = s.iou        != null ? s.iou.toFixed(3)        : '—';
  $('m-dice').textContent       = s.dice       != null ? s.dice.toFixed(3)       : '—';
  $('m-occ-recall').textContent = s.occ_recall != null ? s.occ_recall.toFixed(3) : '—';

  // Track B
  $('m-connectivity').textContent = s.connectivity_ratio  != null ? pct(s.connectivity_ratio)          : '—';
  $('m-resilience').textContent   = s.resilience_index_3  != null ? s.resilience_index_3.toFixed(3)    : '—';
  $('m-resilience5').textContent  = s.resilience_index_5  != null ? s.resilience_index_5.toFixed(3)    : '—';
  $('m-nodes').textContent        = num(s.n_nodes);
  $('m-synthetic').textContent    = num(s.synthetic_edges);
  $('m-gatekeepers').textContent  = num(s.gatekeeper_count);
  $('m-floodcrit').textContent    = num(s.flood_critical_count);

  // APLS — color-code by quality threshold
  const aplsEl = $('m-apls');
  if (aplsEl) {
    aplsEl.textContent = s.apls != null ? s.apls.toFixed(3) : '—';
    if (s.apls != null) {
      aplsEl.style.color = s.apls >= 0.70 ? '#4d8a5c'
                         : s.apls >= 0.50 ? '#c09145'
                         : '#c45a5a';
    }
  }

  if (Array.isArray(s.ablation)) buildAblationChart(s.ablation);
}

/* ── Ablation chart ─────────────────────────────────────────── */
function buildAblationChart(ablation) {
  const canvas = $('ablation-chart');
  if (!canvas || typeof Chart === 'undefined') return;

  const labels = ablation.map(d => d.n_removed);
  const ri     = ablation.map(d => d.resilience_index);
  const frac   = ablation.map(d => d.lcc_fraction);

  if (ablationChart) ablationChart.destroy();
  ablationChart = new Chart(canvas, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Resilience index', data: ri,
          borderColor: '#4d8a5c', backgroundColor: 'rgba(77,138,92,.07)',
          tension: 0.3, fill: true, pointRadius: 2, borderWidth: 1.5,
        },
        {
          label: 'Connected fraction', data: frac,
          borderColor: '#c09145', backgroundColor: 'rgba(192,145,69,.05)',
          tension: 0.3, fill: true, pointRadius: 2, borderWidth: 1.5,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: {
          title: { display: true, text: 'nodes removed', color: '#464d56', font: { size: 9 } },
          ticks: { color: '#464d56', font: { size: 9 }, maxTicksLimit: 8 },
          grid:  { color: 'rgba(34,37,39,.8)' },
        },
        y: {
          min: 0, max: 1,
          ticks: { color: '#464d56', font: { size: 9 } },
          grid:  { color: 'rgba(34,37,39,.8)' },
        },
      },
    },
  });
}

/* ── Zone legend + gatekeeper list ─────────────────────────── */
function updatePanels() {
  if (!graphData) return;
  const nodes = graphData.features.filter(f => f.geometry.type === 'Point');

  // Zone counts
  const counts = { critical: 0, vulnerable: 0, resilient: 0, flood: 0 };
  nodes.forEach(f => {
    const z = f.properties.zone;
    if (z in counts) counts[z]++;
    if (f.properties.flood_critical) counts.flood++;
  });
  $('z-critical').textContent   = counts.critical;
  $('z-vulnerable').textContent = counts.vulnerable;
  $('z-resilient').textContent  = counts.resilient;
  $('z-flood').textContent      = counts.flood;

  // Top 10 by betweenness
  const top   = [...nodes].sort((a, b) => b.properties.betweenness - a.properties.betweenness).slice(0, 10);
  const maxBc = top.length ? (top[0].properties.betweenness || 1) : 1;

  const list = $('gk-list');
  list.innerHTML = '';
  top.forEach((f, i) => {
    const p = f.properties;
    const w = maxBc > 0 ? ((p.betweenness / maxBc) * 100).toFixed(0) : 0;
    const col = zoneColor(p.zone);

    const row = document.createElement('div');
    row.className = 'gk-row';
    row.dataset.id = p.id;
    row.setAttribute('role', 'listitem');
    row.innerHTML =
      `<span class="gk-rank">${i + 1}</span>` +
      `<span class="gk-id">#${p.id}</span>` +
      `<span class="gk-bar"><i style="width:${w}%;background:${col}"></i></span>` +
      `<span class="gk-val">${(p.betweenness || 0).toFixed(3)}</span>`;
    row.addEventListener('click', () => flyToNode(p.id));
    list.appendChild(row);
  });

  populateRerouteSelects(nodes);
}

function zoneColor(z) {
  return z === 'critical' ? '#c45a5a' : z === 'vulnerable' ? '#c09145' : '#4d8a5c';
}

function flyToNode(id) {
  if (!graphData || !map) return;
  const f = graphData.features.find(x => x.geometry.type === 'Point' && x.properties.id === id);
  if (f) map.flyTo({ center: f.geometry.coordinates, zoom: 15, duration: 600 });
}

function populateRerouteSelects(nodes) {
  const from = $('sel-from'), to = $('sel-to');
  if (!from || !to) return;
  const pick = [...nodes]
    .sort((a, b) => b.properties.betweenness - a.properties.betweenness)
    .slice(0, 40);
  const opts = pick.map(f =>
    `<option value="${f.properties.id}">#${f.properties.id} (${f.properties.zone})</option>`
  ).join('');
  from.innerHTML = opts;
  to.innerHTML   = opts;
  if (pick.length > 1) to.selectedIndex = pick.length - 1;
}
