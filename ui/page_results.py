"""
ui/page_results.py
──────────────────
Step 3: per-algorithm result tabs + head-to-head comparison tab.
"""

import streamlit as st
import pandas as pd
from ui.components import (
    step_pill, divider, stat_grid,
    algo_header, winner_banner,
)
from ui.plots import (
    fig_colored_graph, fig_progress,
    fig_color_distribution, fig_ub_convergence,
    fig_bar_compare,
)


# ── Single-algorithm tab ──────────────────────────────────────────────────

def _render_algo_tab(tab, res: dict, variant: str, line_color: str, key_prefix: str,
                     G, pos, gd: dict):
    with tab:
        st.markdown(algo_header(res["algo"], variant), unsafe_allow_html=True)

        # KPI row
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("χ(G)",            res["K"])
        c2.metric("Lower Bound",     res["LB"])
        c3.metric("Nodes Explored",  f"{res['noeuds']:,}")
        c4.metric("Branches Cut",    f"{res['coupes']:,}")
        c5.metric("Time",            f"{res['temps']:.2f}s")

        st.markdown(divider(), unsafe_allow_html=True)

        # Progress chart  +  color distribution
        left, right = st.columns([1.1, 1])
        with left:
            st.markdown("**B&B Search Progress**")
            fig_p = fig_progress(res, line_color)
            if fig_p:
                st.plotly_chart(fig_p, use_container_width=True,
                                key=f"{key_prefix}_progress")
            else:
                st.info("No progress data (solved immediately by DSATUR heuristic).")

        with right:
            st.markdown("**Color Distribution**")
            st.plotly_chart(fig_color_distribution(res),
                            use_container_width=True, key=f"{key_prefix}_dist")

        # Colored graph
        st.markdown(divider(), unsafe_allow_html=True)
        st.markdown("**Optimal Graph Coloring**")
        st.plotly_chart(fig_colored_graph(G, pos, res),
                        use_container_width=True, key=f"{key_prefix}_graph")

        # Vertex table (collapsed by default)
        with st.expander("Vertex Assignment Table", expanded=False):
            st.dataframe(pd.DataFrame({
                "Vertex": range(1, gd["n"] + 1),
                "Color":  [f"C{res['coloriage'][i]}" for i in range(gd["n"])],
                "Degree": gd["deg"],
            }), use_container_width=True, height=280)

        # Export
        lines = [
            f"Algorithm       : {res['algo']}",
            f"Graph           : {st.session_state.get('graph_filename', '—')}",
            f"Chromatic χ(G)  : {res['K']}",
            f"Lower Bound     : {res['LB']}",
            f"Initial UB      : {res['UB_init']}",
            f"Optimal proved  : {res['optimal']}",
            f"Time (s)        : {res['temps']:.4f}",
            f"Nodes explored  : {res['noeuds']:,}",
            f"Branches pruned : {res['coupes']:,}",
            f"Timeout         : {res['timeout']}",
            "", "Coloring (vertex: color):",
        ] + [f"  {i+1}: C{res['coloriage'][i]}" for i in range(gd["n"])]

        st.download_button(
            f"⬇  Export {res['algo']} results",
            data="\n".join(lines),
            file_name=f"{st.session_state.get('graph_filename','graph')}_{key_prefix}.txt",
            mime="text/plain", use_container_width=True,
        )


# ── Comparison tab ────────────────────────────────────────────────────────

def _render_comparison_tab(tab, rs: dict, rf: dict, G, pos):
    with tab:
        # Winner banner
        if   rs["K"] < rf["K"]:
            msg = f"◉ Sewell wins on quality  —  K={rs['K']} vs K={rf['K']}"
        elif rf["K"] < rs["K"]:
            msg = f"◉ Furini wins on quality  —  K={rf['K']} vs K={rs['K']}"
        elif rs["temps"] < rf["temps"]:
            msg = f"◉ Sewell faster  —  same K={rs['K']},  {rs['temps']:.2f}s vs {rf['temps']:.2f}s"
        elif rf["temps"] < rs["temps"]:
            msg = f"◉ Furini faster  —  same K={rf['K']},  {rf['temps']:.2f}s vs {rs['temps']:.2f}s"
        else:
            msg = f"◉ Perfect tie  —  K={rs['K']}, identical times"
        st.markdown(winner_banner(msg), unsafe_allow_html=True)

        # Side-by-side KPI grids
        cs, cf = st.columns(2)
        with cs:
            st.markdown(algo_header("Sewell (1996)", "s"), unsafe_allow_html=True)
            st.markdown(stat_grid([
                ("χ(G)",     rs["K"],               "#4a90e2"),
                ("Nodes",    f"{rs['noeuds']:,}",   None),
                ("Cuts",     f"{rs['coupes']:,}",   None),
                ("Time",     f"{rs['temps']:.2f}s", None),
                ("Optimal",  "Yes ✓" if rs["optimal"] else "No", None),
                ("Timeout",  "⚠" if rs["timeout"] else "—",      None),
            ]), unsafe_allow_html=True)
        with cf:
            st.markdown(algo_header("Furini (2017)", "f"), unsafe_allow_html=True)
            st.markdown(stat_grid([
                ("χ(G)",     rf["K"],               "#38c172"),
                ("Nodes",    f"{rf['noeuds']:,}",   None),
                ("Cuts",     f"{rf['coupes']:,}",   None),
                ("Time",     f"{rf['temps']:.2f}s", None),
                ("Optimal",  "Yes ✓" if rf["optimal"] else "No", None),
                ("Timeout",  "⚠" if rf["timeout"] else "—",      None),
            ]), unsafe_allow_html=True)

        st.markdown(divider(), unsafe_allow_html=True)

        # UB convergence
        st.markdown("**Upper Bound Convergence**")
        fig_conv = fig_ub_convergence(rs, rf)
        if fig_conv:
            st.plotly_chart(fig_conv, use_container_width=True, key="cmp_ub_conv")

        # Bar charts
        bc1, bc2 = st.columns(2)
        with bc1:
            st.plotly_chart(
                fig_bar_compare(rs, rf, "noeuds", "Nodes Explored"),
                use_container_width=True, key="cmp_nodes",
            )
        with bc2:
            st.plotly_chart(
                fig_bar_compare(rs, rf, "coupes", "Branches Pruned"),
                use_container_width=True, key="cmp_cuts",
            )

        # Side-by-side colored graphs
        st.markdown(divider(), unsafe_allow_html=True)
        st.markdown("**Optimal Colorings**")
        cg1, cg2 = st.columns(2)
        with cg1:
            st.plotly_chart(fig_colored_graph(G, pos, rs),
                            use_container_width=True, key="cmp_graph_s")
        with cg2:
            st.plotly_chart(fig_colored_graph(G, pos, rf),
                            use_container_width=True, key="cmp_graph_f")

        # Summary table
        st.markdown(divider(), unsafe_allow_html=True)
        st.markdown("**Summary Table**")
        st.dataframe(pd.DataFrame([
            {"Algorithm": rs["algo"], "χ(G)": rs["K"], "LB": rs["LB"],
             "UB_init": rs["UB_init"], "Nodes": rs["noeuds"],
             "Cuts": rs["coupes"], "Time (s)": round(rs["temps"], 4),
             "Optimal": rs["optimal"], "Timeout": rs["timeout"]},
            {"Algorithm": rf["algo"], "χ(G)": rf["K"], "LB": rf["LB"],
             "UB_init": rf["UB_init"], "Nodes": rf["noeuds"],
             "Cuts": rf["coupes"], "Time (s)": round(rf["temps"], 4),
             "Optimal": rf["optimal"], "Timeout": rf["timeout"]},
        ]), use_container_width=True)


# ── Page entry point ──────────────────────────────────────────────────────

def render():
    gd = st.session_state.get("graph_data")
    rs = st.session_state.get("res_sewell")
    rf = st.session_state.get("res_furini")

    if gd is None or (rs is None and rf is None):
        st.session_state.page = "load"
        st.rerun()

    G, pos = st.session_state.get("graph_pos") or (None, None)
    if G is None:
        from ui.plots import build_graph_pos
        G, pos = build_graph_pos(gd)

    st.markdown(step_pill("⬡  STEP 03 — RESULTS"), unsafe_allow_html=True)

    if st.button("← Run Again"):
        st.session_state.page = "run"
        st.rerun()

    # Build tab list
    tab_names, renderers = [], []
    if rs:
        tab_names.append("Sewell (1996)")
        renderers.append(("s", "#4a90e2", "sewell"))
    if rf:
        tab_names.append("Furini (2017)")
        renderers.append(("f", "#38c172", "furini"))
    if rs and rf:
        tab_names.append("Comparison")

    tabs = st.tabs(tab_names)

    for i, (variant, color, prefix) in enumerate(renderers):
        res = rs if variant == "s" else rf
        _render_algo_tab(tabs[i], res, variant, color, prefix, G, pos, gd)

    if rs and rf:
        _render_comparison_tab(tabs[-1], rs, rf, G, pos)

    st.markdown(divider(), unsafe_allow_html=True)
    bot_l, bot_r = st.columns(2)
    with bot_l:
        if st.button("↺  Run Again", use_container_width=True):
            st.session_state.page = "run"
            st.rerun()
    with bot_r:
        if st.button("↑  Load New File", use_container_width=True):
            st.session_state.page = "load"
            st.rerun()
