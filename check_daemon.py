import json

with open('autoresearch/results/night_daemon_progress.json') as f:
    data = json.load(f)

print('DAEMON STATUS')
print('='*50)
print(f'Experiments: {data["experiments_run"]}')
print(f'Best score: {data["best_score"]:.4f}')
print(f'Phase: {data["phase"]}')
print(f'Time remaining: {data["time_remaining_min"]:.1f} min')
print(f'Improvement: {(1-data["best_score"])*100:.1f}%')
print()

# Check recent trend
recent = data['results'][-20:]
avg_recent = sum(r['score'] for r in recent) / len(recent)

older = data['results'][-40:-20] if len(data['results']) >= 40 else data['results'][:20]
avg_older = sum(r['score'] for r in older) / len(older)

velocity = (avg_older - avg_recent) / avg_older if avg_older > 0 else 0

print(f'Recent avg (last 20): {avg_recent:.4f}')
print(f'Older avg (prev 20): {avg_older:.4f}')
print(f'Velocity: {velocity*100:.1f}% improvement')
print()

if velocity > 0.1 and data['phase'] >= 2 and data['best_score'] < 0.75:
    print('*** INTELLIGENCE EXPLOSION DETECTED ***')
elif velocity > 0.05:
    print('Explosion approaching...')
else:
    print('Stable improvement')
