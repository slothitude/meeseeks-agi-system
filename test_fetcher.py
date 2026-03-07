#!/usr/bin/env python3
"""Test Ladbrokes fetcher."""
from ladbrokes_fetcher import fetch_all_prices

runners = fetch_all_prices()
print(f'Total runners: {len(runners)}')

if runners:
    for r in runners[:5]:
        print(f"  {r['runner_name']} @ {r['fixed_win']}")
else:
    print("  No runners found!")
