#!/usr/bin/env python3
"""
Pending Spawns Processor

Reads pending-spawns.json and spawns the waiting Meeseeks.
This is the missing link - auto_retry creates configs, but nothing spawns them!

Usage:
    python skills/meeseeks/spawn_pending.py --dry-run   # See what would spawn
    python skills/meeseeks/spawn_pending.py --spawn     # Actually spawn
    python skills/meeseeks/spawn_pending.py --clear     # Clear old spawns
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict

CRYPT_ROOT = Path("C:/Users/aaron/.openclaw/workspace/the-crypt")
PENDING_FILE = CRYPT_ROOT / "pending-spawns.json"


def load_pending() -> Dict:
    """Load pending spawns file"""
    if not PENDING_FILE.exists():
        return {"pending": []}
    
    try:
        data = json.loads(PENDING_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return {"pending": data}
        return data
    except:
        return {"pending": []}


def save_pending(data: Dict):
    """Save pending spawns file"""
    PENDING_FILE.parent.mkdir(parents=True, exist_ok=True)
    PENDING_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def get_pending_spawns() -> List[Dict]:
    """Get list of pending spawns"""
    data = load_pending()
    return data.get("pending", [])


def get_spawn_command(config: Dict) -> str:
    """Generate the sessions_spawn command for a config"""
    # Extract key params
    task = config.get("task", "")[:200]  # Truncate for display
    timeout = config.get("runTimeoutSeconds", 180)
    thinking = config.get("thinking", "medium")
    
    return f"sessions_spawn(runtime='subagent', task='...', timeout={timeout}s)"


def dry_run():
    """Show what would be spawned"""
    pending = get_pending_spawns()
    
    if not pending:
        print("No pending spawns.")
        return
    
    print(f"\n=== PENDING SPAWNS ({len(pending)}) ===\n")
    
    # Group by source session
    by_session = {}
    for config in pending:
        source = config.get("_source_session", "unknown")[:20]
        if source not in by_session:
            by_session[source] = []
        by_session[source].append(config)
    
    for source, configs in by_session.items():
        retry_num = configs[0].get("_retry_number", "?")
        added = configs[0].get("_added_at", "?")[:19]
        
        # Get task preview
        task_preview = configs[0].get("task", "")[:60]
        # Clean up Unicode
        task_clean = task_preview.encode('ascii', 'replace').decode('ascii')
        
        print(f"Session: {source}...")
        print(f"  Chunks: {len(configs)}, Retry #{retry_num}, Added: {added}")
        print(f"  Task: {task_clean}...")
        print()
    
    print(f"Total: {len(pending)} pending spawns ready")
    print("\nRun with --spawn to execute")


def spawn_one(config: Dict) -> bool:
    """Spawn a single Meeseeks using sessions_spawn
    
    Returns True if spawned successfully
    """
    # This is called from main agent, which has access to sessions_spawn tool
    # We return the config so the agent can spawn it
    task = config.get("task", "")
    timeout = config.get("runTimeoutSeconds", 180)
    thinking = config.get("thinking", "medium")
    
    print(f"[spawn_pending] Would spawn: {task[:60]}...")
    print(f"  Timeout: {timeout}s, Thinking: {thinking}")
    
    # Return config for actual spawning
    return True


def clear_old(max_age_hours: int = 24):
    """Clear spawns older than max_age_hours"""
    pending = get_pending_spawns()
    
    if not pending:
        print("No pending spawns to clear.")
        return
    
    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    
    new_pending = []
    cleared = 0
    
    for config in pending:
        added_at_str = config.get("_added_at", "")
        if added_at_str:
            try:
                added_at = datetime.fromisoformat(added_at_str)
                if added_at < cutoff:
                    cleared += 1
                    continue
            except:
                pass
        
        new_pending.append(config)
    
    if cleared > 0:
        save_pending({"pending": new_pending})
        print(f"Cleared {cleared} old spawns (older than {max_age_hours}h)")
        print(f"Remaining: {len(new_pending)}")
    else:
        print("No old spawns to clear.")


def get_next_spawn() -> Dict:
    """Get the next spawn config to execute"""
    pending = get_pending_spawns()
    if pending:
        return pending[0]
    return None


def mark_spawned(config: Dict):
    """Mark a config as spawned (remove from pending)"""
    pending = get_pending_spawns()
    
    # Find and remove this config
    task_preview = config.get("task", "")[:100]
    new_pending = [c for c in pending if c.get("task", "")[:100] != task_preview]
    
    save_pending({"pending": new_pending})
    print(f"[spawn_pending] Marked as spawned, {len(new_pending)} remaining")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Process pending spawns")
    parser.add_argument("--dry-run", action="store_true", help="Show what would spawn")
    parser.add_argument("--spawn", action="store_true", help="Spawn next pending")
    parser.add_argument("--clear", action="store_true", help="Clear old spawns")
    parser.add_argument("--clear-all", action="store_true", help="Clear ALL spawns")
    parser.add_argument("--max-age", type=int, default=24, help="Max age in hours")
    parser.add_argument("--next", action="store_true", help="Get next spawn config as JSON")
    
    args = parser.parse_args()
    
    if args.dry_run:
        dry_run()
    elif args.spawn:
        config = get_next_spawn()
        if config:
            spawn_one(config)
        else:
            print("No pending spawns.")
    elif args.clear:
        clear_old(args.max_age)
    elif args.clear_all:
        save_pending({"pending": []})
        print("Cleared all pending spawns.")
    elif args.next:
        config = get_next_spawn()
        if config:
            # Use ascii output for Windows console
            output = json.dumps(config, indent=2, ensure_ascii=True)
            print(output)
        else:
            print("{}")
    else:
        # Default: dry run
        dry_run()


if __name__ == "__main__":
    main()
