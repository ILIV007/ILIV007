#!/usr/bin/env python3
"""
fetch_contributions.py — fetch public GitHub contribution calendar.
No token, no GraphQL. Scrapes github.com/users/<username>/contributions
and writes data/contributions.json with raw days + derived stats.

Usage:
  GITHUB_USERNAME=ILIV007 python scripts/fetch_contributions.py
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta
from collections import defaultdict

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GITHUB_USERNAME", "ILIV007")
OUTPUT_JSON = "data/contributions.json"
URL = f"https://github.com/users/{USERNAME}/contributions"
UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def fetch_html() -> str:
    print(f"Fetching {URL}...")
    resp = requests.get(
        URL,
        headers={"User-Agent": UA, "Accept": "text/html"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.text


def parse_days(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    # GitHub renders days as <td class="ContributionCalendar-day"> with
    # data-date + data-level + id. Counts live in <tool-tip for="<id>">.
    counts: dict[str, int] = {}
    for tip in soup.find_all("tool-tip"):
        tip_id = tip.get("for", "")
        text = tip.get_text()
        m = re.search(r"(\d+)\s+contributions?", text, re.I)
        if m:
            counts[tip_id] = int(m.group(1))
        elif re.search(r"no contributions", text, re.I):
            counts[tip_id] = 0

    days: list[dict] = []
    for cell in soup.select("td.ContributionCalendar-day, rect.ContributionCalendar-day"):
        date = cell.get("data-date")
        if not date:
            continue
        level = int(cell.get("data-level", 0))
        cell_id = cell.get("id", "")
        count = counts.get(cell_id, 0)
        days.append({"date": date, "count": count, "level": level})

    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"]) if days else None

    month_map: dict[str, int] = defaultdict(int)
    for d in days:
        month_map[d["date"][:7]] += d["count"]

    # streaks
    longest = run = 0
    for d in days:
        if d["count"] > 0:
            run += 1
            longest = max(longest, run)
        else:
            run = 0

    # current streak
    current = 0
    for d in reversed(days):
        if d["count"] > 0:
            current += 1
        elif current > 0:
            break

    # check if streak is stale (> 2.5 days since last contribution)
    last_nonzero = next((d for d in reversed(days) if d["count"] > 0), None)
    if last_nonzero:
        last_dt = datetime.strptime(last_nonzero["date"], "%Y-%m-%d")
        if (datetime.now() - last_dt).days > 2:
            current = 0

    monthly = [{"month": m, "count": c} for m, c in sorted(month_map.items())]

    return {
        "total": total,
        "currentStreak": current,
        "longestStreak": longest,
        "bestDay": (
            {"date": best["date"], "count": best["count"]} if best else None
        ),
        "monthly": monthly,
        "firstDate": days[0]["date"] if days else None,
        "lastDate": days[-1]["date"] if days else None,
        "daysCount": len(days),
    }


def main():
    try:
        html = fetch_html()
        days = parse_days(html)
        if not days:
            raise ValueError("no day cells parsed")
        source = "live"
        print(f"Parsed {len(days)} days from live GitHub data.")
    except Exception as e:
        print(f"Live fetch failed ({e}), using demo data.")
        days = demo_days()
        source = "demo"

    data = {
        "username": USERNAME.lower(),
        "days": days,
        "stats": compute_stats(days),
        "source": source,
        "fetchedAt": datetime.now().isoformat(),
    }

    out = Path(OUTPUT_JSON) if False else __import__("pathlib").Path(OUTPUT_JSON)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Written {out} ({len(days)} days, source={source})")


def demo_days() -> list[dict]:
    """Deterministic demo data so the heatmap always animates."""
    days = []
    today = datetime.now()
    start = today - timedelta(days=53 * 7 - 1)
    seed = 0
    for i in range(53 * 7):
        d = start + timedelta(days=i)
        if d > today:
            break
        seed = (seed * 9301 + 49297) % 233280
        r = seed / 233280
        weekend = d.weekday() >= 5
        count = 0
        if r > 0.3:
            count = int(r * (5 if weekend else 14)) + (0 if weekend else 1)
        if r > 0.96:
            count += 8
        level = 0
        if count >= 15:
            level = 4
        elif count >= 9:
            level = 3
        elif count >= 5:
            level = 2
        elif count >= 2:
            level = 1
        days.append({
            "date": d.strftime("%Y-%m-%d"),
            "count": count,
            "level": level,
        })
    return days


if __name__ == "__main__":
    main()
