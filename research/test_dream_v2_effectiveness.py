"""
Dream v2 Effectiveness Test
===========================

Tests whether the new dream system actually improves Meeseeks performance.

Protocol:
1. Run baseline tasks WITHOUT dream wisdom
2. Run dream v2 to extract patterns
3. Run same tasks WITH dream wisdom
4. Compare success rates

Tasks chosen: Mix of types that should trigger workflows
"""

import sys
from pathlib import Path

# Add workspace to path
WORKSPACE = Path(__file__).parent.parent
sys.path.insert(0, str(WORKSPACE))

import json
import time
from datetime import datetime

# Test tasks - each designed to trigger a workflow
TEST_TASKS = [
    # Search tasks
    ("search", "Count all .py files in the workspace"),
    ("search", "Find files containing 'dream' in their name"),
    
    # Build tasks  
    ("build", "Create a simple hello world function"),
    ("build", "Write a function that adds two numbers"),
    
    # Debug tasks
    ("debug", "Find why this code returns None: def f(): pass"),
    
    # General tasks
    ("general", "What is 2 + 2? Answer in one number."),
    ("general", "Name 3 colors. Just the names, nothing else."),
]

def test_without_dream():
    """Run test tasks without dream wisdom."""
    print("=" * 60)
    print("PHASE 1: BASELINE (No Dream Wisdom)")
    print("=" * 60)
    
    results = []
    
    for task_type, task in TEST_TASKS:
        print(f"\n[{task_type}] {task}")
        
        # Spawn without inheriting wisdom
        try:
            from skills.meeseeks.spawn_meeseeks import spawn_prompt
            
            config = spawn_prompt(task, "standard", inherit=False)
            
            # Check if wisdom was injected
            task_content = config.get("task", "")
            has_workflow = "Workflow for" in task_content
            has_hypothesis = "Hypothesis to Test" in task_content
            has_warning = "WARNING" in task_content
            
            print(f"  Workflow injected: {has_workflow}")
            print(f"  Hypothesis injected: {has_hypothesis}")
            print(f"  Warning injected: {has_warning}")
            
            results.append({
                "task": task,
                "type": task_type,
                "has_workflow": has_workflow,
                "has_hypothesis": has_hypothesis,
                "has_warning": has_warning,
                "phase": "baseline"
            })
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                "task": task,
                "type": task_type,
                "error": str(e),
                "phase": "baseline"
            })
    
    return results

def test_with_dream():
    """Run test tasks with dream wisdom."""
    print("\n" + "=" * 60)
    print("PHASE 2: WITH DREAM WISDOM")
    print("=" * 60)
    
    results = []
    
    for task_type, task in TEST_TASKS:
        print(f"\n[{task_type}] {task}")
        
        # Spawn WITH inheriting wisdom
        try:
            from skills.meeseeks.spawn_meeseeks import spawn_prompt
            
            config = spawn_prompt(task, "standard", inherit=True)
            
            # Check if wisdom was injected
            task_content = config.get("task", "")
            has_workflow = "Workflow for" in task_content
            has_hypothesis = "Hypothesis to Test" in task_content
            has_warning = "WARNING" in task_content
            
            # Extract workflow if present
            workflow_steps = []
            if has_workflow:
                idx = task_content.find("Workflow for")
                workflow_section = task_content[idx:idx+500]
                steps = [line.strip() for line in workflow_section.split("\n") if line.strip().startswith(("1.", "2.", "3.", "4.", "5."))]
                workflow_steps = steps
            
            print(f"  Workflow injected: {has_workflow}")
            if workflow_steps:
                print(f"    Steps: {len(workflow_steps)}")
            print(f"  Hypothesis injected: {has_hypothesis}")
            print(f"  Warning injected: {has_warning}")
            
            results.append({
                "task": task,
                "type": task_type,
                "has_workflow": has_workflow,
                "has_hypothesis": has_hypothesis,
                "has_warning": has_warning,
                "workflow_steps": len(workflow_steps) if workflow_steps else 0,
                "phase": "with_dream"
            })
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                "task": task,
                "type": task_type,
                "error": str(e),
                "phase": "with_dream"
            })
    
    return results

def compare_results(baseline, with_dream):
    """Compare baseline vs dream-enhanced results."""
    print("\n" + "=" * 60)
    print("COMPARISON")
    print("=" * 60)
    
    # Count wisdom injection
    baseline_with_wisdom = sum(1 for r in baseline if r.get("has_workflow") or r.get("has_hypothesis"))
    dream_with_wisdom = sum(1 for r in with_dream if r.get("has_workflow") or r.get("has_hypothesis"))
    
    print(f"\nWisdom Injection:")
    print(f"  Baseline: {baseline_with_wisdom}/{len(baseline)} tasks had wisdom")
    print(f"  With Dream: {dream_with_wisdom}/{len(with_dream)} tasks had wisdom")
    
    # By type
    print(f"\nBy Task Type:")
    for task_type in ["search", "build", "debug", "general"]:
        baseline_type = [r for r in baseline if r.get("type") == task_type]
        dream_type = [r for r in with_dream if r.get("type") == task_type]
        
        baseline_wisdom = sum(1 for r in baseline_type if r.get("has_workflow"))
        dream_wisdom = sum(1 for r in dream_type if r.get("has_workflow"))
        
        print(f"  {task_type}: baseline={baseline_wisdom}/{len(baseline_type)}, dream={dream_wisdom}/{len(dream_type)}")
    
    # Workflow quality
    print(f"\nWorkflow Quality:")
    total_steps = sum(r.get("workflow_steps", 0) for r in with_dream)
    tasks_with_workflows = sum(1 for r in with_dream if r.get("has_workflow"))
    if tasks_with_workflows > 0:
        avg_steps = total_steps / tasks_with_workflows
        print(f"  Average steps per workflow: {avg_steps:.1f}")
    
    # Warnings triggered
    warnings = sum(1 for r in with_dream if r.get("has_warning"))
    print(f"\nWarnings Triggered: {warnings}")
    
    return {
        "baseline_wisdom_rate": baseline_with_wisdom / len(baseline) if baseline else 0,
        "dream_wisdom_rate": dream_with_wisdom / len(with_dream) if with_dream else 0,
        "avg_workflow_steps": total_steps / tasks_with_workflows if tasks_with_workflows > 0 else 0,
        "warnings_triggered": warnings
    }

def main():
    print("DREAM V2 EFFECTIVENESS TEST")
    print("=" * 60)
    print(f"Time: {datetime.now().isoformat()}")
    print(f"Tasks: {len(TEST_TASKS)}")
    
    # Phase 1: Baseline
    baseline = test_without_dream()
    
    # Phase 2: With dream
    with_dream = test_with_dream()
    
    # Compare
    stats = compare_results(baseline, with_dream)
    
    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "baseline": baseline,
        "with_dream": with_dream,
        "stats": stats
    }
    
    output_path = Path("research/dream_v2_test_results.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_path}")
    
    # Final verdict
    print("\n" + "=" * 60)
    print("VERDICT")
    print("=" * 60)
    
    if stats["dream_wisdom_rate"] > stats["baseline_wisdom_rate"]:
        improvement = (stats["dream_wisdom_rate"] - stats["baseline_wisdom_rate"]) * 100
        print(f"Dream v2 IMPROVES wisdom injection by {improvement:.0f}%")
    else:
        print("Dream v2 does NOT improve wisdom injection")
    
    if stats["avg_workflow_steps"] >= 3:
        print(f"Workflows have adequate depth ({stats['avg_workflow_steps']:.1f} steps avg)")
    else:
        print(f"Workflows are too shallow ({stats['avg_workflow_steps']:.1f} steps avg)")
    
    if stats["warnings_triggered"] > 0:
        print(f"Failure signals are working ({stats['warnings_triggered']} warnings)")
    else:
        print("No failure signals triggered (may need more diverse tasks)")

if __name__ == "__main__":
    main()
