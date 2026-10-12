import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add manualScenarioOverride variable
if 'let manualScenarioOverride = false;' not in content:
    content = content.replace(
        "let currentRadarScenario = 'moderate';",
        "let currentRadarScenario = 'moderate';\n    let manualScenarioOverride = false;"
    )

# 1. Update setCloudScenario to track manual override
old_set_scen = """    // ── SCENARIO PRESET HANDLER ──
    function setCloudScenario(scenKey) {
      currentRadarScenario = scenKey;"""

new_set_scen = """    // ── SCENARIO PRESET HANDLER ──
    function setCloudScenario(scenKey) {
      currentRadarScenario = scenKey;
      manualScenarioOverride = (scenKey !== 'dateSpecific');"""

if old_set_scen in content:
    content = content.replace(old_set_scen, new_set_scen, 1)

# 2. Update getDateSpecificScenario
old_get_date_scen_pattern = re.compile(r'function getDateSpecificScenario\(\)\s*\{[\s\S]*?return\s*\{[\s\S]*?\};\s*\}', re.DOTALL)

new_get_date_scen = """function getDateSpecificScenario() {
      const dateVal = document.getElementById('dateSelect') ? document.getElementById('dateSelect').value : '2026-01-06';
      const weather = getDateWeatherProfile(dateVal);
      const rows = allData.filter(r => r.datetime && r.datetime.startsWith(dateVal));
      
      let peakVal = 48.0;
      if (rows.length > 0) {
        peakVal = Math.max(...rows.map(r => r.ensemble || 0));
      }
      
      const speed = weather.speedKmh;
      const leadSec = weather.baseL1LeadSec;
      const mm = String(Math.floor(leadSec / 60)).padStart(2, '0');
      const ss = String(leadSec % 60).padStart(2, '0');
      const pMax = Math.round(peakVal);
      const pDrop = Math.max(12, Math.round(peakVal * (weather.sunBlock / 100)));
      const pShaded = Math.max(4, pMax - pDrop);
      const stepSpeed = weather.archetype === 'fast' ? 1.45 : (weather.archetype === 'slow' ? 0.30 : 0.65);
      const dipFreq = weather.freqDip;

      return {
        name: `${weather.title} (${dateVal})`,
        speedKmh: speed,
        simSpeedStep: stepSpeed,
        headingDeg: weather.archetype === 'fast' ? 115 : (weather.archetype === 'slow' ? 95 : 108),
        headingText: `Wind: ${speed} km/h Blowing East · ${weather.title} (Cloud Event at ${weather.eventTime})`,
        leadTimeSec: leadSec,
        leadTimeStr: `${mm}m ${ss}s`,
        corrR: weather.archetype === 'fast' ? "0.94" : (weather.archetype === 'slow' ? "0.81" : "0.89"),
        deltaMW: pDrop,
        cloudRadius: weather.archetype === 'fast' ? 195 : (weather.archetype === 'slow' ? 235 : 155),
        cloudAspect: weather.archetype === 'fast' ? 1.55 : (weather.archetype === 'slow' ? 1.15 : 1.25),
        cloudDarkness: weather.archetype === 'fast' ? 0.72 : (weather.archetype === 'slow' ? 0.30 : 0.45),
        sunBlockPct: weather.sunBlock,
        cloudStartY: weather.archetype === 'fast' ? 120 : (weather.archetype === 'slow' ? 180 : 160),
        cloudTargetY: weather.archetype === 'fast' ? 370 : (weather.archetype === 'slow' ? 250 : 320),
        freqDip: dipFreq,
        freqBadgeText: weather.archetype === 'fast' ? `FREQ CRASH: ${dipFreq.toFixed(2)} Hz` : (weather.archetype === 'slow' ? `FREQ SAG: ${dipFreq.toFixed(2)} Hz` : `FREQ FAULT: ${dipFreq.toFixed(2)} Hz`),
        freqBadgeColor: weather.archetype === 'fast' ? "#991b1b" : (weather.archetype === 'slow' ? "#b45309" : "#dc2626"),
        freqBadgeBg: weather.archetype === 'fast' ? "#fecaca" : (weather.archetype === 'slow' ? "#fef3c7" : "#fee2e2"),
        curveSolar: [pMax, pMax, pMax, Math.round(pMax * 0.85), pShaded, pShaded, Math.round(pShaded * 1.3), Math.round(pMax * 0.6), Math.round(pMax * 0.9)],
        curveDelayedBess: [0, 0, 0, 0, 0, Math.round(pDrop * 0.15), Math.round(pDrop * 0.5), Math.round(pDrop * 0.85), Math.round(pDrop * 0.2)],
        curvePreBess: [0, Math.round(pDrop * 0.2), Math.round(pDrop * 0.6), pDrop, pDrop, pDrop, Math.round(pDrop * 0.9), Math.round(pDrop * 0.6), Math.round(pDrop * 0.15)],
        curveFreqUnmit: [60.00, 60.00, 60.00, 59.98, dipFreq, parseFloat((dipFreq + 0.03).toFixed(2)), 59.88, 59.96, 60.00],
        desc: `Meteorological profile for ${dateVal}: ${weather.title} with simulated cloud passage event at ${weather.eventTime}.`
      };
    }"""

if old_get_date_scen_pattern.search(content):
    content = old_get_date_scen_pattern.sub(new_get_date_scen, content)
    print("Updated getDateSpecificScenario")

# 3. Add updateAdvanceWarningTable
update_table_func = """
    // ── DYNAMIC ADVANCE WARNING TABLE SYNC ──
    function updateAdvanceWarningTable() {
      const scen = getActiveScenario();
      const speedMs = scen.speedKmh / 3.6;
      const targets = [
        { id: 1, dist: 1.85 },
        { id: 2, dist: 1.95 },
        { id: 4, dist: 2.20 },
        { id: 8, dist: 2.35 },
        { id: 15, dist: 14.20 },
        { id: 17, dist: 9.80 }
      ];
      const table = document.querySelector('.matrix-table-card tbody');
      if (!table) return;
      const rows = table.querySelectorAll('tr');
      targets.forEach((t, i) => {
        if (rows[i]) {
          const sec = Math.round((t.dist * 1000) / speedMs);
          const min = (sec / 60).toFixed(1);
          const tdTime = rows[i].children[3];
          if (tdTime) {
            tdTime.innerHTML = `<b style="color:#0284c7; font-family:'JetBrains Mono',monospace;">+${sec} sec (${min} min)</b>`;
          }
        }
      });
    }
"""

if 'function updateAdvanceWarningTable(' not in content:
    content = content.replace('    function setCloudScenario(scenKey) {', update_table_func + '\n    function setCloudScenario(scenKey) {', 1)
    print("Added updateAdvanceWarningTable function")

# 4. Update renderMapView to auto-assign scenario based on date
old_render_map_view = """    // ── MAIN ENTRY POINT FOR TAB 4 ──
    function renderMapView() {
      resizeRadarCanvas();
      initRadarCanvasListeners();

      // Synchronize Active Date Telemetry Badges
      const dateVal = document.getElementById('dateSelect').value || '2026-01-06';
      const dt = new Date(dateVal);
      const dayName = isNaN(dt) ? '' : dt.toLocaleDateString('en-US', { weekday: 'short' });
      const rows = allData.filter(r => r.datetime && r.datetime.startsWith(dateVal));
      const peakVal = rows.length ? Math.max(...rows.map(r => r.ensemble || 0)).toFixed(1) : '52.4';
      
      const dateBadge = document.getElementById('radarActiveDateBadge');
      if (dateBadge) {
        dateBadge.innerHTML = `📅 Active Date: <b>${dateVal} (${dayName})</b> · All 17 Plants Synced`;
      }
      const profBadge = document.getElementById('radarDateProfileBadge');
      if (profBadge) {
        profBadge.textContent = `Observed Fleet Peak: ${peakVal} MW · ${rows.length.toLocaleString()} Data Points Available (${plantDatesMap['all']?.length || 124} Dates)`;
      }

      initSplitImpactCharts();
      syncScenarioUI();
      selectPlantNode(selectedPlantId || 13, false);
      drawTacticalRadarCanvas();
      
      if (!radarAnimFrameId) {
        startRadarLoop();
      }
    }"""

new_render_map_view = """    // ── MAIN ENTRY POINT FOR TAB 4 (DYNAMIC PER DATE & SCENARIO) ──
    function renderMapView() {
      resizeRadarCanvas();
      initRadarCanvasListeners();

      const dateVal = document.getElementById('dateSelect') ? document.getElementById('dateSelect').value : '2026-01-06';
      const dt = new Date(dateVal);
      const dayName = isNaN(dt) ? '' : dt.toLocaleDateString('en-US', { weekday: 'short' });
      const rows = allData.filter(r => r.datetime && r.datetime.startsWith(dateVal));
      const peakVal = rows.length ? Math.max(...rows.map(r => r.ensemble || 0)).toFixed(1) : '52.4';
      const weather = getDateWeatherProfile(dateVal);

      // Auto-assign date weather scenario preset if not manually locked
      if (!manualScenarioOverride || currentRadarScenario === 'dateSpecific') {
        currentRadarScenario = weather.archetype;
        ['mod', 'fast', 'slow', 'date'].forEach(k => {
          const btn = document.getElementById(`scen-${k}`);
          if (btn) btn.classList.remove('active');
        });
        const activeMap = { moderate: 'mod', fast: 'fast', slow: 'slow' };
        const btnEl = document.getElementById(`scen-${activeMap[weather.archetype]}`);
        if (btnEl) btnEl.classList.add('active');
      }

      const activeScen = getActiveScenario();

      const dateBadge = document.getElementById('radarActiveDateBadge');
      if (dateBadge) {
        dateBadge.innerHTML = `📅 Active Date: <b>${dateVal} (${dayName})</b> · Forecast: <b style="color:#0284c7;">${weather.title}</b> · Simulated Cloud Ingress: <b>${weather.eventTime}</b>`;
      }
      const profBadge = document.getElementById('radarDateProfileBadge');
      if (profBadge) {
        const l1Sec = Math.round(1850 / (activeScen.speedKmh / 3.6));
        const l17Sec = Math.round(9800 / (activeScen.speedKmh / 3.6));
        profBadge.textContent = `Fleet Peak: ${peakVal} MW · ${activeScen.speedKmh} km/h Wind · Lead Time: +${(l1Sec/60).toFixed(1)}m (L1) / +${(l17Sec/60).toFixed(1)}m (L17)`;
      }

      initSplitImpactCharts();
      syncScenarioUI();
      selectPlantNode(selectedPlantId || 13, false);
      updateAdvanceWarningTable();
      drawTacticalRadarCanvas();
      
      if (!radarAnimFrameId) {
        startRadarLoop();
      }
    }"""

if old_render_map_view in content:
    content = content.replace(old_render_map_view, new_render_map_view, 1)
    print("Updated renderMapView with auto date assignment")

# 5. In syncScenarioUI and setCloudScenario, call updateAdvanceWarningTable
content = content.replace(
    "initSplitImpactCharts();\n      drawTacticalRadarCanvas();\n    }",
    "initSplitImpactCharts();\n      updateAdvanceWarningTable();\n      drawTacticalRadarCanvas();\n    }"
)

# 6. In drawTacticalRadarCanvas, make node generation dynamic per date
old_canvas_node_gen = """        const nominalMW = node.capMW;
        const currentMW = isShaded ? (nominalMW * Math.max(0.05, 1 - (scen.sunBlockPct || 74) / 100)).toFixed(1) : nominalMW.toFixed(1);"""

new_canvas_node_gen = """        const dateVal = document.getElementById('dateSelect') ? document.getElementById('dateSelect').value : '2026-01-06';
        const nominalMW = getPlantDateGeneration(id, dateVal);
        const currentMW = isShaded ? (nominalMW * Math.max(0.05, 1 - (scen.sunBlockPct || 74) / 100)).toFixed(1) : nominalMW.toFixed(1);"""

if old_canvas_node_gen in content:
    content = content.replace(old_canvas_node_gen, new_canvas_node_gen, 1)
    print("Made canvas node generation dynamic per date")

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Saved full dynamic radar updates!")
