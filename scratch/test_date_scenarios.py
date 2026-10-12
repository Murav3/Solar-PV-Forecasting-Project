import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd

df = pd.read_csv('output/predictions_all.csv')
raw_dates = sorted(df['datetime'].dropna().astype(str).str[:10].unique())
dates_2026 = [d.replace('2024-', '2026-') for d in raw_dates]

def get_date_weather_profile(date_val):
    h = 0
    for c in date_val:
        h = ((h << 5) - h) + ord(c)
        h = h & 0xFFFFFFFF
    if h > 0x7FFFFFFF:
        h -= 0x100000000
    pos_hash = abs(h)

    mod20 = pos_hash % 20
    if mod20 in [0, 1, 2]:
        archetype = 'fast'
        title = 'Fast Storm Day'
        base_speed = 26.5
    elif mod20 in [3, 4, 5]:
        archetype = 'slow'
        title = 'Slow Heavy Fog'
        base_speed = 7.5
    else:
        archetype = 'moderate'
        title = 'Normal Cloud Day'
        base_speed = 13.8

    times = ['09:40 AM', '10:20 AM', '11:10 AM', '11:50 AM', '12:30 PM', '13:10 PM', '13:50 PM', '14:20 PM', '15:10 PM']
    event_time = times[pos_hash % len(times)]
    return archetype, title, base_speed, event_time

counts = {'moderate': 0, 'fast': 0, 'slow': 0}
for d in dates_2026:
    arch, title, spd, t = get_date_weather_profile(d)
    counts[arch] += 1

print(f"Total dates: {len(dates_2026)}")
print(f"Distribution: Normal Cloud Day: {counts['moderate']} ({counts['moderate']/len(dates_2026)*100:.1f}%), Fast Storm: {counts['fast']} ({counts['fast']/len(dates_2026)*100:.1f}%), Heavy Fog: {counts['slow']} ({counts['slow']/len(dates_2026)*100:.1f}%)")

# Test lead times for Plant L1 (1.85 km)
print("\nPlant L1 (1.85 km) Lead Times:")
for arch, spd in [('Normal Cloud Day', 13.8), ('Fast Storm Day', 26.5), ('Slow Heavy Fog', 7.5)]:
    sec = round((1850) / (spd / 3.6))
    print(f"  {arch} ({spd} km/h): {sec}s = +{sec/60:.1f} mins")

# Sample 10 dates
print("\nSample Dates Mapping:")
for d in dates_2026[:10]:
    arch, title, spd, t = get_date_weather_profile(d)
    print(f"  {d} -> {title} (Simulated Event: {t})")
