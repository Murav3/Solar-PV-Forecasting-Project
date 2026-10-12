import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('"L13 · West Watchman Station 1"', '"L13 · West Advance Station 1"')
text = text.replace('"L14 · West Watchman Station 2"', '"L14 · West Advance Station 2"')

remaining = [line.strip() for line in text.split('\n') if 'watchman' in line.lower()]
print(f"Remaining occurrences of 'watchman': {len(remaining)}")

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Saved frontend/index.html!")
