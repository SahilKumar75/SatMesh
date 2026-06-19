/* ============================================================
   SatMesh — client-side resilience engine + map controller
   Full-screen map layout with satellite/street tile switching.
   Depends on: window.SATMESH_DATA (data.js), Leaflet, Chart.js
   ============================================================ */
(function () {
  "use strict";

  const D = window.SATMESH_DATA;

  if (!D) {
    document.body.innerHTML = [
      '<div style="display:flex;align-items:center;justify-content:center;height:100vh;',
      'background:#0a0f1a;color:#e2e8f0;font-family:Inter,system-ui,sans-serif;',
      'text-align:center;flex-direction:column;gap:16px;">',
      '<svg width="48" height="48" fill="none" stroke="#f43f5e" stroke-width="1.5" viewBox="0 0 24 24">',
      '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/>',
      '<line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
      '<h2 style="font-size:1.4rem;margin:0;font-weight:700">Data not loaded</h2>',
      '<p style="color:#7e8da6;max-width:360px;margin:0;line-height:1.6">',
      'Run <code style="background:#111a2b;padding:2px 6px;border-radius:4px;font-family:monospace">',
      'python dashboard/export_web.py</code> to generate data.js, then reload.</p>',
      '</div>',
    ].join("");
    return;
  }

  // ── Palette ──────────────────────────────────────────────────────────────────
  const C = {
    green: "#22c55e", amber: "#f59e0b", red: "#f43f5e",
    slate: "#475569", accent: "#38bdf8",
    disabledFill: "#1a0508", disabledRing: "#f43f5e",
  };

  // ── Derived structures ───────────────────────────────────────────────────────
  const nodeById = new Map(D.nodes.map(n => [n.id, n]));
  const BC_MAX = D.nodes.reduce((m, n) => Math.max(m, n.bc), 0) || 1;
  const LCC_BASELINE = D.meta.lcc_baseline;
  const gkSet = new Set(D.gatekeepers.map(g => g.id));

  const adj = new Map();
  D.nodes.forEach(n => adj.set(n.id, []));
  D.edges.forEach(e => {
    if (!adj.has(e.s)) adj.set(e.s, []);
    if (!adj.has(e.t)) adj.set(e.t, []);
    adj.get(e.s).push({ to: e.t, w: e.len });
    adj.get(e.t).push({ to: e.s, w: e.len });
  });
  const liveNodeIds = D.nodes.filter(n => (adj.get(n.id) || []).length > 0).map(n => n.id);

  // ── App state ────────────────────────────────────────────────────────────────
  const disabled = new Set();
  let routeLayer = null;
  let routeFadeTimer = null;
  let currentTileMode = "satellite";

  // ── Tile layers ──────────────────────────────────────────────────────────────
  const TILES = {
    satellite: {
      url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
      attribution: "Tiles &copy; Esri — Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP",
      maxZoom: 19,
    },
    street: {
      url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors',
      maxZoom: 19,
      subdomains: "abc",
    },
  };

  // ── Leaflet map ──────────────────────────────────────────────────────────────
  const map = L.map("map", {
    center: D.meta.center,
    zoom: 14,
    zoomControl: true,
    preferCanvas: true,
    zoomAnimation: true,
  });

  // Start on satellite
  let tileLayer = L.tileLayer(TILES.satellite.url, {
    maxZoom: TILES.satellite.maxZoom,
    attribution: TILES.satellite.attribution,
  }).addTo(map);

  map.attributionControl.setPrefix("");

  // Reposition zoom control to right-center
  map.zoomControl.setPosition("bottomright");

  const edgeLayer = L.layerGroup().addTo(map);
  const nodeLayer = L.layerGroup().addTo(map);
  const pinLayer  = L.layerGroup().addTo(map);  // gatekeeper teardrop pins
  const nodeMarkers = new Map();
  const pinMarkers  = new Map();

  // ── Tile mode switcher ───────────────────────────────────────────────────────
  function switchTileMode(mode) {
    if (mode === currentTileMode) return;
    map.removeLayer(tileLayer);
    const t = TILES[mode];
    tileLayer = L.tileLayer(t.url, {
      maxZoom: t.maxZoom,
      subdomains: t.subdomains || "",
      attribution: t.attribution,
    }).addTo(map);
    tileLayer.bringToBack();
    currentTileMode = mode;
    document.body.classList.toggle("street-mode", mode === "street");
    document.getElementById("btn-satellite").classList.toggle("active", mode === "satellite");
    document.getElementById("btn-satellite").setAttribute("aria-pressed", String(mode === "satellite"));
    document.getElementById("btn-street").classList.toggle("active", mode === "street");
    document.getElementById("btn-street").setAttribute("aria-pressed", String(mode === "street"));
  }

  // ── Colour helpers ────────────────────────────────────────────────────────────
  function bcColor(bc) {
    const t = Math.max(0, Math.min(1, bc / BC_MAX));
    if (t < 0.5) return lerpHex(C.green, C.amber, t / 0.5);
    return lerpHex(C.amber, C.red, (t - 0.5) / 0.5);
  }
  function lerpHex(a, b, t) {
    const pa = hx(a), pb = hx(b);
    return `rgb(${Math.round(pa[0]+(pb[0]-pa[0])*t)},${Math.round(pa[1]+(pb[1]-pa[1])*t)},${Math.round(pa[2]+(pb[2]-pa[2])*t)})`;
  }
  function hx(h) {
    const n = parseInt(h.slice(1), 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
  }
  function radiusFor(n) {
    return 3 + (n.bc / BC_MAX) * 5;
  }

  // ── Teardrop pin icon (for top 10 gatekeepers) ────────────────────────────────
  function makePinIcon(color, isDisabled) {
    const fill   = isDisabled ? C.disabledFill : color;
    const stroke = isDisabled ? C.disabledRing : "rgba(255,255,255,.9)";
    const dot    = isDisabled ? C.disabledRing : "white";
    const svg =
      `<svg class="sm-pin" width="22" height="32" viewBox="0 0 22 32" xmlns="http://www.w3.org/2000/svg">` +
      `<path d="M11 0C4.9 0 0 4.9 0 11c0 8.25 11 21 11 21s11-12.75 11-21C22 4.9 17.1 0 11 0z"` +
      ` fill="${fill}" stroke="${stroke}" stroke-width="1.5"/>` +
      `<circle cx="11" cy="11" r="4.5" fill="${dot}" opacity="${isDisabled ? '.5' : '1'}"/>` +
      (isDisabled ? `<line x1="7" y1="7" x2="15" y2="15" stroke="${C.disabledRing}" stroke-width="2"/>` : '') +
      `</svg>`;
    return L.divIcon({
      html: svg,
      className: "",
      iconSize: [22, 32],
      iconAnchor: [11, 32],
      tooltipAnchor: [0, -32],
    });
  }

  // ── Draw edges ───────────────────────────────────────────────────────────────
  function drawEdges() {
    edgeLayer.clearLayers();
    const normal = [], healed = [];
    D.edges.forEach(e => (e.syn ? healed : normal).push(e));
    const line = (e, opts) => {
      const a = nodeById.get(e.s), b = nodeById.get(e.t);
      if (!a || !b) return;
      L.polyline([[a.lat, a.lon], [b.lat, b.lon]], opts).addTo(edgeLayer);
    };
    normal.forEach(e => line(e, { color: C.slate, weight: 1, opacity: 0.45 }));
    healed.forEach(e => line(e, { color: C.green, weight: 2, opacity: 0.8 }));
  }

  // ── Draw nodes + gatekeeper pins ─────────────────────────────────────────────
  function drawNodes() {
    nodeLayer.clearLayers();
    pinLayer.clearLayers();
    nodeMarkers.clear();
    pinMarkers.clear();

    // Top 10 gatekeepers get teardrop pins; rest get circle markers
    const topGkIds = new Set(D.gatekeepers.slice(0, 10).map(g => g.id));

    D.nodes.forEach(n => {
      if ((adj.get(n.id) || []).length === 0) return;

      if (topGkIds.has(n.id)) {
        // Teardrop pin marker
        const icon = makePinIcon(bcColor(n.bc), disabled.has(n.id));
        const m = L.marker([n.lat, n.lon], { icon });
        m.bindTooltip(`Node ${n.id} · BC ${n.bc.toFixed(4)} · Gatekeeper`, {
          className: "sm-tip", direction: "top",
        });
        m.on("click", () => toggleNode(n.id));
        m.addTo(pinLayer);
        pinMarkers.set(n.id, m);
      } else {
        // Regular circle marker
        const m = L.circleMarker([n.lat, n.lon], styleNode(n));
        m.bindTooltip(`Node ${n.id} · BC ${n.bc.toFixed(4)}`, {
          className: "sm-tip", direction: "top", offset: [0, -2],
        });
        m.on("click", () => toggleNode(n.id));
        m.addTo(nodeLayer);
        nodeMarkers.set(n.id, m);
      }
    });
  }

  function styleNode(n) {
    if (disabled.has(n.id)) {
      return {
        radius: radiusFor(n) + 2, color: C.disabledRing, weight: 2.5,
        fillColor: C.disabledFill, fillOpacity: 0.9, opacity: 1, dashArray: "5 3",
      };
    }
    return {
      radius: radiusFor(n), color: "rgba(255,255,255,.5)", weight: 0.8,
      fillColor: bcColor(n.bc), fillOpacity: 0.9, opacity: 1, dashArray: null,
    };
  }

  function restyleNode(id) {
    const n = nodeById.get(id);
    if (!n) return;
    // Circle marker
    const m = nodeMarkers.get(id);
    if (m) m.setStyle(styleNode(n)).setRadius(styleNode(n).radius);
    // Pin marker — rebuild icon
    const pm = pinMarkers.get(id);
    if (pm) pm.setIcon(makePinIcon(bcColor(n.bc), disabled.has(id)));
  }

  // ── Connectivity BFS ─────────────────────────────────────────────────────────
  function computeConnectivity() {
    const seen = new Set();
    let largest = 0, components = 0;
    for (const id of liveNodeIds) {
      if (disabled.has(id) || seen.has(id)) continue;
      let size = 0;
      const stack = [id];
      seen.add(id);
      while (stack.length) {
        const cur = stack.pop();
        size++;
        for (const e of (adj.get(cur) || [])) {
          if (disabled.has(e.to) || seen.has(e.to)) continue;
          seen.add(e.to); stack.push(e.to);
        }
      }
      components++;
      if (size > largest) largest = size;
    }
    const reach = LCC_BASELINE > 0 ? (largest / LCC_BASELINE) * 100 : 0;
    return { lcc: largest, components, isolated: Math.max(0, LCC_BASELINE - largest), reach: Math.min(100, reach) };
  }

  // ── Dijkstra ─────────────────────────────────────────────────────────────────
  function dijkstra(src, dst, useFullGraph) {
    if (src === dst) return { dist: 0, path: [src] };
    const dist = new Map(), prev = new Map(), done = new Set();
    dist.set(src, 0);
    const pq = [{ id: src, d: 0 }];
    while (pq.length) {
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
          dist.set(e.to, nd); prev.set(e.to, u); pq.push({ id: e.to, d: nd });
        }
      }
    }
    if (!dist.has(dst)) return null;
    const path = [];
    let cur = dst;
    while (cur !== undefined) { path.unshift(cur); if (cur === src) break; cur = prev.get(cur); }
    if (path[0] !== src) return null;
    return { dist: dist.get(dst), path };
  }

  // ── Interactions ─────────────────────────────────────────────────────────────
  function toggleNode(id) {
    if (disabled.has(id)) disabled.delete(id); else disabled.add(id);
    restyleNode(id);
    syncGkDisabled();
    dismissHint();
    refresh();
  }

  function disableTop3() {
    D.gatekeepers.slice(0, 3).forEach(g => { disabled.add(g.id); restyleNode(g.id); });
    dismissHint();
    refresh();
  }

  function resetNetwork() {
    const was = Array.from(disabled);
    disabled.clear();
    was.forEach(restyleNode);
    clearRoute();
    document.getElementById("rr-panel").classList.remove("show");
    refresh();
  }

  function clearRoute() {
    if (routeFadeTimer) { clearInterval(routeFadeTimer); routeFadeTimer = null; }
    if (routeLayer) { map.removeLayer(routeLayer); routeLayer = null; }
  }

  function computeReroute() {
    const from = parseInt(document.getElementById("sel-from").value, 10);
    const to   = parseInt(document.getElementById("sel-to").value, 10);
    if (isNaN(from) || isNaN(to) || from === to) return;

    const panel = document.getElementById("rr-panel");
    const okBox = document.getElementById("rr-ok");
    const sev   = document.getElementById("rr-sev");
    panel.classList.add("show");
    clearRoute();

    const active   = dijkstra(from, to, false);
    const baseline = dijkstra(from, to, true);

    if (!active) {
      okBox.style.display = "none";
      sev.style.display = "flex";
      return;
    }
    okBox.style.display = "block";
    sev.style.display = "none";

    const latlngs = active.path.map(id => { const n = nodeById.get(id); return [n.lat, n.lon]; });
    routeLayer = L.polyline(latlngs, { color: C.amber, weight: 5, opacity: 0, lineJoin: "round" }).addTo(map);

    // Fade-in
    let op = 0;
    routeFadeTimer = setInterval(() => {
      op = Math.min(0.95, op + 0.07);
      if (routeLayer) routeLayer.setStyle({ opacity: op });
      if (op >= 0.95) { clearInterval(routeFadeTimer); routeFadeTimer = null; }
    }, 16);

    const dist = active.dist;
    const base = baseline ? baseline.dist : null;
    document.getElementById("rr-path").textContent = `${from} → ${to} · ${active.path.length} hops`;
    document.getElementById("rr-dist").textContent = fmtMetres(dist);
    document.getElementById("rr-base").textContent = base != null ? fmtMetres(base) : "—";

    const deltaEl = document.getElementById("rr-delta");
    if (base != null && base > 0) {
      const pct = ((dist - base) / base) * 100;
      deltaEl.textContent = (pct >= 0 ? "+" : "") + pct.toFixed(1) + "%";
      deltaEl.classList.toggle("up", pct > 0.05);
      deltaEl.style.color = pct > 50 ? "var(--red)" : pct > 15 ? "var(--amber)" : "var(--green)";
    } else {
      deltaEl.textContent = "—";
      deltaEl.classList.remove("up");
      deltaEl.style.color = "";
    }
  }

  function fmtMetres(m) {
    return m >= 1000 ? (m / 1000).toFixed(2) + " km" : Math.round(m) + " m";
  }

  // ── Hint toast ───────────────────────────────────────────────────────────────
  function dismissHint() {
    const t = document.getElementById("hint-toast");
    if (t && !t.classList.contains("hidden")) t.classList.add("hidden");
  }

  // ── Status refresh ───────────────────────────────────────────────────────────
  function refresh() {
    const s = computeConnectivity();
    document.getElementById("reach-pct").textContent = s.reach.toFixed(1);
    const bar = document.getElementById("reach-bar");
    bar.style.width = s.reach + "%";
    let g1 = C.green, g2 = "#4ade80", tag = "NOMINAL", tagColor = "var(--accent)";
    if (s.reach < 40)      { g1 = C.red;   g2 = "#fb7185"; tag = "CRITICAL"; tagColor = "var(--red)"; }
    else if (s.reach < 75) { g1 = C.amber; g2 = "#fbbf24"; tag = "DEGRADED"; tagColor = "var(--amber)"; }
    bar.style.background = `linear-gradient(90deg, ${g1}, ${g2})`;
    const tagEl = document.getElementById("status-tag");
    tagEl.textContent = tag;
    tagEl.style.color = tagColor.startsWith("var") ? "" : tagColor;
    tagEl.style.setProperty("--badge-color", tagColor);

    setMetric("m-isolated", s.isolated, s.isolated > 0 ? (s.isolated > 120 ? "bad" : "warn") : "");
    setMetric("m-areas",    s.components, s.components > 1 ? "warn" : "");
    setMetric("m-disabled", disabled.size, disabled.size > 0 ? "bad" : "");
    setMetric("m-lcc",      s.lcc, "");
  }

  function setMetric(id, val, cls) {
    const el = document.getElementById(id);
    el.querySelector(".v").textContent = val.toLocaleString();
    el.classList.remove("warn", "bad");
    if (cls) el.classList.add(cls);
  }

  // ── Gatekeepers ──────────────────────────────────────────────────────────────
  function buildGatekeepers() {
    const wrap = document.getElementById("gk-list");
    wrap.innerHTML = "";
    if (!D.gatekeepers || !D.gatekeepers.length) {
      wrap.innerHTML = '<p style="color:var(--muted);padding:10px;font-size:11px;margin:0">No data.</p>';
      return;
    }
    const max = D.gatekeepers.reduce((m, g) => Math.max(m, g.bc), 0) || 1;
    D.gatekeepers.forEach((g, i) => {
      const row = document.createElement("div");
      row.className = "gk-row";
      row.dataset.id = g.id;
      row.tabIndex = 0;
      row.setAttribute("role", "listitem");
      const pct = (g.bc / max) * 100;
      row.innerHTML =
        `<span class="rank">${String(i + 1).padStart(2, "0")}</span>` +
        `<span class="nid">Node ${g.id}</span>` +
        `<span class="gk-bar"><span class="fill" style="width:${pct}%;background:${bcColor(g.bc)}"></span></span>` +
        `<span class="val tnum">${g.bc.toFixed(3)}</span>`;
      row.addEventListener("click", () => focusNode(g.id));
      row.addEventListener("keydown", e => {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); focusNode(g.id); }
      });
      wrap.appendChild(row);
    });
  }

  function focusNode(id) {
    const n = nodeById.get(id);
    if (!n) return;
    map.flyTo([n.lat, n.lon], 16, { duration: 0.7 });
    const m = nodeMarkers.get(id) || pinMarkers.get(id);
    if (m) m.openTooltip();
    document.querySelectorAll(".gk-row").forEach(r =>
      r.classList.toggle("active", Number(r.dataset.id) === id));
  }

  function syncGkDisabled() {
    document.querySelectorAll(".gk-row").forEach(r =>
      r.classList.toggle("disabled", disabled.has(parseInt(r.dataset.id, 10))));
  }

  // ── Reroute dropdowns ─────────────────────────────────────────────────────────
  function buildSelects() {
    const fromEl = document.getElementById("sel-from");
    const toEl   = document.getElementById("sel-to");
    const ids = Array.from(new Set([...D.gatekeepers.map(g => g.id), ...liveNodeIds]));
    ids.sort((a, b) => a - b);
    const opts = ids.map(id => `<option value="${id}">Node ${id}</option>`).join("");
    fromEl.innerHTML = toEl.innerHTML = opts;
    fromEl.value = D.gatekeepers[0].id;
    toEl.value   = D.gatekeepers[Math.min(5, D.gatekeepers.length - 1)].id;
  }

  // ── Resilience chart ──────────────────────────────────────────────────────────
  function buildChart() {
    const ctx = document.getElementById("ablation-chart");
    if (!ctx || !window.Chart) return;
    Chart.defaults.font.family = "Inter, sans-serif";
    Chart.defaults.color = "#7e8da6";
    new Chart(ctx, {
      type: "line",
      data: {
        labels: D.ablation.map(a => a.n_removed),
        datasets: [
          {
            label: "Resilience index",
            data: D.ablation.map(a => a.resilience_index),
            borderColor: C.accent, backgroundColor: "rgba(56,189,248,.1)",
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
            callbacks: {
              title: t => `${t[0].label} gatekeepers removed`,
              label: c => `${c.dataset.label}: ${c.parsed.y.toFixed(3)}`,
            },
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
            title: { display: true, text: "Index (0–1)", color: "#5b6b85", font: { size: 10 } },
          },
        },
      },
    });
  }

  // ── Ablation table ────────────────────────────────────────────────────────────
  function buildTable() {
    const body = document.getElementById("ablation-body");
    body.innerHTML = "";
    if (!D.ablation || !D.ablation.length) {
      body.innerHTML = `<tr><td colspan="5" style="color:var(--muted);text-align:center;padding:14px;">No data.</td></tr>`;
      return;
    }
    D.ablation.forEach(a => {
      const tr = document.createElement("tr");
      const ri = a.resilience_index;
      const riColor = ri > 0.85 ? C.green : ri > 0.7 ? C.amber : C.red;
      const node = a.node_id == null
        ? `<span class="node-pill none">baseline</span>`
        : `<span class="node-pill">Node ${a.node_id}</span>`;
      tr.innerHTML =
        `<td class="num">${String(a.n_removed).padStart(2, "0")}</td>` +
        `<td>${node}</td>` +
        `<td class="num">${a.lcc_size}</td>` +
        `<td class="num">${(a.lcc_fraction * 100).toFixed(1)}%</td>` +
        `<td class="num"><div class="ri-cell">` +
          `<div class="ri-bar"><div class="fill" style="width:${ri * 100}%;background:${riColor}"></div></div>` +
          `<span>${ri.toFixed(3)}</span></div></td>`;
      body.appendChild(tr);
    });
  }

  // ── Chips navigation (scroll panel to section) ────────────────────────────────
  function wireChips() {
    document.querySelectorAll(".chip[data-panel]").forEach(chip => {
      chip.addEventListener("click", () => {
        const target = document.getElementById(chip.dataset.panel);
        if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
        document.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
        chip.classList.add("active");
      });
    });
  }

  // ── Boot ──────────────────────────────────────────────────────────────────────
  function boot() {
    // Footer
    const footLcc  = document.getElementById("foot-lcc");
    const footMeta = document.getElementById("foot-meta");
    if (footLcc)  footLcc.textContent  = D.meta.lcc_baseline;
    if (footMeta) footMeta.textContent =
      `${D.meta.n_nodes} nodes / ${D.meta.n_edges} edges / ${D.meta.synthetic_edges} healed bridges`;

    drawEdges();
    drawNodes();
    buildGatekeepers();
    buildSelects();
    buildChart();
    buildTable();
    refresh();
    wireChips();

    // Hint toast
    const hintClose = document.getElementById("hint-close");
    if (hintClose) hintClose.addEventListener("click", dismissHint);
    setTimeout(dismissHint, 7000);

    // Toolbar
    document.getElementById("btn-top3").addEventListener("click", () => { disableTop3(); syncGkDisabled(); });
    document.getElementById("btn-reset").addEventListener("click", () => { resetNetwork(); syncGkDisabled(); });
    document.getElementById("btn-route").addEventListener("click", computeReroute);

    // Reroute panel close
    document.getElementById("rr-close").addEventListener("click", () => {
      document.getElementById("rr-panel").classList.remove("show");
      clearRoute();
    });

    // Escape key
    document.addEventListener("keydown", e => {
      if (e.key === "Escape") {
        document.getElementById("rr-panel").classList.remove("show");
        clearRoute();
      }
    });

    // Tile mode buttons
    document.getElementById("btn-satellite").addEventListener("click", () => switchTileMode("satellite"));
    document.getElementById("btn-street").addEventListener("click",    () => switchTileMode("street"));

    // Map settle
    setTimeout(() => map.invalidateSize(), 200);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
