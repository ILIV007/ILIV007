#!/usr/bin/env python3
"""
make_knight_svg.py — a professional ASCII portrait of a knight helmet,
rendered from a photo via the image→ASCII pipeline.

Pipeline:
  1. Load knight-portrait.png, convert to grayscale.
  2. Boost local contrast with CLAHE.
  3. Binarize (dark = helmet, light = background).
  4. Morphological "inside" fill (fills visor/breath holes).
  5. Map brightness to a char ramp (bright→sparse, dark→dense).

The knight is rendered as <text> with a monospace font. The `whoami` prompt
is the first line inside the SVG. Each row types itself in via a left-to-right
SMIL clip wipe with a gold cursor.

Usage:
  python scripts/make_knight_svg.py [source.png] [output.svg] [username]

Defaults: knight-portrait.png → knight.svg, username ILIV007
"""

import sys
from pathlib import Path
import numpy as np
from PIL import Image

RAMP = " .'`,:-=+*rcs#%@".split("")  # bright (sparse) → dark (dense)
COLS = 90
ROWS = 44
FONT_SIZE = 11
CHAR_H = 11
SVG_W = 400
FONT = "'Courier New', Courier, monospace"
FILL = "#c8b5ff"
BG = "#0d1117"
CURSOR = "#e3b341"
PURPLE = "#bc8cff"
MUTED = "#8b949e"
FG = "#c9d1d9"
THRESH = 130


def build_grid(img_path: str) -> list[str]:
    img = Image.open(img_path).convert("L")
    img = img.resize((600, 600), Image.Resampling.LANCZOS)
    arr = np.array(img, dtype=np.float32)
    # CLAHE fallback via simple histogram equalize
    try:
        import cv2
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        arr = clahe.apply(arr.astype(np.uint8)).astype(np.float32)
    except ImportError:
        from PIL import ImageOps
        arr = np.array(ImageOps.equalize(Image.fromarray(arr.astype(np.uint8))), dtype=np.float32)
    # Downsample to grid
    small = Image.fromarray(arr.astype(np.uint8)).resize((COLS, ROWS), Image.Resampling.LANCZOS)
    arr = np.array(small, dtype=np.float32)

    binary = np.where(arr < THRESH, 0, 255)
    R = 1
    inside = np.zeros((ROWS, COLS), dtype=bool)
    for y in range(ROWS):
        for x in range(COLS):
            y0, y1 = max(0, y - R), min(ROWS, y + R + 1)
            x0, x1 = max(0, x - R), min(COLS, x + R + 1)
            if np.any(binary[y0:y1, x0:x1] == 0):
                inside[y, x] = True

    rows = []
    for y in range(ROWS):
        line = ""
        for x in range(COLS):
            if not inside[y, x]:
                line += RAMP[0]
            else:
                b = arr[y, x]
                t = (255 - b) / 255.0
                t = t ** 0.6
                idx = min(len(RAMP) - 1, int(t * (len(RAMP) - 1) + 0.5))
                line += RAMP[max(2, idx)]
        rows.append(line)
    return rows


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def make_svg(rows: list[str], username: str = "ILIV007") -> str:
    user = "".join(c for c in username if c not in '<>"')[:24]
    row_stagger = 0.022
    row_dur = 0.25
    start_delay = 0.2
    prompt_h = 24
    total_h = prompt_h + len(rows) * CHAR_H + 8

    clips, texts, cursors = [], [], []
    for r, line in enumerate(rows):
        begin = f"{start_delay + r * row_stagger:.3f}"
        y = prompt_h + r * CHAR_H
        clips.append(
            f'<clipPath id="kp{r}"><rect x="0" y="{y}" width="0" '
            f'height="{CHAR_H}"><animate attributeName="width" '
            f'from="0" to="{SVG_W}" begin="{begin}s" dur="{row_dur}s" '
            f'fill="freeze" calcMode="spline" keyTimes="0;1" '
            f'keySplines="0.25 0.1 0.25 1"/></rect></clipPath>'
        )
        texts.append(
            f'<text x="0" y="{y + 1}" font-family="{FONT}" '
            f'font-size="{FONT_SIZE}" clip-path="url(#kp{r})">{esc(line)}</text>'
        )
        cx_end = SVG_W - 2
        cursors.append(
            f'<rect x="0" y="{y}" width="2" height="{CHAR_H - 1}" '
            f'fill="{CURSOR}" opacity="0"><animate attributeName="x" '
            f'from="0" to="{cx_end}" begin="{begin}s" dur="{row_dur}s" '
            f'fill="freeze" calcMode="spline" keyTimes="0;1" '
            f'keySplines="0.25 0.1 0.25 1"/><animate attributeName="opacity" '
            f'values="0;1;1;0" keyTimes="0;0.12;0.82;1" begin="{begin}s" '
            f'dur="{row_dur}s" fill="freeze"/></rect>'
        )

    prompt = (
        f'<text x="0" y="16" font-family="{FONT}" '
        f'font-size="{FONT_SIZE + 2}" font-weight="700">'
        f'<tspan fill="{PURPLE}">{esc(user)}@github</tspan>'
        f'<tspan fill="{MUTED}"> ~ $ </tspan>'
        f'<tspan fill="{FG}">whoami</tspan>'
        f'<tspan fill="{CURSOR}"> ▮</tspan></text>'
    )

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="{total_h}" viewBox="0 0 {SVG_W} {total_h}" font-family="{FONT}" font-size="{FONT_SIZE}">
  <rect width="{SVG_W}" height="{total_h}" fill="{BG}"/>
  {prompt}
  <defs>
    {chr(10).join("    " + c for c in clips)}
  </defs>
  <g fill="{FILL}" dominant-baseline="hanging">
    {chr(10).join("    " + t for t in texts)}
  </g>
  <g>
    {chr(10).join("    " + c for c in cursors)}
  </g>
  <title>{esc(user)} — knight portrait</title>
</svg>'''


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "knight-portrait.png"
    out = sys.argv[2] if len(sys.argv) > 2 else "knight.svg"
    username = sys.argv[3] if len(sys.argv) > 3 else "ILIV007"
    print(f"Building ASCII grid from {src}...")
    rows = build_grid(src)
    print(f"Generating SVG ({COLS}×{ROWS})...")
    svg = make_svg(rows, username)
    Path(out).write_text(svg, encoding="utf-8")
    print(f"Written {out} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
