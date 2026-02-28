"""
app.py — Graph Coloring B&B
────────────────────────────
Entry point. Wires together session state, sidebar, theme, and page routing.

Project layout
──────────────
app.py               ← run with: streamlit run app.py
logic/
  graph.py           ← DIMACS parser
  solver.py          ← ctypes wrapper; auto-compiles C on first run
  coloring.h         ← shared C types, BBState, inline helpers
  heuristics.c/h     ← greedy clique + DSATUR (C)
  bb_sewell.c        ← Sewell (1996) B&B (C)
  bb_furini.c        ← Furini (2017) B&B with reduced-graph LB (C)
ui/
  theme.py           ← global CSS
  components.py      ← reusable HTML blocks
  plots.py           ← Plotly figure builders
  page_load.py       ← Step 1: load graph
  page_run.py        ← Step 2: live parallel execution
  page_results.py    ← Step 3: results & comparison

Requirements: gcc on PATH · pip install streamlit plotly networkx pandas numpy
"""

import streamlit as st

# ── Page config (must be first Streamlit call) ────────────────────────────
st.set_page_config(
    page_title="Graph Coloring B&B",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports after page config ─────────────────────────────────────────────
from ui.theme      import inject
from ui.components import page_header, divider
import ui.page_load    as page_load
import ui.page_run     as page_run
import ui.page_results as page_results

# ── Inject global CSS ─────────────────────────────────────────────────────
inject()

# ── Check C compilation at startup ───────────────────────────────────────
from logic.solver import _COMPILE_ERROR
if _COMPILE_ERROR:
    st.error(f"C compilation failed — algorithms will not run.\n\n{_COMPILE_ERROR}")

# ── Session state defaults ────────────────────────────────────────────────
for _k, _v in [
    ("page",            "load"),
    ("graph_data",      None),
    ("graph_filename",  None),
    ("graph_pos",       None),
    ("res_sewell",      None),
    ("res_furini",      None),
    ("temps_max",       120),
]:
    st.session_state.setdefault(_k, _v)

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙  Parameters")
    st.session_state.temps_max = st.slider(
        "Time limit per algorithm (s)",
        min_value=10, max_value=300,
        value=st.session_state.temps_max, step=10,
    )
    st.markdown(divider(), unsafe_allow_html=True)
    st.markdown("""
<div style="font-family:'IBM Plex Mono',monospace;font-size:.78rem;
            color:#4a5568;line-height:1.9;">
<div style="color:#4a90e2;margin-bottom:.3rem;">◉  Sewell (1996)</div>
DSATUR B&B<br>
+ tie-breaking: maximise<br>
shared colour options<br>
with uncoloured neighbours
<br><br>
<div style="color:#38c172;margin-bottom:.3rem;">◉  Furini (2017)</div>
DSATUR B&B<br>
+ reduced-graph LB<br>
recomputed at every node<br>
(proved χ*(DSJC125.9)=44)
<br><br>
<div style="color:#2d3748;font-size:.7rem;">
Engine: C (gcc)<br>
Format: DIMACS .col
</div>
</div>
""", unsafe_allow_html=True)

# ── Page header ───────────────────────────────────────────────────────────
st.markdown(
    page_header(
        "Graph Coloring B&B",
        "SEWELL 1996  ·  FURINI 2017  ·  C ENGINE  ·  DIMACS FORMAT",
    ),
    unsafe_allow_html=True,
)

# ── Page router ───────────────────────────────────────────────────────────
page = st.session_state.page

if   page == "load":    page_load.render()
elif page == "run":     page_run.render()
elif page == "results": page_results.render()
else:
    st.session_state.page = "load"
    st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:2rem 0 1rem;font-family:'IBM Plex Mono',monospace;
            font-size:.7rem;color:#1c2333;letter-spacing:.12em;">
  GRAPH COLORING B&B  ·  SEWELL 1996  ·  FURINI 2017  ·  C ENGINE  ·  STREAMLIT
</div>
""", unsafe_allow_html=True)
