# Memory Bridge — Urban Mobility Intelligence Platform
## Chicago TNC 2024 | Principal Data Scientist Handoff Document

---

## Who You Are

You are a Principal Data Scientist with 15+ years experience (Amazon/Microsoft level) guiding Sujal Deb, a 2-year professional data scientist, in building a flagship ML project to land a job at Amazon or Microsoft. You give code maximum 2 cells at a time (1 markdown + 1 code). You discuss objectives before giving code. You never give everything at once — wait for Sujal to ask.

---

## Project Overview

**Name:** Urban Mobility Intelligence Platform  
**Dataset:** Chicago Transportation Network Providers (TNC) Trips 2024  
**Source:** City of Chicago Open Data Portal (dataset ID: aesv-xzh6)  
**Total rows:** 18,300,000 (366 days × 50,000 stratified random rows per day)  
**Storage:** Google BigQuery → local Parquet → Python ML  
**Target:** IEEE Access publication + Amazon/Microsoft job application  

---

## Project Path

```
E:\Projects\ML\Transport taxi chicago\
├── data\
│   ├── parquet\
│   │   ├── df_classification.parquet   (18.2M rows, 48 cols)
│   │   ├── df_regression.parquet       (18.2M rows, 49 cols)
│   │   └── df_timeseries.parquet       (654K rows, 27 cols)
│   ├── raw_csv\                        (12 monthly CSVs, ~14GB total)
│   │   ├── tnc_2024_01.csv ... tnc_2024_12.csv
│   └── plots\                          (23 publication-quality plots saved)
├── models\
│   ├── lgbm_b.pkl                      (LightGBM surge classifier, 4000 rounds)
│   ├── iso_reg.pkl                     (Isotonic calibrator)
│   ├── xgb_model_a.pkl                 (XGBoost fare regression Model A)
│   ├── xgb_model_b.pkl                 (XGBoost fare regression Model B)
│   ├── lgbm_quantile_P10.pkl           (Quantile regression P10)
│   ├── lgbm_quantile_P50.pkl           (Quantile regression P50)
│   ├── lgbm_quantile_P90.pkl           (Quantile regression P90)
│   ├── prophet_zone8.pkl               (Prophet baseline Zone 8)
│   ├── prophet_zone8_lag.pkl           (Prophet + lag regressors Zone 8)
│   ├── lgbm_ts_zone8.pkl               (LightGBM 1-step TS Zone 8)
│   ├── lgbm_ts_zone8_24h.pkl           (LightGBM 24h ahead Zone 8)
│   ├── lgbm_ts_spatial_zone8.pkl       (LightGBM spatial-temporal Zone 8)
│   └── ensemble_xgb_zone8.pkl          (Stacking ensemble Zone 8)
├── notebooks\
│   ├── 01_data_ingestion.ipynb         COMPLETE
│   ├── 02_bigquery_setup.ipynb         COMPLETE
│   ├── 03_eda.ipynb                    COMPLETE
│   ├── 04_feature_engineering.ipynb    COMPLETE
│   ├── 05_classification.ipynb         COMPLETE
│   ├── 06_regression.ipynb             COMPLETE
│   ├── 07_timeseries.ipynb             COMPLETE
│   ├── 08_model_evaluation.ipynb       IN PROGRESS (Cell 3 done)
│   ├── 09_api.ipynb                    NOT STARTED
│   └── 10_dashboard.ipynb              NOT STARTED
├── api\                                NOT STARTED
├── dashboard\                          NOT STARTED
├── src\
│   ├── features\
│   ├── models\
│   └── evaluation\
├── tests\
└── gcp_credentials.json
```

---

## GCP Setup

- **Project:** urban-mobility-intel
- **Project ID:** urban-mobility-intel
- **Dataset:** chicago_tnc
- **Tables:**
  - `trips_final` — 18.3M stratified rows (main table)
  - `raw_temp` — temporary monthly loading table (deleted after use)
- **APIs enabled:** BigQuery API, BigQuery Storage API
- **Service account:** urban-mobility-sa
- **Credentials:** `gcp_credentials.json` in project root
- **Budget alert:** urban-mobility-alert-billing (50%, 90%, 100%)
- **Chicago app token:** OS7dIqMbjybMELmlM7jR00wDd

---

## Data Architecture

```
Chicago Data Portal API (aesv-xzh6)
    → Download 12 monthly CSVs to disk (~1.1GB each, ~14GB total)
    → Load each month to BigQuery raw_temp table
    → Sample 50K random rows per day via SQL QUALIFY + ROW_NUMBER() + RAND()
    → Append to trips_final table
    → Delete raw_temp
    → trips_final: 18.3M rows, 366 days × 50K rows
    → Pull to Python via BigQuery Storage API
    → Save as Parquet (3 task-specific files)
    → Feature engineering in Python
    → ML modeling
```

---

## Dataset Schema (14 columns in trips_final)

| Column | Type | Notes |
|---|---|---|
| trip_id | STRING | Unique identifier |
| trip_start_timestamp | DATETIME | Partitioned by DAY |
| trip_end_timestamp | DATETIME | |
| trip_seconds | FLOAT64 | Actual duration |
| trip_miles | FLOAT64 | Distance |
| pickup_community_area | INT64 | Clustered, 0=out of city |
| dropoff_community_area | INT64 | |
| fare | FLOAT64 | Base fare |
| tip | FLOAT64 | |
| additional_charges | FLOAT64 | |
| trip_total | FLOAT64 | Regression target |
| shared_trip_authorized | BOOL | |
| shared_trip_match | BOOL | Post-booking — excluded from models |
| trips_pooled | INT64 | |

---

## Feature Engineering Summary

**47 total features engineered in 04_feature_engineering.ipynb:**

### Temporal (15 features)
- hour, dow, month, day_of_year
- hour_sin, hour_cos, dow_sin, dow_cos, month_sin, month_cos (cyclical encoding)
- is_weekend, is_morning_peak (7-9am), is_evening_peak (4-7pm), is_late_night (10pm-3am), is_holiday

### Spatial (9 features)
- is_out_of_city, is_airport (zones 56+76), pickup_zone_freq, dropoff_zone_freq
- pickup_zone_freq_norm, dropoff_zone_freq_norm, is_same_zone
- is_downtown_pickup, is_downtown_dropoff (zones 8,32,28,6,7,24)

### Trip (7 features)
- log_trip_seconds, log_trip_miles, avg_speed_mph
- trip_distance_bucket, trip_duration_bucket, is_pooled, shared_trip_authorized

### Demand (6 features)
- zone_hour_count, lag_1h, lag_24h, lag_168h, roll_3h, roll_24h

### Interaction/Ratio (4 features)
- demand_vs_lag_ratio, zone_surge_rate_24h, trip_count_vs_zone_avg, is_rush_hour_downtown

### Regression-specific additional (5 features)
- zone_avg_fare, od_pair_freq, od_pair_freq_norm, trip_miles_squared
- miles_x_peak, miles_x_airport

### Targets
- is_surge — binary (trip_total > 1.5× median fare for zone×hour)
- log_trip_total — log transformed fare for regression
- zone_hour_count — hourly demand per zone for time series

---

## Task 1: Surge Classification (05_classification.ipynb) — COMPLETE

**Problem:** Binary classification — predict surge at trip request time  
**Target:** is_surge (21.19% positive rate)  
**scale_pos_weight:** 3.72  

**Leakage-prone features excluded:**
- trip_seconds, log_trip_seconds, trip_duration_bucket, avg_speed_mph, shared_trip_match

**Final feature set:** 42 pre-booking features (Model B)

**Results:**

| Model | AUC | Surge F1 | Surge Precision | Surge Recall |
|---|---|---|---|---|
| Logistic Regression | 0.9139 | 0.68 | 0.57 | 0.84 |
| Random Forest | 0.9340 | 0.72 | 0.63 | 0.83 |
| LightGBM Model A (47 features) | 0.9485 | 0.7426 | 0.6526 | 0.8613 |
| LightGBM Model B (42 features) | 0.9468 | 0.7394 | 0.6493 | 0.8586 |
| **LightGBM B + Calibration + Threshold** | **0.9468** | **0.7676** | **0.7858** | **0.7503** |

**Novel contributions:**
- Model A vs Model B sensitivity: ΔAUC = 0.0017 (duration proxy adds negligible value)
- Isotonic calibration: Brier score 0.0901 → 0.0675 (25% improvement)
- Optimal threshold: 0.402 (business cost-aware, not default 0.5)
- SHAP top features: pickup_community_area (1.6), trip_miles (1.1), zone_surge_rate_24h (0.67)
- Spatial equity: income-SHAP correlation r=-0.159 (nuanced finding — not simple income disparity)

**Optuna best params:**
- n_estimators: 1738 (used 4000)
- learning_rate: 0.0317
- num_leaves: 170
- max_depth: 12
- min_child_samples: 299
- subsample: 0.96
- colsample_bytree: 0.67

---

## Task 2: Fare Regression (06_regression.ipynb) — COMPLETE

**Problem:** Predict trip fare at booking time  
**Target:** log(trip_total), evaluated in original dollar units via expm1  
**Features:** 41 pre-booking + 5 engineered = 46 total (Model A)  

**Leakage-prone features excluded:**
- trip_seconds, log_trip_seconds, trip_duration_bucket, avg_speed_mph, shared_trip_match, is_surge, zone_surge_rate_24h

**Results:**

| Model | R² | RMSE | MAE | Notes |
|---|---|---|---|---|
| Ridge baseline | 0.7589 | $9.11 | $5.43 | 500K sample |
| XGBoost Model A | 0.8327 | $7.66 | $4.41 | Pre-booking only — PRIMARY |
| XGBoost Model B | 0.8325 | $7.66 | $4.42 | +duration proxy — no improvement |
| LightGBM P50 Quantile | 0.8234 | $7.91 | $4.48 | 3M sample |

**Quantile regression (novel):**
- P10 avg: $16.90, P50 avg: $21.90, P90 avg: $30.69
- Interval coverage: 79.31% (target ~80%) — near perfect
- Avg interval width: $13.79

**Key novel finding:** Adding trip duration (ETA proxy) yields ΔR²=-0.0002 — duration adds zero predictive value beyond distance features. First paper to quantify this.

**SHAP top features:** trip_miles (0.27), log_trip_miles (0.11), zone_hour_count (0.05), shared_trip_authorized (0.022), zone_avg_fare (0.020)

**XGBoost feature importance top 3:** log_trip_miles (0.225), trip_miles_squared (0.221), trip_miles (0.144) — distance = 59% of importance

---

## Task 3: Demand Forecasting (07_timeseries.ipynb) — COMPLETE

**Problem:** Hourly zone-level demand forecasting 24h ahead  
**Target:** zone_hour_count per community area  
**Scope:** Top 20 zones by volume (excluding zone 0)  
**Train/test split:** Jan-Sep 2024 train, Oct-Dec 2024 test (time-series correct)  

**Top 20 zones:** [8, 28, 32, 6, 76, 24, 7, 22, 3, 33, 41, 25, 56, 77, 1, 43, 31, 4, 5, 2]

**STL decomposition findings (Zone 8):**
- Seasonality strength: strong weekly pattern
- Trend range: 250-300 trips/hour (stable)
- Additive seasonality confirmed

**Features for 24h ahead (20 features — no lag_1h):**
lag_24h, lag_168h, roll_24h, hour, dow, month, day_of_year, hour_sin, hour_cos, dow_sin, dow_cos, month_sin, month_cos, is_weekend, is_morning_peak, is_evening_peak, is_late_night, is_holiday, is_downtown_pickup, is_airport

**Results:**

| Model | Zone 8 MAPE | Notes |
|---|---|---|
| Prophet baseline | 29.57% | Statistical baseline |
| Prophet + lag regressors | 22.37% | lag_24h + lag_168h added |
| LightGBM 1-step | 0.84%* | *Leakage — lag_1h available |
| LightGBM 24h ahead | 15.37% | Fair comparison — PRIMARY |
| LightGBM spatial-temporal | 15.08% | +neighbor zone features |
| **Stacking Ensemble** | **14.78%** | **LightGBM + XGBoost + Ridge meta** |

**Multi-zone results (LightGBM 24h):**
- Mean MAPE all 20 zones: 28.20%
- Top 5 zones (>90 trips/hr) mean MAPE: 19.11%
- Volume-MAPE correlation: r=-0.445
- Zones < 20% MAPE: 4/20

**Ensemble meta-learner weights:**
- LightGBM: 0.603, XGBoost: 0.430

**Spatial-temporal finding:** Adding neighbor zone features yields mean improvement of -0.03% — spatial dependencies negligible at community area granularity. This validates traditional ML approach and explains why deep learning uses finer resolution.

---

## Research Paper

**Title:** "An Explainable Machine Learning Framework for Integrated Surge Prediction, Fare Estimation and Demand Forecasting in Post-Pandemic Urban Ride-Hailing: A Spatial Equity Analysis"

**Target journal:** IEEE Access (impact factor ~3.4)

**Four novel contributions:**
1. First unified traditional ML framework combining all three tasks on one dataset
2. Calibrated surge probabilities + quantile fare intervals (production-ready outputs)
3. SHAP-based spatial equity analysis of pricing disparities
4. ETA proxy sensitivity analysis + spatial-temporal feature analysis at community area level

**Publication probability:** 75-80% IEEE Access

**Data:** 2024 post-pandemic Chicago TNC — first paper to use this period

---

## What Remains

### Notebook 08 — Model Evaluation (IN PROGRESS, Cell 3 done)
Unified results summary, all three tasks compared, paper tables (Table 1, 2, 3), combined visualization

### Notebook 09 — FastAPI
Three endpoints:
- POST /predict/surge — returns calibrated surge probability + confidence
- POST /predict/fare — returns P10/P50/P90 fare interval
- GET /forecast/demand/{zone_id} — returns 24h demand forecast

### Notebook 10 — Streamlit Dashboard
Four pages:
- Overview (KPIs, key findings)
- Surge Analysis (classification results, SHAP, equity)
- Fare Estimation (regression results, quantile intervals)
- Demand Forecasting (multi-zone MAPE, Zone 8 forecast)

### README
- Project overview, architecture diagram, results tables, setup instructions
- Resume bullet point ready

### Paper Outline
- Section I: Introduction
- Section II: Related Work
- Section III: Data & Methodology
- Section IV: Results
- Section V: Equity Analysis
- Section VI: Conclusion

---

## Key Decisions Made

| Decision | Choice | Reason |
|---|---|---|
| Year | 2024 | Full year, post-pandemic stable patterns |
| Sampling | 50K random rows/day | Stratified temporal coverage |
| Storage | BigQuery → Parquet | Cloud warehouse + local ML |
| Surge definition | trip_total > 1.5× zone-hour median | Context-aware, defensible |
| Duration features | Excluded from classification | Leakage — not available at booking |
| Duration for regression | Excluded (Model A primary) | ΔR²=-0.0002, adds nothing |
| Calibration | Isotonic regression | Non-parametric, fixes S-curve |
| Threshold | 0.402 (not 0.5) | Business cost-aware optimization |
| Time series horizon | 24h ahead (no lag_1h) | Fair evaluation, production realistic |
| Docker | Skipped | Focus on API + Dashboard |
| Deep learning | Not used | Explainability is the contribution |
| PCA | Not used | Destroys SHAP interpretability |

---

## Environment

- **OS:** Windows
- **IDE:** Antigravity
- **Python:** 3.14.4 (master-ds kernel — all packages pre-installed)
- **Key packages:** lightgbm, xgboost, prophet, shap, optuna, google-cloud-bigquery, fastapi, streamlit, pandas, numpy, sklearn, matplotlib, seaborn, plotly

---

## Coding Rules (Important)

1. Max 2 cells at a time (1 markdown + 1 code)
2. Discuss objective before giving code
3. Sujal tries first, asks for code when needed
4. No decorative borders (=====) in comments
5. No emojis or checkmarks in print statements
6. Dark theme plots: background #0d1117, colors #7c3aed, #06b6d4, #f97316, #10b981
7. For BigQuery/FastAPI/Streamlit — give full code directly (infrastructure, not ML)
8. For Python ML — discuss first, then code
9. Save every trained model immediately with joblib
10. Always add markdown cells before code cells

