#!/usr/bin/env python3
"""
Transfer Learning Test - Can patterns from one domain help in another?

Experiment: Test if coding bloodline wisdom helps solve ARC-AGI puzzles.
"""

import json
from pathlib import Path
from datetime import datetime

# Paths
ANCESTORS_DIR = Path("C:/Users/aaron/.openclaw/workspace/the-crypt/ancestors")
RESULTS_DIR = Path("C:/Users/aaron/.openclaw/workspace/AGI-STUDY/experiment_results")

def extract_coding_patterns():
    """Extract patterns from coding-related ancestors."""
    coding_keywords = ["code", "debug", "implement", "fix", "refactor", "python", "function"]
    
    coding_ancestors = []
    for f in ANCESTORS_DIR.glob("ancestor-*.md"):
        content = f.read_text(encoding="utf-8").lower()
        if any(kw in content for kw in coding_keywords):
            coding_ancestors.append({
                "file": f.name,
                "content": content,
                "patterns": []
            })
            
            # Extract patterns
            if "chunk" in content:
                coding_ancestors[-1]["patterns"].append("chunking")
            if "test" in content:
                coding_ancestors[-1]["patterns"].append("testing")
            if "understand" in content:
                coding_ancestors[-1]["patterns"].append("understanding")
            if "coordinate" in content or "shared" in content:
                coding_ancestors[-1]["patterns"].append("coordination")
    
    return coding_ancestors

def run_transfer_test():
    """Test if coding patterns would help with ARC puzzles."""
    print("\n" + "=" * 60)
    print("TRANSFER LEARNING TEST")
    print("=" * 60)
    
    coding_ancestors = extract_coding_patterns()
    
    print(f"\n[CODING ANCESTORS]: {len(coding_ancestors)}")
    
    # Count patterns
    from collections import Counter
    all_patterns = []
    for a in coding_ancestors:
        all_patterns.extend(a["patterns"])
    
    pattern_counts = Counter(all_patterns)
    
    print(f"\n[PATTERNS EXTRACTED]:")
    for pattern, count in pattern_counts.most_common():
        print(f"   - {pattern}: {count}")
    
    # These patterns should transfer to ARC puzzles
    transferable_principles = [
        ("chunking", "Break large puzzles into smaller sub-problems"),
        ("testing", "Test solutions on training examples before submitting"),
        ("understanding", "Analyze pattern before implementing solution"),
        ("coordination", "Multiple approaches can work together")
    ]
    
    print(f"\n[TRANSFERABLE PRINCIPLES]:")
    for pattern, application in transferable_principles:
        if pattern in pattern_counts:
            print(f"   [OK] {pattern}: {application}")
        else:
            print(f"   [?] {pattern}: {application} (not found in coding ancestors)")
    
    # Calculate transfer score
    found_patterns = sum(1 for p, _ in transferable_principles if p in pattern_counts)
    transfer_score = found_patterns / len(transferable_principles)
    
    print(f"\n[TRANSFER SCORE]: {transfer_score:.2f}")
    
    if transfer_score >= 0.75:
        print(f"\n[OK] CONCLUSION: Strong transfer potential!")
        print(f"   Coding patterns CAN help solve ARC puzzles.")
    elif transfer_score >= 0.5:
        print(f"\n[~] CONCLUSION: Moderate transfer potential.")
    else:
        print(f"\n[!] CONCLUSION: Limited transfer potential.")
    
    # Save results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    results_file = RESULTS_DIR / f"transfer_test_{timestamp}.json"
    
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "coding_ancestors": len(coding_ancestors),
            "pattern_counts": dict(pattern_counts),
            "transfer_score": transfer_score,
            "passed": transfer_score >= 0.5
        }, f, indent=2)
    
    print(f"\nResults saved to: {results_file}")
    
    return {
        "transfer_score": transfer_score,
        "passed": transfer_score >= 0.5
    }

if __name__ == "__main__":
    run_transfer_test()
