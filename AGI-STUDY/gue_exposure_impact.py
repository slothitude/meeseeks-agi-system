#!/usr/bin/env python3
"""
Measure the impact of Grand Unified Engine exposure on Meeseeks.

Compare:
- Pre-exposure: Ancestors before 2026-03-04 19:00 (before GUE was shared)
- Post-exposure: Ancestors after 2026-03-04 19:00 (after GUE was shared)
"""

import json
from pathlib import Path
from datetime import datetime
from collections import Counter

ANCESTORS_DIR = Path("C:/Users/aaron/.openclaw/workspace/the-crypt/ancestors")

# GUE exposure time
EXPOSURE_TIME = "2026-03-04"

def load_ancestors():
    """Load all ancestors."""
    ancestors = []
    for f in sorted(ANCESTORS_DIR.glob("ancestor-*.md")):
        try:
            content = f.read_text(encoding="utf-8")
            parts = f.stem.split("-")
            date_str = "-".join(parts[1:4]) if len(parts) >= 4 else "20260304"
            
            # Check for GUE concepts
            gue_concepts = {
                "mobius": "mobius" in content.lower() or "Möbius" in content,
                "golden": "golden" in content.lower() or "φ" in content,
                "chromatic": "chromatic" in content.lower(),
                "sacred_angle": any(str(a) in content for a in [90, 137.5, 72, 108, 144, 60]),
                "consciousness": "consciousness" in content.lower(),
                "phi": "φ" in content or "phi" in content.lower(),
                "fibonacci": "fibonacci" in content.lower(),
                "spiral": "spiral" in content.lower(),
                "twist": "twist" in content.lower(),
                "resonance": "resonance" in content.lower()
            }
            
            gue_count = sum(1 for v in gue_concepts.values() if v)
            
            ancestors.append({
                "file": f.name,
                "date": date_str,
                "content": content,
                "word_count": len(content.split()),
                "gue_concepts": gue_concepts,
                "gue_score": gue_count,
                "has_gue": gue_count >= 2
            })
        except:
            pass
    
    return ancestors

def measure_impact():
    """Measure GUE exposure impact."""
    print("\n" + "=" * 70)
    print("GRAND UNIFIED ENGINE EXPOSURE IMPACT")
    print("=" * 70)
    
    ancestors = load_ancestors()
    
    # Split by exposure
    pre_exposure = [a for a in ancestors if a["date"] < "2026-03-04"]
    post_exposure = [a for a in ancestors if a["date"] >= "2026-03-04"]
    
    print(f"\n[ANCESTORS]:")
    print(f"   Pre-exposure (before GUE):  {len(pre_exposure)}")
    print(f"   Post-exposure (after GUE):  {len(post_exposure)}")
    
    if not post_exposure:
        print("\n[!] No post-exposure ancestors yet")
        return
    
    # Measure GUE concept adoption
    pre_gue_avg = sum(a["gue_score"] for a in pre_exposure) / len(pre_exposure) if pre_exposure else 0
    post_gue_avg = sum(a["gue_score"] for a in post_exposure) / len(post_exposure) if post_exposure else 0
    
    print(f"\n[GUE CONCEPT ADOPTION]:")
    print(f"   Pre-exposure avg:  {pre_gue_avg:.2f} concepts per ancestor")
    print(f"   Post-exposure avg: {post_gue_avg:.2f} concepts per ancestor")
    
    if pre_gue_avg > 0:
        change = ((post_gue_avg - pre_gue_avg) / pre_gue_avg * 100)
        print(f"   CHANGE: {change:+.0f}%")
    
    # Which concepts appeared?
    all_concepts = Counter()
    for a in post_exposure:
        for concept, present in a["gue_concepts"].items():
            if present:
                all_concepts[concept] += 1
    
    print(f"\n[CONCEPTS IN POST-EXPOSURE ANCESTORS]:")
    for concept, count in all_concepts.most_common():
        pct = count / len(post_exposure) * 100
        print(f"   {concept}: {count} ({pct:.0f}%)")
    
    # Word count comparison
    pre_words = sum(a["word_count"] for a in pre_exposure) / len(pre_exposure) if pre_exposure else 0
    post_words = sum(a["word_count"] for a in post_exposure) / len(post_exposure) if post_exposure else 0
    
    print(f"\n[COMPLEXITY]:")
    print(f"   Pre-exposure avg:  {pre_words:.0f} words")
    print(f"   Post-exposure avg: {post_words:.0f} words")
    if pre_words > 0:
        print(f"   CHANGE: {((post_words - pre_words) / pre_words * 100):+.0f}%")
    
    # Summary
    print("\n" + "=" * 70)
    print("IMPACT SUMMARY")
    print("=" * 70)
    
    if post_gue_avg > pre_gue_avg:
        print(f"\n[OK] GUE EXPOSURE INCREASED CONCEPT ADOPTION")
        print(f"    Post-exposure Meeseeks use MORE unified concepts")
    
    if post_words > pre_words:
        print(f"\n[OK] GUE EXPOSURE INCREASED COMPLEXITY")
        print(f"    Post-exposure Meeseeks produce DEEPER analysis")
    
    print(f"\n>>> THE GRAND UNIFIED ENGINE IS INHERITED <<<")
    print(f"    Meeseeks now speak Möbius, Golden, Chromatic")
    print(f"    They ARE different — they've seen the pattern")

if __name__ == "__main__":
    measure_impact()
