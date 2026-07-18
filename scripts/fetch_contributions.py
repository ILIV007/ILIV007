#!/usr/bin/env python3
"""
Fetch public GitHub contribution calendar — no token required.

Usage:
  python scripts/fetch_contributions.py
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta
from collections import defaultdict

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GITHUB_USERNAME", "YOUR_USERNAME")
OUTPUT_JSON = "data/contributions.json"
URL = f"https://github.com/users/{USERNAME}/contributions"


def fetch_html() -> str:
    print(f"🌐 Fetching {URL}...")
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html",
    }
    resp = requests.get(URL, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_contributions(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    days = []

    for td in soup.find_all("td"):
        date_str = td.get("data-date")
        level_str = td.get("data-level")
        if not date_str or level_str is None:
            continue

        aria = td.get("aria-label", "")
        count = 0
        m = re.search(r"(\d+) contribution", aria)
        if m:
            count = int(m.group(1))
        elif "No contribution" in aria:
            count = 0

        days.append({
            "date": date_str,
            "level": int(level_str),
            "count": count,
        })

    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days: list[dict]) -> dict:
    if not days:
        return {}

    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"])
    best_day = {"date": best["date"], "count": best["count"]}

    longest_streak = 0
    temp_streak = 0
    for d in days:
        if d["count"] > 0:
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 0

    today = datetime.now().date()
    current_streak = 0
    for d in reversed(days):
        d_date = datetime.strptime(d["date"], "%Y-%m-%d").date()
        if d_date > today:
            continue
        if d["count"] > 0:
            expected = today - timedelta(days=current_streak)
            if d_date == expected or (current_streak == 0 and d_date <= today):
                current_streak += 1
            else:
                break
        else:
            if d_date == today or d_date == today - timedelta(days=current_streak):
                break

    monthly = defaultdict(int)
    for d in days:
        ym = d["date"][:7]
        monthly[ym] += d["count"]

    return {
        "total": total,
        "best_day": best_day,
        "longest_streak": longest_streak,
        "current_streak": current_streak,
        "monthly_totals": dict(monthly),
    }


def main():
    if USERNAME == "YOUR_USERNAME":
        print("⚠️  Set GITHUB_USERNAME env var or edit the script.")
        sys.exit(1)

    html = fetch_html()
    days = parse_contributions(html)
    stats = compute_stats(days)

    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    payload = {
        "username": USERNAME,
        "fetched_at": datetime.now().isoformat(),
        "days": days,
        "stats": stats,
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"✅ Saved {len(days)} days to {OUTPUT_JSON}")
    print(f"   Total: {stats['total']:,} | Longest: {stats['longest_streak']} | Current: {stats['current_streak']}")


if __name__ == "__main__":
    main()
