#!/usr/bin/env python3
"""
Spawn With Learning - Automatic learning capture wrapper.

This provides a drop-in replacement for sessions_spawn that automatically
entombs every run to the Crypt for ancestral learning.

USAGE IN OPENCLAW:

Instead of calling sessions_spawn directly, use this pattern:

```javascript
// In your agent code, after spawning:
const result = await sessions_spawn({
    runtime: 'subagent',
    task: task,
    ...
});

// The result comes back automatically when the subagent completes.
// To enable auto-entombment, we hook into the completion callback.
```

Since we can't directly wrap the tool call, we provide:

1. A post-run function to call when results come back
2. A tracking file for pending Meeseeks
3. Automatic entombment on completion

See LEARNING_HOOK.md for the full integration pattern.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from auto_entomb import auto_entomb, log_run, get_run_stats

# Pending Meeseeks tracking
PENDING_FILE = Path(__file__).parent.parent.parent / "the-crypt" / "pending_meeseeks.json"


def track_spawn(session_key: str, task: str, meeseeks_type: str = "standard", metadata: Dict = None):
    """
    Track a newly spawned Meeseeks for later entombment.
    
    Call this RIGHT AFTER sessions_spawn returns.
    
    Args:
        session_key: The childSessionKey from spawn result
        task: The task that was spawned
        meeseeks_type: Type of Meeseeks (coder, searcher, etc.)
        metadata: Additional metadata to track
    """
    pending = _load_pending()
    
    pending[session_key] = {
        "task": task,
        "meeseeks_type": meeseeks_type,
        "spawned_at": datetime.now().isoformat(),
        "metadata": metadata or {}
    }
    
    _save_pending(pending)


def complete_and_entomb(session_key: str, result: Dict[str, Any]) -> Optional[str]:
    """
    Complete a tracked Meeseeks and auto-entomb.
    
    Call this when the subagent completion message arrives.
    
    Args:
        session_key: The session key of the completed Meeseeks
        result: The result dict (success, output, error, etc.)
        
    Returns:
        Path to entombment file, or None if not tracked
    """
    pending = _load_pending()
    
    if session_key not in pending:
        # Not tracked - still entomb with defaults
        return auto_entomb(
            session_key=session_key,
            task="Unknown (not tracked)",
            result=result,
            meeseeks_type="standard"
        )
    
    # Get tracked info
    tracked = pending.pop(session_key)
    _save_pending(pending)
    
    # Auto-entomb with tracked info
    return auto_entomb(
        session_key=session_key,
        task=tracked["task"],
        result=result,
        meeseeks_type=tracked.get("meeseeks_type", "standard")
    )


def _load_pending() -> Dict[str, Any]:
    """Load pending Meeseeks tracking."""
    if PENDING_FILE.exists():
        try:
            return json.loads(PENDING_FILE.read_text(encoding="utf-8"))
        except:
            return {}
    return {}


def _save_pending(pending: Dict[str, Any]):
    """Save pending Meeseeks tracking."""
    PENDING_FILE.parent.mkdir(parents=True, exist_ok=True)
    PENDING_FILE.write_text(json.dumps(pending, indent=2), encoding="utf-8")


def get_pending_count() -> int:
    """Get number of pending Meeseeks."""
    return len(_load_pending())


def get_pending_tasks() -> list:
    """Get list of pending tasks with info."""
    pending = _load_pending()
    return [
        {
            "session_key": k,
            "task": v["task"][:100],
            "type": v.get("meeseeks_type", "standard"),
            "spawned_at": v.get("spawned_at", "unknown")
        }
        for k, v in pending.items()
    ]


# CLI interface for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Spawn with learning CLI")
    parser.add_argument("command", choices=["stats", "pending", "test"])
    parser.add_argument("--session-key", help="Session key for test")
    
    args = parser.parse_args()
    
    if args.command == "stats":
        stats = get_run_stats()
        print(f"Total runs: {stats['total']}")
        print(f"Success: {stats['success']}")
        print(f"Failed: {stats['failed']}")
        print(f"Success rate: {stats['success_rate']}")
        print(f"Avg duration: {stats['avg_duration_ms']:.0f}ms")
    
    elif args.command == "pending":
        pending = get_pending_tasks()
        if not pending:
            print("No pending Meeseeks")
        else:
            for p in pending:
                print(f"- {p['session_key']}: {p['task']}")
    
    elif args.command == "test":
        # Test the flow
        test_key = args.session_key or "test-key-123"
        
        print(f"1. Tracking spawn: {test_key}")
        track_spawn(test_key, "Test task", "coder")
        
        print(f"2. Pending: {get_pending_count()}")
        
        print(f"3. Completing and entombing...")
        result = {"success": True, "output": "Test completed"}
        path = complete_and_entomb(test_key, result)
        
        print(f"4. Entombed at: {path}")
        print(f"5. Pending now: {get_pending_count()}")
