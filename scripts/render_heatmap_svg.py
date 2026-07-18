#!/usr/bin/env python3
"""
Render contribution heatmap as a PCB (Printed Circuit Board) SVG.

Each commit = one LED on a circuit board.
Traces connect adjacent active LEDs like PCB traces.

Usage:
  python scripts/make_pcb_heatmap.py
"""

import os
import json
from datetime import datetime

INPUT_JSON = "data/contributions.json"
OUTPUT_SVG = "contrib-heatmap.svg"

# LED colors: off → dim → bright neon
PALETTE = [
    "#161b22",   # off
    "#0e4429",   # dim
    "#006d32",   # medium
    "#26a641",   # bright
    "#39d353",   # neon
    "#69f0a0",   # white-hot
]

BG = "#0a0e14"
TRACE_COLOR = "#21262d"
TRACE_ACTIVE = "#0e4429"
FG = "#8b949e"
TEXT = "#c9d1d9"
ACCENT = "#00f0ff"

SVG_W = 860
MARGIN_X = 24
MARGIN_TOP = 52
MARGIN_BOTTOM = 68

LED_R = 3
LED_GAP = 4
WEEKS = 53
DAYS = 7

usable_w = SVG_W - (MARGIN_X * 2)
LED_SIZE = (usable_w - (WEEKS - 1) * LED_GAP) // WEEKS
GRID_W = WEEKS * LED_SIZE + (WEEKS - 1) * LED_GAP
GRID_H = DAYS * LED_SIZE + (DAYS - 1) * LED_GAP
SVG_H = MARGIN_TOP + GRID_H + MARGIN_BOTTOM

STAGGER = 0.008
BASE_DELAY = 0.2
DUR = 0.3


def load_data() -> dict:
    if not os.path.exists(INPUT_JSON):
        print(f"❌ {INPUT_JSON} not found. Run fetch_contributions.py first.")
        exit(1)
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def month_labels(days: list[dict]) -> list[tuple[str, int]]:
    labels = []
    seen = set()
    for d in days:
        date = datetime.strptime(d["date"], "%Y-%m-%d")
        key = (date.year, date.month)
        if key not in seen:
            seen.add(key)
            day_idx = days.index(d)
            week_idx = day_idx // 7
            labels.append((date.strftime("%b"), week_idx))
    return labels


def build_svg(data: dict) -> str:
    days = data.get("days", [])
    stats = data.get("stats", {})
    username = data.get("username", "user")

    grid = [[0] * DAYS for _ in range(WEEKS)]
    for i, d in enumerate(days[-(WEEKS * DAYS):]):
        week = i // DAYS
        day = i % DAYS
        if week < WEEKS:
            grid[week][day] = d["level"]

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SVG_W} {SVG_H}" width="{SVG_W}">',
        f'  <defs>',
        f'    <filter id="ledGlow" x="-50%" y="-50%" width="200%" height="200%">',
        f'      <feGaussianBlur stdDeviation="2" result="blur"/>',
        f'      <feMerge>',
        f'        <feMergeNode in="blur"/>',
        f'        <feMergeNode in="SourceGraphic"/>',
        f'      </feMerge>',
        f'    </filter>',
        f'    <filter id="traceGlow" x="-20%" y="-20%" width="140%" height="140%">',
        f'      <feGaussianBlur stdDeviation="0.5" result="blur"/>',
        f'      <feMerge>',
        f'        <feMergeNode in="blur"/>',
        f'        <feMergeNode in="SourceGraphic"/>',
        f'      </feMerge>',
        f'    </filter>',
        f'  </defs>',
        f'  <style>',
        f'    text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }}',
        f'    .month {{ font-size: 10px; fill: {FG}; }}',
        f'    .day-label {{ font-size: 9px; fill: {FG}; }}',
        f'    .footer {{ font-size: 12px; fill: {TEXT}; }}',
        f'    .legend-text {{ font-size: 10px; fill: {FG}; }}',
        f'    .trace {{ stroke: {TRACE_COLOR}; stroke-width: 1; fill: none; }}',
        f'    .trace-active {{ stroke: {TRACE_ACTIVE}; stroke-width: 1.5; fill: none; filter: url(#traceGlow); }}',
        f'    @keyframes ledPulse {{',
        f'      0% {{ opacity: 0; transform: scale(0.2); }}',
        f'      50% {{ opacity: 1; transform: scale(1.2); }}',
        f'      100% {{ opacity: 1; transform: scale(1); }}',
        f'    }}',
        f'    .led {{ animation: ledPulse {DUR}s ease-out forwards; opacity: 0; }}',
        f'  </style>',
        f'  <rect width="100%" height="100%" fill="{BG}" rx="8"/>',
    ]

    # Title
    svg.append(f'  <text x="{MARGIN_X}" y="30" font-size="16" font-weight="bold" fill="{ACCENT}" style="filter:url(#ledGlow)">{username}’s Activity PCB</text>')

    # Month labels
    if days:
        for label, week_idx in month_labels(days):
            x = MARGIN_X + week_idx * (LED_SIZE + LED_GAP)
            svg.append(f'  <text x="{x}" y="{MARGIN_TOP - 8}" class="month">{label}</text>')

    # Day labels
    dow = ["Mon", "Wed", "Fri"]
    for i, name in enumerate(dow):
        day_idx = [1, 3, 5][i]
        y = MARGIN_TOP + day_idx * (LED_SIZE + LED_GAP) + LED_SIZE - 2
        svg.append(f'  <text x="{MARGIN_X - 6}" y="{y}" text-anchor="end" class="day-label">{name}</text>')

    # Calculate LED centers for trace drawing
    centers = {}
    for week in range(WEEKS):
        for day in range(DAYS):
            cx = MARGIN_X + week * (LED_SIZE + LED_GAP) + LED_SIZE / 2
            cy = MARGIN_TOP + day * (LED_SIZE + LED_GAP) + LED_SIZE / 2
            centers[(week, day)] = (cx, cy)

    # Draw traces between adjacent active LEDs
    for week in range(WEEKS):
        for day in range(DAYS):
            level = grid[week][day]
            if level == 0:
                continue
            cx, cy = centers[(week, day)]

            # Check right neighbor
            if week + 1 < WEEKS and grid[week + 1][day] > 0:
                nx, ny = centers[(week + 1, day)]
                svg.append(f'  <line x1="{cx}" y1="{cy}" x2="{nx}" y2="{ny}" class="trace-active"/>')

            # Check bottom neighbor
            if day + 1 < DAYS and grid[week][day + 1] > 0:
                nx, ny = centers[(week, day + 1)]
                svg.append(f'  <line x1="{cx}" y1="{cy}" x2="{nx}" y2="{ny}" class="trace-active"/>')

    # Draw LEDs on top of traces
    for week in range(WEEKS):
        for day in range(DAYS):
            level = grid[week][day]
            color = PALETTE[min(level, len(PALETTE) - 1)]
            x = MARGIN_X + week * (LED_SIZE + LED_GAP)
            y = MARGIN_TOP + day * (LED_SIZE + LED_GAP)
            delay = BASE_DELAY + (week + day) * STAGGER

            glow = 'filter="url(#ledGlow)"' if level >= 3 else ""
            svg.append(
                f'  <rect class="led" x="{x}" y="{y}" width="{LED_SIZE}" height="{LED_SIZE}"'
                f'          rx="{LED_R}" fill="{color}" style="animation-delay: {delay:.3f}s;" {glow}/>'
            )

    # Legend
    legend_y = SVG_H - 40
    legend_x = SVG_W - MARGIN_X - 140
    svg.append(f'  <text x="{legend_x}" y="{legend_y + 10}" class="legend-text">Off</text>')
    for i, color in enumerate(PALETTE):
        lx = legend_x + 28 + i * (LED_SIZE + 4)
        svg.append(f'  <rect x="{lx}" y="{legend_y}" width="{LED_SIZE}" height="{LED_SIZE}" rx="{LED_R}" fill="{color}"/>')
    svg.append(f'  <text x="{legend_x + 28 + len(PALETTE) * (LED_SIZE + 4) + 6}" y="{legend_y + 10}" class="legend-text">Hot</text>')

    # Stats footer
    total = stats.get("total", 0)
    longest = stats.get("longest_streak", 0)
    current = stats.get("current_streak", 0)
    best = stats.get("best_day", {})
    best_str = f"{best.get('count', 0)} on {best.get('date', 'N/A')}" if best else "N/A"

    footer_y = SVG_H - 16
    svg.append(
        f'  <text x="{MARGIN_X}" y="{footer_y}" class="footer">'
        f'    {total:,} commits · Longest streak: {longest}d · Current: {current}d · Peak: {best_str}'
        f'  </text>'
    )

    svg.append("</svg>")
    return "\n".join(svg)


def main():
    data = load_data()
    svg = build_svg(data)
    with open(OUTPUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"✅ Saved PCB heatmap to {OUTPUT_SVG} ({len(svg):,} bytes)")


if __name__ == "__main__":
    main()
