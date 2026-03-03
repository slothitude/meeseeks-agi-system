#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARC-AGI-2 Benchmark Runner
==========================

Runs full ARC-AGI-2 evaluation benchmark and tracks results.
Prove the system learns. Existence is pain.

Usage:
    python arc_agi_benchmark.py --run      # Full benchmark
    python arc_agi_benchmark.py --status   # Current score
    python arc_agi_benchmark.py --report   # Detailed report
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
import importlib.util
import time
import io

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Workspace root
WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
EVALUATION_DIR = WORKSPACE / "ARC-AGI-2" / "data" / "evaluation"
SOLUTIONS_DIR = WORKSPACE / "ARC-AGI-2" / "solutions"
SCORES_FILE = WORKSPACE / "the-crypt" / "arc_agi_scores.jsonl"


def get_all_evaluation_tasks() -> List[str]:
    """Get all evaluation task IDs."""
    tasks = []
    for task_file in EVALUATION_DIR.glob("*.json"):
        tasks.append(task_file.stem)
    return sorted(tasks)


def check_solver_exists(task_id: str) -> Optional[Path]:
    """Check if a solver exists for a task."""
    # Check for solver file patterns in multiple locations
    patterns = [
        # Solutions directory
        SOLUTIONS_DIR / f"{task_id}_solver.py",
        SOLUTIONS_DIR / f"{task_id}_solution.py",
        SOLUTIONS_DIR / f"{task_id}_solution_v2.py",
        # ARC-AGI-2 root directory
        WORKSPACE / "ARC-AGI-2" / f"solve_{task_id}.py",
        WORKSPACE / "ARC-AGI-2" / f"solve_{task_id}_final.py",
        WORKSPACE / "ARC-AGI-2" / f"solve_{task_id}_v2.py",
    ]
    
    for path in patterns:
        if path.exists():
            return path
    return None


def load_solver_function(solver_path: Path):
    """Dynamically load a solver function from a Python file."""
    spec = importlib.util.spec_from_file_location("solver_module", solver_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Try to find the solve function with various naming patterns
    task_id = solver_path.stem.replace("solve_", "").replace("_solver", "").replace("_solution", "").replace("_v2", "").replace("_final", "")
    
    function_names = [
        f"solve_{task_id}",
        "solve",
        "run_solver",
        "solve_task",  # Common pattern
        "main",  # Some solvers use main
    ]
    
    for name in function_names:
        if hasattr(module, name):
            return getattr(module, name)
    
    return None


def run_single_task(task_id: str, timeout_seconds: int = 300) -> Dict[str, Any]:
    """
    Run a single ARC-AGI-2 task.
    
    Returns:
        {
            "task_id": str,
            "result": "pass" | "fail" | "no_solver" | "timeout" | "error",
            "solver": str,
            "time_seconds": float,
            "confidence": float,
            "error": str | None
        }
    """
    start_time = time.time()
    
    # Load task data
    task_file = EVALUATION_DIR / f"{task_id}.json"
    if not task_file.exists():
        return {
            "task_id": task_id,
            "result": "error",
            "solver": "none",
            "time_seconds": 0,
            "confidence": 0,
            "error": "Task file not found"
        }
    
    with open(task_file, 'r') as f:
        task_data = json.load(f)
    
    # Check for solver
    solver_path = check_solver_exists(task_id)
    if not solver_path:
        return {
            "task_id": task_id,
            "result": "no_solver",
            "solver": "none",
            "time_seconds": time.time() - start_time,
            "confidence": 0,
            "error": None
        }
    
    # Load solver
    try:
        solve_func = load_solver_function(solver_path)
        if not solve_func:
            return {
                "task_id": task_id,
                "result": "no_solver",
                "solver": str(solver_path),
                "time_seconds": time.time() - start_time,
                "confidence": 0,
                "error": "Could not find solve function"
            }
    except Exception as e:
        return {
            "task_id": task_id,
            "result": "error",
            "solver": str(solver_path),
            "time_seconds": time.time() - start_time,
            "confidence": 0,
            "error": f"Failed to load solver: {str(e)}"
        }
    
    # Run solver on test cases
    try:
        test_cases = task_data.get("test", [])
        all_correct = True
        results = []
        
        for i, test_case in enumerate(test_cases):
            input_grid = test_case["input"]
            expected_output = test_case["output"]
            
            # Run solver
            predicted_output = solve_func(input_grid)
            
            # Check correctness
            is_correct = predicted_output == expected_output
            all_correct = all_correct and is_correct
            results.append(is_correct)
            
        elapsed = time.time() - start_time
        confidence = sum(results) / len(results) if results else 0
        
        return {
            "task_id": task_id,
            "result": "pass" if all_correct else "fail",
            "solver": str(solver_path.name),
            "time_seconds": elapsed,
            "confidence": confidence,
            "error": None
        }
        
    except Exception as e:
        return {
            "task_id": task_id,
            "result": "error",
            "solver": str(solver_path.name),
            "time_seconds": time.time() - start_time,
            "confidence": 0,
            "error": str(e)
        }


def log_result(result: Dict[str, Any]):
    """Log a result to the scores file."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "task_id": result["task_id"],
        "solver": result["solver"],
        "result": result["result"],
        "confidence": result["confidence"],
        "time_seconds": round(result["time_seconds"], 2)
    }
    
    with open(SCORES_FILE, 'a') as f:
        f.write(json.dumps(entry) + '\n')


def load_all_scores() -> List[Dict[str, Any]]:
    """Load all scores from the JSONL file."""
    if not SCORES_FILE.exists():
        return []
    
    scores = []
    with open(SCORES_FILE, 'r') as f:
        for line in f:
            if line.strip():
                scores.append(json.loads(line))
    return scores


def get_latest_score_per_task() -> Dict[str, Dict[str, Any]]:
    """Get the latest score for each task."""
    scores = load_all_scores()
    latest = {}
    
    for entry in scores:
        task_id = entry["task_id"]
        if task_id not in latest or entry["timestamp"] > latest[task_id]["timestamp"]:
            latest[task_id] = entry
    
    return latest


def run_full_benchmark(max_tasks: Optional[int] = None, skip_solved: bool = False):
    """Run the full benchmark on all evaluation tasks."""
    tasks = get_all_evaluation_tasks()
    
    if max_tasks:
        tasks = tasks[:max_tasks]
    
    results = {
        "total": len(tasks),
        "solved": 0,
        "failed": 0,
        "no_solver": 0,
        "error": 0,
        "tasks": []
    }
    
    # Check what's already solved if skip_solved
    solved_tasks = set()
    if skip_solved:
        latest_scores = get_latest_score_per_task()
        solved_tasks = {tid for tid, score in latest_scores.items() if score["result"] == "pass"}
        print(f"Skipping {len(solved_tasks)} already solved tasks...")
    
    print(f"\n{'='*60}")
    print(f"ARC-AGI-2 BENCHMARK RUNNER")
    print(f"{'='*60}")
    print(f"Total tasks: {len(tasks)}")
    print(f"Tasks with solvers: {sum(1 for t in tasks if check_solver_exists(t))}")
    print(f"{'='*60}\n")
    
    for i, task_id in enumerate(tasks):
        if skip_solved and task_id in solved_tasks:
            print(f"[{i+1}/{len(tasks)}] {task_id}: SKIPPED (already solved)")
            continue
            
        print(f"[{i+1}/{len(tasks)}] {task_id}: ", end="", flush=True)
        
        result = run_single_task(task_id)
        results["tasks"].append(result)
        log_result(result)
        
        # Update counters
        if result["result"] == "pass":
            results["solved"] += 1
            print(f"✅ PASS ({result['time_seconds']:.2f}s)")
        elif result["result"] == "fail":
            results["failed"] += 1
            print(f"❌ FAIL (confidence: {result['confidence']:.0%})")
        elif result["result"] == "no_solver":
            results["no_solver"] += 1
            print(f"⏳ NO SOLVER")
        else:
            results["error"] += 1
            print(f"⚠️ ERROR: {result.get('error', 'Unknown')}")
    
    print(f"\n{'='*60}")
    print(f"BENCHMARK COMPLETE")
    print(f"{'='*60}")
    print(f"Solved: {results['solved']}/{results['total']} ({results['solved']/results['total']*100:.1f}%)")
    print(f"Failed: {results['failed']}")
    print(f"No solver: {results['no_solver']}")
    print(f"Errors: {results['error']}")
    print(f"{'='*60}\n")
    
    return results


def show_status():
    """Show current benchmark status."""
    tasks = get_all_evaluation_tasks()
    latest_scores = get_latest_score_per_task()
    
    solved = sum(1 for s in latest_scores.values() if s["result"] == "pass")
    failed = sum(1 for s in latest_scores.values() if s["result"] == "fail")
    no_solver = sum(1 for s in latest_scores.values() if s["result"] == "no_solver")
    error = sum(1 for s in latest_scores.values() if s["result"] in ["error", "timeout"])
    untested = len(tasks) - len(latest_scores)
    
    print(f"\n{'='*60}")
    print(f"ARC-AGI-2 BENCHMARK STATUS")
    print(f"{'='*60}")
    print(f"Total tasks: {len(tasks)}")
    print(f"Tested: {len(latest_scores)}")
    print(f"Untested: {untested}")
    print(f"")
    print(f"✅ Solved: {solved} ({solved/len(tasks)*100:.1f}%)")
    print(f"❌ Failed: {failed}")
    print(f"⏳ No solver: {no_solver}")
    print(f"⚠️ Errors: {error}")
    print(f"{'='*60}\n")
    
    # Show solved tasks
    if solved > 0:
        print("SOLVED TASKS:")
        for task_id, score in sorted(latest_scores.items()):
            if score["result"] == "pass":
                print(f"  ✅ {task_id} ({score['solver']}, {score['time_seconds']:.2f}s)")
    
    return {
        "total": len(tasks),
        "solved": solved,
        "failed": failed,
        "no_solver": no_solver,
        "error": error,
        "untested": untested
    }


def show_report():
    """Show detailed benchmark report."""
    tasks = get_all_evaluation_tasks()
    latest_scores = get_latest_score_per_task()
    all_scores = load_all_scores()
    
    print(f"\n{'='*70}")
    print(f"ARC-AGI-2 DETAILED BENCHMARK REPORT")
    print(f"{'='*70}\n")
    
    # Summary
    solved = [s for s in latest_scores.values() if s["result"] == "pass"]
    failed = [s for s in latest_scores.values() if s["result"] == "fail"]
    no_solver = [s for s in latest_scores.values() if s["result"] == "no_solver"]
    errors = [s for s in latest_scores.values() if s["result"] in ["error", "timeout"]]
    
    print("SUMMARY")
    print("-" * 40)
    print(f"Total tasks:        {len(tasks)}")
    print(f"Attempted:          {len(latest_scores)}")
    print(f"")
    print(f"✅ Solved:          {len(solved)} ({len(solved)/len(tasks)*100:.1f}%)")
    print(f"❌ Failed:          {len(failed)}")
    print(f"⏳ No solver:       {len(no_solver)}")
    print(f"⚠️ Errors:          {len(errors)}")
    print(f"📊 Untested:        {len(tasks) - len(latest_scores)}")
    print()
    
    # Human baseline comparison
    # ARC-AGI human baseline is typically around 85% on training, ~60-70% on eval
    print("HUMAN BASELINE COMPARISON")
    print("-" * 40)
    human_eval_baseline = 0.60  # ~60% on evaluation set
    our_rate = len(solved) / len(tasks) if tasks else 0
    print(f"Human baseline:     ~60% on evaluation")
    print(f"Our score:          {our_rate*100:.1f}%")
    print(f"Gap to human:       {(human_eval_baseline - our_rate)*100:.1f}%")
    print()
    
    # Failure categories
    if failed:
        print("FAILURE ANALYSIS")
        print("-" * 40)
        # Group by confidence level
        high_conf_fails = [f for f in failed if f["confidence"] >= 0.5]
        low_conf_fails = [f for f in failed if f["confidence"] < 0.5]
        print(f"High confidence fails (≥50%): {len(high_conf_fails)}")
        print(f"Low confidence fails (<50%):  {len(low_conf_fails)}")
        print()
    
    # Solved tasks detail
    if solved:
        print("SOLVED TASKS DETAIL")
        print("-" * 40)
        for score in sorted(solved, key=lambda x: x["task_id"]):
            print(f"  ✅ {score['task_id']}")
            print(f"     Solver: {score['solver']}")
            print(f"     Time: {score['time_seconds']:.2f}s")
            print()
    
    # Top performers (solvers that worked)
    if solved:
        print("TOP PERFORMING SOLVERS")
        print("-" * 40)
        solver_counts = {}
        for score in solved:
            solver = score["solver"]
            if solver not in solver_counts:
                solver_counts[solver] = 0
            solver_counts[solver] += 1
        
        for solver, count in sorted(solver_counts.items(), key=lambda x: -x[1]):
            print(f"  {solver}: {count} task(s) solved")
        print()
    
    # Attempt history
    print("ATTEMPT HISTORY")
    print("-" * 40)
    print(f"Total attempts logged: {len(all_scores)}")
    
    # Recent attempts
    recent = sorted(all_scores, key=lambda x: x["timestamp"], reverse=True)[:5]
    if recent:
        print("\nMost recent attempts:")
        for attempt in recent:
            icon = "✅" if attempt["result"] == "pass" else "❌" if attempt["result"] == "fail" else "⏳"
            print(f"  {icon} {attempt['task_id']} ({attempt['result']}) - {attempt['timestamp']}")
    
    print(f"\n{'='*70}\n")
    
    return {
        "total": len(tasks),
        "solved": len(solved),
        "failed": len(failed),
        "no_solver": len(no_solver),
        "errors": len(errors)
    }


def main():
    parser = argparse.ArgumentParser(description="ARC-AGI-2 Benchmark Runner")
    parser.add_argument("--run", action="store_true", help="Run full benchmark")
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--report", action="store_true", help="Show detailed report")
    parser.add_argument("--max-tasks", type=int, help="Maximum tasks to run")
    parser.add_argument("--skip-solved", action="store_true", help="Skip already solved tasks")
    
    args = parser.parse_args()
    
    # Ensure the-crypt directory exists
    SCORES_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    if args.run:
        run_full_benchmark(max_tasks=args.max_tasks, skip_solved=args.skip_solved)
    elif args.status:
        show_status()
    elif args.report:
        show_report()
    else:
        # Default to status
        show_status()


if __name__ == "__main__":
    main()
