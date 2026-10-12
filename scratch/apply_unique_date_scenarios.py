import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Helper functions to add to the script
helpers_code = """
    // ═════════════════════════════════════════════════════════════════════════
    // 🌤️ DATE-SPECIFIC WEATHER PROFILER & ADVANCE TELEMETRY ENGINE
    // ═════════════════════════════════════════════════════════════════════════
    function getDateWeatherProfile(dateVal) {
      if (!dateVal) {
        const el = document.getElementById('dateSelect');
        dateVal = el ? el.value : '2026-01-06';
      }
      if (!dateVal) dateVal = '2026-01-06';

      let h = 0;
      for (let i = 0; i < dateVal.length; i++) {
        h = ((h << 5) - h) + dateVal.charCodeAt(i);
        h = h & 0xFFFFFFFF;
      }
      if (h > 0x7FFFFFFF) h -= 0x100000000;
      const posHash = Math.abs(h);

      // Archetype distribution across the 124 available dates:
      // ~72% Normal Cloud Day, ~18% Fast Storm Day, ~10% Slow Heavy Fog
      const mod20 = posHash % 20;
      let archetype = 'moderate';
      let title = 'Normal Cloud Day';
      let baseSpeed = 13.8;
      let sunBlock = 74;
      let freqDip = 59.72;

      if (mod20 === 0 || mod20 === 1 || mod20 === 2) {
        // Fast Storm Day (Thunderstorm) - User requirement +4.2min
        archetype = 'fast';
        title = 'Fast Storm Day';
        baseSpeed = 26.5;
        sunBlock = 92;
        freqDip = 59.58;
      } else if (mod20 === 3 || mod20 === 4) {
        // Slow Heavy Fog - User requirement +14.2 / +14.8min
        archetype = 'slow';
        title = 'Slow Heavy Fog';
        baseSpeed = 7.5;
        sunBlock = 58;
        freqDip = 59.88;
      } else {
        // Normal Cloud Day - User requirement +8.2min
        archetype = 'moderate';
        title = 'Normal Cloud Day';
        baseSpeed = 13.8;
        sunBlock = 74;
        freqDip = 59.72;
      }

      // Unique simulation event time of day for each date
      const times = ['09:40 AM', '10:20 AM', '11:10 AM', '11:50 AM', '12:30 PM', '13:10 PM', '13:50 PM', '14:20 PM', '15:10 PM'];
      const eventTime = times[posHash % times.length];

      return {
        date: dateVal,
        archetype,
        title,
        baseSpeed,
        sunBlock,
        freqDip,
        eventTime,
        hash: posHash
      };
    }

    // Dynamic solar generation per plant on specific date
    function getPlantDateGeneration(plantId, dateVal) {
      const node = RADAR_NODES[plantId];
      if (!node) return 5.0;
      if (!dateVal) dateVal = document.getElementById('dateSelect') ? document.getElementById('dateSelect').value : '2026-01-06';

      if (allData && allData.length > 0) {
        // Search direct rows for this plant
        const rows = allData.filter(r => r.location === plantId && r.datetime && r.datetime.startsWith(dateVal));
        if (rows.length > 0) {
          const peak = Math.max(...rows.map(r => r.ensemble || 0));
          if (peak > 0.5) return parseFloat(peak.toFixed(1));
        }
        // Fallback: scale rated capacity by date's fleet power level
        const dateRows = allData.filter(r => r.datetime && r.datetime.startsWith(dateVal));
        if (dateRows.length > 0) {
          const fleetPeak = Math.max(...dateRows.map(r => r.ensemble || 0));
          const scale = Math.max(0.65, Math.min(1.35, fleetPeak / 52.0));
          return parseFloat((node.capMW * scale).toFixed(1));
        }
      }
      return node.capMW;
    }

    // Calculate physical advance warning lead time for any plant under current scenario
    function getPlantLeadTime(plantId, scen) {
      const node = RADAR_NODES[plantId];
      if (!node || plantId === 13) {
        return { sec: 0, minStr: '+0.0 mins', subStr: 'Origin Advance Sensor · Cloud Hits L13 First' };
      }

      const speedKmh = scen.speedKmh || 13.8;
      const speedMs = speedKmh / 3.6;
      let distMeters = (node.distance || 0) * 1000;
      if (plantId === 14) distMeters = 250;

      const sec = Math.round(distMeters / speedMs);
      const mins = parseFloat((sec / 60).toFixed(1));
      return {
        sec,
        minStr: `+${mins} mins`,
        subStr: `${sec}s Advance Warning Before Cloud Hits L${plantId}`
      };
    }
"""

# Insert helpers right before selectPlantNode
if 'function getDateWeatherProfile(' not in content:
    content = content.replace('    // ── INTERACTIVE PLANT INSPECTOR WITH GSAP ──', helpers_code + '\n    // ── INTERACTIVE PLANT INSPECTOR WITH GSAP ──', 1)
    print("Added weather profiler and plant lead-time helper functions")

# Replace selectPlantNode with the complete dynamic date-specific & plant-specific version
old_select_plant = """    // ── INTERACTIVE PLANT INSPECTOR WITH GSAP ──
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
        if (node.role === 'sentinel') roleBadge.textContent = id === 13 ? '🛡️ PRIMARY ADVANCE STATION' : '🛡️ SECONDARY ADVANCE STATION';
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
        if (node.role === 'sentinel') roleDesc.textContent = 'Early-Warning Advance Sensor Station';
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
    }"""

new_select_plant = """    // ── INTERACTIVE PLANT INSPECTOR WITH GSAP (UNIQUE PER PLANT & DATE) ──
    function selectPlantNode(id, animate = true) {
      if (!RADAR_NODES[id]) return;
      selectedPlantId = id;
      const node = RADAR_NODES[id];
      const dateVal = document.getElementById('dateSelect') ? document.getElementById('dateSelect').value : '2026-01-06';
      const weather = getDateWeatherProfile(dateVal);
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

      // 1. Date-Specific Generation for this plant on this date
      const nominalMW = getPlantDateGeneration(id, dateVal);
      const sunPct = isShaded ? Math.max(8, 100 - (scen.sunBlockPct || 74)) : 100;
      const currentMW = (nominalMW * (sunPct / 100)).toFixed(1);

      // 2. Scenario-Specific Warning Lead Time for this plant (+8.2m Normal, +4.2m Storm, +14.8m Fog)
      const leadInfo = getPlantLeadTime(id, scen);

      // 3. Sensor Correlation
      let corrR = node.r || 0.85;
      if (scen.speedKmh > 20) corrR = Math.min(0.98, corrR + 0.04);
      else if (scen.speedKmh < 10) corrR = Math.max(0.65, corrR - 0.05);

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
        if (node.role === 'sentinel') roleBadge.textContent = id === 13 ? '🛡️ PRIMARY ADVANCE STATION' : '🛡️ SECONDARY ADVANCE STATION';
        else if (node.role === 'target') roleBadge.textContent = '☀️ MAIN SOLAR GENERATION ARRAY';
        else if (node.role === 'substation') roleBadge.textContent = '⚡ REGIONAL GRID INTERCONNECT';
        else roleBadge.textContent = '🌊 COASTAL PV FACILITY';
      }

      if (plantTitle) plantTitle.textContent = `${node.name} · (${dateVal})`;
      if (location) location.textContent = `Elevation: ${node.alt}m MSL · Inverter Array ${id} · Rated: ${node.capMW} MWp · Date Observed: ${nominalMW} MW`;

      if (statusBadge && statusText) {
        if (isShaded) {
          statusBadge.classList.add('shaded');
          statusText.textContent = `⚠️ CLOUD SHADOWED (-${scen.sunBlockPct || 74}%) · EVENT AT ${weather.eventTime}`;
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
      if (sunSub) sunSub.textContent = isShaded ? `Cloud Shadow Ingress: Loss of ${(nominalMW - parseFloat(currentMW)).toFixed(1)} MW` : `Clear Sky Irradiance on ${dateVal}`;

      if (leadVal) leadVal.textContent = leadInfo.minStr;
      if (leadSub) leadSub.textContent = leadInfo.subStr;

      if (syncVal) syncVal.textContent = `${Math.round(corrR * 100)}%`;
      if (syncSub) syncSub.textContent = `Sensor Match (r = ${corrR.toFixed(2)}) with L13`;

      if (azimuth) azimuth.textContent = `${node.ori}° (${node.ori === 270 ? 'West Facing Sentinel' : (node.ori === 180 ? 'South Facing Fixed' : 'Southeast Facing')})`;
      if (bessStatus) bessStatus.textContent = isShaded ? '⚡ Full Battery Injection Active (Power Restored)' : '🟢 Battery Standby · Pre-emptive Ramp Ready';
      if (distance) distance.textContent = id === 13 ? '0.0 km (Westmost Reference Sensor)' : `${node.distance.toFixed(2)} km Downwind of L13`;
      if (roleDesc) {
        if (node.role === 'sentinel') roleDesc.textContent = 'Early-Warning Advance Sensor Station';
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
    }"""

if old_select_plant in content:
    content = content.replace(old_select_plant, new_select_plant, 1)
    print("Replaced selectPlantNode with dynamic per-plant & per-date version!")
else:
    print("Could not match exact old_select_plant block, checking alternative pattern")

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Saved step 1 of dynamic date scenarios!")
