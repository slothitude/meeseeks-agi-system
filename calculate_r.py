#!/usr/bin/env python3
"""
R Calculator - Van Tharp Principles
Calculates R-multiples for detected edges
"""

import csv
from collections import defaultdict
from pathlib import Path

csv_file = Path('race_prices_clean.csv')

with open(csv_file) as f:
    reader = csv.DictReader(f)
    data = list(reader)

print("="*60)
print("R CALCULATOR - VAN THARP PRINCIPLES")
print(f"Observations: {len(data)}")
print("="*60)
print()

# Group by race
races = defaultdict(list)
for row in data:
    key = row['track'] + '_R' + row['race']
    races[key].append(row)

for race_key, rows in sorted(races.items()):
    print(f"{race_key}:")
    
    # Get runner price movements
    runners = defaultdict(list)
    for r in rows:
        runners[r['runner']].append({
            'open': float(r['open']),
            'current': float(r['win']),
            'change': float(r['change_pct'])
        })
    
    edges = []
    
    for runner_name, prices in runners.items():
        if not prices:
            continue
        
        open_p = prices[0]['open']
        current = prices[-1]['current']
        change = prices[-1]['change']
        
        # Skip if no open price
        if open_p <= 0:
            continue
        
        # STEAM edge (price dropped > 5%)
        if change < -5:
            # Back at open, exit at current
            # R = (exit - stake) / stake = (current - open) / open (negative means profit)
            r_multiple = -change / 100  # Simplified R calculation
            
            edges.append({
                'type': 'STEAM',
                'runner': runner_name,
                'open': open_p,
                'current': current,
                'change': change,
                'r': r_multiple
            })
        
        # DRIFT edge (price rose > 5%)
        elif change > 5:
            # Lay at open, back at current
            # R = (open - current) / (open - 1) for lay bet
            r_multiple = change / 100  # Simplified
            
            edges.append({
                'type': 'DRIFT',
                'runner': runner_name,
                'open': open_p,
                'current': current,
                'change': change,
                'r': r_multiple
            })
    
    if edges:
        print(f"  Edges: {len(edges)}")
        total_r = 0
        
        for e in edges:
            print(f"    [{e['type']}] {e['runner']}")
            print(f"      ${e['open']:.2f} -> ${e['current']:.2f} ({e['change']:+.1f}%)")
            print(f"      R potential: +{e['r']:.3f}R")
            total_r += e['r']
        
        print(f"  RACE TOTAL: +{total_r:.3f}R")
    else:
        print(f"  No edges detected")
    
    print()

print("="*60)
