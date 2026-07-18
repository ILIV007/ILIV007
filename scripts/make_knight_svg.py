#!/usr/bin/env python3
"""
make_knight_svg.py — a HAND-DRAWN crusader great helm rendered as a
self-typing monochrome ASCII SVG.

The art is authored directly (not image conversion) so the silhouette is
precise and unmistakable: plumed dome, crusader cross, horizontal eye-slit,
breath holes, flared gorget. The `whoami` prompt lives INSIDE the SVG.

Each art row types itself in via a left-to-right SMIL clip wipe with a gold
cursor, staggered top to bottom. Plays once and freezes.

Usage:
  python scripts/make_knight_svg.py [output.svg] [username]

Defaults: → iliv-knight.svg, username ILIV007
"""

import sys
from pathlib import Path

# Hand-authored crusader great helm. ONLY the content is written here (no
# manual padding) — the centering code below pads each row to CANVAS_W so
# it's always exactly centered. Every row has ODD content width so it
# centers precisely on column 19 of the 39-wide canvas.
#
# Width map:  plume 5,7,5  →  dome 7,11,13,15  →  body 15  →  gorget 19,17
KNIGHT_LINES = [
    "~~~~~",            #  0  plume         w=5
    "~~~~~~~",          #  1  plume         w=7
    "|||||",            #  2  plume stem    w=5
    ".-|||-.",          #  3  dome top      w=7
    ".---|||---.",      #  4  dome          w=11
    ".----|||----.",    #  5  dome          w=13
    "/-----|||-----\\", #  6  dome edge     w=15  ← body width starts
    "|@@@@@@@@@@@@@|",  #  7  body          w=15
    "|@@@@@@@@@@@@@|",  #  8
    "|@@@@@@+@@@@@@|",  #  9  cross         w=15  (+ at center)
    "|@@@@@@+@@@@@@|",  # 10  cross
    "|@@@@@@@@@@@@@|",  # 11
    "|@@@@@@@@@@@@@|",  # 12
    "|@@@@@@@@@@@@@|",  # 13
    "|@@@@@@@@@@@@@|",  # 14
    "|=============|",  # 15  EYE SLIT      w=15
    "|=============|",  # 16  EYE SLIT
    "|@@@@@@@@@@@@@|",  # 17
    "|@@@:@@:@@:@@@|",  # 18  breath holes  w=15  (colons at 3,6,9)
    "|@@@@@@@@@@@@@|",  # 19
    "|@@@@@@@@@@@@@|",  # 20
    "\\@@@@@@@@@@@/",   # 21  narrowing     w=13
    ".---@@@@@@@@@@@---.", # 22  gorget top    w=19  ← flares out
    "|@@@@@@@@@@@@@@@@@|", # 23  gorget        w=19
    "|@@@@@@@@@@@@@@@@@|", # 24
    "|@@@@@@@@@@@@@@@@@|", # 25
    "\\@@@@@@@@@@@@@@@/", # 26  gorget bottom w=17
]

CANVAS_W = 39  # ODD — so odd-width rows center exactly

# Center + pad each row to CANVAS_W. Since CANVAS_W is odd and every content
# row is odd-width, (CANVAS_W - w) is even → left === right → perfect center.
ART = []
for r in KNIGHT_LINES:
    w = len(r)
    left = (CANVAS_W - w) // 2
    ART.append(" " * left + r + " " * (CANVAS_W - left - w))

ART_START_ROW = 2  # row 0 = prompt, row 1 = blank
TOTAL_ROWS = ART_START_ROW + len(ART)

CHAR_W = 10
CHAR_H = 13
W = CANVAS_W * CHAR_W       # 400
H = TOTAL_ROWS * CHAR_H     # 390

FILL = "#c8b5ff"
BG = "#0d1117"
CURSOR = "#e3b341"
PURPLE = "#bc8cff"
MUTED = "#8b949e"
FG = "#c9d1d9"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def make_svg(username: str = "ILIV007") -> str:
    user = "".join(c for c in username if c not in '<>"')[:24]

    row_stagger = 0.04
    row_dur = 0.3
    start_delay = 0.2

    clips, texts, cursors = [], [], []
    for r, line in enumerate(ART):
        begin = f"{start_delay + r * row_stagger:.3f}"
        y = (ART_START_ROW + r) * CHAR_H
        clips.append(
            f'<clipPath id="ke{r}"><rect x="0" y="{y:.2f}" width="0" '
            f'height="{CHAR_H:.2f}"><animate attributeName="width" '
            f'from="0" to="{W}" begin="{begin}s" dur="{row_dur}s" '
            f'fill="freeze" calcMode="spline" keyTimes="0;1" '
            f'keySplines="0.25 0.1 0.25 1"/></rect></clipPath>'
        )
        texts.append(
            f'<text x="0" y="{y + 1.5:.2f}" clip-path="url(#ke{r})" '
            f'textLength="{W}" lengthAdjust="spacingAndGlyphs">'
            f'{esc(line)}</text>'
        )
        cx_end = W - 2
        cursors.append(
            f'<rect x="0" y="{y + 1:.2f}" width="3" height="{CHAR_H - 2:.2f}" '
            f'fill="{CURSOR}" opacity="0"><animate attributeName="x" '
            f'from="0" to="{cx_end}" begin="{begin}s" dur="{row_dur}s" '
            f'fill="freeze" calcMode="spline" keyTimes="0;1" '
            f'keySplines="0.25 0.1 0.25 1"/><animate attributeName="opacity" '
            f'values="0;1;1;0" keyTimes="0;0.12;0.82;1" begin="{begin}s" '
            f'dur="{row_dur}s" fill="freeze"/></rect>'
        )

    prompt_y = 1.5
    prompt = (
        f'<text x="0" y="{prompt_y:.2f}" font-size="13">'
        f'<tspan fill="{PURPLE}">{esc(user)}@github</tspan>'
        f'<tspan fill="{MUTED}"> ~ $ </tspan>'
        f'<tspan fill="{FG}">whoami</tspan>'
        f'<tspan fill="{CURSOR}"> _</tspan></text>'
    )

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
  <rect width="{W}" height="{H}" fill="{BG}"/>
  {prompt}
  <defs>
    {chr(10).join("    " + c for c in clips)}
  </defs>
  <g font-size="12" fill="{FILL}" dominant-baseline="hanging" shape-rendering="crispEdges">
    {chr(10).join("    " + t for t in texts)}
  </g>
  <g>
    {chr(10).join("    " + c for c in cursors)}
  </g>
  <title>{esc(user)} — knight emblem</title>
</svg>'''


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "iliv-knight.svg"
    username = sys.argv[2] if len(sys.argv) > 2 else "ILIV007"
    svg = make_svg(username)
    Path(out).write_text(svg, encoding="utf-8")
    print(f"Written {out} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
