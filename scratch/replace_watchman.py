import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

replacements = [
    ("🛡️ Early-Warning Defense: Plant L13 Watchman System", "🛡️ Early-Warning Defense: Plant L13 Advance Detection System"),
    ("<b>Plant L13 (West Foothills)</b> acts like a <b>watchman</b>", "<b>Plant L13 (West Foothills)</b> acts as an <b>advance detection station</b>"),
    ("Phase 1: Cloud Detected at West Watchman (8 min Warning)", "Phase 1: Cloud Detected at West Advance Station (8 min Warning)"),
    ("Phase 1: Cloud Detected at West Watchman (Plant L13)", "Phase 1: Cloud Detected at West Advance Station (Plant L13)"),
    ("🛡️ L13 Watchman", "🛡️ L13 Advance Station"),
    ("🛡️ L14 Watchman", "🛡️ L14 Advance Station"),
    ("🛡️ WATCHMAN STATION 1", "🛡️ ADVANCE DETECTION STATION 1"),
    ("🛡️ PRIMARY WATCHMAN STATION", "🛡️ PRIMARY ADVANCE STATION"),
    ("🛡️ SECONDARY WATCHMAN STATION", "🛡️ SECONDARY ADVANCE STATION"),
    ("Plant L13 · West Watchman Sensor Array", "Plant L13 · West Foothills Advance Array"),
    ("Plant L13 · West Watchman Station 1", "Plant L13 · West Advance Station 1"),
    ("Plant L14 · West Watchman Station 2", "Plant L14 · West Advance Station 2"),
    ("Watchman Sensor Sync", "Advance Sensor Sync"),
    ("Watchman Sensor Station", "Advance Sensor Station"),
    ("Watchman Sensor Plant", "Advance Sensor Plant"),
    ("between Watchman Plant L13", "between Advance Station Plant L13"),
    ("from Watchman L13", "from Advance Station L13"),
    ("to Watchman L13", "to Advance Station L13"),
    ("with Watchman", "with Advance Station"),
    ("Active Watchman", "Active Advance Station"),
    ("ctx.fillText('WATCHMAN', nx, ny - rad - 5);", "ctx.fillText('ADVANCE', nx, ny - rad - 5);"),
    ("// Watchman Arrays", "// Advance Arrays"),
    ("Early-Warning Cloud Velocity Sentinel", "Early-Warning Advance Sensor Station")
]

for old, new in replacements:
    if old in text:
        text = text.replace(old, new)
        print(f"Replaced: {old[:50]} -> {new[:50]}")
    else:
        print(f"NOT FOUND: {old[:50]}")

# Case-insensitive check for any remaining 'watchman'
remaining = [line.strip() for line in text.split('\n') if 'watchman' in line.lower()]
print(f"\nRemaining occurrences of 'watchman': {len(remaining)}")
for r in remaining:
    print("  ->", r[:100])

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved frontend/index.html successfully!")
