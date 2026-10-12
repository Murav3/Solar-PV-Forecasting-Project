# Python script to replace complex/mysterious jargon with crystal-clear words
import re

target_file = r"c:\Users\harin\Downloads\R_FINAL_REVIEW\Solar-PV-Forecasting-Project\frontend\index.html"

with open(target_file, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Strategic Doctrine Cards
content = content.replace(
    '🛡️ Pre-emptive Defense: Spatio-Temporal Radar',
    '🛡️ Early-Warning Defense: Plant L13 Watchman System'
)
content = content.replace(
    '+8.2 MIN PRE-DISPATCH',
    '+8.2 MIN ADVANCE WARNING'
)
content = content.replace(
    'Advance Lead-Lag Notice',
    'Advance Warning Time'
)
content = content.replace(
    'Lead Reaction Time',
    'Warning Time (Blind)'
)
content = content.replace(
    'By interconnecting all 17 PV arrays into a distributed Doppler network, <b>Plant L13 (West Foothills)</b> acts as an upwind sentinel. \n                The moment irradiance drops at L13, cloud velocity (<b style="color:#0284c7;">13.8 km/h at 108°</b>) is calculated, providing an \n                <b style="color:#0284c7;">8.2-minute lead-time window</b>. Battery storage pre-ramps <i>before</i> the shadow reaches L1–L4, keeping grid frequency pinned at <b>60.00 Hz</b>.',
    'Instead of leaving plants blind, <b>Plant L13 (West Foothills)</b> acts like a <b>watchman</b>. \n                The moment a cloud hits L13, the system calculates cloud speed (<b style="color:#0284c7;">13.8 km/h</b>) and gives an \n                <b style="color:#0284c7;">8.2-minute heads-up warning</b>. Battery storage turns on <i>before</i> the cloud reaches Plants L1–L4, keeping grid power safe and frequency locked at <b>60.00 Hz</b>.'
)

# 2. Console Header
content = content.replace(
    '🛰️ Spatio-Temporal Cloud Velocity Doppler & Lead-Lag Tracking Console',
    '🛰️ Cloud Velocity Early-Warning Radar Console'
)
content = content.replace(
    'Live spatial cross-correlation and cloud transient propagation across 17 distributed PV arrays in the Hualien regional corridor',
    'Live cloud movement tracking and early warning network across all 17 solar plants in the regional grid'
)

# 3. Scenario Buttons
content = content.replace(
    '⛅ Mountain Cumulus (13.8 km/h · 8.2m Lag)',
    '⛅ Normal Cloud Day (13.8 km/h · 8.2m Warning)'
)
content = content.replace(
    '⚡ Cold Front Storm (26.5 km/h · 4.2m Lag)',
    '⚡ Fast Storm Day (26.5 km/h · 4.2m Warning)'
)
content = content.replace(
    '🌊 Coastal Marine Layer (7.5 km/h · 14.8m Lag)',
    '🌊 Slow Heavy Fog (7.5 km/h · 14.8m Warning)'
)
content = content.replace(
    '📅 Replay Selected Date Transients',
    '📅 Replay Selected Date Cloud Event'
)

# 4. Controls & HUDs
content = content.replace(
    'Simulate Transient Event',
    'Simulate Cloud Movement'
)
content = content.replace(
    'Transient Propagation Scrubber:',
    'Cloud Position Slider:'
)
content = content.replace(
    'Phase 1: Upwind Optical Inception (T - 8.2m)',
    'Phase 1: Cloud Detected at West Watchman (8 min Warning)'
)
content = content.replace(
    'ETA Downwind: 08:12',
    'Time Until Impact: 08:12'
)
content = content.replace(
    'DOWNWIND IMPACT ETA',
    'TIME UNTIL CLOUD HITS SOLAR PARK'
)
content = content.replace(
    'Lead Offset: +492s | Cross-Correlation r = 0.89',
    'Advance Warning: 8.2 mins | Sensor Match: 89%'
)
content = content.replace(
    'Mountain Foothill to Pacific Ocean Corridor',
    'Blowing East from Mountains to Coast'
)

# 5. Split Charts
content = content.replace(
    '🔴 Unmitigated Grid (Without Lead-Lag Tracking)',
    '🔴 Without Early Warning (Sudden Cloud Shock)'
)
content = content.replace(
    'Solar plunges without notice. BESS reacts 4 minutes late. Frequency breaches safety limits.',
    'Solar drops without notice. Batteries react 4 minutes late. Grid frequency crashes to 59.72 Hz.'
)
content = content.replace(
    '🟢 Pre-emptively Mitigated (With Spatio-Temporal Lead-Lag)',
    '🟢 With Early Warning (Pre-emptive Defense)'
)
content = content.replace(
    'BESS pre-ramps 8 minutes in advance. Total grid injection remains 100% constant. Zero frequency dip.',
    'Batteries turn on 8 minutes in advance. Total grid power stays 100% constant. Zero frequency drop.'
)

# 6. Table Header & Columns
content = content.replace(
    'Cross-Site Lead-Lag Empirical Correlation Matrix (τ_ij)',
    'Plant-to-Plant Early Warning Delay Table (Lead-Lag Time)'
)
content = content.replace(
    'Measured time delays, spatial distance, and cross-correlation coefficients between Sentinel L13 and downstream arrays',
    'Measured advance warning time and sensor match between Watchman Plant L13 and all other solar plants'
)
content = content.replace(
    '<th>Upwind Sentinel Sensor</th>',
    '<th>Watchman Sensor Plant</th>'
)
content = content.replace(
    '<th>Downwind Target Array</th>',
    '<th>Protected Solar Plant</th>'
)
content = content.replace(
    '<th>Physical Ground Separation</th>',
    '<th>Distance Apart</th>'
)
content = content.replace(
    '<th>Lead-Lag Time Delay (τ)</th>',
    '<th>Advance Warning Time</th>'
)
content = content.replace(
    '<th>Cross-Correlation (r)</th>',
    '<th>Sensor Match Accuracy</th>'
)

# 7. JavaScript Texts
content = content.replace(
    'name: "Mountain Cumulus"',
    'name: "Normal Cloud Day"'
)
content = content.replace(
    'headingText: "WNW → ESE (108°) at 13.8 km/h"',
    'headingText: "Wind: 13.8 km/h Blowing East"'
)
content = content.replace(
    'desc: "Orographic cumulus transient drifting off the Central Mountain Range toward Shoufeng Basin."',
    'desc: "A typical medium-speed cloud drifting off the mountains toward the solar park."'
)
content = content.replace(
    'name: "Cold Front Storm"',
    'name: "Fast Storm Day"'
)
content = content.replace(
    'headingText: "NW → SE (115°) at 26.5 km/h"',
    'headingText: "Fast Storm Wind: 26.5 km/h Blowing East"'
)
content = content.replace(
    'desc: "Rapid convective squall line with high optical attenuation and steep ramp-down transients."',
    'desc: "A fast-moving storm squall line rushing in at twice the normal speed."'
)
content = content.replace(
    'name: "Coastal Marine Layer"',
    'name: "Slow Heavy Fog"'
)
content = content.replace(
    'headingText: "W → E (95°) at 7.5 km/h"',
    'headingText: "Gentle Sea Breeze: 7.5 km/h Blowing East"'
)
content = content.replace(
    'desc: "Broad, slow-moving marine stratus inversion layer producing gradual spatial shadowing."',
    'desc: "A thick morning fog slowly creeping inland from the coast."'
)
content = content.replace(
    'name: `Observed Date (${dateVal})`',
    'name: `Selected Date Cloud (${dateVal})`'
)

# Phase badge updates in JS
content = content.replace(
    'phaseBadge.textContent = `Phase 1: Upwind Optical Inception (T - ${minsLeft.split(\' \')[0]})`;',
    'phaseBadge.textContent = `Phase 1: Cloud Detected at West Watchman (Plant L13)`;'
)
content = content.replace(
    'phaseBadge.textContent = `Phase 1: Upwind Optical Inception (T - ${scen.leadTimeStr.split(\' \')[0]})`;',
    'phaseBadge.textContent = `Phase 1: Cloud Detected at West Watchman (Plant L13)`;'
)
content = content.replace(
    'phaseBadge.textContent = `Phase 2: Lead-Lag In-Flight Vector (BESS Pre-Dispatch Active)`;',
    'phaseBadge.textContent = `Phase 2: Cloud In-Flight · Batteries Turning On`;'
)
content = content.replace(
    'phaseBadge.textContent = `Phase 3: Frontal Shadow Ingress at Main Park L1–L4`;',
    'phaseBadge.textContent = `Phase 3: Cloud Over Panels · Full Battery Backup Active`;'
)
content = content.replace(
    'phaseBadge.textContent = `Phase 4: Full Mitigation Achieved (Frequency Locked at 60.00 Hz)`;',
    'phaseBadge.textContent = `Phase 4: Cloud Passed · Power Safe & 60.00 Hz Preserved`;'
)
content = content.replace(
    'if (cd) cd.textContent = `ETA Downwind: ${minsLeft}`;',
    'if (cd) cd.textContent = `Time Until Impact: ${minsLeft}`;'
)
content = content.replace(
    'if (cd) cd.textContent = `ETA Downwind: ${mm}:${ss}`;',
    'if (cd) cd.textContent = `Time Until Impact: ${mm}:${ss}`;'
)
content = content.replace(
    'if (cd) cd.textContent = `IMPACT OCCLUDED (T = 0)`;',
    'if (cd) cd.textContent = `CLOUD OVER PANELS (T = 0)`;'
)
content = content.replace(
    'if (cd) cd.textContent = `STABILIZED (+4.0m)`;',
    'if (cd) cd.textContent = `GRID SAFE (+4.0m)`;'
)
content = content.replace(
    'if (hudTimer) hudTimer.textContent = `TRANSIENT CLEARED`;',
    'if (hudTimer) hudTimer.textContent = `CLOUD CLEARED`;'
)

# Canvas string updates
content = content.replace(
    'const badgeText = isL13 ? \'🛰️ SENTINEL-1 (UPWIND)\' : \'🛰️ SENTINEL-2\';',
    'const badgeText = isL13 ? \'🛡️ WATCHMAN PLANT L13\' : \'🛡️ WATCHMAN PLANT L14\';'
)
content = content.replace(
    'const ghiText = isShaded ? `GHI: 214 W/m² (-76%)` : `GHI: 896 W/m² (Nominal)`;',
    'const ghiText = isShaded ? `Sunlight Blocked (-76%)` : `Full Sun (Nominal)`;'
)
content = content.replace(
    'ctx.fillText(`TRANSIENT CORE: GHI < 220 W/m²`, cloudX - 65, cloudY - 6);',
    'ctx.fillText(`CLOUD SHADOW: Sunlight Blocked -74%`, cloudX - 85, cloudY - 6);'
)
content = content.replace(
    'ctx.fillText(`OPTICAL ATTENUATION: -74%`, cloudX - 60, cloudY + 8);',
    'ctx.fillText(`POWER DROP: -${scen.deltaMW} MW Fleet Transient`, cloudX - 85, cloudY + 8);'
)
content = content.replace(
    'ctx.fillText(`VECTOR: v = ${scen.speedKmh} km/h | θ = ${scen.headingDeg}° | τ = +${scen.leadTimeSec}s`, sX + 60, sY + 40);',
    'ctx.fillText(`WIND: ${scen.speedKmh} km/h Blowing East | ${scen.leadTimeStr} Warning Window`, sX + 60, sY + 40);'
)
content = content.replace(
    '{ r: 90, label: "Isochrone T - 6.0m (0.6 km)", color: "rgba(2, 132, 199, 0.28)" }',
    '{ r: 90, label: "Warning Line: 6 mins before impact (0.6 km)", color: "rgba(2, 132, 199, 0.28)" }'
)
content = content.replace(
    '{ r: 180, label: "Isochrone T - 3.0m (1.2 km)", color: "rgba(2, 132, 199, 0.38)" }',
    '{ r: 180, label: "Warning Line: 3 mins before impact (1.2 km)", color: "rgba(2, 132, 199, 0.38)" }'
)
content = content.replace(
    '{ r: 275, label: "Isochrone T = 0.0m Arrival (1.85 km - L1 Array Front)", color: "rgba(220, 38, 38, 0.55)", bold: true }',
    '{ r: 275, label: "Impact Line: Cloud Reaches Main Solar Park (0 min)", color: "rgba(220, 38, 38, 0.55)", bold: true }'
)
content = content.replace(
    '{ r: 430, label: "Isochrone T + 12.0m Downstream Corridor (2.8 km)", color: "rgba(100, 116, 139, 0.25)" }',
    '{ r: 430, label: "Recovery Line: Cloud Leaving Solar Park (2.8 km)", color: "rgba(100, 116, 139, 0.25)" }'
)
content = content.replace(
    'ctx.fillText(\'● LIVE DOPPLER RADAR\', 28, 24);',
    'ctx.fillText(\'● LIVE RADAR TRACKING\', 28, 24);'
)
content = content.replace(
    'ctx.fillText(\'CORRIDOR: Hualien Basin  |  ALGO: Lead-Lag Cross-Correlation (τ)\', 165, 24);',
    'ctx.fillText(\'CORRIDOR: 17 Solar Plants  |  SYSTEM: Early Warning Network\', 165, 24);'
)

with open(target_file, "w", encoding="utf-8") as f:
    f.write(content)

print("SUCCESS: Jargon replaced with simple, crystal-clear terms!")
