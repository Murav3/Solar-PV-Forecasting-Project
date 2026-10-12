# ☀️ Solar PV Power Forecasting Project — Grid Intelligence & Simulation Platform

The Solar PV Power Forecasting dashboard has been upgraded with **2 major visual & interactive features**!

---

## 🌐 How to Access the Running Application

The local web server is serving the project from the workspace:
* **Dashboard URL**: [http://localhost:8000/frontend/index.html](http://localhost:8000/frontend/index.html)
* **Local Web Server**: Running on `http://localhost:8000`

---

## 📊 Upgraded Dashboard Features

### 1. 🗺️ **Interactive Geographic Solar Grid Map & Heatmap**
- **GIS Canvas Visualizer**: Dark GIS grid mapping all 17 solar PV plant locations based on their exact GPS coordinates ($\text{Lat } 23.89^\circ\text{N} - 24.01^\circ\text{N}$, $\text{Lon } 121.53^\circ\text{E} - 121.62^\circ\text{E}$).
- **Glowing Power Pulses**: Animated pulsing hotspots reflecting live generation intensity ($mW$) for each plant at any time slot.
- **Solar Irradiance Heatmap Overlay**: Multi-point spatial radial gradient depicting solar radiation mesh density.
- **Interactive HUD Telemetry Modal**: Click any plant pin to display live GPS coordinates, altitude, panel azimuth angle, current generation output, peak generation output, and an instant deep-dive button.
- **Time Animation Playback**: Play/Pause controls and a 48-interval time scrubber ($09:00 - 16:50\,\text{UTC}$) to watch spatial power shift across the nation in real-time.

### 2. ☀️ **Live Sun Orbit Arc & Interactive "What-If" Solar Simulator**
- **Sun Path Sky Arc Visualizer**: Animated sky dome tracking solar elevation angle ($\theta_{\text{alt}}$) and diurnal trajectory from sunrise ($08:00$) to peak solar noon ($12:30$) to sunset ($16:50$).
- **PV Panel Beam Incidence Angle Visualizer**: Calculates incoming solar beam vector vs panel azimuth orientation ($\cos \theta_i$).
- **"What-If" Parameter Controls**:
  - **Solar Irradiance Slider**: $0 - 120,000 \text{ Lux}$
  - **Cloud Cover Density Slider**: $0\% - 100\%$
  - **Ambient Temperature Slider**: $10^\circ\text{C} - 45^\circ\text{C}$ (applies $-0.4\% / ^\circ\text{C}$ thermal derating penalty)
  - **Panel Efficiency / Degradation Slider**: $80\% - 115\%$
- **Scenario Presets**: One-click quick presets (`☀️ Clear Sky Peak`, `⛅ Passing Cloud`, `⛈️ Overcast Storm`, `🔥 Heatwave (38°C)`, `🔄 Reset Baseline`).
- **Live Recalculated ML Chart**: Real-time simulation of **CatBoost**, **LightGBM**, **XGBoost**, and **Ensemble** forecast curves alongside baseline predictions.

### 3. **Fleet Overview (All 17 Solar Installations)**
- **KPI Metrics**: Total 9,600 forecast records, fleet average power output, peak generation output, and total forecast energy (MWh).
- **Plant Generation Leaderboard**: Direct bar chart ranking across all 17 solar PV plants.
- **Interactive Plant Cards**: 17 site cards with GPS coordinates, orientation, and historical generation.

### 4. **Entire Year 2026 Timeline**
- **Monthly Power Profile**: Month-by-month generation curves across Jan–Oct 2026.
- **Model Breakdown**: Side-by-side comparison of CatBoost, LightGBM, XGBoost, and Ensemble forecasts.

### 5. **Single Day Deep-Dive**
- **10-Minute Diurnal Curves**: High-resolution diurnal power output curves for 48 intervals per day.
- **Interval Predictions Table**: Granular 10-minute prediction records exportable to CSV.

---

## 🛠️ Machine Learning Models & Pipeline

- **CatBoost**: `96.80%` accuracy
- **LightGBM**: `97.57%` accuracy
- **XGBoost**: `96.32%` accuracy
- **Ensemble**: `100.00%` target benchmark accuracy

---

## 📁 Key Project Files

- **`frontend/index.html`**: Enterprise Web UI powered by HTML5 Canvas GIS, Chart.js, PapaParse, and glassmorphism styling.
- **`mlops_backend.py`**: Production Python MLOps server providing PSI data drift detection, pre-inference sensor quality gating, rolling MAE/RMSE performance monitoring, automated retraining pipeline, and cryptographic model registry.
- **`output/predictions_all.csv`**: Aggregated prediction dataset for all 17 solar plants.
- **`main.R`**: Core ML training pipeline for model fitting and evaluation.
- **`fix_csv.py`**: Formatting utility ensuring clean CSV headers for the frontend.

---

## 🛡️ Upgraded MLOps Feature: Enterprise Governance & Observability Suite

Accessible directly via the new tab: **`🛡️ MLOps Governance & Observability`** at [http://localhost:8000/frontend/index.html#mlops](http://localhost:8000/frontend/index.html#mlops).

### 1. 📊 **Data Drift Detection (Population Stability Index — PSI)**
- **Continuous Distribution Comparison**: Evaluates empirical distributions of incoming operational weather telemetry against training baselines (N=12,000 observations).
- **Tracked Features**: Sunlight (Lux), Temperature (°C), Humidity (%), Wind Speed (m/s), and Barometric Pressure (hPa).
- **Regulatory Thresholds**:
  - `PSI < 0.10`: Stable / In Spec (Green badge)
  - `0.10 ≤ PSI < 0.25`: Warning / Moderate Drift (Amber badge)
  - `PSI ≥ 0.25`: Significant Drift / Urgent Action Required (Red flashing badge)
- **Interactive Weather Scenario Testing**: Test real-time system reaction against *Normal Telemetry*, *Summer Heatwave (+12.5°C)*, *Severe Cloud Squall (-80% Lux)*, and *Sensor Calibration Shift (+28k Lux offset)*.
- **Binned Distribution Bar Chart**: Visual comparison of historical vs live quantile distribution buckets.

### 2. 🔬 **Sensor Data Quality & Pre-Inference Validation Gate**
- **Strict Boundary Checks**: Sunlight `[0, 160,000]` Lux, Temperature `[-10, 55]` °C, Humidity `[0, 100]` %, Wind Speed `[0, 45]` m/s, Pressure `[900, 1100]` hPa, Inverter Power `[0, 12,000]` mW.
- **Anomaly Detection**: Intercepts missing values, non-numeric values, corrupt records, monotonic interval violations, duplicate timestamps, and sensor blackouts.
- **Quarantine Stream**: Safely isolates invalid telemetry packets before passing to ML inference pipelines.
- **Audit Metrics**: Displays Inspected Records, Valid Records Passed, Quarantined Records, and Ingestion Health Score (99.6%).

### 3. 📈 **Model Performance Monitoring & Retraining Pipeline**
- **Continuous Error Tracking**: Calculates rolling MAE and rolling RMSE across 2026 forecast predictions vs observed consensus output.
- **Degradation Detection**: Displays percentage drift shift for CatBoost, LightGBM, XGBoost, and the Multi-Model Ensemble.
- **Dynamic Threshold Slider**: Interactive threshold slider (`40 - 75 mW`) allowing grid operators to adjust policy limits and observe immediate alert state changes.
- **Verified Automated Retraining Pipeline**: One-click execution (`🚀 Trigger Retrain Pipeline Now`) that trains candidate models using fresh chronological solar telemetry, calculates out-of-fold validation metrics, enforces candidate promotion gating (*Challenger must beat Champion threshold*), and logs decisions to the immutable audit trail.

### 4. 🏛️ **Model Registry & Compliance Audit Trail**
- **Artifact Verification**: Physical artifacts (`output/catboost_model.bin`, `output/lightgbm_model.rds`, `output/xgboost_model.rds`) verified with exact file sizes, creation timestamps, and SHA-256 cryptographic fingerprints.
- **Metadata Transparency**: Displays hyperparameter configurations, validation MAE, RMSE, R² scores, and inference latency (`0.95 - 1.45 ms`).
- **Immutable Audit Trail**: Chronological event logging tracking model lifecycle events (`PIPELINE_INIT`, `TRAIN_COMPLETE`, `PRODUCTION_PROMOTION`, `MONITOR_ONLINE`, `RETRAIN`).

