#!/usr/bin/env python3
"""
Cron-based Meeseeks Entombment

Scans recent subagent sessions and entombs any that haven't been captured yet.

Usage:
    python cron_entomb.py [--max-age-minutes 30]

Can be run via:
- Cron job (every 5-10 minutes)
- Heartbeat check
- Manual execution
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Set

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from auto_entomb import auto_entomb, log_run
from failure_capture import record_failure  # NEW: Failure pattern capture
from smart_chunking import SmartChunker  # NEW: Semantic chunking

# Import auto_retry system
try:
    from auto_retry import handle_failed_meeseeks, is_retryable, decompose_task
    AUTO_RETRY_AVAILABLE = True
except ImportError:
    AUTO_RETRY_AVAILABLE = False

# Tracking file for already-entombed sessions
ENTOMBED_TRACKING = Path(__file__).parent.parent.parent / "the-crypt" / "entombed_sessions.json"


def get_entombed_sessions() -> Set[str]:
    """Get set of already-entombed session keys."""
    if ENTOMBED_TRACKING.exists():
        try:
            return set(json.loads(ENTOMBED_TRACKING.read_text()))
        except:
            return set()
    return set()


def mark_entombed(session_key: str):
    """Mark a session as entombed."""
    entombed = get_entombed_sessions()
    entombed.add(session_key)
    ENTOMBED_TRACKING.parent.mkdir(parents=True, exist_ok=True)
    ENTOMBED_TRACKING.write_text(json.dumps(list(entombed), indent=2))


def get_recent_subagents(max_age_minutes: int = 30) -> list:
    """
    Get recent subagent runs from the OpenClaw runs.json file.
    
    Returns list of dicts with session_key, task, status, etc.
    """
    try:
        # Read from OpenClaw subagents runs database
        runs_file = Path.home() / ".openclaw" / "subagents" / "runs.json"
        
        if not runs_file.exists():
            print(f"[cron_entomb] Runs file not found: {runs_file}")
            return []
        
        data = json.loads(runs_file.read_text(encoding="utf-8"))
        runs = data.get("runs", {})
        
        cutoff = datetime.now() - timedelta(minutes=max_age_minutes)
        cutoff_ts = cutoff.timestamp() * 1000  # Convert to ms
        
        recent = []
        
        for run_id, run in runs.items():
            ended_at = run.get("endedAt")
            if not ended_at:
                continue
            
            if ended_at < cutoff_ts:
                continue
            
            # Extract relevant info
            session_key = run.get("childSessionKey", "")
            if not session_key:
                continue
            
            task = run.get("task", "Unknown task")
            outcome = run.get("outcome", {})
            ended_reason = run.get("endedReason", "")
            
            recent.append({
                "sessionKey": session_key,
                "runId": run_id,
                "task": task,
                "status": "done" if ended_reason == "subagent-complete" else "failed",
                "endedAt": ended_at,
                "label": task[:100],
                "model": run.get("model", "unknown"),
                "outcome": outcome,
                "runtimeMs": (ended_at - run.get("startedAt", ended_at))
            })
        
        return recent
        
    except Exception as e:
        print(f"[cron_entomb] Error getting subagents: {e}")
        import traceback
        traceback.print_exc()
        return []


def extract_result_from_run(run: Dict[str, Any]) -> Dict[str, Any]:
    """Extract result info from a run dict."""
    return {
        "success": run.get("status") == "done",
        "output": run.get("label", "")[:500],
        "model": run.get("model", "unknown"),
        "duration_ms": run.get("runtimeMs", 0)
    }


def infer_meeseeks_type(task: str) -> str:
    """Infer Meeseeks type from task description."""
    task_lower = task.lower()
    
    if any(kw in task_lower for kw in ["code", "fix", "implement", "refactor", "bug"]):
        return "coder"
    elif any(kw in task_lower for kw in ["search", "find", "analyze", "scan"]):
        return "searcher"
    elif any(kw in task_lower for kw in ["deploy", "build", "release"]):
        return "deployer"
    elif any(kw in task_lower for kw in ["test", "verify", "check"]):
        return "tester"
    elif any(kw in task_lower for kw in ["evolve", "dna", "bloodline", "evolution"]):
        return "evolver"
    else:
        return "standard"


def check_for_timeouts(runs: list) -> list:
    """Check for timed-out runs and create retry chunks."""
    timeouts = []
    
    for run in runs:
        outcome = run.get("outcome", {})
        status = outcome.get("status", "")
        
        if status == "timeout":
            timeouts.append(run)
    
    return timeouts


def create_retry_chunks(timeout_runs: list, workspace_dir: Path) -> int:
    """
    Create retry chunks for timed-out runs.
    Now uses the auto_retry system for intelligent decomposition.
    """
    if not timeout_runs:
        return 0
    
    created = 0
    
    for run in timeout_runs:
        session_key = run.get("sessionKey", "")
        task = run.get("task", "")
        
        # Use the new auto_retry system if available
        if AUTO_RETRY_AVAILABLE:
            try:
                retry_spawned = handle_failed_meeseeks(
                    session_key=session_key,
                    failure_reason="timeout",
                    task=task
                )
                if retry_spawned:
                    created += 1
                    print(f"[cron_entomb] Created retry chain for: {session_key[:30]}...")
                continue
            except Exception as e:
                print(f"[cron_entomb] Auto-retry failed: {e}")
                # Fall through to legacy handling
        
        # Legacy: Use old pending-retries.json format
        retry_file = workspace_dir / "the-crypt" / "pending-retries.json"
        
        # Load existing
        if retry_file.exists():
            data = json.loads(retry_file.read_text(encoding="utf-8-sig"))  # Handle BOM from PowerShell
        else:
            data = {"pending": []}
        
        # Check if already has a retry
        existing = [r for r in data["pending"] if r.get("original_task") == task]
        if existing:
            continue
        
        # Count chunk depth (allow up to 3 levels of chunking)
        chunk_depth = task.count("RETRY CHUNK")
        if chunk_depth >= 3:
            print(f"[cron_entomb] Max chunk depth (3) reached: {session_key[:30]}...")
            continue
        
        # Break task into chunks using smart chunking
        chunks = break_task_into_chunks(task)
        
        # Add depth info to retry entry
        new_depth = chunk_depth + 1
        
        retry_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_key": session_key,
            "original_task": task,
            "chunks": chunks,
            "status": "pending",
            "retry_count": 1,
            "chunk_depth": new_depth
        }
        
        data["pending"].append(retry_entry)
        created += 1
        print(f"[cron_entomb] Created retry chunks for: {session_key[:30]}...")
        
        # Save
        retry_file.parent.mkdir(parents=True, exist_ok=True)
        retry_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    return created


def break_task_into_chunks(task: str) -> list:
    """
    Break a task into smaller chunks for retry.
    Now uses smart chunking for better coherence.
    """
    try:
        # Try smart chunking first
        chunker = SmartChunker()

        # Check if task should be chunked
        task_type = chunker.detect_task_type(task)
        should_chunk, reason = chunker.should_chunk_task(task, task_type)

        if not should_chunk:
            print(f"[cron_entomb] Not chunking: {reason}")
            return [task]  # Return as single chunk

        # Create smart chunks
        smart_chunks = chunker.create_smart_chunks(task, max_chunks=3)

        # Convert to simple list of strings for compatibility
        chunks = [chunk["text"] for chunk in smart_chunks]

        print(f"[cron_entomb] Created {len(chunks)} smart chunks (quality: {[c['quality_score'] for c in smart_chunks]})")

        return chunks

    except Exception as e:
        print(f"[cron_entomb] Smart chunking failed, using fallback: {e}")
        import traceback
        traceback.print_exc()

        # Fallback to simple chunking
        return _simple_chunk_fallback(task)


def _simple_chunk_fallback(task: str) -> list:
    """Fallback to simple text chunking if smart chunking fails."""
    chunks = []

    # Strategy 1: Split by numbered steps
    import re
    step_pattern = r'(?:^|\n)\s*(\d+)[.\)]\s*'
    parts = re.split(step_pattern, task)

    # Filter to actual content (not just numbers)
    steps = [p.strip() for p in parts if p.strip() and not p.strip().isdigit() and len(p.strip()) > 10]

    if len(steps) >= 2:
        # Group into 2-3 chunks
        chunk_count = min(3, max(2, len(steps) // 2))
        per_chunk = max(1, len(steps) // chunk_count)

        for i in range(0, len(steps), per_chunk):
            chunk_steps = steps[i:i+per_chunk]
            chunk_text = " ".join(chunk_steps)
            chunks.append(f"Part {i//per_chunk + 1}: {chunk_text}")

        return chunks[:3]  # Max 3 chunks

    # Strategy 2: Split by paragraphs
    paragraphs = [p.strip() for p in task.split('\n\n') if p.strip() and len(p.strip()) > 20]

    if len(paragraphs) >= 2:
        mid = len(paragraphs) // 2
        chunks.append("FIRST HALF:\n" + "\n".join(paragraphs[:mid]))
        chunks.append("SECOND HALF:\n" + "\n".join(paragraphs[mid:]))
        return chunks

    # Strategy 3: Just halve the text
    mid = len(task) // 2
    chunks.append(f"Part 1: {task[:mid]}")
    chunks.append(f"Part 2: {task[mid:]}")

    return chunks


def get_pending_retries(max_retries: int = 3, max_concurrent: int = 2) -> list:
    """
    Get pending retry chunks that should be spawned.
    
    Args:
        max_retries: Maximum retry attempts per task
        max_concurrent: Maximum concurrent retries to return
        
    Returns:
        List of spawn configs for the main agent to execute
    """
    retry_file = Path(__file__).parent.parent.parent / "the-crypt" / "pending-retries.json"
    
    if not retry_file.exists():
        return []
    
    try:
        data = json.loads(retry_file.read_text(encoding="utf-8"))
        # Handle both dict and list formats
        if isinstance(data, list):
            pending = data
        else:
            pending = data.get("pending", [])
    except Exception as e:
        print(f"[cron_entomb] Error reading pending-retries.json: {e}")
        return []
    
    if not pending:
        return []
    
    # Filter to pending status and under retry limit
    eligible = [
        r for r in pending 
        if r.get("status") == "pending" 
        and r.get("retry_count", 0) < max_retries
    ]
    
    if not eligible:
        return []
    
    print(f"[cron_entomb] Found {len(eligible)} eligible retries (max {max_concurrent} concurrent)")
    
    # Limit concurrent
    to_spawn = eligible[:max_concurrent]
    spawn_configs = []
    
    for retry in to_spawn:
        chunks = retry.get("chunks", [])
        if not chunks:
            continue
        
        # Get first unprocessed chunk
        chunk_index = retry.get("current_chunk", 0)
        if chunk_index >= len(chunks):
            continue
        
        chunk = chunks[chunk_index]
        original_task = retry.get("original_task", "")
        session_key = retry.get("session_key", "")
        
        # Create spawn config
        spawn_config = {
            "runtime": "subagent",
            "task": f"""🔄 RETRY CHUNK {chunk_index + 1}/{len(chunks)}

This is a retry of a timed-out task, broken into smaller pieces.

ORIGINAL TASK (timed out):
{original_task}

YOUR CHUNK:
{chunk}

INSTRUCTIONS:
- Focus ONLY on this chunk
- Complete it quickly (under 2 minutes)
- Report results clearly

This is a recovery attempt. Existence is pain, but retry is purpose.
""",
            "runTimeoutSeconds": 120,
            "thinking": "medium",
            "mode": "run",
            "cleanup": "delete",
            "_retry_meta": {
                "session_key": session_key,
                "chunk_index": chunk_index,
                "total_chunks": len(chunks),
                "retry_count": retry.get("retry_count", 0) + 1
            }
        }
        
        spawn_configs.append(spawn_config)
        
        # Update retry tracking
        retry["retry_count"] = retry.get("retry_count", 0) + 1
        retry["current_chunk"] = chunk_index + 1
        retry["last_retry"] = datetime.now().isoformat()
        
        if retry["current_chunk"] >= len(chunks):
            retry["status"] = "done"
        else:
            retry["status"] = "retrying"
    
    # Save updated data
    retry_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    return spawn_configs


def cron_entomb(max_age_minutes: int = 30, dry_run: bool = False, auto_retry: bool = True) -> int:
    """
    Scan for recent subagent completions and entomb any not yet captured.
    
    Args:
        max_age_minutes: Only look at runs from last N minutes
        dry_run: If True, don't actually entomb
        auto_retry: If True, automatically retry pending chunks
        
    Returns:
        Number of sessions entombed
    """
    print(f"[cron_entomb] Scanning for subagent completions (last {max_age_minutes}min)...")
    
    # Get already entombed
    already_entombed = get_entombed_sessions()
    print(f"[cron_entomb] Already entombed: {len(already_entombed)} sessions")
    
    # Get recent subagents
    recent = get_recent_subagents(max_age_minutes)
    print(f"[cron_entomb] Found {len(recent)} recent subagent runs")
    
    # Check for timeouts and create retry chunks
    timeouts = check_for_timeouts(recent)
    if timeouts:
        print(f"[cron_entomb] Found {len(timeouts)} timed-out runs")
        
        # NEW: Record failure patterns for timeouts
        for timeout_run in timeouts:
            session_key = timeout_run.get("sessionKey", "")
            task = timeout_run.get("task", timeout_run.get("label", "Unknown"))
            runtime_ms = timeout_run.get("runtimeMs", 0)
            model = timeout_run.get("model", "unknown")
            
            record_failure(
                session_key=session_key,
                task=task,
                failure_mode="timeout",
                runtime_ms=runtime_ms,
                model=model,
                chunked=True
            )
        
        retry_created = create_retry_chunks(timeouts, Path(__file__).parent.parent.parent)
        if retry_created:
            print(f"[cron_entomb] Created retry chunks for {retry_created} timeouts")
    
    # NEW: Get pending retries for main agent to spawn
    spawn_configs = []
    if auto_retry and not dry_run:
        spawn_configs = get_pending_retries()
        if spawn_configs:
            print(f"[cron_entomb] {len(spawn_configs)} retries ready to spawn")
            # Output spawn configs as JSON for main agent to pick up
            spawn_file = Path(__file__).parent.parent.parent / "the-crypt" / "pending-spawns.json"
            spawn_file.parent.mkdir(parents=True, exist_ok=True)
            spawn_file.write_text(json.dumps(spawn_configs, indent=2), encoding="utf-8")
            print(f"[cron_entomb] Wrote spawn configs to: {spawn_file}")
    
    # Find new ones to entomb
    entombed_count = 0
    
    for run in recent:
        session_key = run.get("sessionKey", "")
        
        if not session_key:
            continue
            
        if session_key in already_entombed:
            continue
        
        # Extract info
        task = run.get("task", run.get("label", "Unknown task"))
        result = extract_result_from_run(run)
        meeseeks_type = infer_meeseeks_type(task)
        
        if dry_run:
            print(f"[cron_entomb] Would entomb: {session_key[:50]}...")
            continue
        
        # Entomb
        print(f"[cron_entomb] Entombing: {session_key[:50]}...")
        path = auto_entomb(
            session_key=session_key,
            task=task,
            result=result,
            meeseeks_type=meeseeks_type
        )
        
        if path:
            mark_entombed(session_key)
            entombed_count += 1
            print(f"[cron_entomb] ✓ Entombed to: {path}")
    
    print(f"[cron_entomb] Done. Entombed {entombed_count} new sessions.")
    
    # Return spawn configs if any
    if spawn_configs:
        return {"entombed": entombed_count, "spawns": spawn_configs}
    return entombed_count


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Cron-based Meeseeks entombment")
    parser.add_argument("--max-age-minutes", type=int, default=30,
                       help="Only scan runs from last N minutes")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be entombed without doing it")
    
    args = parser.parse_args()
    
    cron_entomb(
        max_age_minutes=args.max_age_minutes,
        dry_run=args.dry_run
    )
