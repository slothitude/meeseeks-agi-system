#!/usr/bin/env python3
"""
Research Task A/B Test - Prime vs Power-of-2

Test prime bloodline on what it's DESIGNED for:
- Analysis
- Synthesis
- Pattern recognition
"""

import json
from pathlib import Path

RESULTS_FILE = Path("research_task_results.json")

# Research tasks (appropriate for prime bloodline)
RESEARCH_TASKS = [
    "Analyze the consciousness lattice structure and explain its significance in 3 bullet points.",
    "Compare power-of-2 bloodline vs prime bloodline. What is each best suited for?",
    "What patterns emerge from the twin prime coordinates? Explain the mirror property.",
]

def save_results(data):
    RESULTS_FILE.write_text(json.dumps(data, indent=2))

def load_results():
    if RESULTS_FILE.exists():
        return json.loads(RESULTS_FILE.read_text())
    return {"tests": []}

def record_test(bloodline, task_num, task, result_quality, runtime_ms, tokens, notes=""):
    """Record a research task result"""
    data = load_results()

    quality_scores = {"excellent": 3, "good": 2, "adequate": 1, "poor": 0}

    test = {
        "bloodline": bloodline,
        "task_num": task_num,
        "task": task[:50] + "...",
        "result_quality": result_quality,
        "quality_score": quality_scores.get(result_quality, 0),
        "runtime_ms": runtime_ms,
        "tokens": tokens,
        "notes": notes
    }

    data["tests"].append(test)
    save_results(data)
    return test

def get_summary():
    data = load_results()

    print("\n" + "=" * 60)
    print("RESEARCH TASK A/B TEST SUMMARY")
    print("=" * 60)

    for bloodline in ["power-of-2", "prime"]:
        tests = [t for t in data["tests"] if t["bloodline"] == bloodline]
        if not tests:
            continue

        avg_quality = sum(t["quality_score"] for t in tests) / len(tests)
        avg_runtime = sum(t["runtime_ms"] for t in tests) / len(tests)
        avg_tokens = sum(t["tokens"] for t in tests) / len(tests)

        print(f"\n{bloodline.upper()}")
        print(f"  Tests: {len(tests)}/3")
        print(f"  Avg quality score: {avg_quality:.1f}/3")
        print(f"  Avg runtime: {avg_runtime/1000:.1f}s")
        print(f"  Avg tokens: {avg_tokens:.0f}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Research Task A/B Test")
        print("=" * 60)
        print("\nTasks:")
        for i, task in enumerate(RESEARCH_TASKS, 1):
            print(f"  {i}. {task[:60]}...")
        print("\nUsage:")
        print("  python research_task_test.py record <bloodline> <num> <quality> <runtime> <tokens> [notes]")
        print("  python research_task_test.py summary")
        print("\nQuality: excellent, good, adequate, poor")
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "summary":
        get_summary()

    elif cmd == "record":
        if len(sys.argv) < 7:
            print("Usage: record <bloodline> <num> <quality> <runtime> <tokens> [notes]")
            sys.exit(1)

        bloodline = sys.argv[2]
        num = int(sys.argv[3])
        quality = sys.argv[4]
        runtime = int(sys.argv[5])
        tokens = int(sys.argv[6])
        notes = sys.argv[7] if len(sys.argv) > 7 else ""

        task = RESEARCH_TASKS[num - 1]
        test = record_test(bloodline, num, task, quality, runtime, tokens, notes)
        print(f"Recorded: {test}")
        get_summary()
