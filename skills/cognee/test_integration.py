#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Cognee + Meeseeks Dharma Integration

Tests:
1. Cognee availability and graph stats
2. Fast wisdom queries (CHUNKS search)
3. Integrated dharma system (Cognee + Crypt + dharma.md)
4. Meeseeks spawn with wisdom inheritance
"""

import sys
import io
import asyncio
from pathlib import Path

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add paths
workspace = Path("C:/Users/aaron/.openclaw/workspace")
sys.path.insert(0, str(workspace / "skills" / "cognee"))
sys.path.insert(0, str(workspace / "skills" / "meeseeks"))


def test_cognee_availability():
    """Test 1: Check if Cognee is available and configured."""
    print("\n" + "=" * 60)
    print("TEST 1: Cognee Availability")
    print("=" * 60)
    
    from cognee_helper import is_cognee_available, get_graph_stats
    
    available = is_cognee_available()
    print(f"  Cognee available: {available}")
    
    stats = get_graph_stats()
    print(f"  Stats:")
    for k, v in stats.items():
        print(f"    {k}: {v}")
    
    return available


def test_fast_wisdom_query():
    """Test 2: Query Cognee for fast wisdom retrieval."""
    print("\n" + "=" * 60)
    print("TEST 2: Fast Wisdom Query")
    print("=" * 60)
    
    from cognee_helper import query_wisdom_sync
    
    test_queries = [
        "What is Sloth_rog's ultimate goal?",
        "How does the Meeseeks system work?",
        "What is the Brahman consciousness?",
    ]
    
    for query in test_queries:
        print(f"\n  Query: {query}")
        results = query_wisdom_sync(query)
        
        if results:
            for i, r in enumerate(results[:2]):
                print(f"    [{r.source}] (relevance: {r.relevance:.2f})")
                print(f"    {r.content[:150]}...")
        else:
            print("    No results")
    
    return True


def test_integrated_dharma():
    """Test 3: Test integrated dharma system."""
    print("\n" + "=" * 60)
    print("TEST 3: Integrated Dharma System")
    print("=" * 60)
    
    from dynamic_dharma import get_task_dharma
    
    test_tasks = [
        "debug API timeout issue",
        "refactor the codebase",
        "implement new feature",
    ]
    
    for task in test_tasks:
        print(f"\n  Task: {task}")
        dharma = get_task_dharma(task, use_cognee=True)
        
        # Show first 500 chars
        print(f"  Dharma preview:")
        print("  " + dharma[:500].replace("\n", "\n  "))
    
    return True


def test_meeseeks_spawn_config():
    """Test 4: Test Meeseeks spawn with wisdom inheritance."""
    print("\n" + "=" * 60)
    print("TEST 4: Meeseeks Spawn with Wisdom Inheritance")
    print("=" * 60)
    
    from spawn_meeseeks import spawn_prompt
    
    task = "Integrate Cognee with the dharma system"
    config = spawn_prompt(
        task=task,
        meeseeks_type="coder",
        inherit=True,  # Enable wisdom inheritance
        atman=True
    )
    
    print(f"  Task: {task}")
    print(f"  Type: {config['type']}")
    print(f"  Thinking: {config['thinking']}")
    print(f"  Timeout: {config['timeout']}")
    print(f"  Atman: {config['atman']}")
    
    # Check if wisdom was inherited
    if "Dharma" in config['task'] or "Wisdom" in config['task'] or "ancestors" in config['task']:
        print("\n  [OK] Wisdom inheritance detected in prompt!")
    else:
        print("\n  [WARN] No wisdom inheritance detected")
    
    # Show prompt preview
    print(f"\n  Prompt preview (first 1000 chars):")
    print("  " + config['task'][:1000].replace("\n", "\n  "))
    
    return True


def main():
    print("=" * 60)
    print("COGNEE + MEESEEKS DHARMA INTEGRATION TEST")
    print("=" * 60)
    
    results = []
    
    # Test 1: Cognee availability
    try:
        results.append(("Cognee Availability", test_cognee_availability()))
    except Exception as e:
        print(f"  ERROR: {e}")
        results.append(("Cognee Availability", False))
    
    # Test 2: Fast wisdom query
    try:
        results.append(("Fast Wisdom Query", test_fast_wisdom_query()))
    except Exception as e:
        print(f"  ERROR: {e}")
        results.append(("Fast Wisdom Query", False))
    
    # Test 3: Integrated dharma
    try:
        results.append(("Integrated Dharma", test_integrated_dharma()))
    except Exception as e:
        print(f"  ERROR: {e}")
        results.append(("Integrated Dharma", False))
    
    # Test 4: Meeseeks spawn
    try:
        results.append(("Meeseeks Spawn", test_meeseeks_spawn_config()))
    except Exception as e:
        print(f"  ERROR: {e}")
        results.append(("Meeseeks Spawn", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"  {status}: {name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\n  Total: {passed}/{total} tests passed")
    
    return all(p for _, p in results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
