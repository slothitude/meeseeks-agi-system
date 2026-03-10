#!/usr/bin/env python3
"""Test Ladbrokes fetcher."""
from ladbrokes_fetcher import fetch_all_prices

# Use category T (thoroughbreds) only
runners = fetch_all_prices(categories=["T"], au_only=True)
print(f'Total runners: {len(runners)}')

if runners:
    for r in runners[:5]:
        print(f"  {r['runner_name']} @ {r['fixed_win']} ({r['meeting_name']} R{r['race_number']})")
else:
    print("  No runners found!")
