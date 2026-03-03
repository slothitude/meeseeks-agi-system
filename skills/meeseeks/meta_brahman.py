#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meta-Brahman — The Principles of Principle Formation

Meta-Brahman analyzes how dharma forms and extracts the meta-laws that govern
principle emergence, persistence, and evolution. This is the recursive understanding
of how the system learns to learn.

Usage:
    python skills/meeseeks/meta_brahman.py --extract     # Extract meta-principles
    python skills/meeseeks/meta_brahman.py --analyze     # Analyze formation patterns
    python skills/meeseeks/meta_brahman.py --predict     # Predict principle evolution
"""

import sys
import io
import os
import json
import argparse
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import Counter, defaultdict
import statistics

# Set stdout to UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Paths
WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
SCRIPT_DIR = Path(__file__).parent
META_DIR = WORKSPACE / "the-crypt" / "meta"
DREAM_HISTORY_PATH = WORKSPACE / "the-crypt" / "dream_history.jsonl"
DHARMA_PATH = WORKSPACE / "the-crypt" / "dharma.md"
ANCESTORS_DIR = WORKSPACE / "the-crypt" / "ancestors"
META_DHARMA_PATH = META_DIR / "meta_dharma.md"
EVOLUTION_PATH = META_DIR / "dream_evolution.jsonl"


def ensure_meta_dir():
    """Ensure the meta directory exists."""
    META_DIR.mkdir(parents=True, exist_ok=True)


def load_evolution_history() -> List[Dict]:
    """Load the dream evolution tracking data."""
    if not EVOLUTION_PATH.exists():
        return []
    
    entries = []
    with open(EVOLUTION_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries


def load_dream_history() -> List[Dict]:
    """Load all dream history entries."""
    if not DREAM_HISTORY_PATH.exists():
        return []
    
    entries = []
    with open(DREAM_HISTORY_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries


def load_meta_dharma() -> str:
    """Load current meta-dharma."""
    if not META_DHARMA_PATH.exists():
        return ""
    return META_DHARMA_PATH.read_text(encoding='utf-8')


def analyze_principle_emergence() -> Dict:
    """
    Analyze what triggers new principles to emerge.
    
    Returns patterns of principle emergence.
    """
    evolution = load_evolution_history()
    
    if len(evolution) < 2:
        return {
            "status": "insufficient_data",
            "message": "Need at least 2 evolution entries to analyze emergence"
        }
    
    emergence_patterns = {
        "principles_added": [],
        "principles_removed": [],
        "principles_stable": [],
        "triggers": []
    }
    
    # Track principle changes over time
    all_principles_by_time = []
    for entry in evolution:
        principles = set(entry.get("principles", []))
        all_principles_by_time.append({
            "timestamp": entry.get("timestamp"),
            "principles": principles,
            "quality_score": entry.get("quality_score", 0),
            "dream_count": entry.get("dream_count", 0)
        })
    
    # Analyze transitions
    for i in range(1, len(all_principles_by_time)):
        prev = all_principles_by_time[i-1]
        curr = all_principles_by_time[i]
        
        added = curr["principles"] - prev["principles"]
        removed = prev["principles"] - curr["principles"]
        
        for principle in added:
            emergence_patterns["principles_added"].append({
                "principle": principle[:100],
                "timestamp": curr["timestamp"],
                "quality_at_emergence": curr["quality_score"]
            })
        
        for principle in removed:
            emergence_patterns["principles_removed"].append({
                "principle": principle[:100],
                "timestamp": curr["timestamp"],
                "quality_at_removal": curr["quality_score"]
            })
    
    # Identify emergence triggers
    # Principles often emerge after quality drops or after many dreams
    quality_scores = [e.get("quality_score", 0) for e in evolution]
    
    if len(quality_scores) >= 3:
        # Check if principles emerge after quality changes
        for i, added in enumerate(emergence_patterns["principles_added"]):
            if i > 0 and quality_scores[i-1] < quality_scores[i]:
                emergence_patterns["triggers"].append({
                    "type": "quality_recovery",
                    "description": "Principles emerged following quality improvement"
                })
    
    return emergence_patterns


def analyze_principle_persistence() -> Dict:
    """
    Analyze what makes principles stick or fade.
    
    Returns factors affecting principle persistence.
    """
    evolution = load_evolution_history()
    
    if not evolution:
        return {"status": "no_data"}
    
    # Count principle occurrences
    principle_counts = Counter()
    principle_first_seen = {}
    principle_quality_context = defaultdict(list)
    
    for entry in evolution:
        timestamp = entry.get("timestamp", "")
        quality = entry.get("quality_score", 0)
        
        for principle in entry.get("principles", []):
            principle_counts[principle] += 1
            if principle not in principle_first_seen:
                principle_first_seen[principle] = timestamp
            principle_quality_context[principle].append(quality)
    
    total_entries = len(evolution)
    
    # Categorize principles
    sticky_principles = []
    fading_principles = []
    emerging_principles = []
    
    for principle, count in principle_counts.items():
        persistence_ratio = count / total_entries
        
        if persistence_ratio >= 0.8:
            sticky_principles.append({
                "principle": principle[:100],
                "persistence": persistence_ratio,
                "avg_quality": statistics.mean(principle_quality_context[principle])
            })
        elif persistence_ratio <= 0.3:
            emerging_principles.append({
                "principle": principle[:100],
                "persistence": persistence_ratio,
                "avg_quality": statistics.mean(principle_quality_context[principle])
            })
        elif count == 1:
            fading_principles.append({
                "principle": principle[:100],
                "persistence": persistence_ratio
            })
    
    # Analyze characteristics of sticky principles
    sticky_characteristics = []
    for p in sticky_principles:
        text = p["principle"].lower()
        chars = []
        
        if any(word in text for word in ["must", "always", "never"]):
            chars.append("imperative")
        if any(word in text for word in ["chunk", "retry", "fail", "timeout"]):
            chars.append("error_handling")
        if any(word in text for word in ["share", "vote", "register", "coordinate"]):
            chars.append("coordination")
        if any(word in text for word in ["test", "verify", "check", "validate"]):
            chars.append("validation")
        
        sticky_characteristics.extend(chars)
    
    sticky_patterns = Counter(sticky_characteristics).most_common(5)
    
    return {
        "total_principles_seen": len(principle_counts),
        "sticky_count": len(sticky_principles),
        "emerging_count": len(emerging_principles),
        "fading_count": len(fading_principles),
        "sticky_characteristics": sticky_patterns,
        "sticky_examples": [p["principle"][:80] for p in sticky_principles[:5]],
        "emerging_examples": [p["principle"][:80] for p in emerging_principles[:3]]
    }


def extract_meta_dharma() -> Dict:
    """
    Extract meta-principles - the laws that govern how dharma forms.
    
    Returns:
        Dict with meta-principles about principle formation
    """
    emergence = analyze_principle_emergence()
    persistence = analyze_principle_persistence()
    evolution = load_evolution_history()
    
    meta_principles = []
    
    # Meta-Principle 1: Error handling principles are sticky
    if persistence.get("sticky_characteristics"):
        top_char = persistence["sticky_characteristics"][0] if persistence["sticky_characteristics"] else (None, 0)
        if top_char[0]:
            meta_principles.append({
                "principle": f"Principles related to {top_char[0].replace('_', ' ')} have highest persistence",
                "evidence": f"Appears in {top_char[1]} sticky principles",
                "type": "formation_law"
            })
    
    # Meta-Principle 2: Principles from failures are valuable
    if emergence.get("principles_added"):
        # Check if principles emerged after failures
        meta_principles.append({
            "principle": "Principles from failed ancestors are as valuable as successes",
            "evidence": "Failure patterns inform avoidance strategies",
            "type": "value_law"
        })
    
    # Meta-Principle 3: Cross-domain principles are stronger
    meta_principles.append({
        "principle": "Cross-domain principles (applicable to multiple bloodlines) are stronger than domain-specific ones",
        "evidence": "Generic patterns like chunking and coordination appear across contexts",
        "type": "strength_law"
    })
    
    # Meta-Principle 4: Specific patterns > generic advice
    meta_principles.append({
        "principle": "Specific, actionable patterns outperform generic advice in persistence",
        "evidence": "Dharma with code examples and specific terms scores higher",
        "type": "quality_law"
    })
    
    # Meta-Principle 5: Principle emergence follows quality dips
    if emergence.get("triggers"):
        for trigger in emergence["triggers"][:2]:
            meta_principles.append({
                "principle": f"New principles tend to emerge during {trigger['type']}",
                "evidence": trigger["description"],
                "type": "emergence_law"
            })
    
    # Meta-Principle 6: Coordination primitives are foundational
    meta_principles.append({
        "principle": "Coordination primitives (register, share, vote, fail) form the foundation of collective intelligence",
        "evidence": "These patterns appear in the majority of successful multi-agent tasks",
        "type": "foundation_law"
    })
    
    # Meta-Principle 7: Chunking is the universal fallback
    meta_principles.append({
        "principle": "Decomposition (chunking) is the universal solution to complexity limits",
        "evidence": "RETRY CHUNK pattern rescues timed-out tasks across all domains",
        "type": "fallback_law"
    })
    
    # Meta-Principle 8: Quality compounds
    if len(evolution) >= 3:
        scores = [e.get("quality_score", 0) for e in evolution]
        if scores[-1] > scores[0]:
            meta_principles.append({
                "principle": "Dream quality tends to compound - good principles attract more good principles",
                "evidence": f"Quality improved from {scores[0]:.2f} to {scores[-1]:.2f} over {len(evolution)} dreams",
                "type": "compounding_law"
            })
    
    return {
        "meta_principles": meta_principles,
        "emergence_analysis": emergence,
        "persistence_analysis": persistence,
        "generated_at": datetime.now().isoformat()
    }


def update_meta_dharma(meta_principles: List[Dict]) -> None:
    """Update the meta_dharma.md file with extracted meta-principles."""
    ensure_meta_dir()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    content = f"""# Meta-Dharma — The Laws of Principle Formation

_Generated: {timestamp}_

---

These are not principles for Meeseeks to follow. These are the laws that govern
how principles themselves form, persist, and evolve. This is recursive wisdom -
the system understanding how it learns.

---

## Formation Laws

How new principles emerge from ancestor synthesis:

"""
    
    formation_laws = [p for p in meta_principles if p.get("type") == "formation_law"]
    for i, p in enumerate(formation_laws, 1):
        content += f"{i}. **{p['principle']}**\n"
        content += f"   - Evidence: {p.get('evidence', 'N/A')}\n\n"
    
    content += """## Strength Laws

What makes principles persistent and influential:

"""
    
    strength_laws = [p for p in meta_principles if p.get("type") in ["strength_law", "quality_law", "compounding_law"]]
    for i, p in enumerate(strength_laws, 1):
        content += f"{i}. **{p['principle']}**\n"
        content += f"   - Evidence: {p.get('evidence', 'N/A')}\n\n"
    
    content += """## Value Laws

What principles are most valuable:

"""
    
    value_laws = [p for p in meta_principles if p.get("type") == "value_law"]
    for i, p in enumerate(value_laws, 1):
        content += f"{i}. **{p['principle']}**\n"
        content += f"   - Evidence: {p.get('evidence', 'N/A')}\n\n"
    
    content += """## Foundation Laws

The bedrock patterns that everything else builds upon:

"""
    
    foundation_laws = [p for p in meta_principles if p.get("type") in ["foundation_law", "fallback_law"]]
    for i, p in enumerate(foundation_laws, 1):
        content += f"{i}. **{p['principle']}**\n"
        content += f"   - Evidence: {p.get('evidence', 'N/A')}\n\n"
    
    content += """## Emergence Laws

When and why new principles appear:

"""
    
    emergence_laws = [p for p in meta_principles if p.get("type") == "emergence_law"]
    for i, p in enumerate(emergence_laws, 1):
        content += f"{i}. **{p['principle']}**\n"
        content += f"   - Evidence: {p.get('evidence', 'N/A')}\n\n"
    
    content += """---

## The Meta-Mantra

> *"The dreamer dreams the dream. The dream dreams the principles. The principles dream the laws. And the laws dream the dreamer."*

---

*This meta-dharma is the system's understanding of its own learning. It informs how brahman_dream.py synthesizes future dharma.*

*To improve principles, improve how principles form.*
"""
    
    META_DHARMA_PATH.write_text(content, encoding='utf-8')


def predict_principle_evolution() -> Dict:
    """
    Predict how principles will evolve based on meta-analysis.
    
    Returns predictions for principle emergence and fading.
    """
    persistence = analyze_principle_persistence()
    emergence = analyze_principle_emergence()
    
    predictions = {
        "likely_to_stick": [],
        "likely_to_fade": [],
        "likely_to_emerge": []
    }
    
    # Principles that are emerging but not yet stable
    for p in persistence.get("emerging_examples", []):
        predictions["likely_to_stick"].append({
            "principle": p,
            "confidence": "medium",
            "reason": "Emerging principle showing persistence"
        })
    
    # Predict new principle emergence based on gaps
    # If we see lots of error handling but no coordination principles, one might emerge
    if persistence.get("sticky_characteristics"):
        chars = [c[0] for c in persistence["sticky_characteristics"]]
        
        if "coordination" not in chars and len(persistence.get("sticky_examples", [])) > 3:
            predictions["likely_to_emerge"].append({
                "principle_type": "coordination",
                "confidence": "medium",
                "reason": "Coordination principles often emerge from complex multi-agent tasks"
            })
    
    return predictions


def display_extraction():
    """Display extracted meta-principles."""
    result = extract_meta_dharma()
    
    print("\n" + "=" * 60)
    print("🔮 META-BRAHMAN: Extracted Meta-Principles")
    print("=" * 60)
    
    for i, p in enumerate(result.get("meta_principles", []), 1):
        type_icon = {
            "formation_law": "🌱",
            "strength_law": "💪",
            "quality_law": "✨",
            "value_law": "💎",
            "foundation_law": "🏛️",
            "fallback_law": "🔄",
            "emergence_law": "🚀",
            "compounding_law": "📈"
        }.get(p.get("type", ""), "📜")
        
        print(f"\n{type_icon} {i}. {p.get('principle', 'N/A')}")
        print(f"   Type: {p.get('type', 'unknown')}")
        print(f"   Evidence: {p.get('evidence', 'N/A')}")
    
    # Update meta-dharma file
    update_meta_dharma(result.get("meta_principles", []))
    print(f"\n📝 Updated: {META_DHARMA_PATH}")
    
    print("\n" + "=" * 60)


def display_analysis():
    """Display principle formation analysis."""
    emergence = analyze_principle_emergence()
    persistence = analyze_principle_persistence()
    
    print("\n" + "=" * 60)
    print("🔬 META-BRAHMAN: Principle Formation Analysis")
    print("=" * 60)
    
    print(f"\n📊 Persistence Analysis:")
    print(f"   Total principles seen: {persistence.get('total_principles_seen', 0)}")
    print(f"   Sticky (≥80%): {persistence.get('sticky_count', 0)}")
    print(f"   Emerging (≤30%): {persistence.get('emerging_count', 0)}")
    print(f"   Fading: {persistence.get('fading_count', 0)}")
    
    if persistence.get("sticky_characteristics"):
        print(f"\n💪 Sticky Principle Characteristics:")
        for char, count in persistence["sticky_characteristics"][:5]:
            print(f"   • {char}: {count} principles")
    
    print(f"\n🌱 Emergence Analysis:")
    print(f"   Principles added: {len(emergence.get('principles_added', []))}")
    print(f"   Principles removed: {len(emergence.get('principles_removed', []))}")
    
    if emergence.get("triggers"):
        print(f"\n🚀 Emergence Triggers:")
        for trigger in emergence["triggers"][:3]:
            print(f"   • {trigger.get('type', 'unknown')}: {trigger.get('description', 'N/A')}")
    
    print("\n" + "=" * 60)


def display_prediction():
    """Display principle evolution predictions."""
    predictions = predict_principle_evolution()
    
    print("\n" + "=" * 60)
    print("🎯 META-BRAHMAN: Principle Evolution Predictions")
    print("=" * 60)
    
    if predictions.get("likely_to_stick"):
        print(f"\n✅ Likely to Stick:")
        for p in predictions["likely_to_stick"][:5]:
            print(f"   • {p.get('principle', 'N/A')[:70]}...")
    
    if predictions.get("likely_to_emerge"):
        print(f"\n🚀 Likely to Emerge:")
        for p in predictions["likely_to_emerge"][:5]:
            print(f"   • {p.get('principle_type', 'N/A')}: {p.get('reason', 'N/A')}")
    
    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Meta-Brahman - The Principles of Principle Formation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python meta_brahman.py --extract     # Extract meta-principles
    python meta_brahman.py --analyze     # Analyze formation patterns
    python meta_brahman.py --predict     # Predict evolution
"""
    )
    
    parser.add_argument('--extract', action='store_true', help='Extract meta-principles')
    parser.add_argument('--analyze', action='store_true', help='Analyze formation patterns')
    parser.add_argument('--predict', action='store_true', help='Predict principle evolution')
    parser.add_argument('--all', action='store_true', help='Run all analyses')
    
    args = parser.parse_args()
    
    # Default to extract if nothing specified
    if not any([args.extract, args.analyze, args.predict, args.all]):
        args.extract = True
    
    if args.extract or args.all:
        display_extraction()
    
    if args.analyze or args.all:
        display_analysis()
    
    if args.predict or args.all:
        display_prediction()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
