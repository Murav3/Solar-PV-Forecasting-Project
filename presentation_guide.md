# ☀️ Solar PV Power Forecasting Project — Technical Deep-Dive & Architecture Guide

---

## 🏗️ 1. Complete System Architecture & Data Flow

```
┌─────────────────────────┐      ┌───────────────────────────┐
│ 17 Solar Plant CSV Logs │  &   │ External Weather Sensors  │
└────────────┬────────────┘      └─────────────┬─────────────┘
             │                                 │
             ▼                                 ▼
┌────────────────────────────────────────────────────────────┐
│                    R Pipeline (main.R)                     │
│  - Resampling to 10-min intervals (08:00 - 16:59 UTC)      │
│  - Linear interpolation for missing weather data           │
│  - Physical plant metadata join (Lat, Lon, Azimuth, Alt)   │
│  - Feature Engineering: Lag 24h + 08:50 AM morning baseline│
└────────────────────────────┬───────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│                  Machine Learning Engine                   │
│   ├── CatBoost  (Depth=6, 1500 iterations, R² 96.80%)     │
│   ├── LightGBM  (Leaves=63, 1000 rounds,    R² 97.57%)     │
│   └── XGBoost   (Hist-based tree, 1000 r,   R² 96.32%)     │
└────────────────────────────┬───────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│                    Ensemble Aggregation                    │
│   Power_Ensemble = max( (CatBoost + LightGBM + XGBoost) / 3, 0 )
└────────────────────────────┬───────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│                Python Formatter (fix_csv.py)               │
│   Produces standardized output/predictions_all.csv         │
└────────────────────────────┬───────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────┐
│             Web Dashboard (frontend/index.html)            │
│   - PapaParse CSV Ingestion                                │
│   - Chart.js Rendering (Fleet Leaderboard, Diurnal Curves)  │
│   - Tabular Search & CSV Data Export                       │
└────────────────────────────────────────────────────────────┘
```

---

## 🔬 2. Step-by-Step Technical Breakdown

### **Step 1: Data Ingestion & Cleaning (`main.R` Sections 1–4)**
* **Merging CSVs (`merge_csv`)**: Loads power output records across all plants from `TrainingData/` and `TrainingData_Additional/` using R's high-performance `data.table::fread()`. Converts dates to UTC standard (`POSIXct`).
* **Resampling External Weather Data (`prepare_external_data`)**: Reads raw weather logs (solar radiation lux, temperature, humidity, wind speed, atmospheric pressure). Aggregates data into **10-minute bins** using `floor_date(datetime, "10 minutes")` and takes column means. Missing weather entries are linearly interpolated using `approx()`.
* **Daylight Window Filtering (`generate_full_data`)**: Restricts all time-series logs to active solar generation hours (**08:00 AM to 16:59 PM UTC**), creating a regular 10-minute grid across all 17 plant locations.

---

### **Step 2: Feature Engineering & Contextual Joins (`main.R` Sections 5–6)**
Before training the AI, raw time-series data is converted into high-dimensional feature vectors:
1. **Physical Plant Specifications**: Joins physical attributes for all 17 plants:
   - Latitude & Longitude (Location positioning)
   - Azimuth orientation angle (Degrees relative to South: e.g. 180° = South, 208° = SSW)
   - Altitude above sea level (meters)
2. **Temporal Encoding**: Extracts `month`, `day`, `hour`, `minute`, and Unix timestamps to capture seasonal and sun-angle movement.
3. **Historical Vectorized Lag Features (`create_samples`)**:
   - **Yesterday's Power (`yesterday_*`)**: For any time slot $t$, the system looks back 24 hours ($t - 86,400\text{ seconds}$) to fetch the power generated at the exact same time slot on the previous day.
   - **Morning Baseline (`morning_*`)**: Captures the power generation recorded at **08:50 AM** on the current day. This acts as an early indicator of day-long cloud cover.
   - **Current Weather Context (`current_*`)**: Attaches real-time atmospheric measurements (Lux, Temp, Wind, Pressure, Humidity).

---

### **Step 3: Machine Learning Training & Ensembling (`main.R` Sections 7–8)**

Three distinct gradient-boosted decision tree architectures are trained in parallel:

1. **CatBoost (`catboost.train`)**:
   - **Hyperparameters**: `iterations=1500`, `learning_rate=0.05`, `depth=6`, `loss_function="RMSE"`.
   - **Strengths**: Optimizes categorical feature combinations and reduces target leakage.

2. **LightGBM (`lgb.train`)**:
   - **Hyperparameters**: `num_leaves=63`, `learning_rate=0.05`, `nrounds=1000`.
   - **Strengths**: Uses **Leaf-wise tree growth** (splits the node with max loss reduction) rather than level-wise, making it ultra-fast and achieving the highest single-model accuracy (97.57%).

3. **XGBoost (`xgb.train`)**:
   - **Hyperparameters**: `max_depth=6`, `eta=0.05`, `nrounds=1000`, `tree_method="hist"`.
   - **Strengths**: Histogram-based binning speeds up continuous feature evaluations.

4. **Ensemble & Post-Processing**:
   $$\hat{y}_{\text{ensemble}} = \max\left( \frac{\hat{y}_{\text{CatBoost}} + \hat{y}_{\text{LightGBM}} + \hat{y}_{\text{XGBoost}}}{3}, \, 0 \right)$$
   Negative predictions (physically impossible for solar generation) are clipped to 0 using `pmax(p, 0)` and rounded to 2 decimal places. Results are exported to `output/predictions_all.csv`.

---

### **Step 4: CSV Standardization Utility (`fix_csv.py`)**
* Reads raw outputs from R (`catboost_pred.csv`, `lightgbm_pred.csv`, `xgboost_pred.csv`, `submission.csv`).
* Parses template serial codes (e.g. `20240117090001` ➔ Date: `2024-01-17 09:00`, Location ID: `1`).
* Formats clean columns: `serial_no`, `datetime`, `location`, `catboost`, `lightgbm`, `xgboost`, `ensemble`.

---

### **Step 5: Client-Side Web Dashboard (`frontend/index.html`)**
* **Asynchronous Data Loading**: Uses **PapaParse** to parse `output/predictions_all.csv` directly in the browser memory without requiring a heavy backend database.
* **Client-Side Aggregation**:
  - Groups records by location (1 to 17) to compute average vs. peak power output for the Fleet Leaderboard.
  - Groups records by month (Jan–Oct) to plot monthly generation trends.
  - Filters by plant and selected date to render 48-point diurnal curves (09:00 to 16:50).
* **Dynamic Visualization**: Uses **Chart.js** with custom tooltips, dark glassmorphism gradients, and smooth line/bar animation transitions.
* **CSV Export Utility**: Generates client-side CSV downloads on demand via dynamic DOM `Blob` links (`exportCurrentViewCSV()`).

---

## 🎯 3. Technical Terms & Definitions Cheat Sheet

* **PV (Photovoltaic)**: Technology that converts sunlight directly into electricity using solar panels.
* **Diurnal Curve**: A graph showing power output rising from morning sunrise, peaking at solar noon, and falling towards sunset.
* **Gradient Boosting**: An ML technique where trees are built sequentially, with each new tree correcting errors made by previous trees.
* **R² Score (Coefficient of Determination)**: Measures how well predictions match actual values (100% = perfect prediction).
* **PapaParse**: A lightweight JavaScript library used to parse large CSV files quickly inside web browsers.
* **Chart.js**: An open-source HTML5 JavaScript library for rendering responsive animated charts.
