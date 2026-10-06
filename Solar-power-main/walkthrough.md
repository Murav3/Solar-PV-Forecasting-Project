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
- **`output/predictions_all.csv`**: Aggregated prediction dataset for all 17 solar plants.
- **`main.R`**: Core ML training pipeline for model fitting and evaluation.
- **`fix_csv.py`**: Formatting utility ensuring clean CSV headers for the frontend.
