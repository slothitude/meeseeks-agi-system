#!/usr/bin/env python3
"""
ARB Reality Check
=================

Why are all edges negative?

The Pattern:
- Ladbrokes: 7.00
- Betfair LAY: 9.00
- Edge: -22%

This means Ladbrokes is OFFERING 7.00
But to lay at Betfair, someone must BACK at 9.00

The Insight:
- Bookies offer WORSE odds than exchanges (their margin)
- For ARB to work: Bookie > Exchange
- This rarely happens because bookies adjust quickly

The Reality:
- True ARBs appear when:
  1. Bookie is slow to adjust
  2. Exchange has laid the favorite heavily
  3. Error in bookie pricing

Current State:
- All edges negative = bookies are correctly priced
- No slow adjustments
- No errors

What This Means:
- System is working correctly
- Just waiting for bookie mistake
- Could be hours or days between opportunities

Options:
1. Wait patiently (100% win rate when they appear)
2. Lower threshold to 0% (break-even trades for practice)
3. Add more bookies (Neds, TAB, Sportsbet)
4. Switch to NEAR-ARB (small negative edge for volume)

The Lesson:
ARB is not constant action. It's patience punctuated by opportunity.
"""

# Quick stats from today
stats = {
    "races_scanned": 8,
    "runners_checked": 80,
    "positive_edges": 0,
    "best_edge": -7.14,  # Ninja at Randwick
    "worst_edge": -72.0,  # Eraantyva at Corowa
    "average_edge": -25.0,
}

print("Today's ARB Stats:")
print(f"  Races: {stats['races_scanned']}")
print(f"  Runners: {stats['runners_checked']}")
print(f"  Positive edges: {stats['positive_edges']}")
print(f"  Best edge: {stats['best_edge']:.2f}%")
print(f"  Average edge: {stats['average_edge']:.2f}%")
print("\nConclusion: Bookies are correctly priced. Waiting for mistakes.")
