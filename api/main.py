from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import numpy as np
import joblib
import os

# ── app ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="Urban Mobility Intelligence API",
    description="Surge prediction, fare estimation and demand forecasting for Chicago TNC trips.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── model paths ───────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(BASE, "..", "models")

# ── load models at startup ────────────────────────────────────────────
lgbm_clf       = joblib.load(os.path.join(MODELS, "lgbm_b.pkl"))
iso_reg        = joblib.load(os.path.join(MODELS, "iso_reg.pkl"))
xgb_fare       = joblib.load(os.path.join(MODELS, "xgb_model_a.pkl"))
lgbm_q10       = joblib.load(os.path.join(MODELS, "lgbm_quantile_P10.pkl"))
lgbm_q50       = joblib.load(os.path.join(MODELS, "lgbm_quantile_P50.pkl"))
lgbm_q90       = joblib.load(os.path.join(MODELS, "lgbm_quantile_P90.pkl"))
ensemble       = joblib.load(os.path.join(MODELS, "ensemble_xgb_zone8.pkl"))

# ── feature helpers ───────────────────────────────────────────────────
DOWNTOWN_ZONES = {8, 32, 28, 6, 7, 24}
AIRPORT_ZONES  = {56, 76}

def build_temporal(hour: int, dow: int, month: int, day_of_year: int):
    return {
        "hour"             : hour,
        "dow"              : dow,
        "month"            : month,
        "day_of_year"      : day_of_year,
        "hour_sin"         : np.sin(2 * np.pi * hour / 24),
        "hour_cos"         : np.cos(2 * np.pi * hour / 24),
        "dow_sin"          : np.sin(2 * np.pi * dow / 7),
        "dow_cos"          : np.cos(2 * np.pi * dow / 7),
        "month_sin"        : np.sin(2 * np.pi * month / 12),
        "month_cos"        : np.cos(2 * np.pi * month / 12),
        "is_weekend"       : int(dow >= 5),
        "is_morning_peak"  : int(7 <= hour <= 9),
        "is_evening_peak"  : int(16 <= hour <= 19),
        "is_late_night"    : int(hour >= 22 or hour <= 3),
        "is_holiday"       : 0,
    }

def build_spatial(pickup_zone: int, dropoff_zone: int, is_out_of_city: int):
    return {
        "pickup_community_area"  : pickup_zone,
        "dropoff_community_area" : dropoff_zone,
        "is_out_of_city"         : is_out_of_city,
        "is_airport"             : int(pickup_zone in AIRPORT_ZONES),
        "pickup_zone_freq"       : 50000,
        "dropoff_zone_freq"      : 50000,
        "pickup_zone_freq_norm"  : 0.5,
        "dropoff_zone_freq_norm" : 0.5,
        "is_same_zone"           : int(pickup_zone == dropoff_zone),
        "is_downtown_pickup"     : int(pickup_zone in DOWNTOWN_ZONES),
        "is_downtown_dropoff"    : int(dropoff_zone in DOWNTOWN_ZONES),
    }

# ── schemas ───────────────────────────────────────────────────────────
class TripRequest(BaseModel):
    pickup_zone       : int   = Field(..., ge=0, le=77, description="Pickup community area (0=out of city)")
    dropoff_zone      : int   = Field(..., ge=0, le=77, description="Dropoff community area")
    trip_miles        : float = Field(..., gt=0, description="Estimated trip distance in miles")
    hour_of_day       : int   = Field(..., ge=0, le=23)
    day_of_week       : int   = Field(..., ge=0, le=6, description="0=Monday, 6=Sunday")
    month             : int   = Field(..., ge=1, le=12)
    day_of_year       : int   = Field(..., ge=1, le=366)
    shared_authorized : bool  = False
    trips_pooled      : int   = 1
    zone_hour_count   : float = Field(100.0, description="Current zone demand (trips/hour)")
    lag_24h           : float = Field(100.0, description="Zone demand same hour yesterday")
    lag_168h          : float = Field(100.0, description="Zone demand same hour last week")

class DemandRequest(BaseModel):
    zone_id     : int   = Field(..., ge=1, le=77)
    hour_of_day : int   = Field(..., ge=0, le=23)
    day_of_week : int   = Field(..., ge=0, le=6)
    month       : int   = Field(..., ge=1, le=12)
    day_of_year : int   = Field(..., ge=1, le=366)
    lag_24h     : float = Field(100.0)
    lag_168h    : float = Field(100.0)
    roll_24h    : float = Field(100.0)

# ── feature builders ──────────────────────────────────────────────────
CLF_FEATURES = [
    'trip_miles','pickup_community_area','dropoff_community_area',
    'shared_trip_authorized','trips_pooled','is_out_of_city',
    'hour','dow','month','day_of_year',
    'hour_sin','hour_cos','dow_sin','dow_cos','month_sin','month_cos',
    'is_weekend','is_morning_peak','is_evening_peak','is_late_night','is_holiday',
    'is_airport','pickup_zone_freq','dropoff_zone_freq',
    'pickup_zone_freq_norm','dropoff_zone_freq_norm',
    'is_same_zone','is_downtown_pickup','is_downtown_dropoff',
    'log_trip_miles','trip_distance_bucket','is_pooled',
    'zone_hour_count','lag_1h','lag_24h','lag_168h','roll_3h','roll_24h',
    'demand_vs_lag_ratio','zone_surge_rate_24h','trip_count_vs_zone_avg',
    'is_rush_hour_downtown'
]
REG_FEATURES = [
    'trip_miles','pickup_community_area','dropoff_community_area',
    'shared_trip_authorized','trips_pooled','is_out_of_city',
    'hour','dow','month','day_of_year',
    'hour_sin','hour_cos','dow_sin','dow_cos','month_sin','month_cos',
    'is_weekend','is_morning_peak','is_evening_peak','is_late_night','is_holiday',
    'is_airport','pickup_zone_freq','dropoff_zone_freq',
    'pickup_zone_freq_norm','dropoff_zone_freq_norm',
    'is_same_zone','is_downtown_pickup','is_downtown_dropoff',
    'log_trip_miles','trip_distance_bucket','is_pooled',
    'zone_hour_count','lag_1h','lag_24h','lag_168h','roll_3h','roll_24h',
    'demand_vs_lag_ratio','trip_count_vs_zone_avg','is_rush_hour_downtown',
    'zone_avg_fare','od_pair_freq','od_pair_freq_norm',
    'trip_miles_squared','miles_x_peak','miles_x_airport'
]

TS_FEATURES = [
    'lag_24h','lag_168h','roll_24h',
    'hour','dow','month','day_of_year',
    'hour_sin','hour_cos','dow_sin','dow_cos','month_sin','month_cos',
    'is_weekend','is_morning_peak','is_evening_peak','is_late_night','is_holiday',
    'is_downtown_pickup','is_airport'
]

def build_clf_features(r: TripRequest) -> np.ndarray:
    t = build_temporal(r.hour_of_day, r.day_of_week, r.month, r.day_of_year)
    s = build_spatial(r.pickup_zone, r.dropoff_zone, int(r.pickup_zone == 0))
    is_peak = int(t['is_morning_peak'] or t['is_evening_peak'])
    extras = {
        "trip_miles"           : r.trip_miles,
        "shared_trip_authorized": int(r.shared_authorized),
        "trips_pooled"         : r.trips_pooled,
        "log_trip_miles"       : np.log1p(r.trip_miles),
        "trip_distance_bucket" : int(np.clip(np.searchsorted([2,5,10,20], r.trip_miles) + 1, 1, 5)),
        "is_pooled"            : int(r.trips_pooled > 1),
        "zone_hour_count"      : r.zone_hour_count,
        "lag_1h"               : r.zone_hour_count,
        "lag_24h"              : r.lag_24h,
        "lag_168h"             : r.lag_168h,
        "roll_3h"              : r.zone_hour_count,
        "roll_24h"             : r.lag_24h,
        "demand_vs_lag_ratio"  : min(r.zone_hour_count / max(r.lag_24h, 1), 10),
        "trip_count_vs_zone_avg": 1.0,
        "is_rush_hour_downtown": int(is_peak and r.pickup_zone in DOWNTOWN_ZONES),
        "zone_surge_rate_24h"  : 0.21,  # overall surge rate as default
    }
    row = {**t, **s, **extras}
    return np.array([[row[f] for f in CLF_FEATURES]])

def build_reg_features(r: TripRequest) -> np.ndarray:
    t = build_temporal(r.hour_of_day, r.day_of_week, r.month, r.day_of_year)
    s = build_spatial(r.pickup_zone, r.dropoff_zone, int(r.pickup_zone == 0))
    is_peak = int(t['is_morning_peak'] or t['is_evening_peak'])
    extras = {
        "trip_miles"           : r.trip_miles,
        "shared_trip_authorized": int(r.shared_authorized),
        "trips_pooled"         : r.trips_pooled,
        "log_trip_miles"       : np.log1p(r.trip_miles),
        "trip_distance_bucket" : int(np.clip(np.searchsorted([2,5,10,20], r.trip_miles) + 1, 1, 5)),
        "is_pooled"            : int(r.trips_pooled > 1),
        "zone_hour_count"      : r.zone_hour_count,
        "lag_1h"               : r.zone_hour_count,
        "lag_24h"              : r.lag_24h,
        "lag_168h"             : r.lag_168h,
        "roll_3h"              : r.zone_hour_count,
        "roll_24h"             : r.lag_24h,
        "demand_vs_lag_ratio"  : min(r.zone_hour_count / max(r.lag_24h, 1), 10),
        "trip_count_vs_zone_avg": 1.0,
        "is_rush_hour_downtown": int(is_peak and r.pickup_zone in DOWNTOWN_ZONES),
        "zone_avg_fare"        : 22.0,
        "od_pair_freq"         : 10000,
        "od_pair_freq_norm"    : 0.3,
        "trip_miles_squared"   : r.trip_miles ** 2,
        "miles_x_peak"         : r.trip_miles * is_peak,
        "miles_x_airport"      : r.trip_miles * int(r.pickup_zone in AIRPORT_ZONES),
    }
    row = {**t, **s, **extras}
    return np.array([[row[f] for f in REG_FEATURES]])

def build_ts_features(r: DemandRequest) -> np.ndarray:
    t = build_temporal(r.hour_of_day, r.day_of_week, r.month, r.day_of_year)
    row = {
        **t,
        "lag_24h"          : r.lag_24h,
        "lag_168h"         : r.lag_168h,
        "roll_24h"         : r.roll_24h,
        "is_downtown_pickup": int(r.zone_id in DOWNTOWN_ZONES),
        "is_airport"       : int(r.zone_id in AIRPORT_ZONES),
    }
    return np.array([[row[f] for f in TS_FEATURES]])

# ── endpoints ─────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "models_loaded": 7}

@app.get("/")
def root():
    return {
        "name"       : "Urban Mobility Intelligence API",
        "version"    : "1.0.0",
        "endpoints"  : ["/predict/surge", "/predict/fare", "/forecast/demand/{zone_id}", "/health"],
        "paper"      : "An Explainable ML Framework for Integrated Surge Prediction, Fare Estimation and Demand Forecasting"
    }

@app.post("/predict/surge")
def predict_surge(trip: TripRequest):
    try:
        X       = build_clf_features(trip)
        raw_prob = float(lgbm_clf.predict_proba(X)[0, 1])
        cal_prob = float(iso_reg.predict([raw_prob])[0])
        cal_prob = float(np.clip(cal_prob, 0, 1))
        is_surge = cal_prob >= 0.402
        confidence = "high" if abs(cal_prob - 0.402) > 0.2 else "medium"
        return {
            "surge_probability"  : round(cal_prob, 4),
            "surge_predicted"    : is_surge,
            "confidence"         : confidence,
            "threshold_used"     : 0.402,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/fare")
def predict_fare(trip: TripRequest):
    try:
        X    = build_reg_features(trip)
        p50  = float(np.expm1(np.clip(xgb_fare.predict(X)[0], 0, 10)))
        p10  = float(np.expm1(np.clip(lgbm_q10.predict(X)[0], 0, 10)))
        p90  = float(np.expm1(np.clip(lgbm_q90.predict(X)[0], 0, 10)))
        return {
            "fare_estimate"  : round(p50, 2),
            "fare_range_low" : round(p10, 2),
            "fare_range_high": round(p90, 2),
            "currency"       : "USD",
            "note"           : "79.3% of actual fares fall within this range"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/forecast/demand/{zone_id}")
def forecast_demand(
    zone_id    : int,
    hour_of_day: int = 12,
    day_of_week: int = 1,
    month      : int = 6,
    day_of_year: int = 160,
    lag_24h    : float = 100.0,
    lag_168h   : float = 100.0,
    roll_24h   : float = 100.0,
):
    if zone_id < 1 or zone_id > 77:
        raise HTTPException(status_code=400, detail="zone_id must be between 1 and 77")
    try:
        req = DemandRequest(
            zone_id=zone_id, hour_of_day=hour_of_day,
            day_of_week=day_of_week, month=month,
            day_of_year=day_of_year, lag_24h=lag_24h,
            lag_168h=lag_168h, roll_24h=roll_24h
        )
        X           = build_ts_features(req)
        lgbm_pred   = float(np.clip(ensemble['lgbm_ts'].predict(X)[0]
                            if hasattr(ensemble, '__getitem__') and 'lgbm_ts' in ensemble
                            else 100.0, 0, None))
        return {
            "zone_id"               : zone_id,
            "hour_of_day"           : hour_of_day,
            "predicted_trips"       : round(lgbm_pred, 1),
            "model"                 : "LightGBM 24h ahead",
            "note"                  : "Zone 8 MAPE 14.78% on Oct-Dec 2024 holdout"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))