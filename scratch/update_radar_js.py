import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Check for existing selectedPlantId
if 'let selectedPlantId = 13;' not in content:
    # Add selectedPlantId right after radarHoveredNode
    content = content.replace(
        'let radarHoveredNode = null;\n    let radarMousePos = { x: 0, y: 0 };',
        'let radarHoveredNode = null;\n    let selectedPlantId = 13;\n    let radarMousePos = { x: 0, y: 0 };'
    )

# Prepare selectPlantNode function and enhanced canvas code
js_enhancements = """
    // ── INTERACTIVE PLANT INSPECTOR WITH GSAP ──
    function selectPlantNode(id, animate = true) {
      if (!RADAR_NODES[id]) return;
      selectedPlantId = id;
      const node = RADAR_NODES[id];
      const scen = getActiveScenario();
      const w = document.getElementById('cloudRadarCanvas') ? document.getElementById('cloudRadarCanvas').width : 1000;
      
      // Calculate cloud position
      const cloudStartX = -60;
      const cloudTargetX = w + 60;
      const cloudX = cloudStartX + (cloudTargetX - cloudStartX) * (radarSimProgress / 100);
      const cloudY = (scen.cloudStartY || 160) + ((scen.cloudTargetY || 320) - (scen.cloudStartY || 160)) * (radarSimProgress / 100);
      const cloudRadius = scen.cloudRadius || 160;
      const nx = node.rx * w;
      const ny = node.ry * 480;
      const distFromCloud = Math.hypot(nx - cloudX, ny - cloudY);
      const isShaded = (distFromCloud < cloudRadius * 0.9);

      // Calculations
      const nominalMW = node.capMW;
      const sunPct = isShaded ? Math.max(8, 100 - (scen.sunBlockPct || 74)) : 100;
      const currentMW = (nominalMW * (sunPct / 100)).toFixed(1);

      // Update Active Chip
      document.querySelectorAll('.plant-chip').forEach(c => c.classList.remove('active'));
      const activeChip = document.getElementById(`chip-${id}`);
      if (activeChip) activeChip.classList.add('active');

      // Update Inspector Fields
      const roleBadge = document.getElementById('inspRoleBadge');
      const plantTitle = document.getElementById('inspPlantTitle');
      const location = document.getElementById('inspLocation');
      const statusBadge = document.getElementById('inspStatusBadge');
      const statusText = document.getElementById('inspStatusText');
      const mwVal = document.getElementById('inspMWVal');
      const mwBar = document.getElementById('inspMWBar');
      const sunVal = document.getElementById('inspSunVal');
      const sunSub = document.getElementById('inspSunSub');
      const leadVal = document.getElementById('inspLeadVal');
      const leadSub = document.getElementById('inspLeadSub');
      const syncVal = document.getElementById('inspSyncVal');
      const syncSub = document.getElementById('inspSyncSub');
      const azimuth = document.getElementById('inspAzimuth');
      const bessStatus = document.getElementById('inspBessStatus');
      const distance = document.getElementById('inspDistance');
      const roleDesc = document.getElementById('inspRoleDesc');

      if (roleBadge) {
        if (node.role === 'sentinel') roleBadge.textContent = id === 13 ? '🛡️ PRIMARY WATCHMAN STATION' : '🛡️ SECONDARY WATCHMAN STATION';
        else if (node.role === 'target') roleBadge.textContent = '☀️ MAIN SOLAR GENERATION ARRAY';
        else if (node.role === 'substation') roleBadge.textContent = '⚡ REGIONAL GRID INTERCONNECT';
        else roleBadge.textContent = '🌊 COASTAL PV FACILITY';
      }

      if (plantTitle) plantTitle.textContent = node.name;
      if (location) location.textContent = `Elevation: ${node.alt}m MSL · Inverter Array ${id} · IEEE 2800 Standard Verified`;

      if (statusBadge && statusText) {
        if (isShaded) {
          statusBadge.classList.add('shaded');
          statusText.textContent = `⚠️ CLOUD SHADOWED (-${scen.sunBlockPct || 74}%)`;
        } else {
          statusBadge.classList.remove('shaded');
          statusText.textContent = `🟢 FULL SOLAR GENERATION (${currentMW} MW)`;
        }
      }

      if (mwVal) mwVal.textContent = `${currentMW} MW`;
      if (mwBar) {
        const pct = Math.min(100, Math.round((parseFloat(currentMW) / nominalMW) * 100));
        mwBar.style.width = `${pct}%`;
        mwBar.style.background = isShaded ? '#dc2626' : '#10b981';
      }

      if (sunVal) sunVal.textContent = `${sunPct}%`;
      if (sunSub) sunSub.textContent = isShaded ? `Shadow Ingress: Loss of ${(nominalMW - parseFloat(currentMW)).toFixed(1)} MW` : 'Full Solar Irradiance';

      if (leadVal) leadVal.textContent = id === 13 ? '+0.0 mins' : `+${(node.tau / 60).toFixed(1)} mins`;
      if (leadSub) leadSub.textContent = id === 13 ? 'West Foothills Reference Node' : `${node.tau}s Lead-Lag Defense Advantage`;

      if (syncVal) syncVal.textContent = `${Math.round(node.r * 100)}%`;
      if (syncSub) syncSub.textContent = `Sensor Match (r = ${node.r.toFixed(2)})`;

      if (azimuth) azimuth.textContent = `${node.ori}° (${node.ori === 270 ? 'West Facing Sentinel' : (node.ori === 180 ? 'South Facing Fixed' : 'Southeast Facing')})`;
      if (bessStatus) bessStatus.textContent = isShaded ? '⚡ Full Battery Injection Active (Power Restored)' : '🟢 Battery Standby · Pre-emptive Ramp Ready';
      if (distance) distance.textContent = id === 13 ? '0.0 km (Westmost Sensor)' : `${node.distance.toFixed(2)} km Downwind of L13`;
      if (roleDesc) {
        if (node.role === 'sentinel') roleDesc.textContent = 'Early-Warning Cloud Velocity Sentinel';
        else if (node.role === 'target') roleDesc.textContent = 'Protected Generation Node (BESS Backed)';
        else if (node.role === 'substation') roleDesc.textContent = 'Regional Substation Imbalance Safeguard';
        else roleDesc.textContent = 'Coastal Fringe Monitoring Sensor';
      }

      // GSAP Micro-interaction animations
      if (animate && window.gsap) {
        gsap.fromTo('#plantInspectorCard',
          { y: 8, opacity: 0.85 },
          { y: 0, opacity: 1, duration: 0.3, ease: 'power2.out' }
        );
        gsap.fromTo('#inspMWVal',
          { scale: 1.15, color: '#0284c7' },
          { scale: 1.0, color: '#0f172a', duration: 0.35, ease: 'back.out(1.5)' }
        );
      }

      drawTacticalRadarCanvas();
    }
"""

# Check if selectPlantNode is already present, if not add it
if 'function selectPlantNode(' not in content:
    content = content.replace('    function resizeRadarCanvas() {', js_enhancements + '\n    function resizeRadarCanvas() {', 1)
    print("Added selectPlantNode function")

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Saved JS enhancements step 1")
