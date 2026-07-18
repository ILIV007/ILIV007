#!/usr/bin/env python3
"""
Build a system status dashboard SVG.

Shows: CPU, RAM, Workers, Requests, Latency as real dashboard bars.
Uses CSS keyframes for bar fill animation.

Usage:
  python scripts/make_system_status.py
"""

import os
import json

OUTPUT = "system-status.svg"
WIDTH = 860
HEIGHT = 200
BG = "#0a0e14"
FG = "#c9d1d9"
ACCENT_CYAN = "#00f0ff"
ACCENT_GREEN = "#39d353"
ACCENT_MAGENTA = "#ff00a0"
ACCENT_YELLOW = "#e3b341"
ACCENT_ORANGE = "#f0883e"

FONT = '"JetBrains Mono", "Fira Code", "Courier New", monospace'
FONT_SIZE = 12
LINE_H = 22
MARGIN_X = 28
MARGIN_TOP = 36


def load_stats() -> dict:
    try:
        with open("data/stats.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "cpu": 72,
            "ram": 58,
            "workers": 6,
            "requests": "2.8M",
            "latency": "18ms",
            "uptime": "99.97%",
        }


def build_svg() -> str:
    stats = load_stats()

    metrics = [
        ("CPU", stats.get("cpu", 72), ACCENT_CYAN, "%"),
        ("RAM", stats.get("ram", 58), ACCENT_GREEN, "%"),
        ("Workers", stats.get("workers", 6), ACCENT_MAGENTA, ""),
        ("Requests", stats.get("requests", "2.8M"), ACCENT_YELLOW, ""),
        ("Latency", stats.get("latency", "18ms"), ACCENT_ORANGE, ""),
    ]

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}">',
        f'  <defs>',
        f'    <filter id="barGlow" x="-5%" y="-20%" width="110%" height="140%">',
        f'      <feGaussianBlur stdDeviation="1" result="blur"/>',
        f'      <feMerge>',
        f'        <feMergeNode in="blur"/>',
        f'        <feMergeNode in="SourceGraphic"/>',
        f'      </feMerge>',
        f'    </filter>',
        f'  </defs>',
        f'  <style>',
        f'    text {{ font-family: {FONT}; font-size: {FONT_SIZE}px; }}',
        f'    .title {{ fill: {ACCENT_CYAN}; font-weight: bold; font-size: 14px; filter: url(#barGlow); }}',
        f'    .label {{ fill: {FG}; font-weight: bold; }}',
        f'    .value {{ fill: {FG}; }}',
        f'    .bar-bg {{ fill: #1c2128; rx: 3; }}',
        f'    .bar-fill {{ rx: 3; filter: url(#barGlow); }}',
        f'    @keyframes barGrow {{',
        f'      from {{ width: 0; }}',
        f'      to   {{ width: var(--target-width); }}',
        f'    }}',
        f'    .anim-bar {{ animation: barGrow 0.8s ease-out forwards; }}',
        f'  </style>',
        f'  <rect width="100%" height="100%" fill="{BG}" rx="8" stroke="#21262d" stroke-width="1"/>',
    ]

    # Title
    svg.append(f'  <text x="{MARGIN_X}" y="24" class="title">SYSTEM STATUS</text>')
    svg.append(f'  <line x1="{MARGIN_X}" y1="32" x2="{WIDTH - MARGIN_X}" y2="32" stroke="#21262d" stroke-width="1"/>')

    # Two-column layout
    col_width = (WIDTH - MARGIN_X * 2 - 40) // 2
    bar_max_w = col_width - 80

    y_left = MARGIN_TOP
    y_right = MARGIN_TOP

    for i, (label, value, color, suffix) in enumerate(metrics):
        is_left = i % 2 == 0
        x = MARGIN_X if is_left else MARGIN_X + col_width + 40
        y = y_left if is_left else y_right

        # Label
        svg.append(f'  <text x="{x}" y="{y}" class="label">{label}</text>')

        # Bar background
        bar_y = y + 6
        svg.append(f'  <rect class="bar-bg" x="{x}" y="{bar_y}" width="{bar_max_w}" height="10"/>')

        # Bar fill (animated)
        if isinstance(value, (int, float)) and suffix == "%":
            fill_w = int(bar_max_w * value / 100)
            svg.append(f'  <rect class="bar-fill anim-bar" x="{x}" y="{bar_y}" height="10" fill="{color}"')
            svg.append(f'        style="--target-width: {fill_w}px; width: 0;"/>')
            val_text = f"{value}{suffix}"
        else:
            # For non-percentage values, show full bar or partial
            fill_w = int(bar_max_w * 0.7) if isinstance(value, (int, float)) else bar_max_w
            svg.append(f'  <rect class="bar-fill anim-bar" x="{x}" y="{bar_y}" height="10" fill="{color}"')
            svg.append(f'        style="--target-width: {fill_w}px; width: 0;"/>')
            val_text = f"{value}{suffix}"

        # Value text
        svg.append(f'  <text x="{x + bar_max_w + 8}" y="{bar_y + 9}" class="value">{val_text}</text>')

        if is_left:
            y_left += LINE_H + 8
        else:
            y_right += LINE_H + 8

    svg.append("</svg>")
    return "\n".join(svg)


def main():
    svg = build_svg()
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"✅ Saved system status to {OUTPUT} ({len(svg):,} bytes)")


if __name__ == "__main__":
    main()
