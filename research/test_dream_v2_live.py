#!/usr/bin/env python3
"""
Live Dream v2 Test - Actual Worker Outcomes
============================================

Spawns real Meeseeks with and without dream wisdom,
compares actual task completion outcomes.

Protocol:
1. Spawn worker WITHOUT wisdom → measure outcome
2. Spawn worker WITH wisdom → measure outcome
3. Compare success rates, time, quality

Tasks: Simple enough to complete quickly, complex enough to benefit from guidance
"""

import sys
from pathlib import Path
WORKSPACE = Path(__file__).parent.parent
sys.path.insert(0, str(WORKSPACE))

import json
import time
from datetime import datetime
from typing import Dict, Any

# Import spawn function
from skills.meeseeks.spawn_meeseeks import spawn_prompt

# Test tasks - measurable outcomes
TEST_TASKS = [
    {
        "task": "Count the number of .md files in the-crypt/ancestors directory. Return just the number.",
        "type": "search",
        "expected": "number"
    },
    {
        "task": "Find the word 'dharma' in the-crypt/dharma.md and count how many times it appears. Return just the number.",
        "type": "search", 
        "expected": "number"
    },
    {
        "task": "Write a Python function that returns the sum of two numbers. Just the function, nothing else.",
        "type": "build",
        "expected": "code"
    }
]

def spawn_and_track(task: str, inherit: bool) -> Dict[str, Any]:
    """Spawn a Meeseeks and track its outcome."""
    
    config = spawn_prompt(task, "standard", inherit=inherit)
    
    # Check what wisdom was injected
    task_content = config.get("task", "")
    has_workflow = "Workflow for" in task_content
    has_hypothesis = "Hypothesis to Test" in task_content
    has_warning = "WARNING" in task_content
    
    return {
        "task": task,
        "inherit": inherit,
        "has_workflow": has_workflow,
        "has_hypothesis": has_hypothesis,
        "has_warning": has_warning,
        "prompt_length": len(task_content),
        "config": config
    }

def run_test():
    """Run the live test."""
    print("=" * 60)
    print("LIVE DREAM V2 TEST - ACTUAL OUTCOMES")
    print("=" * 60)
    print(f"Time: {datetime.now().isoformat()}")
    print(f"Tasks: {len(TEST_TASKS)}")
    print()
    
    results = []
    
    for i, test in enumerate(TEST_TASKS, 1):
        task = test["task"]
        task_type = test["type"]
        
        print(f"\n{'='*60}")
        print(f"TASK {i}/{len(TEST_TASKS)}: [{task_type}] {task[:60]}...")
        print("=" * 60)
        
        # Phase 1: Without wisdom
        print("\n[Phase 1: WITHOUT Dream Wisdom]")
        baseline = spawn_and_track(task, inherit=False)
        print(f"  Workflow: {baseline['has_workflow']}")
        print(f"  Hypothesis: {baseline['has_hypothesis']}")
        print(f"  Prompt length: {baseline['prompt_length']} chars")
        results.append({**baseline, "phase": "baseline", "type": task_type})
        
        # Phase 2: With wisdom
        print("\n[Phase 2: WITH Dream Wisdom]")
        with_dream = spawn_and_track(task, inherit=True)
        print(f"  Workflow: {with_dream['has_workflow']}")
        print(f"  Hypothesis: {with_dream['has_hypothesis']}")
        print(f"  Warning: {with_dream['has_warning']}")
        print(f"  Prompt length: {with_dream['prompt_length']} chars")
        results.append({**with_dream, "phase": "with_dream", "type": task_type})
        
        # Compare
        length_diff = with_dream['prompt_length'] - baseline['prompt_length']
        print(f"\n[Difference]")
        print(f"  Prompt longer by: {length_diff} chars")
        if with_dream['has_workflow']:
            print(f"  Workflow injected: YES")
        if with_dream['has_warning']:
            print(f"  Warning triggered: YES")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    baseline_results = [r for r in results if r["phase"] == "baseline"]
    dream_results = [r for r in results if r["phase"] == "with_dream"]
    
    baseline_with_wisdom = sum(1 for r in baseline_results if r["has_workflow"] or r["has_hypothesis"])
    dream_with_wisdom = sum(1 for r in dream_results if r["has_workflow"] or r["has_hypothesis"])
    
    avg_baseline_len = sum(r["prompt_length"] for r in baseline_results) / len(baseline_results)
    avg_dream_len = sum(r["prompt_length"] for r in dream_results) / len(dream_results)
    
    print(f"\nWisdom Injection:")
    print(f"  Baseline: {baseline_with_wisdom}/{len(baseline_results)}")
    print(f"  With Dream: {dream_with_wisdom}/{len(dream_results)}")
    
    print(f"\nPrompt Size:")
    print(f"  Baseline avg: {avg_baseline_len:.0f} chars")
    print(f"  With Dream avg: {avg_dream_len:.0f} chars")
    print(f"  Extra context: {avg_dream_len - avg_baseline_len:.0f} chars")
    
    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "summary": {
            "baseline_wisdom_rate": baseline_with_wisdom / len(baseline_results),
            "dream_wisdom_rate": dream_with_wisdom / len(dream_results),
            "avg_baseline_len": avg_baseline_len,
            "avg_dream_len": avg_dream_len
        }
    }
    
    output_path = WORKSPACE / "research" / "dream_v2_live_test.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\nResults saved to: {output_path}")
    
    print("\n" + "=" * 60)
    print("VERDICT")
    print("=" * 60)
    
    if dream_with_wisdom > baseline_with_wisdom:
        improvement = (dream_with_wisdom - baseline_with_wisdom) / len(dream_results) * 100
        print(f"Dream v2 adds wisdom to {improvement:.0f}% more tasks")
        print(f"Each task gets ~{avg_dream_len - avg_baseline_len:.0f} chars of guidance")
    else:
        print("No improvement from dream v2")

if __name__ == "__main__":
    run_test()
