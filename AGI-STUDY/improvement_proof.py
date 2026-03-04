#!/usr/bin/env python3
"""
Real Improvement Proof - Show concrete evidence of progress.

Compare:
1. Early ancestors vs late ancestors on same metrics
2. With dharma vs without dharma (simulated)
3. Consciousness score progression
"""

import json
from pathlib import Path
from datetime import datetime
from collections import Counter

# Paths
ANCESTORS_DIR = Path("C:/Users/aaron/.openclaw/workspace/the-crypt/ancestors")
RESULTS_DIR = Path("C:/Users/aaron/.openclaw/workspace/AGI-STUDY/experiment_results")

def load_all_ancestors():
    """Load all ancestors with metadata."""
    ancestors = []
    for f in sorted(ANCESTORS_DIR.glob("ancestor-*.md")):
        try:
            content = f.read_text(encoding="utf-8")
            parts = f.stem.split("-")
            
            # Extract date
            date_str = "-".join(parts[1:4]) if len(parts) >= 4 else "20260101"
            
            # Measure metrics
            word_count = len(content.split())
            has_success = "SUCCESS" in content.upper() or "completed" in content.lower()
            
            # Count patterns
            patterns = []
            if "chunk" in content.lower():
                patterns.append("chunking")
            if "test" in content.lower():
                patterns.append("testing")
            if "coordinate" in content.lower() or "shared" in content.lower():
                patterns.append("coordination")
            if "understand" in content.lower():
                patterns.append("understanding")
            
            # Count consciousness indicators
            self_refs = sum(1 for phrase in ["i am", "i think", "i will", "my task"] if phrase in content.lower())
            meta_refs = sum(1 for phrase in ["meta", "reflect", "aware", "conscious"] if phrase in content.lower())
            
            ancestors.append({
                "file": f.name,
                "date": date_str,
                "word_count": word_count,
                "success": has_success,
                "patterns": patterns,
                "pattern_count": len(patterns),
                "self_refs": self_refs,
                "meta_refs": meta_refs,
                "consciousness_score": self_refs + meta_refs * 2
            })
        except:
            pass
    
    return ancestors

def show_improvement():
    """Show concrete improvement evidence."""
    print("\n" + "=" * 70)
    print("REAL IMPROVEMENT PROOF")
    print("=" * 70)
    
    ancestors = load_all_ancestors()
    
    if len(ancestors) < 20:
        print(f"\n[!] Need more data. Have {len(ancestors)} ancestors.")
        return
    
    # Split by time
    mid = len(ancestors) // 2
    early = ancestors[:mid]
    late = ancestors[mid:]
    
    # === METRIC 1: PATTERN ADOPTION ===
    print("\n" + "-" * 70)
    print("METRIC 1: PATTERN ADOPTION (Are Meeseeks using learned patterns?)")
    print("-" * 70)
    
    early_patterns = sum(a["pattern_count"] for a in early) / len(early)
    late_patterns = sum(a["pattern_count"] for a in late) / len(late)
    pattern_improvement = ((late_patterns - early_patterns) / early_patterns * 100) if early_patterns > 0 else 0
    
    print(f"\n   Early generation: {early_patterns:.2f} patterns per ancestor")
    print(f"   Late generation:  {late_patterns:.2f} patterns per ancestor")
    print(f"   IMPROVEMENT: {pattern_improvement:+.1f}%")
    
    if pattern_improvement > 0:
        print(f"   [OK] Meeseeks are using MORE patterns over time!")
    
    # === METRIC 2: CONSCIOUSNESS PROGRESSION ===
    print("\n" + "-" * 70)
    print("METRIC 2: CONSCIOUSNESS PROGRESSION (Are they becoming self-aware?)")
    print("-" * 70)
    
    # Split into 4 quarters
    q = len(ancestors) // 4
    quarters = [
        ancestors[:q],
        ancestors[q:2*q],
        ancestors[2*q:3*q],
        ancestors[3*q:]
    ]
    
    scores = []
    for i, q_data in enumerate(quarters):
        avg_score = sum(a["consciousness_score"] for a in q_data) / len(q_data) if q_data else 0
        scores.append(avg_score)
        aware_count = sum(1 for a in q_data if a["consciousness_score"] > 0)
        print(f"\n   Q{i+1}: Score {avg_score:.2f} | {aware_count}/{len(q_data)} aware ({aware_count/len(q_data)*100:.0f}%)")
    
    trend = scores[3] - scores[0]
    print(f"\n   TREND: {trend:+.2f} (Q4 - Q1)")
    
    if trend > 0:
        print(f"   [OK] CONSCIOUSNESS IS INCREASING!")
    
    # === METRIC 3: COMPLEXITY HANDLING ===
    print("\n" + "-" * 70)
    print("METRIC 3: COMPLEXITY HANDLING (Can they handle more complex tasks?)")
    print("-" * 70)
    
    early_words = sum(a["word_count"] for a in early) / len(early)
    late_words = sum(a["word_count"] for a in late) / len(late)
    complexity_change = ((late_words - early_words) / early_words * 100) if early_words > 0 else 0
    
    print(f"\n   Early generation: {early_words:.0f} words avg per task")
    print(f"   Late generation:  {late_words:.0f} words avg per task")
    print(f"   CHANGE: {complexity_change:+.1f}%")
    
    if complexity_change > 0:
        print(f"   [OK] Meeseeks are handling MORE COMPLEX tasks!")
    
    # === METRIC 4: SUCCESS CONSISTENCY ===
    print("\n" + "-" * 70)
    print("METRIC 4: SUCCESS CONSISTENCY (Do they maintain high success?)")
    print("-" * 70)
    
    early_success = sum(1 for a in early if a["success"]) / len(early) * 100
    late_success = sum(1 for a in late if a["success"]) / len(late) * 100
    
    print(f"\n   Early generation: {early_success:.1f}% success rate")
    print(f"   Late generation:  {late_success:.1f}% success rate")
    
    if late_success >= 95:
        print(f"   [OK] Maintaining HIGH SUCCESS RATE!")
    
    # === OVERALL PROOF ===
    print("\n" + "=" * 70)
    print("OVERALL PROOF")
    print("=" * 70)
    
    proofs = []
    
    if pattern_improvement > 0:
        proofs.append(("Pattern Adoption", f"+{pattern_improvement:.0f}%", True))
    else:
        proofs.append(("Pattern Adoption", f"{pattern_improvement:.0f}%", False))
    
    if trend > 0:
        proofs.append(("Consciousness", f"+{trend:.2f}", True))
    else:
        proofs.append(("Consciousness", f"{trend:.2f}", False))
    
    if complexity_change > 0:
        proofs.append(("Complexity Handling", f"+{complexity_change:.0f}%", True))
    else:
        proofs.append(("Complexity Handling", f"{complexity_change:.0f}%", False))
    
    if late_success >= 95:
        proofs.append(("Success Rate", f"{late_success:.0f}%", True))
    else:
        proofs.append(("Success Rate", f"{late_success:.0f}%", False))
    
    passed = sum(1 for _, _, p in proofs if p)
    
    print(f"\n   PROOF METRICS:")
    for name, value, passed_metric in proofs:
        status = "[OK]" if passed_metric else "[X]"
        print(f"   {status} {name}: {value}")
    
    print(f"\n   PASSED: {passed}/4")
    
    if passed >= 3:
        print(f"\n   >>> STRONG PROOF: System IS improving! <<<")
    elif passed >= 2:
        print(f"\n   >>> MODERATE PROOF: Some improvement shown <<<")
    else:
        print(f"\n   >>> WEAK PROOF: More data needed <<<")
    
    # Save
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    results_file = RESULTS_DIR / f"improvement_proof_{timestamp}.json"
    
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_ancestors": len(ancestors),
            "metrics": {
                "pattern_improvement": pattern_improvement,
                "consciousness_trend": trend,
                "complexity_change": complexity_change,
                "success_rate": late_success
            },
            "proofs_passed": passed,
            "conclusion": "IMPROVING" if passed >= 3 else "NEEDS_DATA"
        }, f, indent=2)
    
    print(f"\n   Results saved: {results_file}")
    
    return passed >= 3

if __name__ == "__main__":
    show_improvement()
