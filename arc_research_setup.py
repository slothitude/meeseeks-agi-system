import sys
sys.path.insert(0, "C:/Users/aaron/.openclaw/workspace")

import asyncio
from skills.meeseeks.helpers.communication import SharedState

async def setup():
    shared = SharedState("arc-agi-2-research", "arc_researcher")
    await shared.register("ARC-AGI-2 researcher")
    return shared

shared = asyncio.run(setup())
print("[OK] Connected to shared state")
print(f"Workflow: {shared.workflow_id}")
print(f"Worker: {shared.worker_id}")
