#!/usr/bin/env python3
"""
Build a mission/personality card SVG.

Shows: Motto, Mission, Current Objective, Philosophy.

Usage:
  python scripts/make_mission_card.py
"""

import os

OUTPUT = "mission-card.svg"
WIDTH = 860
HEIGHT = 160
BG = "#0a0e14"
FG = "#c9d1d9"
ACCENT_CYAN = "#00f0ff"
ACCENT_GREEN = "#39d353"
ACCENT_MAGENTA = "#ff00a0"
ACCENT_YELLOW = "#e3b341"

FONT = '"JetBrains Mono", "Fira Code", "Courier New", monospace'
FONT_SIZE = 12
LINE_H = 20
MARGIN_X = 28
MARGIN_TOP = 32

MISSION = [
    ("Motto", "Building autonomous AI systems at the edge.", ACCENT_CYAN),
    ("Mission", "Making AI tools open, accessible, and lightning-fast.", ACCENT_GREEN),
    ("Current Objective", "Fredy v8 — AI Agent Orchestrator with multi-model routing.", ACCENT_MAGENTA),
    ("Philosophy", "Ship fast. Iterate faster. Open source everything.", ACCENT_YELLOW),
]


def build_svg() -> str:
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}">',
        f'  <defs>',
        f'    <filter id="glow" x="-10%" y="-10%" width="120%" height="120%">',
        f'      <feGaussianBlur stdDeviation="1.5" result="blur"/>',
        f'      <feMerge>',
        f'        <feMergeNode in="blur"/>',
        f'        <feMergeNode in="SourceGraphic"/>',
        f'      </feMerge>',
        f'    </filter>',
        f'  </defs>',
        f'  <style>',
        f'    text {{ font-family: {FONT}; font-size: {FONT_SIZE}px; }}',
        f'    .title {{ fill: {ACCENT_CYAN}; font-weight: bold; font-size: 14px; filter: url(#glow); }}',
        f'    .key {{ fill: {ACCENT_CYAN}; font-weight: bold; }}',
        f'    .val {{ fill: {FG}; }}',
        f'    @keyframes fadeSlide {{',
        f'      from {{ opacity: 0; transform: translateX(-8px); }}',
        f'      to   {{ opacity: 1; transform: translateX(0); }}',
        f'    }}',
        f'    .anim {{ animation: fadeSlide 0.4s ease-out forwards; opacity: 0; }}',
        f'  </style>',
        f'  <rect width="100%" height="100%" fill="{BG}" rx="8" stroke="#21262d" stroke-width="1"/>',
    ]

    # Title
    svg.append(f'  <text x="{MARGIN_X}" y="22" class="title">MISSION BRIEFING</text>')
    svg.append(f'  <line x1="{MARGIN_X}" y1="30" x2="{WIDTH - MARGIN_X}" y2="30" stroke="#21262d" stroke-width="1"/>')

    y = MARGIN_TOP
    for i, (key, val, color) in enumerate(MISSION):
        delay = 0.3 + i * 0.15
        svg.append(f'  <g class="anim" style="animation-delay: {delay:.2f}s;">')
        svg.append(f'    <text x="{MARGIN_X}" y="{y}" class="key" style="fill:{color}">{key}</text>')
        svg.append(f'    <text x="{MARGIN_X + 140}" y="{y}" class="val">{val}</text>')
        svg.append(f'  </g>')
        y += LINE_H + 4

    svg.append("</svg>")
    return "\n".join(svg)


def main():
    svg = build_svg()
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"✅ Saved mission card to {OUTPUT} ({len(svg):,} bytes)")


if __name__ == "__main__":
    main()
