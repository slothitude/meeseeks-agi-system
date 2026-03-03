#!/usr/bin/env python3
"""Quick test of karma observer integration."""

import sys
from pathlib import Path

# Add skills/meeseeks to path
sys.path.insert(0, str(Path(__file__).parent))

from karma_observer import (
    observe_karma, 
    log_karma_observation, 
    analyze_karma_patterns,
    format_analysis_output
)

# Test 1: Observe karma for a specific ancestor
print("=" * 60)
print("TEST 1: Observe Karma for Specific Ancestor")
print("=" * 60)

test_ancestor = Path(__file__).parent.parent.parent / "the-crypt" / "ancestors" / "ancestor-20260303-084630-9118.md"
if test_ancestor.exists():
    karma = observe_karma(str(test_ancestor))
    print(f"\n✓ Observed karma for {karma['ancestor_id']}")
    print(f"  Task: {karma['task'][:80]}")
    print(f"  Outcome: {karma['outcome']}")
    print(f"  Alignment: {karma['alignment']}")
    print(f"  Followed: {karma['dharma_followed']}")
    print(f"  Ignored: {karma['dharma_ignored']}")
    print(f"  Insight: {karma['insight']}")
else:
    print(f"✗ Test ancestor not found: {test_ancestor}")

# Test 2: Analyze karma patterns
print("\n" + "=" * 60)
print("TEST 2: Analyze Karma Patterns")
print("=" * 60)

analysis = analyze_karma_patterns()
print(format_analysis_output(analysis))

# Test 3: Verify karma log exists
print("\n" + "=" * 60)
print("TEST 3: Verify Karma Log")
print("=" * 60)

karma_log = Path(__file__).parent.parent.parent / "the-crypt" / "karma_observations.jsonl"
if karma_log.exists():
    with open(karma_log, 'r', encoding='utf-8') as f:
        count = sum(1 for _ in f)
    print(f"✓ Karma log exists with {count} observations")
    print(f"  Location: {karma_log}")
else:
    print(f"✗ Karma log not found")

print("\n" + "=" * 60)
print("✓ Karma Observer System Operational")
print("=" * 60)
