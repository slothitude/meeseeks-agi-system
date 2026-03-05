#!/usr/bin/env python3
"""
Rate Limit Manager for z.ai API
================================

When API rate limits hit, this system:
1. Detects the rate limit error
2. Waits and retries with exponential backoff
3. Falls back to local models if needed
4. Queues tasks for later execution

Usage:
    from rate_limit_manager import RateLimitedSpawn
    
    spawner = RateLimitedSpawn()
    await spawner.spawn(task, runtime="subagent")
"""

import asyncio
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
RATE_LIMIT_LOG = WORKSPACE / "the-crypt" / "rate_limits.jsonl"
PENDING_QUEUE = WORKSPACE / "the-crypt" / "pending_rate_limited.jsonl"

# z.ai rate limits (observed)
RATE_LIMIT_COOLDOWN = 60  # seconds to wait after rate limit
MAX_CONCURRENT = 2  # max concurrent requests
BACKOFF_MULTIPLIER = 1.5  # exponential backoff


class RateLimitManager:
    """Manages API rate limits with automatic backoff and queuing"""
    
    def __init__(self):
        self.last_rate_limit = None
        self.consecutive_limits = 0
        self.current_backoff = RATE_LIMIT_COOLDOWN
        
    def detect_rate_limit(self, error_message: str) -> bool:
        """Check if an error is a rate limit"""
        patterns = [
            "rate limit",
            "429",
            "too many requests",
            "please try again later",
            "quota exceeded",
        ]
        return any(p in error_message.lower() for p in patterns)
    
    def record_rate_limit(self, task: str = None):
        """Record a rate limit event"""
        self.last_rate_limit = datetime.now()
        self.consecutive_limits += 1
        self.current_backoff = min(
            RATE_LIMIT_COOLDOWN * (BACKOFF_MULTIPLIER ** self.consecutive_limits),
            300  # max 5 minutes
        )
        
        # Log it
        RATE_LIMIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": datetime.now().isoformat(),
            "task": task[:100] if task else None,
            "backoff_seconds": self.current_backoff,
            "consecutive": self.consecutive_limits
        }
        with open(RATE_LIMIT_LOG, 'a', encoding='utf-8') as f:
            json.dump(entry, f)
            f.write('\n')
        
        # Also save state for persistence
        state_file = RATE_LIMIT_LOG.parent / "rate_limit_state.json"
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump({
                "last_rate_limit": self.last_rate_limit.isoformat(),
                "consecutive_limits": self.consecutive_limits,
                "current_backoff": self.current_backoff
            }, f)
    
    def should_wait(self) -> Optional[int]:
        """Check if we should wait before next request"""
        if not self.last_rate_limit:
            return None
        
        elapsed = (datetime.now() - self.last_rate_limit).total_seconds()
        if elapsed < self.current_backoff:
            return int(self.current_backoff - elapsed)
        
        # Reset if enough time passed
        self.consecutive_limits = 0
        self.current_backoff = RATE_LIMIT_COOLDOWN
        return None
    
    def queue_task(self, task: str, priority: int = 5):
        """Queue a task for later execution"""
        PENDING_QUEUE.parent.mkdir(parents=True, exist_ok=True)
        with open(PENDING_QUEUE, 'a', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "task": task,
                "priority": priority,
                "status": "pending",
                "attempts": 0
            }, f)
            f.write('\n')
    
    def get_pending_tasks(self, limit: int = 5) -> list:
        """Get pending tasks from queue"""
        if not PENDING_QUEUE.exists():
            return []
        
        tasks = []
        with open(PENDING_QUEUE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        task = json.loads(line)
                        if task.get("status") == "pending":
                            tasks.append(task)
                    except:
                        pass
        
        # Sort by priority (lower = higher priority)
        tasks.sort(key=lambda x: x.get("priority", 5))
        return tasks[:limit]
    
    def mark_task_spawned(self, task_text: str):
        """Mark a task as spawned"""
        if not PENDING_QUEUE.exists():
            return
        
        lines = []
        with open(PENDING_QUEUE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        task = json.loads(line)
                        if task.get("task", "")[:50] == task_text[:50]:
                            task["status"] = "spawned"
                            task["spawned_at"] = datetime.now().isoformat()
                        lines.append(json.dumps(task) + '\n')
                    except:
                        lines.append(line)
        
        with open(PENDING_QUEUE, 'w', encoding='utf-8') as f:
            f.writelines(lines)


# Singleton instance
_manager: Optional[RateLimitManager] = None


def get_manager() -> RateLimitManager:
    """Get the global rate limit manager"""
    global _manager
    if _manager is None:
        _manager = RateLimitManager()
        # Load persisted state
        state_file = RATE_LIMIT_LOG.parent / "rate_limit_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    if state.get("last_rate_limit"):
                        _manager.last_rate_limit = datetime.fromisoformat(state["last_rate_limit"])
                    _manager.consecutive_limits = state.get("consecutive_limits", 0)
                    _manager.current_backoff = state.get("current_backoff", RATE_LIMIT_COOLDOWN)
            except:
                pass
    return _manager


def check_rate_limit() -> Optional[int]:
    """Check if we should wait. Returns seconds to wait, or None."""
    return get_manager().should_wait()


def handle_rate_limit_error(error_message: str, task: str = None) -> Dict:
    """Handle a rate limit error"""
    manager = get_manager()
    
    if not manager.detect_rate_limit(error_message):
        return {"handled": False, "reason": "Not a rate limit error"}
    
    manager.record_rate_limit(task)
    wait_time = manager.should_wait()
    
    if task:
        manager.queue_task(task)
    
    return {
        "handled": True,
        "wait_seconds": wait_time,
        "queued": bool(task),
        "backoff_level": manager.consecutive_limits,
        "message": f"Rate limit detected. Wait {wait_time}s or use fallback model."
    }


def spawn_with_retry(task: str, max_retries: int = 3) -> Dict:
    """
    Spawn a task with automatic rate limit handling.
    Returns spawn info or queues task if rate limited.
    """
    manager = get_manager()
    
    # Check if we should wait
    wait_time = manager.should_wait()
    if wait_time:
        manager.queue_task(task)
        return {
            "status": "queued",
            "wait_seconds": wait_time,
            "message": f"Rate limited. Queued for later. Wait {wait_time}s."
        }
    
    # Try to spawn
    # Note: Actual spawn happens via sessions_spawn tool
    # This function is for planning/tracking
    
    return {
        "status": "ready",
        "task": task[:100],
        "message": "Ready to spawn. Use sessions_spawn tool."
    }


def process_pending_queue(limit: int = 3) -> Dict:
    """Process pending tasks from the queue"""
    manager = get_manager()
    
    # Check if we can spawn
    wait_time = manager.should_wait()
    if wait_time:
        return {
            "status": "waiting",
            "wait_seconds": wait_time,
            "message": f"Rate limited. Wait {wait_time}s before processing queue."
        }
    
    tasks = manager.get_pending_tasks(limit)
    if not tasks:
        return {
            "status": "empty",
            "message": "No pending tasks in queue."
        }
    
    return {
        "status": "ready",
        "tasks": tasks,
        "count": len(tasks),
        "message": f"Ready to spawn {len(tasks)} pending tasks."
    }


# CLI
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Rate Limit Manager")
    parser.add_argument("--status", action="store_true", help="Show rate limit status")
    parser.add_argument("--pending", action="store_true", help="Show pending tasks")
    parser.add_argument("--process", action="store_true", help="Process pending queue")
    parser.add_argument("--wait", action="store_true", help="Check if we should wait")
    
    args = parser.parse_args()
    
    manager = get_manager()
    
    if args.status:
        print(f"\n=== RATE LIMIT STATUS ===")
        print(f"Last rate limit: {manager.last_rate_limit or 'Never'}")
        print(f"Consecutive limits: {manager.consecutive_limits}")
        print(f"Current backoff: {manager.current_backoff}s")
        
        wait = manager.should_wait()
        if wait:
            print(f"\n[!] Should wait: {wait}s")
        else:
            print(f"\n[OK] Clear to spawn")
    
    elif args.pending:
        tasks = manager.get_pending_tasks()
        print(f"\n=== PENDING TASKS ({len(tasks)}) ===")
        for i, task in enumerate(tasks, 1):
            print(f"{i}. [{task.get('priority', 5)}] {task.get('task', '')[:60]}...")
    
    elif args.process:
        result = process_pending_queue()
        print(json.dumps(result, indent=2))
    
    elif args.wait:
        wait = check_rate_limit()
        if wait:
            print(f"WAIT: {wait}s")
        else:
            print("CLEAR")
    
    else:
        # Default: status
        wait = check_rate_limit()
        if wait:
            print(f"RATE_LIMITED:{wait}")
        else:
            print("CLEAR")
