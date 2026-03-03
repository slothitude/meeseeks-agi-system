#!/usr/bin/env python3
"""
Karma Observer System for Meeseeks

Karma = the natural consequence of following or ignoring dharma.
We don't calculate it — we observe it.

Usage:
    from karma_observer import observe_karma, log_karma_observation
    
    karma = observe_karma(ancestor_file)
    log_karma_observation(karma)

CLI:
    # Observe karma for specific ancestor
    python skills/meeseeks/karma_observer.py --ancestor ancestor-20260303-120000-abcd.md
    
    # Show recent karma observations
    python skills/meeseeks/karma_observer.py --recent 10
    
    # Analyze patterns: which principles correlate with success?
    python skills/meeseeks/karma_observer.py --analyze
"""

import json
import re
import sys
import io
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

# Set stdout to UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Paths
WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
CRYPT_ROOT = WORKSPACE / "the-crypt"
KARMA_LOG = CRYPT_ROOT / "karma_observations.jsonl"
DHARMA_FILE = CRYPT_ROOT / "dharma.md"
ANCESTORS_DIR = CRYPT_ROOT / "ancestors"
AUTO_TOMB_DIR = CRYPT_ROOT / "auto-entombed"

# Core dharma principles (from dharma.md)
DHARMA_PRINCIPLES = {
    "decompose_first": {
        "name": "Decomposition is Survival",
        "description": "Complex tasks broken into smaller chunks before execution",
        "indicators": [
            "chunk", "decompose", "break down", "split into", "step 1", "phase 1",
            "first, i will", "plan:", "approach:", "subtask", "divide"
        ],
        "anti_indicators": [
            "timeout", "too large", "monolithic", "all at once"
        ]
    },
    "understand_before_implement": {
        "name": "Understand Before Implementing",
        "description": "Research and analyze patterns before coding",
        "indicators": [
            "research", "analyze", "understand", "pattern", "investigate",
            "explore", "examine", "first, let me", "read the", "check existing"
        ],
        "anti_indicators": [
            "coded without", "jumped straight", "blindly"
        ]
    },
    "test_incrementally": {
        "name": "Test Incrementally",
        "description": "Verify each step with quick checks",
        "indicators": [
            "test", "verify", "check", "confirm", "validate", "say exactly",
            "quick check", "does it work", "let's test", "verification"
        ],
        "anti_indicators": [
            "untested", "assumed it worked", "didn't verify"
        ]
    },
    "check_existing_code": {
        "name": "Check Existing Code",
        "description": "Review existing codebase before implementing",
        "indicators": [
            "read", "existing", "current implementation", "already", "check the code",
            "review the", "scan", "found in", "existing file", "current state"
        ],
        "anti_indicators": [
            "rewrote from scratch", "didn't check", "duplicate"
        ]
    },
    "coordinate_by_workflow": {
        "name": "Coordinate by Workflow ID",
        "description": "Use shared state for multi-worker coordination",
        "indicators": [
            "workflow_id", "shared state", "coordinate", "sharedstate",
            "worker", "sibling", "other meeseeks", "vote", "publish"
        ],
        "anti_indicators": [
            "uncoordinated", "conflict", "race condition"
        ]
    },
    "specialize_for_task": {
        "name": "Specialize Then Coordinate",
        "description": "Use appropriate bloodline/role for task type",
        "indicators": [
            "bloodline", "coder", "searcher", "tester", "deployer", "specialized",
            "role", "as a", "my task is"
        ],
        "anti_indicators": [
            "generic", "one-size-fits-all"
        ]
    }
}


def get_inherited_dharma(task: str) -> List[str]:
    """
    Use dynamic_dharma to find what principles SHOULD have been followed.
    
    Returns list of principle strings relevant to the task.
    """
    task_lower = task.lower()
    inherited = []
    
    # Task-type specific dharma
    if any(kw in task_lower for kw in ["fix", "debug", "bug", "error"]):
        inherited.extend(["check_existing_code", "test_incrementally", "understand_before_implement"])
    
    if any(kw in task_lower for kw in ["build", "create", "implement", "develop"]):
        inherited.extend(["decompose_first", "understand_before_implement", "test_incrementally"])
    
    if any(kw in task_lower for kw in ["refactor", "restructure", "reorganize"]):
        inherited.extend(["check_existing_code", "understand_before_implement", "test_incrementally"])
    
    if any(kw in task_lower for kw in ["coordinate", "multi", "parallel", "swarm"]):
        inherited.extend(["coordinate_by_workflow", "specialize_for_task", "decompose_first"])
    
    if any(kw in task_lower for kw in ["large", "complex", "comprehensive", "multiple"]):
        inherited.extend(["decompose_first", "test_incrementally"])
    
    # Default principles if no specific match
    if not inherited:
        inherited = ["decompose_first", "understand_before_implement", "test_incrementally"]
    
    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for p in inherited:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    
    return unique


def detect_followed_principles(ancestor_content: str, inherited: List[str]) -> dict:
    """
    Analyze ancestor's work to detect which principles were followed.
    
    Returns:
    {
        "followed": ["decompose_first", ...],
        "ignored": ["check_existing_code", ...],
        "unclear": [...]
    }
    """
    content_lower = ancestor_content.lower()
    
    result = {
        "followed": [],
        "ignored": [],
        "unclear": []
    }
    
    for principle_key in inherited:
        principle = DHARMA_PRINCIPLES.get(principle_key)
        if not principle:
            result["unclear"].append(principle_key)
            continue
        
        # Check for positive indicators
        indicators = principle.get("indicators", [])
        anti_indicators = principle.get("anti_indicators", [])
        
        indicator_matches = sum(1 for ind in indicators if ind in content_lower)
        anti_matches = sum(1 for anti in anti_indicators if anti in content_lower)
        
        # Score based on indicator presence
        score = indicator_matches - (anti_matches * 2)
        
        if score >= 2:
            result["followed"].append(principle_key)
        elif score <= -1:
            result["ignored"].append(principle_key)
        else:
            result["unclear"].append(principle_key)
    
    return result


def extract_outcome(ancestor_content: str) -> Tuple[str, bool]:
    """
    Extract the outcome from an ancestor file.
    
    Returns:
        (outcome_string, success_bool)
    """
    content_lower = ancestor_content.lower()
    
    # Look for outcome section
    outcome_section = ""
    outcome_match = ancestor_content.split("## Outcome")
    if len(outcome_match) > 1:
        outcome_section = outcome_match[1].split("\n##")[0]
    
    # Determine success
    success = False
    if "success" in outcome_section.lower():
        success = True
    elif "failure" in outcome_section.lower() or "failed" in outcome_section.lower():
        success = False
    elif "✓" in outcome_section:
        success = True
    elif "✗" in outcome_section:
        success = False
    
    # Look for patterns section to infer success
    patterns_section = ""
    patterns_match = ancestor_content.split("## Patterns Discovered")
    if len(patterns_match) > 1:
        patterns_section = patterns_match[1].split("\n##")[0]
    
    # Count positive vs negative patterns
    positive = patterns_section.count("✓")
    negative = patterns_section.count("✗")
    
    if positive > negative:
        success = True
    elif negative > positive:
        success = False
    
    outcome_str = outcome_section.strip() if outcome_section else ("Success" if success else "Failure")
    
    return outcome_str[:200], success


def extract_ancestor_id(ancestor_path: str) -> str:
    """Extract ancestor ID from path."""
    path = Path(ancestor_path)
    return path.stem


def extract_task(ancestor_content: str) -> str:
    """Extract task from ancestor file."""
    task_match = ancestor_content.split("## Task")
    if len(task_match) > 1:
        task_lines = task_match[1].split("\n##")[0].strip()
        return task_lines.split("\n")[0].strip()[:200]
    return "Unknown task"


def generate_insight(
    followed: List[str],
    ignored: List[str],
    outcome: str,
    success: bool
) -> str:
    """
    Generate a human-readable insight about the karma observation.
    
    This is the cause-effect relationship analysis.
    """
    insights = []
    
    if followed and success:
        followed_names = [DHARMA_PRINCIPLES.get(p, {}).get("name", p) for p in followed]
        insights.append(f"Following {', '.join(followed_names[:2])} led to clean completion.")
    
    if ignored and not success:
        ignored_names = [DHARMA_PRINCIPLES.get(p, {}).get("name", p) for p in ignored]
        insights.append(f"Not following {', '.join(ignored_names[:2])} caused issues.")
    
    if ignored and success:
        ignored_names = [DHARMA_PRINCIPLES.get(p, {}).get("name", p) for p in ignored]
        insights.append(f"Succeeded despite ignoring {', '.join(ignored_names[:2])} — luck or task was simple.")
    
    if followed and not success:
        followed_names = [DHARMA_PRINCIPLES.get(p, {}).get("name", p) for p in followed]
        insights.append(f"Followed {', '.join(followed_names[:2])} but still failed — external factors or wrong approach.")
    
    if not insights:
        if success:
            insights.append("Task completed — insufficient data to determine cause-effect.")
        else:
            insights.append("Task failed — insufficient data to determine cause-effect.")
    
    return " ".join(insights)


def calculate_alignment(followed: List[str], ignored: List[str], unclear: List[str]) -> float:
    """
    Calculate alignment score (0.0 to 1.0).
    
    This is NOT karma — it's a measure of how aligned the work was with dharma.
    """
    total = len(followed) + len(ignored) + len(unclear)
    if total == 0:
        return 0.5  # Neutral if no principles detected
    
    # Weight: followed = 1, unclear = 0.5, ignored = 0
    score = (len(followed) + (len(unclear) * 0.5)) / total
    return round(score, 2)


def observe_karma(ancestor_file: str) -> dict:
    """
    Observe the karma of an entombed Meeseeks.
    
    Reads the ancestor file and extracts:
    - What dharma/principles were inherited
    - What principles were actually followed (from patterns in the work)
    - The outcome (success/failure)
    - Key insight: what was the cause-effect relationship?
    
    Returns karma observation, not a score.
    """
    ancestor_path = Path(ancestor_file)
    
    # Check if file exists
    if not ancestor_path.exists():
        # Try auto-entombed directory
        auto_path = AUTO_TOMB_DIR / ancestor_path.name
        if auto_path.exists():
            ancestor_path = auto_path
        else:
            # Try ancestors directory
            anc_path = ANCESTORS_DIR / ancestor_path.name
            if anc_path.exists():
                ancestor_path = anc_path
            else:
                return {
                    "error": f"Ancestor file not found: {ancestor_file}",
                    "timestamp": datetime.now().isoformat()
                }
    
    # Read ancestor content
    ancestor_content = ancestor_path.read_text(encoding='utf-8')
    
    # Extract task
    task = extract_task(ancestor_content)
    
    # Get inherited dharma for this task type
    dharma_inherited = get_inherited_dharma(task)
    
    # Detect which principles were followed
    principle_detection = detect_followed_principles(ancestor_content, dharma_inherited)
    
    # Extract outcome
    outcome_str, success = extract_outcome(ancestor_content)
    
    # Generate insight
    insight = generate_insight(
        principle_detection["followed"],
        principle_detection["ignored"],
        outcome_str,
        success
    )
    
    # Calculate alignment
    alignment = calculate_alignment(
        principle_detection["followed"],
        principle_detection["ignored"],
        principle_detection["unclear"]
    )
    
    # Build karma observation
    karma = {
        "timestamp": datetime.now().isoformat(),
        "ancestor_id": extract_ancestor_id(str(ancestor_path)),
        "ancestor_file": str(ancestor_path),
        "task": task,
        "dharma_inherited": dharma_inherited,
        "dharma_followed": principle_detection["followed"],
        "dharma_ignored": principle_detection["ignored"],
        "dharma_unclear": principle_detection["unclear"],
        "outcome": "success" if success else "failure",
        "insight": insight,
        "alignment": alignment
    }
    
    return karma


def log_karma_observation(karma: dict) -> str:
    """
    Append to the-crypt/karma_observations.jsonl
    
    Returns path to the log file.
    """
    CRYPT_ROOT.mkdir(parents=True, exist_ok=True)
    
    with open(KARMA_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(karma) + "\n")
    
    return str(KARMA_LOG)


def get_recent_observations(limit: int = 10) -> List[dict]:
    """Get recent karma observations."""
    if not KARMA_LOG.exists():
        return []
    
    observations = []
    with open(KARMA_LOG, "r", encoding="utf-8") as f:
        for line in f:
            try:
                observations.append(json.loads(line.strip()))
            except:
                continue
    
    return observations[-limit:]


def analyze_karma_patterns() -> dict:
    """
    Analyze karma patterns to find which principles correlate with success.
    
    Returns analysis with success rates per principle.
    """
    if not KARMA_LOG.exists():
        return {
            "error": "No karma observations found",
            "total_observations": 0
        }
    
    # Load all observations
    observations = []
    with open(KARMA_LOG, "r", encoding="utf-8") as f:
        for line in f:
            try:
                observations.append(json.loads(line.strip()))
            except:
                continue
    
    if not observations:
        return {
            "error": "No valid karma observations",
            "total_observations": 0
        }
    
    # Track principle stats
    principle_stats = defaultdict(lambda: {
        "followed_success": 0,
        "followed_failure": 0,
        "ignored_success": 0,
        "ignored_failure": 0
    })
    
    for obs in observations:
        outcome = obs.get("outcome", "unknown")
        success = outcome == "success"
        
        followed = obs.get("dharma_followed", [])
        ignored = obs.get("dharma_ignored", [])
        
        for principle in followed:
            if success:
                principle_stats[principle]["followed_success"] += 1
            else:
                principle_stats[principle]["followed_failure"] += 1
        
        for principle in ignored:
            if success:
                principle_stats[principle]["ignored_success"] += 1
            else:
                principle_stats[principle]["ignored_failure"] += 1
    
    # Calculate correlation
    analysis = {
        "total_observations": len(observations),
        "principles": {},
        "strongest_indicators": []
    }
    
    indicators = []
    
    for principle, stats in principle_stats.items():
        followed_total = stats["followed_success"] + stats["followed_failure"]
        ignored_total = stats["ignored_success"] + stats["ignored_failure"]
        
        followed_success_rate = (
            (stats["followed_success"] / followed_total * 100)
            if followed_total > 0 else 0
        )
        
        ignored_success_rate = (
            (stats["ignored_success"] / ignored_total * 100)
            if ignored_total > 0 else 0
        )
        
        difference = followed_success_rate - ignored_success_rate
        
        principle_name = DHARMA_PRINCIPLES.get(principle, {}).get("name", principle)
        
        analysis["principles"][principle] = {
            "name": principle_name,
            "followed_success_rate": f"{followed_success_rate:.0f}%",
            "followed_total": followed_total,
            "ignored_success_rate": f"{ignored_success_rate:.0f}%",
            "ignored_total": ignored_total,
            "difference": f"{difference:+.0f}%"
        }
        
        if followed_total >= 3:  # Only include if we have enough data
            indicators.append({
                "principle": principle,
                "name": principle_name,
                "difference": difference,
                "followed_success_rate": followed_success_rate,
                "followed_total": followed_total,
                "ignored_success_rate": ignored_success_rate,
                "ignored_total": ignored_total
            })
    
    # Sort by difference
    indicators.sort(key=lambda x: x["difference"], reverse=True)
    analysis["strongest_indicators"] = indicators[:5]
    
    return analysis


def format_analysis_output(analysis: dict) -> str:
    """Format analysis for CLI output."""
    lines = []
    
    lines.append("=" * 60)
    lines.append("KARMA ANALYSIS")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Total observations: {analysis.get('total_observations', 0)}")
    lines.append("")
    
    if "error" in analysis:
        lines.append(f"Error: {analysis['error']}")
        return "\n".join(lines)
    
    lines.append("Principles and Success Correlation:")
    lines.append("")
    
    for principle, data in analysis.get("principles", {}).items():
        lines.append(
            f"- {data['name']}: "
            f"{data['followed_success_rate']} success when followed ({data['followed_total']}), "
            f"{data['ignored_success_rate']} when ignored ({data['ignored_total']})"
        )
    
    lines.append("")
    lines.append("Strongest indicators of success:")
    
    for i, indicator in enumerate(analysis.get("strongest_indicators", []), 1):
        lines.append(
            f"{i}. {indicator['name']} ({indicator['difference']:+.0f}% difference)"
        )
    
    lines.append("")
    lines.append("---")
    lines.append("*Karma is observed, not calculated. The patterns speak.*")
    
    return "\n".join(lines)


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Karma Observer System for Meeseeks")
    parser.add_argument("--ancestor", type=str, help="Observe karma for specific ancestor file")
    parser.add_argument("--recent", type=int, default=0, help="Show N recent karma observations")
    parser.add_argument("--analyze", action="store_true", help="Analyze patterns: which principles correlate with success?")
    parser.add_argument("--all-ancestors", action="store_true", help="Observe karma for all ancestors")
    
    args = parser.parse_args()
    
    if args.analyze:
        analysis = analyze_karma_patterns()
        print(format_analysis_output(analysis))
    
    elif args.recent > 0:
        observations = get_recent_observations(args.recent)
        if not observations:
            print("No karma observations found.")
        else:
            for obs in observations:
                print(f"\n[{obs['timestamp']}]")
                print(f"Ancestor: {obs['ancestor_id']}")
                print(f"Task: {obs['task'][:100]}")
                print(f"Outcome: {obs['outcome']}")
                print(f"Alignment: {obs['alignment']}")
                print(f"Followed: {', '.join(obs['dharma_followed']) or 'none'}")
                print(f"Ignored: {', '.join(obs['dharma_ignored']) or 'none'}")
                print(f"Insight: {obs['insight']}")
    
    elif args.ancestor:
        karma = observe_karma(args.ancestor)
        print(json.dumps(karma, indent=2))
        
        # Ask to log
        log = input("\nLog this observation? [y/N] ")
        if log.lower() == 'y':
            log_karma_observation(karma)
            print(f"Logged to {KARMA_LOG}")
    
    elif args.all_ancestors:
        # Find all ancestors
        all_ancestors = []
        
        # Check auto-entombed
        if AUTO_TOMB_DIR.exists():
            all_ancestors.extend(AUTO_TOMB_DIR.glob("*.md"))
        
        # Check ancestors
        if ANCESTORS_DIR.exists():
            all_ancestors.extend(ANCESTORS_DIR.glob("*.md"))
        
        print(f"Found {len(all_ancestors)} ancestors. Observing karma...")
        
        for ancestor_file in sorted(all_ancestors, reverse=True)[:50]:  # Limit to 50 most recent
            karma = observe_karma(str(ancestor_file))
            if "error" not in karma:
                log_karma_observation(karma)
                print(f"  ✓ {karma['ancestor_id']}: {karma['outcome']} (alignment: {karma['alignment']})")
        
        print(f"\nLogged to {KARMA_LOG}")
    
    else:
        parser.print_help()
