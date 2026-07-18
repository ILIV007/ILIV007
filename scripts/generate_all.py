#!/usr/bin/env python3
"""
Master script: generate all GPOS SVG assets locally.

Usage:
  python scripts/generate_all.py
"""

import sys
import os
import subprocess

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPTS_DIR)


def run(cmd: list[str]) -> None:
    print(f"\n▶ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=REPO_ROOT)
    if result.returncode != 0:
        print(f"❌ Command failed: {' '.join(cmd)}")
        sys.exit(result.returncode)


def main():
    print("🚀 GPOS — GitHub Profile Operating System")
    print("   Generating all SVG assets...\n")

    # 1. Boot Sequence
    run(["python", "scripts/make_boot_sequence.py"])

    # 2. Mission Card
    run(["python", "scripts/make_mission_card.py"])

    # 3. System Status
    run(["python", "scripts/make_system_status.py"])

    # 4. Network Flow
    run(["python", "scripts/make_network_flow.py"])

    # 5. System Log
    run(["python", "scripts/make_system_log.py"])

    # 6. Fetch contributions + PCB heatmap
    run(["python", "scripts/fetch_contributions.py"])
    run(["python", "scripts/render_heatmap_svg.py"])

    print("\n✅ All GPOS assets generated!")
    print("   Files: boot-sequence.svg, mission-card.svg, system-status.svg,")
    print("          network-flow.svg, system-log.svg, contrib-heatmap.svg")


if __name__ == "__main__":
    main()
