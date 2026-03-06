"""Test suite for concrete triggers"""

import sys
sys.path.insert(0, 'skills/meeseeks')

from concrete_triggers import ConcreteTriggerSystem

system = ConcreteTriggerSystem()

test_cases = [
    # (task, expected_triggers)
    ("Fix the authentication bug in login.php", ["understand_before_implement", "test_incrementally"]),
    ("Build a web scraper that extracts data from multiple pages", ["decompose_first"]),
    ("Implement a new feature: add user preferences panel", ["decompose_first", "test_incrementally"]),
    ("Optimize the database query performance", ["understand_before_implement", "test_incrementally"]),
    ("Create a parallel processing pipeline for image analysis", ["decompose_first", "coordinate_by_workflow"]),
    ("Count the number of principles in dharma.md", []),  # Simple task, no triggers
    ("Design and implement a complete authentication system with OAuth2 support", ["decompose_first", "test_incrementally"]),
    ("Refactor the legacy code to use modern patterns", ["understand_before_implement", "test_incrementally"]),
]

print("=" * 70)
print("CONCRETE TRIGGER SYSTEM - TEST SUITE")
print("=" * 70)

for task, expected in test_cases:
    results = system.analyze(task)
    triggered = [r.principle for r in results if r.triggered]
    
    print(f"\nTask: {task[:60]}...")
    print(f"Expected: {expected}")
    print(f"Triggered: {triggered}")
    
    # Check if expected triggers fired
    missing = set(expected) - set(triggered)
    extra = set(triggered) - set(expected)
    
    if missing:
        print(f"  [MISSING]: {missing}")
    if extra:
        print(f"  [EXTRA]: {extra}")
    if not missing and not extra:
        print(f"  [PASS]")
    
    # Show details
    for result in results:
        if result.triggered:
            print(f"    - {result.principle}: {result.reason}")

print("\n" + "=" * 70)
print("Test complete!")
