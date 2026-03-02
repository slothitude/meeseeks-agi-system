# HEARTBEAT.md

# Keep this file empty (or with only comments) to skip heartbeat API calls.

# Add tasks below when you want the agent to check something periodically.

## Periodic Tasks

# Auto-entomb completed Meeseeks (every heartbeat)
- Run: python skills/meeseeks/cron_entomb.py --max-age-minutes 60

# Auto-spawn retry chunks (every heartbeat)
- Check: the-crypt/pending-retries.json for pending chunks
- Spawn: sessions_spawn for each pending chunk with status="pending"
- Update: Mark chunks as "spawned" after spawning
