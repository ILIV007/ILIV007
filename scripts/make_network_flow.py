#!/usr/bin/env python3
"""
Build an animated network architecture flow SVG with branching.

Browser → Cloudflare → AI Router → [Claude, Gemini, GPT, DeepSeek, Qwen]
                                     ↓
                              Fredy/Hermes/Pixoris
                                     ↓
                                   Telegram

Animated packets flow through all paths.

Usage:
  python scripts/make_network_flow.py
"""

import os

OUTPUT = "network-flow.svg"
WIDTH = 860
HEIGHT = 320
BG = "#0a0e14"

ACCENT_CYAN = "#00f0ff"
ACCENT_GREEN = "#39d353"
ACCENT_MAGENTA = "#ff00a0"
ACCENT_PURPLE = "#a371f7"
ACCENT_ORANGE = "#f0883e"
ACCENT_YELLOW = "#e3b341"
ACCENT_BLUE = "#58a6ff"

FONT = '"JetBrains Mono", "Fira Code", "Courier New", monospace'
FONT_SIZE = 10

# Node positions: (name, x, y, color, icon)
NODES = [
    ("Browser", 60, 50, ACCENT_CYAN, "🌍"),
    ("Cloudflare\nWorker", 60, 130, ACCENT_GREEN, "☁️"),
    ("AI Router", 60, 210, ACCENT_MAGENTA, "🧠"),
]

# Branching nodes (models)
MODELS = [
    ("Claude", 240, 170, ACCENT_PURPLE, "🟣"),
    ("Gemini", 320, 170, ACCENT_BLUE, "🔵"),
    ("GPT", 400, 170, ACCENT_GREEN, "🟢"),
    ("DeepSeek", 480, 170, ACCENT_ORANGE, "🟠"),
    ("Qwen", 560, 170, ACCENT_YELLOW, "🟡"),
]

# Output nodes
OUTPUTS = [
    ("Fredy", 400, 250, ACCENT_CYAN, "🤖"),
    ("Hermes", 480, 250, ACCENT_GREEN, "📡"),
    ("Pixoris", 560, 250, ACCENT_MAGENTA, "⚡"),
]

FINAL = ("Telegram", 400, 310, ACCENT_ORANGE, "📱")


def build_svg() -> str:
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}">',
        f'  <defs>',
        f'    <filter id="nodeGlow" x="-15%" y="-15%" width="130%" height="130%">',
        f'      <feGaussianBlur stdDeviation="2" result="blur"/>',
        f'      <feMerge>',
        f'        <feMergeNode in="blur"/>',
        f'        <feMergeNode in="SourceGraphic"/>',
        f'      </feMerge>',
        f'    </filter>',
        f'    <linearGradient id="packetGrad" x1="0%" y1="0%" x2="100%" y2="0%">',
        f'      <stop offset="0%" style="stop-color:{ACCENT_CYAN};stop-opacity:0"/>',
        f'      <stop offset="50%" style="stop-color:{ACCENT_CYAN};stop-opacity:1"/>',
        f'      <stop offset="100%" style="stop-color:{ACCENT_CYAN};stop-opacity:0"/>',
        f'    </linearGradient>',
        f'  </defs>',
        f'  <style>',
        f'    text {{ font-family: {FONT}; font-size: {FONT_SIZE}px; text-anchor: middle; }}',
        f'    .node-box {{ rx: 6; stroke-width: 1.5; filter: url(#nodeGlow); }}',
        f'    .node-label {{ fill: #c9d1d9; font-weight: bold; }}',
        f'    .node-icon {{ font-size: 16px; }}',
        f'    .conn {{ stroke-width: 1.5; stroke-dasharray: 3,3; opacity: 0.35; }}',
        f'    .packet {{ rx: 2.5; fill: url(#packetGrad); }}',
        f'    .section-title {{ fill: {ACCENT_CYAN}; font-weight: bold; font-size: 12px; filter: url(#nodeGlow); }}',
        f'  </style>',
        f'  <rect width="100%" height="100%" fill="{BG}" rx="8" stroke="#21262d" stroke-width="1"/>',
    ]

    # Title
    svg.append(f'  <text x="{WIDTH // 2}" y="20" text-anchor="middle" class="section-title">NETWORK ARCHITECTURE</text>')
    svg.append(f'  <line x1="24" y1="28" x2="{WIDTH - 24}" y2="28" stroke="#21262d" stroke-width="1"/>')

    # ── Vertical pipeline (Browser → Worker → Router) ──
    for i in range(len(NODES) - 1):
        x1, y1 = NODES[i][1], NODES[i][2]
        x2, y2 = NODES[i + 1][1], NODES[i + 1][2]
        svg.append(f'  <line x1="{x1}" y1="{y1 + 20}" x2="{x2}" y2="{y2 - 20}" stroke="{NODES[i][3]}" class="conn">')
        svg.append(f'    <animate attributeName="stroke-dashoffset" from="6" to="0" dur="0.8s" repeatCount="indefinite"/>')
        svg.append(f'  </line>')

    # ── Branching lines (Router → Models) ──
    router_x, router_y = NODES[2][1], NODES[2][2]
    for name, mx, my, color, icon in MODELS:
        svg.append(f'  <line x1="{router_x + 40}" y1="{router_y}" x2="{mx - 20}" y2="{my}" stroke="{color}" class="conn">')
        svg.append(f'    <animate attributeName="stroke-dashoffset" from="6" to="0" dur="1s" repeatCount="indefinite"/>')
        svg.append(f'  </line>')

    # ── Converging lines (Models → Outputs) ──
    for name, mx, my, color, icon in MODELS:
        for oname, ox, oy, ocolor, oicon in OUTPUTS:
            # Only connect some models to outputs for visual clarity
            if (name == "Claude" and oname == "Fredy") or \
               (name == "Gemini" and oname == "Hermes") or \
               (name == "GPT" and oname == "Pixoris") or \
               (name == "DeepSeek" and oname == "Fredy") or \
               (name == "Qwen" and oname == "Hermes"):
                svg.append(f'  <line x1="{mx}" y1="{my + 15}" x2="{ox}" y2="{oy - 15}" stroke="{color}" class="conn" opacity="0.2"/>')

    # ── Final line (Outputs → Telegram) ──
    for oname, ox, oy, ocolor, oicon in OUTPUTS:
        fx, fy = FINAL[1], FINAL[2]
        svg.append(f'  <line x1="{ox}" y1="{oy + 15}" x2="{fx}" y2="{fy - 15}" stroke="{ocolor}" class="conn" opacity="0.25"/>')

    # ── Animated packets ──
    # Vertical packets
    for i in range(len(NODES) - 1):
        x1, y1 = NODES[i][1], NODES[i][2]
        x2, y2 = NODES[i + 1][1], NODES[i + 1][2]
        svg.append(f'  <rect class="packet" x="{x1 - 4}" y="{y1 + 20}" width="8" height="4" rx="2">')
        svg.append(f'    <animate attributeName="y" from="{y1 + 20}" to="{y2 - 20}" dur="1.5s" repeatCount="indefinite"')
        svg.append(f'             begin="{i * 0.5}s"/>')
        svg.append(f'  </rect>')

    # Branching packets
    for j, (name, mx, my, color, icon) in enumerate(MODELS):
        svg.append(f'  <rect class="packet" x="{router_x + 40}" y="{router_y - 2}" width="6" height="4" rx="2" fill="{color}">')
        svg.append(f'    <animate attributeName="x" from="{router_x + 40}" to="{mx - 20}" dur="1s" repeatCount="indefinite"')
        svg.append(f'             begin="{j * 0.3}s"/>')
        svg.append(f'    <animate attributeName="y" from="{router_y}" to="{my}" dur="1s" repeatCount="indefinite"')
        svg.append(f'             begin="{j * 0.3}s"/>')
        svg.append(f'  </rect>')

    # ── Draw nodes ──
    node_w = 70
    node_h = 36

    def draw_node(name, x, y, color, icon, is_small=False):
        w = 50 if is_small else node_w
        h = 28 if is_small else node_h
        svg.append(f'  <rect class="node-box" x="{x - w//2}" y="{y - h//2}" width="{w}" height="{h}"')
        svg.append(f'        fill="{BG}" stroke="{color}"/>')
        svg.append(f'  <text x="{x}" y="{y + 4}" class="node-label" style="fill:{color}; font-size:{FONT_SIZE - 1 if is_small else FONT_SIZE}px">{name}</text>')

    # Main pipeline nodes
    for name, x, y, color, icon in NODES:
        draw_node(name, x, y, color, icon)

    # Model nodes (smaller)
    for name, x, y, color, icon in MODELS:
        draw_node(name, x, y, color, icon, is_small=True)

    # Output nodes
    for name, x, y, color, icon in OUTPUTS:
        draw_node(name, x, y, color, icon, is_small=True)

    # Final node
    draw_node(FINAL[0], FINAL[1], FINAL[2], FINAL[3], FINAL[4])

    svg.append("</svg>")
    return "\n".join(svg)


def main():
    svg = build_svg()
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"✅ Saved network flow to {OUTPUT} ({len(svg):,} bytes)")


if __name__ == "__main__":
    main()
