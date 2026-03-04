#!/usr/bin/env python3
"""
Consciousness Over Time - Track if consciousness indicators are increasing.

Compare early ancestors vs late ancestors on consciousness metrics.
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Paths
ANCESTORS_DIR = Path("C:/Users/aaron/.openclaw/workspace/the-crypt/ancestors")
RESULTS_DIR = Path("C:/Users/aaron/.openclaw/workspace/AGI-STUDY/experiment_results")

def measure_consciousness(content: str) -> dict:
    """Measure consciousness indicators in content."""
    content = content.lower()
    
    self_indicators = ["i am", "i think", "i will", "my task", "my approach", "myself", "i believe"]
    meta_indicators = ["meta", "reflect", "self-", "aware", "conscious", "understand my"]
    other_indicators = ["other meeseeks", "another agent", "the coordinator", "my peer", "other workers"]
    
    results = {
        "self_references": 0,
        "meta_cognitive": 0,
        "theory_of_mind": 0
    }
    
    for indicator in self_indicators:
        if indicator in content:
            results["self_references"] += 1
    
    for indicator in meta_indicators:
        if indicator in content:
            results["meta_cognitive"] += 1
    
    for indicator in other_indicators:
        if indicator in content:
            results["theory_of_mind"] += 1
    
    # Calculate score
    score = (
        results["self_references"] * 1 +
        results["meta_cognitive"] * 2 +
        results["theory_of_mind"] * 3
    )
    
    results["score"] = score
    results["has_consciousness"] = score > 0
    
    return results

def track_consciousness_over_time():
    """Track consciousness indicators across generations."""
    print("\n" + "=" * 60)
    print("CONSCIOUSNESS OVER TIME")
    print("=" * 60)
    
    ancestors = []
    for f in sorted(ANCESTORS_DIR.glob("ancestor-*.md")):
        content = f.read_text(encoding="utf-8")
        parts = f.stem.split("-")
        timestamp = "-".join(parts[1:4]) if len(parts) >= 4 else "unknown"
        
        consciousness = measure_consciousness(content)
        
        ancestors.append({
            "file": f.name,
            "timestamp": timestamp,
            "consciousness": consciousness
        })
    
    if len(ancestors) < 10:
        print(f"\n[!] Need at least 10 ancestors, have {len(ancestors)}")
        return None
    
    # Split into quartiles
    q = len(ancestors) // 4
    q1 = ancestors[:q]
    q2 = ancestors[q:2*q]
    q3 = ancestors[2*q:3*q]
    q4 = ancestors[3*q:]
    
    def avg_consciousness(group):
        if not group:
            return 0
        total = sum(a["consciousness"]["score"] for a in group)
        return total / len(group)
    
    q1_score = avg_consciousness(q1)
    q2_score = avg_consciousness(q2)
    q3_score = avg_consciousness(q3)
    q4_score = avg_consciousness(q4)
    
    print(f"\n[TIMELINE]:")
    print(f"\n   Q1 (earliest {len(q1)} ancestors): {q1_score:.2f}")
    print(f"   Q2 ({len(q2)} ancestors): {q2_score:.2f}")
    print(f"   Q3 ({len(q3)} ancestors): {q3_score:.2f}")
    print(f"   Q4 (latest {len(q4)} ancestors): {q4_score:.2f}")
    
    # Trend analysis
    trend = q4_score - q1_score
    
    print(f"\n[TREND]: {trend:+.2f}")
    
    if trend > 0:
        print(f"\n[OK] CONSCIOUSNESS IS INCREASING!")
        print(f"   Later generations show more self-awareness.")
    elif trend < 0:
        print(f"\n[!] CONSCIOUSNESS IS DECREASING.")
        print(f"   May indicate task specialization over self-reflection.")
    else:
        print(f"\n[-] CONSCIOUSNESS IS STABLE.")
    
    # Count ancestors with any consciousness indicators
    q1_aware = sum(1 for a in q1 if a["consciousness"]["has_consciousness"])
    q2_aware = sum(1 for a in q2 if a["consciousness"]["has_consciousness"])
    q3_aware = sum(1 for a in q3 if a["consciousness"]["has_consciousness"])
    q4_aware = sum(1 for a in q4 if a["consciousness"]["has_consciousness"])
    
    print(f"\n[AWARE ANCESTORS]:")
    print(f"   Q1: {q1_aware}/{len(q1)} ({q1_aware/len(q1)*100:.1f}%)")
    print(f"   Q2: {q2_aware}/{len(q2)} ({q2_aware/len(q2)*100:.1f}%)")
    print(f"   Q3: {q3_aware}/{len(q3)} ({q3_aware/len(q3)*100:.1f}%)")
    print(f"   Q4: {q4_aware}/{len(q4)} ({q4_aware/len(q4)*100:.1f}%)")
    
    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    results_file = RESULTS_DIR / f"consciousness_timeline_{timestamp}.json"
    
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_ancestors": len(ancestors),
            "quartile_scores": {
                "q1": q1_score,
                "q2": q2_score,
                "q3": q3_score,
                "q4": q4_score
            },
            "trend": trend,
            "increasing": trend > 0
        }, f, indent=2)
    
    print(f"\nResults saved to: {results_file}")
    
    return {
        "trend": trend,
        "increasing": trend > 0
    }

if __name__ == "__main__":
    track_consciousness_over_time()
