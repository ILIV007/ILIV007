#!/usr/bin/env python3
"""
make_info_card.py — a minimal, fantasy-flavored neofetch-style info card SVG.

Title bar + `ILIV007@github ~ $ summon` prompt (INSIDE the SVG), then
◆ ILIYA (gold) and short key/value rows — class / level / stack / channel /
oath / guild. level is "??". channel is ILIVIR3. Each line fades + slides
in (CSS keyframes, freeze). Purple + gold palette.

Usage:
  python scripts/make_info_card.py [output.svg] [username]

Defaults: → info-card.svg, username ILIV007
"""

import sys
from pathlib import Path

W, H = 460, 514
BG = "#0d1117"
TITLE_BG = "#161b22"
BORDER = "#30363d"
FG = "#c9d1d9"
MUTED = "#8b949e"
GOLD = "#e3b341"
PURPLE = "#bc8cff"
LAVENDER = "#d2a8ff"
FONT = "'Courier New', Courier, monospace"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def pad(s: str, n: int) -> str:
    return (s + " " * n)[:n]


def make_svg(username: str = "ILIV007") -> str:
    user = "".join(c for c in username if c not in '<>"')[:24]
    rows = [
        ("cmd",),
        ("sep",),
        ("name",),
        ("kv", "class", "developer"),
        ("kv", "level", "?? · quest just begun"),
        ("kv", "stack", "learning · building"),
        ("kv", "channel", "ILIVIR3"),
        ("motto", '"start small, stay curious"'),
        ("sep",),
        ("kv", "guild", f"github.com/{user}"),
    ]
    title_bar_h = 30
    pad_x = 22
    line_h = 26
    y = title_bar_h + 32
    delay = 0.3
    stagger = 0.1
    dur = 0.4
    groups = []
    for r in rows:
        kind = r[0]
        inner = ""
        if kind == "sep":
            inner = f'<line x1="{pad_x}" y1="{y - 9}" x2="{W - pad_x}" y2="{y - 9}" stroke="{BORDER}" stroke-width="1" stroke-dasharray="2 3"/>'
        elif kind == "cmd":
            inner = f'<text x="{pad_x}" y="{y}" font-family="{FONT}" font-size="13" font-weight="700"><tspan fill="{PURPLE}">{esc(user)}@github</tspan><tspan fill="{MUTED}"> ~ $ </tspan><tspan fill="{FG}">summon</tspan><tspan fill="{GOLD}"> ▮</tspan></text>'
        elif kind == "name":
            inner = f'<text x="{pad_x}" y="{y}" font-family="{FONT}" font-size="18" font-weight="700"><tspan fill="{PURPLE}">◆ </tspan><tspan fill="{GOLD}">ILIYA</tspan></text>'
        elif kind == "kv":
            _, key, val = r
            inner = f'<text x="{pad_x}" y="{y}" font-family="{FONT}" font-size="13"><tspan fill="{GOLD}">{pad(key, 8)}</tspan><tspan fill="{LAVENDER}">{esc(val)}</tspan></text>'
        elif kind == "motto":
            _, text = r
            inner = f'<text x="{pad_x + 8}" y="{y}" font-family="{FONT}" font-size="12" font-style="italic" fill="{MUTED}">{esc(text)}</text>'
        groups.append(f'<g class="cardline" style="animation-delay:{delay:.2f}s">{inner}</g>')
        y += line_h
        delay += stagger

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">
  <style>
    .cardline {{ opacity: 0; animation: ci {dur}s cubic-bezier(0.22,0.61,0.36,1) forwards; }}
    @keyframes ci {{ from {{ opacity: 0; transform: translateX(-8px); }} to {{ opacity: 1; transform: translateX(0); }} }}
    @media (prefers-reduced-motion: reduce) {{ .cardline {{ opacity: 1; animation: none; transform: none; }} }}
  </style>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8" ry="8" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
  <path d="M0.5 8 a8 8 0 0 1 8 -7.5 H{W - 8.5} a8 8 0 0 1 8 7.5 V{title_bar_h} H0.5 Z" fill="{TITLE_BG}"/>
  <line x1="0.5" y1="{title_bar_h}" x2="{W - 0.5}" y2="{title_bar_h}" stroke="{BORDER}" stroke-width="1"/>
  <circle cx="14" cy="15" r="5" fill="#ff5f56"/>
  <circle cx="30" cy="15" r="5" fill="#ffbd2e"/>
  <circle cx="46" cy="15" r="5" fill="#27c93f"/>
  <text x="{W / 2}" y="19.5" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{MUTED}">{esc(user)}@github — profile</text>
  {chr(10).join("  " + g for g in groups)}
  <title>ILIYA — neofetch card</title>
</svg>'''


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "info-card.svg"
    username = sys.argv[2] if len(sys.argv) > 2 else "ILIV007"
    svg = make_svg(username)
    Path(out).write_text(svg, encoding="utf-8")
    print(f"Written {out} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
