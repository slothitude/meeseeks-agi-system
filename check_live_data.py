import csv
from collections import defaultdict
from pathlib import Path

csv_file = Path('race_prices_clean.csv')
if not csv_file.exists():
    print('No data')
    exit(0)

with open(csv_file) as f:
    reader = csv.DictReader(f)
    data = list(reader)

print(f'Total observations: {len(data)}')
print()

# Group by race
races = defaultdict(list)
for row in data:
    key = row['track'] + '_R' + row['race']
    races[key].append(row)

for race_key, rows in sorted(races.items()):
    print(f'{race_key}:')
    print(f'  Observations: {len(rows)}')
    
    # Show price movements
    runners = defaultdict(list)
    for r in rows:
        runners[r['runner']].append({
            'open': float(r['open']),
            'current': float(r['win']),
            'change': float(r['change_pct'])
        })
    
    print('  Top 4:')
    for runner_name in list(runners.keys())[:4]:
        prices = runners[runner_name]
        first = prices[0]
        last = prices[-1]
        
        open_p = first['open']
        current = last['current']
        change = ((current - open_p) / open_p * 100) if open_p > 0 else 0
        
        edge = 'STEAM' if change < -5 else ('DRIFT' if change > 5 else '')
        edge_str = f' [{edge}]' if edge else ''
        
        print(f'    {runner_name}: ${open_p:.2f} -> ${current:.2f} ({change:+.1f}%){edge_str}')
    
    print()
