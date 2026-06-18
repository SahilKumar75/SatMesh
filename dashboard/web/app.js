/* ============================================================
   SatMesh — client-side resilience engine + map controller
   Depends on: window.SATMESH_DATA (data.js), Leaflet, Chart.js
   Works fully offline (file://). All computation is in-browser.
   ============================================================ */
(function () {
  "use strict";

  const D = window.SATMESH_DATA;
  if (!D) { console.error("SATMESH_DATA missing — load data.js first."); return; }

  // ---------- palette ----------
  const C = {
    green: "#22c55e", amber: "#f59e0b", red: "#f43f5e",
    slate: "#475569", accent: "#38bdf8", disabled: "#0a0f1a",
  };

  // ---------- derived structures ----------
  const nodeById = new Map(D.nodes.map(n => [n.id, n]));
  const BC_MAX = D.nodes.reduce((m, n) => Math.max(m, n.bc), 0) || 1;
  const LCC_BASELINE = D.meta.lcc_baseline;
  const gkSet = new Set(D.gatekeepers.map(g => g.id));

  // adjacency (undirected) over edges — used for connectivity + dijkstra
  const adj = new Map();
  D.nodes.forEach(n => adj.set(n.id, []));
  D.edges.forEach(e => {
    if (!adj.has(e.s)) adj.set(e.s, []);
    if (!adj.has(e.t)) adj.set(e.t, []);
    adj.get(e.s).push({ to: e.t, w: e.len });
    adj.get(e.t).push({ to: e.s, w: e.len });
  });

  // nodes that actually participate in the graph (deg>0)
  const liveNodeIds = D.nodes.filter(n => (adj.get(n.id) || []).length > 0).map(n => n.id);

  // ---------- state ----------
  const disabled = new Set();   // disabled node ids
  let routeLayer = null;        // current reroute polyline

  // ============================================================
  // Connectivity: components over enabled subgraph
  // ============================================================
  function computeConnectivity() {
    const seen = new Set();
    let largest = 0, components = 0;
    for (const id of liveNodeIds) {
      if (disabled.has(id) || seen.has(id)) continue;
      // BFS
      let size = 0;
      const stack = [id];
      seen.add(id);
      while (stack.length) {
        const cur = stack.pop();
        size++;
        const neigh = adj.get(cur) || [];
        for (const e of neigh) {
          if (disabled.has(e.to) || seen.has(e.to)) continue;
          seen.add(e.to);
          stack.push(e.to);
        }
      }
      components++;
      if (size > largest) largest = size;
    }
    const reach = LCC_BASELINE > 0 ? (largest / LCC_BASELINE) * 100 : 0;
    return {
      lcc: largest,
      components,
      isolated: Math.max(0, LCC_BASELINE - largest),
      reach: Math.min(100, reach),
    };
  }

  // ============================================================
  // Dijkstra (excludes disabled nodes). Returns {dist, path[]}
  // ignoreDisabled=true → baseline route over full graph.
  // ============================================================
  function dijkstra(src, dst, useFullGraph) {
    if (src === dst) return { dist: 0, path: [src] };
    const dist = new Map(), prev = new Map(), done = new Set();
    dist.set(src, 0);
    // simple binary-less PQ via array scan (graph is small ~600 nodes)
    const pq = [{ id: src, d: 0 }];
    while (pq.length) {
      // pop min
      let mi = 0;
      for (let i = 1; i < pq.length; i++) if (pq[i].d < pq[mi].d) mi = i;
      const { id: u, d } = pq.splice(mi, 1)[0];
      if (done.has(u)) continue;
      done.add(u);
      if (u === dst) break;
      for (const e of (adj.get(u) || [])) {
        if (!useFullGraph && disabled.has(e.to)) continue;
        if (done.has(e.to)) continue;
        const nd = d + e.w;
        if (nd < (dist.has(e.to) ? dist.get(e.to) : Infinity)) {
          dist.set(e.to, nd);
          prev.set(e.to, u);
          pq.push({ id: e.to, d: nd });
        }
      }
    }
    if (!dist.has(dst)) return null;
    // reconstruct
    const path = [];
    let cur = dst;
    while (cur !== undefined) { path.unshift(cur); if (cur === src) break; cur = prev.get(cur); }
    if (path[0] !== src) return null;
    return { dist: dist.get(dst), path };
  }

  // ============================================================
  // Map setup
  // ============================================================
  const map = L.map("map", {
    center: D.meta.center,
    zoom: 14,
    zoomControl: true,
    preferCanvas: true,
    attributionControl: false,
  });

  L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
    maxZoom: 20, subdomains: "abcd",
  }).addTo(map);

  const edgeLayer = L.layerGroup().addTo(map);
  const nodeLayer = L.layerGroup().addTo(map);
  const nodeMarkers = new Map(); // id -> circleMarker

  // colour ramp green→amber→red by bc/bc_max
  function bcColor(bc) {
    const t = Math.max(0, Math.min(1, bc / BC_MAX));
    if (t < 0.5) return lerpHex(C.green, C.amber, t / 0.5);
    return lerpHex(C.amber, C.red, (t - 0.5) / 0.5);
  }
  function lerpHex(a, b, t) {
    const pa = hx(a), pb = hx(b);
    const r = Math.round(pa[0] + (pb[0] - pa[0]) * t);
    const g = Math.round(pa[1] + (pb[1] - pa[1]) * t);
    const bl = Math.round(pa[2] + (pb[2] - pa[2]) * t);
    return `rgb(${r},${g},${bl})`;
  }
  function hx(h) {
    const n = parseInt(h.slice(1), 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
  }
  function radiusFor(n) {
    const base = 3 + (n.bc / BC_MAX) * 6;          // 3..9 by betweenness
    return gkSet.has(n.id) ? base + 2.5 : base;
  }

  function drawEdges() {
    edgeLayer.clearLayers();
    // draw normal edges first, healed bridges on top
    const normal = [], healed = [];
    D.edges.forEach(e => (e.syn ? healed : normal).push(e));
    const line = (e, opts) => {
      const a = nodeById.get(e.s), b = nodeById.get(e.t);
      if (!a || !b) return;
      L.polyline([[a.lat, a.lon], [b.lat, b.lon]], opts).addTo(edgeLayer);
    };
    normal.forEach(e => line(e, { color: C.slate, weight: 1, opacity: 0.5 }));
    healed.forEach(e => line(e, { color: C.green, weight: 2, opacity: 0.85 }));
  }

  function drawNodes() {
    nodeLayer.clearLayers();
    nodeMarkers.clear();
    D.nodes.forEach(n => {
      if ((adj.get(n.id) || []).length === 0) return; // skip orphan points
      const m = L.circleMarker([n.lat, n.lon], styleNode(n));
      m.bindTooltip(`Node ${n.id} · betweenness ${n.bc.toFixed(4)}`, {
        className: "sm-tip", direction: "top", offset: [0, -2],
      });
      m.on("click", () => toggleNode(n.id));
      m.addTo(nodeLayer);
      nodeMarkers.set(n.id, m);
    });
  }

  function styleNode(n) {
    if (disabled.has(n.id)) {
      return {
        radius: radiusFor(n) + 2, color: C.red, weight: 2.5,
        fillColor: C.disabled, fillOpacity: 1, opacity: 1,
      };
    }
    return {
      radius: radiusFor(n), color: "#0a0f1a", weight: 0.6,
      fillColor: bcColor(n.bc), fillOpacity: 0.92, opacity: 1,
    };
  }

  function restyleNode(id) {
    const m = nodeMarkers.get(id), n = nodeById.get(id);
    if (m && n) m.setStyle(styleNode(n)).setRadius(styleNode(n).radius);
  }

  // ============================================================
  // Interactions
  // ============================================================
  function toggleNode(id) {
    if (disabled.has(id)) disabled.delete(id); else disabled.add(id);
    restyleNode(id);
    syncGkDisabled();
    refresh();
  }

  function disableTop3() {
    D.gatekeepers.slice(0, 3).forEach(g => disabled.add(g.id));
    D.gatekeepers.slice(0, 3).forEach(g => restyleNode(g.id));
    refresh();
  }

  function resetNetwork() {
    const wasDisabled = Array.from(disabled);
    disabled.clear();
    wasDisabled.forEach(restyleNode);
    clearRoute();
    document.getElementById("rr-panel").classList.remove("show");
    refresh();
  }

  function clearRoute() {
    if (routeLayer) { map.removeLayer(routeLayer); routeLayer = null; }
  }

  function computeReroute() {
    const from = parseInt(document.getElementById("sel-from").value, 10);
    const to = parseInt(document.getElementById("sel-to").value, 10);
    const panel = document.getElementById("rr-panel");
    const okBox = document.getElementById("rr-ok");
    const sev = document.getElementById("rr-sev");
    panel.classList.add("show");
    clearRoute();

    const active = dijkstra(from, to, false);
    const baseline = dijkstra(from, to, true);

    if (!active) {
      okBox.style.display = "none";
      sev.style.display = "flex";
      return;
    }
    okBox.style.display = "block";
    sev.style.display = "none";

    // draw amber path on top
    const latlngs = active.path.map(id => {
      const n = nodeById.get(id); return [n.lat, n.lon];
    });
    routeLayer = L.polyline(latlngs, {
      color: C.amber, weight: 6, opacity: 0.95, lineJoin: "round",
    }).addTo(map);

    const dist = active.dist;
    const base = baseline ? baseline.dist : null;
    document.getElementById("rr-path").textContent =
      `${from} → ${to} · ${active.path.length} hops`;
    document.getElementById("rr-dist").textContent = fmtMetres(dist);
    document.getElementById("rr-base").textContent = base != null ? fmtMetres(base) : "—";

    const deltaEl = document.getElementById("rr-delta");
    if (base != null && base > 0) {
      const pct = ((dist - base) / base) * 100;
      deltaEl.textContent = (pct >= 0 ? "+" : "") + pct.toFixed(1) + "%";
      deltaEl.classList.toggle("up", pct > 0.05);
    } else {
      deltaEl.textContent = "—";
    }
  }

  function fmtMetres(m) {
    return m >= 1000 ? (m / 1000).toFixed(2) + " km" : Math.round(m) + " m";
  }

  // ============================================================
  // Live status card refresh
  // ============================================================
  function refresh() {
    const s = computeConnectivity();

    document.getElementById("reach-pct").textContent = s.reach.toFixed(1);
    const bar = document.getElementById("reach-bar");
    bar.style.width = s.reach + "%";
    // colour gauge by health
    let g1 = C.green, g2 = "#4ade80", tag = "NOMINAL", tagColor = C.accent;
    if (s.reach < 40)      { g1 = C.red;   g2 = "#fb7185"; tag = "CRITICAL"; tagColor = C.red; }
    else if (s.reach < 75) { g1 = C.amber; g2 = "#fbbf24"; tag = "DEGRADED"; tagColor = C.amber; }
    bar.style.background = `linear-gradient(90deg, ${g1}, ${g2})`;
    const tagEl = document.getElementById("status-tag");
    tagEl.textContent = tag;
    tagEl.style.color = tagColor;
    tagEl.style.borderColor = tagColor + "55";
    tagEl.style.background = tagColor + "1a";

    setMetric("m-isolated", s.isolated, s.isolated > 0 ? (s.isolated > 120 ? "bad" : "warn") : "");
    setMetric("m-areas", s.components, s.components > 1 ? "warn" : "");
    setMetric("m-disabled", disabled.size, disabled.size > 0 ? "bad" : "");
    setMetric("m-lcc", s.lcc, "");
  }

  function setMetric(id, val, cls) {
    const el = document.getElementById(id);
    el.querySelector(".v").textContent = val.toLocaleString();
    el.classList.remove("warn", "bad");
    if (cls) el.classList.add(cls);
  }

  // ============================================================
  // Sidebar: gatekeeper list
  // ============================================================
  function buildGatekeepers() {
    const wrap = document.getElementById("gk-list");
    wrap.innerHTML = "";
    const max = D.gatekeepers.reduce((m, g) => Math.max(m, g.bc), 0) || 1;
    D.gatekeepers.forEach((g, i) => {
      const row = document.createElement("div");
      row.className = "gk-row";
      row.dataset.id = g.id;
      const pct = (g.bc / max) * 100;
      row.innerHTML =
        `<span class="rank">${String(i + 1).padStart(2, "0")}</span>` +
        `<span class="nid">Node ${g.id}</span>` +
        `<span class="gk-bar"><span class="fill" style="width:${pct}%;background:${bcColor(g.bc)}"></span></span>` +
        `<span class="val tnum">${g.bc.toFixed(3)}</span>`;
      row.addEventListener("click", () => focusNode(g.id));
      wrap.appendChild(row);
    });
  }

  function focusNode(id) {
    const n = nodeById.get(id);
    if (!n) return;
    map.flyTo([n.lat, n.lon], 16, { duration: 0.6 });
    const m = nodeMarkers.get(id);
    if (m) m.openTooltip();
    document.querySelectorAll(".gk-row").forEach(r =>
      r.classList.toggle("active", r.dataset.id == id));
  }

  // reflect disabled state in gk list styling
  function syncGkDisabled() {
    document.querySelectorAll(".gk-row").forEach(r =>
      r.classList.toggle("disabled", disabled.has(parseInt(r.dataset.id, 10))));
  }

  // ============================================================
  // Reroute dropdowns
  // ============================================================
  function buildSelects() {
    const from = document.getElementById("sel-from");
    const to = document.getElementById("sel-to");
    // populate with gatekeepers first (most interesting), then a sample of live nodes
    const ids = Array.from(new Set([
      ...D.gatekeepers.map(g => g.id),
      ...liveNodeIds,
    ]));
    ids.sort((a, b) => a - b);
    const opts = ids.map(id => `<option value="${id}">Node ${id}</option>`).join("");
    from.innerHTML = opts;
    to.innerHTML = opts;
    // sensible defaults: two far-apart gatekeepers
    from.value = D.gatekeepers[0].id;
    to.value = D.gatekeepers[Math.min(5, D.gatekeepers.length - 1)].id;
  }

  // ============================================================
  // Resilience chart (ablation)
  // ============================================================
  function buildChart() {
    const ctx = document.getElementById("ablation-chart");
    if (!ctx || !window.Chart) return;
    const labels = D.ablation.map(a => a.n_removed);
    Chart.defaults.font.family = "Inter, sans-serif";
    Chart.defaults.color = "#7e8da6";
    new Chart(ctx, {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: "Resilience index",
            data: D.ablation.map(a => a.resilience_index),
            borderColor: C.accent, backgroundColor: "rgba(56,189,248,.12)",
            fill: true, tension: 0.32, borderWidth: 2,
            pointRadius: 2, pointBackgroundColor: C.accent,
          },
          {
            label: "Connected fraction",
            data: D.ablation.map(a => a.lcc_fraction),
            borderColor: C.amber, backgroundColor: "transparent",
            fill: false, tension: 0.32, borderWidth: 2, borderDash: [4, 3],
            pointRadius: 2, pointBackgroundColor: C.amber,
          },
        ],
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: "#16223a", borderColor: "#1e2d47", borderWidth: 1,
            titleColor: "#e2e8f0", bodyColor: "#b4c0d4",
            callbacks: { title: (t) => `${t[0].label} gatekeepers removed` },
          },
        },
        scales: {
          x: {
            grid: { color: "rgba(30,45,71,.5)" },
            ticks: { maxRotation: 0, font: { size: 10 } },
            title: { display: true, text: "Nodes removed", color: "#5b6b85", font: { size: 10 } },
          },
          y: {
            min: 0, max: 1,
            grid: { color: "rgba(30,45,71,.5)" },
            ticks: { stepSize: 0.25, font: { size: 10 } },
          },
        },
      },
    });
  }

  // ============================================================
  // Ablation table
  // ============================================================
  function buildTable() {
    const body = document.getElementById("ablation-body");
    body.innerHTML = "";
    D.ablation.forEach(a => {
      const tr = document.createElement("tr");
      const ri = a.resilience_index;
      const riColor = ri > 0.85 ? C.green : ri > 0.7 ? C.amber : C.red;
      const node = a.node_id == null
        ? `<span class="node-pill none">— baseline —</span>`
        : `<span class="node-pill">Node ${a.node_id}</span>`;
      tr.innerHTML =
        `<td class="num">${String(a.n_removed).padStart(2, "0")}</td>` +
        `<td>${node}</td>` +
        `<td class="num">${a.lcc_size}</td>` +
        `<td class="num">${(a.lcc_fraction * 100).toFixed(1)}%</td>` +
        `<td class="num">${a.efficiency.toExponential(2)}</td>` +
        `<td class="num"><div class="ri-cell">` +
          `<div class="ri-bar"><div class="fill" style="width:${ri * 100}%;background:${riColor}"></div></div>` +
          `<span>${ri.toFixed(3)}</span></div></td>`;
      body.appendChild(tr);
    });
  }

  // ============================================================
  // Wire up + boot
  // ============================================================
  function boot() {
    document.getElementById("foot-meta").textContent =
      `${D.meta.n_nodes} nodes / ${D.meta.n_edges} edges / ${D.meta.synthetic_edges} healed bridges`;

    drawEdges();
    drawNodes();
    buildGatekeepers();
    buildSelects();
    buildChart();
    buildTable();
    refresh();

    document.getElementById("btn-top3").addEventListener("click", () => { disableTop3(); syncGkDisabled(); });
    document.getElementById("btn-reset").addEventListener("click", () => { resetNetwork(); syncGkDisabled(); });
    document.getElementById("btn-route").addEventListener("click", computeReroute);
    document.getElementById("rr-close").addEventListener("click", () => {
      document.getElementById("rr-panel").classList.remove("show");
      clearRoute();
    });

    // ensure map sizes correctly after layout settles
    setTimeout(() => map.invalidateSize(), 200);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
