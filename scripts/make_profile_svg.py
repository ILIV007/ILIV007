#!/usr/bin/env python3
"""
make_profile_svg.py — ONE combined SVG containing the entire GitHub profile:
a single terminal window with the activity feed at top, then the knight
emblem (rect-based, left) and the neofetch info card (right) side by side —
all in ONE coordinate system, ONE frame.

No separate images, no floating HTML prompt text. The README just embeds
this single SVG. Prompts (`tail -f activity.log`, `whoami`) live inside
as colored <text> tspans.

The knight is rendered with RECT cells (pixel-exact, font-independent).

Usage:
  GITHUB_USERNAME=ILIV007 python scripts/make_profile_svg.py [output.svg]

Defaults: → profile.svg
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime, timezone

import requests

USERNAME = os.environ.get("GITHUB_USERNAME", "ILIV007")

# ── layout ──────────────────────────────────────────────────────────────
W = 860
PAD = 24
TITLE_BAR_H = 32
ACT_PROMPT_Y = TITLE_BAR_H + 26
ACT_LINE_H = 24
ACT_LINES = 6
ACT_SECTION_H = 30 + ACT_LINES * ACT_LINE_H + 12
DIVIDER_Y = TITLE_BAR_H + ACT_SECTION_H + 16
WHO_PROMPT_Y = DIVIDER_Y + 24
CONTENT_Y = WHO_PROMPT_Y + 28

KNIGHT_COLS = 25
KNIGHT_ROWS = 23
CELL = 13
GAP = 2
PITCH = CELL + GAP
KNIGHT_W = KNIGHT_COLS * PITCH   # 375
KNIGHT_H = KNIGHT_ROWS * PITCH   # 345
KNIGHT_X = PAD

CARD_X = PAD + KNIGHT_W + 20
CARD_W = W - CARD_X - PAD

H = int(CONTENT_Y + max(KNIGHT_H, 360) + PAD)

# ── colors ──────────────────────────────────────────────────────────────
BG = "#0d1117"
TITLE_BG = "#161b22"
BORDER = "#30363d"
FG = "#c9d1d9"
MUTED = "#8b949e"
GOLD = "#e3b341"
PURPLE = "#bc8cff"
LAVENDER = "#d2a8ff"
GREEN = "#39d353"
FONT = "'Courier New', Courier, monospace"

DENSITY_FILL = {
    " ": "transparent", ".": "#2d1b4e", ":": "#4c1d95", "-": "#5b21b6",
    "+": "#e3b341", "=": "#c4b5fd", "@": "#a855f7", "#": "#9333ea",
    "|": "#6d28d9", "/": "#6d28d9", "\\": "#6d28d9", "~": "#7c3aed", "^": "#8b5cf6",
}

KNIGHT_ART = [
    "        .  :  .        ",
    "         :::::         ",
    "          ...          ",
    "        .-:::-.        ",
    "       .---::---.      ",
    "       /----::----\\   ",
    "       |@@@@@@@@@@@@@| ",
    "       |@@@@@@+@@@@@@| ",
    "       |@@@@@@+@@@@@@| ",
    "       |@@@@@@@@@@@@@| ",
    "       |@@@@@@@@@@@@@| ",
    "       |@@@@@@@@@@@@@| ",
    "       |@@@@@@@@@@@@@| ",
    "       |=============| ",
    "       |=============| ",
    "       |@@@@@@@@@@@@@| ",
    "       |@@:@@:@@:@@:@| ",
    "       |@@@@@@@@@@@@@| ",
    "        \\@@@@@@@@@@@/  ",
    "    .---@@@@@@@@@@@---.",
    "    |@@@@@@@@@@@@@@@@@|",
    "    |@@@@@@@@@@@@@@@@@|",
    "     \\@@@@@@@@@@@@@@@/ ",
]


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def time_ago(iso: str) -> str:
    diff = time.time() - datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp()
    m = int(diff / 60)
    if m < 1: return "just now"
    if m < 60: return f"{m}m ago"
    h = m // 60
    if h < 24: return f"{h}h ago"
    d = h // 24
    if d < 7: return f"{d}d ago"
    return f"{d // 7}w ago"


# ── activity fetch ──────────────────────────────────────────────────────
def format_event(raw: dict) -> dict | None:
    etype = raw.get("type", "")
    repo = raw.get("repo", {}).get("name", "unknown")
    created = raw.get("created_at", "")
    p = raw.get("payload", {})
    detail = ""
    if etype == "PushEvent": detail = f"pushed {p.get('size') or len(p.get('commits', [])) or 1} commit(s) to"
    elif etype == "WatchEvent": detail = "starred"
    elif etype == "CreateEvent": detail = f"created {p.get('ref_type', 'branch')} in"
    elif etype == "ForkEvent": detail = "forked"
    elif etype == "IssuesEvent": detail = f"{p.get('action', 'opened')} issue in"
    elif etype == "PullRequestEvent": detail = f"{p.get('action', 'opened')} PR in"
    elif etype == "ReleaseEvent": detail = "released"
    elif etype == "PublicEvent": detail = "made public"
    elif etype == "DeleteEvent": detail = f"deleted {p.get('ref_type', 'branch')} in"
    elif etype == "IssueCommentEvent": detail = "commented in"
    else: detail = "activity in"
    return {"type": etype, "repo": repo, "createdAt": created, "detail": detail}


def demo_events(username: str) -> list[dict]:
    now = time.time()
    def mins(m): return datetime.fromtimestamp(now - m * 60, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return [
        {"type": "PushEvent", "repo": f"{username}/ILIV007", "createdAt": mins(47), "detail": "pushed 3 commit(s) to"},
        {"type": "WatchEvent", "repo": "vercel/next.js", "createdAt": mins(180), "detail": "starred"},
        {"type": "CreateEvent", "repo": f"{username}/ILIV007", "createdAt": mins(320), "detail": "created branch in"},
        {"type": "PullRequestEvent", "repo": f"{username}/ILIV007", "createdAt": mins(720), "detail": "opened PR in"},
        {"type": "IssuesEvent", "repo": f"{username}/ILIV007", "createdAt": mins(1440), "detail": "opened issue in"},
        {"type": "ForkEvent", "repo": "shadcn-ui/ui", "createdAt": mins(2880), "detail": "forked"},
    ]


def fetch_events() -> tuple[list[dict], str]:
    try:
        resp = requests.get(
            f"https://api.github.com/users/{USERNAME}/events/public",
            headers={"Accept": "application/vnd.github+json", "User-Agent": "ILIV007-profile-readme"},
            timeout=15,
        )
        resp.raise_for_status()
        raw = resp.json()
        if not raw: raise ValueError("no events")
        events = []
        for e in raw:
            f = format_event(e)
            if f: events.append(f)
            if len(events) >= 6: break
        if not events: raise ValueError("no parseable events")
        print(f"Fetched {len(events)} live events.")
        return events, "live"
    except Exception as e:
        print(f"Live fetch failed ({e}), using demo events.")
        return demo_events(USERNAME), "demo"


# ── SVG builders ────────────────────────────────────────────────────────
def build_knight_rects() -> tuple[list[str], list[str], list[str]]:
    clips, cell_groups, cursors = [], [], []
    row_stagger = 0.04
    row_dur = 0.28
    start_delay = 0.4

    for r in range(KNIGHT_ROWS):
        row = (KNIGHT_ART[r] + " " * KNIGHT_COLS)[:KNIGHT_COLS]
        begin = f"{start_delay + r * row_stagger:.3f}"
        y = r * PITCH

        clips.append(
            f'<clipPath id="kr{r}"><rect x="{KNIGHT_X}" y="{CONTENT_Y + y:.2f}" '
            f'width="0" height="{PITCH}"><animate attributeName="width" '
            f'from="0" to="{KNIGHT_W}" begin="{begin}s" dur="{row_dur}s" '
            f'fill="freeze" calcMode="spline" keyTimes="0;1" '
            f'keySplines="0.25 0.1 0.25 1"/></rect></clipPath>'
        )

        row_cells = []
        for c in range(KNIGHT_COLS):
            ch = row[c]
            fill = DENSITY_FILL.get(ch, "transparent")
            if fill == "transparent": continue
            row_cells.append(
                f'<rect x="{KNIGHT_X + c * PITCH:.2f}" y="{CONTENT_Y + y:.2f}" '
                f'width="{CELL}" height="{CELL}" rx="2" fill="{fill}"/>'
            )
        cell_groups.append(f'<g clip-path="url(#kr{r})">{"".join(row_cells)}</g>')

        cx_end = KNIGHT_X + KNIGHT_W - 3
        cursors.append(
            f'<rect x="{KNIGHT_X}" y="{CONTENT_Y + y + 1:.2f}" width="4" '
            f'height="{PITCH - 2}" fill="{GOLD}" opacity="0">'
            f'<animate attributeName="x" from="{KNIGHT_X}" to="{cx_end}" '
            f'begin="{begin}s" dur="{row_dur}s" fill="freeze" calcMode="spline" '
            f'keyTimes="0;1" keySplines="0.25 0.1 0.25 1"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" '
            f'keyTimes="0;0.12;0.82;1" begin="{begin}s" dur="{row_dur}s" fill="freeze"/></rect>'
        )
    return clips, cell_groups, cursors


def build_info_card(user: str) -> list[str]:
    groups = []
    x = CARD_X + 16
    y = CONTENT_Y + 6
    line_h = 24
    delay = 0.5
    stagger = 0.1

    rows = [
        f'<tspan fill="{GOLD}">◆</tspan>  <tspan fill="{FG}" font-weight="700" font-size="16">ILIYA</tspan>',
        f'<tspan fill="{GOLD}">class   </tspan><tspan fill="{LAVENDER}">developer</tspan>',
        f'<tspan fill="{GOLD}">level   </tspan><tspan fill="{LAVENDER}">?? · quest just begun</tspan>',
        f'<tspan fill="{GOLD}">stack   </tspan><tspan fill="{LAVENDER}">learning · building</tspan>',
        f'<tspan fill="{GOLD}">channel </tspan><tspan fill="{LAVENDER}">ILIVIR3</tspan>',
        f'<tspan fill="{MUTED}" font-style="italic">  "start small, stay curious"</tspan>',
        f'<tspan fill="{GOLD}">guild   </tspan><tspan fill="{LAVENDER}">github.com/{esc(user)}</tspan>',
    ]
    for r in rows:
        groups.append(
            f'<g class="cardline" style="animation-delay:{delay:.2f}s">'
            f'<text x="{x}" y="{y:.1f}" font-family="{FONT}" font-size="13" '
            f'font-weight="600">{r}</text></g>'
        )
        y += line_h
        delay += stagger
    return groups


def build_activity_lines(events: list[dict], user: str) -> list[str]:
    lines = []
    x = PAD
    y = ACT_PROMPT_Y + 22
    base_delay = 0.3
    stagger = 0.12

    for i, e in enumerate(events[:ACT_LINES]):
        delay = f"{base_delay + i * stagger:.2f}"
        t = time_ago(e["createdAt"])
        is_own = e["repo"].lower().startswith(user.lower() + "/")
        repo_color = GOLD if is_own else LAVENDER
        lines.append(
            f'<g class="logline" style="animation-delay:{delay}s">'
            f'<text x="{x}" y="{y:.1f}" font-family="{FONT}" font-size="13">'
            f'<tspan fill="{MUTED}">[{esc(t)}]</tspan> '
            f'<tspan fill="{GREEN}">{esc(e["detail"])}</tspan> '
            f'<tspan fill="{repo_color}">{esc(e["repo"])}</tspan>'
            f'</text></g>'
        )
        y += ACT_LINE_H
    return lines


def make_svg(events: list[dict], source: str) -> str:
    user = USERNAME
    badge_color = GREEN if source == "live" else GOLD

    knight_clips, knight_cells, knight_cursors = build_knight_rects()
    card_lines = build_info_card(user)
    act_lines = build_activity_lines(events, user)

    act_prompt = (
        f'<text x="{PAD}" y="{ACT_PROMPT_Y:.1f}" font-family="{FONT}" '
        f'font-size="14" font-weight="700">'
        f'<tspan fill="{PURPLE}">{esc(user)}@github</tspan>'
        f'<tspan fill="{MUTED}"> ~ $ </tspan>'
        f'<tspan fill="{FG}">tail -f activity.log</tspan>'
        f'<tspan fill="{GOLD}"> ▮</tspan></text>'
    )
    who_prompt = (
        f'<text x="{PAD}" y="{WHO_PROMPT_Y:.1f}" font-family="{FONT}" '
        f'font-size="14" font-weight="700">'
        f'<tspan fill="{PURPLE}">{esc(user)}@github</tspan>'
        f'<tspan fill="{MUTED}"> ~ $ </tspan>'
        f'<tspan fill="{FG}">whoami</tspan></text>'
    )
    divider = (
        f'<line x1="{PAD}" y1="{DIVIDER_Y}" x2="{W - PAD}" y2="{DIVIDER_Y}" '
        f'stroke="{BORDER}" stroke-width="1" stroke-dasharray="3 4"/>'
    )

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <style>
    .logline, .cardline {{ opacity: 0; animation: fadeIn 0.4s cubic-bezier(0.22,0.61,0.36,1) forwards; }}
    @keyframes fadeIn {{ from {{ opacity: 0; transform: translateX(-8px); }} to {{ opacity: 1; transform: translateX(0); }} }}
    @media (prefers-reduced-motion: reduce) {{ .logline, .cardline {{ opacity: 1; animation: none; transform: none; }} }}
  </style>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" ry="10" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
  <path d="M0.5 10 a10 10 0 0 1 10 -9.5 H{W - 10.5} a10 10 0 0 1 10 9.5 V{TITLE_BAR_H} H0.5 Z" fill="{TITLE_BG}"/>
  <line x1="0.5" y1="{TITLE_BAR_H}" x2="{W - 0.5}" y2="{TITLE_BAR_H}" stroke="{BORDER}" stroke-width="1"/>
  <circle cx="16" cy="16" r="5" fill="#ff5f56"/>
  <circle cx="33" cy="16" r="5" fill="#ffbd2e"/>
  <circle cx="50" cy="16" r="5" fill="#27c93f"/>
  <text x="{W / 2}" y="20.5" text-anchor="middle" font-family="{FONT}" font-size="12" fill="{MUTED}">{esc(user)}@github — profile</text>
  <text x="{W - 18}" y="20.5" text-anchor="end" font-family="{FONT}" font-size="11" fill="{badge_color}">● {source}</text>
  {act_prompt}
  {chr(10).join("  " + l for l in act_lines)}
  {divider}
  {who_prompt}
  <g>
    <defs>{chr(10).join("      " + c for c in knight_clips)}</defs>
    {chr(10).join("    " + c for c in knight_cells)}
    {chr(10).join("    " + c for c in knight_cursors)}
  </g>
  {chr(10).join("  " + c for c in card_lines)}
  <title>{esc(user)} — GitHub profile</title>
</svg>'''


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "profile.svg"
    events, source = fetch_events()
    svg = make_svg(events, source)
    Path(out).write_text(svg, encoding="utf-8")
    print(f"Written {out} ({len(svg)} bytes, source={source})")


if __name__ == "__main__":
    main()
