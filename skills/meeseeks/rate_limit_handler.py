#!/usr/bin/env python3
"""
Rate Limit Handler for Meeseeks Spawning
========================================

When z.ai API returns 429 (rate limit), this system:
1. Detects the rate limit error
2. Queues the task for retry
3. Waits before retrying
4. Uses fallback models when available

Usage:
    from rate_limit_handler import RateLimitHandler
    
    handler = RateLimitHandler()
    
    # Check before spawning
    if handler.can_spawn():
        sessions_spawn(...)
    else:
        handler.queue_task(task)
        
    # On rate limit error
    handler.on_rate_limit(task, error)
"""

import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict

WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
QUEUE_FILE = WORKSPACE / "the-crypt" / "rate_limit_queue.json"
RATE_LOG = WORKSPACE / "the-crypt" / "rate_limit_log.jsonl"

# Rate limit settings
MAX_CONCURRENT = 2  # Max concurrent z.ai requests
COOLDOWN_SECONDS = 60  # Wait after rate limit
MIN_SPAWN_INTERVAL = 5  # Min seconds between spawns


@dataclass
class QueuedTask:
    task: str
    thinking: str
    runtime: str
    timeout: int
    queued_at: str
    retry_count: int
    priority: int  # Lower = higher priority


class RateLimitHandler:
    def __init__(self):
        self.queue_file = QUEUE_FILE
        self.log_file = RATE_LOG
        self.last_spawn_time = 0
        self.active_spawns = 0
        self.rate_limited_until = 0
        
    def load_queue(self) -> List[QueuedTask]:
        """Load queued tasks"""
        if not self.queue_file.exists():
            return []
        
        try:
            with open(self.queue_file, 'r') as f:
                data = json.load(f)
                return [QueuedTask(**item) for item in data]
        except:
            return []
    
    def save_queue(self, tasks: List[QueuedTask]):
        """Save queued tasks"""
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.queue_file, 'w') as f:
            json.dump([asdict(t) for t in tasks], f, indent=2)
    
    def can_spawn(self) -> bool:
        """Check if we can spawn now"""
        now = time.time()
        
        # Check cooldown from rate limit
        if now < self.rate_limited_until:
            return False
        
        # Check min interval
        if now - self.last_spawn_time < MIN_SPAWN_INTERVAL:
            return False
        
        # Check concurrent limit
        if self.active_spawns >= MAX_CONCURRENT:
            return False
        
        return True
    
    def on_spawn(self):
        """Call when spawning"""
        self.last_spawn_time = time.time()
        self.active_spawns += 1
    
    def on_complete(self):
        """Call when spawn completes"""
        if self.active_spawns > 0:
            self.active_spawns -= 1
    
    def on_rate_limit(self, task: str, thinking: str = "high", 
                       runtime: str = "subagent", timeout: int = 600,
                       priority: int = 5):
        """Call when rate limit hit - queue the task"""
        self.rate_limited_until = time.time() + COOLDOWN_SECONDS
        
        queued = QueuedTask(
            task=task,
            thinking=thinking,
            runtime=runtime,
            timeout=timeout,
            queued_at=datetime.now().isoformat(),
            retry_count=0,
            priority=priority
        )
        
        queue = self.load_queue()
        queue.append(queued)
        # Sort by priority
        queue.sort(key=lambda x: x.priority)
        self.save_queue(queue)
        
        # Log the rate limit
        self.log_rate_limit(task)
        
        return queued
    
    def get_next_task(self) -> Optional[QueuedTask]:
        """Get next task from queue if we can spawn"""
        if not self.can_spawn():
            return None
        
        queue = self.load_queue()
        if not queue:
            return None
        
        # Get highest priority task
        task = queue.pop(0)
        task.retry_count += 1
        self.save_queue(queue)
        
        return task
    
    def log_rate_limit(self, task: str):
        """Log rate limit event"""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "task_preview": task[:100],
            "cooldown_seconds": COOLDOWN_SECONDS
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def get_status(self) -> Dict:
        """Get rate limit status"""
        queue = self.load_queue()
        now = time.time()
        
        return {
            "can_spawn": self.can_spawn(),
            "active_spawns": self.active_spawns,
            "queued_tasks": len(queue),
            "rate_limited": now < self.rate_limited_until,
            "cooldown_remaining": max(0, self.rate_limited_until - now),
            "last_spawn": self.last_spawn_time
        }
    
    def spawn_from_queue(self, spawn_func) -> Optional[Dict]:
        """Spawn next task from queue using provided spawn function"""
        task = self.get_next_task()
        if not task:
            return None
        
        try:
            result = spawn_func(
                runtime=task.runtime,
                task=task.task,
                thinking=task.thinking,
                mode="run",
                runTimeoutSeconds=task.timeout
            )
            self.on_spawn()
            return result
        except Exception as e:
            # Re-queue if failed
            if "rate limit" in str(e).lower() or "429" in str(e):
                queue = self.load_queue()
                task.retry_count += 1
                if task.retry_count < 5:  # Max 5 retries
                    queue.insert(0, task)  # Put back at front
                    self.save_queue(queue)
                self.rate_limited_until = time.time() + COOLDOWN_SECONDS
            raise


# CLI
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Rate Limit Handler")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--queue", type=str, help="Queue a task")
    parser.add_argument("--next", action="store_true", help="Get next task")
    parser.add_argument("--clear", action="store_true", help="Clear queue")
    
    args = parser.parse_args()
    
    handler = RateLimitHandler()
    
    if args.status:
        status = handler.get_status()
        print("\n=== RATE LIMIT STATUS ===")
        for k, v in status.items():
            print(f"{k}: {v}")
    
    elif args.queue:
        handler.on_rate_limit(args.queue)
        print(f"Queued task (cooldown {COOLDOWN_SECONDS}s)")
    
    elif args.next:
        task = handler.get_next_task()
        if task:
            print(f"Next task: {task.task[:100]}...")
            print(f"Priority: {task.priority}, Retries: {task.retry_count}")
        else:
            print("No tasks in queue or rate limited")
    
    elif args.clear:
        handler.save_queue([])
        print("Queue cleared")
    
    else:
        status = handler.get_status()
        print(f"Can spawn: {status['can_spawn']}")
        print(f"Queued: {status['queued_tasks']}")
