#!/usr/bin/env python3
"""
make_activity_feed.py — a LIVE GitHub activity feed rendered as an animated
terminal log SVG.

Scrapes the public events API at
  https://api.github.com/users/<username>/events/public
(no token, no auth). Renders the last ~6 events as terminal log lines that
fade+slide in one by one. The `tail -f activity.log` prompt lives INSIDE
the SVG.

Falls back to deterministic demo events if the API is rate-limited.

Usage:
  GITHUB_USERNAME=ILIV007 python scripts/make_activity_feed.py [output.svg]
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

import requests

USERNAME = os.environ.get("GITHUB_USERNAME", "ILIV007")
API_URL = f"https://api.github.com/users/{USERNAME}/events/public"
UA = "ILIV007-profile-readme"

W, H = 860, 260
BG = "#0d1117"
BORDER = "#30363d"
FG = "#c9d1d9"
MUTED = "#8b949e"
PURPLE = "#bc8cff"
GOLD = "#e3b341"
LAVENDER = "#d2a8ff"
GREEN = "#39d353"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def time_ago(iso: str) -> str:
    diff = time.time() - datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp()
    m = int(diff / 60)
    if m < 1:
        return "just now"
    if m < 60:
        return f"{m}m ago"
    h = m // 60
    if h < 24:
        return f"{h}h ago"
    d = h // 24
    if d < 7:
        return f"{d}d ago"
    return f"{d // 7}w ago"


def format_event(raw: dict) -> dict | None:
    etype = raw.get("type", "")
    repo = raw.get("repo", {}).get("name", "unknown")
    created = raw.get("created_at", "")
    payload = raw.get("payload", {})
    detail = ""

    if etype == "PushEvent":
        size = payload.get("size") or len(payload.get("commits", [])) or 1
        detail = f"pushed {size} commit{'s' if size != 1 else ''} to"
    elif etype == "WatchEvent":
        detail = "starred"
    elif etype == "CreateEvent":
        detail = f"created {payload.get('ref_type', 'branch')} in"
    elif etype == "ForkEvent":
        detail = "forked"
    elif etype == "IssuesEvent":
        detail = f"{payload.get('action', 'opened')} issue in"
    elif etype == "PullRequestEvent":
        detail = f"{payload.get('action', 'opened')} PR in"
    elif etype == "ReleaseEvent":
        detail = "released"
    elif etype == "PublicEvent":
        detail = "made public"
    elif etype == "DeleteEvent":
        detail = f"deleted {payload.get('ref_type', 'branch')} in"
    elif etype == "IssueCommentEvent":
        detail = "commented in"
    else:
        detail = "activity in"

    return {"type": etype, "repo": repo, "createdAt": created, "detail": detail}


def demo_events(username: str) -> list[dict]:
    now = time.time()
    def mins(m):
        return datetime.utcfromtimestamp(now - m * 60).strftime("%Y-%m-%dT%H:%M:%SZ")
    return [
        {"type": "PushEvent", "repo": f"{username}/ILIV007", "createdAt": mins(47), "detail": "pushed 3 commits to"},
        {"type": "WatchEvent", "repo": "vercel/next.js", "createdAt": mins(180), "detail": "starred"},
        {"type": "CreateEvent", "repo": f"{username}/ILIV007", "createdAt": mins(320), "detail": "created branch in"},
        {"type": "PullRequestEvent", "repo": f"{username}/ILIV007", "createdAt": mins(720), "detail": "opened PR in"},
        {"type": "IssuesEvent", "repo": f"{username}/ILIV007", "createdAt": mins(1440), "detail": "opened issue in"},
        {"type": "ForkEvent", "repo": "shadcn-ui/ui", "createdAt": mins(2880), "detail": "forked"},
    ]


def fetch_events() -> tuple[list[dict], str]:
    try:
        resp = requests.get(
            API_URL,
            headers={"Accept": "application/vnd.github+json", "User-Agent": UA},
            timeout=15,
        )
        resp.raise_for_status()
        raw = resp.json()
        if not raw:
            raise ValueError("no events")
        events = []
        for e in raw:
            f = format_event(e)
            if f:
                events.append(f)
            if len(events) >= 6:
                break
        if not events:
            raise ValueError("no parseable events")
        print(f"Fetched {len(events)} live events from GitHub API.")
        return events, "live"
    except Exception as e:
        print(f"Live fetch failed ({e}), using demo events.")
        return demo_events(USERNAME), "demo"


def render_svg(events: list[dict], source: str) -> str:
    events = events[:6]
    title_bar_h = 30
    pad_x = 22
    line_h = 26
    prompt_y = title_bar_h + 24
    log_start_y = prompt_y + 22

    prompt = (
        f'<text x="{pad_x}" y="{prompt_y:.1f}" font-size="14">'
        f'<tspan fill="{PURPLE}">{esc(USERNAME)}@github</tspan>'
        f'<tspan fill="{MUTED}"> ~ $ </tspan>'
        f'<tspan fill="{FG}">tail -f activity.log</tspan>'
        f'<tspan fill="{GOLD}"> _</tspan></text>'
    )

    lines = []
    base_delay = 0.3
    stagger = 0.12
    dur = 0.4

    for i, e in enumerate(events):
        y = log_start_y + i * line_h
        delay = f"{base_delay + i * stagger:.2f}"
        t = time_ago(e["createdAt"])
        is_own = e["repo"].lower().startswith(USERNAME.lower() + "/")
        repo_color = GOLD if is_own else LAVENDER
        lines.append(
            f'<g class="logline" style="animation-delay:{delay}s">'
            f'<text x="{pad_x}" y="{y:.1f}" font-size="13">'
            f'<tspan fill="{MUTED}">[{esc(t)}]</tspan> '
            f'<tspan fill="{GREEN}">{esc(e["detail"])}</tspan> '
            f'<tspan fill="{repo_color}">{esc(e["repo"])}</tspan>'
            f'</text></g>'
        )

    badge_color = GREEN if source == "live" else GOLD
    badge = (
        f'<text x="{W - 22}" y="{title_bar_h - 10:.1f}" text-anchor="end" '
        f'font-size="11" fill="{badge_color}">● {source}</text>'
    )

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
  <style>
    .logline {{ opacity: 0; animation: logline {dur}s cubic-bezier(0.22,0.61,0.36,1) forwards; }}
    @keyframes logline {{
      from {{ opacity: 0; transform: translateX(-10px); }}
      to {{ opacity: 1; transform: translateX(0); }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      .logline {{ opacity: 1; animation: none; transform: none; }}
    }}
  </style>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="8" ry="8" fill="{BG}" stroke="{BORDER}" stroke-width="1"/>
  <path d="M0.5 8 a8 8 0 0 1 8 -7.5 H{W - 8.5} a8 8 0 0 1 8 7.5 V{title_bar_h} H0.5 Z" fill="#161b22"/>
  <line x1="0.5" y1="{title_bar_h}" x2="{W - 0.5}" y2="{title_bar_h}" stroke="{BORDER}" stroke-width="1"/>
  <circle cx="14" cy="15" r="5" fill="#ff5f56"/>
  <circle cx="30" cy="15" r="5" fill="#ffbd2e"/>
  <circle cx="46" cy="15" r="5" fill="#27c93f"/>
  <text x="{W / 2}" y="19.5" text-anchor="middle" font-size="12" fill="{MUTED}">{esc(USERNAME)}@github — activity.log</text>
  {badge}
  {prompt}
  {chr(10).join("  " + l for l in lines)}
  <title>Live activity for {esc(USERNAME)}</title>
</svg>'''


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "activity-feed.svg"
    events, source = fetch_events()
    svg = render_svg(events, source)
    Path(out).write_text(svg, encoding="utf-8")
    print(f"Written {out} ({len(svg)} bytes, source={source})")


if __name__ == "__main__":
    main()
