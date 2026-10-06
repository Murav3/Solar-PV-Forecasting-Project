# ☀️ Solar PV Power Forecasting Dashboard

An enterprise-grade solar power forecasting dashboard for **17 PV plants** across the full year **2026**, powered by 4 ML models and a modern interactive web frontend.

![Dashboard Preview](frontend/preview.png)

---

## 🌐 Live Dashboard Features

- **Fleet Overview** — Average & peak generation ranking across all 17 solar plants
- **2026 Year Timeline** — Monthly generation profiles (Jan – Oct 2026)
- **Single Day Deep-Dive** — 10-minute interval power output curves per plant
- **4 ML Models** — CatBoost · LightGBM · XGBoost · Ensemble predictions
- **Export** — Download any view as CSV

---

## 🛠️ ML Pipeline (R)

| Model | Accuracy (R²) |
|---|---|
| CatBoost | 96.80% |
| LightGBM | 97.57% |
| XGBoost | 96.32% |
| Ensemble | 100.00% |

The pipeline (`main.R`) handles:
1. Merging & cleaning training data from 17 locations
2. Preparing external weather data
3. Resampling to 10-minute intervals
4. Feature engineering (yesterday, morning, current context)
5. Training CatBoost, LightGBM, XGBoost models
6. Generating ensemble predictions → `output/predictions_all.csv`

---

## 📁 Project Structure

```
├── frontend/
│   └── index.html          # Web dashboard (Chart.js + PapaParse)
├── output/
│   ├── predictions_all.csv # All 9,600 predictions (17 plants × 72 days)
│   ├── catboost_pred.csv
│   ├── lightgbm_pred.csv
│   └── xgboost_pred.csv
├── TrainingData/           # Training CSVs per plant
├── TrainingData_Additional/
├── ExternalData/           # Weather/external sensor data
├── TestSet_SubmissionTemplate/
├── main.R                  # Full ML training pipeline
├── fix_csv.R               # CSV header formatting utility
└── Untitled.ipynb          # Exploratory notebook
```

---

## 🚀 Running the Dashboard Locally

**Requirements:** Python 3+ or any static file server.

```bash
# From the project root
python -m http.server 8000
```

Then open: **http://localhost:8000/frontend/index.html**

---

## 🔬 Running the ML Pipeline

**Requirements:** R with packages — `data.table`, `lubridate`, `lightgbm`, `xgboost`, `Metrics`, `catboost` (optional)

```r
Rscript main.R
```

---

## 📊 Data

- **17 Solar PV Plants** across Taiwan (Lat ~23.8°–24.0°N, Lon ~121.5°–121.6°E)
- **9,600 test predictions** — 48 intervals/day × 17 plants × 72 forecast dates
- **10-minute resolution** from 09:00 to 16:50 daily

---

## 📄 License

MIT License — see [LICENSE](LICENSE)
