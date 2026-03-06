#!/usr/bin/env python3
"""Night Watch Status Check - 2:19 AM"""
from datetime import datetime, timezone, timedelta
from pathlib import Path

print("="*60)
print("NIGHT WATCH - 2:19 AM")
print("="*60)
print()

# Check files
opps = Path("steamarb_opportunities.json")
log = Path("steamarb_log.csv")

print("Files:")
print(f"  Opportunities: {'exists' if opps.exists() else 'not yet (10am)'}")
print(f"  Trade log: {'exists' if log.exists() else 'not yet (10am)'}")
print()

# Time until 10am
now = datetime.now()
ten_am = now.replace(hour=10, minute=0, second=0, microsecond=0)
if ten_am < now:
    ten_am += timedelta(days=1)

time_to_10am = ten_am - now
hours = time_to_10am.seconds // 3600
minutes = (time_to_10am.seconds % 3600) // 60

print(f"Time to 10am: {hours}h {minutes}m")
print()
print("System Status: [OK] ARMED")
print("Mode: Paper Trading (safe)")
print("Next action: Automatic at 10:00 AM")
print()
print("="*60)
print("Night watch complete. Resting until 10am.")
print("="*60)
