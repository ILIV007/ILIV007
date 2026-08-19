#!/usr/bin/env python3
"""
make_profile_svg.py — ONE animated SVG that looks like the terminal blog.
Rendered in the GitHub profile README via <img>. No JS (GitHub strips it).

Usage: python scripts/make_profile_svg.py [output.svg]
Default: → profile.svg
"""
import sys
from pathlib import Path

W, H = 860, 520
BG = "#07070e"; FG = "#a8a3c9"; HI = "#f0edff"
P1 = "#b388ff"; P2 = "#5fb0ff"; DIM = "#544e78"
OK = "#3fe0a0"; WARN = "#ffc861"; RED = "#ff5f87"

def esc(s):
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

BOOT_LINES = [
    ("", "tty-blog bios — neon cold start"),
    ("ok", "mounting /dev/blog ... 5 posts, 3 projects"),
    ("ok", "loading commands ... ls, cat, links, whoami, neofetch"),
    ("ok", "cursor blink rate ... 1.06s (CRT-accurate)"),
    ("warn", "nostalgia levels ... within legal limits"),
    ("ok", "starting fakesh 1.06 ... done"),
]

BANNER_CHARS = {
    "I": ["10","10","10","10","10","10"],
    "L": ["11","10","10","10","10","11"],
    "V": ["10 01","10 01","10 01","10 01","01 10","00 00"],
    "0": ["01110","10001","10001","10001","10001","01110"],
    "7": ["11111","00010","00100","01000","01000","01000"],
}
BANNER = "ILIV007"
BP = 5; BG_GAP = 1; BC_GAP = 8; BROWS = 6; BCOLS = 5
BW = len(BANNER) * BCOLS * (BP + BG_GAP) + (len(BANNER) - 1) * BC_GAP
BH = BROWS * (BP + BG_GAP)

def banner_rects(ox, oy):
    rects = []
    cx = ox
    for ci, ch in enumerate(BANNER):
        bm = BANNER_CHARS.get(ch)
        if not bm: continue
        col = P1 if ci < 4 else P2
        for r in range(BROWS):
            row = bm[r]
            parts = row.split(" ")
            po = 0
            for part in parts:
                for c in range(len(part)):
                    if part[c] == "1":
                        x = cx + (po + c) * (BP + BG_GAP)
                        y = oy + r * (BP + BG_GAP)
                        rects.append(f'<rect x="{x}" y="{y}" width="{BP}" height="{BP}" rx="1" fill="{col}"/>')
                po += len(part)
        cx += BCOLS * (BP + BG_GAP) + BC_GAP
    return "\n  ".join(rects)

INFO_LINES = [
    ("OS", "tty-blog neon", P1),
    ("Kernel", "single-file.html", P1),
    ("Shell", "fakesh 1.06", P1),
    ("Theme", "neon (purple)", P1),
    ("Deps", "0", P1),
]
CONTACT_LINES = [
    ("github", "github.com/ILIV007"),
    ("email", "ILIV007@proton.me"),
    ("telegram", "@ILIVIR3"),
    ("website", "ilivir3.pages.dev"),
]

def make_svg():
    title_bar_h = 32; pad_x = 22
    boot_y = title_bar_h + 20; boot_lh = 20
    boot_d = 0.15; boot_st = 0.25; boot_dur = 0.4
    boot_texts = []
    for i, (tag, text) in enumerate(BOOT_LINES):
        y = boot_y + i * boot_lh
        d = f"{boot_d + i * boot_st:.2f}"
        tc = OK if tag == "ok" else WARN if tag == "warn" else DIM
        tt = f'<tspan fill="{tc}" font-weight="700">[ {tag} ]</tspan> ' if tag else ""
        boot_texts.append(f'<text x="{pad_x}" y="{y}" font-family="\'Courier New\', monospace" font-size="13" fill="{DIM}" opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{d}s" dur="{boot_dur}s" fill="freeze"/>{tt}{esc(text)}</text>')

    ban_y = boot_y + len(BOOT_LINES) * boot_lh + 12
    ban_x = (W - BW) / 2
    ban_d = f"{boot_d + len(BOOT_LINES) * boot_st:.2f}"
    ban_g = f'<g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{ban_d}s" dur="0.6s" fill="freeze"/>{banner_rects(ban_x, ban_y)}</g>'

    tag_y = ban_y + BH + 16
    tag_d = f"{float(ban_d) + 0.4:.2f}"
    tag = f'<text x="{W/2}" y="{tag_y}" text-anchor="middle" font-family="\'Courier New\', monospace" font-size="12" fill="{DIM}" opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{tag_d}s" dur="0.4s" fill="freeze"/>~/dev — a developer blog that behaves like a TTY</text>'

    info_y = tag_y + 24; info_lh = 18
    info_sd = float(tag_d) + 0.2
    info_ts = []
    for i, (k, v, vc) in enumerate(INFO_LINES):
        y = info_y + i * info_lh
        d = f"{info_sd + i * 0.1:.2f}"
        info_ts.append(f'<text x="{pad_x}" y="{y}" font-family="\'Courier New\', monospace" font-size="13" opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{d}s" dur="0.3s" fill="freeze"/><tspan fill="{P1}" font-weight="700">{esc(k.ljust(10))}</tspan><tspan fill="{vc}">{esc(v)}</tspan></text>')

    con_y = info_y + len(INFO_LINES) * info_lh + 14
    con_ts = []
    for i, (lb, v) in enumerate(CONTACT_LINES):
        y = con_y + i * info_lh
        d = f"{info_sd + len(INFO_LINES) * 0.1 + i * 0.1:.2f}"
        con_ts.append(f'<text x="{pad_x}" y="{y}" font-family="\'Courier New\', monospace" font-size="13" opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{d}s" dur="0.3s" fill="freeze"/><tspan fill="{P2}" font-weight="700">{esc(lb.ljust(10))}</tspan><tspan fill="{HI}">{esc(v)}</tspan></text>')

    pr_y = con_y + len(CONTACT_LINES) * info_lh + 16
    pr_d = f"{info_sd + (len(INFO_LINES) + len(CONTACT_LINES)) * 0.1 + 0.2:.2f}"
    prompt = f'<text x="{pad_x}" y="{pr_y}" font-family="\'Courier New\', monospace" font-size="13" opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{pr_d}s" dur="0.3s" fill="freeze"/><tspan fill="{P2}" font-weight="700">guest@iliv007</tspan><tspan fill="{DIM}">:</tspan><tspan fill="{P1}" font-weight="700">~</tspan><tspan fill="{P2}" font-weight="700">$ </tspan><tspan fill="{HI}">help</tspan></text>'
    cur = f'<rect x="{pad_x + 210}" y="{pr_y - 12}" width="8" height="14" rx="1" fill="{P1}" opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{pr_d}s" dur="0.2s" fill="freeze"/><animate attributeName="opacity" values="1;0;1" keyTimes="0;0.5;1" begin="{float(pr_d) + 0.3:.2f}s" dur="1.06s" repeatCount="indefinite"/></rect>'

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" ry="10" fill="{BG}" stroke="{DIM}" stroke-width="1" opacity="0.5"/>
  <path d="M0.5 10 a10 10 0 0 1 10 -9.5 H{W-10.5} a10 10 0 0 1 10 9.5 V{title_bar_h} H0.5 Z" fill="#0d0d18"/>
  <line x1="0.5" y1="{title_bar_h}" x2="{W-0.5}" y2="{title_bar_h}" stroke="{DIM}" stroke-width="1" opacity="0.5"/>
  <circle cx="16" cy="16" r="5" fill="#ff5f56"/>
  <circle cx="33" cy="16" r="5" fill="#ffbd2e"/>
  <circle cx="50" cy="16" r="5" fill="#27c93f"/>
  <text x="{W/2}" y="20.5" text-anchor="middle" font-family="'Courier New', monospace" font-size="11" fill="{DIM}">guest@iliv007: ~ — tty0</text>
  <text x="{W-18}" y="20.5" text-anchor="end" font-family="'Courier New', monospace" font-size="11" fill="{OK}">● live</text>
  {chr(10).join("  " + t for t in boot_texts)}
  {ban_g}
  {tag}
  {chr(10).join("  " + t for t in info_ts)}
  {chr(10).join("  " + t for t in con_ts)}
  {prompt}
  {cur}
  <title>ILIV007 — terminal</title>
</svg>'''

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "profile.svg"
    svg = make_svg()
    Path(out).write_text(svg, encoding="utf-8")
    print(f"Written {out} ({len(svg)} bytes)")
