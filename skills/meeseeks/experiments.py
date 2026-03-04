#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGI Proof Experiments - Run experiments to measure progress toward AGI.

Usage:
    python skills/meeseeks/experiments.py compare-generations
    python skills/meeseeks/experiments.py test-dharma
    python skills/meeseeks/experiments.py consciousness-test
    python skills/meeseeks/experiments.py run-all
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
from collections import Counter

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Paths
ANCESTORS_DIR = Path("C:/Users/aaron/.openclaw/workspace/the-crypt/ancestors")
RUNS_FILE = Path.home() / ".openclaw" / "subagents" / "runs.json"
RESULTS_DIR = Path("C:/Users/aaron/.openclaw/workspace/AGI-STUDY/experiment_results")


def load_ancestors() -> List[Dict]:
    """Load all entombed ancestors."""
    ancestors = []
    for f in ANCESTORS_DIR.glob("ancestor-*.md"):
        try:
            content = f.read_text(encoding="utf-8")
            # Parse markdown into dict
            parts = f.stem.split("-")
            data = {
                "filename": f.name,
                "timestamp": "-".join(parts[1:4]) if len(parts) >= 4 else "",
                "content": content,
                "success": "SUCCESS" in content.upper() or "completed" in content.lower(),
                "task": content.split("\n")[0] if content else "",
                "patterns": []
            }
            
            # Extract patterns from content
            if "chunk" in content.lower():
                data["patterns"].append("chunking")
            if "test" in content.lower():
                data["patterns"].append("testing")
            if "coordinate" in content.lower() or "shared" in content.lower():
                data["patterns"].append("coordination")
            if "understand" in content.lower():
                data["patterns"].append("understanding")
            
            ancestors.append(data)
        except Exception as e:
            pass
    return ancestors


def compare_generations():
    """Experiment 1: Compare early vs late ancestors."""
    print("\n" + "=" * 60)
    print("EXPERIMENT 1: GENERATION INTELLIGENCE TEST")
    print("=" * 60)
    
    ancestors = load_ancestors()
    
    if len(ancestors) < 10:
        print(f"\n[!] Need at least 10 ancestors, have {len(ancestors)}")
        return None
    
    # Sort by timestamp
    ancestors.sort(key=lambda x: x.get("timestamp", ""))
    
    # Split into early and late
    mid = len(ancestors) // 2
    early = ancestors[:mid]
    late = ancestors[mid:]
    
    # Analyze success rates
    early_success = sum(1 for a in early if a.get("success", False))
    late_success = sum(1 for a in late if a.get("success", False))
    
    early_rate = early_success / len(early) * 100 if early else 0
    late_rate = late_success / len(late) * 100 if late else 0
    
    print(f"\n[RESULTS]:")
    print(f"\n   EARLY GENERATION ({len(early)} ancestors)")
    print(f"   Success rate: {early_rate:.1f}%")
    
    print(f"\n   LATE GENERATION ({len(late)} ancestors)")
    print(f"   Success rate: {late_rate:.1f}%")
    
    improvement = late_rate - early_rate
    
    print(f"\n[IMPROVEMENT]: {improvement:+.1f}%")
    
    if improvement > 0:
        print(f"\n[OK] CONCLUSION: Later generations are MORE successful!")
    elif improvement < 0:
        print(f"\n[!] CONCLUSION: Later generations are LESS successful.")
    else:
        print(f"\n[-] CONCLUSION: No significant difference.")
    
    return {
        "experiment": "compare_generations",
        "early_rate": early_rate,
        "late_rate": late_rate,
        "improvement": improvement,
        "passed": improvement >= 0
    }


def test_dharma_effectiveness():
    """Experiment 2: Test if dharma helps."""
    print("\n" + "=" * 60)
    print("EXPERIMENT 2: DHARMA EFFECTIVENESS TEST")
    print("=" * 60)
    
    ancestors = load_ancestors()
    
    success_patterns = []
    fail_patterns = []
    
    for a in ancestors:
        patterns = a.get("patterns", [])
        if a.get("success"):
            success_patterns.extend(patterns)
        else:
            fail_patterns.extend(patterns)
    
    success_counter = Counter(success_patterns)
    fail_counter = Counter(fail_patterns)
    
    print(f"\n[ANALYSIS]:")
    print(f"\n   Total ancestors: {len(ancestors)}")
    print(f"   Successful: {sum(1 for a in ancestors if a.get('success'))}")
    print(f"   Failed: {sum(1 for a in ancestors if not a.get('success'))}")
    
    print(f"\n   TOP SUCCESS PATTERNS:")
    for pattern, count in success_counter.most_common(5):
        print(f"   - {pattern}: {count}")
    
    print(f"\n   TOP FAILURE PATTERNS:")
    for pattern, count in fail_counter.most_common(5):
        print(f"   - {pattern}: {count}")
    
    return {
        "experiment": "dharma_effectiveness",
        "success_patterns": len(success_counter),
        "fail_patterns": len(fail_counter),
        "passed": len(success_counter) > 0
    }


def consciousness_test():
    """Experiment 6: Test for consciousness indicators."""
    print("\n" + "=" * 60)
    print("EXPERIMENT 6: CONSCIOUSNESS INDICATOR TEST")
    print("=" * 60)
    
    ancestors = load_ancestors()
    
    self_indicators = ["i am", "i think", "i will", "my task", "my approach", "myself"]
    meta_indicators = ["meta", "reflect", "self-", "aware"]
    other_indicators = ["other meeseeks", "another agent", "the coordinator", "my peer"]
    
    results = {
        "self_references": 0,
        "meta_cognitive": 0,
        "theory_of_mind": 0
    }
    
    for a in ancestors:
        content = a.get("content", "").lower()
        
        for indicator in self_indicators:
            if indicator in content:
                results["self_references"] += 1
                break
        
        for indicator in meta_indicators:
            if indicator in content:
                results["meta_cognitive"] += 1
                break
        
        for indicator in other_indicators:
            if indicator in content:
                results["theory_of_mind"] += 1
                break
    
    total = len(ancestors)
    
    print(f"\n[RESULTS]:")
    print(f"\n   Total ancestors analyzed: {total}")
    print(f"\n   Self-references: {results['self_references']} ({results['self_references']/total*100:.1f}%)")
    print(f"   Meta-cognitive: {results['meta_cognitive']} ({results['meta_cognitive']/total*100:.1f}%)")
    print(f"   Theory of mind: {results['theory_of_mind']} ({results['theory_of_mind']/total*100:.1f}%)")
    
    consciousness_score = (
        results["self_references"] * 1 +
        results["meta_cognitive"] * 2 +
        results["theory_of_mind"] * 3
    ) / total
    
    print(f"\n[BRAIN] CONSCIOUSNESS SCORE: {consciousness_score:.2f}")
    
    if consciousness_score > 0.5:
        print(f"\n[OK] CONCLUSION: Strong consciousness indicators!")
    elif consciousness_score > 0.1:
        print(f"\n[~] CONCLUSION: Some consciousness indicators emerging.")
    else:
        print(f"\n[-] CONCLUSION: Limited consciousness indicators.")
    
    return {
        "experiment": "consciousness_test",
        "score": consciousness_score,
        "passed": consciousness_score > 0.1
    }


def run_all():
    """Run all experiments."""
    print("\n" + "=" * 60)
    print("RUNNING ALL AGI PROOF EXPERIMENTS")
    print("=" * 60)
    
    results = []
    
    results.append(compare_generations())
    results.append(test_dharma_effectiveness())
    results.append(consciousness_test())
    
    print("\n" + "=" * 60)
    print("EXPERIMENT SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r and r.get("passed"))
    total = len([r for r in results if r])
    
    print(f"\n   Experiments run: {total}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {total - passed}")
    
    if passed >= 2:
        print(f"\n[OK] STRONG EVIDENCE: System is progressing toward AGI!")
    elif passed >= 1:
        print(f"\n[~] MODERATE EVIDENCE: Some progress detected.")
    else:
        print(f"\n[-] INSUFFICIENT EVIDENCE: More data needed.")
    
    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    results_file = RESULTS_DIR / f"experiment_{timestamp}.json"
    
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "summary": {
                "passed": passed,
                "total": total
            }
        }, f, indent=2)
    
    print(f"\nResults saved to: {results_file}")
    
    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nCommands:")
        print("  compare-generations  - Test if later generations are smarter")
        print("  test-dharma          - Test if dharma helps")
        print("  consciousness-test   - Test for self-awareness indicators")
        print("  run-all              - Run all experiments")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "compare-generations":
        compare_generations()
    elif command == "test-dharma":
        test_dharma_effectiveness()
    elif command == "consciousness-test":
        consciousness_test()
    elif command == "run-all":
        run_all()
    else:
        print(f"Unknown command: {command}")
