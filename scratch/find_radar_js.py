with open('frontend/index.html', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if 'cloudRadarCanvas' in line or 'drawRadarCanvas' in line or 'toggleRadarSim' in line or 'radarPlantNodes' in line or 'setCloudScenario' in line:
            print(f"{i}: {line.strip()[:100]}")
