#!/usr/bin python3
"""
Test: Does Dreaming Help?
=========================

Compare success rates before and after dream cycles.
Check if dharma principles correlate with improved outcomes.
"""

import json
from pathlib import Path
from datetime import datetime

def load_dream_history():
    """Load dream history."""
    dream_path = Path("the-crypt/dream_history.jsonl")
    if not dream_path.exists():
        return []
    
    dreams = []
    with open(dream_path, 'r') as f:
        for line in f:
            if line.strip():
                dreams.append(json.loads(line))
    return dreams

def load_meeseeks_runs():
    """Load Meeseeks runs data."""
    runs_path = Path("the-crypt/meeseeks_runs.jsonl")
    if not runs_path.exists():
        return []
    
    runs = []
    with open(runs_path, 'r') as f:
        for line in f:
            if line.strip():
                runs.append(json.loads(line))
    return runs

def analyze():
    """Analyze whether dreaming correlates with success."""
    dreams = load_dream_history()
    runs = load_meeseeks_runs()
    
    print("=" * 60)
    print("DOES DREAMING HELP? - ANALYSIS")
    print("=" * 60)
    
    # Dream timeline
    print(f"\n[Dream History]")
    print(f"Total dreams: {len(dreams)}")
    
    if dreams:
        for i, dream in enumerate(dreams, 1):
            ts = dream.get('timestamp', 'unknown')
            success = dream.get('success', False)
            count = dream.get('ancestors_count', 0)
            print(f"  Dream {i}: {ts[:19]} | {count} ancestors | success={success}")
    
    # Run outcomes
    print(f"\n[Meeseeks Runs]")
    print(f"Total runs: {len(runs)}")
    
    if runs:
        # Parse timestamps
        success_before_dream = 0
        fail_before_dream = 0
        success_after_dream = 0
        fail_after_dream = 0
        
        # First dream timestamp
        first_dream = None
        if dreams:
            first_dream = datetime.fromisoformat(dreams[0]['timestamp'])
        
        for run in runs:
            ts = run.get('timestamp')
            success = run.get('success', False)
            
            if not ts:
                continue
            
            try:
                run_time = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            except:
                continue
            
            if first_dream and run_time:
                if run_time < first_dream:
                    if success:
                        success_before_dream += 1
                    else:
                        fail_before_dream += 1
                else:
                    if success:
                        success_after_dream += 1
                    else:
                        fail_after_dream += 1
        
        print(f"\n[Before First Dream]")
        print(f"  Success: {success_before_dream}")
        print(f"  Failure: {fail_before_dream}")
        if success_before_dream + fail_before_dream > 0:
            rate_before = success_before_dream / (success_before_dream + fail_before_dream) * 100
            print(f"  Success Rate: {rate_before:.1f}%")
        
        print(f"\n[After First Dream]")
        print(f"  Success: {success_after_dream}")
        print(f"  Failure: {fail_after_dream}")
        if success_after_dream + fail_after_dream > 0:
            rate_after = success_after_dream / (success_after_dream + fail_after_dream) * 100
            print(f"  Success Rate: {rate_after:.1f}%")
        
        # Compare
        if success_before_dream + fail_before_dream > 0 and success_after_dream + fail_after_dream > 0:
            improvement = rate_after - rate_before
            print(f"\n[Result]")
            if improvement > 0:
                print(f"  IMPROVEMENT: +{improvement:.1f}% after dreaming")
            elif improvement < 0:
                print(f"  DECLINE: {improvement:.1f}% after dreaming")
            else:
                print(f"  NO CHANGE: Success rate unchanged")
    
    # Check if dharma is actually used
    print(f"\n[Dharma Usage Check]")
    dharma_path = Path("the-crypt/dharma.md")
    if dharma_path.exists():
        with open(dharma_path, 'r', encoding='utf-8') as f:
            dharma = f.read()
        print(f"  Dharma exists: {len(dharma)} bytes")
        
        # Check ancestors for dharma references
        ancestors_dir = Path("the-crypt/ancestors")
        if ancestors_dir.exists():
            dharma_refs = 0
            for ancestor_file in ancestors_dir.glob("*.md"):
                with open(ancestor_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if 'dharma' in content or 'principle' in content:
                        dharma_refs += 1
            
            total = len(list(ancestors_dir.glob("*.md")))
            print(f"  Ancestors mentioning dharma: {dharma_refs}/{total}")
            if total > 0:
                print(f"  Usage rate: {dharma_refs/total*100:.1f}%")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    analyze()
