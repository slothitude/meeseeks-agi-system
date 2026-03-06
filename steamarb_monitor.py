#!/usr/bin/env python3
"""
SteamArb Live Monitor
=====================

Quick status check during trading hours.
Shows current opportunities, R profit, and market status.

Usage:
    python steamarb_monitor.py
"""

import json
from pathlib import Path
from datetime import datetime

OPPS_FILE = Path("steamarb_opportunities.json")
LOG_FILE = Path("steamarb_log.csv")


def show_status():
    """Show current trading status."""
    print("="*60)
    print("STEAMARB STATUS")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    print()

    # Check opportunities
    if OPPS_FILE.exists():
        with open(OPPS_FILE) as f:
            opps = json.load(f)

        if opps:
            total_r = sum(o.get("profit_r", 0) for o in opps)
            arbs = [o for o in opps if o.get("engine") == "ARB"]
            steams = [o for o in opps if o.get("engine") == "STEAM"]
            values = [o for o in opps if o.get("engine") == "VALUE"]

            print(f"📊 OPPORTUNITIES: {len(opps)}")
            print(f"  ⚡ ARB: {len(arbs)}")
            print(f"  🔥 STEAM: {len(steams)}")
            print(f"  💎 VALUE: {len(values)}")
            print()
            print(f"💰 TOTAL R: +{total_r:.4f}R")
            print(f"💰 TOTAL AUD: ${total_r:.2f}")
            print()

            # Show last 5
            print("LATEST 5:")
            for o in opps[:5]:
                symbol = {"ARB": "⚡", "STEAM": "🔥", "VALUE": "💎"}.get(o.get("engine"), "•")
                print(f"  {symbol} {o.get('runner_name', '?')[:20]:20s} | +{o.get('profit_r', 0):.4f}R | {o.get('timestamp', '?')[:16]}")
        else:
            print("📭 No opportunities yet")
    else:
        print("📭 No data file yet (markets not open)")

    print()
    print("="*60)

    # Check log
    if LOG_FILE.exists():
        with open(LOG_FILE) as f:
            lines = f.readlines()
        print(f"📝 Log entries: {len(lines) - 1}")  # Minus header
    else:
        print("📝 Log: Not created yet")

    print("="*60)


if __name__ == "__main__":
    show_status()
