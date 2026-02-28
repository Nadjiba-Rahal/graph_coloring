"""
ui/page_run.py
──────────────
Step 2: live dual-execution racing view.
Both algorithms run in parallel threads (ctypes releases the GIL).
"""

import time
import threading
import streamlit as st
from logic.solver import solve_sewell, solve_furini
from ui.components import (
    step_pill, divider,
    race_panel, race_panel_idle,
    algo_header,
)


def render():
    gd = st.session_state.get("graph_data")
    if gd is None:
        st.session_state.page = "load"
        st.rerun()

    fname    = st.session_state.get("graph_filename", "graph.col")
    tmax     = st.session_state.get("temps_max", 120)

    st.markdown(step_pill("⬡  STEP 02 — LIVE EXECUTION"), unsafe_allow_html=True)
    st.markdown(f"""
<div style="font-family:'IBM Plex Mono',monospace;font-size:.8rem;
            color:#4a5568;margin-bottom:1.2rem;">
  Graph: <span style="color:#e2e8f0">{fname}</span>
  &nbsp;·&nbsp; n={gd['n']} &nbsp;·&nbsp; m={gd['m']:,}
  &nbsp;·&nbsp; time limit={tmax}s
</div>
""", unsafe_allow_html=True)

    # ── Action buttons ────────────────────────────────────────────────
    b1, b2, b3 = st.columns([1, 1, 1.5])
    run_s    = b1.button("▶  Sewell only",   use_container_width=True)
    run_f    = b2.button("▶  Furini only",   use_container_width=True)
    run_both = b3.button("▶  Run Both & Compare ↓", use_container_width=True)

    st.markdown(divider(), unsafe_allow_html=True)

    # ── Side-by-side race panel headers ──────────────────────────────
    h1, h2 = st.columns(2)
    h1.markdown(algo_header("Sewell (1996)", "s"), unsafe_allow_html=True)
    h2.markdown(algo_header("Furini (2017)", "f"), unsafe_allow_html=True)

    col_s, col_f = st.columns(2)
    ph_s = col_s.empty()
    ph_f = col_f.empty()
    ph_status = st.empty()

    # ── Helpers ───────────────────────────────────────────────────────
    def _render_panels(live_s, live_f):
        ph_s.markdown(race_panel("SEWELL (1996)", "race-s", live_s), unsafe_allow_html=True)
        ph_f.markdown(race_panel("FURINI (2017)", "race-f", live_f), unsafe_allow_html=True)

    def _run_both_parallel():
        live_s: dict = {}
        live_f: dict = {}

        res_s = [None]
        res_f = [None]

        def _ts():
            res_s[0] = solve_sewell(gd, tmax, live_s)

        def _tf():
            res_f[0] = solve_furini(gd, tmax, live_f)

        ts = threading.Thread(target=_ts, daemon=True)
        tf = threading.Thread(target=_tf, daemon=True)
        ts.start(); tf.start()
        ph_status.info("⟳  Both algorithms running in parallel (C engine)…")

        while ts.is_alive() or tf.is_alive():
            _render_panels(live_s, live_f)
            time.sleep(0.2)

        ts.join(); tf.join()
        live_s["done"] = True
        live_f["done"] = True
        _render_panels(live_s, live_f)
        ph_status.success("✓  Both algorithms finished.")
        st.session_state.res_sewell = res_s[0]
        st.session_state.res_furini = res_f[0]

    def _run_one(solver_fn, key, live_label, color_cls, ph_active, ph_idle, idle_label):
        live: dict = {}
        ph_idle.markdown(race_panel_idle(idle_label), unsafe_allow_html=True)
        res = [None]

        def _t():
            res[0] = solver_fn(gd, tmax, live)

        t = threading.Thread(target=_t, daemon=True)
        t.start()
        while t.is_alive():
            ph_active.markdown(race_panel(live_label, color_cls, live), unsafe_allow_html=True)
            time.sleep(0.2)
        t.join()
        live["done"] = True
        ph_active.markdown(race_panel(live_label, color_cls, live), unsafe_allow_html=True)
        st.session_state[key] = res[0]

    # ── Dispatch ──────────────────────────────────────────────────────
    if run_both:
        _run_both_parallel()
        st.session_state.page = "results"
        st.rerun()

    elif run_s:
        _run_one(solve_sewell, "res_sewell",
                 "SEWELL (1996)", "race-s", ph_s, ph_f, "FURINI (2017)")
        st.session_state.page = "results"
        st.rerun()

    elif run_f:
        _run_one(solve_furini, "res_furini",
                 "FURINI (2017)", "race-f", ph_f, ph_s, "SEWELL (1996)")
        st.session_state.page = "results"
        st.rerun()

    else:
        # Show existing results in panels if available
        rs = st.session_state.get("res_sewell")
        rf = st.session_state.get("res_furini")
        if rs:
            ph_s.markdown(race_panel("SEWELL (1996)", "race-s", {
                "done": True, "UB": rs["K"], "LB": rs["LB"],
                "noeuds": rs["noeuds"], "coupes": rs["coupes"], "temps": rs["temps"],
            }), unsafe_allow_html=True)
        else:
            ph_s.markdown(race_panel_idle("SEWELL (1996)"), unsafe_allow_html=True)
        if rf:
            ph_f.markdown(race_panel("FURINI (2017)", "race-f", {
                "done": True, "UB": rf["K"], "LB": rf["LB"],
                "noeuds": rf["noeuds"], "coupes": rf["coupes"], "temps": rf["temps"],
            }), unsafe_allow_html=True)
        else:
            ph_f.markdown(race_panel_idle("FURINI (2017)"), unsafe_allow_html=True)

        if rs or rf:
            if st.button("▶  View Results →", use_container_width=True):
                st.session_state.page = "results"
                st.rerun()

    st.markdown(divider(), unsafe_allow_html=True)
    if st.button("← Load New File"):
        st.session_state.page = "load"
        st.rerun()
