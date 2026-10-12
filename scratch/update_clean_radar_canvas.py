import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update initRadarCanvasListeners to add click event
old_listeners = """      canvas.addEventListener('mouseleave', () => {
        radarHoveredNode = null;
        drawTacticalRadarCanvas();
      });"""

new_listeners = """      canvas.addEventListener('click', e => {
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;
        const clickX = (e.clientX - rect.left) * scaleX;
        const clickY = (e.clientY - rect.top) * scaleY;
        const w = canvas.width;
        const h = canvas.height;

        let hit = null;
        for (const [id, node] of Object.entries(RADAR_NODES)) {
          const nx = node.rx * w;
          const ny = node.ry * h;
          if (Math.hypot(clickX - nx, clickY - ny) <= 24) {
            hit = parseInt(id);
            break;
          }
        }
        if (hit) {
          selectPlantNode(hit, true);
        }
      });

      canvas.addEventListener('mouseleave', () => {
        radarHoveredNode = null;
        drawTacticalRadarCanvas();
      });"""

if old_listeners in content and 'canvas.addEventListener(\'click\'' not in content:
    content = content.replace(old_listeners, new_listeners, 1)
    print("Added canvas click listener")

# 2. Update renderMapView to call selectPlantNode(selectedPlantId || 13, false)
content = re.sub(
    r'initSplitImpactCharts\(\);\s*syncScenarioUI\(\);\s*drawTacticalRadarCanvas\(\);',
    'initSplitImpactCharts();\n      syncScenarioUI();\n      selectPlantNode(selectedPlantId || 13, false);\n      drawTacticalRadarCanvas();',
    content
)
print("Updated renderMapView")

# 3. Update onRadarScrubber to call selectPlantNode(selectedPlantId, false)
content = re.sub(
    r'function onRadarScrubber\(val\) \{\s*radarSimProgress = parseFloat\(val\);\s*updateRadarSimProgressUI\(\);\s*drawTacticalRadarCanvas\(\);\s*updateChartsHighlight\(\);\s*\}',
    'function onRadarScrubber(val) {\n      radarSimProgress = parseFloat(val);\n      updateRadarSimProgressUI();\n      selectPlantNode(selectedPlantId, false);\n      drawTacticalRadarCanvas();\n      updateChartsHighlight();\n    }',
    content
)
print("Updated onRadarScrubber")

# 4. Replace the entire drawTacticalRadarCanvas function with the ultra-clean, clutter-free, interactive version
old_draw_start = "    // ── TACTICAL CANVAS RENDERER ──\n    function drawTacticalRadarCanvas() {"
# Find the end of drawTacticalRadarCanvas by looking for drawNodeHoverHUD
draw_end_marker = "    // ── DRAW NODE HOVER TELEMETRY HUD ──"

idx_start = content.find(old_draw_start)
idx_end = content.find(draw_end_marker)

if idx_start != -1 and idx_end != -1:
    clean_draw_function = """    // ── TACTICAL CANVAS RENDERER (CLEAN, SIMPLE, ULTRA-PREMIUM WITH GSAP) ──
    function drawTacticalRadarCanvas() {
      const canvas = document.getElementById('cloudRadarCanvas');
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const w = canvas.width;
      const h = canvas.height;
      const scen = getActiveScenario();

      // 1. Crisp Slate Background
      ctx.fillStyle = '#f8fafc';
      ctx.fillRect(0, 0, w, h);

      // 2. High-Tech Grid & Distance Axes (0 to 15 km)
      ctx.strokeStyle = 'rgba(226, 232, 240, 0.85)';
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
      ctx.font = '500 8.5px "JetBrains Mono", monospace';
      for (let x = 600; x < w - 60; x += 120) {
        const km = ((x - (RADAR_NODES[13].rx * w)) / 55).toFixed(1);
        if (km >= 0) {
          ctx.fillText(`${km} km`, x, 24);
        }
      }

      // 3. Sentinel L13 Origin & Clean Concentric Range Rings (No messy central text!)
      const sX = RADAR_NODES[13].rx * w;
      const sY = RADAR_NODES[13].ry * h;

      const cleanArcs = [
        { r: 120, label: "0.8 km" },
        { r: 240, label: "1.6 km" },
        { r: 380, label: "2.6 km" }
      ];

      cleanArcs.forEach(arc => {
        ctx.save();
        ctx.strokeStyle = 'rgba(2, 132, 199, 0.18)';
        ctx.lineWidth = 1.2;
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.arc(sX, sY, arc.r, -Math.PI * 0.40, Math.PI * 0.40);
        ctx.stroke();

        // Subtle, clean distance tag in perimeter zone away from nodes
        ctx.fillStyle = '#94a3b8';
        ctx.font = '600 8px "JetBrains Mono", monospace';
        const angle = -Math.PI * 0.38;
        const tx = sX + Math.cos(angle) * (arc.r + 4);
        const ty = sY + Math.sin(angle) * (arc.r + 4);
        if (ty > 18 && ty < 100) {
          ctx.fillText(arc.label, tx, ty);
        }
        ctx.restore();
      });

      // 4. Directional Doppler Cloud Propagation Vector Line (Subtle & Clean)
      const radHeading = scen.headingDeg * (Math.PI / 180);
      const vecLen = Math.min(520, w * 0.55);
      const vecEndX = sX + Math.cos(radHeading) * vecLen;
      const vecEndY = sY + Math.sin(radHeading) * vecLen;

      const arrowGrad = ctx.createLinearGradient(sX, sY, vecEndX, vecEndY);
      arrowGrad.addColorStop(0, 'rgba(2, 132, 199, 0.7)');
      arrowGrad.addColorStop(1, 'rgba(14, 165, 233, 0.05)');

      ctx.save();
      ctx.strokeStyle = arrowGrad;
      ctx.lineWidth = 2.0;
      ctx.setLineDash([6, 4]);
      ctx.beginPath();
      ctx.moveTo(sX - 50, sY - 15);
      ctx.lineTo(vecEndX, vecEndY);
      ctx.stroke();
      ctx.restore();

      // 5. Inter-Array Fiber Telemetry Links
      const targetLinks = [1, 2, 4, 8, 12, 15, 17];
      targetLinks.forEach((tId, idx) => {
        const target = RADAR_NODES[tId];
        const tx = target.rx * w;
        const ty = target.ry * h;

        ctx.save();
        ctx.strokeStyle = 'rgba(186, 230, 253, 0.65)';
        ctx.lineWidth = 1.0;
        ctx.beginPath();
        ctx.moveTo(sX, sY);
        ctx.lineTo(tx, ty);
        ctx.stroke();

        const pulseTime = ((Date.now() / 1200) + idx * 0.18) % 1;
        const px = sX + (tx - sX) * pulseTime;
        const py = sY + (ty - sY) * pulseTime;
        ctx.fillStyle = '#0284c7';
        ctx.beginPath();
        ctx.arc(px, py, 2.2, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      });

      // 6. Rotating Tactical Radar Sweep Beam from Sentinel L13
      ctx.save();
      const sweepRad = 300;
      const sweepGrad = ctx.createRadialGradient(sX, sY, 10, sX, sY, sweepRad);
      sweepGrad.addColorStop(0, 'rgba(2, 132, 199, 0.18)');
      sweepGrad.addColorStop(1, 'rgba(2, 132, 199, 0.0)');

      ctx.fillStyle = sweepGrad;
      ctx.beginPath();
      ctx.moveTo(sX, sY);
      ctx.arc(sX, sY, sweepRad, radarSweepAngle, radarSweepAngle + 0.35);
      ctx.closePath();
      ctx.fill();
      ctx.restore();

      // 7. Dynamic Moving Cloud Footprint
      const cloudStartX = -60;
      const cloudStartY = scen.cloudStartY || 160;
      const cloudTargetX = w + 60;
      const cloudTargetY = scen.cloudTargetY || 320;
      const cloudX = cloudStartX + (cloudTargetX - cloudStartX) * (radarSimProgress / 100);
      const cloudY = cloudStartY + (cloudTargetY - cloudStartY) * (radarSimProgress / 100);
      const cloudRadius = scen.cloudRadius || 160;
      const aspect = scen.cloudAspect || 1.25;

      ctx.save();
      const cGrad = ctx.createRadialGradient(cloudX, cloudY, 15, cloudX, cloudY, cloudRadius);
      if (currentRadarScenario === 'fast') {
        cGrad.addColorStop(0, 'rgba(15, 23, 42, 0.75)');
        cGrad.addColorStop(0.35, 'rgba(30, 41, 59, 0.60)');
        cGrad.addColorStop(0.75, 'rgba(51, 65, 85, 0.30)');
        cGrad.addColorStop(1, 'rgba(100, 116, 139, 0.0)');
      } else if (currentRadarScenario === 'slow') {
        cGrad.addColorStop(0, 'rgba(148, 163, 184, 0.40)');
        cGrad.addColorStop(0.45, 'rgba(203, 213, 225, 0.25)');
        cGrad.addColorStop(0.8, 'rgba(226, 232, 240, 0.12)');
        cGrad.addColorStop(1, 'rgba(241, 245, 249, 0.0)');
      } else {
        cGrad.addColorStop(0, 'rgba(30, 41, 59, 0.45)');
        cGrad.addColorStop(0.45, 'rgba(71, 85, 105, 0.28)');
        cGrad.addColorStop(0.8, 'rgba(100, 116, 139, 0.10)');
        cGrad.addColorStop(1, 'rgba(148, 163, 184, 0.0)');
      }

      ctx.fillStyle = cGrad;
      ctx.beginPath();
      ctx.ellipse(cloudX, cloudY, cloudRadius * aspect, cloudRadius * (1 / aspect), (scen.headingDeg - 90) * (Math.PI / 180), 0, Math.PI * 2);
      ctx.fill();

      // Cloud Contour Outline
      ctx.strokeStyle = (currentRadarScenario === 'fast') ? 'rgba(239, 68, 68, 0.40)' : ((currentRadarScenario === 'slow') ? 'rgba(186, 230, 253, 0.5)' : 'rgba(255, 255, 255, 0.50)');
      ctx.lineWidth = 1.2;
      ctx.setLineDash([4, 3]);
      ctx.beginPath();
      ctx.ellipse(cloudX, cloudY, cloudRadius * 0.7, cloudRadius * 0.5, (scen.headingDeg - 90) * (Math.PI / 180), 0, Math.PI * 2);
      ctx.stroke();

      // Clean, single-line Cloud Status Badge inside cloud
      ctx.fillStyle = (currentRadarScenario === 'slow') ? '#0f172a' : 'rgba(255, 255, 255, 0.95)';
      ctx.font = '700 8.5px "JetBrains Mono", monospace';
      ctx.textAlign = 'center';
      ctx.fillText(`☁️ CLOUD FRONT (-${scen.sunBlockPct || 74}% SUN · -${scen.deltaMW} MW)`, cloudX, cloudY);
      ctx.restore();

      // 8. Render All 17 PV Array Station Nodes Cleanly
      for (const [idStr, node] of Object.entries(RADAR_NODES)) {
        const id = parseInt(idStr);
        const nx = node.rx * w;
        const ny = node.ry * h;
        const isHovered = (radarHoveredNode === id);
        const isSelected = (selectedPlantId === id);
        const distFromCloud = Math.hypot(nx - cloudX, ny - cloudY);
        const isShaded = (distFromCloud < cloudRadius * 0.9);

        const nominalMW = node.capMW;
        const currentMW = isShaded ? (nominalMW * Math.max(0.05, 1 - (scen.sunBlockPct || 74) / 100)).toFixed(1) : nominalMW.toFixed(1);

        const baseRad = (node.role === 'sentinel') ? 14 : ((node.role === 'substation') ? 13 : 11);
        const rad = isHovered ? (baseRad + 2) : baseRad;

        // Selected Plant Animated Beacon Aura Ring
        if (isSelected) {
          ctx.save();
          const t = Date.now() / 350;
          const auraRad = rad + 5 + ((Math.sin(t) + 1) * 3);
          const auraAlpha = 0.65 - ((Math.sin(t) + 1) * 0.2);
          ctx.strokeStyle = `rgba(37, 99, 235, ${auraAlpha})`;
          ctx.lineWidth = 2.5;
          ctx.beginPath();
          ctx.arc(nx, ny, auraRad, 0, Math.PI * 2);
          ctx.stroke();
          ctx.restore();
        }

        // Shaded Warning Halo
        if (isShaded) {
          ctx.save();
          ctx.strokeStyle = 'rgba(239, 68, 68, 0.45)';
          ctx.lineWidth = 2.0;
          ctx.beginPath();
          ctx.arc(nx, ny, rad + 4, 0, Math.PI * 2);
          ctx.stroke();
          ctx.restore();
        }

        // Node Circle Body Fill
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(nx, ny, rad, 0, Math.PI * 2);
        ctx.fill();

        // Node Border Color
        let strokeColor = '#0284c7';
        let strokeWidth = 2.0;
        if (isSelected) {
          strokeColor = '#2563eb';
          strokeWidth = 3.5;
        } else if (isShaded) {
          strokeColor = '#dc2626';
          strokeWidth = 2.5;
        } else if (node.role === 'sentinel') {
          strokeColor = '#0284c7';
          strokeWidth = 2.8;
        } else if (node.role === 'target') {
          strokeColor = '#10b981';
          strokeWidth = 2.2;
        } else if (node.role === 'substation') {
          strokeColor = '#6366f1';
          strokeWidth = 2.5;
        } else {
          strokeColor = '#0284c7';
          strokeWidth = 2.2;
        }

        ctx.strokeStyle = strokeColor;
        ctx.lineWidth = strokeWidth;
        ctx.stroke();

        // Node Identifier Inside Circle
        ctx.fillStyle = '#0f172a';
        ctx.font = `800 ${rad > 12 ? '10px' : '9px'} Inter, sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(`L${id}`, nx, ny);

        // Minimal, Clean Subtitle Labels (No overlapping badges!)
        if (node.role === 'sentinel') {
          ctx.font = '700 7.5px "JetBrains Mono", monospace';
          ctx.fillStyle = isShaded ? '#dc2626' : '#0369a1';
          ctx.fillText('WATCHMAN', nx, ny - rad - 5);
          ctx.font = '600 7.5px "JetBrains Mono", monospace';
          ctx.fillStyle = isShaded ? '#dc2626' : '#64748b';
          ctx.fillText(`${currentMW} MW`, nx, ny + rad + 7);
        } else {
          ctx.font = '600 7.5px "JetBrains Mono", monospace';
          ctx.fillStyle = isShaded ? '#dc2626' : '#64748b';
          ctx.fillText(`${currentMW} MW`, nx, ny + rad + 7);
        }
      }

      // 9. Interactive Hover HUD Popup
      if (radarHoveredNode && radarHoveredNode !== selectedPlantId) {
        drawNodeHoverHUD(ctx, radarHoveredNode, w, h);
      }

      // 10. Top Tactical Telemetry Bar
      ctx.save();
      ctx.textAlign = 'left';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = 'rgba(15, 23, 42, 0.92)';
      drawRoundRect(ctx, 16, 12, 540, 24, 6);
      ctx.fill();

      ctx.fillStyle = '#38bdf8';
      ctx.font = '700 9px "JetBrains Mono", monospace';
      ctx.fillText('● LIVE RADAR GRID', 26, 24);

      ctx.fillStyle = '#cbd5e1';
      ctx.font = '500 8.5px "JetBrains Mono", monospace';
      ctx.fillText('17 PV PLANTS SYNCHRONIZED · CLICK ANY PLANT TO INSPECT TELEMETRY', 145, 24);
      ctx.restore();

      // 11. Scale Bar & Compass HUD
      drawRadarScaleAndCompass(ctx, w, h);
    }
\n"""

    content = content[:idx_start] + clean_draw_function + content[idx_end:]
    print("Successfully replaced drawTacticalRadarCanvas with clean, interactive version!")
else:
    print("Could not locate drawTacticalRadarCanvas bounds:", idx_start, idx_end)

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Saved complete radar engine enhancements!")
