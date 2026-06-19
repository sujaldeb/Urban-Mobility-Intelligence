import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import os

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Urban Mobility Intelligence",
    page_icon="🚖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

API_BASE = "https://urban-mobility-intelligence-1.onrender.com"
PLOTS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "plots")

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background-color: #0a0f1e !important;
    font-family: 'Inter', sans-serif;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="block-container"] { padding-top: 1.5rem; max-width: 1200px; }

/* ── Tab bar ── */
[data-testid="stTabs"] > div:first-child {
    border-bottom: 1px solid rgba(255,255,255,0.08);
    gap: 0;
}
button[data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: #64748b !important;
    padding: 0.6rem 1.4rem !important;
    border-radius: 0 !important;
    background: transparent !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.2s ease;
}
button[data-baseweb="tab"]:hover { color: #cbd5e1 !important; }
button[data-baseweb="tab"][aria-selected="true"] {
    color: #ffffff !important;
    border-bottom: 2px solid #7c3aed !important;
    background: transparent !important;
}
[data-testid="stTabsContent"] { padding-top: 1.5rem; }

/* ── Glass card ── */
.glass-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
}
.glass-card-accent {
    background: rgba(124,58,237,0.08);
    border: 1px solid rgba(124,58,237,0.25);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
}

/* ── KPI card ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.85rem;
    margin-bottom: 1.2rem;
}
.kpi-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    border-radius: 12px 0 0 12px;
}
.kpi-purple::before  { background: #7c3aed; }
.kpi-cyan::before    { background: #06b6d4; }
.kpi-orange::before  { background: #f97316; }
.kpi-green::before   { background: #10b981; }
.kpi-label {
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #64748b;
    margin-bottom: 0.3rem;
}
.kpi-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1;
    font-family: 'JetBrains Mono', monospace;
}
.kpi-sub {
    font-size: 0.72rem;
    color: #475569;
    margin-top: 0.25rem;
}

/* ── Section heading ── */
.section-eyebrow {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #7c3aed;
    margin-bottom: 0.3rem;
}
.section-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 0.5rem;
    line-height: 1.3;
}
.section-body {
    font-size: 0.88rem;
    color: #94a3b8;
    line-height: 1.65;
}

/* ── Hero ── */
.hero-wrap {
    background: linear-gradient(135deg, rgba(124,58,237,0.12) 0%, rgba(6,182,212,0.06) 100%);
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 18px;
    padding: 2.4rem 2.8rem;
    margin-bottom: 1.6rem;
    position: relative;
    overflow: hidden;
}
.hero-wrap::after {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(124,58,237,0.15) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-size: 2.1rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.2;
    margin-bottom: 0.5rem;
}
.hero-sub {
    font-size: 0.95rem;
    color: #94a3b8;
    max-width: 600px;
    line-height: 1.6;
}
.hero-badge {
    display: inline-block;
    background: rgba(124,58,237,0.18);
    border: 1px solid rgba(124,58,237,0.35);
    border-radius: 20px;
    padding: 0.25rem 0.85rem;
    font-size: 0.72rem;
    font-weight: 600;
    color: #a78bfa;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}

/* ── Results table ── */
.results-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.84rem;
}
.results-table th {
    text-align: left;
    padding: 0.6rem 0.9rem;
    color: #64748b;
    font-weight: 500;
    font-size: 0.72rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}
.results-table td {
    padding: 0.65rem 0.9rem;
    color: #cbd5e1;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}
.results-table tr.best td {
    color: #ffffff;
    font-weight: 600;
}
.results-table tr.best td:first-child { color: #a78bfa; }
.mono { font-family: 'JetBrains Mono', monospace; }

/* ── Link button ── */
.link-btn {
    display: inline-block;
    text-decoration: none;
    padding: 0.45rem 1.1rem;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 500;
    margin-right: 0.6rem;
    transition: all 0.2s;
}
.link-btn-purple {
    background: rgba(124,58,237,0.15);
    border: 1px solid rgba(124,58,237,0.35);
    color: #a78bfa;
}
.link-btn-cyan {
    background: rgba(6,182,212,0.1);
    border: 1px solid rgba(6,182,212,0.3);
    color: #67e8f9;
}

/* ── Prediction result ── */
.pred-box {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-top: 1rem;
}
.pred-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: #ffffff;
}
.pred-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #475569;
    margin-bottom: 0.2rem;
}
.badge-surge {
    display: inline-block;
    background: rgba(249,115,22,0.15);
    border: 1px solid rgba(249,115,22,0.35);
    color: #fb923c;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    margin-left: 0.5rem;
}
.badge-clear {
    display: inline-block;
    background: rgba(16,185,129,0.12);
    border: 1px solid rgba(16,185,129,0.3);
    color: #34d399;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    margin-left: 0.5rem;
}
.badge-high {
    display: inline-block;
    background: rgba(124,58,237,0.12);
    border: 1px solid rgba(124,58,237,0.3);
    color: #a78bfa;
    padding: 0.15rem 0.6rem;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 500;
}

/* ── Divider ── */
.divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin: 1.6rem 0;
}

/* ── Input overrides ── */
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] select {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: white !important;
}
label { font-size: 0.82rem !important; color: #94a3b8 !important; }

/* ── Streamlit button ── */
[data-testid="stButton"] button {
    background: linear-gradient(135deg, #7c3aed, #6d28d9) !important;
    border: none !important;
    border-radius: 9px !important;
    color: white !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 1.8rem !important;
    transition: opacity 0.2s !important;
}
[data-testid="stButton"] button:hover { opacity: 0.85 !important; }

/* ── Findings chip ── */
.finding-chip {
    background: rgba(255,255,255,0.03);
    border-left: 3px solid #7c3aed;
    border-radius: 0 8px 8px 0;
    padding: 0.65rem 1rem;
    margin-bottom: 0.6rem;
    font-size: 0.84rem;
    color: #94a3b8;
}
.finding-chip strong { color: #e2e8f0; }
</style>
""", unsafe_allow_html=True)





import base64

def show_plot(filename, caption=None):
    path = os.path.join(PLOTS_DIR, filename)
    if os.path.exists(path):
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        ext = filename.split(".")[-1]
        mime = "image/png" if ext == "png" else "image/jpeg"
        st.markdown(f'<img src="data:{mime};base64,{data}" style="width:100%;border-radius:8px;">', unsafe_allow_html=True)
        if caption:
            st.markdown(f'<div style="font-size:0.72rem;color:#475569;margin-top:0.3rem;">{caption}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.02);border:1px dashed rgba(255,255,255,0.1);
        border-radius:10px;padding:2rem;text-align:center;color:#475569;font-size:0.8rem;">
            {filename} — place in <code>data/plots/</code>
        </div>""", unsafe_allow_html=True)


def api_post(endpoint, payload):
    try:
        r = requests.post(f"{API_BASE}{endpoint}", json=payload, timeout=15)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.Timeout:
        return None, "Request timed out — the API may be cold-starting on Render (free tier). Try again in 30s."
    except Exception as e:
        return None, str(e)


def api_get(endpoint):
    try:
        r = requests.get(f"{API_BASE}{endpoint}", timeout=15)
        r.raise_for_status()
        return r.json(), None
    except requests.exceptions.Timeout:
        return None, "Request timed out — the API may be cold-starting on Render (free tier). Try again in 30s."
    except Exception as e:
        return None, str(e)


# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:1.2rem;">
    <div style="width:36px;height:36px;background:linear-gradient(135deg,#7c3aed,#06b6d4);
    border-radius:9px;display:flex;align-items:center;justify-content:center;
    font-size:1.1rem;">🚖</div>
    <div>
        <div style="font-size:0.72rem;color:#475569;font-weight:500;
        letter-spacing:0.08em;text-transform:uppercase;">Urban Mobility Intelligence</div>
        <div style="font-size:0.82rem;color:#64748b;">Chicago TNC 2024 · 18.3M trips</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "  Overview  ",
    "  Surge Analysis  ",
    "  Fare Estimation  ",
    "  Demand Forecasting  ",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    # Hero
    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-badge">IEEE Access · Manuscript In Preparation</div>
        <div class="hero-title">An Explainable ML Framework<br>for Urban Ride-Hailing</div>
        <div class="hero-sub">
            A unified three-task system — surge classification, fare estimation, and
            demand forecasting — trained on 18.3 million Chicago TNC trips from 2024.
            Deployed as a live REST API with SHAP-based spatial equity analysis.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Links
    st.markdown("""
    <div style="margin-bottom:1.6rem;">
        <a class="link-btn link-btn-purple" href="https://github.com/sujaldeb/Urban-Mobility-Intelligence" target="_blank">
            GitHub Repository
        </a>
        <a class="link-btn link-btn-cyan" href="https://urban-mobility-intelligence-1.onrender.com/docs" target="_blank">
            Live API Docs
        </a>
    </div>
    """, unsafe_allow_html=True)

    # KPI grid
    st.markdown("""
    <div class="kpi-grid">
        <div class="kpi-card kpi-purple">
            <div class="kpi-label">Surge AUC</div>
            <div class="kpi-value">0.9468</div>
            <div class="kpi-sub">LightGBM + Isotonic calibration</div>
        </div>
        <div class="kpi-card kpi-purple">
            <div class="kpi-label">Surge F1</div>
            <div class="kpi-value">0.7676</div>
            <div class="kpi-sub">threshold 0.402 · Brier 0.0675</div>
        </div>
        <div class="kpi-card kpi-cyan">
            <div class="kpi-label">Fare R²</div>
            <div class="kpi-value">0.8327</div>
            <div class="kpi-sub">XGBoost · RMSE $7.66</div>
        </div>
        <div class="kpi-card kpi-cyan">
            <div class="kpi-label">Interval Coverage</div>
            <div class="kpi-value">79.3%</div>
            <div class="kpi-sub">P10–P90 quantile · width $13.79</div>
        </div>
        <div class="kpi-card kpi-green">
            <div class="kpi-label">Demand MAPE</div>
            <div class="kpi-value">14.78%</div>
            <div class="kpi-sub">Stacking ensemble · 24h horizon</div>
        </div>
        <div class="kpi-card kpi-orange">
            <div class="kpi-label">Training rows</div>
            <div class="kpi-value">18.3M</div>
            <div class="kpi-sub">366 days · 50K stratified/day</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    hr = "<hr class='divider'>"
    st.markdown(hr, unsafe_allow_html=True)

    # Key findings
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="section-eyebrow">Key Findings</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">What the data revealed</div>', unsafe_allow_html=True)
        findings = [
            ("<strong>Pickup zone</strong> drives 37% of surge prediction importance (SHAP)", ""),
            ("<strong>Income–surge correlation:</strong> r = −0.159 — lower-income zones face disproportionate surge exposure", ""),
            ("<strong>ETA sensitivity:</strong> adding trip duration to fare regression yields ΔR² = −0.0002 — no value at booking time", ""),
            ("<strong>Spatial granularity plateau:</strong> spatial-temporal features improve MAPE by only −0.03pp over 24h baseline", ""),
            ("<strong>Calibration gain:</strong> isotonic regression reduced Brier score by 25% (0.0901 → 0.0675)", ""),
        ]
        for text, _ in findings:
            st.markdown(f'<div class="finding-chip">{text}</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="section-eyebrow">Architecture</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">System overview</div>', unsafe_allow_html=True)
        show_plot("24_unified_results.png")

    st.markdown(hr, unsafe_allow_html=True)

    # Novel contributions
    st.markdown('<div class="section-eyebrow">Novel Contributions</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">7 contributions toward IEEE Access</div>', unsafe_allow_html=True)
    contribs = [
        ("01", "Unified 3-task framework", "First paper combining surge, fare, and demand on a single TNC dataset"),
        ("02", "Calibrated surge probabilities", "Isotonic regression, Brier 0.0675 — suitable for production dispatch"),
        ("03", "Quantile fare intervals", "79.31% empirical coverage, P10/P50/P90 — actionable uncertainty estimates"),
        ("04", "SHAP spatial equity", "r = −0.159 income–SHAP correlation quantifies algorithmic inequality"),
        ("05", "ETA sensitivity analysis", "Rigorous ablation proving duration adds zero predictive value at booking"),
        ("06", "Spatial-temporal analysis", "Community-area granularity caps improvement, guiding future sensor investment"),
        ("07", "Post-pandemic 2024 data", "18.3M rows across full calendar year — largest public TNC study to date"),
    ]
    cols = st.columns(3)
    for i, (num, title, desc) in enumerate(contribs):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="glass-card" style="min-height:110px;">
                <div style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;
                color:#7c3aed;font-weight:600;margin-bottom:0.4rem;">{num}</div>
                <div style="font-size:0.88rem;font-weight:600;color:#e2e8f0;
                margin-bottom:0.3rem;">{title}</div>
                <div style="font-size:0.78rem;color:#64748b;line-height:1.5;">{desc}</div>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — SURGE ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-eyebrow">Task 1</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Surge Classification</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-body">Binary prediction of surge pricing at trip-request time. No trip duration used — only features available at booking.</div><br>', unsafe_allow_html=True)

    # Results table
    st.markdown("""
    <div class="glass-card">
        <div class="section-eyebrow" style="margin-bottom:0.8rem;">Model Comparison</div>
        <table class="results-table">
            <thead><tr><th>Model</th><th>AUC</th><th>Surge F1</th><th>Brier</th></tr></thead>
            <tbody>
                <tr><td>Logistic Regression</td>
                    <td class="mono">0.9139</td><td class="mono">0.6800</td><td class="mono">—</td></tr>
                <tr><td>Random Forest</td>
                    <td class="mono">0.9340</td><td class="mono">0.7200</td><td class="mono">—</td></tr>
                <tr><td>LightGBM A (47 features)</td>
                    <td class="mono">0.9485</td><td class="mono">0.7426</td><td class="mono">—</td></tr>
                <tr><td>LightGBM B (42 features)</td>
                    <td class="mono">0.9468</td><td class="mono">0.7394</td><td class="mono">—</td></tr>
                <tr class="best"><td>LightGBM B + Calibration</td>
                    <td class="mono">0.9468</td><td class="mono">0.7676</td><td class="mono">0.0675</td></tr>
            </tbody>
        </table>
        <div style="font-size:0.73rem;color:#475569;margin-top:0.8rem;">
            Highlighted row = deployed model. Optimal threshold: 0.402 (cost-aware PR analysis).
            Calibration improved Brier score 25%: 0.0901 → 0.0675.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Plots row
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-eyebrow" style="margin-bottom:0.5rem;">Calibration</div>', unsafe_allow_html=True)
        show_plot("07_calibration.png", "Reliability diagram before/after isotonic calibration")
    with col2:
        st.markdown('<div class="section-eyebrow" style="margin-bottom:0.5rem;">Threshold Optimization</div>', unsafe_allow_html=True)
        show_plot("08_threshold_optimization.png", "PR curve + F1 vs. threshold")

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="section-eyebrow" style="margin-bottom:0.5rem;">SHAP Global Importance</div>', unsafe_allow_html=True)
        show_plot("09_shap_importance.png", "Top features by mean |SHAP| value")
    with col4:
        st.markdown('<div class="section-eyebrow" style="margin-bottom:0.5rem;">Spatial Equity</div>', unsafe_allow_html=True)
        show_plot("11_equity_analysis.png", "Income vs. surge SHAP — r = −0.159")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Live predictor
    st.markdown("""
    <div class="glass-card-accent">
        <div class="section-eyebrow">Live Prediction</div>
        <div class="section-title" style="font-size:1.1rem;margin-bottom:0.2rem;">Surge Probability Estimator</div>
        <div class="section-body" style="font-size:0.81rem;">
            Calls the live Render API — may take 10–30s on first request (cold start).
        </div>
    </div>
    """, unsafe_allow_html=True)

    s_col1, s_col2, s_col3 = st.columns(3)
    with s_col1:
        pickup_zone   = st.number_input("Pickup Zone", 1, 77, 8, key="s_pickup")
        dropoff_zone  = st.number_input("Dropoff Zone", 1, 77, 32, key="s_dropoff")
        trip_miles    = st.number_input("Trip Miles", 0.1, 50.0, 3.5, step=0.1, key="s_miles")
        shared_auth   = st.checkbox("Shared trip authorized", value=False, key="s_shared")
    with s_col2:
        hour_of_day   = st.number_input("Hour of Day (0–23)", 0, 23, 17, key="s_hour")
        day_of_week   = st.number_input("Day of Week (0=Mon)", 0, 6, 4, key="s_dow")
        month         = st.number_input("Month", 1, 12, 6, key="s_month")
        day_of_year   = st.number_input("Day of Year", 1, 366, 160, key="s_doy")
    with s_col3:
        zone_hour_count = st.number_input("Zone-Hour Trip Count", 0, 2000, 350, key="s_zhc")
        lag_24h         = st.number_input("Lag 24h Count", 0, 2000, 280, key="s_l24")
        lag_168h        = st.number_input("Lag 168h Count", 0, 2000, 310, key="s_l168")
        trips_pooled    = st.number_input("Trips Pooled", 1, 4, 1, key="s_pooled")

    if st.button("Predict Surge", key="surge_btn"):
        payload = {
            "pickup_zone": int(pickup_zone),
            "dropoff_zone": int(dropoff_zone),
            "trip_miles": float(trip_miles),
            "hour_of_day": int(hour_of_day),
            "day_of_week": int(day_of_week),
            "month": int(month),
            "day_of_year": int(day_of_year),
            "shared_authorized": bool(shared_auth),
            "trips_pooled": int(trips_pooled),
            "zone_hour_count": int(zone_hour_count),
            "lag_24h": int(lag_24h),
            "lag_168h": int(lag_168h),
        }
        with st.spinner("Calling API..."):
            result, err = api_post("/predict/surge", payload)

        if err:
            st.error(err)
        else:
            prob      = result.get("surge_probability", 0)
            predicted = result.get("surge_predicted", False)
            conf      = result.get("confidence", "—")
            threshold = result.get("threshold_used", 0.402)

            surge_badge = '<span class="badge-surge">SURGE</span>' if predicted else '<span class="badge-clear">CLEAR</span>'
            conf_badge  = f'<span class="badge-high">{conf} confidence</span>'

            st.markdown(f"""
            <div class="pred-box">
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1.2rem;">
                    <div>
                        <div class="pred-label">Surge Probability</div>
                        <div class="pred-value" style="color:{'#fb923c' if prob>threshold else '#34d399'};">
                            {prob:.1%}
                        </div>
                    </div>
                    <div>
                        <div class="pred-label">Prediction</div>
                        <div style="margin-top:0.4rem;font-size:1.1rem;font-weight:600;color:#e2e8f0;">
                            {'Surge Active' if predicted else 'No Surge'} {surge_badge}
                        </div>
                    </div>
                    <div>
                        <div class="pred-label">Confidence · Threshold</div>
                        <div style="margin-top:0.4rem;">{conf_badge}</div>
                        <div style="font-size:0.76rem;color:#475569;margin-top:0.3rem;">
                            threshold = {threshold}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Mini gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob * 100,
                number={"suffix": "%", "font": {"color": "white", "size": 32}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#334155", "tickwidth": 1},
                    "bar": {"color": "#f97316" if predicted else "#10b981", "thickness": 0.25},
                    "bgcolor": "rgba(0,0,0,0)",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0, threshold * 100], "color": "rgba(16,185,129,0.08)"},
                        {"range": [threshold * 100, 100], "color": "rgba(249,115,22,0.08)"},
                    ],
                    "threshold": {
                        "line": {"color": "#7c3aed", "width": 2},
                        "thickness": 0.75,
                        "value": threshold * 100,
                    },
                },
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=200,
                margin=dict(t=20, b=10, l=20, r=20),
                font={"color": "white", "family": "Inter"},
            )
            st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — FARE ESTIMATION
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-eyebrow">Task 2</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Fare Estimation</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-body">Point prediction (XGBoost) combined with P10/P50/P90 quantile intervals. Trip duration excluded — ΔR² = −0.0002 confirms zero information gain at booking time.</div><br>', unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">
        <div class="section-eyebrow" style="margin-bottom:0.8rem;">Model Comparison</div>
        <table class="results-table">
            <thead><tr><th>Model</th><th>R²</th><th>RMSE</th><th>Notes</th></tr></thead>
            <tbody>
                <tr><td>Ridge Regression</td>
                    <td class="mono">0.7589</td><td class="mono">$9.11</td><td>Baseline</td></tr>
                <tr class="best"><td>XGBoost Model A</td>
                    <td class="mono">0.8327</td><td class="mono">$7.66</td><td>Primary — deployed</td></tr>
                <tr><td>XGBoost Model B (+ ETA)</td>
                    <td class="mono">0.8325</td><td class="mono">$7.66</td><td>ΔR² = −0.0002</td></tr>
                <tr><td>LightGBM P50 (quantile)</td>
                    <td class="mono">0.8234</td><td class="mono">$7.91</td><td>Interval midpoint</td></tr>
            </tbody>
        </table>
        <div style="font-size:0.73rem;color:#475569;margin-top:0.8rem;">
            Quantile coverage: 79.31% of actual fares fall inside P10–P90. Avg interval width: $13.79.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-eyebrow" style="margin-bottom:0.5rem;">Quantile Intervals</div>', unsafe_allow_html=True)
        show_plot("14_quantile_intervals.png", "P10/P50/P90 fare intervals across trip distance")
    with col2:
        st.markdown('<div class="section-eyebrow" style="margin-bottom:0.5rem;">SHAP — Fare Drivers</div>', unsafe_allow_html=True)
        show_plot("16_shap_regression.png", "Global SHAP importance for fare regression")

    # ETA finding callout
    st.markdown("""
    <div class="glass-card" style="border-left:3px solid #06b6d4;border-radius:0 14px 14px 0;
    background:rgba(6,182,212,0.05);border-color:rgba(6,182,212,0.25);">
        <div style="font-size:0.72rem;font-weight:600;letter-spacing:0.08em;
        text-transform:uppercase;color:#06b6d4;margin-bottom:0.4rem;">ETA Sensitivity Finding</div>
        <div style="font-size:0.88rem;color:#e2e8f0;font-weight:500;">
            Adding trip duration to the model yields ΔR² = −0.0002 — effectively zero.
        </div>
        <div style="font-size:0.8rem;color:#64748b;margin-top:0.3rem;line-height:1.55;">
            This is a key ablation result: real-world fare APIs cannot know trip duration at booking time.
            The finding validates excluding ETA from production fare models, and demonstrates that
            distance + zone features fully capture fare variance.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Live fare estimator
    st.markdown("""
    <div class="glass-card-accent">
        <div class="section-eyebrow">Live Prediction</div>
        <div class="section-title" style="font-size:1.1rem;margin-bottom:0.2rem;">Fare Interval Estimator</div>
        <div class="section-body" style="font-size:0.81rem;">
            Returns P10 / P50 / P90 quantile estimates. 79.3% of real fares fall within the range.
        </div>
    </div>
    """, unsafe_allow_html=True)

    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        f_pickup       = st.number_input("Pickup Zone", 1, 77, 8, key="f_pickup")
        f_dropoff      = st.number_input("Dropoff Zone", 1, 77, 32, key="f_dropoff")
        f_miles        = st.number_input("Trip Miles", 0.1, 50.0, 5.0, step=0.1, key="f_miles")
    with f_col2:
        f_hour         = st.number_input("Hour of Day (0–23)", 0, 23, 17, key="f_hour")
        f_dow          = st.number_input("Day of Week (0=Mon)", 0, 6, 4, key="f_dow")
        f_month        = st.number_input("Month", 1, 12, 6, key="f_month")
    with f_col3:
        f_shared       = st.checkbox("Shared trip authorized", value=False, key="f_shared")
        f_pooled       = st.number_input("Trips Pooled", 1, 4, 1, key="f_pooled")
        f_zhc          = st.number_input("Zone-Hour Trip Count", 0, 2000, 350, key="f_zhc")

    if st.button("Estimate Fare", key="fare_btn"):
        payload = {
            "pickup_zone": int(f_pickup),
            "dropoff_zone": int(f_dropoff),
            "trip_miles": float(f_miles),
            "hour_of_day": int(f_hour),
            "day_of_week": int(f_dow),
            "month": int(f_month),
            "shared_authorized": bool(f_shared),
            "trips_pooled": int(f_pooled),
            "zone_hour_count": int(f_zhc),
        }
        with st.spinner("Calling API..."):
            result, err = api_post("/predict/fare", payload)

        if err:
            st.error(err)
        else:
            p50   = result.get("fare_estimate", 0)
            p10   = result.get("fare_range_low", 0)
            p90   = result.get("fare_range_high", 0)
            note  = result.get("note", "")

            st.markdown(f"""
            <div class="pred-box">
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1.2rem;">
                    <div>
                        <div class="pred-label">Fare Estimate (P50)</div>
                        <div class="pred-value">${p50:.2f}</div>
                    </div>
                    <div>
                        <div class="pred-label">Low Estimate (P10)</div>
                        <div class="pred-value" style="color:#10b981;">${p10:.2f}</div>
                    </div>
                    <div>
                        <div class="pred-label">High Estimate (P90)</div>
                        <div class="pred-value" style="color:#f97316;">${p90:.2f}</div>
                    </div>
                </div>
                <div style="font-size:0.76rem;color:#475569;margin-top:0.8rem;">{note}</div>
            </div>
            """, unsafe_allow_html=True)

            # Interval bar chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=["P10 (Low)", "P50 (Estimate)", "P90 (High)"],
                y=[p10, p50, p90],
                marker_color=["#10b981", "#7c3aed", "#f97316"],
                marker_line_width=0,
                text=[f"${v:.2f}" for v in [p10, p50, p90]],
                textposition="outside",
                textfont={"color": "white", "size": 12},
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=240,
                margin=dict(t=20, b=10, l=10, r=10),
                yaxis=dict(
                    showgrid=True, gridcolor="rgba(255,255,255,0.05)",
                    tickprefix="$", tickfont={"color": "#64748b"}, zeroline=False,
                ),
                xaxis=dict(tickfont={"color": "#94a3b8"}),
                font={"color": "white", "family": "Inter"},
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — DEMAND FORECASTING
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-eyebrow">Task 3</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Demand Forecasting</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-body">24-hour ahead trip demand forecasting per community area. Stacking ensemble beats Prophet baseline by 14.79pp MAPE. Zone 8 (Near North Side) is the primary benchmark.</div><br>', unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card">
        <div class="section-eyebrow" style="margin-bottom:0.8rem;">Model Comparison</div>
        <table class="results-table">
            <thead><tr><th>Model</th><th>Zone 8 MAPE</th><th>Notes</th></tr></thead>
            <tbody>
                <tr><td>Prophet Baseline</td>
                    <td class="mono">29.57%</td><td>Statistical baseline</td></tr>
                <tr><td>Prophet + Lag Regressors</td>
                    <td class="mono">22.37%</td><td>External regressors added</td></tr>
                <tr><td>LightGBM 24h</td>
                    <td class="mono">15.37%</td><td>Primary ML model</td></tr>
                <tr><td>LightGBM Spatial-Temporal</td>
                    <td class="mono">15.08%</td><td>Neighbor zone features</td></tr>
                <tr class="best"><td>Stacking Ensemble</td>
                    <td class="mono">14.78%</td><td>Below 15% target — deployed</td></tr>
            </tbody>
        </table>
        <div style="font-size:0.73rem;color:#475569;margin-top:0.8rem;">
            Top-5 zone mean MAPE: 19.11%. Volume–MAPE correlation: r = −0.445 (busier zones forecast more accurately).
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-eyebrow" style="margin-bottom:0.5rem;">Model Comparison Summary</div>', unsafe_allow_html=True)
        show_plot("22_ts_comparison.png", "MAPE comparison across all time-series models")
    with col2:
        st.markdown('<div class="section-eyebrow" style="margin-bottom:0.5rem;">Multi-Zone Performance</div>', unsafe_allow_html=True)
        show_plot("21_multizone_forecast.png", "MAPE by community area — volume correlation visible")

    col3, col4 = st.columns(2)
    with col3:
        st.markdown('<div class="section-eyebrow" style="margin-bottom:0.5rem;">STL Decomposition</div>', unsafe_allow_html=True)
        show_plot("19_stl_decomposition.png", "Zone 8 trend / weekly / daily / residual components")
    with col4:
        st.markdown('<div class="section-eyebrow" style="margin-bottom:0.5rem;">Spatial-Temporal Analysis</div>', unsafe_allow_html=True)
        show_plot("23_spatial_temporal.png", "Neighbor-zone features — marginal improvement at CA granularity")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # Live forecast
    st.markdown("""
    <div class="glass-card-accent">
        <div class="section-eyebrow">Live Prediction</div>
        <div class="section-title" style="font-size:1.1rem;margin-bottom:0.2rem;">24-Hour Demand Forecast</div>
        <div class="section-body" style="font-size:0.81rem;">
            Enter any Chicago community area zone (1–77) to retrieve the 24h demand forecast.
        </div>
    </div>
    """, unsafe_allow_html=True)

    d_col1, d_col2 = st.columns([1, 2])
    with d_col1:
        zone_id = st.number_input("Community Area Zone ID", 1, 77, 8, key="d_zone")
        st.markdown("""
        <div style="font-size:0.75rem;color:#475569;margin-top:0.3rem;line-height:1.5;">
            Zone 8 = Near North Side<br>
            Zone 32 = Loop<br>
            Zone 76 = O'Hare Airport
        </div>
        """, unsafe_allow_html=True)

    with d_col1:
        forecast_btn = st.button("Get Forecast", key="forecast_btn")

    if forecast_btn:
        with st.spinner("Fetching 24-hour forecast..."):
            result, err = api_get(f"/forecast/demand/{int(zone_id)}")

        if err:
            st.error(err)
        else:
            zone_out  = result.get("zone_id", zone_id)
            hour      = result.get("hour_of_day", 0)
            trips     = result.get("predicted_trips", 0)
            model_name = result.get("model", "LightGBM 24h ahead")
            note      = result.get("note", "")

            st.markdown(f"""
            <div class="pred-box">
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1.2rem;">
                    <div>
                        <div class="pred-label">Zone</div>
                        <div class="pred-value" style="font-size:1.5rem;">{zone_out}</div>
                    </div>
                    <div>
                        <div class="pred-label">Forecast Hour</div>
                        <div class="pred-value" style="font-size:1.5rem;">{hour}:00</div>
                    </div>
                    <div>
                        <div class="pred-label">Predicted Trips</div>
                        <div class="pred-value" style="font-size:1.5rem;color:#7c3aed;">{int(trips):,}</div>
                    </div>
                </div>
                <div style="font-size:0.76rem;color:#475569;margin-top:0.8rem;">
                    Model: {model_name} · {note}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div style="margin-top:3rem;padding-top:1.2rem;
    border-top:1px solid rgba(255,255,255,0.06);
    display:flex;justify-content:space-between;align-items:center;">
        <div style="font-size:0.76rem;color:#334155;">
            Urban Mobility Intelligence Platform · Chicago TNC 2024 · 18.3M trips
        </div>
        <div style="font-size:0.76rem;color:#334155;">
            <a href="https://github.com/sujaldeb/Urban-Mobility-Intelligence"
            style="color:#475569;text-decoration:none;">GitHub</a>
            &nbsp;·&nbsp;
            <a href="https://urban-mobility-intelligence-1.onrender.com/docs"
            style="color:#475569;text-decoration:none;">API Docs</a>
            &nbsp;·&nbsp;
            <a href="https://www.sujaldeb.in" style="color:#475569;text-decoration:none;">Portfolio</a>
        </div>
    </div>
    """, unsafe_allow_html=True)