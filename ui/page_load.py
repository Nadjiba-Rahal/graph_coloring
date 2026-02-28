"""
ui/page_load.py
───────────────
Step 1: upload a DIMACS .col file, preview the graph, show initial bounds.
"""

import streamlit as st
from logic.graph import parse_dimacs
from ui.components import step_pill, stat_grid, divider
from ui.plots import build_graph_pos, fig_plain_graph


def render():
    st.markdown(step_pill("⬡  STEP 01 — LOAD GRAPH"), unsafe_allow_html=True)

    left, right = st.columns([1.4, 1])

    with left:
        uploaded = st.file_uploader(
            "Drop a DIMACS .col file here",
            type="col", label_visibility="collapsed",
        )



    if uploaded is None:
        st.info("Upload a DIMACS .col file to begin.")
        return

    try:
        with st.spinner("Parsing DIMACS…"):
            gd = parse_dimacs(uploaded.read())
    except Exception as exc:
        st.error(f"Parse error: {exc}")
        return

    st.markdown(divider(), unsafe_allow_html=True)

    # Stat grid (n, m, density + initial bounds already in graph_data)
    st.markdown(stat_grid([
        ("Vertices",    gd["n"],              None),
        ("Edges",       f"{gd['m']:,}",       None),
        ("Density",     f"{gd['density']:.1f}%", None),
    ]), unsafe_allow_html=True)

    # Graph preview
    G, pos = build_graph_pos(gd)
    st.plotly_chart(
        fig_plain_graph(G, pos, title=uploaded.name),
        use_container_width=True,
        key="graph_preview_load",
    )

    # Persist to session
    st.session_state.graph_data     = gd
    st.session_state.graph_filename = uploaded.name
    st.session_state.graph_pos      = (G, pos)
    st.session_state.res_sewell     = None
    st.session_state.res_furini     = None

    if st.button("▶  Run Algorithms →", use_container_width=True):
        st.session_state.page = "run"
        st.rerun()
