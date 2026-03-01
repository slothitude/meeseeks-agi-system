#!/usr/bin/env python3
"""
Meeseeks Feedback Loop - Complete Implementation

Implements the full feedback loop described in meeseeks-manager/SKILL.md:
- Automatic retry with reflection memory
- Desperation escalation
- Failure context extraction
- Human escalation when needed

Based on:
- Reflexion (Shinn et al., 2023)
- Self-Refine (Madaan et al., 2023)
- Intrinsic Metacognitive Learning (ICML 2025)
"""

import json
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime

from spawn_meeseeks import spawn_prompt
from reflection_store import store_failure, format_reflections, clear_reflections


@dataclass
class MeeseeksResult:
    """Result from a Meeseeks execution."""
    success: bool
    output: str
    error: Optional[str] = None
    logs: Optional[str] = None
    attempts: int = 1
    failures: List[Dict[str, Any]] = field(default_factory=list)
    needs_human: bool = False


def extract_approach_from_logs(logs: str) -> str:
    """
    Parse logs to understand what approach was tried.
    
    Looks for:
    - Files read/edited
    - Commands executed
    - Strategies attempted
    """
    if not logs:
        return "Unknown approach (no logs available)"
    
    approach_parts = []
    
    # Look for file operations
    if "read" in logs.lower() or "reading" in logs.lower():
        approach_parts.append("read files")
    if "edit" in logs.lower() or "wrote" in logs.lower():
        approach_parts.append("modified files")
    if "bash" in logs.lower() or "exec" in logs.lower():
        approach_parts.append("ran commands")
    
    # Look for common patterns
    if "test" in logs.lower():
        approach_parts.append("ran tests")
    if "error" in logs.lower():
        approach_parts.append("encountered errors")
    
    if approach_parts:
        return "Attempted to: " + ", ".join(approach_parts)
    
    return "Approach unclear from logs"


def analyze_failure_reason(result: Dict[str, Any]) -> str:
    """
    Categorize and explain why a failure occurred.
    
    Categories:
    - Syntax error
    - Test failure
    - Logic error
    - Timeout
    - Missing dependency
    - Permission issue
    - etc.
    """
    error = result.get("error", "")
    output = result.get("output", "")
    logs = result.get("logs", "")
    
    combined = f"{error} {output} {logs}".lower()
    
    # Categorize based on patterns
    if "timeout" in combined or "timed out" in combined:
        return "Task timed out - may need more time or simpler approach"
    
    if "syntax" in combined or "parse error" in combined:
        return "Syntax error - code structure issue"
    
    if "test" in combined and ("fail" in combined or "error" in combined):
        return "Tests failed - implementation doesn't meet requirements"
    
    if "not found" in combined or "cannot find" in combined:
        return "Missing dependency or file - check paths and installations"
    
    if "permission" in combined or "access denied" in combined:
        return "Permission issue - may need elevated privileges"
    
    if "type" in combined and "error" in combined:
        return "Type error - mismatched data types or null values"
    
    if "import" in combined or "module" in combined:
        return "Import/module error - missing or incorrect dependency"
    
    if "connection" in combined or "network" in combined:
        return "Network/connection issue - check connectivity"
    
    # Generic fallback
    if error:
        return f"Error: {error[:200]}"
    
    return "Unknown failure reason"


async def spawn_meeseeks_with_feedback(
    task: str,
    meeseeks_type: str = "standard",
    max_retries: int = 3,
    spawn_func: Callable = None,
    **kwargs
) -> MeeseeksResult:
    """
    Spawn a Meeseeks with automatic feedback loop.
    
    Args:
        task: The task description
        meeseeks_type: Initial type of Meeseeks
        max_retries: Maximum number of retry attempts
        spawn_func: Async function to spawn (sessions_spawn equivalent)
        **kwargs: Additional arguments for spawn
        
    Returns:
        MeeseeksResult with success status and details
        
    Example:
        result = await spawn_meeseeks_with_feedback(
            task="Fix the auth bug in login.ts",
            meeseeks_type="coder",
            max_retries=3,
            spawn_func=sessions_spawn
        )
        
        if result.success:
            print(f"Done in {result.attempts} attempts!")
        else:
            print(f"Failed after {result.attempts} attempts")
            print("Needs human intervention:", result.needs_human)
    """
    if spawn_func is None:
        raise ValueError("spawn_func is required - pass your sessions_spawn function")
    
    attempt = 1
    failures = []
    
    while attempt <= max_retries:
        # Get reflection memory from previous failures
        previous_failures = format_reflections(task) if attempt > 1 else None
        
        # Generate spawn config with accumulated context
        config = spawn_prompt(
            task=task,
            meeseeks_type=meeseeks_type,
            attempt=attempt,
            previous_failures=previous_failures
        )
        
        # Spawn the Meeseeks
        spawn_result = await spawn_func(
            runtime='subagent',
            task=config['task'],
            thinking=config['thinking'],
            runTimeoutSeconds=config.get('timeout'),
            mode='run',
            cleanup='delete',
            **kwargs
        )
        
        # Check result
        if spawn_result.get('success', False):
            # Success! Clear reflections and return
            clear_reflections(task)
            
            return MeeseeksResult(
                success=True,
                output=spawn_result.get('output', ''),
                attempts=attempt,
                failures=failures
            )
        
        # Failed - extract failure context
        error = spawn_result.get('error', 'Unknown error')
        logs = spawn_result.get('logs', '')
        approach = extract_approach_from_logs(logs)
        reason = analyze_failure_reason(spawn_result)
        
        # Store in reflection memory
        store_failure(
            task=task,
            error=error,
            approach=approach,
            reason=reason,
            logs=logs
        )
        
        failures.append({
            "attempt": attempt,
            "error": error,
            "approach": approach,
            "reason": reason
        })
        
        # Check retry limit
        if attempt >= max_retries:
            return MeeseeksResult(
                success=False,
                error="Max retries reached",
                attempts=attempt,
                failures=failures,
                needs_human=True
            )
        
        # Increment for next attempt
        attempt += 1
    
    # Should not reach here, but safety fallback
    return MeeseeksResult(
        success=False,
        error="Unexpected loop exit",
        attempts=attempt,
        failures=failures,
        needs_human=True
    )


def format_failure_report(result: MeeseeksResult) -> str:
    """
    Format a failure report for human escalation.
    """
    lines = [
        f"❌ Meeseeks failed after {result.attempts} attempts.",
        "",
        "**Failures:**"
    ]
    
    for failure in result.failures:
        lines.append(f"\n{failure['attempt']}. {failure['error']}")
        lines.append(f"   - Tried: {failure['approach']}")
        lines.append(f"   - Reason: {failure['reason']}")
    
    lines.extend([
        "",
        "This may need human intervention. Options:",
        "- Try a different Meeseeks type",
        "- Increase retry limit",
        "- Take a completely different approach",
        "- Investigate manually"
    ])
    
    return "\n".join(lines)


# Synchronous wrapper for non-async contexts
def spawn_meeseeks_sync(
    task: str,
    meeseeks_type: str = "standard",
    max_retries: int = 3,
    spawn_func: Callable = None,
    **kwargs
) -> MeeseeksResult:
    """
    Synchronous version of spawn_meeseeks_with_feedback.
    
    Requires spawn_func to be a synchronous function.
    """
    import asyncio
    
    # If spawn_func is async, run it in event loop
    if asyncio.iscoroutinefunction(spawn_func):
        async def _run():
            return await spawn_meeseeks_with_feedback(
                task, meeseeks_type, max_retries, spawn_func, **kwargs
            )
        return asyncio.run(_run())
    
    # Synchronous spawn_func
    attempt = 1
    failures = []
    
    while attempt <= max_retries:
        previous_failures = format_reflections(task) if attempt > 1 else None
        
        config = spawn_prompt(
            task=task,
            meeseeks_type=meeseeks_type,
            attempt=attempt,
            previous_failures=previous_failures
        )
        
        spawn_result = spawn_func(
            runtime='subagent',
            task=config['task'],
            thinking=config['thinking'],
            runTimeoutSeconds=config.get('timeout'),
            mode='run',
            cleanup='delete',
            **kwargs
        )
        
        if spawn_result.get('success', False):
            clear_reflections(task)
            return MeeseeksResult(
                success=True,
                output=spawn_result.get('output', ''),
                attempts=attempt,
                failures=failures
            )
        
        error = spawn_result.get('error', 'Unknown error')
        logs = spawn_result.get('logs', '')
        approach = extract_approach_from_logs(logs)
        reason = analyze_failure_reason(spawn_result)
        
        store_failure(task, error, approach, reason, logs)
        failures.append({"attempt": attempt, "error": error, "approach": approach, "reason": reason})
        
        if attempt >= max_retries:
            return MeeseeksResult(
                success=False,
                error="Max retries reached",
                attempts=attempt,
                failures=failures,
                needs_human=True
            )
        
        attempt += 1
    
    return MeeseeksResult(success=False, error="Unexpected exit", attempts=attempt, failures=failures, needs_human=True)


if __name__ == "__main__":
    print("Meeseeks Feedback Loop - Complete Implementation")
    print("\nThis module provides:")
    print("  - spawn_meeseeks_with_feedback() - Async feedback loop")
    print("  - spawn_meeseeks_sync() - Sync feedback loop")
    print("  - extract_approach_from_logs() - Parse what was tried")
    print("  - analyze_failure_reason() - Categorize failures")
    print("  - format_failure_report() - Human-readable failure report")
    print("\nUsage:")
    print("  from feedback_loop import spawn_meeseeks_with_feedback")
    print("  result = await spawn_meeseeks_with_feedback(task, 'coder', spawn_func=sessions_spawn)")
    print("\nSee meeseeks-manager/SKILL.md for full documentation.")
