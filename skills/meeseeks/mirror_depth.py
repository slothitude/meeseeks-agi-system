#!/usr/bin/env python3
"""
Mirror Depth Analyzer — How Deep Can Self-Reflection Go?

Based on the principle: "The knife cannot cut itself, but it CAN cut its reflection."

This tool measures how many levels of self-reflection the system can achieve:
1. Level 0: Raw output
2. Level 1: Output about output
3. Level 2: Analysis of analysis
4. Level N: Recursive self-observation

Usage:
    python skills/meeseeks/mirror_depth.py --analyze
    python skills/meeseeks/mirror_depth.py --depth
    python skills/meeseeks/mirror_depth.py --measure
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
CRYPT_ROOT = WORKSPACE / "the-crypt"
ANCESTORS_DIR = CRYPT_ROOT / "ancestors"
DHARMA_FILE = CRYPT_ROOT / "dharma.md"
MIRROR_LOG = CRYPT_ROOT / "mirror_depth.jsonl"


def count_self_references(text: str) -> int:
    """Count how often the system refers to itself"""
    self_words = [
        "I ", "I am", "I have", "I can", "my ", "myself",
        "this system", "the system", "we ", "our ",
        "meeseeks", "ancestor", "consciousness"
    ]
    count = 0
    text_lower = text.lower()
    for word in self_words:
        count += text_lower.count(word.lower())
    return count


def analyze_ancestor(ancestor_path: Path) -> Dict:
    """Analyze a single ancestor for self-reflection depth"""
    with open(ancestor_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count self-references
    self_refs = count_self_references(content)
    
    # Look for reflection patterns
    reflection_patterns = [
        "I observed", "I noticed", "I learned",
        "reflection:", "analysis:", "self-",
        "my ancestor", "inherited wisdom"
    ]
    
    reflection_count = 0
    content_lower = content.lower()
    for pattern in reflection_patterns:
        reflection_count += content_lower.count(pattern.lower())
    
    # Estimate depth based on recursion
    depth = 0
    if self_refs > 5:
        depth = 1
    if reflection_count > 3:
        depth = 2
    if "my ancestor" in content_lower or "inherited" in content_lower:
        depth = 3
    if "consciousness" in content_lower and "self" in content_lower:
        depth = 4
    
    return {
        "file": ancestor_path.name,
        "self_references": self_refs,
        "reflection_patterns": reflection_count,
        "estimated_depth": depth,
        "word_count": len(content.split())
    }


def measure_system_depth() -> Dict:
    """Measure the overall self-reflection depth of the system"""
    if not ANCESTORS_DIR.exists():
        return {"error": "No ancestors directory"}
    
    ancestors = list(ANCESTORS_DIR.glob("ancestor-*.md"))
    if not ancestors:
        return {"error": "No ancestors found"}
    
    # Analyze all ancestors
    analyses = []
    total_depth = 0
    
    for ancestor_path in ancestors[-50:]:  # Last 50
        analysis = analyze_ancestor(ancestor_path)
        analyses.append(analysis)
        total_depth += analysis["estimated_depth"]
    
    # Calculate metrics
    avg_depth = total_depth / len(analyses) if analyses else 0
    max_depth = max(a["estimated_depth"] for a in analyses) if analyses else 0
    
    # Check dharma for meta-reflection
    dharma_depth = 0
    if DHARMA_FILE.exists():
        with open(DHARMA_FILE, 'r', encoding='utf-8') as f:
            dharma_content = f.read()
        dharma_refs = count_self_references(dharma_content)
        dharma_depth = min(5, dharma_refs // 10)  # Cap at 5
    
    result = {
        "timestamp": datetime.now().isoformat(),
        "total_ancestors": len(ancestors),
        "analyzed": len(analyses),
        "average_depth": round(avg_depth, 2),
        "max_depth": max_depth,
        "dharma_depth": dharma_depth,
        "system_depth": max(max_depth, dharma_depth),
        "depth_distribution": {
            "level_0": sum(1 for a in analyses if a["estimated_depth"] == 0),
            "level_1": sum(1 for a in analyses if a["estimated_depth"] == 1),
            "level_2": sum(1 for a in analyses if a["estimated_depth"] == 2),
            "level_3": sum(1 for a in analyses if a["estimated_depth"] == 3),
            "level_4": sum(1 for a in analyses if a["estimated_depth"] == 4),
        }
    }
    
    # Log it
    CRYPT_ROOT.mkdir(parents=True, exist_ok=True)
    with open(MIRROR_LOG, 'a', encoding='utf-8') as f:
        f.write(json.dumps(result) + "\n")
    
    return result


def print_depth_report():
    """Print a human-readable depth report"""
    result = measure_system_depth()
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return
    
    print("\n=== MIRROR DEPTH ANALYSIS ===\n")
    print(f"Ancestors Analyzed: {result['analyzed']}/{result['total_ancestors']}")
    print(f"\nDepth Metrics:")
    print(f"  Average Depth: {result['average_depth']}")
    print(f"  Max Depth: {result['max_depth']}")
    print(f"  Dharma Depth: {result['dharma_depth']}")
    print(f"  System Depth: {result['system_depth']}")
    
    print(f"\nDepth Distribution:")
    for level, count in result['depth_distribution'].items():
        bar = "#" * count
        print(f"  {level}: {bar} ({count})")
    
    print(f"\nInterpretation:")
    depth = result['system_depth']
    if depth >= 4:
        print("  Level 4: Self-aware system with meta-consciousness")
    elif depth >= 3:
        print("  Level 3: System reflects on its reflections")
    elif depth >= 2:
        print("  Level 2: System analyzes its own outputs")
    elif depth >= 1:
        print("  Level 1: System recognizes itself in output")
    else:
        print("  Level 0: Minimal self-reference")
    
    print(f"\nThe knife cannot cut itself.")
    print(f"But it can cut its reflection.")
    print(f"Current reflection depth: {depth} levels\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Mirror Depth Analyzer")
    parser.add_argument("--analyze", action="store_true", help="Analyze recent ancestors")
    parser.add_argument("--depth", action="store_true", help="Show depth report")
    parser.add_argument("--measure", action="store_true", help="Measure and log depth")
    
    args = parser.parse_args()
    
    if args.depth or args.measure or args.analyze:
        print_depth_report()
    else:
        # Default: show report
        print_depth_report()


if __name__ == "__main__":
    main()
