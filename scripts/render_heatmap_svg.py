#!/usr/bin/env python3
"""
render_heatmap_svg.py — render the contribution calendar as a 53×7 grid
of rounded boxes on a violet ramp. Diagonal CSS-keyframe reveal, month/
day labels, Less→More legend, stats footer. Purple theme (no green).

Usage:
  python scripts/render_heatmap_svg.py [data/contributions.json] [output.svg]

Defaults: data/contributions.json → contrib-heatmap.svg
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

W, H = 860, 196
LEFT, TOP = 40, 30
CELL, GAP = 12, 3
PITCH = CELL + GAP
BG = "#0d1117"
BORDER = "#30363d"
FG = "#c9d1d9"
MUTED = "#8b949e"

# violet ramp (none → brightest)
PALETTE = ["#161b22", "#2d1b4e", "#4c1d95", "#7c3aed", "#a855f7", "#c4b5fd"]
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
DAY_LABELS = ["", "Mon", "", "Wed", "", "Fri", ""]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fmt(n: int) -> str:
    return f"{n:,}"


def level_for(count: int) -> int:
    if count <= 0: return 0
    if count <= 3: return 1
    if count <= 7: return 2
    if count <= 12: return 3
    if count <= 19: return 4
    return 5


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "data/contributions.json"
    out = sys.argv[2] if len(sys.argv) > 2 else "contrib-heatmap.svg"

    data = json.loads(Path(src).read_text(encoding="utf-8"))
    days = data["days"]
    s = data["stats"]
    username = data.get("username", "ILIV007")
    source_tag = data.get("source", "demo")

    if not days:
        Path(out).write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">'
            f'<rect width="{W}" height="{H}" fill="{BG}"/></svg>'
        )
        return

    first = datetime.strptime(days[0]["date"], "%Y-%m-%d")
    first_dow = first.weekday() + 1  # Python: Mon=0, we need Sun=0
    first_dow = first_dow % 7
    first_ms = first.timestamp()

    cells, month_labels, prev_month = [], [], -1
    for d in days:
        dt = datetime.strptime(d["date"], "%Y-%m-%d")
        dow = (dt.weekday() + 1) % 7  # Sun=0..Sat=6
        days_since = int(round((dt.timestamp() - first_ms) / 86400))
        week = (days_since + first_dow) // 7
        x = LEFT + week * PITCH
        y = TOP + dow * PITCH
        lvl = level_for(d["count"])
        fill = PALETTE[lvl]
        delay = f"{0.1 + (week + dow) * 0.01:.3f}"
        cells.append(
            f'<g class="cell" style="animation-delay:{delay}s">'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{CELL}" height="{CELL}" '
            f'rx="2.5" ry="2.5" fill="{fill}">'
            f'<title>{d["date"]}: {d["count"]}</title></rect></g>'
        )
        m = dt.month - 1
        if dow <= 1 and m != prev_month and week >= 0:
            month_labels.append(
                f'<text x="{x:.1f}" y="{TOP - 8:.1f}" font-size="11" '
                f'fill="{MUTED}">{MONTHS[m]}</text>'
            )
            prev_month = m

    day_labels = []
    for i in range(7):
        if not DAY_LABELS[i]:
            continue
        day_labels.append(
            f'<text x="{LEFT - 8:.1f}" y="{TOP + i * PITCH + CELL - 2:.1f}" '
            f'text-anchor="end" font-size="10" fill="{MUTED}">{DAY_LABELS[i]}</text>'
        )

    legend_y = TOP + 7 * PITCH + 18
    legend_x = W - 30 - len(PALETTE) * (CELL + 4)
    legend_cells = []
    for i, c in enumerate(PALETTE):
        legend_cells.append(
            f'<rect x="{legend_x + i * (CELL + 4):.1f}" y="{legend_y:.1f}" '
            f'width="{CELL}" height="{CELL}" rx="2.5" ry="2.5" fill="{c}"/>'
        )

    best = s.get("bestDay") or {}
    footer = (
        f'<text x="40" y="{legend_y + CELL - 1:.1f}" font-size="12" fill="{FG}">'
        f'<tspan fill="#c4b5fd" font-weight="700">{fmt(s["total"])}</tspan>'
        f' contributions in the last year'
        f'  ·  current streak <tspan fill="#bc8cff">{s["currentStreak"]}d</tspan>'
        f'  ·  longest <tspan fill="#bc8cff">{s["longestStreak"]}d</tspan>'
        f'  ·  best day <tspan fill="#e3b341">{fmt(best.get("count", 0))}</tspan>'
        f'</text>'
    )
    legend_text = (
        f'<text x="{legend_x - 8:.1f}" y="{legend_y + CELL - 1:.1f}" '
        f'text-anchor="end" font-size="11" fill="{MUTED}">Less</text>'
        f'<text x="{legend_x + len(PALETTE) * (CELL + 4) + 4:.1f}" '
        f'y="{legend_y + CELL - 1:.1f}" font-size="11" fill="{MUTED}">More</text>'
    )
    user_tag = (
        f'<text x="{W - 30}" y="{TOP - 8:.1f}" text-anchor="end" '
        f'font-size="11" fill="{MUTED}">{esc(username)} · {source_tag}</text>'
    )

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
  <style>
    .cell {{ opacity: 0; animation: cellIn 0.45s ease-out forwards; transform-box: fill-box; transform-origin: center; }}
    @keyframes cellIn {{ from {{ opacity: 0; transform: translateY(-4px) scale(0.5); }} to {{ opacity: 1; transform: translateY(0) scale(1); }} }}
    @media (prefers-reduced-motion: reduce) {{ .cell {{ opacity: 1; animation: none; transform: none; }} }}
  </style>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8" ry="8" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
  {user_tag}
  {chr(10).join("  " + m for m in month_labels)}
  {chr(10).join("  " + d for d in day_labels)}
  {chr(10).join("  " + c for c in cells)}
  {legend_text}
  {chr(10).join("  " + lc for lc in legend_cells)}
  {footer}
  <title>Contribution heatmap for {esc(username)}</title>
</svg>'''

    Path(out).write_text(svg, encoding="utf-8")
    print(f"Written {out} ({len(svg)} bytes, {len(days)} days)")


if __name__ == "__main__":
    main()
