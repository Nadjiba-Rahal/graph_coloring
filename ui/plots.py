"""
ui/plots.py
───────────
All Plotly figure builders.  No Streamlit calls here — functions return
go.Figure objects; the page modules call st.plotly_chart().
"""

import numpy as np
import networkx as nx
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

COLOR_PALETTE = [
    "#4a90e2", "#38c172", "#e2a84a", "#e24a6e",
    "#9b59b6", "#1abc9c", "#e74c3c", "#3498db",
    "#f39c12", "#2ecc71", "#e056fd", "#00b8d9",
]

_BASE = dict(
    plot_bgcolor ="#0d1117",
    paper_bgcolor="#07080d",
    font=dict(color="#8892a4", family="IBM Plex Mono, monospace", size=11),
)


def _dark_axes():
    return dict(showgrid=True, gridcolor="#1c2333", zeroline=False, tickfont=dict(size=10))


def _no_axes():
    return dict(showgrid=False, zeroline=False, showticklabels=False)


# ── Graph layout ──────────────────────────────────────────────────────────

def build_graph_pos(graph_data: dict):
    """Return (nx.Graph, pos_dict) for the graph."""
    n, voisins = graph_data["n"], graph_data["voisins"]
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for u in range(n):
        for v in voisins[u]:
            if u < v:
                G.add_edge(u, v)
    pos = nx.spring_layout(G, k=2.2, iterations=60, seed=42)
    return G, pos


def _edge_trace(G, pos):
    ex, ey = [], []
    for u, v in G.edges():
        x0, y0 = pos[u]; x1, y1 = pos[v]
        ex += [x0, x1, None]; ey += [y0, y1, None]
    return go.Scatter(x=ex, y=ey, mode="lines",
                      line=dict(width=1, color="#1c2f4a"),
                      hoverinfo="skip", showlegend=False)


def _plain_node_trace(G, pos):
    xy = np.array([pos[v] for v in G.nodes()])
    return go.Scatter(
        x=xy[:, 0], y=xy[:, 1], mode="markers",
        marker=dict(size=10, color="#1a3a5c",
                    line=dict(width=1.5, color="#4a90e2")),
        text=[f"V{v}  deg={G.degree(v)}" for v in G.nodes()],
        hoverinfo="text", showlegend=False,
    )


def _colored_traces(n, colors, pos, k):
    traces = []
    for c in range(k):
        nodes = [i for i in range(n) if i < len(colors) and colors[i] == c]
        if not nodes:
            continue
        xy = np.array([pos[v] for v in nodes])
        traces.append(go.Scatter(
            x=xy[:, 0], y=xy[:, 1],
            mode="markers+text",
            marker=dict(size=13, color=COLOR_PALETTE[c % len(COLOR_PALETTE)],
                        line=dict(width=1.5, color="#07080d")),
            text=[str(i) for i in nodes],
            textposition="middle center",
            textfont=dict(color="white", size=9, family="IBM Plex Mono, monospace"),
            hovertemplate=f"Vertex %{{text}}  Color {c}<extra></extra>",
            name=f"Color {c}",
        ))
    return traces


# ── Public figure builders ────────────────────────────────────────────────

def fig_plain_graph(G, pos, title: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(_edge_trace(G, pos))
    fig.add_trace(_plain_node_trace(G, pos))
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>",
                   font=dict(color="#e2e8f0", size=13, family="Syne, sans-serif")),
        height=420, showlegend=False,
        margin=dict(b=10, l=10, r=10, t=50),
        xaxis=_no_axes(), yaxis=_no_axes(),
        **_BASE,
    )
    return fig


def fig_colored_graph(G, pos, res: dict) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(_edge_trace(G, pos))
    for tr in _colored_traces(len(res["coloriage"]), res["coloriage"], pos, res["K"]):
        fig.add_trace(tr)
    fig.update_layout(
        title=dict(text=f"<b>{res['algo']}  —  χ(G) = {res['K']}</b>",
                   font=dict(color="#e2e8f0", size=13, family="Syne, sans-serif")),
        height=440, showlegend=True,
        margin=dict(b=10, l=10, r=10, t=50),
        xaxis=_no_axes(), yaxis=_no_axes(),
        legend=dict(bgcolor="#0d1117", bordercolor="#1c2333", borderwidth=1,
                    font=dict(color="#8892a4", size=10)),
        **_BASE,
    )
    return fig


def fig_progress(res: dict, line_color: str) -> go.Figure | None:
    kpi = [r for r in res.get("historique_kpi", []) if r.get("UB") is not None]
    if not kpi:
        return None
    df = pd.DataFrame(kpi)
    h = line_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    fill_rgba = f"rgba({r},{g},{b},0.07)"

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=df["temps"], y=df["UB"], name="UB",
                   line=dict(color=line_color, width=2.5),
                   fill="tozeroy", fillcolor=fill_rgba),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=df["temps"], y=df["noeuds"], name="Nodes",
                   line=dict(color="#4a5568", width=1.5, dash="dot")),
        secondary_y=True,
    )
    if res["LB"]:
        fig.add_hline(y=res["LB"], line_dash="dash", line_color="#e24a6e",
                      line_width=1, annotation_text="LB",
                      annotation_position="right", secondary_y=False)
    fig.update_layout(
        height=340, margin=dict(l=50, r=50, t=20, b=40),
        legend=dict(bgcolor="#0d1117", bordercolor="#1c2333",
                    borderwidth=1, font=dict(size=10)),
        **_BASE,
    )
    fig.update_xaxes(title_text="Time (s)", gridcolor="#1c2333", title_font=dict(size=10))
    fig.update_yaxes(title_text="UB",    gridcolor="#1c2333", title_font=dict(size=10), secondary_y=False)
    fig.update_yaxes(title_text="Nodes", gridcolor="#1c2333", title_font=dict(size=10), secondary_y=True)
    return fig


def fig_color_distribution(res: dict) -> go.Figure:
    k      = res["K"]
    counts = np.bincount(res["coloriage"], minlength=k)
    pal    = [COLOR_PALETTE[i % len(COLOR_PALETTE)] for i in range(k)]
    fig = go.Figure(go.Bar(
        x=[f"C{i}" for i in range(k)], y=counts,
        marker_color=pal, text=counts, textposition="outside",
        textfont=dict(size=9, color="#8892a4"),
    ))
    fig.update_layout(
        showlegend=False, height=340,
        margin=dict(l=40, r=20, t=20, b=40),
        yaxis=dict(gridcolor="#1c2333", title="Vertices"),
        **_BASE,
    )
    return fig


def fig_ub_convergence(rs: dict, rf: dict) -> go.Figure | None:
    kpi_s = [r for r in rs.get("historique_kpi", []) if r.get("UB") is not None]
    kpi_f = [r for r in rf.get("historique_kpi", []) if r.get("UB") is not None]
    if not kpi_s and not kpi_f:
        return None
    fig = go.Figure()
    if kpi_s:
        df = pd.DataFrame(kpi_s)
        fig.add_trace(go.Scatter(x=df["temps"], y=df["UB"], name="Sewell UB",
                                 line=dict(color="#4a90e2", width=2.5)))
    if kpi_f:
        df = pd.DataFrame(kpi_f)
        fig.add_trace(go.Scatter(x=df["temps"], y=df["UB"], name="Furini UB",
                                 line=dict(color="#38c172", width=2.5)))
    fig.update_layout(
        height=360, margin=dict(l=50, r=20, t=20, b=40),
        legend=dict(bgcolor="#0d1117", bordercolor="#1c2333",
                    borderwidth=1, font=dict(size=11)),
        xaxis=dict(title="Time (s)", gridcolor="#1c2333"),
        yaxis=dict(title="Upper Bound", gridcolor="#1c2333"),
        **_BASE,
    )
    return fig


def fig_bar_compare(rs: dict, rf: dict, field: str, title: str) -> go.Figure:
    vals = [rs[field], rf[field]]
    fig = go.Figure(go.Bar(
        x=["Sewell", "Furini"], y=vals,
        marker_color=["#4a90e2", "#38c172"],
        text=[f"{v:,}" for v in vals],
        textposition="outside", textfont=dict(size=10),
    ))
    fig.update_layout(
        showlegend=False, height=300,
        margin=dict(l=40, r=20, t=30, b=40),
        title=dict(text=f"<b>{title}</b>", font=dict(color="#e2e8f0", size=12)),
        yaxis=dict(gridcolor="#1c2333"),
        **_BASE,
    )
    return fig
