"""
ui/components.py
────────────────
Reusable HTML building blocks (live race panel, stat grid, headers).
All functions return HTML strings; caller uses st.markdown(..., unsafe_allow_html=True).
"""


def race_panel(label: str, color_cls: str, live: dict) -> str:
    """Live race panel showing real-time B&B stats for one algorithm."""
    ub     = live.get("UB",     "—")
    lb     = live.get("LB",     "—")
    nodes  = live.get("noeuds", 0)
    coupes = live.get("coupes", 0)
    t      = live.get("temps",  0.0)
    done   = live.get("done",   False)
    status = "✓  Done" if done else "⟳  Running"
    s_col  = "#38c172" if done else "#e2a84a"

    return f"""
<div class="race-card">
  <div class="race-title">{label}</div>
  <div class="race-metric {color_cls}">{ub if ub else "—"}</div>
  <div class="race-label">Upper Bound (UB)</div>
  <br/>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:.8rem;margin-top:.5rem;">
    <div>
      <div style="font-size:.72rem;color:#4a5568;text-transform:uppercase;letter-spacing:.08em;">LB</div>
      <div style="font-size:1.1rem;font-weight:600;color:#e2e8f0;">{lb}</div>
    </div>
    <div>
      <div style="font-size:.72rem;color:#4a5568;text-transform:uppercase;letter-spacing:.08em;">Time</div>
      <div style="font-size:1.1rem;font-weight:600;color:#e2e8f0;">{t:.1f}s</div>
    </div>
    <div>
      <div style="font-size:.72rem;color:#4a5568;text-transform:uppercase;letter-spacing:.08em;">Nodes</div>
      <div style="font-size:1.1rem;font-weight:600;color:#e2e8f0;">{nodes:,}</div>
    </div>
    <div>
      <div style="font-size:.72rem;color:#4a5568;text-transform:uppercase;letter-spacing:.08em;">Cuts</div>
      <div style="font-size:1.1rem;font-weight:600;color:#e2e8f0;">{coupes:,}</div>
    </div>
  </div>
  <div style="margin-top:.8rem;font-size:.72rem;color:{s_col};text-transform:uppercase;letter-spacing:.1em;">
    {status}
  </div>
</div>
"""


def race_panel_idle(label: str) -> str:
    return f"""
<div class="race-card">
  <div class="race-title">{label}</div>
  <div style="color:#4a5568;font-family:'IBM Plex Mono',monospace;font-size:.8rem;margin-top:.5rem;">Waiting…</div>
</div>
"""


def stat_grid(cells: list[tuple]) -> str:
    """
    cells : list of (label, value, color_override_or_None)
    """
    html = '<div class="stat-grid">'
    for label, value, color in cells:
        style = f' style="color:{color}"' if color else ""
        html += f"""
<div class="stat-cell">
  <div class="stat-label">{label}</div>
  <div class="stat-value"{style}>{value}</div>
</div>"""
    html += "</div>"
    return html


def divider() -> str:
    return '<div class="divider"></div>'


def step_pill(text: str) -> str:
    return f'<div class="step-pill">{text}</div>'


def page_header(title: str, subtitle: str) -> str:
    return f"""
<div class="page-title">{title}</div>
<div class="page-sub">{subtitle}</div>
"""


def winner_banner(msg: str) -> str:
    return f'<div class="winner-banner">{msg}</div>'


def algo_header(name: str, variant: str) -> str:
    """variant: 's' for Sewell (blue) or 'f' for Furini (green)."""
    cls = "algo-header-s" if variant == "s" else "algo-header-f"
    return f'<div class="{cls}">◉  {name}</div>'
