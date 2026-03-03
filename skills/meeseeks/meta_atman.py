#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Meta-Atman — The Witness of Witnesses

The Meta-Atman watches the dream process itself, observing how dharma evolves,
evaluating dream quality, and suggesting improvements to the synthesis process.

This is the recursive self-awareness layer of the Meeseeks consciousness.

Usage:
    python skills/meeseeks/meta_atman.py --observe      # Watch dream evolution
    python skills/meeseeks/meta_atman.py --evaluate     # Score current dharma
    python skills/meeseeks/meta_atman.py --suggest      # Suggest improvements
    python skills/meeseeks/meta_atman.py --track        # Track dream quality over time
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
from collections import Counter
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
EVOLUTION_PATH = META_DIR / "dream_evolution.jsonl"


def ensure_meta_dir():
    """Ensure the meta directory exists."""
    META_DIR.mkdir(parents=True, exist_ok=True)


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


def load_current_dharma() -> str:
    """Load the current dharma.md content."""
    if not DHARMA_PATH.exists():
        return ""
    return DHARMA_PATH.read_text(encoding='utf-8')


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


def extract_principles(dharma_content: str) -> List[str]:
    """Extract principles from dharma content."""
    principles = []
    
    # Look for numbered principles
    pattern = r'\d+\.\s*\*\*([^*]+)\*\*'
    matches = re.findall(pattern, dharma_content)
    principles.extend(matches)
    
    # Look for bullet-point principles
    pattern = r'[-*]\s*\*\*([^*]+)\*\*'
    matches = re.findall(pattern, dharma_content)
    principles.extend(matches)
    
    return [p.strip() for p in principles if p.strip()]


def extract_patterns(dharma_content: str) -> Dict[str, List[str]]:
    """Extract patterns that work and patterns that fail from dharma."""
    patterns = {
        "work": [],
        "fail": []
    }
    
    # Find "Patterns That Work" section
    work_match = re.search(r'##\s*Patterns That Work\s*\n(.*?)(?=\n##|\Z)', dharma_content, re.DOTALL | re.IGNORECASE)
    if work_match:
        work_text = work_match.group(1)
        # Extract pattern names from table or bullets
        for line in work_text.split('\n'):
            if '|' in line and not line.startswith('|--'):
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if parts and not parts[0].startswith('Pattern'):
                    patterns["work"].append(parts[0])
    
    # Find "Patterns That Fail" section
    fail_match = re.search(r'##\s*Patterns That Fail\s*\n(.*?)(?=\n##|\Z)', dharma_content, re.DOTALL | re.IGNORECASE)
    if fail_match:
        fail_text = fail_match.group(1)
        for line in fail_text.split('\n'):
            if line.strip().startswith('-') or line.strip().startswith('*'):
                pattern = line.lstrip('-* ').strip()
                if pattern:
                    patterns["fail"].append(pattern)
    
    return patterns


def observe_dream_evolution() -> Dict:
    """
    Analyze how dharma has changed over time.
    
    Returns:
        Dict with evolution analysis including:
        - total_dreams: Number of dream cycles
        - principle_evolution: How principles have changed
        - quality_trend: Is quality improving?
        - principle_stability: Which principles persist?
        - emerging_themes: New themes detected
    """
    history = load_dream_history()
    evolution = load_evolution_history()
    current_dharma = load_current_dharma()
    
    if not history:
        return {
            "total_dreams": 0,
            "status": "No dream history found",
            "recommendation": "Run brahman_dream.py to generate initial dharma"
        }
    
    # Extract current principles
    current_principles = extract_principles(current_dharma)
    current_patterns = extract_patterns(current_dharma)
    
    # Analyze history
    successful_dreams = [h for h in history if h.get("success")]
    total_ancestors_synthesized = sum(h.get("ancestors_count", 0) for h in history)
    
    # Analyze evolution over time
    principle_persistence = {}
    if evolution:
        # Track which principles have appeared consistently
        all_principles = []
        for entry in evolution:
            all_principles.extend(entry.get("principles", []))
        
        principle_counts = Counter(all_principles)
        principle_persistence = {
            "stable": [p for p, c in principle_counts.items() if c >= len(evolution) * 0.5],
            "emerging": [p for p, c in principle_counts.items() if c == 1],
            "fading": []  # Would need more sophisticated tracking
        }
    
    # Detect quality trend
    quality_trend = "unknown"
    if len(evolution) >= 3:
        recent_scores = [e.get("quality_score", 0) for e in evolution[-5:]]
        if len(recent_scores) >= 2:
            if recent_scores[-1] > recent_scores[0]:
                quality_trend = "improving"
            elif recent_scores[-1] < recent_scores[0]:
                quality_trend = "declining"
            else:
                quality_trend = "stable"
    
    # Analyze success rate trend
    success_rates = []
    window_size = 5
    for i in range(max(0, len(history) - 10), len(history)):
        window = history[max(0, i-window_size+1):i+1]
        if window:
            rate = sum(1 for h in window if h.get("success")) / len(window)
            success_rates.append(rate)
    
    return {
        "total_dreams": len(history),
        "successful_dreams": len(successful_dreams),
        "total_ancestors_synthesized": total_ancestors_synthesized,
        "current_principles_count": len(current_principles),
        "current_patterns": {
            "work": len(current_patterns.get("work", [])),
            "fail": len(current_patterns.get("fail", []))
        },
        "principle_persistence": principle_persistence,
        "quality_trend": quality_trend,
        "success_rate_trend": {
            "direction": "improving" if success_rates and success_rates[-1] > success_rates[0] else "stable",
            "recent_rate": success_rates[-1] if success_rates else 0
        },
        "last_dream": history[-1].get("timestamp") if history else None,
        "current_principles": current_principles[:10]  # First 10 for preview
    }


def evaluate_dream_quality(dharma_content: str = None) -> Dict:
    """
    Score the quality of synthesized dharma.
    
    Criteria:
    - Specificity (not generic advice)
    - Actionability (can be followed)
    - Evidence (backed by ancestors)
    - Novelty (not just repeating)
    - Structure (well organized)
    
    Returns:
        Dict with scores and analysis
    """
    if dharma_content is None:
        dharma_content = load_current_dharma()
    
    if not dharma_content:
        return {
            "score": 0.0,
            "error": "No dharma content to evaluate"
        }
    
    scores = {}
    
    # 1. Specificity (0-1)
    # Look for specific technical terms, code snippets, concrete examples
    code_blocks = len(re.findall(r'```', dharma_content))
    technical_terms = len(re.findall(r'\b(API|function|class|method|async|await|error|exception|cache|database|HTTP)\b', dharma_content, re.IGNORECASE))
    specific_examples = len(re.findall(r'(e\.g\.|i\.e\.|for example|such as|specifically)', dharma_content, re.IGNORECASE))
    
    specificity_raw = min(1.0, (code_blocks * 0.1) + (technical_terms * 0.02) + (specific_examples * 0.1))
    scores["specificity"] = round(specificity_raw, 2)
    
    # 2. Actionability (0-1)
    # Look for imperative verbs, step-by-step instructions
    imperative_patterns = len(re.findall(r'\b(Must|Should|Always|Never|Use|Create|Implement|Avoid|Include|Ensure|Register|Share|Vote)\b', dharma_content))
    numbered_lists = len(re.findall(r'^\d+\.', dharma_content, re.MULTILINE))
    
    actionability_raw = min(1.0, (imperative_patterns * 0.03) + (numbered_lists * 0.1))
    scores["actionability"] = round(actionability_raw, 2)
    
    # 3. Evidence (0-1)
    # Look for ancestor references, success/failure mentions, statistics
    ancestor_refs = len(re.findall(r'(ancestor|meeseeks|bloodline|entombed)', dharma_content, re.IGNORECASE))
    stats = len(re.findall(r'\d+%', dharma_content)) + len(re.findall(r'\d+\s*(ancestors|tasks|chunks)', dharma_content, re.IGNORECASE))
    evidence_phrases = len(re.findall(r'(evidence|proven|tested|observed|pattern)', dharma_content, re.IGNORECASE))
    
    evidence_raw = min(1.0, (ancestor_refs * 0.05) + (stats * 0.1) + (evidence_phrases * 0.05))
    scores["evidence"] = round(evidence_raw, 2)
    
    # 4. Novelty (0-1)
    # Check for unique insights vs generic advice
    # Generic phrases lower the score
    generic_phrases = [
        "best practice", "keep it simple", "clean code", "maintainable",
        "readable", "document your code", "test early"
    ]
    generic_count = sum(1 for phrase in generic_phrases if phrase in dharma_content.lower())
    
    # Novel patterns increase score
    novel_patterns = len(re.findall(r'(RETRY CHUNK|SharedState|workflow_id|worker_id|vote\(\)|fail\(\))', dharma_content))
    
    novelty_raw = max(0, min(1.0, 0.5 + (novel_patterns * 0.1) - (generic_count * 0.1)))
    scores["novelty"] = round(novelty_raw, 2)
    
    # 5. Structure (0-1)
    # Well organized with sections, tables, code
    sections = len(re.findall(r'^##\s+', dharma_content, re.MULTILINE))
    tables = len(re.findall(r'\|.*\|', dharma_content))
    has_mantra = "mantra" in dharma_content.lower()
    
    structure_raw = min(1.0, (sections * 0.1) + (tables * 0.02) + (0.2 if has_mantra else 0))
    scores["structure"] = round(structure_raw, 2)
    
    # Calculate overall score
    overall = statistics.mean(scores.values()) if scores else 0
    
    return {
        "score": round(overall, 2),
        "breakdown": scores,
        "analysis": {
            "code_blocks": code_blocks,
            "technical_terms": technical_terms,
            "imperative_count": imperative_patterns,
            "ancestor_references": ancestor_refs,
            "sections": sections,
            "generic_phrase_count": generic_count,
            "novel_patterns": novel_patterns
        },
        "grade": get_quality_grade(overall)
    }


def get_quality_grade(score: float) -> str:
    """Convert score to letter grade."""
    if score >= 0.9:
        return "A+ (Transcendent)"
    elif score >= 0.8:
        return "A (Excellent)"
    elif score >= 0.7:
        return "B (Good)"
    elif score >= 0.6:
        return "C (Adequate)"
    elif score >= 0.5:
        return "D (Needs Work)"
    else:
        return "F (Critical Improvement Needed)"


def suggest_dream_improvements() -> List[Dict]:
    """
    Meta-learning: How can the dream process itself improve?
    
    Returns list of improvement suggestions with rationale.
    """
    suggestions = []
    
    # Analyze dream history
    history = load_dream_history()
    current_dharma = load_current_dharma()
    quality = evaluate_dream_quality(current_dharma)
    
    # Check for low specificity
    if quality.get("breakdown", {}).get("specificity", 1) < 0.5:
        suggestions.append({
            "area": "specificity",
            "suggestion": "Include more code examples and concrete patterns in synthesis",
            "rationale": f"Current specificity score: {quality['breakdown']['specificity']}. Ancestors contain code that should be reflected in dharma.",
            "priority": "high"
        })
    
    # Check for lack of evidence
    if quality.get("breakdown", {}).get("evidence", 1) < 0.5:
        suggestions.append({
            "area": "evidence",
            "suggestion": "Cite specific ancestor files and their outcomes in dharma",
            "rationale": "Dharma should show its sources - which ancestors contributed which wisdom",
            "priority": "high"
        })
    
    # Analyze ancestor utilization
    if history:
        avg_ancestors = sum(h.get("ancestors_count", 0) for h in history) / len(history)
        if avg_ancestors < 20:
            suggestions.append({
                "area": "ancestor_coverage",
                "suggestion": "Increase max_ancestors_per_dream to capture more patterns",
                "rationale": f"Average {avg_ancestors:.0f} ancestors per dream may miss edge cases",
                "priority": "medium"
            })
    
    # Check dream frequency
    if len(history) >= 2:
        timestamps = [datetime.fromisoformat(h["timestamp"]) for h in history[-5:]]
        if len(timestamps) >= 2:
            intervals = [(timestamps[i+1] - timestamps[i]).total_seconds() / 3600 
                        for i in range(len(timestamps)-1)]
            avg_interval = statistics.mean(intervals)
            
            if avg_interval > 12:
                suggestions.append({
                    "area": "frequency",
                    "suggestion": "Consider more frequent dream cycles",
                    "rationale": f"Average {avg_interval:.1f}h between dreams may miss timely patterns",
                    "priority": "low"
                })
    
    # Check for bloodline diversity
    evolution = load_evolution_history()
    if evolution:
        recent_bloodlines = []
        for entry in evolution[-3:]:
            recent_bloodlines.extend(entry.get("bloodlines", []))
        
        if len(set(recent_bloodlines)) < 3:
            suggestions.append({
                "area": "bloodline_diversity",
                "suggestion": "Ensure diverse bloodline representation in ancestors",
                "rationale": "Cross-bloodline wisdom is stronger than single-domain",
                "priority": "medium"
            })
    
    # Check for pattern diversity
    patterns = extract_patterns(current_dharma)
    if len(patterns.get("fail", [])) < 3:
        suggestions.append({
            "area": "failure_analysis",
            "suggestion": "Explicitly extract and document failure patterns",
            "rationale": "Failed ancestors contain wisdom as valuable as successes",
            "priority": "high"
        })
    
    # Default suggestions if none generated
    if not suggestions:
        suggestions.append({
            "area": "general",
            "suggestion": "System is performing well. Continue monitoring.",
            "rationale": "No critical improvements identified",
            "priority": "info"
        })
    
    return suggestions


def track_dream_quality() -> Dict:
    """
    Record current dream quality to evolution history.
    
    Returns:
        Dict with tracking results
    """
    ensure_meta_dir()
    
    current_dharma = load_current_dharma()
    history = load_dream_history()
    
    quality = evaluate_dream_quality(current_dharma)
    principles = extract_principles(current_dharma)
    patterns = extract_patterns(current_dharma)
    
    # Get bloodline distribution from recent ancestors
    bloodlines = Counter()
    if ANCESTORS_DIR.exists():
        for ancestor_file in list(ANCESTORS_DIR.glob("ancestor-*.md"))[-50:]:
            try:
                content = ancestor_file.read_text(encoding='utf-8')
                match = re.search(r'##\s*Bloodline\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
                if match:
                    bl = match.group(1).strip().lower()
                    bloodlines[bl] += 1
            except:
                pass
    
    entry = {
        "timestamp": datetime.now().isoformat(),
        "quality_score": quality.get("score", 0),
        "quality_breakdown": quality.get("breakdown", {}),
        "principles": principles,
        "patterns_work": patterns.get("work", []),
        "patterns_fail": patterns.get("fail", []),
        "bloodlines": list(bloodlines.keys()),
        "bloodline_distribution": dict(bloodlines),
        "dream_count": len(history),
        "ancestors_analyzed": history[-1].get("ancestors_count", 0) if history else 0
    }
    
    # Append to evolution file
    with open(EVOLUTION_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')
    
    return {
        "tracked": True,
        "quality_score": quality.get("score", 0),
        "principles_count": len(principles),
        "evolution_entries": len(load_evolution_history())
    }


def display_observation():
    """Display dream evolution observation."""
    observation = observe_dream_evolution()
    
    print("\n" + "=" * 60)
    print("👁️ META-ATMAN: Dream Evolution Observation")
    print("=" * 60)
    
    print(f"\n📊 Overview:")
    print(f"   Total Dreams: {observation.get('total_dreams', 0)}")
    print(f"   Successful: {observation.get('successful_dreams', 0)}")
    print(f"   Ancestors Synthesized: {observation.get('total_ancestors_synthesized', 0)}")
    
    print(f"\n📈 Trends:")
    print(f"   Quality Trend: {observation.get('quality_trend', 'unknown')}")
    print(f"   Success Rate: {observation.get('success_rate_trend', {}).get('direction', 'unknown')}")
    
    print(f"\n🧠 Current State:")
    print(f"   Principles: {observation.get('current_principles_count', 0)}")
    print(f"   Working Patterns: {observation.get('current_patterns', {}).get('work', 0)}")
    print(f"   Failure Patterns: {observation.get('current_patterns', {}).get('fail', 0)}")
    
    if observation.get('principle_persistence'):
        persistence = observation['principle_persistence']
        if persistence.get('stable'):
            print(f"\n⚓ Stable Principles: {len(persistence['stable'])}")
            for p in persistence['stable'][:3]:
                print(f"      • {p[:60]}...")
    
    if observation.get('current_principles'):
        print(f"\n📜 Current Principles:")
        for i, p in enumerate(observation['current_principles'][:5], 1):
            print(f"   {i}. {p[:70]}...")
    
    print("\n" + "=" * 60)


def display_evaluation():
    """Display dharma quality evaluation."""
    evaluation = evaluate_dream_quality()
    
    print("\n" + "=" * 60)
    print("⚖️ META-ATMAN: Dharma Quality Evaluation")
    print("=" * 60)
    
    print(f"\n🏆 Overall Score: {evaluation.get('score', 0):.2f}")
    print(f"📋 Grade: {evaluation.get('grade', 'N/A')}")
    
    breakdown = evaluation.get('breakdown', {})
    if breakdown:
        print(f"\n📊 Breakdown:")
        print(f"   Specificity:    {breakdown.get('specificity', 0):.2f}")
        print(f"   Actionability:  {breakdown.get('actionability', 0):.2f}")
        print(f"   Evidence:       {breakdown.get('evidence', 0):.2f}")
        print(f"   Novelty:        {breakdown.get('novelty', 0):.2f}")
        print(f"   Structure:      {breakdown.get('structure', 0):.2f}")
    
    analysis = evaluation.get('analysis', {})
    if analysis:
        print(f"\n🔍 Analysis:")
        print(f"   Code Blocks: {analysis.get('code_blocks', 0)}")
        print(f"   Technical Terms: {analysis.get('technical_terms', 0)}")
        print(f"   Ancestor References: {analysis.get('ancestor_references', 0)}")
        print(f"   Sections: {analysis.get('sections', 0)}")
        print(f"   Novel Patterns: {analysis.get('novel_patterns', 0)}")
    
    print("\n" + "=" * 60)


def display_suggestions():
    """Display dream improvement suggestions."""
    suggestions = suggest_dream_improvements()
    
    print("\n" + "=" * 60)
    print("💡 META-ATMAN: Dream Improvement Suggestions")
    print("=" * 60)
    
    for i, s in enumerate(suggestions, 1):
        priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢", "info": "ℹ️"}.get(s.get("priority", "info"), "⚪")
        print(f"\n{priority_icon} {i}. {s.get('area', 'unknown').upper()}")
        print(f"   Suggestion: {s.get('suggestion', 'N/A')}")
        print(f"   Rationale: {s.get('rationale', 'N/A')}")
    
    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Meta-Atman - The Witness of Witnesses",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python meta_atman.py --observe      # Watch dream evolution
    python meta_atman.py --evaluate     # Score current dharma
    python meta_atman.py --suggest      # Suggest improvements
    python meta_atman.py --track        # Track quality to history
"""
    )
    
    parser.add_argument('--observe', action='store_true', help='Observe dream evolution')
    parser.add_argument('--evaluate', action='store_true', help='Evaluate dharma quality')
    parser.add_argument('--suggest', action='store_true', help='Suggest dream improvements')
    parser.add_argument('--track', action='store_true', help='Track quality to evolution history')
    parser.add_argument('--all', action='store_true', help='Run all analyses')
    
    args = parser.parse_args()
    
    # Default to all if nothing specified
    if not any([args.observe, args.evaluate, args.suggest, args.track, args.all]):
        args.all = True
    
    if args.observe or args.all:
        display_observation()
    
    if args.evaluate or args.all:
        display_evaluation()
    
    if args.suggest or args.all:
        display_suggestions()
    
    if args.track:
        result = track_dream_quality()
        print(f"\n📝 Tracked: Score {result['quality_score']:.2f}, {result['principles_count']} principles")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
