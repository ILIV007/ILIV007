#!/usr/bin/env python3
"""
Build a system log SVG that shows deployment logs.

Types out like a real deploy log with checkmarks.

Usage:
  python scripts/make_system_log.py
"""

import os

OUTPUT = "system-log.svg"
WIDTH = 860
HEIGHT = 180
BG = "#0a0e14"
FG = "#c9d1d9"
ACCENT_GREEN = "#39d353"
ACCENT_CYAN = "#00f0ff"
ACCENT_YELLOW = "#e3b341"
ACCENT_MAGENTA = "#ff00a0"

FONT = '"JetBrains Mono", "Fira Code", "Courier New", monospace'
FONT_SIZE = 12
LINE_H = 20
MARGIN_X = 28
MARGIN_TOP = 36

LOG_LINES = [
    ("> Deploying Fredy v8.2 to Cloudflare Workers...", 0.2, "cmd"),
    ("  ✔ Build completed in 4.2s", 0.8, "ok"),
    ("  ✔ KV store synced", 1.1, "ok"),
    ("  ✔ Worker deployed to 275 edge nodes", 1.4, "ok"),
    ("", 0.0, "none"),
    ("> Syncing Hermes v3.1...", 1.8, "cmd"),
    ("  ✔ OpenRouter endpoints updated", 2.3, "ok"),
    ("  ✔ Rate limits configured", 2.6, "ok"),
    ("", 0.0, "none"),
    ("> Updating AI Router models...", 3.0, "cmd"),
    ("  ✔ Claude 4 Sonnet — online", 3.5, "ok"),
    ("  ✔ Gemini 2.5 Pro — online", 3.8, "ok"),
    ("  ✔ GPT-4.1 — online", 4.1, "ok"),
    ("", 0.0, "none"),
    ("[SYSTEM] All services operational. Latency: 18ms", 4.6, "ready"),
]


def build_svg() -> str:
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}">',
        f'  <defs>',
        f'    <filter id="glow" x="-10%" y="-10%" width="120%" height="120%">',
        f'      <feGaussianBlur stdDeviation="1.2" result="blur"/>',
        f'      <feMerge>',
        f'        <feMergeNode in="blur"/>',
        f'        <feMergeNode in="SourceGraphic"/>',
        f'      </feMerge>',
        f'    </filter>',
        f'  </defs>',
        f'  <style>',
        f'    text {{ font-family: {FONT}; font-size: {FONT_SIZE}px; }}',
        f'    .title {{ fill: {ACCENT_CYAN}; font-weight: bold; font-size: 13px; filter: url(#glow); }}',
        f'    .cmd {{ fill: {ACCENT_YELLOW}; }}',
        f'    .ok {{ fill: {ACCENT_GREEN}; }}',
        f'    .ready {{ fill: {ACCENT_CYAN}; font-weight: bold; filter: url(#glow); }}',
        f'    .cursor {{ fill: {ACCENT_CYAN}; }}',
        f'  </style>',
        f'  <rect width="100%" height="100%" fill="{BG}" rx="8" stroke="#21262d" stroke-width="1"/>',
    ]

    # Title
    svg.append(f'  <text x="{MARGIN_X}" y="22" class="title">SYSTEM LOG</text>')
    svg.append(f'  <line x1="{MARGIN_X}" y1="30" x2="{WIDTH - MARGIN_X}" y2="30" stroke="#21262d" stroke-width="1"/>')

    y = MARGIN_TOP
    for text, delay, style in LOG_LINES:
        if not text:
            y += LINE_H - 4
            continue

        if style == "cmd":
            clip_id = f"log-clip-{len(svg)}"
            svg.append(f'  <clipPath id="{clip_id}">')
            svg.append(f'    <rect x="{MARGIN_X}" y="{y - LINE_H + 4}" width="0" height="{LINE_H}">')
            svg.append(f'      <animate attributeName="width" from="0" to="{len(text) * FONT_SIZE * 0.6:.1f}"')
            svg.append(f'               begin="{delay:.2f}s" dur="0.3s" fill="freeze"/>')
            svg.append(f'    </rect>')
            svg.append(f'  </clipPath>')
            svg.append(f'  <text x="{MARGIN_X}" y="{y}" class="cmd" clip-path="url(#{clip_id})">{text}</text>')
        elif style == "ok":
            clip_id = f"log-clip-{len(svg)}"
            svg.append(f'  <clipPath id="{clip_id}">')
            svg.append(f'    <rect x="{MARGIN_X}" y="{y - LINE_H + 4}" width="0" height="{LINE_H}">')
            svg.append(f'      <animate attributeName="width" from="0" to="{len(text) * FONT_SIZE * 0.6:.1f}"')
            svg.append(f'               begin="{delay:.2f}s" dur="0.25s" fill="freeze"/>')
            svg.append(f'    </rect>')
            svg.append(f'  </clipPath>')
            svg.append(f'  <text x="{MARGIN_X}" y="{y}" class="ok" clip-path="url(#{clip_id})">{text}</text>')
        elif style == "ready":
            clip_id = f"log-clip-{len(svg)}"
            svg.append(f'  <clipPath id="{clip_id}">')
            svg.append(f'    <rect x="{MARGIN_X}" y="{y - LINE_H + 4}" width="0" height="{LINE_H}">')
            svg.append(f'      <animate attributeName="width" from="0" to="{len(text) * FONT_SIZE * 0.6:.1f}"')
            svg.append(f'               begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>')
            svg.append(f'    </rect>')
            svg.append(f'  </clipPath>')
            svg.append(f'  <text x="{MARGIN_X}" y="{y}" class="ready" clip-path="url(#{clip_id})">{text}</text>')

        y += LINE_H - 2

    # Blinking cursor at end
    svg.append(f'  <rect class="cursor" x="{MARGIN_X}" y="{y - 12}" width="8" height="14" rx="1">')
    svg.append(f'    <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"')
    svg.append(f'             begin="5.5s"/>')
    svg.append(f'  </rect>')

    svg.append("</svg>")
    return "\n".join(svg)


def main():
    svg = build_svg()
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"✅ Saved system log to {OUTPUT} ({len(svg):,} bytes)")


if __name__ == "__main__":
    main()
