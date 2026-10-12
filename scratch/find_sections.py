with open('frontend/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
for i, line in enumerate(lines, 1):
    l = line.strip()
    if ('class="tab-btn"' in l) or ('id="view' in l) or ('id="tab' in l) or ('id="cloud' in l) or ('id="radar' in l) or ('btnRadarSimPlay' in l) or ('radar-hud' in l):
        print(f"{i}: {l[:120]}")
