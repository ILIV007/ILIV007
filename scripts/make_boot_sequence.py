#!/usr/bin/env python3
"""
Build a boot sequence SVG that types out like a real OS booting.

Lines appear one by one with typing effect. Uses SMIL.

Usage:
  python scripts/make_boot_sequence.py
"""

import os

OUTPUT = "boot-sequence.svg"
WIDTH = 860
HEIGHT = 280
BG = "#0a0e14"
FG = "#c9d1d9"
ACCENT_CYAN = "#00f0ff"
ACCENT_GREEN = "#39d353"
ACCENT_MAGENTA = "#ff00a0"
ACCENT_YELLOW = "#e3b341"
ACCENT_RED = "#ff5f56"

FONT = '"JetBrains Mono", "Fira Code", "Courier New", monospace'
FONT_SIZE = 12
LINE_H = 18
MARGIN_X = 28
MARGIN_TOP = 24

BOOT_LINES = [
    ("", 0.0, "none"),  # spacer
    ("ILLYA AI COMMAND CENTER v2.0", 0.1, "title"),
    ("═══════════════════════════════════════════════════════════════", 0.3, "divider"),
    ("", 0.0, "none"),
    ("[ OK ]  Kernel: Linux 6.8-cloud-amd64", 0.5, "ok"),
    ("[ OK ]  Memory: 64GB DDR5 ECC", 0.65, "ok"),
    ("[ OK ]  CPU: AMD EPYC 9654 (96 cores)", 0.8, "ok"),
    ("[ OK ]  Storage: NVMe RAID-10 4TB", 0.95, "ok"),
    ("[ OK ]  Network: 10Gbps fiber uplink", 1.1, "ok"),
    ("", 0.0, "none"),
    ("[INIT]  Loading AI Core modules...", 1.3, "init"),
    ("[INIT]  Mounting Cloudflare Workers...", 1.5, "init"),
    ("[INIT]  Initializing AI Router...", 1.7, "init"),
    ("[INIT]  Connecting to OpenRouter API...", 1.9, "init"),
    ("", 0.0, "none"),
    ("[ OK ]  Fredy Agent     v8.2  — ONLINE", 2.2, "ok"),
    ("[ OK ]  Hermes Agent    v3.1  — ONLINE", 2.4, "ok"),
    ("[ OK ]  Pixoris Engine  v2.2  — ONLINE", 2.6, "ok"),
    ("[ OK ]  Hades Army      v0.9  — ONLINE", 2.8, "ok"),
    ("[ OK ]  IVAI Bot        v4.0  — ONLINE", 3.0, "ok"),
    ("", 0.0, "none"),
    ("[ OK ]  Claude 4 Sonnet  — CONNECTED", 3.3, "ok"),
    ("[ OK ]  Gemini 2.5 Pro   — CONNECTED", 3.5, "ok"),
    ("[ OK ]  GPT-4.1          — CONNECTED", 3.7, "ok"),
    ("[ OK ]  DeepSeek V3      — CONNECTED", 3.9, "ok"),
    ("[ OK ]  Qwen 3           — CONNECTED", 4.1, "ok"),
    ("", 0.0, "none"),
    ("═══════════════════════════════════════════════════════════════", 4.4, "divider"),
    ("", 0.0, "none"),
    ("SYSTEM READY. Type 'whoami' to begin.", 4.7, "ready"),
    ("iliya@cloud:~$ _", 5.0, "prompt"),
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
        f'    .divider {{ fill: #21262d; }}',
        f'    .ok {{ fill: {ACCENT_GREEN}; }}',
        f'    .init {{ fill: {ACCENT_YELLOW}; }}',
        f'    .ready {{ fill: {ACCENT_CYAN}; font-weight: bold; filter: url(#glow); }}',
        f'    .prompt {{ fill: {ACCENT_MAGENTA}; font-weight: bold; }}',
        f'    .cursor {{ fill: {ACCENT_CYAN}; }}',
        f'  </style>',
        f'  <rect width="100%" height="100%" fill="{BG}" rx="8" stroke="#21262d" stroke-width="1"/>',
    ]

    y = MARGIN_TOP
    for text, delay, style in BOOT_LINES:
        if not text:
            y += LINE_H - 4
            continue

        if style == "title":
            svg.append(f'  <text x="{WIDTH // 2}" y="{y}" text-anchor="middle" class="title">{text}</text>')
        elif style == "divider":
            svg.append(f'  <text x="{MARGIN_X}" y="{y}" class="divider">{text}</text>')
        elif style == "ok":
            # Typing effect for OK lines
            clip_id = f"boot-clip-{len(svg)}"
            svg.append(f'  <clipPath id="{clip_id}">')
            svg.append(f'    <rect x="{MARGIN_X}" y="{y - LINE_H + 4}" width="0" height="{LINE_H}">')
            svg.append(f'      <animate attributeName="width" from="0" to="{len(text) * FONT_SIZE * 0.6:.1f}"')
            svg.append(f'               begin="{delay:.2f}s" dur="0.3s" fill="freeze"/>')
            svg.append(f'    </rect>')
            svg.append(f'  </clipPath>')
            svg.append(f'  <text x="{MARGIN_X}" y="{y}" class="ok" clip-path="url(#{clip_id})">{text}</text>')
        elif style == "init":
            clip_id = f"boot-clip-{len(svg)}"
            svg.append(f'  <clipPath id="{clip_id}">')
            svg.append(f'    <rect x="{MARGIN_X}" y="{y - LINE_H + 4}" width="0" height="{LINE_H}">')
            svg.append(f'      <animate attributeName="width" from="0" to="{len(text) * FONT_SIZE * 0.6:.1f}"')
            svg.append(f'               begin="{delay:.2f}s" dur="0.25s" fill="freeze"/>')
            svg.append(f'    </rect>')
            svg.append(f'  </clipPath>')
            svg.append(f'  <text x="{MARGIN_X}" y="{y}" class="init" clip-path="url(#{clip_id})">{text}</text>')
        elif style == "ready":
            clip_id = f"boot-clip-{len(svg)}"
            svg.append(f'  <clipPath id="{clip_id}">')
            svg.append(f'    <rect x="{MARGIN_X}" y="{y - LINE_H + 4}" width="0" height="{LINE_H}">')
            svg.append(f'      <animate attributeName="width" from="0" to="{len(text) * FONT_SIZE * 0.6:.1f}"')
            svg.append(f'               begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>')
            svg.append(f'    </rect>')
            svg.append(f'  </clipPath>')
            svg.append(f'  <text x="{MARGIN_X}" y="{y}" class="ready" clip-path="url(#{clip_id})">{text}</text>')
        elif style == "prompt":
            svg.append(f'  <text x="{MARGIN_X}" y="{y}" class="prompt">{text}</text>')
            # Blinking cursor
            cursor_x = MARGIN_X + len(text) * FONT_SIZE * 0.6
            svg.append(f'  <rect class="cursor" x="{cursor_x}" y="{y - 12}" width="8" height="14" rx="1">')
            svg.append(f'    <animate attributeName="opacity" values="1;0;1" dur="1s" repeatCount="indefinite"')
            svg.append(f'             begin="{delay:.2f}s"/>')
            svg.append(f'  </rect>')

        y += LINE_H - 2

    svg.append("</svg>")
    return "\n".join(svg)


def main():
    svg = build_svg()
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"✅ Saved boot sequence to {OUTPUT} ({len(svg):,} bytes)")


if __name__ == "__main__":
    main()
