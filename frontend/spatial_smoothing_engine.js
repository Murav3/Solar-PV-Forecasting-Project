/**
 * Spatial Portfolio Smoothing & Diversification Analytics Engine
 * National Grid Intelligence Platform — Solar PV Forecasting
 * 
 * Provides rigorous mathematical routines for:
 * 1. Timestamp-aligned inner-join across arbitrary plant sub-fleets
 * 2. Diurnal solar cycle detrending
 * 3. Spatial Haversine distance & decorrelation curve fitting (r vs km)
 * 4. Micro-ramp rate analysis (ΔP/Δt), ramp volatility reduction & distributions
 * 5. Portfolio Diversification Index (PDI), Smoothing Factor (S) & Volatility Dampening Gain
 */

(function (global) {
  'use strict';

  // ── CONSTANTS & METADATA ──
  const EARTH_RADIUS_KM = 6371.0088;

  const DEFAULT_PLANT_INFO = {
    1:  { lat: 23.899444, lon: 121.544444, ori: 181, alt: 5, name: "PV Plant L1", cluster: "inland" },
    2:  { lat: 23.899722, lon: 121.544722, ori: 175, alt: 5, name: "PV Plant L2", cluster: "inland" },
    3:  { lat: 23.899722, lon: 121.545000, ori: 180, alt: 5, name: "PV Plant L3", cluster: "inland" },
    4:  { lat: 23.899444, lon: 121.544444, ori: 161, alt: 5, name: "PV Plant L4", cluster: "inland" },
    5:  { lat: 23.899444, lon: 121.544722, ori: 208, alt: 5, name: "PV Plant L5", cluster: "inland" },
    6:  { lat: 23.899444, lon: 121.544444, ori: 208, alt: 5, name: "PV Plant L6", cluster: "inland" },
    7:  { lat: 23.899444, lon: 121.544444, ori: 172, alt: 5, name: "PV Plant L7", cluster: "inland" },
    8:  { lat: 23.899722, lon: 121.545000, ori: 219, alt: 3, name: "PV Plant L8", cluster: "inland" },
    9:  { lat: 23.899444, lon: 121.544444, ori: 151, alt: 3, name: "PV Plant L9", cluster: "inland" },
    10: { lat: 23.899444, lon: 121.544444, ori: 223, alt: 1, name: "PV Plant L10", cluster: "inland" },
    11: { lat: 23.899722, lon: 121.544722, ori: 131, alt: 1, name: "PV Plant L11", cluster: "inland" },
    12: { lat: 23.899722, lon: 121.544722, ori: 298, alt: 1, name: "PV Plant L12", cluster: "inland" },
    13: { lat: 23.897778, lon: 121.539444, ori: 249, alt: 5, name: "PV Plant L13", cluster: "inland" },
    14: { lat: 23.897778, lon: 121.539444, ori: 197, alt: 5, name: "PV Plant L14", cluster: "inland" },
    15: { lat: 24.009167, lon: 121.617222, ori: 127, alt: 1, name: "PV Plant L15", cluster: "coastal" },
    16: { lat: 24.008889, lon: 121.617222, ori: 82,  alt: 1, name: "PV Plant L16", cluster: "coastal" },
    17: { lat: 23.975128, lon: 121.613275, ori: 0,   alt: 0, name: "PV Plant L17", cluster: "coastal" }
  };

  // ── MATHEMATICAL & STATISTICAL HELPERS ──
  function mean(arr) {
    if (!arr || arr.length === 0) return 0;
    let s = 0;
    for (let i = 0; i < arr.length; i++) s += arr[i];
    return s / arr.length;
  }

  function sampleStdDev(arr, m) {
    if (!arr || arr.length < 2) return 0;
    const avg = m !== undefined ? m : mean(arr);
    let sumSq = 0;
    for (let i = 0; i < arr.length; i++) {
      const diff = arr[i] - avg;
      sumSq += diff * diff;
    }
    return Math.sqrt(sumSq / (arr.length - 1));
  }

  function popStdDev(arr, m) {
    if (!arr || arr.length === 0) return 0;
    const avg = m !== undefined ? m : mean(arr);
    let sumSq = 0;
    for (let i = 0; i < arr.length; i++) {
      const diff = arr[i] - avg;
      sumSq += diff * diff;
    }
    return Math.sqrt(sumSq / arr.length);
  }

  function coefVariation(arr) {
    if (!arr || arr.length < 2) return 0;
    const m = mean(arr);
    if (Math.abs(m) < 1e-9) return 0;
    const s = sampleStdDev(arr, m);
    return s / m;
  }

  function pearsonCorr(x, y) {
    const n = Math.min(x.length, y.length);
    if (n < 3) return 0;
    let sumX = 0, sumY = 0;
    for (let i = 0; i < n; i++) {
      sumX += x[i];
      sumY += y[i];
    }
    const mx = sumX / n, my = sumY / n;
    let num = 0, denX = 0, denY = 0;
    for (let i = 0; i < n; i++) {
      const dx = x[i] - mx;
      const dy = y[i] - my;
      num += dx * dy;
      denX += dx * dx;
      denY += dy * dy;
    }
    const den = Math.sqrt(denX * denY);
    if (den < 1e-12) return 0;
    const r = num / den;
    return Math.max(-1, Math.min(1, r));
  }

  // Haversine formula for great-circle distance
  function haversineDistance(lat1, lon1, lat2, lon2) {
    if (lat1 === lat2 && lon1 === lon2) return 0;
    const toRad = Math.PI / 180.0;
    const dLat = (lat2 - lat1) * toRad;
    const dLon = (lon2 - lon1) * toRad;
    const rLat1 = lat1 * toRad;
    const rLat2 = lat2 * toRad;

    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(rLat1) * Math.cos(rLat2) *
              Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return EARTH_RADIUS_KM * c;
  }

  function parseDateKey(str) {
    if (!str) return '';
    // Format YYYY-MM-DD HH:mm or YYYY-MM-DDTHH:mm
    return String(str).replace('T', ' ').substring(0, 16);
  }

  // Cardinal direction from meteorological azimuth
  function aziToCompass(deg) {
    if (deg == null || isNaN(deg)) return 'N/A';
    const normalized = ((deg % 360) + 360) % 360;
    const dirs = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW'];
    const idx = Math.round(normalized / 22.5) % 16;
    return dirs[idx];
  }

  // ════════════════════════════════════════════════════════════════════════════
  // FEATURE 1 & 2: DATA ALIGNMENT & DATE FILTER ENGINE
  // ════════════════════════════════════════════════════════════════════════════
  const SpatialDataEngine = {
    /**
     * Performs strict timestamp-aligned inner join across selected plants.
     * 
     * @param {Array} rawData - allData records with { datetime, location, ensemble, ... }
     * @param {Array<number>} selectedPlants - list of plant IDs to include (e.g. [1, 2, 15, 16])
     * @param {Object} options - {
     *    monthFilter: 'all' | '2026-01' ...
     *    dateFilter: '' | '2026-08-15' ...
     *    mode: 'range' | 'diurnal' | 'microramp'
     *    targetValueKey: 'ensemble' (or 'catboost', 'lightgbm', 'xgboost')
     * }
     */
    alignFleetData(rawData, selectedPlants, options = {}) {
      const mode = options.mode || 'range';
      const monthFilter = options.monthFilter || 'all';
      const dateFilter = options.dateFilter || '';
      const valueKey = options.targetValueKey || 'ensemble';

      if (!rawData || !rawData.length || !selectedPlants || !selectedPlants.length) {
        return {
          timestamps: [], plantSeries: {}, fleetSeries: [],
          alignedCount: 0, totalRawCount: rawData ? rawData.length : 0,
          droppedCount: 0, droppedRatio: 0, duplicatesHandled: 0,
          isInsufficient: true, reason: 'No data or no plants selected'
        };
      }

      const activePlantSet = new Set(selectedPlants.map(Number));
      const plantTimeMap = {};
      selectedPlants.forEach(pid => { plantTimeMap[pid] = new Map(); });

      let duplicatesHandled = 0;

      // Single pass – collect per-plant time->value maps
      for (let i = 0; i < rawData.length; i++) {
        const row = rawData[i];
        const pid = Number(row.location);
        if (!activePlantSet.has(pid)) continue;
        const val = row[valueKey];
        if (val === null || val === undefined || isNaN(Number(val))) continue;
        const dtStr = parseDateKey(row.datetime);
        if (!dtStr) continue;
        if (monthFilter !== 'all' && !dtStr.startsWith(monthFilter)) continue;
        if (mode === 'microramp' && dateFilter && !dtStr.startsWith(dateFilter)) continue;
        else if (dateFilter && options.strictDate && !dtStr.startsWith(dateFilter)) continue;
        const pMap = plantTimeMap[pid];
        if (pMap.has(dtStr)) {
          duplicatesHandled++;
          pMap.set(dtStr, (pMap.get(dtStr) + Number(val)) / 2);
        } else {
          pMap.set(dtStr, Number(val));
        }
      }

      // Union of all timestamps (so every plant's data is used for individual stats)
      const unionSet = new Set();
      selectedPlants.forEach(pid => { for (const k of plantTimeMap[pid].keys()) unionSet.add(k); });
      const allTimes = Array.from(unionSet).sort();

      // Inner-join timestamps (needed for fleet aggregate line; may be empty for cross-cluster)
      let commonTimes = allTimes;
      if (selectedPlants.length > 1) {
        commonTimes = allTimes.filter(t => selectedPlants.every(pid => plantTimeMap[pid].has(t)));
      }

      // Build per-plant series on their OWN available timestamps (for CV, std, histogram)
      const plantSeries = {};
      selectedPlants.forEach(pid => {
        const pMap = plantTimeMap[pid];
        const times = Array.from(pMap.keys()).sort();
        const arr = new Float64Array(times.length);
        for (let i = 0; i < times.length; i++) arr[i] = pMap.get(times[i]);
        plantSeries[pid] = arr;
        plantSeries[pid]._timeMap = pMap; // keep for pairwise correlation
        plantSeries[pid]._times = times;
      });

      // Fleet aggregate on common timestamps; fallback to largest-overlap pair if none
      let usedTimes = commonTimes;
      if (commonTimes.length < 2 && selectedPlants.length >= 2) {
        // Find the pair with most overlap and use that
        let bestCount = 0;
        for (let a = 0; a < selectedPlants.length; a++) {
          for (let b = a + 1; b < selectedPlants.length; b++) {
            const pA = selectedPlants[a], pB = selectedPlants[b];
            let overlap = 0;
            for (const t of plantTimeMap[pA].keys()) { if (plantTimeMap[pB].has(t)) overlap++; }
            if (overlap > bestCount) {
              bestCount = overlap;
              usedTimes = Array.from(plantTimeMap[pA].keys())
                .filter(t => plantTimeMap[pB].has(t)).sort();
            }
          }
        }
      }

      const fleetSeries = new Float64Array(usedTimes.length);
      for (let i = 0; i < usedTimes.length; i++) {
        let sum = 0;
        selectedPlants.forEach(pid => {
          if (plantTimeMap[pid].has(usedTimes[i])) sum += plantTimeMap[pid].get(usedTimes[i]);
        });
        fleetSeries[i] = sum;
      }

      const totalUnion = allTimes.length;
      const isInsufficient = totalUnion < 2;

      return {
        timestamps: usedTimes.length >= 2 ? usedTimes : allTimes,
        plantSeries,
        plantTimeMap,
        fleetSeries,
        alignedCount: totalUnion,
        totalRawCount: rawData.length,
        rawMatchedRows: totalUnion,
        droppedCount: 0,
        droppedRatio: 0,
        duplicatesHandled,
        isInsufficient,
        mode, monthFilter, dateFilter,
        commonCount: commonTimes.length,
        unionCount: totalUnion
      };
    },

    /**
     * Compute detrended series by subtracting average diurnal profile for each plant.
     * Isolates cloud fluctuations from predictable sun-rise/sun-set cycle.
     */
    detrendDiurnalCycle(plantSeries, timestamps, selectedPlants) {
      if (!selectedPlants || selectedPlants.length === 0) return {};
      const diurnalMean = {};
      const detrended = {};

      selectedPlants.forEach(pid => {
        const arr = plantSeries[pid];
        if (!arr || arr.length === 0) return;
        const times = arr._times || timestamps || [];
        const todSums = {}, todCounts = {};

        for (let i = 0; i < arr.length; i++) {
          const tStr = times[i] || '';
          const tod = tStr.length >= 16 ? tStr.substring(11, 16) : '12:00';
          todSums[tod] = (todSums[tod] || 0) + arr[i];
          todCounts[tod] = (todCounts[tod] || 0) + 1;
        }

        diurnalMean[pid] = {};
        for (const tod in todSums) {
          diurnalMean[pid][tod] = todSums[tod] / (todCounts[tod] || 1);
        }

        const dArr = new Float64Array(arr.length);
        const tMap = new Map();
        for (let i = 0; i < arr.length; i++) {
          const tStr = times[i] || '';
          const tod = tStr.length >= 16 ? tStr.substring(11, 16) : '12:00';
          const base = diurnalMean[pid][tod] || 0;
          dArr[i] = arr[i] - base;
          if (times[i]) tMap.set(times[i], dArr[i]);
        }
        dArr._timeMap = tMap;
        dArr._times = times;
        detrended[pid] = dArr;
      });

      return { detrended, diurnalMean };
    }
  };

  // ════════════════════════════════════════════════════════════════════════════
  // FEATURE 4 & 7: PORTFOLIO DIVERSIFICATION INDEX & SMOOTHING FACTOR
  // ════════════════════════════════════════════════════════════════════════════
  const SpatialPortfolioEngine = {
    /**
     * Compute fleet & individual metrics:
     * - Mean Individual CV
     * - Fleet CV
     * - Smoothing Factor S = Fleet CV / Mean Individual CV
     * - Volatility Dampening Gain (%) = (1 - S) * 100
     */
    computePortfolioKPIs(plantSeries, fleetSeries, selectedPlants) {
      if (!selectedPlants || !selectedPlants.length || !fleetSeries || fleetSeries.length < 2) {
        return {
          valid: false,
          activeCount: selectedPlants ? selectedPlants.length : 0,
          totalGenKW: 0,
          fleetMeanKW: 0,
          fleetStdKW: 0,
          fleetCV: 0,
          meanIndCV: 0,
          smoothingFactor: null,
          volatilityGainPct: null,
          indCVMap: {},
          indMeanMap: {},
          indStdMap: {},
          statusText: 'Insufficient observations for portfolio metrics'
        };
      }

      const indCVMap = {};
      const indMeanMap = {};
      const indStdMap = {};
      const validIndCVs = [];

      selectedPlants.forEach(pid => {
        const s = plantSeries[pid];
        const m = mean(s);
        const sd = sampleStdDev(s, m);
        indMeanMap[pid] = m;
        indStdMap[pid] = sd;

        if (m > 1e-6) {
          const cv = sd / m;
          indCVMap[pid] = cv;
          validIndCVs.push(cv);
        } else {
          indCVMap[pid] = 0;
        }
      });

      const fleetMean = mean(fleetSeries);
      const fleetStd = sampleStdDev(fleetSeries, fleetMean);
      const fleetCV = fleetMean > 1e-6 ? (fleetStd / fleetMean) : 0;
      const totalGenSum = selectedPlants.reduce((acc, pid) => acc + (indMeanMap[pid] || 0), 0);

      const meanIndCV = validIndCVs.length > 0 ? mean(validIndCVs) : 0;

      let smoothingFactor = null;
      let volatilityGainPct = null;

      // Mathematical safeguard: S requires valid non-zero individual CV
      if (meanIndCV > 1e-6 && fleetMean > 1e-6) {
        smoothingFactor = fleetCV / meanIndCV;
        volatilityGainPct = (1.0 - smoothingFactor) * 100.0;
      } else if (selectedPlants.length === 1) {
        smoothingFactor = 1.0;
        volatilityGainPct = 0.0;
      }

      return {
        valid: true,
        activeCount: selectedPlants.length,
        totalGenKW: totalGenSum,
        fleetMeanKW: fleetMean,
        fleetStdKW: fleetStd,
        fleetCV,
        meanIndCV,
        smoothingFactor,
        volatilityGainPct,
        indCVMap,
        indMeanMap,
        indStdMap
      };
    }
  };

  // ════════════════════════════════════════════════════════════════════════════
  // FEATURE 5: SPATIAL DECORRELATION CURVE (r vs Distance in km)
  // ════════════════════════════════════════════════════════════════════════════
  const SpatialDecorrelationEngine = {
    /**
     * Compute pairwise distances and Pearson correlation coefficients.
     * Fits exponential decorrelation model r(d) = A * exp(-d / d0) + C
     */
    computeDecorrelationCurve(plantSeries, selectedPlants, plantInfoMap = DEFAULT_PLANT_INFO) {
      if (!selectedPlants || selectedPlants.length < 2) {
        return {
          pairs: [],
          fit: null,
          hasModel: false,
          reason: 'Need at least 2 active plants to compute spatial decorrelation'
        };
      }

      const pairs = [];
      const n = selectedPlants.length;

      for (let i = 0; i < n; i++) {
        const p1 = selectedPlants[i];
        const info1 = plantInfoMap[p1] || DEFAULT_PLANT_INFO[p1];
        if (!info1 || info1.lat == null || info1.lon == null) continue;

        for (let j = i + 1; j < n; j++) {
          const p2 = selectedPlants[j];
          const info2 = plantInfoMap[p2] || DEFAULT_PLANT_INFO[p2];
          if (!info2 || info2.lat == null || info2.lon == null) continue;

          const distKm = haversineDistance(info1.lat, info1.lon, info2.lat, info2.lon);

          // Compute Pearson correlation only on OVERLAPPING timestamps
          let r = 0;
          if (plantSeries[p1]._timeMap && plantSeries[p2]._timeMap) {
            const mapA = plantSeries[p1]._timeMap;
            const mapB = plantSeries[p2]._timeMap;
            const xVals = [], yVals = [];
            for (const [t, v] of mapA) {
              if (mapB.has(t)) { xVals.push(v); yVals.push(mapB.get(t)); }
            }
            if (xVals.length >= 3) r = pearsonCorr(xVals, yVals);
          } else {
            r = pearsonCorr(plantSeries[p1], plantSeries[p2]);
          }

          pairs.push({
            p1, p2,
            label: `L${p1}–L${p2}`,
            distanceKm: Number(distKm.toFixed(3)),
            r: Number(r.toFixed(4)),
            cluster: (info1.cluster === info2.cluster) ? info1.cluster : 'cross-cluster'
          });
        }
      }

      if (pairs.length === 0) {
        return { pairs: [], fit: null, hasModel: false, reason: 'No valid plant coordinates' };
      }

      // Sort pairs by ascending distance
      pairs.sort((a, b) => a.distanceKm - b.distanceKm);

      // Fit model: r(d) = A * exp(-d / d0) + C
      // Using robust grid search optimization on realistic solar decorrelation parameters
      const fit = this.fitExponentialDecay(pairs);

      return {
        pairs,
        fit,
        hasModel: fit && fit.rSquared >= 0.1,
        totalPairs: pairs.length
      };
    },

    fitExponentialDecay(pairs) {
      if (!pairs || pairs.length < 3) return null;

      const rValues = pairs.map(p => p.r);
      const rMin = Math.min(...rValues);
      const rMax = Math.max(...rValues);

      let bestA = 0, bestD0 = 5, bestC = 0.5, minSSE = Infinity;

      // Candidate parameter search
      const cCandidates = [rMin, (rMin + rMax) / 2, 0.2, 0.4, 0.6, 0.8];
      const d0Candidates = [1.0, 2.5, 5.0, 8.0, 12.0, 18.0, 25.0, 40.0];

      for (let ci = 0; ci < cCandidates.length; ci++) {
        const C = cCandidates[ci];
        for (let di = 0; di < d0Candidates.length; di++) {
          const d0 = d0Candidates[di];
          // Solve linear A by least squares: A = sum((r_i - C)*exp(-d/d0)) / sum(exp(-2d/d0))
          let num = 0, den = 0;
          for (let k = 0; k < pairs.length; k++) {
            const expTerm = Math.exp(-pairs[k].distanceKm / d0);
            num += (pairs[k].r - C) * expTerm;
            den += expTerm * expTerm;
          }
          const A = den > 1e-9 ? (num / den) : 0;
          if (A < 0 && rMax > rMin + 0.1) continue; // Decays with distance, A generally positive

          let sse = 0;
          for (let k = 0; k < pairs.length; k++) {
            const pred = A * Math.exp(-pairs[k].distanceKm / d0) + C;
            const diff = pairs[k].r - pred;
            sse += diff * diff;
          }

          if (sse < minSSE) {
            minSSE = sse;
            bestA = A;
            bestD0 = d0;
            bestC = C;
          }
        }
      }

      // Compute Total Sum of Squares (SST) and R^2
      const meanR = mean(rValues);
      let sst = 0;
      for (let k = 0; k < pairs.length; k++) {
        const d = pairs[k].r - meanR;
        sst += d * d;
      }

      const rSquared = sst > 1e-9 ? Math.max(0, 1 - (minSSE / sst)) : 0;

      // Generate curve samples for plotting
      const maxDist = Math.max(...pairs.map(p => p.distanceKm), 16.0);
      const curvePoints = [];
      const numSteps = 50;
      for (let s = 0; s <= numSteps; s++) {
        const d = (s / numSteps) * maxDist;
        const rPred = bestA * Math.exp(-d / bestD0) + bestC;
        curvePoints.push({ x: Number(d.toFixed(2)), y: Number(Math.max(-1, Math.min(1, rPred)).toFixed(4)) });
      }

      return {
        amplitudeA: Number(bestA.toFixed(4)),
        decorrelationRadiusKm: Number(bestD0.toFixed(2)),
        baselineC: Number(bestC.toFixed(4)),
        rSquared: Number(rSquared.toFixed(3)),
        formula: `r(d) = ${bestA.toFixed(3)} · exp(-d / ${bestD0.toFixed(1)} km) + ${bestC.toFixed(3)}`,
        curvePoints
      };
    }
  };

  // ════════════════════════════════════════════════════════════════════════════
  // FEATURE 6: RAMP-RATE VOLATILITY REDUCTION & DISTRIBUTION
  // ════════════════════════════════════════════════════════════════════════════
  const SpatialRampRateEngine = {
    /**
     * Compute ΔP/Δt ramps for individual plants and fleet aggregate.
     * Expressed in kW/10-min or scaled kW/hr.
     */
    computeRampRates(plantSeries, fleetSeries, timestamps, selectedPlants) {
      if (!timestamps || timestamps.length < 2 || !selectedPlants || !selectedPlants.length) {
        return {
          valid: false,
          reason: 'Need at least 2 consecutive aligned observations'
        };
      }

      const MAX_INTERVAL_MINUTES = 30; // Do not calculate ramps across overnight or outage gaps
      const indRamps = {};
      selectedPlants.forEach(pid => {
        indRamps[pid] = [];
      });
      const fleetRamps = [];
      const fleetRampsPerPlant = []; // Normalized by plant count for direct shape comparison
      const rampTimestamps = [];
      let skippedGaps = 0;

      const nPlants = selectedPlants.length;

      for (let i = 1; i < timestamps.length; i++) {
        const tPrev = new Date(timestamps[i - 1].replace(' ', 'T') + ':00Z').getTime();
        const tCurr = new Date(timestamps[i].replace(' ', 'T') + ':00Z').getTime();
        const diffMinutes = (tCurr - tPrev) / (1000 * 60);

        if (diffMinutes <= 0 || diffMinutes > MAX_INTERVAL_MINUTES) {
          skippedGaps++;
          continue; // Discard overnight jump or large telemetry gap
        }

        const fleetDelta = fleetSeries[i] - fleetSeries[i - 1];
        if (!isNaN(fleetDelta)) {
          fleetRamps.push(fleetDelta);
          fleetRampsPerPlant.push(fleetDelta / nPlants);
          rampTimestamps.push(timestamps[i]);
        }
      }

      // Compute individual ramps for each plant using its own active time series
      selectedPlants.forEach(pid => {
        const pArr = plantSeries[pid];
        indRamps[pid] = [];
        if (pArr && pArr.length > 1) {
          for (let k = 1; k < pArr.length; k++) {
            const delta = pArr[k] - pArr[k - 1];
            if (!isNaN(delta) && Math.abs(delta) < 1000) {
              indRamps[pid].push(delta);
            }
          }
        }
      });

      if (fleetRamps.length < 2) {
        return {
          valid: false,
          reason: 'Insufficient consecutive regular intervals (all separated by > 30m gaps)'
        };
      }

      // Compute statistics
      const fleetRampStd = sampleStdDev(fleetRamps);
      const fleetMeanAbsRamp = mean(fleetRamps.map(r => Math.abs(r)));
      const fleetPeakUp = Math.max(...fleetRamps);
      const fleetPeakDown = Math.min(...fleetRamps);

      const indRampStdMap = {};
      const indMaxUpMap = {};
      const indMaxDownMap = {};
      const indAbsMeanMap = {};
      const allIndRampsConcatenated = [];

      selectedPlants.forEach(pid => {
        const rList = indRamps[pid];
        const rStd = sampleStdDev(rList);
        indRampStdMap[pid] = rStd;
        indMaxUpMap[pid] = Math.max(...rList);
        indMaxDownMap[pid] = Math.min(...rList);
        indAbsMeanMap[pid] = mean(rList.map(r => Math.abs(r)));
        for (let k = 0; k < rList.length; k++) allIndRampsConcatenated.push(rList[k]);
      });

      const meanIndRampStd = mean(selectedPlants.map(pid => indRampStdMap[pid]));
      const meanIndAbsRamp = mean(selectedPlants.map(pid => indAbsMeanMap[pid]));

      // Normalized Fleet Volatility per-plant comparison:
      // σ(ΔP_fleet / N) vs Mean Individual σ(ΔP_i)
      const fleetPerPlantStd = fleetRampStd / nPlants;
      let rampVolatilityReductionPct = 0;
      if (meanIndRampStd > 1e-6) {
        rampVolatilityReductionPct = (1.0 - (fleetPerPlantStd / meanIndRampStd)) * 100.0;
      }

      // Compute Comparative Histogram Bins
      const histogram = this.computeComparativeHistogram(allIndRampsConcatenated, fleetRampsPerPlant);

      return {
        valid: true,
        intervalLabel: '10-Minute Ramps (kW/10-min)',
        totalRampsComputed: fleetRamps.length,
        skippedGaps,
        fleetRampStd,
        fleetPerPlantStd,
        meanIndRampStd,
        rampVolatilityReductionPct,
        fleetMeanAbsRamp,
        meanIndAbsRamp,
        fleetPeakUp,
        fleetPeakDown,
        indRampStdMap,
        indMaxUpMap,
        indMaxDownMap,
        histogram,
        fleetRamps,
        indRamps
      };
    },

    computeComparativeHistogram(indRamps, fleetPerPlantRamps, numBins = 15) {
      if (!indRamps.length || !fleetPerPlantRamps.length) return null;

      // Find common range covering 99% of distributions
      const allR = indRamps.concat(fleetPerPlantRamps);
      allR.sort((a, b) => a - b);
      const p01 = allR[Math.floor(allR.length * 0.005)];
      const p99 = allR[Math.floor(allR.length * 0.995)];
      const minVal = Math.floor(Math.min(p01, -20));
      const maxVal = Math.ceil(Math.max(p99, 20));

      const binWidth = (maxVal - minVal) / numBins;
      const binLabels = [];
      const indFrequencies = new Array(numBins).fill(0);
      const fleetFrequencies = new Array(numBins).fill(0);

      for (let b = 0; b < numBins; b++) {
        const binStart = minVal + b * binWidth;
        const binEnd = binStart + binWidth;
        binLabels.push(`${Math.round(binStart)} to ${Math.round(binEnd)}`);
      }

      // Tally individual ramps
      for (let i = 0; i < indRamps.length; i++) {
        const v = indRamps[i];
        let b = Math.floor((v - minVal) / binWidth);
        if (b < 0) b = 0;
        if (b >= numBins) b = numBins - 1;
        indFrequencies[b]++;
      }

      // Tally fleet per-plant ramps
      for (let i = 0; i < fleetPerPlantRamps.length; i++) {
        const v = fleetPerPlantRamps[i];
        let b = Math.floor((v - minVal) / binWidth);
        if (b < 0) b = 0;
        if (b >= numBins) b = numBins - 1;
        fleetFrequencies[b]++;
      }

      // Normalize to percentage
      const indTotal = indRamps.length || 1;
      const fleetTotal = fleetPerPlantRamps.length || 1;
      const indPct = indFrequencies.map(f => Number(((f / indTotal) * 100).toFixed(1)));
      const fleetPct = fleetFrequencies.map(f => Number(((f / fleetTotal) * 100).toFixed(1)));

      return {
        binLabels,
        indPct,
        fleetPct,
        binWidth: Number(binWidth.toFixed(1))
      };
    }
  };

  // ════════════════════════════════════════════════════════════════════════════
  // FEATURE 3: TRUE AZIMUTH DIRECTIONAL ROSE RENDERER
  // ════════════════════════════════════════════════════════════════════════════
  const SpatialAzimuthRose = {
    /**
     * Renders a true directional compass rose on an HTML5 canvas element.
     * Maps plant azimuth angle (0°=N, 90°=E, 180°=S, 270°=W) to physical geometry.
     */
    renderCanvasCompass(canvasId, selectedPlants, plantInfoMap = DEFAULT_PLANT_INFO, activeMeans = {}) {
      const canvas = document.getElementById(canvasId);
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      // Handle high-DPI retina display
      const rect = canvas.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      const w = (rect.width > 30 ? rect.width : (canvas.width || 220));
      const h = (rect.height > 30 ? rect.height : (canvas.height || 220));
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
      ctx.scale(dpr, dpr);

      const cx = w / 2;
      const cy = h / 2;
      const maxRadius = Math.min(cx, cy) - 20;

      // Clear
      ctx.clearRect(0, 0, w, h);

      // Draw background gradient dome
      const radGrad = ctx.createRadialGradient(cx, cy, 6, cx, cy, maxRadius + 14);
      radGrad.addColorStop(0, '#f8fafc');
      radGrad.addColorStop(0.85, '#f1f5f9');
      radGrad.addColorStop(1, '#e2e8f0');
      ctx.fillStyle = radGrad;
      ctx.beginPath();
      ctx.arc(cx, cy, maxRadius + 10, 0, Math.PI * 2);
      ctx.fill();

      // Concentric circles
      ctx.strokeStyle = '#cbd5e1';
      ctx.lineWidth = 1;
      [0.33, 0.66, 1.0].forEach(frac => {
        ctx.beginPath();
        ctx.arc(cx, cy, maxRadius * frac, 0, Math.PI * 2);
        ctx.stroke();
      });

      // Cardinal axes
      const cardinals = [
        { label: 'N', angle: -Math.PI / 2, color: '#dc2626' },
        { label: 'E', angle: 0, color: '#2563eb' },
        { label: 'S', angle: Math.PI / 2, color: '#d97706' },
        { label: 'W', angle: Math.PI, color: '#7c3aed' }
      ];

      const cardFont = Math.max(9, Math.round(w / 24));
      cardinals.forEach(c => {
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        const x = cx + Math.cos(c.angle) * (maxRadius + 4);
        const y = cy + Math.sin(c.angle) * (maxRadius + 4);
        ctx.lineTo(x, y);
        ctx.strokeStyle = '#94a3b8';
        ctx.setLineDash([2, 2]);
        ctx.stroke();
        ctx.setLineDash([]);

        // Label
        ctx.font = `bold ${cardFont}px Inter, sans-serif`;
        ctx.fillStyle = c.color;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        const lx = cx + Math.cos(c.angle) * (maxRadius + 13);
        const ly = cy + Math.sin(c.angle) * (maxRadius + 13);
        ctx.fillText(c.label, lx, ly);
      });

      // Inter-cardinals NE, SE, SW, NW
      const inters = [
        { label: 'NE', deg: 45 }, { label: 'SE', deg: 135 },
        { label: 'SW', deg: 225 }, { label: 'NW', deg: 315 }
      ];
      const interFont = Math.max(7.5, Math.round(w / 30));
      inters.forEach(it => {
        const rad = (it.deg - 90) * (Math.PI / 180);
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(cx + Math.cos(rad) * maxRadius, cy + Math.sin(rad) * maxRadius);
        ctx.strokeStyle = '#e2e8f0';
        ctx.stroke();
        ctx.font = `${interFont}px JetBrains Mono, monospace`;
        ctx.fillStyle = '#94a3b8';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(it.label, cx + Math.cos(rad) * (maxRadius + 10), cy + Math.sin(rad) * (maxRadius + 10));
      });

      // Group overlapping plant angles to offset markers cleanly
      const angleGroups = {};
      const allPids = Object.keys(plantInfoMap).map(Number);
      const activeSet = new Set((selectedPlants || []).map(Number));

      allPids.forEach(pid => {
        const info = plantInfoMap[pid] || DEFAULT_PLANT_INFO[pid];
        if (!info || info.ori == null) return;
        const ori = info.ori;
        if (!angleGroups[ori]) angleGroups[ori] = [];
        angleGroups[ori].push(pid);
      });

      const nodeRadiusActive = Math.max(5.5, Math.round(w / 34));
      const nodeRadiusInactive = Math.max(3.5, Math.round(w / 50));
      const labelFont = Math.max(7.5, Math.round(w / 28));

      // Plot Plants
      Object.keys(angleGroups).forEach(oriStr => {
        const ori = Number(oriStr);
        const pids = angleGroups[ori];
        const rad = (ori - 90) * (Math.PI / 180);

        pids.forEach((pid, rank) => {
          const isActive = activeSet.has(pid);
          const radialFrac = 0.52 + (rank * 0.22);
          const rDist = maxRadius * Math.min(0.95, radialFrac);
          const px = cx + Math.cos(rad) * rDist;
          const py = cy + Math.sin(rad) * rDist;

          // Ray line to plant
          ctx.beginPath();
          ctx.moveTo(cx, cy);
          ctx.lineTo(px, py);
          ctx.strokeStyle = isActive ? 'rgba(37, 99, 235, 0.4)' : 'rgba(148, 163, 184, 0.2)';
          ctx.lineWidth = isActive ? 1.5 : 1;
          ctx.stroke();

          // Plant point badge
          ctx.beginPath();
          ctx.arc(px, py, isActive ? nodeRadiusActive : nodeRadiusInactive, 0, Math.PI * 2);
          ctx.fillStyle = isActive ? '#2563eb' : '#94a3b8';
          ctx.fill();
          ctx.strokeStyle = '#ffffff';
          ctx.lineWidth = 1.5;
          ctx.stroke();

          // Plant ID label
          ctx.font = isActive ? `bold ${labelFont}px JetBrains Mono, monospace` : `${labelFont}px JetBrains Mono, monospace`;
          ctx.fillStyle = isActive ? '#0f172a' : '#64748b';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';

          // Slight label offset perpendicular to ray
          const perpAngle = rad + Math.PI / 2;
          const labelDist = 14;
          const lx = px + Math.cos(perpAngle) * (rank % 2 === 0 ? labelDist : -labelDist);
          const ly = py + Math.sin(perpAngle) * (rank % 2 === 0 ? labelDist : -labelDist);
          ctx.fillText(`L${pid}`, lx, ly);
        });
      });

      // Center compass hub
      ctx.beginPath();
      ctx.arc(cx, cy, 5, 0, Math.PI * 2);
      ctx.fillStyle = '#0f172a';
      ctx.fill();
    }
  };

  // Export to global scope / CommonJS
  const SpatialSmoothingEngine = {
    DEFAULT_PLANT_INFO,
    mean,
    sampleStdDev,
    popStdDev,
    coefVariation,
    pearsonCorr,
    haversineDistance,
    aziToCompass,
    SpatialDataEngine,
    SpatialPortfolioEngine,
    SpatialDecorrelationEngine,
    SpatialRampRateEngine,
    SpatialAzimuthRose
  };

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = SpatialSmoothingEngine;
  } else {
    global.SpatialSmoothingEngine = SpatialSmoothingEngine;
  }

})(typeof window !== 'undefined' ? window : this);
