"""
ui/theme.py
───────────
Call inject() once at the top of app.py.
"""

import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── backgrounds ── */
[data-testid="stAppViewContainer"] { background: #f5f5f7; }
[data-testid="stHeader"]           { background: transparent !important; }
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e0e0e0 !important;
}

/* ── scrollbar ── */
::-webkit-scrollbar { width:6px; }
::-webkit-scrollbar-track { background:#f5f5f7; }
::-webkit-scrollbar-thumb { background:#d0d0d0; border-radius:3px; }

/* ── typography ── */
h1,h2,h3,h4,h5,h6 {
    color:#1a1a1a !important; font-family:'Inter',sans-serif !important;
    font-weight:800 !important; letter-spacing:-.02em !important;
}
p, li, .stMarkdown p { color:#555555 !important; }
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p { color:#555555 !important; }

/* ── page header ── */
.page-title {
    font-family:'Inter',sans-serif; font-size:2.6rem; font-weight:800;
    letter-spacing:-.04em; color:#1a1a1a;
    display:flex; align-items:center; gap:.6rem; margin-bottom:.2rem;
}
.page-sub {
    font-family:'Inter',sans-serif; font-size:.82rem;
    color:#999999; margin-bottom:2rem; letter-spacing:.04em;
}

/* ── step pill ── */
.step-pill {
    display:inline-flex; align-items:center; gap:.5rem;
    background:#ffffff; border:1px solid #e0e0e0; border-radius:100px;
    padding:.35rem 1rem; font-family:'Inter',sans-serif;
    font-size:.78rem; color:#0066cc; margin-bottom:1.5rem; letter-spacing:.06em;
}

/* ── stat grid ── */
.stat-grid {
    display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr));
    gap:1px; background:#e0e0e0; border:1px solid #e0e0e0;
    border-radius:12px; overflow:hidden; margin-bottom:1.5rem;
}
.stat-cell {
    background:#ffffff; padding:1.1rem 1.2rem;
    display:flex; flex-direction:column; gap:.25rem;
}
.stat-label {
    font-family:'Inter',sans-serif; font-size:.7rem;
    color:#999999; text-transform:uppercase; letter-spacing:.1em;
}
.stat-value {
    font-family:'Inter',sans-serif; font-size:1.55rem;
    font-weight:600; color:#1a1a1a; line-height:1;
}

/* ── algo headers ── */
.algo-header-s {
    font-family:'Inter',sans-serif; font-size:1rem; font-weight:700;
    color:#0066cc; display:flex; align-items:center; gap:.5rem;
    padding:.5rem .8rem; background:#f0f6ff; border:1px solid #d6e4f5;
    border-radius:8px; margin-bottom:.8rem;
}
.algo-header-f {
    font-family:'Inter',sans-serif; font-size:1rem; font-weight:700;
    color:#009933; display:flex; align-items:center; gap:.5rem;
    padding:.5rem .8rem; background:#f0fff4; border:1px solid #d6f5e8;
    border-radius:8px; margin-bottom:.8rem;
}

/* ── race card ── */
.race-card {
    background:#ffffff; border:1px solid #e0e0e0; border-radius:12px;
    padding:1.2rem 1.4rem; font-family:'Inter',sans-serif; height:100%;
}
.race-title { font-size:.72rem; color:#999999; text-transform:uppercase; letter-spacing:.1em; margin-bottom:.8rem; }
.race-metric { font-size:2.2rem; font-weight:600; margin-bottom:.2rem; }
.race-label  { font-size:.68rem; color:#999999; text-transform:uppercase; letter-spacing:.08em; }
.race-s { color:#0066cc; }
.race-f { color:#009933; }

/* ── winner banner ── */
.winner-banner {
    background:#fff9f0; border:1px solid #ffd166; border-radius:10px;
    padding:1rem 1.5rem; text-align:center; font-family:'Inter',sans-serif;
    font-size:1.1rem; font-weight:700; color:#d97706; margin-bottom:1.5rem;
}

/* ── divider ── */
.divider { height:1px; background:#e0e0e0; margin:1.8rem 0; }

/* ── buttons ── */
.stButton>button {
    background:#ffffff !important; color:#0066cc !important;
    border:1px solid #0066cc !important; border-radius:8px !important;
    font-family:'Inter',sans-serif !important; font-size:.82rem !important;
    font-weight:600 !important; padding:.6rem 1.4rem !important;
    transition:all .2s !important; letter-spacing:.04em !important;
}
.stButton>button:hover {
    background:#f0f6ff !important; border-color:#0066cc !important;
    transform:translateY(-1px) !important;
}

/* ── file uploader ── */
[data-testid="stFileUploader"] > section {
    background:#ffffff !important; border:2px dashed #e0e0e0 !important;
    border-radius:12px !important;
}
[data-testid="stFileUploader"] > section:hover { border-color:#0066cc !important; }

/* ── metrics ── */
[data-testid="metric-container"] {
    background:#ffffff !important; border:1px solid #e0e0e0 !important;
    border-radius:10px !important; padding:1rem 1.2rem !important;
}
[data-testid="metric-container"] label {
    color:#999999 !important; font-family:'Inter',sans-serif !important;
    font-size:.72rem !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color:#1a1a1a !important; font-family:'Inter',sans-serif !important;
}

/* ── tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background:#ffffff !important; border-bottom:1px solid #e0e0e0 !important; gap:0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family:'Inter',sans-serif !important; font-size:.8rem !important;
    color:#999999 !important; padding:.6rem 1.2rem !important;
    border-radius:0 !important; background:transparent !important;
}
.stTabs [aria-selected="true"] {
    color:#0066cc !important; border-bottom:2px solid #0066cc !important;
    background:transparent !important;
}

/* ── alerts ── */
.stAlert { border-radius:8px !important; font-family:'Inter',sans-serif !important; font-size:.82rem !important; }

/* ── dataframe ── */
[data-testid="stDataFrame"] { border:1px solid #e0e0e0 !important; border-radius:8px !important; }
</style>
"""


def inject():
    """Inject global CSS into the Streamlit app."""
    st.markdown(_CSS, unsafe_allow_html=True)
