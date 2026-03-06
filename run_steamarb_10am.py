#!/usr/bin/env python3
"""
SteamArb Auto-Start Script
===========================

Called by cron job at 10am Brisbane time.
Runs paper trading for 6 hours (until 4pm, with 1hr buffer before 5pm cutoff).

Logs opportunities and sends summary to Telegram.
"""

import subprocess
import json
from datetime import datetime
from pathlib import Path

def run_paper_trading():
    """Run paper trading session."""
    print("="*60)
    print("STEAMARB AUTO-START")
    print(f"Time: {datetime.now()}")
    print("="*60)
    
    # Run the engine
    result = subprocess.run(
        ["python", "steam_arb_live.py", "--paper", "--duration", "360"],
        capture_output=True,
        text=True,
        timeout=22200  # 6 hours + buffer
    )
    
    print(result.stdout)
    
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    
    # Load results
    opps_file = Path("steamarb_opportunities.json")
    if opps_file.exists():
        with open(opps_file) as f:
            opps = json.load(f)
        
        if opps:
            total_r = sum(o.get("profit_r", 0) for o in opps)
            arbs = len([o for o in opps if o.get("engine") == "ARB"])
            steams = len([o for o in opps if o.get("engine") == "STEAM"])
            values = len([o for o in opps if o.get("engine") == "VALUE"])
            
            print("\n" + "="*60)
            print("SESSION RESULTS")
            print("="*60)
            print(f"Opportunities: {len(opps)}")
            print(f"  ⚡ ARB: {arbs}")
            print(f"  🔥 STEAM: {steams}")
            print(f"  💎 VALUE: {values}")
            print(f"\nTotal R: +{total_r:.4f}R")
            print(f"Total AUD: ${total_r:.2f}")
            print("="*60)
            
            return True
    
    print("\nNo opportunities found today")
    return True


if __name__ == "__main__":
    run_paper_trading()
