with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_gen_func = """    // Dynamic solar generation per plant on specific date
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
    }"""

new_gen_func = """    // Dynamic solar generation per plant on specific date (MW calibrated to plant rated capacity)
    function getPlantDateGeneration(plantId, dateVal) {
      const node = RADAR_NODES[plantId];
      if (!node) return 5.0;
      if (!dateVal) dateVal = document.getElementById('dateSelect') ? document.getElementById('dateSelect').value : '2026-01-06';

      // Evaluate the solar irradiance index for this specific date from allData
      let sunIndex = 0.88; // Default ~88% of rated peak
      if (allData && allData.length > 0) {
        const dateRows = allData.filter(r => r.datetime && r.datetime.startsWith(dateVal));
        if (dateRows.length > 0) {
          const maxPeak = Math.max(...dateRows.map(r => r.ensemble || 0));
          // Normalize maxPeak against fleet scale (~800kW max)
          sunIndex = Math.max(0.60, Math.min(1.0, maxPeak / 750.0));
        }
      }

      // Small deterministic per-plant variation for this date
      const hash = (dateVal.charCodeAt(dateVal.length - 1) * 7 + plantId * 13) % 17;
      const plantJitter = ((hash - 8) / 8) * 0.08; // +/- 8%
      const effectiveIndex = Math.max(0.55, Math.min(1.0, sunIndex + plantJitter));

      return parseFloat((node.capMW * effectiveIndex).toFixed(1));
    }"""

if old_gen_func in content:
    content = content.replace(old_gen_func, new_gen_func, 1)
    print("Updated getPlantDateGeneration to realistic MW scaling")
else:
    print("Could not match exact old_gen_func block")

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Saved updated MW scaling!")
