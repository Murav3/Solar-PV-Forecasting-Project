import csv
import os

output_dir = "output"

# 1. Fix individual prediction CSVs header to serial_no,power_mw
files_map = {
    "catboost_pred.csv": "catboost",
    "lightgbm_pred.csv": "lightgbm",
    "xgboost_pred.csv": "xgboost",
    "submission.csv": "ensemble"
}

preds = {}

for filename, key in files_map.items():
    filepath = os.path.join(output_dir, filename)
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        continue
    
    rows = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) >= 2:
                rows.append((row[0].strip(), row[1].strip()))
    
    # Write back with standard headers
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["serial_no", "power_mw"])
        writer.writerows(rows)
    
    print(f"Fixed header for {filename}: {len(rows)} rows")
    preds[key] = {r[0]: r[1] for r in rows}

# 2. Re-create predictions_all.csv
template_path = os.path.join("TestSet_SubmissionTemplate", "upload(no answer).csv")
serials = []
with open(template_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        if row:
            serials.append(row[0].strip())

print(f"Loaded template serials: {len(serials)}")

all_rows = []
for s in serials:
    # s is like '20240117090001'
    # chars 0..12: '202401170900' -> '2024-01-17 09:00'
    # chars 12..14: '01' -> 1
    if len(s) >= 14:
        date_part = s[:8]
        time_part = s[8:12]
        loc_part = int(s[12:14])
        dt_formatted = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]} {time_part[:2]}:{time_part[2:4]}"
    else:
        dt_formatted = ""
        loc_part = ""
    
    cb_val = preds.get("catboost", {}).get(s, "0")
    lgb_val = preds.get("lightgbm", {}).get(s, "0")
    xgb_val = preds.get("xgboost", {}).get(s, "0")
    ens_val = preds.get("ensemble", {}).get(s, "0")
    
    all_rows.append([s, dt_formatted, loc_part, cb_val, lgb_val, xgb_val, ens_val])

predictions_all_path = os.path.join(output_dir, "predictions_all.csv")
with open(predictions_all_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["serial_no", "datetime", "location", "catboost", "lightgbm", "xgboost", "ensemble"])
    writer.writerows(all_rows)

print(f"Successfully generated {predictions_all_path} with {len(all_rows)} rows!")
