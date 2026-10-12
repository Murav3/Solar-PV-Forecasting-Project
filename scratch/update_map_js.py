# Updated Python helper to update map JavaScript and table typography in index.html cleanly
import re

target_file = r"c:\Users\harin\Downloads\R_FINAL_REVIEW\Solar-PV-Forecasting-Project\frontend\index.html"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# Replace LaTeX in table headers with clean typography
content = content.replace(
    'Cross-Site Lead-Lag Empirical Correlation Matrix ($\\tau_{ij}$)',
    'Cross-Site Lead-Lag Empirical Correlation Matrix (τ_ij)'
)
content = content.replace(
    'Lead-Lag Time Delay ($\\tau$)',
    'Lead-Lag Time Delay (τ)'
)
content = content.replace(
    'Cross-Correlation ($r$)',
    'Cross-Correlation (r)'
)
content = content.replace(
    '($\\tau_{ij}$)',
    '(τ_ij)'
)
content = content.replace(
    '($\\tau$)',
    '(τ)'
)
content = content.replace(
    '($r$)',
    '(r)'
)

start_marker = "    // ═════════════════════════════════════════════════════════════════════════\n    // 🛰️ FEATURE 1: US UTILITY-GRADE SPATIO-TEMPORAL CLOUD VELOCITY & LEAD-LAG ENGINE"
end_marker = "    // Initialize on page load"

if start_marker not in content:
    print("ERROR: start_marker not found")
    exit(1)

if end_marker not in content:
    print("ERROR: end_marker not found")
    exit(1)

start_idx = content.find(start_marker)
end_idx = content.find(end_marker)

new_js = """    // ═════════════════════════════════════════════════════════════════════════
    // 🛰️ FEATURE 1: US UTILITY-GRADE SPATIO-TEMPORAL CLOUD VELOCITY & LEAD-LAG ENGINE
    // ═════════════════════════════════════════════════════════════════════════
    const RADAR_NODES = {
      // Sentinel Arrays (West Foothills - Leading Edge Sensor Net)
      13: { rx: 0.12, ry: 0.46, name: "L13 · West Sentinel Feed 1", role: "sentinel", distance: 0.0, capMW: 5.2, alt: 310, ori: 270, tau: 0, r: 1.00 },
      14: { rx: 0.12, ry: 0.68, name: "L14 · West Sentinel Feed 2", role: "sentinel", distance: 0.25, capMW: 4.8, alt: 295, ori: 270, tau: 48, r: 0.96 },

      // Main Solar Park L1–L12 (Downwind Targets - Shoufeng Main Complex)
      1:  { rx: 0.35, ry: 0.36, name: "L1 · Shoufeng Park Array A1", role: "target", distance: 1.85, capMW: 6.0, alt: 85, ori: 180, tau: 492, r: 0.89 },
      2:  { rx: 0.44, ry: 0.36, name: "L2 · Shoufeng Park Array A2", role: "target", distance: 1.95, capMW: 6.0, alt: 85, ori: 180, tau: 518, r: 0.88 },
      3:  { rx: 0.53, ry: 0.36, name: "L3 · Shoufeng Park Array A3", role: "target", distance: 2.05, capMW: 5.5, alt: 82, ori: 180, tau: 544, r: 0.86 },
      4:  { rx: 0.62, ry: 0.36, name: "L4 · Shoufeng Park Array A4", role: "target", distance: 2.20, capMW: 5.5, alt: 82, ori: 180, tau: 585, r: 0.85 },

      5:  { rx: 0.35, ry: 0.52, name: "L5 · Shoufeng Park Array B1", role: "target", distance: 1.90, capMW: 6.2, alt: 84, ori: 180, tau: 505, r: 0.87 },
      6:  { rx: 0.44, ry: 0.52, name: "L6 · Shoufeng Park Array B2", role: "target", distance: 2.00, capMW: 6.2, alt: 84, ori: 180, tau: 532, r: 0.86 },
      7:  { rx: 0.53, ry: 0.52, name: "L7 · Shoufeng Park Array B3", role: "target", distance: 2.10, capMW: 5.8, alt: 80, ori: 180, tau: 560, r: 0.84 },
      8:  { rx: 0.62, ry: 0.52, name: "L8 · Shoufeng Park Array B4", role: "target", distance: 2.35, capMW: 5.8, alt: 80, ori: 180, tau: 625, r: 0.84 },

      9:  { rx: 0.35, ry: 0.68, name: "L9 · Shoufeng Park Array C1", role: "target", distance: 1.95, capMW: 5.0, alt: 83, ori: 180, tau: 519, r: 0.86 },
      10: { rx: 0.44, ry: 0.68, name: "L10 · Shoufeng Park Array C2", role: "target", distance: 2.05, capMW: 5.0, alt: 83, ori: 180, tau: 545, r: 0.85 },
      11: { rx: 0.53, ry: 0.68, name: "L11 · Shoufeng Park Array C3", role: "target", distance: 2.15, capMW: 5.2, alt: 79, ori: 180, tau: 572, r: 0.83 },
      12: { rx: 0.62, ry: 0.68, name: "L12 · Shoufeng Park Array C4", role: "target", distance: 2.40, capMW: 5.2, alt: 79, ori: 180, tau: 638, r: 0.82 },

      // Coastal Arrays (Far Eastern Periphery)
      15: { rx: 0.80, ry: 0.32, name: "L15 · Ji'an Coastal Array N1", role: "coastal", distance: 14.20, capMW: 8.5, alt: 18, ori: 135, tau: 3780, r: 0.71 },
      16: { rx: 0.89, ry: 0.40, name: "L16 · Ji'an Coastal Array N2", role: "coastal", distance: 14.80, capMW: 8.5, alt: 15, ori: 135, tau: 3940, r: 0.69 },

      // Regional Grid Feed Node
      17: { rx: 0.82, ry: 0.70, name: "L17 · Hualien Grid Interconnect", role: "substation", distance: 9.80, capMW: 12.0, alt: 42, ori: 180, tau: 2550, r: 0.74 }
    };

    const CLOUD_SCENARIOS = {
      moderate: {
        name: "Mountain Cumulus",
        speedKmh: 13.8,
        headingDeg: 108,
        headingText: "WNW → ESE (108°) at 13.8 km/h",
        leadTimeSec: 492,
        leadTimeStr: "08m 12s",
        corrR: "0.89",
        deltaMW: 38,
        desc: "Orographic cumulus transient drifting off the Central Mountain Range toward Shoufeng Basin."
      },
      fast: {
        name: "Cold Front Storm",
        speedKmh: 26.5,
        headingDeg: 115,
        headingText: "NW → SE (115°) at 26.5 km/h",
        leadTimeSec: 251,
        leadTimeStr: "04m 11s",
        corrR: "0.94",
        deltaMW: 62,
        desc: "Rapid convective squall line with high optical attenuation and steep ramp-down transients."
      },
      slow: {
        name: "Coastal Marine Layer",
        speedKmh: 7.5,
        headingDeg: 95,
        headingText: "W → E (95°) at 7.5 km/h",
        leadTimeSec: 889,
        leadTimeStr: "14m 49s",
        corrR: "0.81",
        deltaMW: 24,
        desc: "Broad, slow-moving marine stratus inversion layer producing gradual spatial shadowing."
      }
    };

    let currentRadarScenario = 'moderate';
    let radarSimProgress = 0; // 0 to 100
    let radarSimRunning = false;
    let radarSimTimer = null;
    let radarSweepAngle = 0;
    let radarAnimFrameId = null;
    let unmitigatedChartInst = null;
    let mitigatedChartInst = null;
    let radarCanvasListenersAttached = false;
    let radarHoveredNode = null;
    let radarMousePos = { x: 0, y: 0 };

    // Canvas roundRect cross-browser helper
    function drawRoundRect(ctx, x, y, width, height, radius) {
      if (typeof ctx.roundRect === 'function') {
        ctx.beginPath();
        ctx.roundRect(x, y, width, height, radius);
        return;
      }
      ctx.beginPath();
      ctx.moveTo(x + radius, y);
      ctx.lineTo(x + width - radius, y);
      ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
      ctx.lineTo(x + width, y + height - radius);
      ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
      ctx.lineTo(x + radius, y + height);
      ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
      ctx.lineTo(x, y + radius);
      ctx.quadraticCurveTo(x, y, x + radius, y);
      ctx.closePath();
    }

    function resizeRadarCanvas() {
      const canvas = document.getElementById('cloudRadarCanvas');
      if (!canvas || !canvas.parentElement) return;
      const rect = canvas.parentElement.getBoundingClientRect();
      const targetW = Math.max(900, Math.round(rect.width));
      if (canvas.width !== targetW || canvas.height !== 480) {
        canvas.width = targetW;
        canvas.height = 480;
      }
    }

    // ── MAIN ENTRY POINT FOR TAB 4 ──
    function renderMapView() {
      resizeRadarCanvas();
      initRadarCanvasListeners();
      initSplitImpactCharts();
      syncScenarioUI();
      drawTacticalRadarCanvas();
      
      if (!radarAnimFrameId) {
        startRadarLoop();
      }
    }

    // ── SCENARIO PRESET HANDLER ──
    function setCloudScenario(scenKey) {
      if (!CLOUD_SCENARIOS[scenKey]) return;
      currentRadarScenario = scenKey;

      ['mod', 'fast', 'slow'].forEach(k => {
        const btn = document.getElementById(`scen-${k}`);
        if (btn) btn.classList.remove('active');
      });
      const activeMap = { moderate: 'mod', fast: 'fast', slow: 'slow' };
      const btnEl = document.getElementById(`scen-${activeMap[scenKey]}`);
      if (btnEl) btnEl.classList.add('active');

      // Reset progress
      radarSimProgress = 0;
      document.getElementById('radarSimScrubber').value = 0;
      if (radarSimRunning) toggleRadarSim(); // pause

      syncScenarioUI();
      updateSplitImpactCharts();
      drawTacticalRadarCanvas();
    }

    function syncScenarioUI() {
      const scen = CLOUD_SCENARIOS[currentRadarScenario];
      const hudTimer = document.getElementById('hudLeadTimer');
      const hudOffset = document.getElementById('hudLeadOffset');
      const hudWind = document.getElementById('hudWindVectorText');
      const cd = document.getElementById('radarSimCountdown');
      const phaseBadge = document.getElementById('radarSimPhaseBadge');

      if (hudTimer) hudTimer.textContent = scen.leadTimeStr;
      if (hudOffset) hudOffset.textContent = `Lead Offset: +${scen.leadTimeSec}s | Cross-Correlation r = ${scen.corrR}`;
      if (hudWind) hudWind.textContent = scen.headingText;
      if (cd) cd.textContent = `ETA Downwind: ${scen.leadTimeStr}`;
      if (phaseBadge) {
        phaseBadge.textContent = `Phase 1: Upwind Optical Inception (T - ${scen.leadTimeStr.split(' ')[0]})`;
        phaseBadge.style.color = '#0284c7';
        phaseBadge.style.background = '#e0f2fe';
        phaseBadge.style.borderColor = '#bae6fd';
      }
    }

    // ── SIMULATION SCRUBBER & PLAYBACK CONTROLS ──
    function toggleRadarSim() {
      radarSimRunning = !radarSimRunning;
      const btn = document.getElementById('btnRadarSimPlay');
      const icon = document.getElementById('radarSimPlayIcon');
      const txt = document.getElementById('radarSimPlayText');

      if (radarSimRunning) {
        if (btn) btn.classList.add('playing');
        if (icon) icon.textContent = '⏸';
        if (txt) txt.textContent = 'Pause Simulation';
        startRadarSimTimer();
      } else {
        if (btn) btn.classList.remove('playing');
        if (icon) icon.textContent = '▶';
        if (txt) txt.textContent = 'Simulate Transient Event';
        stopRadarSimTimer();
      }
    }

    function startRadarSimTimer() {
      stopRadarSimTimer();
      radarSimTimer = setInterval(() => {
        radarSimProgress += 0.8;
        if (radarSimProgress > 100) {
          radarSimProgress = 0;
        }
        document.getElementById('radarSimScrubber').value = Math.round(radarSimProgress);
        onRadarScrubber(radarSimProgress);
      }, 50);
    }

    function stopRadarSimTimer() {
      if (radarSimTimer) {
        clearInterval(radarSimTimer);
        radarSimTimer = null;
      }
    }

    function onRadarScrubber(val) {
      radarSimProgress = parseFloat(val);
      updateRadarSimProgressUI();
      drawTacticalRadarCanvas();
      updateChartsHighlight();
    }

    function updateRadarSimProgressUI() {
      const scen = CLOUD_SCENARIOS[currentRadarScenario];
      const p = radarSimProgress;
      const cd = document.getElementById('radarSimCountdown');
      const hudTimer = document.getElementById('hudLeadTimer');
      const phaseBadge = document.getElementById('radarSimPhaseBadge');

      if (p < 20) {
        const minsLeft = scen.leadTimeStr;
        if (cd) cd.textContent = `ETA Downwind: ${minsLeft}`;
        if (hudTimer) hudTimer.textContent = minsLeft;
        if (phaseBadge) {
          phaseBadge.textContent = `Phase 1: Upwind Optical Inception (T - ${minsLeft.split(' ')[0]})`;
          phaseBadge.style.color = '#0284c7';
          phaseBadge.style.background = '#e0f2fe';
          phaseBadge.style.borderColor = '#bae6fd';
        }
      } else if (p >= 20 && p < 60) {
        const frac = (p - 20) / 40;
        const secsRem = Math.max(0, Math.round(scen.leadTimeSec * (1 - frac)));
        const mm = String(Math.floor(secsRem / 60)).padStart(2, '0');
        const ss = String(secsRem % 60).padStart(2, '0');
        const timeStr = `${mm}m ${ss}s`;
        if (cd) cd.textContent = `ETA Downwind: ${mm}:${ss}`;
        if (hudTimer) hudTimer.textContent = timeStr;
        if (phaseBadge) {
          phaseBadge.textContent = `Phase 2: Lead-Lag In-Flight Vector (BESS Pre-Dispatch Active)`;
          phaseBadge.style.color = '#b45309';
          phaseBadge.style.background = '#fef3c7';
          phaseBadge.style.borderColor = '#fde68a';
        }
      } else if (p >= 60 && p < 85) {
        if (cd) cd.textContent = `IMPACT OCCLUDED (T = 0)`;
        if (hudTimer) hudTimer.textContent = `00m 00s`;
        if (phaseBadge) {
          phaseBadge.textContent = `Phase 3: Frontal Shadow Ingress at Main Park L1–L4`;
          phaseBadge.style.color = '#7c3aed';
          phaseBadge.style.background = '#f3e8ff';
          phaseBadge.style.borderColor = '#ddd6fe';
        }
      } else {
        if (cd) cd.textContent = `STABILIZED (+4.0m)`;
        if (hudTimer) hudTimer.textContent = `TRANSIENT CLEARED`;
        if (phaseBadge) {
          phaseBadge.textContent = `Phase 4: Full Mitigation Achieved (Frequency Locked at 60.00 Hz)`;
          phaseBadge.style.color = '#059669';
          phaseBadge.style.background = '#dcfce7';
          phaseBadge.style.borderColor = '#bbf7d0';
        }
      }
    }

    // ── INTERACTIVE CANVAS LISTENER ──
    function initRadarCanvasListeners() {
      if (radarCanvasListenersAttached) return;
      const canvas = document.getElementById('cloudRadarCanvas');
      if (!canvas) return;

      canvas.addEventListener('mousemove', e => {
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;
        radarMousePos.x = (e.clientX - rect.left) * scaleX;
        radarMousePos.y = (e.clientY - rect.top) * scaleY;

        const w = canvas.width;
        const h = canvas.height;
        let hit = null;
        for (const [id, node] of Object.entries(RADAR_NODES)) {
          const nx = node.rx * w;
          const ny = node.ry * h;
          const d = Math.hypot(radarMousePos.x - nx, radarMousePos.y - ny);
          if (d <= 24) {
            hit = parseInt(id);
            break;
          }
        }
        radarHoveredNode = hit;
        canvas.style.cursor = hit ? 'pointer' : 'crosshair';
        drawTacticalRadarCanvas();
      });

      canvas.addEventListener('mouseleave', () => {
        radarHoveredNode = null;
        drawTacticalRadarCanvas();
      });

      window.addEventListener('resize', () => {
        if (activeTab === 'map') {
          resizeRadarCanvas();
          drawTacticalRadarCanvas();
        }
      });

      radarCanvasListenersAttached = true;
    }

    // ── ANIMATION LOOP FOR DOPPLER RADAR SWEEP ──
    function startRadarLoop() {
      function tick() {
        if (activeTab === 'map') {
          radarSweepAngle = (radarSweepAngle + 0.02) % (Math.PI * 2);
          drawTacticalRadarCanvas();
        }
        radarAnimFrameId = requestAnimationFrame(tick);
      }
      radarAnimFrameId = requestAnimationFrame(tick);
    }

    // ── TACTICAL CANVAS RENDERER ──
    function drawTacticalRadarCanvas() {
      const canvas = document.getElementById('cloudRadarCanvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const w = canvas.width;
      const h = canvas.height;
      const scen = CLOUD_SCENARIOS[currentRadarScenario];

      // 1. Clear & Background
      ctx.fillStyle = '#f8fafc';
      ctx.fillRect(0, 0, w, h);

      // 2. High-Tech Grid & Distance Axes (0 to 15 km)
      ctx.strokeStyle = 'rgba(226, 232, 240, 0.9)';
      ctx.lineWidth = 1;
      const gridSize = 45;
      for (let x = 0; x < w; x += gridSize) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, h);
        ctx.stroke();
      }
      for (let y = 0; y < h; y += gridSize) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(w, y);
        ctx.stroke();
      }

      // Distance Axis Ticks along top
      ctx.fillStyle = '#94a3b8';
      ctx.font = '500 9px "JetBrains Mono", monospace';
      for (let x = 90; x < w; x += 130) {
        const km = ((x - (RADAR_NODES[13].rx * w)) / 55).toFixed(1);
        if (km >= 0) {
          ctx.fillText(`${km} km`, x - 10, 16);
        }
      }

      // 3. Sentinel L13 Origin & Isochrone Rings
      const sX = RADAR_NODES[13].rx * w;
      const sY = RADAR_NODES[13].ry * h;

      // Concentric Isochrone Arcs
      const isochrones = [
        { r: 90, label: "Isochrone T - 6.0m (0.6 km)", color: "rgba(2, 132, 199, 0.28)" },
        { r: 180, label: "Isochrone T - 3.0m (1.2 km)", color: "rgba(2, 132, 199, 0.38)" },
        { r: 275, label: "Isochrone T = 0.0m Arrival (1.85 km - L1 Array Front)", color: "rgba(220, 38, 38, 0.55)", bold: true },
        { r: 430, label: "Isochrone T + 12.0m Downstream Corridor (2.8 km)", color: "rgba(100, 116, 139, 0.25)" }
      ];

      isochrones.forEach(iso => {
        ctx.save();
        ctx.strokeStyle = iso.color;
        ctx.lineWidth = iso.bold ? 2.0 : 1.2;
        ctx.setLineDash(iso.bold ? [6, 4] : [4, 4]);
        ctx.beginPath();
        ctx.arc(sX, sY, iso.r, -Math.PI * 0.42, Math.PI * 0.42);
        ctx.stroke();

        ctx.fillStyle = iso.bold ? '#b91c1c' : '#0369a1';
        ctx.font = `${iso.bold ? '700' : '500'} 8.5px "JetBrains Mono", monospace`;
        const textAngle = 0.12;
        const tx = sX + Math.cos(textAngle) * (iso.r + 6);
        const ty = sY + Math.sin(textAngle) * (iso.r + 6);
        ctx.fillText(iso.label, tx, ty);
        ctx.restore();
      });

      // 4. Directional Doppler Cloud Propagation Vector
      const radHeading = scen.headingDeg * (Math.PI / 180);
      const vecLen = Math.min(520, w * 0.55);
      const vecEndX = sX + Math.cos(radHeading) * vecLen;
      const vecEndY = sY + Math.sin(radHeading) * vecLen;

      const arrowGrad = ctx.createLinearGradient(sX, sY, vecEndX, vecEndY);
      arrowGrad.addColorStop(0, 'rgba(2, 132, 199, 0.85)');
      arrowGrad.addColorStop(1, 'rgba(14, 165, 233, 0.1)');

      ctx.save();
      ctx.strokeStyle = arrowGrad;
      ctx.lineWidth = 2.5;
      ctx.setLineDash([8, 4]);
      ctx.beginPath();
      ctx.moveTo(sX - 60, sY - 20);
      ctx.lineTo(vecEndX, vecEndY);
      ctx.stroke();
      ctx.restore();

      ctx.save();
      ctx.fillStyle = '#0284c7';
      ctx.font = '700 9.5px "JetBrains Mono", monospace';
      ctx.fillText(`VECTOR: v = ${scen.speedKmh} km/h | θ = ${scen.headingDeg}° | τ = +${scen.leadTimeSec}s`, sX + 60, sY + 40);
      ctx.restore();

      // 5. Inter-Array Fiber/Microwave Telemetry Links
      const targetLinks = [1, 2, 4, 8, 12, 15, 17];
      targetLinks.forEach((tId, idx) => {
        const target = RADAR_NODES[tId];
        const tx = target.rx * w;
        const ty = target.ry * h;

        ctx.save();
        ctx.strokeStyle = 'rgba(186, 230, 253, 0.75)';
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.moveTo(sX, sY);
        ctx.lineTo(tx, ty);
        ctx.stroke();

        const pulseTime = ((Date.now() / 1200) + idx * 0.18) % 1;
        const px = sX + (tx - sX) * pulseTime;
        const py = sY + (ty - sY) * pulseTime;
        ctx.fillStyle = '#0284c7';
        ctx.beginPath();
        ctx.arc(px, py, 2.5, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      });

      // 6. Rotating Tactical Radar Sweep Beam from Sentinel L13
      ctx.save();
      const sweepRad = 300;
      const sweepGrad = ctx.createRadialGradient(sX, sY, 10, sX, sY, sweepRad);
      sweepGrad.addColorStop(0, 'rgba(2, 132, 199, 0.22)');
      sweepGrad.addColorStop(1, 'rgba(2, 132, 199, 0.0)');

      ctx.fillStyle = sweepGrad;
      ctx.beginPath();
      ctx.moveTo(sX, sY);
      ctx.arc(sX, sY, sweepRad, radarSweepAngle, radarSweepAngle + 0.35);
      ctx.closePath();
      ctx.fill();
      ctx.restore();

      // 7. Dynamic Moving Cloud Transient Footprint
      const cloudStartX = -40;
      const cloudStartY = 160;
      const cloudTargetX = w + 40;
      const cloudTargetY = 320;
      const cloudX = cloudStartX + (cloudTargetX - cloudStartX) * (radarSimProgress / 100);
      const cloudY = cloudStartY + (cloudTargetY - cloudStartY) * (radarSimProgress / 100);
      const cloudRadius = 160;

      ctx.save();
      const cGrad = ctx.createRadialGradient(cloudX, cloudY, 15, cloudX, cloudY, cloudRadius);
      cGrad.addColorStop(0, 'rgba(30, 41, 59, 0.48)');
      cGrad.addColorStop(0.45, 'rgba(71, 85, 105, 0.32)');
      cGrad.addColorStop(0.8, 'rgba(100, 116, 139, 0.12)');
      cGrad.addColorStop(1, 'rgba(148, 163, 184, 0.0)');

      ctx.fillStyle = cGrad;
      ctx.beginPath();
      ctx.ellipse(cloudX, cloudY, cloudRadius * 1.25, cloudRadius * 0.85, 0.25, 0, Math.PI * 2);
      ctx.fill();

      // Isobars
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.55)';
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 3]);
      ctx.beginPath();
      ctx.ellipse(cloudX, cloudY, cloudRadius * 0.7, cloudRadius * 0.5, 0.25, 0, Math.PI * 2);
      ctx.stroke();

      ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
      ctx.font = '700 8.5px "JetBrains Mono", monospace';
      ctx.fillText(`TRANSIENT CORE: GHI < 220 W/m²`, cloudX - 65, cloudY - 6);
      ctx.fillText(`OPTICAL ATTENUATION: -74%`, cloudX - 60, cloudY + 8);
      ctx.restore();

      // 8. Render All 17 PV Array Station Nodes
      for (const [idStr, node] of Object.entries(RADAR_NODES)) {
        const id = parseInt(idStr);
        const nx = node.rx * w;
        const ny = node.ry * h;
        const isHovered = (radarHoveredNode === id);
        const distFromCloud = Math.hypot(nx - cloudX, ny - cloudY);
        const isShaded = (distFromCloud < cloudRadius * 0.9);

        const nominalMW = node.capMW;
        const currentMW = isShaded ? (nominalMW * 0.24).toFixed(1) : nominalMW.toFixed(1);

        if (node.role === 'sentinel') {
          const isL13 = (id === 13);
          const rad = isHovered ? 16 : 13;

          if (isShaded) {
            ctx.save();
            ctx.strokeStyle = '#ef4444';
            ctx.lineWidth = 2.5;
            ctx.beginPath();
            ctx.arc(nx, ny, rad + 8, 0, Math.PI * 2);
            ctx.stroke();
            ctx.restore();
          }

          ctx.fillStyle = '#ffffff';
          ctx.beginPath();
          ctx.arc(nx, ny, rad, 0, Math.PI * 2);
          ctx.fill();

          ctx.strokeStyle = isShaded ? '#dc2626' : (isHovered ? '#0284c7' : '#0369a1');
          ctx.lineWidth = 3;
          ctx.stroke();

          ctx.fillStyle = '#0f172a';
          ctx.font = '800 11px Inter, sans-serif';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(`L${id}`, nx, ny);

          // Badge
          ctx.font = '700 8.5px "JetBrains Mono", monospace';
          const badgeText = isL13 ? '🛰️ SENTINEL-1 (UPWIND)' : '🛰️ SENTINEL-2';
          const bW = ctx.measureText(badgeText).width + 10;
          ctx.fillStyle = isShaded ? '#fee2e2' : '#e0f2fe';
          ctx.strokeStyle = isShaded ? '#f87171' : '#7dd3fc';
          ctx.lineWidth = 1;
          drawRoundRect(ctx, nx - bW / 2, ny - 30, bW, 16, 4);
          ctx.fill();
          ctx.stroke();

          ctx.fillStyle = isShaded ? '#991b1b' : '#0369a1';
          ctx.fillText(badgeText, nx, ny - 22);

          const ghiText = isShaded ? `GHI: 214 W/m² (-76%)` : `GHI: 896 W/m² (Nominal)`;
          ctx.font = '600 8px "JetBrains Mono", monospace';
          ctx.fillStyle = isShaded ? '#b91c1c' : '#475569';
          ctx.fillText(ghiText, nx, ny + 24);

        } else if (node.role === 'target') {
          const rad = isHovered ? 13 : 10;
          const isPreArmed = (radarSimProgress >= 20 && radarSimProgress < 60);

          ctx.fillStyle = '#ffffff';
          ctx.beginPath();
          ctx.arc(nx, ny, rad, 0, Math.PI * 2);
          ctx.fill();

          let nodeBorder = '#0284c7';
          if (isShaded) nodeBorder = '#7c3aed';
          else if (isPreArmed) nodeBorder = '#059669';

          ctx.strokeStyle = nodeBorder;
          ctx.lineWidth = isHovered ? 3.5 : 2.2;
          ctx.stroke();

          ctx.fillStyle = '#0f172a';
          ctx.font = '700 9px Inter, sans-serif';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(`L${id}`, nx, ny);

          const pText = `${currentMW} MW`;
          ctx.font = '600 8px "JetBrains Mono", monospace';
          const pW = ctx.measureText(pText).width + 8;
          ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
          ctx.strokeStyle = 'rgba(148, 163, 184, 0.5)';
          ctx.lineWidth = 1;
          drawRoundRect(ctx, nx - pW / 2, ny + 13, pW, 14, 3);
          ctx.fill();
          ctx.stroke();

          ctx.fillStyle = isShaded ? '#7c3aed' : '#334155';
          ctx.fillText(pText, nx, ny + 20);

        } else {
          const rad = isHovered ? 14 : 11;
          ctx.fillStyle = '#ffffff';
          ctx.beginPath();
          ctx.arc(nx, ny, rad, 0, Math.PI * 2);
          ctx.fill();

          ctx.strokeStyle = (id === 17) ? '#0284c7' : '#0d9488';
          ctx.lineWidth = 2.5;
          ctx.stroke();

          ctx.fillStyle = '#0f172a';
          ctx.font = '700 9px Inter, sans-serif';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(`L${id}`, nx, ny);

          const roleLabel = (id === 17) ? 'Grid Substation' : 'Coastal Watch';
          ctx.font = '600 8px "JetBrains Mono", monospace';
          ctx.fillStyle = '#475569';
          ctx.fillText(roleLabel, nx, ny + 20);
        }
      }

      // 9. Interactive Hover HUD Popup
      if (radarHoveredNode) {
        drawNodeHoverHUD(ctx, radarHoveredNode, w, h);
      }

      // 10. Top Tactical Telemetry Bar
      ctx.save();
      ctx.fillStyle = 'rgba(15, 23, 42, 0.92)';
      drawRoundRect(ctx, 16, 12, 540, 24, 6);
      ctx.fill();

      ctx.fillStyle = '#38bdf8';
      ctx.font = '700 9.5px "JetBrains Mono", monospace';
      ctx.fillText(`● LIVE DOPPLER TRACKING`, 26, 28);

      ctx.fillStyle = '#f8fafc';
      ctx.font = '500 9px "JetBrains Mono", monospace';
      ctx.fillText(`CORRIDOR: Hualien 17-Plant Array | ALGO: Lead-Lag Cross-Correlation (τ)`, 175, 28);
      ctx.restore();

      // 11. Scale Bar & Compass HUD
      drawRadarScaleAndCompass(ctx, w, h);
    }

    // ── DRAW NODE HOVER TELEMETRY HUD ──
    function drawNodeHoverHUD(ctx, id, w, h) {
      const node = RADAR_NODES[id];
      const nx = node.rx * w;
      const ny = node.ry * h;
      const mx = Math.min(nx + 18, w - 230);
      const my = Math.min(ny - 10, h - 140);
      const hudW = 210;
      const hudH = 120;

      ctx.save();
      ctx.fillStyle = 'rgba(15, 23, 42, 0.96)';
      ctx.strokeStyle = '#0284c7';
      ctx.lineWidth = 1.5;
      drawRoundRect(ctx, mx, my, hudW, hudH, 6);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = '#38bdf8';
      ctx.font = '700 10.5px Inter, sans-serif';
      ctx.textAlign = 'left';
      ctx.fillText(node.name, mx + 12, my + 18);

      ctx.fillStyle = '#cbd5e1';
      ctx.font = '500 9px "JetBrains Mono", monospace';
      ctx.fillText(`Role: ${node.role.toUpperCase()} ARRAY`, mx + 12, my + 34);
      ctx.fillText(`Ground Distance from L13: ${node.distance.toFixed(2)} km`, mx + 12, my + 49);
      ctx.fillText(`Empirical Time Delay (τ): +${node.tau}s (${(node.tau / 60).toFixed(1)}m)`, mx + 12, my + 64);
      ctx.fillText(`Cross-Correlation: r = ${node.r.toFixed(2)}`, mx + 12, my + 79);
      ctx.fillText(`Nameplate Capacity: ${node.capMW.toFixed(1)} MW`, mx + 12, my + 94);
      ctx.fillText(`Panel Orientation: ${node.ori}° | Alt: ${node.alt}m`, mx + 12, my + 109);
      ctx.restore();
    }

    // ── SCALE BAR & COMPASS HUD ──
    function drawRadarScaleAndCompass(ctx, w, h) {
      ctx.save();
      const sbX = 25, sbY = h - 22;
      ctx.strokeStyle = '#334155';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(sbX, sbY);
      ctx.lineTo(sbX + 110, sbY);
      ctx.moveTo(sbX, sbY - 4); ctx.lineTo(sbX, sbY + 4);
      ctx.moveTo(sbX + 55, sbY - 3); ctx.lineTo(sbX + 55, sbY + 3);
      ctx.moveTo(sbX + 110, sbY - 4); ctx.lineTo(sbX + 110, sbY + 4);
      ctx.stroke();

      ctx.fillStyle = '#475569';
      ctx.font = '600 8.5px "JetBrains Mono", monospace';
      ctx.textAlign = 'center';
      ctx.fillText('0', sbX, sbY - 7);
      ctx.fillText('1.0 km', sbX + 55, sbY - 7);
      ctx.fillText('2.0 km', sbX + 110, sbY - 7);
      ctx.restore();
    }

    // ── SPLIT-SCREEN CHARTS INITIALIZATION ──
    function initSplitImpactCharts() {
      const timeLabels = ['-8 min', '-6 min', '-4 min', '-2 min', '0 min (Shadow Ingress)', '+2 min', '+4 min', '+6 min', '+8 min'];

      // 1. Unmitigated Chart
      const ctxUnmit = document.getElementById('unmitigatedChart');
      if (ctxUnmit) {
        if (unmitigatedChartInst) unmitigatedChartInst.destroy();
        unmitigatedChartInst = new Chart(ctxUnmit, {
          type: 'line',
          data: {
            labels: timeLabels,
            datasets: [
              {
                label: 'PV Generation (MW)',
                data: [50, 50, 50, 48, 12, 12, 14, 25, 45],
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.08)',
                borderWidth: 2.2,
                pointRadius: 3,
                tension: 0.3,
                fill: true,
                yAxisID: 'y'
              },
              {
                label: 'Delayed BESS Reserve (MW)',
                data: [0, 0, 0, 0, 0, 4, 18, 32, 8],
                borderColor: '#f59e0b',
                borderDash: [4, 4],
                borderWidth: 1.8,
                pointRadius: 2,
                tension: 0.2,
                yAxisID: 'y'
              },
              {
                label: 'Grid Frequency (Hz)',
                data: [60.00, 60.00, 60.00, 59.98, 59.72, 59.74, 59.86, 59.96, 60.00],
                borderColor: '#dc2626',
                borderWidth: 3,
                pointRadius: 4,
                pointBackgroundColor: '#b91c1c',
                tension: 0.25,
                yAxisID: 'y1'
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'top',
                labels: { boxWidth: 10, font: { family: 'Inter', size: 10 } }
              },
              tooltip: {
                backgroundColor: '#0f172a',
                titleFont: { family: 'Inter', size: 11 },
                bodyFont: { family: 'JetBrains Mono', size: 10 }
              }
            },
            scales: {
              x: {
                grid: { color: 'rgba(0, 0, 0, 0.04)' },
                ticks: { color: '#64748b', font: { family: 'JetBrains Mono', size: 9.5 } }
              },
              y: {
                position: 'left',
                min: 0,
                max: 65,
                title: { display: true, text: 'Power (MW)', font: { size: 9.5 } },
                grid: { color: 'rgba(0, 0, 0, 0.04)' },
                ticks: { color: '#64748b', font: { family: 'JetBrains Mono', size: 9.5 }, callback: v => v + ' MW' }
              },
              y1: {
                position: 'right',
                min: 59.60,
                max: 60.10,
                title: { display: true, text: 'Frequency (Hz)', font: { size: 9.5 } },
                grid: { drawOnChartArea: false },
                ticks: { color: '#dc2626', font: { family: 'JetBrains Mono', size: 9.5, weight: 'bold' }, callback: v => v.toFixed(2) + ' Hz' }
              }
            }
          }
        });
      }

      // 2. Pre-emptively Mitigated Chart
      const ctxMit = document.getElementById('mitigatedChart');
      if (ctxMit) {
        if (mitigatedChartInst) mitigatedChartInst.destroy();
        mitigatedChartInst = new Chart(ctxMit, {
          type: 'line',
          data: {
            labels: timeLabels,
            datasets: [
              {
                label: 'PV Generation (MW)',
                data: [50, 50, 50, 48, 12, 12, 14, 25, 45],
                borderColor: '#94a3b8',
                borderDash: [3, 3],
                borderWidth: 1.5,
                pointRadius: 2,
                tension: 0.3,
                yAxisID: 'y'
              },
              {
                label: 'Pre-emptive BESS Reserve (MW)',
                data: [0, 8, 22, 38, 38, 38, 36, 25, 5],
                borderColor: '#0284c7',
                backgroundColor: 'rgba(2, 132, 199, 0.12)',
                borderWidth: 2.2,
                pointRadius: 3,
                tension: 0.3,
                fill: true,
                yAxisID: 'y'
              },
              {
                label: 'Net Grid Power Delivered (MW)',
                data: [50, 50, 50, 50, 50, 50, 50, 50, 50],
                borderColor: '#059669',
                borderWidth: 2.5,
                pointRadius: 2,
                tension: 0,
                yAxisID: 'y'
              },
              {
                label: 'Grid Frequency (Hz)',
                data: [60.00, 60.00, 60.00, 60.00, 60.00, 60.00, 60.00, 60.00, 60.00],
                borderColor: '#10b981',
                borderWidth: 3.2,
                pointRadius: 4,
                pointBackgroundColor: '#059669',
                tension: 0,
                yAxisID: 'y1'
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'top',
                labels: { boxWidth: 10, font: { family: 'Inter', size: 10 } }
              },
              tooltip: {
                backgroundColor: '#0f172a',
                titleFont: { family: 'Inter', size: 11 },
                bodyFont: { family: 'JetBrains Mono', size: 10 }
              }
            },
            scales: {
              x: {
                grid: { color: 'rgba(0, 0, 0, 0.04)' },
                ticks: { color: '#64748b', font: { family: 'JetBrains Mono', size: 9.5 } }
              },
              y: {
                position: 'left',
                min: 0,
                max: 65,
                title: { display: true, text: 'Power (MW)', font: { size: 9.5 } },
                grid: { color: 'rgba(0, 0, 0, 0.04)' },
                ticks: { color: '#64748b', font: { family: 'JetBrains Mono', size: 9.5 }, callback: v => v + ' MW' }
              },
              y1: {
                position: 'right',
                min: 59.60,
                max: 60.10,
                title: { display: true, text: 'Frequency (Hz)', font: { size: 9.5 } },
                grid: { drawOnChartArea: false },
                ticks: { color: '#059669', font: { family: 'JetBrains Mono', size: 9.5, weight: 'bold' }, callback: v => v.toFixed(2) + ' Hz' }
              }
            }
          }
        });
      }
    }

    function updateSplitImpactCharts() {
      if (!unmitigatedChartInst || !mitigatedChartInst) return;
      unmitigatedChartInst.update();
      mitigatedChartInst.update();
    }

    function updateChartsHighlight() {
      const stepIdx = Math.min(8, Math.floor((radarSimProgress / 100) * 8.99));
      [unmitigatedChartInst, mitigatedChartInst].forEach(chart => {
        if (!chart) return;
        chart.data.datasets.forEach(ds => {
          ds.pointRadius = ds.data.map((_, i) => (i === stepIdx ? 7 : (ds.label.includes('Frequency') ? 3 : 2)));
        });
        chart.update('none');
      });
    }

"""

new_content = content[:start_idx] + new_js + content[end_idx:]

with open(target_file, "w", encoding="utf-8") as f:
    f.write(new_content)

print("SUCCESS: index.html updated with responsive nodes and drawRoundRect!")
