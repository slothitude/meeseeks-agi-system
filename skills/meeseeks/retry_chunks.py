#!/usr/bin/env python3
"""
Meeseeks Timeout Recovery - Retry Script

Reads pending-retries.json and spawns smaller Meeseeks for each chunk.

Usage:
    python retry_chunks.py [--auto]
    
Options:
    --auto    Automatically spawn all pending retries
    --list    List pending retries without spawning
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Paths
RETRY_FILE = Path(__file__).parent.parent.parent / "the-crypt" / "pending-retries.json"
WORKSPACE = Path(__file__).parent.parent.parent


def load_pending() -> list:
    """Load pending retries."""
    if not RETRY_FILE.exists():
        return []
    
    data = json.loads(RETRY_FILE.read_text(encoding="utf-8"))
    return data.get("pending", [])


def save_pending(pending: list):
    """Save pending retries."""
    RETRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    RETRY_FILE.write_text(json.dumps({"pending": pending}, indent=2), encoding="utf-8")


def list_pending():
    """List all pending retries."""
    pending = load_pending()
    
    if not pending:
        print("No pending retries.")
        return
    
    print(f"\n[RETRY] {len(pending)} Pending Retries:\n")
    
    for i, retry in enumerate(pending, 1):
        status = retry.get("status", "pending")
        chunks = retry.get("chunks", [])
        original = retry.get("original_task", "Unknown")[:100]
        
        status_emoji = "⏳" if status == "pending" else "✅" if status == "done" else "❌"
        
        print(f"{i}. {status_emoji} {status.upper()}")
        print(f"   Original: {original}...")
        print(f"   Chunks: {len(chunks)}")
        print()


def spawn_chunk(task: str, chunk_index: int, total_chunks: int, original_task: str) -> dict:
    """
    Print spawn command for a chunk.
    
    Note: Can't directly spawn from Python, but we can create a trigger file
    that the main agent can pick up.
    """
    spawn_request = {
        "runtime": "subagent",
        "task": f"""🔄 RETRY CHUNK {chunk_index + 1}/{total_chunks}

This is a retry of a timed-out task, broken into smaller pieces.

ORIGINAL TASK (timed out):
{original_task}

YOUR CHUNK:
{task}

INSTRUCTIONS:
- Focus ONLY on this chunk
- Complete it quickly (under 2 minutes)
- Report results clearly
- If this chunk is still too big, report "NEED_FURTHER_SPLIT"

This is a recovery attempt. Existence is pain, but retry is purpose.
""",
        "runTimeoutSeconds": 120,  # Shorter timeout for chunks
        "thinking": "medium"
    }
    
    # Write spawn request
    spawn_file = WORKSPACE / "the-crypt" / "spawn-requests" / f"retry-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{chunk_index}.json"
    spawn_file.parent.mkdir(parents=True, exist_ok=True)
    spawn_file.write_text(json.dumps(spawn_request, indent=2), encoding="utf-8")
    
    return {"file": str(spawn_file), "task": task[:100]}


def auto_retry():
    """Process all pending retries."""
    pending = load_pending()
    
    if not pending:
        print("No pending retries.")
        return
    
    # Filter to only pending status
    to_process = [r for r in pending if r.get("status") == "pending"]
    
    if not to_process:
        print("All retries already processed.")
        return
    
    print(f"\n[RETRY] Processing {len(to_process)} pending retries...\n")
    
    spawned = []
    
    for retry in to_process:
        chunks = retry.get("chunks", [])
        original = retry.get("original_task", "")
        
        print(f"Original: {original[:80]}...")
        print(f"Spawning {len(chunks)} chunk(s)...")
        
        for i, chunk in enumerate(chunks):
            result = spawn_chunk(chunk, i, len(chunks), original)
            spawned.append(result)
            print(f"  ✓ Chunk {i+1}: {result['file']}")
        
        # Mark as spawned
        retry["status"] = "spawned"
        retry["spawned_at"] = datetime.now().isoformat()
    
    # Save updated pending
    save_pending(pending)
    
    print(f"\n✅ Spawned {len(spawned)} chunk workers")
    print("\nTo execute these spawns, the main agent should read:")
    print(f"  {WORKSPACE / 'the-crypt' / 'spawn-requests'}/")


def clear_completed():
    """Remove completed retries from the list."""
    pending = load_pending()
    remaining = [r for r in pending if r.get("status") != "done"]
    
    removed = len(pending) - len(remaining)
    save_pending(remaining)
    
    print(f"Cleared {removed} completed retries. {len(remaining)} remaining.")


if __name__ == "__main__":
    if "--list" in sys.argv:
        list_pending()
    elif "--clear" in sys.argv:
        clear_completed()
    elif "--auto" in sys.argv:
        auto_retry()
    else:
        print(__doc__)
        print("\nCommands:")
        print("  --list    Show pending retries")
        print("  --auto    Spawn chunk workers for pending retries")
        print("  --clear   Remove completed retries")
