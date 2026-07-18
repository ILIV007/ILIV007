#!/usr/bin/env python3
"""
make_info_card.py — generate a minimal, fantasy-flavored neofetch-style
info card SVG.

Title bar + `ILIV007@github ~ $ summon` prompt, then ◆ ILIYA (gold) and
short key/value rows — class / level / stack / channel / oath / guild.
level is left mysterious ("??"). channel is ILIVIR3. Each line fades +
slides in on a short stagger (CSS keyframes, freeze). Purple + gold palette.

Usage:
  python scripts/make_info_card.py [output.svg]

Defaults: → info-card.svg
"""

import sys
from pathlib import Path

W, H = 480, 384
BG = "#0d1117"
TITLE_BG = "#161b22"
BORDER = "#30363d"
FG = "#c9d1d9"
MUTED = "#8b949e"
GOLD = "#e3b341"
PURPLE = "#bc8cff"
LAVENDER = "#d2a8ff"

USERNAME = "ILIV007"
HOST = "github"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def pad(s: str, n: int) -> str:
    return (s + " " * n)[:n]


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "info-card.svg"

    rows = [
        ("cmd",),
        ("sep",),
        ("name",),
        ("kv", "class", "developer", LAVENDER),
        ("kv", "level", "?? · quest just begun", LAVENDER),
        ("kv", "stack", "learning · building", LAVENDER),
        ("kv", "channel", "ILIVIR3", LAVENDER),
        ("motto", '"start small, stay curious"'),
        ("sep",),
        ("kv", "guild", f"github.com/{USERNAME}", LAVENDER),
    ]

    title_bar_h = 30
    pad_x = 22
    line_h = 24
    y = title_bar_h + 30
    delay = 0.18
    stagger = 0.10
    dur = 0.42

    groups = []
    for r in rows:
        inner = ""
        kind = r[0]
        if kind == "sep":
            inner = (
                f'<line x1="{pad_x}" y1="{y - 9:.1f}" x2="{W - pad_x}" '
                f'y2="{y - 9:.1f}" stroke="{BORDER}" stroke-width="1" '
                f'stroke-dasharray="2 3"/>'
            )
        elif kind == "cmd":
            inner = (
                f'<text x="{pad_x}" y="{y:.1f}" font-size="13">'
                f'<tspan fill="{PURPLE}">{esc(USERNAME)}@{esc(HOST)}</tspan>'
                f'<tspan fill="{MUTED}"> ~ $ </tspan>'
                f'<tspan fill="{FG}">summon</tspan></text>'
            )
        elif kind == "name":
            inner = (
                f'<text x="{pad_x}" y="{y:.1f}" font-size="18" font-weight="700">'
                f'<tspan fill="{PURPLE}">◆ </tspan>'
                f'<tspan fill="{GOLD}">ILIYA</tspan></text>'
            )
        elif kind == "kv":
            _, key, val, val_color = r
            inner = (
                f'<text x="{pad_x}" y="{y:.1f}" font-size="13">'
                f'<tspan fill="{GOLD}">{pad(key, 8)}</tspan>'
                f'<tspan fill="{val_color}">{esc(val)}</tspan></text>'
            )
        elif kind == "motto":
            _, text = r
            inner = (
                f'<text x="{pad_x + 8}" y="{y:.1f}" font-size="12" '
                f'font-style="italic" fill="{MUTED}">{esc(text)}</text>'
            )
        groups.append(
            f'<g class="nline" style="animation-delay:{delay:.2f}s">{inner}</g>'
        )
        y += line_h
        delay += stagger

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
  <style>
    .nline {{ opacity: 0; animation: nline {dur}s cubic-bezier(0.22,0.61,0.36,1) forwards; }}
    @keyframes nline {{
      from {{ opacity: 0; transform: translateX(-8px); }}
      to   {{ opacity: 1; transform: translateX(0); }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      .nline {{ opacity: 1; animation: none; transform: none; }}
    }}
  </style>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8" ry="8" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
  <path d="M0.5 8 a8 8 0 0 1 8 -7.5 H{W - 8.5} a8 8 0 0 1 8 7.5 V{title_bar_h} H0.5 Z" fill="{TITLE_BG}"/>
  <line x1="0.5" y1="{title_bar_h}" x2="{W - 0.5}" y2="{title_bar_h}" stroke="{BORDER}" stroke-width="1"/>
  <circle cx="14" cy="15" r="5" fill="#ff5f56"/>
  <circle cx="30" cy="15" r="5" fill="#ffbd2e"/>
  <circle cx="46" cy="15" r="5" fill="#27c93f"/>
  <text x="{W / 2}" y="19.5" text-anchor="middle" font-size="12" fill="{MUTED}">{esc(USERNAME)}@{esc(HOST)} — profile</text>
  {chr(10).join("  " + g for g in groups)}
  <title>ILIYA — neofetch card</title>
</svg>'''

    Path(out).write_text(svg, encoding="utf-8")
    print(f"Written {out} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
