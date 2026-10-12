import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

count = 0
for i, line in enumerate(lines, 1):
    if 'watchman' in line.lower():
        count += 1
        print(f"{i}: {line.strip()[:110]}")

print(f"\nTotal occurrences of 'watchman': {count}")
