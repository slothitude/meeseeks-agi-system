# HEARTBEAT.md

# Keep this file empty (or with only comments) to skip heartbeat API calls.

# Add tasks below when you want the agent to check something periodically.

## Periodic Tasks

# Auto-entomb completed Meeseeks (every heartbeat)
- Run: python skills/meeseeks/cron_entomb.py --max-age-minutes 60

# Note: Entombs Meeseeks sessions that completed >60 mins ago
