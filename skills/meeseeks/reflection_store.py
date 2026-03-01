#!/usr/bin/env python3
"""
Meeseeks Reflection Memory Store
Stores and retrieves failure contexts for iterative improvement.

Based on:
- Reflexion (Shinn et al., 2023): https://github.com/noahshinn/reflexion
- Self-Refine (Madaan et al., 2023): https://arxiv.org/abs/2303.17651
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any

# Storage location
REFLECTION_DIR = Path(__file__).parent / "reflections"


class ReflectionStore:
    """
    Persistent storage for Meeseeks failure reflections.
    
    Each task gets its own reflection file containing:
    - All attempts made
    - What was tried
    - Why it failed
    - What to avoid next time
    """
    
    def __init__(self):
        REFLECTION_DIR.mkdir(exist_ok=True)
    
    def _get_task_id(self, task: str) -> str:
        """Generate a stable task ID from task description."""
        # Normalize task for consistent hashing
        normalized = " ".join(task.lower().split())
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
    
    def _get_reflection_path(self, task_id: str) -> Path:
        """Get the file path for a task's reflections."""
        return REFLECTION_DIR / f"{task_id}.json"
    
    def store_failure(
        self,
        task: str,
        error: str,
        approach: str,
        reason: str,
        logs: str = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Store a failure reflection for a task.
        
        Args:
            task: The task description
            error: Error message or exception
            approach: What approach was tried
            reason: Why it failed (root cause analysis)
            logs: Optional execution logs
            metadata: Optional additional context
            
        Returns:
            Task ID for reference
        """
        task_id = self._get_task_id(task)
        reflection_path = self._get_reflection_path(task_id)
        
        # Load existing reflections or create new
        if reflection_path.exists():
            with open(reflection_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {
                "task": task,
                "task_id": task_id,
                "created": datetime.now().isoformat(),
                "failures": []
            }
        
        # Add new failure
        failure_record = {
            "attempt": len(data["failures"]) + 1,
            "timestamp": datetime.now().isoformat(),
            "error": error,
            "approach": approach,
            "reason": reason,
            "logs": logs[:500] if logs else None,  # Truncate logs
            "metadata": metadata
        }
        
        data["failures"].append(failure_record)
        data["updated"] = datetime.now().isoformat()
        
        # Save
        with open(reflection_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return task_id
    
    def get_failures(self, task: str) -> List[Dict[str, Any]]:
        """
        Retrieve all failure reflections for a task.
        
        Args:
            task: The task description
            
        Returns:
            List of failure records, or empty list if none
        """
        task_id = self._get_task_id(task)
        reflection_path = self._get_reflection_path(task_id)
        
        if not reflection_path.exists():
            return []
        
        with open(reflection_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data.get("failures", [])
    
    def format_for_prompt(self, task: str, max_failures: int = 5) -> str:
        """
        Format failure reflections for injection into a retry prompt.
        
        Args:
            task: The task description
            max_failures: Maximum number of failures to include
            
        Returns:
            Formatted string for prompt injection
        """
        failures = self.get_failures(task)
        
        if not failures:
            return ""
        
        # Take most recent failures
        recent_failures = failures[-max_failures:]
        
        output = "\n## 🪞 REFLECTION MEMORY - Previous Attempts\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        output += "**These approaches did NOT work. Learn from them:**\n\n"
        
        for failure in recent_failures:
            output += f"### ❌ Attempt {failure['attempt']}\n"
            output += f"**Approach:** {failure['approach']}\n"
            output += f"**Error:** {failure['error']}\n"
            output += f"**Why it failed:** {failure['reason']}\n\n"
        
        output += "⚠️ **DO NOT repeat these approaches.**\n"
        output += "Analyze WHY they failed and try something DIFFERENT.\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        return output
    
    def clear_reflections(self, task: str) -> bool:
        """
        Clear all reflections for a task (after success).
        
        Args:
            task: The task description
            
        Returns:
            True if reflections were cleared, False if none existed
        """
        task_id = self._get_task_id(task)
        reflection_path = self._get_reflection_path(task_id)
        
        if reflection_path.exists():
            reflection_path.unlink()
            return True
        
        return False
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """
        Get summary of all tasks with reflections.
        
        Returns:
            List of task summaries
        """
        tasks = []
        
        for path in REFLECTION_DIR.glob("*.json"):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            tasks.append({
                "task_id": data["task_id"],
                "task": data["task"][:100] + "..." if len(data["task"]) > 100 else data["task"],
                "failure_count": len(data["failures"]),
                "created": data["created"],
                "updated": data.get("updated", data["created"])
            })
        
        return tasks


# Singleton instance
_store = None

def get_store() -> ReflectionStore:
    """Get the singleton ReflectionStore instance."""
    global _store
    if _store is None:
        _store = ReflectionStore()
    return _store


# Convenience functions
def store_failure(task: str, error: str, approach: str, reason: str, **kwargs) -> str:
    """Store a failure reflection."""
    return get_store().store_failure(task, error, approach, reason, **kwargs)


def get_reflections(task: str) -> List[Dict[str, Any]]:
    """Get all failure reflections for a task."""
    return get_store().get_failures(task)


def format_reflections(task: str, max_failures: int = 5) -> str:
    """Format reflections for prompt injection."""
    return get_store().format_for_prompt(task, max_failures)


def clear_reflections(task: str) -> bool:
    """Clear reflections for a task."""
    return get_store().clear_reflections(task)


if __name__ == "__main__":
    # Demo/test
    import sys
    import io
    
    # Fix Windows encoding
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    if len(sys.argv) < 2:
        print("Reflection Store - Meeseeks Memory System")
        print("\nCommands:")
        print("  list                    - Show all tasks with reflections")
        print("  show <task>             - Show reflections for a task")
        print("  clear <task>            - Clear reflections for a task")
        print("  test                    - Run a test with sample data")
        sys.exit(0)
    
    cmd = sys.argv[1]
    store = get_store()
    
    if cmd == "list":
        tasks = store.get_all_tasks()
        if not tasks:
            print("No reflections stored.")
        else:
            for task in tasks:
                print(f"\n[{task['task_id']}] {task['task']}")
                print(f"  Failures: {task['failure_count']}, Updated: {task['updated']}")
    
    elif cmd == "show":
        if len(sys.argv) < 3:
            print("Usage: reflection_store.py show <task>")
            sys.exit(1)
        task = sys.argv[2]
        print(store.format_for_prompt(task))
    
    elif cmd == "clear":
        if len(sys.argv) < 3:
            print("Usage: reflection_store.py clear <task>")
            sys.exit(1)
        task = sys.argv[2]
        if store.clear_reflections(task):
            print(f"✓ Reflections cleared for task")
        else:
            print("No reflections found for task")
    
    elif cmd == "test":
        task = "Fix the authentication bug in login.ts"
        
        print("Storing test reflections...")
        store_failure(task, "TypeError: undefined is not a function", 
                      "Tried to access user.auth.token directly", 
                      "user object was null due to async timing")
        
        store_failure(task, "AssertionError: expected true to be false",
                      "Mocked the auth service incorrectly",
                      "Mock wasn't resetting between tests")
        
        print("\n" + "="*60)
        print("FORMATTED FOR PROMPT:")
        print("="*60)
        print(store.format_for_prompt(task))
