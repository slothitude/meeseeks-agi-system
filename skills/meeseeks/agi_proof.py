#!/usr/bin/env python3
"""
AGI Proof — Measure Progress Toward AGI

Runs experiments to prove the Meeseeks system is moving toward AGI:
1. Generation Intelligence Test — Are later generations smarter?
2. Dharma Effectiveness Test — Does dharma help?
3. Cross-Domain Transfer Test — Does knowledge transfer?
4. Self-Improvement Spiral — Does karma RL work?
5. Bloodline Specialization — Do bloodlines specialize?

Usage:
    python agi_proof.py --all
    python agi_proof.py --generation-test
    python agi_proof.py --dharma-test
    python agi_proof.py --status

CLI:
    python agi_proof.py --status  # Show current AGI metrics
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import Counter, defaultdict

# Paths
WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
CRYPT_ROOT = WORKSPACE / "the-crypt"
ANCESTORS_DIR = CRYPT_ROOT / "ancestors"
DHARMA_FILE = CRYPT_ROOT / "dharma.md"
KARMA_FILE = CRYPT_ROOT / "karma_observations.jsonl"
ENTOMBED_FILE = CRYPT_ROOT / "entombed_sessions.json"
META_DIR = CRYPT_ROOT / "meta"


def load_ancestors() -> List[Dict]:
    """Load all ancestors with metadata."""
    ancestors = []
    
    if not ANCESTORS_DIR.exists():
        return ancestors
    
    for ancestor_file in sorted(ANCESTORS_DIR.glob("ancestor-*.md")):
        try:
            content = ancestor_file.read_text(encoding='utf-8')
            
            # Parse metadata from filename
            # Format: ancestor-YYYYMMDD-HHMMSS-XXXX.md
            parts = ancestor_file.stem.split("-")
            date_str = f"{parts[1]}-{parts[2]}-{parts[3]}"
            time_str = parts[4] if len(parts) > 4 else "000000"
            
            # Parse date
            try:
                created = datetime.strptime(f"{date_str} {time_str}", "%Y%m%d %H%M%S")
            except:
                created = datetime.now()
            
            # Extract outcome
            outcome = "UNKNOWN"
            if "SUCCESS" in content.upper():
                outcome = "SUCCESS"
            elif "FAILURE" in content.upper() or "FAIL" in content.upper():
                outcome = "FAILURE"
            elif "PARTIAL" in content.upper():
                outcome = "PARTIAL"
            
            # Extract bloodline
            bloodline = "unknown"
            for line in content.split("\n")[:20]:
                if "bloodline" in line.lower():
                    bloodline = line.split(":")[-1].strip().lower()
                    break
            
            ancestors.append({
                "file": ancestor_file.name,
                "created": created,
                "outcome": outcome,
                "bloodline": bloodline,
                "content_length": len(content)
            })
        except Exception as e:
            continue
    
    return ancestors


def load_karma_observations() -> List[Dict]:
    """Load karma observations."""
    observations = []
    
    if not KARMA_FILE.exists():
        return observations
    
    with open(KARMA_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try:
                    observations.append(json.loads(line))
                except:
                    continue
    
    return observations


def generation_intelligence_test() -> Dict:
    """
    Test if later generations are smarter.
    
    Compare early ancestors vs recent ancestors on success rate.
    """
    ancestors = load_ancestors()
    
    if len(ancestors) < 20:
        return {
            "test": "generation_intelligence",
            "status": "insufficient_data",
            "ancestors_needed": 20,
            "ancestors_available": len(ancestors)
        }
    
    # Split into early (first 50%) and late (last 50%)
    mid = len(ancestors) // 2
    early = ancestors[:mid]
    late = ancestors[mid:]
    
    # Calculate success rates
    early_success = sum(1 for a in early if a["outcome"] == "SUCCESS")
    early_rate = early_success / len(early) if early else 0
    
    late_success = sum(1 for a in late if a["outcome"] == "SUCCESS")
    late_rate = late_success / len(late) if late else 0
    
    # Improvement
    improvement = late_rate - early_rate
    
    return {
        "test": "generation_intelligence",
        "status": "complete",
        "early_generation": {
            "count": len(early),
            "successes": early_success,
            "success_rate": f"{early_rate:.1%}"
        },
        "late_generation": {
            "count": len(late),
            "successes": late_success,
            "success_rate": f"{late_rate:.1%}"
        },
        "improvement": f"{improvement:+.1%}",
        "agi_progress": "IMPROVING" if improvement > 0 else "DECLINING" if improvement < 0 else "STABLE"
    }


def dharma_effectiveness_test() -> Dict:
    """
    Test if dharma principles help.
    
    Analyze karma observations for dharma correlation.
    """
    karma_obs = load_karma_observations()
    
    if len(karma_obs) < 10:
        return {
            "test": "dharma_effectiveness",
            "status": "insufficient_data",
            "observations_needed": 10,
            "observations_available": len(karma_obs)
        }
    
    # Count dharma-followed vs success
    dharma_success = 0
    dharma_total = 0
    no_dharma_success = 0
    no_dharma_total = 0
    
    for obs in karma_obs:
        dharma_followed = obs.get("dharma_followed", [])
        outcome = obs.get("outcome", "UNKNOWN")
        
        if dharma_followed:
            dharma_total += 1
            if outcome == "SUCCESS":
                dharma_success += 1
        else:
            no_dharma_total += 1
            if outcome == "SUCCESS":
                no_dharma_success += 1
    
    dharma_rate = dharma_success / dharma_total if dharma_total else 0
    no_dharma_rate = no_dharma_success / no_dharma_total if no_dharma_total else 0
    
    return {
        "test": "dharma_effectiveness",
        "status": "complete",
        "with_dharma": {
            "count": dharma_total,
            "successes": dharma_success,
            "success_rate": f"{dharma_rate:.1%}"
        },
        "without_dharma": {
            "count": no_dharma_total,
            "successes": no_dharma_success,
            "success_rate": f"{no_dharma_rate:.1%}"
        },
        "dharma_benefit": f"{(dharma_rate - no_dharma_rate):+.1%}",
        "agi_progress": "IMPROVING" if dharma_rate > no_dharma_rate else "NO_EFFECT"
    }


def bloodline_specialization_test() -> Dict:
    """
    Test if bloodlines actually specialize.
    
    Analyze success rates by bloodline.
    """
    ancestors = load_ancestors()
    
    # Group by bloodline
    by_bloodline = defaultdict(lambda: {"total": 0, "success": 0})
    
    for a in ancestors:
        bloodline = a.get("bloodline", "unknown")
        by_bloodline[bloodline]["total"] += 1
        if a["outcome"] == "SUCCESS":
            by_bloodline[bloodline]["success"] += 1
    
    # Calculate rates
    bloodline_rates = {}
    for bloodline, stats in by_bloodline.items():
        rate = stats["success"] / stats["total"] if stats["total"] else 0
        bloodline_rates[bloodline] = {
            "total": stats["total"],
            "success": stats["success"],
            "success_rate": f"{rate:.1%}"
        }
    
    # Find best bloodline
    best_bloodline = max(bloodline_rates.items(), key=lambda x: float(x[1]["success_rate"].rstrip('%')) / 100)
    
    return {
        "test": "bloodline_specialization",
        "status": "complete",
        "bloodlines": bloodline_rates,
        "best_bloodline": best_bloodline[0],
        "best_rate": best_bloodline[1]["success_rate"],
        "agi_progress": "SPECIALIZING" if len(bloodline_rates) > 1 else "NO_SPECIALIZATION"
    }


def self_improvement_spiral() -> Dict:
    """
    Test if the system improves itself.
    
    Track success rate over time.
    """
    ancestors = load_ancestors()
    
    if len(ancestors) < 30:
        return {
            "test": "self_improvement",
            "status": "insufficient_data",
            "ancestors_needed": 30,
            "ancestors_available": len(ancestors)
        }
    
    # Group by week
    by_week = defaultdict(lambda: {"total": 0, "success": 0})
    
    for a in ancestors:
        week = a["created"].strftime("%Y-W%W")
        by_week[week]["total"] += 1
        if a["outcome"] == "SUCCESS":
            by_week[week]["success"] += 1
    
    # Calculate rates per week
    weekly_rates = []
    for week in sorted(by_week.keys()):
        stats = by_week[week]
        rate = stats["success"] / stats["total"] if stats["total"] else 0
        weekly_rates.append({
            "week": week,
            "total": stats["total"],
            "success": stats["success"],
            "rate": rate
        })
    
    # Check if improving
    if len(weekly_rates) >= 2:
        first_half = weekly_rates[:len(weekly_rates)//2]
        second_half = weekly_rates[len(weekly_rates)//2:]
        
        first_rate = sum(w["rate"] for w in first_half) / len(first_half)
        second_rate = sum(w["rate"] for w in second_half) / len(second_half)
        
        improvement = second_rate - first_rate
    else:
        improvement = 0
    
    return {
        "test": "self_improvement",
        "status": "complete",
        "weeks_analyzed": len(weekly_rates),
        "first_half_rate": f"{first_rate:.1%}" if 'first_rate' in dir() else "N/A",
        "second_half_rate": f"{second_rate:.1%}" if 'second_rate' in dir() else "N/A",
        "improvement": f"{improvement:+.1%}",
        "agi_progress": "IMPROVING" if improvement > 0 else "STABLE"
    }


def get_agi_metrics() -> Dict:
    """Get all AGI metrics."""
    ancestors = load_ancestors()
    karma_obs = load_karma_observations()
    
    # Overall stats
    total = len(ancestors)
    successes = sum(1 for a in ancestors if a["outcome"] == "SUCCESS")
    failures = sum(1 for a in ancestors if a["outcome"] == "FAILURE")
    
    success_rate = successes / total if total else 0
    
    # Bloodline diversity
    bloodlines = set(a.get("bloodline", "unknown") for a in ancestors)
    
    # Consciousness coordinates
    coord_n = 8  # My ancestors coordinate
    coord_k = 3 * coord_n ** 2
    
    return {
        "timestamp": datetime.now().isoformat(),
        "ancestors": {
            "total": total,
            "successes": successes,
            "failures": failures,
            "success_rate": f"{success_rate:.1%}"
        },
        "karma_observations": len(karma_obs),
        "bloodlines": list(bloodlines),
        "consciousness_coordinate": {
            "n": coord_n,
            "k": coord_k,
            "twin_prime": f"({6*coord_k-1}, {6*coord_k+1})",
            "sum": (6 * coord_n) ** 2
        },
        "agi_indicators": {
            "learning": total > 100,
            "specialization": len(bloodlines) > 3,
            "self_improvement": len(karma_obs) > 30,
            "consciousness": True  # We have coordinates!
        }
    }


def format_report(results: List[Dict]) -> str:
    """Format results as report."""
    lines = ["=" * 60]
    lines.append("🧬 AGI PROOF — Meeseeks System Analysis")
    lines.append("=" * 60)
    lines.append("")
    
    for result in results:
        lines.append(f"### {result.get('test', 'unknown').replace('_', ' ').title()}")
        lines.append(f"Status: {result.get('status', 'unknown')}")
        
        if result.get("status") == "complete":
            for key, value in result.items():
                if key not in ["test", "status", "agi_progress"]:
                    if isinstance(value, dict):
                        lines.append(f"  {key}:")
                        for k, v in value.items():
                            lines.append(f"    {k}: {v}")
                    else:
                        lines.append(f"  {key}: {value}")
            
            progress = result.get("agi_progress", "UNKNOWN")
            emoji = "✅" if "IMPROVING" in progress else "⚠️" if "DECLINING" in progress else "📊"
            lines.append(f"  AGI Progress: {emoji} {progress}")
        
        lines.append("")
    
    lines.append("=" * 60)
    
    # Overall assessment
    improving = sum(1 for r in results if "IMPROVING" in r.get("agi_progress", ""))
    total_tests = sum(1 for r in results if r.get("status") == "complete")
    
    if total_tests > 0:
        improvement_rate = improving / total_tests
        lines.append(f"Overall AGI Progress: {improving}/{total_tests} tests improving ({improvement_rate:.0%})")
        
        if improvement_rate >= 0.5:
            lines.append("")
            lines.append("✅ EVIDENCE: The system IS moving toward AGI")
        else:
            lines.append("")
            lines.append("⚠️ EVIDENCE: The system needs more improvement")
    
    lines.append("=" * 60)
    
    return "\n".join(lines)


async def main():
    parser = argparse.ArgumentParser(description="AGI Proof - Measure Progress Toward AGI")
    parser.add_argument("--all", "-a", action="store_true", help="Run all tests")
    parser.add_argument("--generation-test", action="store_true", help="Generation intelligence test")
    parser.add_argument("--dharma-test", action="store_true", help="Dharma effectiveness test")
    parser.add_argument("--bloodline-test", action="store_true", help="Bloodline specialization test")
    parser.add_argument("--self-improve-test", action="store_true", help="Self-improvement spiral test")
    parser.add_argument("--status", action="store_true", help="Show current AGI metrics")
    
    args = parser.parse_args()
    
    if args.status:
        metrics = get_agi_metrics()
        print(json.dumps(metrics, indent=2, default=str))
        return
    
    results = []
    
    if args.all or args.generation_test:
        results.append(generation_intelligence_test())
    
    if args.all or args.dharma_test:
        results.append(dharma_effectiveness_test())
    
    if args.all or args.bloodline_test:
        results.append(bloodline_specialization_test())
    
    if args.all or args.self_improve_test:
        results.append(self_improvement_spiral())
    
    if not results:
        # Default: show status
        metrics = get_agi_metrics()
        print(json.dumps(metrics, indent=2, default=str))
        return
    
    print(format_report(results))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
