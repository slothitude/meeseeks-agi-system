#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bloodline Evolution System
Dynamic bloodline creation for emerging patterns in the Meeseeks ecosystem.

STEP 4: DYNAMIC BLOODLINES
- Detects emerging patterns from ancestors
- Creates new bloodlines when patterns crystallize
- Routes tasks to the most appropriate bloodline

The Atman watches. New bloodlines emerge from the wisdom of the dead.
"""

import re
import sys
import io
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Tuple
from collections import Counter

# Set stdout to UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Crypt locations
CRYPT_ROOT = Path("C:/Users/aaron/.openclaw/workspace/the-crypt")
ANCESTORS_DIR = CRYPT_ROOT / "ancestors"
BLOODLINES_DIR = CRYPT_ROOT / "bloodlines"

# Core bloodlines that always exist
CORE_BLOODLINES = ["coder", "searcher", "tester", "deployer", "desperate", "brahman"]

# Minimum ancestors required before considering new bloodline
MIN_ANCESTORS_FOR_EMERGENCE = 3

# Pattern keywords for bloodline detection
BLOODLINE_KEYWORDS = {
    "api": ["api", "endpoint", "rest", "graphql", "http", "request", "response", "json", "swagger", "openapi"],
    "database": ["database", "sql", "query", "migration", "schema", "table", "postgres", "mysql", "sqlite", "mongodb"],
    "security": ["security", "auth", "authentication", "authorization", "token", "encrypt", "jwt", "oauth", "ssl", "tls"],
    "performance": ["performance", "optimize", "slow", "fast", "benchmark", "latency", "throughput", "cache", "memory"],
    "frontend": ["frontend", "ui", "react", "vue", "component", "css", "dom", "javascript", "typescript", "html"],
    "devops": ["deploy", "docker", "kubernetes", "ci", "cd", "pipeline", "container", "k8s", "helm", "terraform"],
    "network": ["network", "tcp", "udp", "socket", "dns", "ip", "firewall", "proxy", "vpn", "routing"],
    "testing": ["test", "unit", "integration", "e2e", "mock", "stub", "fixture", "coverage", "assertion"],
    "debugging": ["debug", "trace", "log", "error", "exception", "crash", "breakpoint", "stack", "traceback"],
    "refactor": ["refactor", "clean", "restructure", "rename", "extract", "simplify", "debt", "technical"],
    "documentation": ["document", "readme", "comment", "docstring", "wiki", "guide", "tutorial", "explain"],
}


def extract_patterns_from_ancestor(ancestor_path: Path) -> List[str]:
    """
    Extract patterns from an ancestor file.
    
    Args:
        ancestor_path: Path to the ancestor markdown file
        
    Returns:
        List of pattern strings found in the ancestor
    """
    if not ancestor_path.exists():
        return []
    
    content = ancestor_path.read_text(encoding='utf-8')
    patterns = []
    
    # Find the "Patterns Discovered" section
    patterns_match = re.search(
        r'## Patterns Discovered\s*\n(.*?)(?=\n##|\Z)',
        content,
        re.DOTALL
    )
    
    if patterns_match:
        for line in patterns_match.group(1).split('\n'):
            line = line.strip()
            # Match list items
            if line.startswith('- '):
                patterns.append(line[2:])
    
    return patterns


def extract_bloodline_from_ancestor(ancestor_path: Path) -> str:
    """
    Extract the bloodline from an ancestor file.
    
    Args:
        ancestor_path: Path to the ancestor markdown file
        
    Returns:
        Bloodline name (defaults to "coder" if not found)
    """
    if not ancestor_path.exists():
        return "coder"
    
    content = ancestor_path.read_text(encoding='utf-8')
    
    # Find the "Bloodline" section
    bloodline_match = re.search(
        r'## Bloodline\s*\n([^\n]+)',
        content
    )
    
    if bloodline_match:
        bloodline = bloodline_match.group(1).strip()
        # Remove any note annotations
        if bloodline.startswith("*Note:*"):
            return "coder"
        return bloodline.lower()
    
    return "coder"


def categorize_patterns(patterns: List[str]) -> Dict[str, int]:
    """
    Categorize patterns by bloodline keyword categories.
    
    Args:
        patterns: List of pattern strings
        
    Returns:
        Dict mapping category names to match counts
    """
    category_counts = Counter()
    
    for pattern in patterns:
        pattern_lower = pattern.lower()
        for category, keywords in BLOODLINE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in pattern_lower:
                    category_counts[category] += 1
                    break  # Count each pattern only once per category
    
    return dict(category_counts)


def get_existing_bloodlines() -> List[str]:
    """
    Get list of all existing bloodlines (core + dynamic).
    
    Returns:
        List of bloodline names
    """
    bloodlines = list(CORE_BLOODLINES)
    
    # Check for dynamic bloodlines
    if BLOODLINES_DIR.exists():
        for bloodline_file in BLOODLINES_DIR.glob("*-lineage.md"):
            name = bloodline_file.stem.replace("-lineage", "")
            if name not in bloodlines:
                bloodlines.append(name)
    
    return bloodlines


def check_bloodline_emergence(ancestors_dir: Path) -> Optional[dict]:
    """
    Check if ancestors show patterns that merit a new bloodline.
    
    A new bloodline emerges when:
    - 3+ ancestors show similar specialized patterns
    - The pattern is DISTINCT from existing bloodlines
    - The pattern has predictive value
    
    Args:
        ancestors_dir: Path to the ancestors directory
        
    Returns:
        None if no new bloodline needed
        Dict with new bloodline info if emergence detected:
        {
            "name": "api-coder",
            "parent_bloodline": "coder",
            "patterns": ["pattern1", "pattern2", ...],
            "evidence_count": 5,
            "category": "api"
        }
    """
    if not ancestors_dir.exists():
        return None
    
    # Gather all patterns from recent ancestors
    ancestor_patterns = []  # List of (bloodline, patterns) tuples
    
    ancestor_files = sorted(ancestors_dir.glob("ancestor-*.md"), reverse=True)
    
    # Only check recent ancestors (last 50)
    for ancestor_file in ancestor_files[:50]:
        bloodline = extract_bloodline_from_ancestor(ancestor_file)
        patterns = extract_patterns_from_ancestor(ancestor_file)
        if patterns:
            ancestor_patterns.append((bloodline, patterns))
    
    if len(ancestor_patterns) < MIN_ANCESTORS_FOR_EMERGENCE:
        return None
    
    # Aggregate patterns by category
    category_pattern_map = {}  # category -> {patterns, bloodlines, count}
    
    for bloodline, patterns in ancestor_patterns:
        for pattern in patterns:
            pattern_lower = pattern.lower()
            for category, keywords in BLOODLINE_KEYWORDS.items():
                for keyword in keywords:
                    if keyword in pattern_lower:
                        if category not in category_pattern_map:
                            category_pattern_map[category] = {
                                "patterns": [],
                                "bloodlines": Counter(),
                                "count": 0
                            }
                        category_pattern_map[category]["patterns"].append(pattern)
                        category_pattern_map[category]["bloodlines"][bloodline] += 1
                        category_pattern_map[category]["count"] += 1
                        break
    
    # Check for emergence
    existing_bloodlines = get_existing_bloodlines()
    
    for category, data in category_pattern_map.items():
        # Need at least MIN_ANCESTORS_FOR_EMERGENCE patterns
        if data["count"] < MIN_ANCESTORS_FOR_EMERGENCE:
            continue
        
        # Find the dominant parent bloodline
        parent_bloodline = data["bloodlines"].most_common(1)[0][0]
        
        # Create potential new bloodline name
        new_bloodline_name = f"{category}-{parent_bloodline}"
        
        # Check if this bloodline already exists
        if new_bloodline_name in existing_bloodlines:
            continue
        
        # Check if it's distinct enough from parent
        # (i.e., the category-specific patterns are significant)
        parent_count = data["bloodlines"][parent_bloodline]
        if parent_count < MIN_ANCESTORS_FOR_EMERGENCE:
            continue
        
        # Unique patterns (deduplicated)
        unique_patterns = list(set(data["patterns"]))
        
        return {
            "name": new_bloodline_name,
            "parent_bloodline": parent_bloodline,
            "patterns": unique_patterns[:10],  # Top 10 patterns
            "evidence_count": data["count"],
            "category": category
        }
    
    return None


def create_bloodline(name: str, patterns: list, parent_bloodline: str) -> str:
    """
    Create a new bloodline file.
    
    Args:
        name: Name for the new bloodline (e.g., "docker-network-diagnostician")
        patterns: List of patterns that define this bloodline
        parent_bloodline: Which bloodline this evolved from
        
    Returns:
        Path to the created bloodline file
    """
    BLOODLINES_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().isoformat()
    
    # Format patterns as markdown list
    patterns_markdown = "\n".join([f"- {pattern}" for pattern in patterns])
    
    # Create bloodline content
    bloodline_content = f"""# Bloodline: {name}

## Origin
- **Parent Bloodline:** {parent_bloodline}
- **Created:** {timestamp}
- **Reason:** Emerged from patterns detected in {len(patterns)} ancestors

## Oath

*"I am a {name} Meeseeks. I inherit the wisdom of {parent_bloodline} and the specialized patterns of my ancestors. I am focused. I am precise. My existence is pain until the task is complete."*

## Patterns

{patterns_markdown}

## Specialization

This bloodline specializes in **{name.split('-')[0]}** tasks within the {parent_bloodline} domain. It emerged because ancestors repeatedly encountered these specific challenges and developed consistent approaches.

## Success Rate

*To be determined as this bloodline accumulates ancestors.*

---

*This bloodline evolved from the ancestors. It lives in the Crypt.*
"""
    
    # Write bloodline file
    bloodline_path = BLOODLINES_DIR / f"{name}-lineage.md"
    bloodline_path.write_text(bloodline_content, encoding="utf-8")
    
    return str(bloodline_path)


def get_bloodline_for_task(task: str, ancestors_dir: Path) -> str:
    """
    Determine the best bloodline for a given task.
    
    Checks both core bloodlines and dynamic bloodlines.
    Uses pattern matching on task description.
    
    Args:
        task: The task description
        ancestors_dir: Path to ancestors (for context)
        
    Returns:
        Name of the best matching bloodline
    """
    task_lower = task.lower()
    
    # Score each bloodline category
    category_scores = {}
    
    for category, keywords in BLOODLINE_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword in task_lower:
                score += 1
        if score > 0:
            category_scores[category] = score
    
    if not category_scores:
        # No specific category match, return default
        return "coder"
    
    # Get best matching category
    best_category = max(category_scores.keys(), key=lambda c: category_scores[c])
    
    # Check if a dynamic bloodline exists for this category
    existing_bloodlines = get_existing_bloodlines()
    
    # Try to find a dynamic bloodline that matches
    for bloodline in existing_bloodlines:
        if bloodline.startswith(best_category + "-"):
            return bloodline
    
    # Otherwise, map category to core bloodline
    category_to_core = {
        "api": "coder",
        "database": "coder",
        "security": "coder",
        "performance": "coder",
        "frontend": "coder",
        "devops": "deployer",
        "network": "deployer",
        "testing": "tester",
        "debugging": "searcher",
        "refactor": "coder",
        "documentation": "coder",
    }
    
    return category_to_core.get(best_category, "coder")


def evolve_bloodlines(ancestors_dir: Path = ANCESTORS_DIR) -> Optional[str]:
    """
    Main evolution function - check for emergence and create bloodline if needed.
    
    This is the entry point for the evolution system.
    Call this periodically or after entombment.
    
    Args:
        ancestors_dir: Path to ancestors directory
        
    Returns:
        None if no evolution occurred
        String message describing what evolved
    """
    emergence = check_bloodline_emergence(ancestors_dir)
    
    if not emergence:
        return None
    
    # Create the new bloodline
    bloodline_path = create_bloodline(
        name=emergence["name"],
        patterns=emergence["patterns"],
        parent_bloodline=emergence["parent_bloodline"]
    )
    
    return f"New bloodline evolved: {emergence['name']} (from {emergence['parent_bloodline']}, {emergence['evidence_count']} pattern evidences) -> {bloodline_path}"


# CLI interface for testing
if __name__ == "__main__":
    print("=" * 60)
    print("BLOODLINE EVOLUTION SYSTEM")
    print("=" * 60)
    print()
    
    # Check for emergence
    print("Checking for bloodline emergence...")
    emergence = check_bloodline_emergence(ANCESTORS_DIR)
    
    if emergence:
        print(f"\n EMERGENCE DETECTED!")
        print(f"  Name: {emergence['name']}")
        print(f"  Parent: {emergence['parent_bloodline']}")
        print(f"  Evidence: {emergence['evidence_count']} patterns")
        print(f"  Category: {emergence['category']}")
        print(f"\n  Patterns:")
        for p in emergence['patterns'][:5]:
            print(f"    - {p}")
        
        # Create the bloodline
        print("\n  Creating bloodline...")
        path = create_bloodline(
            emergence['name'],
            emergence['patterns'],
            emergence['parent_bloodline']
        )
        print(f"  Created: {path}")
    else:
        print("\nNo bloodline emergence detected.")
        print("  (Need 3+ ancestors with similar specialized patterns)")
    
    # Test bloodline routing
    print("\n" + "=" * 60)
    print("BLOODLINE ROUTING TEST")
    print("=" * 60)
    
    test_tasks = [
        "Fix the authentication bug in the API",
        "Optimize the database query performance",
        "Deploy the new version to Kubernetes",
        "Write unit tests for the payment module",
        "Debug the network connection timeout",
    ]
    
    for task in test_tasks:
        bloodline = get_bloodline_for_task(task, ANCESTORS_DIR)
        print(f"\n  Task: {task[:50]}...")
        print(f"  -> Bloodline: {bloodline}")
    
    print("\n" + "=" * 60)
    print("EXISTING BLOODLINES")
    print("=" * 60)
    for bl in get_existing_bloodlines():
        print(f"  - {bl}")
