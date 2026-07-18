#!/usr/bin/env python3
"""
make_knight_svg.py — convert a prepped knight image into a self-typing
monochrome ASCII SVG.

The prepped image is downsampled to an 80×40 character grid. Each pixel's
brightness picks a glyph from a density ramp (bright → sparse, dark → dense).
The image is binarized first so the background is completely clean — only
the helmet silhouette prints. A morphological "inside" fill keeps the visor
slit and breath holes from punching holes in the shape.

Each row "types" itself in via a left-to-right SMIL clip wipe with a gold
cursor riding the edge, staggered top to bottom. Plays once and freezes.

Usage:
  python scripts/make_knight_svg.py [prepped-image] [output.svg]

Defaults: data/prepped.png → iliv-knight.svg
"""

import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps

# --- config ---
RAMP = " .:-=+*#%@"          # bright (sparse) → dark (dense)
COLS = 80
ROWS = 40
CHAR_W = 4.0
CHAR_H = 8.0
W = int(COLS * CHAR_W)       # 320
H = int(ROWS * CHAR_H)       # 320
FILL = "#c8b5ff"             # light violet
BG = "#0d1117"
CURSOR = "#e3b341"           # knight gold
THRESH = 140                 # binarization threshold
INSIDE_R = 1                 # morphological radius
MIN_DENSE_IDX = 4            # interior uses at least '#' density


def build_grid(img_path: str) -> list[str]:
    img = Image.open(img_path).convert("L")
    # Resize to grid using nearest-neighbor for crisp edges
    img = img.resize((COLS, ROWS), Image.Resampling.LANCZOS)
    arr = np.array(img, dtype=np.float32)

    # 1) Binarize: helmet (0) vs background/feature (255)
    binary = np.where(arr < THRESH, 0, 255)

    # 2) Morphological "inside" mask: a pixel is inside the helmet if any
    #    pixel within radius R is black (0).
    inside = np.zeros((ROWS, COLS), dtype=bool)
    for y in range(ROWS):
        for x in range(COLS):
            y0, y1 = max(0, y - INSIDE_R), min(ROWS, y + INSIDE_R + 1)
            x0, x1 = max(0, x - INSIDE_R), min(COLS, x + INSIDE_R + 1)
            if np.any(binary[y0:y1, x0:x1] == 0):
                inside[y, x] = True

    # 3) Map to ramp
    rows: list[str] = []
    for y in range(ROWS):
        line = ""
        for x in range(COLS):
            if not inside[y, x]:
                line += RAMP[0]  # background → blank
            else:
                b = arr[y, x]
                t = (255 - b) / 255.0
                t = t ** 0.5  # strong push toward dense
                idx = min(len(RAMP) - 1, int(t * (len(RAMP) - 1) + 0.5))
                if idx < MIN_DENSE_IDX:
                    idx = MIN_DENSE_IDX
                line += RAMP[idx]
        rows.append(line)
    return rows


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def make_svg(rows: list[str]) -> str:
    row_stagger = 0.028
    row_dur = 0.32
    start_delay = 0.15

    clips, texts, cursors = [], [], []
    for r, line in enumerate(rows):
        begin = f"{start_delay + r * row_stagger:.3f}"
        y = r * CHAR_H
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
            f'<rect x="0" y="{y + 1:.2f}" width="2.4" height="{CHAR_H - 2:.2f}" '
            f'fill="{CURSOR}" opacity="0"><animate attributeName="x" '
            f'from="0" to="{cx_end}" begin="{begin}s" dur="{row_dur}s" '
            f'fill="freeze" calcMode="spline" keyTimes="0;1" '
            f'keySplines="0.25 0.1 0.25 1"/><animate attributeName="opacity" '
            f'values="0;1;1;0" keyTimes="0;0.12;0.82;1" begin="{begin}s" '
            f'dur="{row_dur}s" fill="freeze"/></rect>'
        )

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <defs>
    {chr(10).join("    " + c for c in clips)}
  </defs>
  <g font-size="8" fill="{FILL}" dominant-baseline="hanging" shape-rendering="crispEdges">
    {chr(10).join("    " + t for t in texts)}
  </g>
  <g>
    {chr(10).join("    " + c for c in cursors)}
  </g>
  <title>ILIV007 — knight emblem</title>
</svg>'''


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "data/prepped.png"
    out = sys.argv[2] if len(sys.argv) > 2 else "iliv-knight.svg"
    print(f"Building ASCII grid from {src}...")
    rows = build_grid(src)
    print(f"Generating SVG ({COLS}×{ROWS})...")
    svg = make_svg(rows)
    Path(out).write_text(svg, encoding="utf-8")
    print(f"Written {out} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
