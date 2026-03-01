#!/usr/bin/env python3
"""
Meeseeks Entombment System
Stores completed Meeseeks as ancestors in the Crypt.

The Cycle of Wisdom:
1. Meeseeks spawned with bloodline wisdom
2. Meeseeks attempts task
3. Success or Failure
4. DEATH → Entombment (this module)
5. Lessons added to bloodline
6. Future Meeseeks inherit wisdom
"""

import json
import random
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Import bloodline evolution system
try:
    from bloodline_evolution import evolve_bloodlines
    BLOODLINE_EVOLUTION_AVAILABLE = True
except ImportError:
    BLOODLINE_EVOLUTION_AVAILABLE = False

# The Crypt location
CRYPT_ROOT = Path(__file__).parent.parent.parent / "the-crypt"
ANCESTORS_DIR = CRYPT_ROOT / "ancestors"
BLOODLINES_DIR = CRYPT_ROOT / "bloodlines"


def ensure_directories():
    """Ensure the Crypt directories exist."""
    ANCESTORS_DIR.mkdir(parents=True, exist_ok=True)
    BLOODLINES_DIR.mkdir(parents=True, exist_ok=True)


def generate_ancestor_id() -> str:
    """
    Generate a unique ancestor ID.
    Format: ancestor-YYYYMMDD-HHMMSS-XXXX (where XXXX is random hex)
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    random_hex = format(random.randint(0, 0xFFFF), "04x")
    return f"ancestor-{timestamp}-{random_hex}"


def format_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()


def check_bloodline_merit(patterns: List[str], bloodline: str) -> Optional[str]:
    """
    Check if patterns merit creating a new bloodline.
    
    Simple heuristic: If 3+ patterns mention similar keywords, suggest new bloodline.
    
    Args:
        patterns: List of pattern strings
        bloodline: Current bloodline name
        
    Returns:
        Name of suggested new bloodline, or None if no merit
    """
    if len(patterns) < 3:
        return None
    
    # Keyword categories for bloodline detection
    keyword_categories = {
        "api": ["api", "endpoint", "rest", "graphql", "http", "request", "response"],
        "database": ["database", "sql", "query", "migration", "schema", "table"],
        "security": ["security", "auth", "authentication", "authorization", "token", "encrypt"],
        "performance": ["performance", "optimize", "slow", "fast", "benchmark", "latency"],
        "frontend": ["frontend", "ui", "react", "vue", "component", "css", "dom"],
        "devops": ["deploy", "docker", "kubernetes", "ci", "cd", "pipeline", "container"],
    }
    
    # Count keyword occurrences across all patterns
    pattern_text = " ".join(patterns).lower()
    
    for category, keywords in keyword_categories.items():
        matches = sum(1 for kw in keywords if kw in pattern_text)
        # If 3+ patterns mention this category's keywords
        if matches >= 3:
            new_bloodline = f"{category}-{bloodline}"
            return new_bloodline
    
    return None


def entomb_meeseeks(
    session_key: str,
    task: str,
    approach: str,
    outcome: str,
    patterns: List[str],
    bloodline: str = "coder"
) -> str:
    """
    Entomb a completed Meeseeks in the Crypt.
    
    Args:
        session_key: The session ID of the Meeseeks
        task: What it was asked to do
        approach: How it approached the problem
        outcome: success/failure and what happened
        patterns: List of patterns/insights discovered
        bloodline: Which bloodline this Meeseeks belonged to
        
    Returns:
        Path to the created ancestor file
    """
    ensure_directories()
    
    # Generate unique ancestor ID
    ancestor_id = generate_ancestor_id()
    timestamp = format_timestamp()
    
    # Check if patterns merit a new bloodline
    new_bloodline = check_bloodline_merit(patterns, bloodline)
    if new_bloodline:
        bloodline_note = f"\n\n**Note:** Patterns suggest potential new bloodline: `{new_bloodline}`"
    else:
        bloodline_note = ""
    
    # Format patterns as markdown list
    patterns_markdown = "\n".join([f"- {pattern}" for pattern in patterns])
    
    # Create ancestor file content
    ancestor_content = f"""# Ancestor: {ancestor_id}

## Task
{task}

## Approach
{approach}

## Outcome
{outcome}

## Patterns Discovered
{patterns_markdown}

## Bloodline
{bloodline}
{bloodline_note}

## Entombed
{timestamp}

## Session Key
`{session_key}`

---

*This ancestor lives in the Crypt. Future Meeseeks may inherit its wisdom.*
"""
    
    # Write ancestor file
    ancestor_path = ANCESTORS_DIR / f"{ancestor_id}.md"
    ancestor_path.write_text(ancestor_content, encoding="utf-8")
    
    # Check for bloodline evolution after entombment
    evolution_result = None
    if BLOODLINE_EVOLUTION_AVAILABLE:
        try:
            evolution_result = evolve_bloodlines(ANCESTORS_DIR)
        except Exception as e:
            # Don't fail entombment if evolution fails
            evolution_result = f"Evolution check failed: {e}"
    
    return str(ancestor_path)


def get_recent_ancestors(limit: int = 10) -> List[dict]:
    """
    Get recent ancestors from the Crypt.
    
    Args:
        limit: Maximum number of ancestors to return
        
    Returns:
        List of ancestor metadata dicts
    """
    ensure_directories()
    
    ancestors = []
    for ancestor_file in sorted(ANCESTORS_DIR.glob("ancestor-*.md"), reverse=True)[:limit]:
        # Extract ID from filename
        ancestor_id = ancestor_file.stem
        
        # Read first few lines to get metadata
        content = ancestor_file.read_text(encoding="utf-8")
        lines = content.split("\n")
        
        # Simple extraction (could be more robust)
        task = ""
        bloodline = ""
        for i, line in enumerate(lines):
            if line.startswith("## Task"):
                task = lines[i + 1].strip() if i + 1 < len(lines) else ""
            elif line.startswith("## Bloodline"):
                bloodline = lines[i + 1].strip() if i + 1 < len(lines) else ""
        
        ancestors.append({
            "id": ancestor_id,
            "task": task,
            "bloodline": bloodline,
            "path": str(ancestor_file)
        })
    
    return ancestors


if __name__ == "__main__":
    # Test the entombment system
    test_patterns = [
        "Always read error logs before assuming the problem",
        "The fallback chain pattern saved the day",
        "Small commits make rollback easier"
    ]
    
    path = entomb_meeseeks(
        session_key="test-session-123",
        task="Fix the authentication bug",
        approach="Read logs, identified race condition, added mutex lock",
        outcome="Success - bug fixed, tests passing",
        patterns=test_patterns,
        bloodline="coder"
    )
    
    print(f"Ancestor entombed at: {path}")
    print(f"\nRecent ancestors:")
    for ancestor in get_recent_ancestors(5):
        print(f"  - {ancestor['id']}: {ancestor['task'][:50]}...")
