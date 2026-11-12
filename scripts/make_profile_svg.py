#!/usr/bin/env python3
"""
make_profile_svg.py — the GitHub profile terminal art.

Stage B (2026-11-12): the SVG is STATIC on purpose. The old version fetched
live GitHub stats (repos/followers/...) and baked them into the image, so the
numbers went stale between refreshes. The profile README must contain no
variable numbers, so this generator emits one fixed SVG — no API calls, no
dependencies. The update-profile-art workflow still runs on push/schedule,
but it now regenerates byte-identical output (a no-op).

Usage: python scripts/make_profile_svg.py [output.svg]
"""
import sys
from pathlib import Path

SVG = r"""<?xml version="1.0" encoding="UTF-8"?>
<!-- ILIV007 profile terminal — neon, no JavaScript, SMIL only.
     No numbers, no stats, nothing that goes stale: fixed text only. -->
<svg xmlns="http://www.w3.org/2000/svg" width="860" height="308" viewBox="0 0 860 308">
  <defs>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2.5" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <!-- window -->
  <rect x="0.5" y="0.5" width="859" height="307" rx="10" fill="#07070e" stroke="#b388ff" stroke-width="1" opacity="0.6"/>
  <path d="M0.5 10 a10 10 0 0 1 10 -9.5 H849.5 a10 10 0 0 1 10 9.5 V32 H0.5 Z" fill="#0d0d18"/>
  <line x1="0.5" y1="32" x2="859.5" y2="32" stroke="#b388ff" stroke-width="1" opacity="0.4"/>
  <circle cx="16" cy="16" r="5" fill="#ff5f56"/>
  <circle cx="33" cy="16" r="5" fill="#ffbd2e"/>
  <circle cx="50" cy="16" r="5" fill="#27c93f"/>
  <text x="430" y="20.5" text-anchor="middle" font-family="'Courier New', monospace" font-size="11" fill="#8b85b8">guest@iliv007: ~ — tty0</text>
  <text x="842" y="20.5" text-anchor="end" font-family="'Courier New', monospace" font-size="11" fill="#3fe0a0">● live</text>

  <!-- drifting motes -->
  <circle cx="120" cy="90" r="1.5" fill="#b388ff" opacity="0.5">
    <animate attributeName="opacity" values="0.15;0.7;0.15" dur="4s" repeatCount="indefinite"/>
    <animateTransform attributeName="transform" type="translate" values="0,0;0,-8;0,0" dur="4s" repeatCount="indefinite"/>
  </circle>
  <circle cx="700" cy="150" r="1.5" fill="#3fe0a0" opacity="0.5">
    <animate attributeName="opacity" values="0.15;0.7;0.15" dur="5s" repeatCount="indefinite"/>
    <animateTransform attributeName="transform" type="translate" values="0,0;0,-8;0,0" dur="5s" repeatCount="indefinite"/>
  </circle>
  <circle cx="420" cy="250" r="1.5" fill="#b388ff" opacity="0.4">
    <animate attributeName="opacity" values="0.1;0.6;0.1" dur="6s" repeatCount="indefinite"/>
    <animateTransform attributeName="transform" type="translate" values="0,0;0,-8;0,0" dur="6s" repeatCount="indefinite"/>
  </circle>

  <!-- boot log -->
  <g font-family="'Courier New', monospace" font-size="13" fill="#8b85b8">
    <text x="28" y="62">[ ok ] mounting /dev/iliv007 ... done</text>
    <text x="28" y="88">[ ok ] starting fakesh ... ready</text>
    <text x="28" y="114">[ ok ] nostalgia levels ... within legal limits</text>
  </g>

  <!-- session -->
  <g font-family="'Courier New', monospace" font-size="14">
    <text x="28" y="154"><tspan fill="#3fe0a0">guest@iliv007:~$</tspan><tspan fill="#e8e6f5"> whoami</tspan></text>
    <text x="28" y="180" fill="#c9c6e8">iliya — builder of useful software</text>

    <text x="28" y="218"><tspan fill="#3fe0a0">guest@iliv007:~$</tspan><tspan fill="#e8e6f5"> whatis iliya</tspan></text>
    <text x="28" y="244" fill="#c9c6e8">bots, tools and web apps — from idea to live product.</text>

    <text x="28" y="282"><tspan fill="#3fe0a0">guest@iliv007:~$</tspan></text><rect x="196" y="270" width="9" height="16" fill="#3fe0a0"><animate attributeName="opacity" values="1;0;1" dur="1.06s" repeatCount="indefinite"/></rect>
  </g>

  <title>ILIV007 — terminal</title>
</svg>
"""

def main() -> None:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "profile.svg")
    out.write_text(SVG, encoding="utf-8")
    print(f"wrote {out} ({len(SVG)} bytes, static)")

if __name__ == "__main__":
    main()
