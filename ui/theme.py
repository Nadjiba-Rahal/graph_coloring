"""
ui/theme.py
───────────
Single source of truth for all Streamlit CSS.
Call inject() once at the top of app.py.
"""

import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Syne:wght@400;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Syne', sans-serif; }

/* ── backgrounds ── */
[data-testid="stAppViewContainer"] { background: #07080d; }
[data-testid="stHeader"]           { background: transparent !important; }
[data-testid="stSidebar"] {
    background: #0d1117 !important;
    border-right: 1px solid #1c2333 !important;
}

/* ── scrollbar ── */
::-webkit-scrollbar { width:6px; }
::-webkit-scrollbar-track { background:#07080d; }
::-webkit-scrollbar-thumb { background:#2d3748; border-radius:3px; }

/* ── typography ── */
h1,h2,h3,h4,h5,h6 {
    color:#e2e8f0 !important; font-family:'Syne',sans-serif !important;
    font-weight:800 !important; letter-spacing:-.02em !important;
}
p, li, .stMarkdown p { color:#8892a4 !important; }
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p { color:#8892a4 !important; }

/* ── page header ── */
.page-title {
    font-family:'Syne',sans-serif; font-size:2.6rem; font-weight:800;
    letter-spacing:-.04em; color:#e2e8f0;
    display:flex; align-items:center; gap:.6rem; margin-bottom:.2rem;
}
.page-sub {
    font-family:'IBM Plex Mono',monospace; font-size:.82rem;
    color:#4a5568; margin-bottom:2rem; letter-spacing:.04em;
}

/* ── step pill ── */
.step-pill {
    display:inline-flex; align-items:center; gap:.5rem;
    background:#0d1117; border:1px solid #1c2333; border-radius:100px;
    padding:.35rem 1rem; font-family:'IBM Plex Mono',monospace;
    font-size:.78rem; color:#4a90e2; margin-bottom:1.5rem; letter-spacing:.06em;
}

/* ── stat grid ── */
.stat-grid {
    display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr));
    gap:1px; background:#1c2333; border:1px solid #1c2333;
    border-radius:12px; overflow:hidden; margin-bottom:1.5rem;
}
.stat-cell {
    background:#0d1117; padding:1.1rem 1.2rem;
    display:flex; flex-direction:column; gap:.25rem;
}
.stat-label {
    font-family:'IBM Plex Mono',monospace; font-size:.7rem;
    color:#4a5568; text-transform:uppercase; letter-spacing:.1em;
}
.stat-value {
    font-family:'IBM Plex Mono',monospace; font-size:1.55rem;
    font-weight:600; color:#e2e8f0; line-height:1;
}

/* ── algo headers ── */
.algo-header-s {
    font-family:'Syne',sans-serif; font-size:1rem; font-weight:700;
    color:#4a90e2; display:flex; align-items:center; gap:.5rem;
    padding:.5rem .8rem; background:#0d1421; border:1px solid #1a2744;
    border-radius:8px; margin-bottom:.8rem;
}
.algo-header-f {
    font-family:'Syne',sans-serif; font-size:1rem; font-weight:700;
    color:#38c172; display:flex; align-items:center; gap:.5rem;
    padding:.5rem .8rem; background:#0d1f17; border:1px solid #1a3a2b;
    border-radius:8px; margin-bottom:.8rem;
}

/* ── race card ── */
.race-card {
    background:#0d1117; border:1px solid #1c2333; border-radius:12px;
    padding:1.2rem 1.4rem; font-family:'IBM Plex Mono',monospace; height:100%;
}
.race-title { font-size:.72rem; color:#4a5568; text-transform:uppercase; letter-spacing:.1em; margin-bottom:.8rem; }
.race-metric { font-size:2.2rem; font-weight:600; margin-bottom:.2rem; }
.race-label  { font-size:.68rem; color:#4a5568; text-transform:uppercase; letter-spacing:.08em; }
.race-s { color:#4a90e2; }
.race-f { color:#38c172; }

/* ── winner banner ── */
.winner-banner {
    background:#0d1117; border:1px solid #b7791f; border-radius:10px;
    padding:1rem 1.5rem; text-align:center; font-family:'Syne',sans-serif;
    font-size:1.1rem; font-weight:700; color:#f6c90e; margin-bottom:1.5rem;
}

/* ── divider ── */
.divider { height:1px; background:#1c2333; margin:1.8rem 0; }

/* ── buttons ── */
.stButton>button {
    background:#0d1421 !important; color:#4a90e2 !important;
    border:1px solid #1a2744 !important; border-radius:8px !important;
    font-family:'IBM Plex Mono',monospace !important; font-size:.82rem !important;
    font-weight:600 !important; padding:.6rem 1.4rem !important;
    transition:all .2s !important; letter-spacing:.04em !important;
}
.stButton>button:hover {
    background:#111d35 !important; border-color:#4a90e2 !important;
    transform:translateY(-1px) !important;
}

/* ── file uploader ── */
[data-testid="stFileUploader"] > section {
    background:#0d1117 !important; border:2px dashed #1c2333 !important;
    border-radius:12px !important;
}
[data-testid="stFileUploader"] > section:hover { border-color:#4a90e2 !important; }

/* ── metrics ── */
[data-testid="metric-container"] {
    background:#0d1117 !important; border:1px solid #1c2333 !important;
    border-radius:10px !important; padding:1rem 1.2rem !important;
}
[data-testid="metric-container"] label {
    color:#4a5568 !important; font-family:'IBM Plex Mono',monospace !important;
    font-size:.72rem !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color:#e2e8f0 !important; font-family:'IBM Plex Mono',monospace !important;
}

/* ── tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background:#0d1117 !important; border-bottom:1px solid #1c2333 !important; gap:0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family:'IBM Plex Mono',monospace !important; font-size:.8rem !important;
    color:#4a5568 !important; padding:.6rem 1.2rem !important;
    border-radius:0 !important; background:transparent !important;
}
.stTabs [aria-selected="true"] {
    color:#4a90e2 !important; border-bottom:2px solid #4a90e2 !important;
    background:transparent !important;
}

/* ── alerts ── */
.stAlert { border-radius:8px !important; font-family:'IBM Plex Mono',monospace !important; font-size:.82rem !important; }

/* ── dataframe ── */
[data-testid="stDataFrame"] { border:1px solid #1c2333 !important; border-radius:8px !important; }
</style>
"""


def inject():
    """Inject global CSS into the Streamlit app."""
    st.markdown(_CSS, unsafe_allow_html=True)
