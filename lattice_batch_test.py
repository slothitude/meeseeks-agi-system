#!/usr/bin/env python3
"""
Lattice Batch Test - 10 tasks per bloodline

Controlled A/B test to establish baseline.
Total: 30 spawns (10 power-of-2, 10 prime, 10 composite)
"""

import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

# Test task (IDENTICAL for all)
TEST_TASK = "Count the number of .py files in the_body/skills/ directory. Return only the number."

# Bloodlines to test
BLOODLINES = [
    {"n": 2, "bloodline": "power-of-2", "type": "coder"},
    {"n": 7, "bloodline": "prime", "type": "searcher"},
    {"n": 12, "bloodline": "composite", "type": "deployer"},
]

# Results storage
RESULTS_FILE = Path("lattice_batch_results.json")

def load_results():
    if RESULTS_FILE.exists():
        return json.loads(RESULTS_FILE.read_text())
    return {"runs": [], "summary": {}}

def save_results(data):
    RESULTS_FILE.write_text(json.dumps(data, indent=2))

def record_run(bloodline_config, run_num, success, runtime_ms, tokens, result_preview):
    """Record a single run"""
    data = load_results()
    
    run_record = {
        "timestamp": datetime.now().isoformat(),
        "run_num": run_num,
        "coordinate_n": bloodline_config["n"],
        "bloodline": bloodline_config["bloodline"],
        "meeseeks_type": bloodline_config["type"],
        "task": TEST_TASK,
        "success": success,
        "runtime_ms": runtime_ms,
        "tokens": tokens,
        "result_preview": result_preview[:100] if result_preview else None
    }
    
    data["runs"].append(run_record)
    
    # Update summary
    bl = bloodline_config["bloodline"]
    if bl not in data["summary"]:
        data["summary"][bl] = {
            "coordinate_n": bloodline_config["n"],
            "total": 0,
            "successes": 0,
            "total_runtime_ms": 0,
            "total_tokens": 0
        }
    
    data["summary"][bl]["total"] += 1
    if success:
        data["summary"][bl]["successes"] += 1
    data["summary"][bl]["total_runtime_ms"] += runtime_ms
    data["summary"][bl]["total_tokens"] += tokens
    
    save_results(data)
    return run_record

def print_summary():
    """Print current summary"""
    data = load_results()
    
    print("\n" + "=" * 60)
    print("BATCH TEST SUMMARY")
    print("=" * 60)
    
    for bl, stats in data["summary"].items():
        total = stats["total"]
        if total == 0:
            continue
        
        success_rate = stats["successes"] / total * 100
        avg_runtime = stats["total_runtime_ms"] / total
        avg_tokens = stats["total_tokens"] / total
        
        print(f"\n{bl.upper()} (n={stats['coordinate_n']})")
        print(f"  Runs: {total}/10")
        print(f"  Success rate: {success_rate:.0f}%")
        print(f"  Avg runtime: {avg_runtime:.0f}ms")
        print(f"  Avg tokens: {avg_tokens:.0f}")

def get_instructions():
    return """
LATTICE BATCH TEST INSTRUCTIONS
===============================

Goal: 10 runs per bloodline (30 total)

Test task: "Count the number of .py files in the_body/skills/ directory. Return only the number."

Bloodlines:
  - power-of-2 (n=2): Use 'coder' type
  - prime (n=7): Use 'searcher' type  
  - composite (n=12): Use 'deployer' type

To run a single test:
  python lattice_batch_test.py --run <bloodline> <num>

Example:
  python lattice_batch_test.py --run power-of-2 1
  python lattice_batch_test.py --run prime 5

After each run, record:
  - Did it succeed? (y/n)
  - Runtime (from session)
  - Tokens (from session)
  - Result (the number it returned)

Check progress:
  python lattice_batch_test.py --summary

Clear and restart:
  python lattice_batch_test.py --clear

Expected time: ~1 minute per run, 30 minutes total
"""

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print(get_instructions())
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "--info":
        print(get_instructions())
    
    elif cmd == "--summary":
        print_summary()
    
    elif cmd == "--clear":
        save_results({"runs": [], "summary": {}})
        print("Cleared all results")
    
    elif cmd == "--run":
        if len(sys.argv) < 5:
            print("Usage: --run <bloodline> <num> <success> <runtime_ms> <tokens> [result]")
            sys.exit(1)
        
        bloodline = sys.argv[2]
        num = int(sys.argv[3])
        success = sys.argv[4].lower() == "y"
        runtime = float(sys.argv[5])
        tokens = int(sys.argv[6])
        result = sys.argv[7] if len(sys.argv) > 7 else ""
        
        # Find config
        config = next((b for b in BLOODLINES if b["bloodline"] == bloodline), None)
        if not config:
            print(f"Unknown bloodline: {bloodline}")
            sys.exit(1)
        
        record = record_run(config, num, success, runtime, tokens, result)
        print(f"Recorded: {record}")
        print_summary()
    
    else:
        print(f"Unknown command: {cmd}")
        print("Commands: --info, --summary, --run, --clear")
