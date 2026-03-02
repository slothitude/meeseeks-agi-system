#!/usr/bin/env python3
"""
Auto-Entombment Wrapper for Meeseeks

Wraps sessions_spawn to automatically entomb Meeseeks after completion.
Every run (success or failure) becomes an ancestor in the Crypt.

Usage:
    from auto_entomb import spawn_and_entomb
    
    result = spawn_and_entomb(
        task="Fix the bug",
        meeseeks_type="coder",
        session_key="agent:main:subagent:xxx"
    )
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from genealogy import spawn_with_genealogy, MeeseeksGenealogy, SpeciesManager

# Import existing entombment
try:
    from entomb_meeseeks import entomb_meeseeks
    ENTOMB_AVAILABLE = True
except ImportError:
    ENTOMB_AVAILABLE = False

# The Crypt location
CRYPT_ROOT = Path(__file__).parent.parent.parent / "the-crypt"
AUTO_TOMB_DIR = CRYPT_ROOT / "auto-entombed"
RUN_LOG = CRYPT_ROOT / "meeseeks_runs.jsonl"


def ensure_directories():
    """Ensure auto-entomb directories exist."""
    AUTO_TOMB_DIR.mkdir(parents=True, exist_ok=True)


def log_run(session_key: str, task: str, result: Dict[str, Any]):
    """Log every Meeseeks run to a JSONL file for tracking."""
    ensure_directories()
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "session_key": session_key,
        "task": task[:200],  # Truncate long tasks
        "success": result.get("success", False),
        "model": result.get("model", "unknown"),
        "duration_ms": result.get("duration_ms", 0),
    }
    
    with open(RUN_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def extract_patterns_from_result(result: Dict[str, Any]) -> List[str]:
    """
    Extract learning patterns from a Meeseeks result.
    
    Looks for:
    - Error patterns
    - Success patterns
    - Tool usage patterns
    - Approach descriptions
    """
    patterns = []
    
    output = result.get("output", "")
    error = result.get("error", "")
    
    # Success patterns
    if result.get("success"):
        patterns.append("✓ Task completed successfully")
        
        # Look for approach mentions
        if "approach:" in output.lower() or "strategy:" in output.lower():
            patterns.append("Documented approach/strategy")
    
    # Failure patterns
    if not result.get("success"):
        if error:
            patterns.append(f"✗ Error: {error[:100]}")
        else:
            patterns.append("✗ Failed without explicit error")
    
    # Tool usage patterns
    tools_used = []
    for tool in ["read", "write", "edit", "exec", "browser", "search"]:
        if f'"{tool}"' in output or f"'{tool}'" in output or f"used {tool}" in output.lower():
            tools_used.append(tool)
    
    if tools_used:
        patterns.append(f"Tools used: {', '.join(tools_used)}")
    
    # File patterns
    if ".ts" in output or ".js" in output:
        patterns.append("Worked with TypeScript/JavaScript files")
    if ".py" in output:
        patterns.append("Worked with Python files")
    if ".md" in output:
        patterns.append("Worked with Markdown files")
    
    # Error type patterns
    if "timeout" in error.lower() or "timeout" in output.lower():
        patterns.append("⚠ Timeout encountered - consider longer timeout")
    if "rate limit" in error.lower():
        patterns.append("⚠ Rate limited - consider backoff")
    if "not found" in error.lower():
        patterns.append("⚠ Resource not found")
    
    return patterns if patterns else ["No extractable patterns"]


def infer_approach(output: str, task: str) -> str:
    """Infer the approach taken from output and task."""
    output_lower = output.lower()
    
    if "read" in output_lower and "edit" in output_lower:
        return "Read-analyze-edit cycle"
    elif "search" in output_lower:
        return "Search-based discovery"
    elif "browser" in output_lower:
        return "Browser automation"
    elif "exec" in output_lower:
        return "Shell command execution"
    elif "analysis" in output_lower:
        return "Analysis and reasoning"
    else:
        return "Standard execution"


def auto_entomb(
    session_key: str,
    task: str,
    result: Dict[str, Any],
    meeseeks_type: str = "standard"
) -> Optional[str]:
    """
    Automatically entomb a completed Meeseeks.
    
    Called after every sessions_spawn completes.
    
    Args:
        session_key: The session ID of the Meeseeks
        task: What it was asked to do
        result: The result dict from sessions_spawn
        meeseeks_type: Type of Meeseeks (coder, searcher, etc.)
        
    Returns:
        Path to the created ancestor file, or None if failed
    """
    ensure_directories()
    
    # Log the run
    log_run(session_key, task, result)
    
    # Extract patterns
    patterns = extract_patterns_from_result(result)
    
    # Determine outcome
    if result.get("success"):
        outcome = "Success - task completed"
    else:
        error = result.get("error", "Unknown failure")
        outcome = f"Failure - {error[:200]}"
    
    # Infer approach
    output = result.get("output", "")
    approach = infer_approach(output, task)
    
    # Use existing entombment if available
    if ENTOMB_AVAILABLE:
        try:
            return entomb_meeseeks(
                session_key=session_key,
                task=task,
                approach=approach,
                outcome=outcome,
                patterns=patterns,
                bloodline=meeseeks_type
            )
        except Exception as e:
            print(f"[auto_entomb] Entombment failed: {e}")
    
    # Fallback: direct file write
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    ancestor_id = f"auto-{timestamp}"
    
    content = f"""# Auto-Entombed: {ancestor_id}

## Session
`{session_key}`

## Task
{task}

## Approach
{approach}

## Outcome
{outcome}

## Patterns Discovered
{chr(10).join(f'- {p}' for p in patterns)}

## Meeseeks Type
{meeseeks_type}

## Entombed
{datetime.now().isoformat()}

## Raw Output Preview
```
{output[:500]}
```

---

*Auto-entombed by auto_entomb.py*
"""
    
    ancestor_path = AUTO_TOMB_DIR / f"{ancestor_id}.md"
    ancestor_path.write_text(content, encoding="utf-8")
    
    return str(ancestor_path)


def spawn_and_entomb_wrapper(
    spawn_func,
    task: str,
    meeseeks_type: str = "standard",
    **kwargs
) -> Dict[str, Any]:
    """
    Wrapper that calls spawn function and auto-entombs result.
    
    Usage:
        # Wrap the sessions_spawn call
        result = spawn_and_entomb_wrapper(
            spawn_func=sessions_spawn,
            task="Fix the bug",
            meeseeks_type="coder",
            runtime="subagent",
            ...
        )
    
    Args:
        spawn_func: The sessions_spawn function to call
        task: The task to spawn
        meeseeks_type: Type of Meeseeks
        **kwargs: Additional args passed to spawn_func
        
    Returns:
        The result dict with added 'entomb_path' key
    """
    import asyncio
    import time
    
    start_time = time.time()
    
    # Call the spawn function
    if asyncio.iscoroutinefunction(spawn_func):
        result = asyncio.run(spawn_func(task=task, **kwargs))
    else:
        result = spawn_func(task=task, **kwargs)
    
    duration_ms = int((time.time() - start_time) * 1000)
    
    # Add timing
    if isinstance(result, dict):
        result["duration_ms"] = duration_ms
    
    # Extract session key
    session_key = result.get("childSessionKey", result.get("sessionKey", "unknown"))
    
    # Auto-entomb
    entomb_path = auto_entomb(
        session_key=session_key,
        task=task,
        result=result,
        meeseeks_type=meeseeks_type
    )
    
    # Add entomb path to result
    if isinstance(result, dict):
        result["entomb_path"] = entomb_path
    
    return result


# Convenience function for manual use
def get_recent_auto_entombs(limit: int = 10) -> List[Dict[str, str]]:
    """Get recent auto-entombed ancestors."""
    ensure_directories()
    
    ancestors = []
    for ancestor_file in sorted(AUTO_TOMB_DIR.glob("auto-*.md"), reverse=True)[:limit]:
        content = ancestor_file.read_text(encoding="utf-8")
        
        # Extract task (simple parsing)
        task = ""
        for line in content.split("\n"):
            if line.startswith("## Task"):
                idx = content.split("\n").index(line)
                task = content.split("\n")[idx + 1].strip() if idx + 1 < len(content.split("\n")) else ""
                break
        
        ancestors.append({
            "id": ancestor_file.stem,
            "task": task[:100],
            "path": str(ancestor_file)
        })
    
    return ancestors


def get_run_stats() -> Dict[str, Any]:
    """Get statistics from the run log."""
    ensure_directories()
    
    if not RUN_LOG.exists():
        return {"total": 0, "success": 0, "failed": 0}
    
    runs = []
    with open(RUN_LOG, "r", encoding="utf-8") as f:
        for line in f:
            try:
                runs.append(json.loads(line.strip()))
            except:
                continue
    
    total = len(runs)
    success = sum(1 for r in runs if r.get("success"))
    
    return {
        "total": total,
        "success": success,
        "failed": total - success,
        "success_rate": f"{(success / total * 100):.1f}%" if total > 0 else "N/A",
        "avg_duration_ms": sum(r.get("duration_ms", 0) for r in runs) / total if total > 0 else 0
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-entomb Meeseeks")
    parser.add_argument("--json-input", action="store_true", 
                       help="Read input from stdin as JSON")
    parser.add_argument("--stats", action="store_true",
                       help="Show run statistics")
    parser.add_argument("--recent", type=int, default=0,
                       help="Show N recent auto-entombs")
    
    args = parser.parse_args()
    
    if args.stats:
        stats = get_run_stats()
        print(json.dumps(stats, indent=2))
    
    elif args.recent > 0:
        ancestors = get_recent_auto_entombs(args.recent)
        print(json.dumps(ancestors, indent=2))
    
    elif args.json_input:
        # Read JSON from stdin (for hook calls)
        input_data = json.loads(sys.stdin.read())
        
        path = auto_entomb(
            session_key=input_data.get("session_key", "unknown"),
            task=input_data.get("task", "Unknown task"),
            result=input_data.get("result", {}),
            meeseeks_type=input_data.get("meeseeks_type", "standard")
        )
        
        print(json.dumps({"entomb_path": path}))
    
    else:
        # Test auto-entombment
        test_result = {
            "success": True,
            "output": "I fixed the bug by reading the file and adding a null check.",
            "model": "glm-4.7-flash"
        }
        
        path = auto_entomb(
            session_key="test-session-123",
            task="Fix the authentication bug",
            result=test_result,
            meeseeks_type="coder"
        )
        
        print(f"Auto-entombed at: {path}")
        print(f"\nStats: {get_run_stats()}")
