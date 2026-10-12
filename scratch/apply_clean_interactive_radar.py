import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add GSAP script tag in <head> if not present
if 'gsap.min.js' not in content:
    target_tag = '<script src="https://cdn.jsdelivr.net/npm/papaparse@5.4.1/papaparse.min.js"></script>'
    replacement = target_tag + '\n  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>'
    content = content.replace(target_tag, replacement, 1)
    print("Added GSAP script tag")

# 2. Add / Update CSS
css_addon = """
    /* Tactical HUD Badges on Canvas - Hide floating countdown overlay (replay window) */
    .radar-hud-countdown {
      display: none !important;
    }

    .radar-hud-wind {
      position: absolute;
      bottom: 14px;
      left: 14px;
      background: rgba(255, 255, 255, 0.96);
      border: 1px solid #cbd5e1;
      padding: 7px 12px;
      border-radius: 8px;
      font-size: 11px;
      display: flex;
      align-items: center;
      gap: 8px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
      backdrop-filter: blur(4px);
    }

    /* Interactive Plant Quick-Select Chips Bar */
    .radar-plant-chips-bar {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 14px;
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 10px;
      margin-bottom: 12px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.03);
      overflow-x: auto;
    }

    .chips-label {
      font-size: 10.5px;
      font-weight: 800;
      color: #64748b;
      letter-spacing: 0.5px;
      white-space: nowrap;
      display: flex;
      align-items: center;
      gap: 5px;
    }

    .radar-plant-chips {
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
    }

    .plant-chip {
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 11px;
      font-family: 'JetBrains Mono', monospace;
      font-weight: 700;
      border: 1px solid #cbd5e1;
      background: #f8fafc;
      color: #334155;
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      display: inline-flex;
      align-items: center;
      gap: 4px;
      user-select: none;
    }

    .plant-chip:hover {
      border-color: #0284c7;
      color: #0284c7;
      background: #f0f9ff;
      transform: translateY(-1px);
    }

    .plant-chip.active {
      background: #0284c7 !important;
      color: #ffffff !important;
      border-color: #0284c7 !important;
      box-shadow: 0 2px 8px rgba(2, 132, 199, 0.35);
      transform: translateY(-1px);
    }

    .plant-chip.sentinel {
      border-color: #7dd3fc;
      background: #f0f9ff;
      color: #0369a1;
    }

    /* Ultra-Premium GSAP Plant Telemetry Inspector Card */
    .radar-inspector-card {
      background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 16px 20px;
      margin-top: 14px;
      box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.06), 0 2px 6px -1px rgba(15, 23, 42, 0.04);
      position: relative;
      overflow: hidden;
    }

    .radar-inspector-card::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: linear-gradient(90deg, #0284c7, #38bdf8, #10b981);
    }

    .inspector-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 14px;
      gap: 12px;
      flex-wrap: wrap;
    }

    .inspector-title-wrap {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .inspector-badge {
      font-size: 9.5px;
      font-weight: 800;
      letter-spacing: 0.6px;
      text-transform: uppercase;
      font-family: 'JetBrains Mono', monospace;
      color: #0284c7;
      background: #e0f2fe;
      padding: 2.5px 8px;
      border-radius: 4px;
      width: fit-content;
      border: 1px solid #bae6fd;
    }

    .inspector-title {
      font-size: 15px;
      font-weight: 800;
      color: #0f172a;
      letter-spacing: -0.2px;
    }

    .inspector-loc {
      font-size: 11.5px;
      color: #64748b;
    }

    .inspector-status-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 5px 12px;
      border-radius: 6px;
      background: #dcfce7;
      color: #15803d;
      border: 1px solid #bbf7d0;
      font-size: 11px;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
      transition: all 0.25s ease;
    }

    .inspector-status-badge.shaded {
      background: #fee2e2;
      color: #b91c1c;
      border-color: #fecaca;
    }

    .status-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: currentColor;
      box-shadow: 0 0 6px currentColor;
    }

    .inspector-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin-bottom: 14px;
    }

    .inspector-metric {
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: 12px 14px;
      display: flex;
      flex-direction: column;
      gap: 4px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
      transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .inspector-metric:hover {
      border-color: #cbd5e1;
      transform: translateY(-1px);
    }

    .metric-lbl {
      font-size: 10px;
      font-weight: 700;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.4px;
    }

    .metric-val {
      font-size: 18px;
      font-weight: 800;
      font-family: 'JetBrains Mono', monospace;
      color: #0f172a;
      letter-spacing: -0.5px;
    }

    .metric-sub {
      font-size: 10px;
      font-weight: 600;
      color: #0284c7;
      font-family: 'JetBrains Mono', monospace;
    }

    .metric-progress-bg {
      width: 100%;
      height: 5px;
      background: #e2e8f0;
      border-radius: 3px;
      margin-top: 4px;
      overflow: hidden;
    }

    .metric-progress-bar {
      height: 100%;
      background: #10b981;
      border-radius: 3px;
      transition: width 0.3s ease, background 0.3s ease;
    }

    .inspector-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-top: 12px;
      border-top: 1px solid #e2e8f0;
      font-size: 11px;
      color: #475569;
      flex-wrap: wrap;
      gap: 10px;
    }

    .inspector-spec-item {
      display: inline-flex;
      align-items: center;
      gap: 5px;
    }
"""

# Replace existing radar HUD CSS block
old_hud_css_pattern = re.compile(r'/\* Tactical HUD Badges on Canvas \*/\s*\.radar-hud-countdown\s*\{[^}]+\}\s*\.radar-hud-wind\s*\{[^}]+\}', re.DOTALL)
if old_hud_css_pattern.search(content):
    content = old_hud_css_pattern.sub(css_addon, content)
    print("Replaced HUD CSS with premium GSAP Inspector & Chips CSS")
else:
    print("Could not match old HUD CSS pattern directly, checking alternative")

# 3. Add Plant Chips Bar and Inspector Card in HTML for viewMap
html_chips_and_inspector = """            <!-- Interactive Plant Selection Strip -->
            <div class="radar-plant-chips-bar">
              <span class="chips-label">🎯 CLICK TO INSPECT PLANT:</span>
              <div class="radar-plant-chips" id="radarPlantChips">
                <button class="plant-chip sentinel active" id="chip-13" onclick="selectPlantNode(13)">🛡️ L13 Watchman</button>
                <button class="plant-chip sentinel" id="chip-14" onclick="selectPlantNode(14)">🛡️ L14 Watchman</button>
                <button class="plant-chip" id="chip-1" onclick="selectPlantNode(1)">L1</button>
                <button class="plant-chip" id="chip-2" onclick="selectPlantNode(2)">L2</button>
                <button class="plant-chip" id="chip-3" onclick="selectPlantNode(3)">L3</button>
                <button class="plant-chip" id="chip-4" onclick="selectPlantNode(4)">L4</button>
                <button class="plant-chip" id="chip-5" onclick="selectPlantNode(5)">L5</button>
                <button class="plant-chip" id="chip-6" onclick="selectPlantNode(6)">L6</button>
                <button class="plant-chip" id="chip-7" onclick="selectPlantNode(7)">L7</button>
                <button class="plant-chip" id="chip-8" onclick="selectPlantNode(8)">L8</button>
                <button class="plant-chip" id="chip-9" onclick="selectPlantNode(9)">L9</button>
                <button class="plant-chip" id="chip-10" onclick="selectPlantNode(10)">L10</button>
                <button class="plant-chip" id="chip-11" onclick="selectPlantNode(11)">L11</button>
                <button class="plant-chip" id="chip-12" onclick="selectPlantNode(12)">L12</button>
                <button class="plant-chip" id="chip-15" onclick="selectPlantNode(15)">L15 Coastal</button>
                <button class="plant-chip" id="chip-16" onclick="selectPlantNode(16)">L16 Coastal</button>
                <button class="plant-chip" id="chip-17" onclick="selectPlantNode(17)">⚡ L17 Substation</button>
              </div>
            </div>

            <!-- High-Definition Tactical Canvas Wrap -->"""

content = content.replace('            <!-- High-Definition Tactical Canvas Wrap -->', html_chips_and_inspector, 1)

# Inspector Card HTML to insert after canvas wrap
inspector_card_html = """              <!-- Floating Wind Compass Indicator -->
              <div class="radar-hud-wind">
                <span style="font-size:13px;">🧭</span>
                <div>
                  <div style="font-weight:700; color:#0f172a;" id="hudWindVectorText">WNW → ESE (108°) at 13.8 km/h</div>
                  <div style="font-size:9.5px; color:#64748b;">Blowing East from Mountains to Coast</div>
                </div>
              </div>
            </div>

            <!-- Ultra-Premium GSAP Plant Telemetry Inspector Card -->
            <div class="radar-inspector-card" id="plantInspectorCard">
              <div class="inspector-header">
                <div class="inspector-title-wrap">
                  <span class="inspector-badge" id="inspRoleBadge">🛡️ WATCHMAN STATION 1</span>
                  <h4 class="inspector-title" id="inspPlantTitle">Plant L13 · West Watchman Sensor Array</h4>
                  <span class="inspector-loc" id="inspLocation">West Foothills Ridge · 310m Elevation · Direct Western View</span>
                </div>
                <div class="inspector-status-badge" id="inspStatusBadge">
                  <span class="status-dot"></span>
                  <span id="inspStatusText">FULL SOLAR PRODUCTION</span>
                </div>
              </div>
              <div class="inspector-grid">
                <div class="inspector-metric">
                  <span class="metric-lbl">Live Solar Output</span>
                  <span class="metric-val" id="inspMWVal">5.2 MW</span>
                  <div class="metric-progress-bg">
                    <div class="metric-progress-bar" id="inspMWBar" style="width: 100%;"></div>
                  </div>
                </div>
                <div class="inspector-metric">
                  <span class="metric-lbl">Sunlight Level</span>
                  <span class="metric-val" id="inspSunVal">100%</span>
                  <span class="metric-sub" id="inspSunSub">Full Irradiance (Clear Sky)</span>
                </div>
                <div class="inspector-metric">
                  <span class="metric-lbl">Advance Warning Lead</span>
                  <span class="metric-val" id="inspLeadVal">+0.0 mins</span>
                  <span class="metric-sub" id="inspLeadSub">Leading Edge Origin Sensor</span>
                </div>
                <div class="inspector-metric">
                  <span class="metric-lbl">Watchman Sensor Sync</span>
                  <span class="metric-val" id="inspSyncVal">100%</span>
                  <span class="metric-sub" id="inspSyncSub">Direct Benchmark (r = 1.00)</span>
                </div>
              </div>
              <div class="inspector-footer">
                <div class="inspector-spec-item">📐 <b>Panel Azimuth:</b> <span id="inspAzimuth">270° (West Facing)</span></div>
                <div class="inspector-spec-item">⚡ <b>Defense Link:</b> <span id="inspBessStatus">Armed for Sub-100ms Fast Ramp</span></div>
                <div class="inspector-spec-item">📍 <b>Distance to L13:</b> <span id="inspDistance">0.0 km (Origin Benchmark)</span></div>
                <div class="inspector-spec-item">🏭 <b>Plant Role:</b> <span id="inspRoleDesc">Early-Warning Sentinel Array</span></div>
              </div>
            </div>"""

old_wind_and_end = """              <!-- Floating Wind Compass Indicator -->
              <div class="radar-hud-wind">
                <span style="font-size:13px;">🧭</span>
                <div>
                  <div style="font-weight:700; color:#0f172a;" id="hudWindVectorText">WNW → ESE (108°) at 13.8 km/h</div>
                  <div style="font-size:9.5px; color:#64748b;">Blowing East from Mountains to Coast</div>
                </div>
              </div>
            </div>"""

content = content.replace(old_wind_and_end, inspector_card_html, 1)
print("Added Plant Chips and Inspector HTML")

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Saved HTML updates successfully!")
