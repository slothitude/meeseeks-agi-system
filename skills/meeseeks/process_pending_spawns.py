#!/usr/bin/env python3
"""
Process pending retry chunks from pending-spawns.json.

Called by heartbeat to spawn queued retry chunks with rate limiting.

Usage:
    python skills/meeseeks/process_pending_spawns.py --check
    python skills/meeseeks/process_pending_spawns.py --spawn --max 3
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Paths
CRYPT_ROOT = Path(__file__).parent.parent.parent / "the-crypt"
PENDING_SPAWNS_FILE = CRYPT_ROOT / "pending-spawns.json"
MAX_SPAWNS_PER_RUN = 3
MAX_RETRIES_PER_TASK = 3


def load_pending_spawns():
    """Load pending spawns from file."""
    if not PENDING_SPAWNS_FILE.exists():
        return {"pending": []}

    with open(PENDING_SPAWNS_FILE, 'r') as f:
        return json.load(f)


def save_pending_spawns(data):
    """Save pending spawns to file."""
    with open(PENDING_SPAWNS_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def check_pending():
    """Check status of pending spawns."""
    data = load_pending_spawns()
    pending = data.get("pending", [])

    if not pending:
        print("[pending_spawns] No pending chunks")
        return 0

    print(f"[pending_spawns] {len(pending)} chunks pending:")

    for i, p in enumerate(pending[:5]):  # Show first 5
        meta = p.get("_retry_meta", {})
        retry_num = p.get("_retry_number", 0)
        chunk_idx = meta.get("chunk_index", 0)
        total = meta.get("total_chunks", 1)
        age = (datetime.now() - datetime.fromisoformat(p.get("_added_at", datetime.now().isoformat()))).total_seconds() / 60

        print(f"  [{i+1}] Chunk {chunk_idx+1}/{total} - retry #{retry_num} - age: {age:.0f}min")

    if len(pending) > 5:
        print(f"  ... and {len(pending) - 5} more")

    return len(pending)


def spawn_pending(max_spawns=MAX_SPAWNS_PER_RUN):
    """
    Spawn pending chunks with rate limiting.

    Returns count of spawned chunks.
    """
    data = load_pending_spawns()
    pending = data.get("pending", [])

    if not pending:
        print("[pending_spawns] Nothing to spawn")
        return 0

    spawned = 0
    remaining = []

    for p in pending:
        if spawned >= max_spawns:
            # Rate limit - keep remaining for next heartbeat
            remaining.append(p)
            continue

        # Check retry limit
        retry_num = p.get("_retry_number", 0)
        if retry_num >= MAX_RETRIES_PER_TASK:
            print(f"[pending_spawns] SKIP: Max retries reached for {p['_retry_meta'].get('original_session', 'unknown')[:20]}...")
            continue

        # Spawn this chunk
        # Note: Actual spawning is done by main agent via sessions_spawn
        # This script just marks them as ready
        p["_ready_to_spawn"] = True
        p["_spawned_at"] = datetime.now().isoformat()
        spawned += 1

        meta = p.get("_retry_meta", {})
        print(f"[pending_spawns] READY: Chunk {meta.get('chunk_index', 0)+1}/{meta.get('total_chunks', 1)}")

    # Save remaining back to file
    data["pending"] = remaining + [p for p in pending if not p.get("_ready_to_spawn")]
    save_pending_spawns(data)

    print(f"[pending_spawns] Spawned {spawned} chunks, {len(remaining)} remaining")
    return spawned


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Process pending retry spawns")
    parser.add_argument("--check", action="store_true", help="Check pending status")
    parser.add_argument("--spawn", action="store_true", help="Mark chunks for spawning")
    parser.add_argument("--max", type=int, default=3, help="Max spawns per run")

    args = parser.parse_args()

    if args.check:
        check_pending()
    elif args.spawn:
        spawn_pending(args.max)
    else:
        # Default: check
        check_pending()


if __name__ == "__main__":
    main()
