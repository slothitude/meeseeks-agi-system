#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARC-AGI-2 Evaluation - Check what patterns we can solve

Current solver has task-specific solutions:
- 00576224 - Pattern Tiling
- 0d3d703e - Color Mapping
- 017c7c7b - Vertical Extension
- 0520fde7 - Mask-based Extraction
- 137eaa0f - Diagonal Anchor Extraction

This script checks which evaluation tasks have similar patterns.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import numpy as np

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def load_task(filepath):
    """Load a single task from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def analyze_task(task_id, task_data):
    """
    Analyze a task to identify its pattern type.

    Returns:
        dict with pattern analysis
    """
    analysis = {
        "task_id": task_id,
        "num_train": len(task_data.get('train', [])),
        "num_test": len(task_data.get('test', [])),
        "pattern_hints": [],
        "complexity": "unknown"
    }

    # Analyze training examples
    for i, example in enumerate(task_data.get('train', [])):
        inp = np.array(example.get('input', []))
        out = np.array(example.get('output', []))

        # Check size relationship
        in_size = inp.shape
        out_size = out.shape

        if out_size == (3, 3):
            analysis["pattern_hints"].append("3x3 output")
        elif out_size[0] == in_size[0] * 3 and out_size[1] == in_size[1] * 3:
            analysis["pattern_hints"].append("3x tiling")
        elif out_size == in_size:
            analysis["pattern_hints"].append("same size (color/shape transform)")

        # Check for color 5 (marker)
        if 5 in inp:
            analysis["pattern_hints"].append("color 5 marker")

        # Check for color mapping (same size, different colors)
        if out_size == in_size:
            unique_in = set(inp.flatten())
            unique_out = set(out.flatten())
            if unique_in != unique_out:
                analysis["pattern_hints"].append("color mapping")

    # Estimate complexity
    if len(analysis["pattern_hints"]) == 0:
        analysis["complexity"] = "unknown"
    elif len(analysis["pattern_hints"]) <= 2:
        analysis["complexity"] = "simple"
    else:
        analysis["complexity"] = "complex"

    return analysis

def run_analysis():
    """Analyze all evaluation tasks."""
    eval_dir = Path("C:/Users/aaron/.openclaw/workspace/ARC-AGI-2/data/evaluation")
    results_dir = Path("C:/Users/aaron/.openclaw/workspace/AGI-STUDY/results")
    results_dir.mkdir(exist_ok=True)

    tasks = sorted(eval_dir.glob("*.json"))
    total = len(tasks)

    # Pattern categories
    categories = {
        "3x3_output": [],
        "tiling": [],
        "color_mapping": [],
        "marker_based": [],
        "same_size": [],
        "unknown": []
    }

    print(f"ARC-AGI-2 Pattern Analysis")
    print(f"=" * 50)
    print(f"Total evaluation tasks: {total}")
    print()

    for i, task_path in enumerate(tasks, 1):
        task_id = task_path.stem
        task_data = load_task(task_path)

        analysis = analyze_task(task_id, task_data)

        # Categorize
        hints = analysis["pattern_hints"]

        if "3x3 output" in hints:
            categories["3x3_output"].append(task_id)
        if "3x tiling" in hints:
            categories["tiling"].append(task_id)
        if "color mapping" in hints:
            categories["color_mapping"].append(task_id)
        if "color 5 marker" in hints:
            categories["marker_based"].append(task_id)
        if "same size (color/shape transform)" in hints:
            categories["same_size"].append(task_id)
        if not hints:
            categories["unknown"].append(task_id)

        if i % 20 == 0:
            print(f"Analyzed {i}/{total}...")

    # Summary
    print()
    print("=" * 50)
    print("PATTERN ANALYSIS RESULTS")
    print("=" * 50)

    print(f"\n📊 Pattern Categories:\n")
    for category, tasks in categories.items():
        print(f"  {category}: {len(tasks)} tasks")
        if len(tasks) <= 5:
            print(f"    → {', '.join(tasks)}")

    # Tasks we can probably solve (similar to training)
    print(f"\n🎯 Likely Solvable (based on known patterns):\n")

    solvable = []
    # 3x3 output with markers = likely similar to 137eaa0f
    for task_id in categories["3x3_output"]:
        if task_id in categories["marker_based"]:
            solvable.append(task_id)

    print(f"  Diagonal anchor extraction pattern: {len(solvable)} tasks")
    if len(solvable) <= 10:
        print(f"    → {', '.join(solvable)}")

    tiling_solvable = categories["tiling"]
    print(f"\n  Tiling pattern: {len(tiling_solvable)} tasks")
    if len(tiling_solvable) <= 10:
        print(f"    → {', '.join(tiling_solvable)}")

    color_solvable = categories["color_mapping"]
    print(f"\n  Color mapping pattern: {len(color_solvable)} tasks")
    if len(color_solvable) <= 10:
        print(f"    → {', '.join(color_solvable)}")

    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_tasks": total,
        "categories": {k: len(v) for k, v in categories.items()},
        "category_members": categories,
        "estimated_solvable": len(solvable) + len(tiling_solvable) + len(color_solvable)
    }

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    results_file = results_dir / f"pattern_analysis_{timestamp}.json"

    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n📄 Full results saved to: {results_file}")

    # Next steps
    print(f"\n" + "=" * 50)
    print("NEXT STEPS")
    print("=" * 50)
    print("""
1. Run solver on tiling tasks (pattern: 00576224)
2. Run solver on color mapping tasks (pattern: 0d3d703e)
3. Run solver on 3x3 marker tasks (pattern: 137eaa0f)
4. For unknown patterns, spawn Meeseeks to analyze
5. Build pattern library from solved tasks
    """)

    return results

if __name__ == "__main__":
    run_analysis()
