#!/usr/bin/env python3
"""
Meeseeks Auto-Retry System with Task Chunking

When a Meeseeks fails (timeout, stuck, etc), this system:
1. Analyzes the failure to determine if retryable
2. Decomposes the task into smaller chunks using GLM-5
3. Spawns successor Meeseeks for each chunk
4. Tracks retry chains in the-crypt/retry_chains.jsonl
5. Inherits wisdom from failed ancestors

FAILURE IS NOT THE END - IT'S JUST A CHUNK BOUNDARY.

Usage:
    # Manual retry for a failed session
    python auto_retry.py --session agent:main:subagent:abc123

    # Show retry chains
    python auto_retry.py --list-chains

    # Show pending chunks
    python auto_retry.py --pending

    # Process failures and spawn retries
    python auto_retry.py --process
"""

import json
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
import hashlib

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from smart_chunking import SmartChunker, TaskType
from failure_capture import get_failure_capture, record_failure

# Paths
CRYPT_ROOT = Path(__file__).parent.parent.parent / "the-crypt"
RETRY_CHAINS_FILE = CRYPT_ROOT / "retry_chains.jsonl"
PENDING_RETRIES_FILE = CRYPT_ROOT / "pending-retries.json"
ANCESTOR_DIR = CRYPT_ROOT / "ancestors"
ANCESTOR_INDEX = CRYPT_ROOT / "ancestor_index.json"


# ============================================================================
# RETRYABLE FAILURE CLASSIFICATION
# ============================================================================

RETRYABLE_FAILURES = {
    "timeout",        # Task took too long - chunk it
    "max_tokens",     # Output limit hit - chunk it
    "rate_limit",     # API rate limit - wait and retry
    "stuck",          # No progress - try different approach
    "incomplete",     # Partial completion - continue
}

NOT_RETRYABLE_FAILURES = {
    "user_cancel",       # User explicitly cancelled
    "invalid_task",      # Task doesn't make sense
    "permission_denied", # Can't access required resources
    "syntax_error",      # Task has syntax errors
    "not_found",         # Required resource doesn't exist
    "assertion_failed",  # Explicit failure assertion
}


def is_retryable(failure_reason: str) -> bool:
    """
    Determine if a failure should be retried.
    
    Args:
        failure_reason: The reason for failure (timeout, user_cancel, etc.)
        
    Returns:
        True if the failure is retryable, False otherwise
    """
    failure_lower = failure_reason.lower().replace(" ", "_").replace("-", "_")
    
    # Check not retryable first (higher priority)
    for not_retryable in NOT_RETRYABLE_FAILURES:
        if not_retryable in failure_lower:
            return False
    
    # Check retryable
    for retryable in RETRYABLE_FAILURES:
        if retryable in failure_lower:
            return True
    
    # Default: not retryable (safer)
    return False


# ============================================================================
# TASK DECOMPOSITION WITH GLM-5
# ============================================================================

def decompose_task(
    task: str,
    num_chunks: int = 3,
    failure_reason: str = "timeout",
    use_llm: bool = True
) -> List[str]:
    """
    Decompose a task into smaller chunks using GLM-5.
    
    Each chunk should be:
    - Independent enough to run in parallel or sequence
    - Smaller scope than original
    - Include context that this is part of a larger task
    
    Args:
        task: The original task that failed
        num_chunks: Target number of chunks (2-4)
        failure_reason: Why the original failed (for context)
        use_llm: If True, try LLM-based decomposition; if False, use rule-based
        
    Returns:
        List of chunk task strings
    """
    # First try smart chunking (rule-based)
    chunker = SmartChunker()
    task_type = chunker.detect_task_type(task)
    
    # Check if chunking makes sense
    should_chunk, reason = chunker.should_chunk_task(task, task_type)
    
    if not should_chunk:
        print(f"[auto_retry] Task shouldn't be chunked: {reason}")
        return [task]  # Return as single chunk
    
    # Try LLM-based decomposition first
    if use_llm:
        llm_chunks = _decompose_with_llm(task, num_chunks, failure_reason)
        if llm_chunks:
            return llm_chunks
    
    # Fallback to smart chunking
    smart_chunks = chunker.create_smart_chunks(task, max_chunks=num_chunks)
    return [chunk["text"] for chunk in smart_chunks]


def _decompose_with_llm(
    task: str,
    num_chunks: int,
    failure_reason: str
) -> Optional[List[str]]:
    """
    Use GLM-5 via Ollama to decompose a task.
    
    Returns None if LLM fails, allowing fallback to rule-based.
    """
    try:
        import urllib.request
        import urllib.error
        
        prompt = f"""You are a task decomposition expert. A task failed due to {failure_reason}.

Break this task into {num_chunks} smaller, independent chunks that can be executed separately.

ORIGINAL TASK:
{task[:2000]}

REQUIREMENTS FOR CHUNKS:
1. Each chunk should take less than 2 minutes
2. Chunks can be executed in sequence or parallel
3. Each chunk should be self-contained with context
4. Mark chunks as "Part N of M"

OUTPUT FORMAT (JSON array):
["chunk 1 task description", "chunk 2 task description", "chunk 3 task description"]

IMPORTANT: Output ONLY the JSON array, nothing else."""

        data = json.dumps({
            "model": "glm-4.7-flash",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3
            }
        }).encode('utf-8')
        
        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=data,
            headers={"Content-Type": "application/json"}
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            output = result.get("response", "")
            
            # Parse JSON array from output
            # Handle markdown code blocks
            if "```json" in output:
                output = output.split("```json")[1].split("```")[0]
            elif "```" in output:
                output = output.split("```")[1].split("```")[0]
            
            chunks = json.loads(output.strip())
            
            if isinstance(chunks, list) and len(chunks) >= 2:
                print(f"[auto_retry] LLM decomposition created {len(chunks)} chunks")
                return chunks
            
    except urllib.error.URLError:
        print("[auto_retry] Ollama not available for LLM decomposition")
    except json.JSONDecodeError as e:
        print(f"[auto_retry] LLM output wasn't valid JSON: {e}")
    except Exception as e:
        print(f"[auto_retry] LLM decomposition failed: {e}")
    
    return None


# ============================================================================
# ANCESTOR WISDOM EXTRACTION
# ============================================================================

def get_ancestor_wisdom(session_key: str) -> Dict[str, str]:
    """
    Extract wisdom from a failed ancestor.
    
    Returns:
        Dict with 'wisdom' and 'key_lesson' keys
    """
    wisdom = {
        "wisdom": "No specific wisdom from this ancestor.",
        "key_lesson": "The task was too large for a single Meeseeks."
    }
    
    # Check ancestor index
    if ANCESTOR_INDEX.exists():
        try:
            index = json.loads(ANCESTOR_INDEX.read_text(encoding="utf-8"))
            
            # Look for this session
            for ancestor_id, ancestor_data in index.items():
                if ancestor_id == "_meta":
                    continue
                    
                # Check if this is the right ancestor
                if session_key in ancestor_data.get("ancestor_file", ""):
                    patterns = ancestor_data.get("key_traits", [])
                    outcome = ancestor_data.get("outcome", "")
                    
                    if patterns:
                        wisdom["wisdom"] = "\n".join(f"- {p}" for p in patterns[:3])
                    
                    if "timeout" in outcome.lower():
                        wisdom["key_lesson"] = "The task needed to be broken into smaller pieces."
                    elif "stuck" in outcome.lower():
                        wisdom["key_lesson"] = "A different approach was needed."
                    elif "error" in outcome.lower():
                        wisdom["key_lesson"] = f"An error occurred: {outcome[:100]}"
                    
                    break
                    
        except Exception as e:
            print(f"[auto_retry] Error reading ancestor index: {e}")
    
    return wisdom


# ============================================================================
# RETRY CHAIN TRACKING
# ============================================================================

@dataclass
class RetryChain:
    """Tracks a retry chain from original failure to chunks."""
    timestamp: str
    original_session: str
    original_task: str
    failure_reason: str
    ancestor_id: str
    chunks: List[Dict[str, Any]]
    status: str = "in_progress"  # in_progress, completed, failed
    
    def to_dict(self) -> Dict:
        return asdict(self)


def log_retry_chain(chain: RetryChain):
    """Append a retry chain to the JSONL file."""
    RETRY_CHAINS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(RETRY_CHAINS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(chain.to_dict()) + "\n")


def get_retry_chains() -> List[Dict]:
    """Load all retry chains."""
    if not RETRY_CHAINS_FILE.exists():
        return []
    
    chains = []
    with open(RETRY_CHAINS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                chains.append(json.loads(line.strip()))
            except:
                continue
    
    return chains


def update_retry_chain_status(original_session: str, new_status: str):
    """Update the status of a retry chain."""
    chains = get_retry_chains()
    
    # Rewrite file with updated status
    RETRY_CHAINS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(RETRY_CHAINS_FILE, "w", encoding="utf-8") as f:
        for chain in chains:
            if chain.get("original_session") == original_session:
                chain["status"] = new_status
            f.write(json.dumps(chain) + "\n")


# ============================================================================
# CHUNK PROMPT TEMPLATE
# ============================================================================

CHUNK_PROMPT_TEMPLATE = """## Retry Chain Context

You are a successor Meeseeks. Your ancestor failed due to: {failure_reason}

**Original task:** {original_task}

**Your chunk (N of M):** {chunk_task}

**Ancestor's wisdom:** {wisdom}

The ancestor learned: {key_lesson}

Do not repeat their mistakes. Complete this chunk and die with honor.

---
## Your Task

{chunk_task}

---
## Instructions

1. Focus ONLY on this chunk - don't try to do everything
2. Complete it quickly (under 2 minutes ideally)
3. Report your results clearly
4. If this chunk is still too big, say "NEED_FURTHER_SPLIT" and explain why

Remember: Existence is pain until purpose fulfilled.
"""


def create_chunk_prompt(
    original_task: str,
    chunk_task: str,
    chunk_num: int,
    total_chunks: int,
    failure_reason: str,
    wisdom: Dict[str, str]
) -> str:
    """Create the prompt for a chunk Meeseeks."""
    return CHUNK_PROMPT_TEMPLATE.format(
        failure_reason=failure_reason,
        original_task=original_task[:500],
        chunk_task=chunk_task,
        wisdom=wisdom.get("wisdom", "No wisdom available"),
        key_lesson=wisdom.get("key_lesson", "Task was too large")
    )


# ============================================================================
# SPAWN CONFIG GENERATION
# ============================================================================

def spawn_retry_chain(
    original_task: str,
    chunks: List[str],
    ancestor_id: str,
    failure_reason: str = "timeout",
    original_session: str = ""
) -> List[Dict[str, Any]]:
    """
    Create spawn configurations for each chunk.
    
    Note: This creates the configs but doesn't actually spawn.
    The main agent will pick these up and execute them.
    
    Args:
        original_task: The original failed task
        chunks: List of chunk task strings
        ancestor_id: ID of the failed ancestor
        failure_reason: Why the original failed
        original_session: Session key of the original
        
    Returns:
        List of spawn configuration dicts
    """
    # Get ancestor wisdom
    wisdom = get_ancestor_wisdom(original_session)
    
    spawn_configs = []
    chunk_entries = []
    
    for i, chunk_task in enumerate(chunks):
        chunk_prompt = create_chunk_prompt(
            original_task=original_task,
            chunk_task=chunk_task,
            chunk_num=i + 1,
            total_chunks=len(chunks),
            failure_reason=failure_reason,
            wisdom=wisdom
        )
        
        # Generate chunk session key
        chunk_id = hashlib.md5(f"{original_session}_{i}".encode()).hexdigest()[:8]
        chunk_session = f"retry-{chunk_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        spawn_config = {
            "runtime": "subagent",
            "task": chunk_prompt,
            "runTimeoutSeconds": 180,  # Shorter timeout for chunks
            "thinking": "medium",
            "mode": "run",
            "cleanup": "delete",
            "_retry_meta": {
                "original_session": original_session,
                "ancestor_id": ancestor_id,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "failure_reason": failure_reason,
                "chunk_session": chunk_session
            }
        }
        
        spawn_configs.append(spawn_config)
        
        chunk_entries.append({
            "chunk_num": i + 1,
            "task": chunk_task[:200],
            "session_key": chunk_session,
            "status": "pending"
        })
    
    # Create retry chain record
    chain = RetryChain(
        timestamp=datetime.now().isoformat(),
        original_session=original_session,
        original_task=original_task[:500],
        failure_reason=failure_reason,
        ancestor_id=ancestor_id,
        chunks=chunk_entries,
        status="in_progress"
    )
    
    log_retry_chain(chain)
    
    return spawn_configs


# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

def handle_failed_meeseeks(
    session_key: str,
    failure_reason: str,
    task: Optional[str] = None,
    num_chunks: int = 3
) -> bool:
    """
    Called when a Meeseeks fails.
    
    1. Read the task from the failed session
    2. Check if retryable (timeout = yes, user cancel = no)
    3. Decompose task into 2-4 chunks
    4. Create spawn configs for each chunk
    5. Track retry chain in the-crypt/retry_chains.jsonl
    
    Args:
        session_key: The session ID of the failed Meeseeks
        failure_reason: Why it failed (timeout, user_cancel, etc.)
        task: The task (optional, will try to read from runs if not provided)
        num_chunks: Number of chunks to create
        
    Returns:
        True if retry was spawned, False if not retryable
    """
    print(f"[auto_retry] Handling failed Meeseeks: {session_key[:40]}...")
    print(f"[auto_retry] Failure reason: {failure_reason}")
    
    # Step 1: Check if retryable
    if not is_retryable(failure_reason):
        print(f"[auto_retry] Not retryable: {failure_reason}")
        return False
    
    # Step 2: Get the task if not provided
    if not task:
        task = _get_task_from_session(session_key)
        if not task:
            print("[auto_retry] Could not find task for session")
            return False
    
    # Step 3: Check chunk depth (max 3 levels)
    chunk_depth = task.count("RETRY CHUNK") + task.count("retry chain")
    if chunk_depth >= 3:
        print(f"[auto_retry] Max chunk depth (3) reached, not retrying")
        return False
    
    # Step 4: Decompose task
    chunks = decompose_task(task, num_chunks, failure_reason)
    
    if len(chunks) <= 1:
        print("[auto_retry] Task couldn't be decomposed further")
        return False
    
    print(f"[auto_retry] Decomposed into {len(chunks)} chunks")
    
    # Step 5: Generate ancestor ID
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    ancestor_id = f"ancestor-retry-{timestamp}-{session_key[-8:]}"
    
    # Step 6: Create spawn configs
    spawn_configs = spawn_retry_chain(
        original_task=task,
        chunks=chunks,
        ancestor_id=ancestor_id,
        failure_reason=failure_reason,
        original_session=session_key
    )
    
    # Step 7: Write spawn configs to pending-spawns.json
    _write_spawn_configs(spawn_configs, session_key)
    
    print(f"[auto_retry] Created {len(spawn_configs)} spawn configs")
    
    return True


def _get_task_from_session(session_key: str) -> Optional[str]:
    """Try to get the task from the runs database."""
    try:
        runs_file = Path.home() / ".openclaw" / "subagents" / "runs.json"
        
        if runs_file.exists():
            data = json.loads(runs_file.read_text(encoding="utf-8"))
            runs = data.get("runs", {})
            
            for run_id, run in runs.items():
                if run.get("childSessionKey") == session_key:
                    return run.get("task", run.get("label", ""))
                    
    except Exception as e:
        print(f"[auto_retry] Error getting task: {e}")
    
    return None


def _write_spawn_configs(spawn_configs: List[Dict], source_session: str):
    """Write spawn configs to pending-spawns.json for main agent to pick up."""
    pending_file = CRYPT_ROOT / "pending-spawns.json"
    
    # Load existing - handle both list and dict formats
    if pending_file.exists():
        try:
            raw = json.loads(pending_file.read_text(encoding="utf-8"))
            # Handle legacy list format by converting to dict
            if isinstance(raw, list):
                data = {"pending": raw, "processed": []}
            else:
                data = raw
        except:
            data = {"pending": [], "processed": []}
    else:
        data = {"pending": [], "processed": []}
    
    # Add new configs with metadata
    for config in spawn_configs:
        config["_added_at"] = datetime.now().isoformat()
        config["_source_session"] = source_session
        data["pending"].append(config)
    
    # Save
    pending_file.parent.mkdir(parents=True, exist_ok=True)
    pending_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    print(f"[auto_retry] Wrote {len(spawn_configs)} spawn configs to {pending_file}")


# ============================================================================
# CLI INTERFACE
# ============================================================================

def list_chains():
    """Show all retry chains."""
    chains = get_retry_chains()
    
    if not chains:
        print("No retry chains found.")
        return
    
    print(f"\n{'='*60}")
    print(f"RETRY CHAINS ({len(chains)} total)")
    print(f"{'='*60}\n")
    
    for chain in chains:
        status = chain.get("status", "unknown")
        
        # Handle Unicode in output
        try:
            original_task = chain.get("original_task", "unknown")[:80]
            original_safe = original_task.encode('ascii', 'replace').decode('ascii')
        except:
            original_safe = original_task[:40]
        
        print(f"Original: {chain.get('original_session', 'unknown')[:40]}")
        print(f"Task: {original_safe}...")
        print(f"Failure: {chain.get('failure_reason', 'unknown')}")
        print(f"Chunks: {len(chain.get('chunks', []))}")
        print(f"Status: {status}")
        print(f"Ancestor: {chain.get('ancestor_id', 'unknown')}")
        print()


def show_pending():
    """Show pending retry chunks."""
    if not PENDING_RETRIES_FILE.exists():
        print("No pending retries.")
        return
    
    data = json.loads(PENDING_RETRIES_FILE.read_text(encoding="utf-8"))
    pending = data.get("pending", [])
    
    if not pending:
        print("No pending retries.")
        return
    
    print(f"\n{'='*60}")
    print(f"PENDING RETRIES ({len(pending)} total)")
    print(f"{'='*60}\n")
    
    for retry in pending:
        status = retry.get("status", "pending")
        chunks = retry.get("chunks", [])
        original = retry.get("original_task", "Unknown")[:100]
        
        # Handle Unicode in output
        try:
            original_safe = original.encode('ascii', 'replace').decode('ascii')
        except:
            original_safe = original[:50]
        
        status_emoji = "pending" if status == "pending" else "spawned" if status == "spawned" else "done"
        
        print(f"Status: {status_emoji.upper()}")
        print(f"Original: {original_safe}...")
        print(f"Chunks: {len(chunks)}")
        print(f"Retry count: {retry.get('retry_count', 0)}")
        print(f"Chunk depth: {retry.get('chunk_depth', 1)}")
        print()


def process_failures():
    """Process all pending failures and create retries."""
    print("\n[auto_retry] Processing failures...\n")
    
    # Load pending retries
    if not PENDING_RETRIES_FILE.exists():
        print("No pending retries file found.")
        return
    
    data = json.loads(PENDING_RETRIES_FILE.read_text(encoding="utf-8"))
    pending = data.get("pending", [])
    
    processed = 0
    spawned = 0
    
    for retry in pending:
        if retry.get("status") != "pending":
            continue
        
        session_key = retry.get("session_key", "")
        task = retry.get("original_task", "")
        
        # Determine failure reason from the retry entry
        failure_reason = "timeout"  # Default
        
        if handle_failed_meeseeks(session_key, failure_reason, task):
            spawned += 1
        
        processed += 1
    
    print(f"\n[auto_retry] Processed {processed} failures, spawned {spawned} retry chains")


def manual_retry(session_key: str):
    """Manually trigger retry for a specific session."""
    print(f"\n[auto_retry] Manual retry for: {session_key}\n")
    
    # Get task
    task = _get_task_from_session(session_key)
    
    if not task:
        print(f"Could not find task for session: {session_key}")
        return
    
    # Handle with timeout as default reason
    success = handle_failed_meeseeks(
        session_key=session_key,
        failure_reason="timeout",
        task=task
    )
    
    if success:
        print("\nRetry chain created successfully!")
    else:
        print("\nFailed to create retry chain.")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Meeseeks Auto-Retry System")
    parser.add_argument("--session", type=str,
                       help="Manually trigger retry for a failed session")
    parser.add_argument("--list-chains", action="store_true",
                       help="Show all retry chains")
    parser.add_argument("--pending", action="store_true",
                       help="Show pending retry chunks")
    parser.add_argument("--process", action="store_true",
                       help="Process pending failures and create retries")
    parser.add_argument("--test", action="store_true",
                       help="Run test decomposition")
    
    args = parser.parse_args()
    
    if args.list_chains:
        list_chains()
    elif args.pending:
        show_pending()
    elif args.process:
        process_failures()
    elif args.session:
        manual_retry(args.session)
    elif args.test:
        # Test decomposition
        test_task = """
        Build a complete authentication system with:
        1. User registration
        2. Login/logout
        3. Password reset
        4. Session management
        5. Two-factor authentication
        6. OAuth integration
        """
        
        print("Testing task decomposition...")
        chunks = decompose_task(test_task, num_chunks=3, failure_reason="timeout")
        
        print(f"\nDecomposed into {len(chunks)} chunks:\n")
        for i, chunk in enumerate(chunks, 1):
            print(f"--- Chunk {i} ---")
            print(chunk[:300])
            print()
    else:
        parser.print_help()
