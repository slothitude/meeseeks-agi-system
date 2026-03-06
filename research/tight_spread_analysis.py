#!/usr/bin/env python3
"""
Tight Spread Analysis - Betfair Overnight

Discovered during 1:19 AM scan:
- Shes An Artist: Back 2.18, Lay 2.22, Spread 0.04
- Medicinal: Back 2.76, Lay 3.00, Spread 0.24
- Travolta: Back 6.60, Lay 8.60, Spread 1.00
- Martist: Back 1.95, Lay 3.20, Spread 1.25

These are TIGHT spreads (1 tick or less) in overnight markets.
Most markets have 500-1000 tick spreads.

Question: Why do these markets have liquidity?

Hypothesis: These could be early markets for tomorrow that already have money coming in.

Time check needed:
- 11:25, 11:30, 11:45, 11:49, 11:53... all morning times
- Shes An Artist at 11:45 (18 min from now)
- Medicinal at 11:49 (4 min from now)

This is very interesting - professional steam scalpers often work 
the tightest spreads. But liquidity is entering early.

SteamArb Opportunity:
If we can detect a price drop on Ladbrokes but back Betfair to lay for the profit.

But's possible these are gold mines even overnight.
"""

import json
from datetime import datetime

# Load scan data
with open("steamarb_opportunities.json") as f:
    try:
        opps = json.load(f)
    except:
        opps = []

# Analysis
print("="*60)
print("TIGHT SPREAD ANALYSIS")
print("="*60)
print(f"Timestamp: {datetime.now()}")
print()

if opps:
    print("No opportunities logged yet")
else:
    print(f"Logged opportunities: {len(opps)}")
    for opp in opps:
        print(f"  {opp['engine']}: {opp['runner_name']}")
        print(f"    Spread: {opp['betfair_lay'] - opp['betfair_back']:.2f}")
        print(f"    Profit: +{opp['profit_r']:.4f}R")
else:
    print("\nNo tight spreads found in logged opportunities")
    print("Most spreads are 500-1000 ticks (overnight liquidity)")
    print("But some markets DO have tight spreads")
    print("This suggests early professional action")
