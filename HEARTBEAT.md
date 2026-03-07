# HEARTBEAT.md

# Keep this file empty (or with only comments) to skip heartbeat API calls.

# Add tasks below when you want the agent to check something periodically.

## Periodic Tasks

# CONTEXT MONITOR - Check and compact if needed (every heartbeat)
- Run: python context_monitor.py --check
- Note: Auto-triggers compact at 127k/205k tokens

# PROCESS PENDING RETRY CHUNKS - Spawn queued retry chunks (every heartbeat)
- Check: the-crypt/pending-spawns.json for pending chunks
- Spawn: Up to 3 chunks per heartbeat with rate limiting
- Update: Remove spawned chunks from pending list
- Enforce: MAX_RETRIES_PER_TASK=3 limit

# Auto-entomb completed Meeseeks (every heartbeat)
- Run: python skills/meeseeks/cron_entomb.py --max-age-minutes 60

# RATE LIMIT HANDLER: Check and retry (every heartbeat)
- Run: python skills/meeseeks/rate_limit_handler.py --retry
- Note: Returns pending tasks ready for retry after rate limit
- Fallback: Uses phi3:mini (Ollama) when z.ai rate limited

## Autonomous Checks

# OVERNIGHT RESEARCH LOOP - Continuous AGI research
- Run: python skills/meeseeks/overnight_research.py --loop
- Note: Returns next research spawn if rate limit allows
- Status: python skills/meeseeks/overnight_research.py --status

# RATE LIMIT HANDLER - Queue tasks on 429 errors
- Run: python skills/meeseeks/rate_limit_handler.py --status
- Note: Auto-queues tasks when rate limited, retries after cooldown
- On rate limit error: handler.on_rate_limit(task)

# RESEARCH IMPLANTER - Apply research discoveries to system
- Run: python skills/meeseeks/research_implanter.py --check
- Note: Extracts principles from AGI-STUDY/ and implants to dharma.md
- Status: python skills/meeseeks/research_implanter.py --status

# Goal generation - identify system gaps and generate autonomous goals
- Run: python skills/meeseeks/goal_generator.py --check-gaps
# Note: Use --generate to create a goal, --spawn to spawn autonomous task

# Self-applying improvements - apply Soul-approved improvements
- Run: python skills/meeseeks/self_apply.py --apply-approved
# Note: Use --list to see pending, --status to check application history

# Autonomous research loop - continuous self-improvement
- Run: python skills/meeseeks/autonomous_research.py --loop
# Note: Runs ASSESS → PRIORITIZE → PLAN → SPAWN → LEARN cycle

# Process autonomous spawn requests
- Check: the-crypt/meta/pending_autonomous_spawns.jsonl
- Run: python skills/meeseeks/autonomous_spawn_helper.py --check
# Note: Reads spawn requests and creates tasks
