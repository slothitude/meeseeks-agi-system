#!/usr/bin/env python3
"""
Rate Limit Handler - Auto-fallback when API limits hit
=====================================================

When z.ai rate limits (429 error), automatically:
1. Detect the rate limit
2. Switch to Ollama fallback
3. Queue the task for retry
4. Resume when limit resets

Usage:
    from rate_limit_handler import RateLimitHandler
    
    handler = RateLimitHandler()
    
    # Wrap API calls
    result = handler.call(lambda: some_api_call())
    
    # Or check status
    handler.status()
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Callable, Optional, Dict

WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
RATE_LIMIT_LOG = WORKSPACE / "the-crypt" / "rate_limits.jsonl"
PENDING_TASKS = WORKSPACE / "the-crypt" / "pending_rate_limited.json"


class RateLimitHandler:
    def __init__(self):
        self.rate_limited = False
        self.limit_reset_time = None
        self.fallback_model = "phi3:mini"  # Ollama
        self.primary_model = "zai/glm-5"
        self.log_file = RATE_LIMIT_LOG
        self.pending_file = PENDING_TASKS
        
    def is_rate_limited(self) -> bool:
        """Check if we're currently rate limited"""
        if not self.rate_limited:
            return False
            
        # Check if reset time has passed
        if self.limit_reset_time and datetime.now() > self.limit_reset_time:
            self.rate_limited = False
            self.limit_reset_time = None
            return False
            
        return True
    
    def detect_rate_limit(self, error: Exception) -> bool:
        """Detect if an error is a rate limit"""
        error_str = str(error).lower()
        rate_limit_patterns = [
            "rate limit",
            "429",
            "too many requests",
            "api rate limit reached",
            "please try again later",
            "quota exceeded",
        ]
        return any(p in error_str for p in rate_limit_patterns)
    
    def handle_rate_limit(self, error: Exception, task: Optional[Dict] = None):
        """Handle a rate limit error"""
        self.rate_limited = True
        # Assume 5 minute reset (z.ai typical)
        self.limit_reset_time = datetime.now() + timedelta(minutes=5)
        
        # Log it
        self.log_rate_limit(error)
        
        # Queue task if provided
        if task:
            self.queue_task(task)
    
    def log_rate_limit(self, error: Exception):
        """Log rate limit event"""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "error": str(error),
            "reset_time": self.limit_reset_time.isoformat() if self.limit_reset_time else None,
            "fallback_model": self.fallback_model
        }
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(record) + '\n')
    
    def queue_task(self, task: Dict):
        """Queue a task for retry after rate limit resets"""
        pending = []
        
        if self.pending_file.exists():
            try:
                pending = json.loads(self.pending_file.read_text())
            except:
                pending = []
        
        task["queued_at"] = datetime.now().isoformat()
        task["retry_after"] = self.limit_reset_time.isoformat() if self.limit_reset_time else None
        pending.append(task)
        
        self.pending_file.write_text(json.dumps(pending, indent=2))
    
    def get_pending_tasks(self) -> list:
        """Get pending tasks that are ready to retry"""
        if not self.pending_file.exists():
            return []
        
        try:
            pending = json.loads(self.pending_file.read_text())
        except:
            return []
        
        # Filter tasks that are ready
        ready = []
        for task in pending:
            retry_after = task.get("retry_after")
            if retry_after:
                retry_time = datetime.fromisoformat(retry_after)
                if datetime.now() > retry_time:
                    ready.append(task)
            else:
                ready.append(task)
        
        return ready
    
    def get_fallback_model(self) -> str:
        """Get the fallback model to use"""
        return self.fallback_model
    
    def status(self) -> Dict:
        """Get rate limit status"""
        pending_count = len(self.get_pending_tasks())
        
        # Get recent rate limits
        recent_limits = []
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    lines = f.readlines()[-5:]  # Last 5
                    for line in lines:
                        if line.strip():
                            recent_limits.append(json.loads(line))
            except:
                pass
        
        return {
            "rate_limited": self.is_rate_limited(),
            "reset_time": self.limit_reset_time.isoformat() if self.limit_reset_time else None,
            "pending_tasks": pending_count,
            "primary_model": self.primary_model,
            "fallback_model": self.fallback_model,
            "recent_limits": len(recent_limits)
        }


def get_spawn_model() -> str:
    """
    Get the appropriate model for spawning.
    Returns fallback if rate limited.
    """
    handler = RateLimitHandler()
    
    if handler.is_rate_limited():
        print(f"[RATE-LIMIT] Using fallback: {handler.fallback_model}")
        return handler.fallback_model
    
    return handler.primary_model


def check_and_retry_pending() -> list:
    """
    Check pending tasks and return those ready for retry.
    Call this from heartbeat to auto-retry rate-limited tasks.
    """
    handler = RateLimitHandler()
    return handler.get_pending_tasks()


# CLI
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Rate Limit Handler")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--model", action="store_true", help="Get current model to use")
    parser.add_argument("--retry", action="store_true", help="Get pending tasks ready for retry")
    
    args = parser.parse_args()
    
    handler = RateLimitHandler()
    
    if args.status:
        status = handler.status()
        print("\n=== RATE LIMIT STATUS ===")
        print(f"Rate Limited: {status['rate_limited']}")
        if status['reset_time']:
            print(f"Reset Time: {status['reset_time']}")
        print(f"Pending Tasks: {status['pending_tasks']}")
        print(f"Primary Model: {status['primary_model']}")
        print(f"Fallback Model: {status['fallback_model']}")
        print(f"Recent Limits: {status['recent_limits']}")
    
    elif args.model:
        model = get_spawn_model()
        print(f"Model to use: {model}")
    
    elif args.retry:
        pending = check_and_retry_pending()
        if pending:
            print(f"Tasks ready for retry: {len(pending)}")
            for task in pending:
                print(f"  - {task.get('task', 'Unknown')[:50]}...")
        else:
            print("No tasks pending retry")
    
    else:
        status = handler.status()
        print(f"Rate limited: {status['rate_limited']}")
        print(f"Pending: {status['pending_tasks']}")
