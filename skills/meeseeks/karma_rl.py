#!/usr/bin/env python3
"""
Karma Reinforcement Learning - Update dharma weights based on karma correlation.

The RL loop that was missing:
1. Analyze karma observations for success correlation
2. Update dharma.md with weighted principles
3. Strong principles = emphasized, weak principles = de-emphasized

Usage:
    python skills/meeseeks/karma_rl.py --check    # See what would change
    python skills/meeseeks/karma_rl.py --apply    # Update dharma.md
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Paths
CRYPT_ROOT = Path(__file__).parent.parent.parent / "the-crypt"
KARMA_LOG = CRYPT_ROOT / "karma_observations.jsonl"
DHARMA_FILE = CRYPT_ROOT / "dharma.md"
RL_LOG = CRYPT_ROOT / "karma_rl_log.jsonl"

# Thresholds
MIN_OBSERVATIONS = 10  # Need at least this many observations to trust correlation
STRONG_CORRELATION = 0.7  # 70%+ success when followed
WEAK_CORRELATION = 0.5  # 50% or less = principle doesn't matter


def analyze_karma_for_rl() -> Dict:
    """
    Analyze karma observations and return principle weights.

    Returns dict of {principle: {weight, success_rate, observations, recommendation}}
    """
    if not KARMA_LOG.exists():
        return {"error": "No karma observations found"}

    observations = []
    with open(KARMA_LOG, 'r') as f:
        for line in f:
            if line.strip():
                observations.append(json.loads(line))

    if len(observations) < MIN_OBSERVATIONS:
        return {
            "error": f"Insufficient observations ({len(observations)} < {MIN_OBSERVATIONS})",
            "observations": len(observations)
        }

    # Track success rates per principle
    principle_stats = {}

    for obs in observations:
        for principle in obs.get("dharma_inherited", []):
            if principle not in principle_stats:
                principle_stats[principle] = {
                    "followed_success": 0,
                    "followed_failure": 0,
                    "ignored_success": 0,
                    "ignored_failure": 0,
                    "name": principle.replace("_", " ").title()
                }

            # Track followed vs ignored
            if principle in obs.get("dharma_followed", []):
                if obs.get("outcome") == "success":
                    principle_stats[principle]["followed_success"] += 1
                else:
                    principle_stats[principle]["followed_failure"] += 1
            elif principle in obs.get("dharma_ignored", []):
                if obs.get("outcome") == "success":
                    principle_stats[principle]["ignored_success"] += 1
                else:
                    principle_stats[principle]["ignored_failure"] += 1

    # Calculate weights
    results = {}
    for principle, stats in principle_stats.items():
        followed_total = stats["followed_success"] + stats["followed_failure"]
        ignored_total = stats["ignored_success"] + stats["ignored_failure"]

        if followed_total == 0:
            continue  # Never followed, can't calculate

        followed_rate = stats["followed_success"] / followed_total if followed_total > 0 else 0
        ignored_rate = stats["ignored_success"] / ignored_total if ignored_total > 0 else 0.5

        # Weight = correlation strength
        # High weight = principle matters (big difference between followed/ignored)
        correlation = followed_rate - ignored_rate

        # Determine recommendation
        if followed_rate >= STRONG_CORRELATION and correlation >= 0.3:
            recommendation = "EMPHASIZE"
            weight = 1.0 + correlation
        elif followed_rate <= WEAK_CORRELATION and abs(correlation) < 0.1:
            recommendation = "DE_EMPHASIZE"
            weight = 0.5
        else:
            recommendation = "MAINTAIN"
            weight = 1.0

        results[principle] = {
            "name": stats["name"],
            "weight": round(weight, 2),
            "followed_success_rate": round(followed_rate * 100, 1),
            "ignored_success_rate": round(ignored_rate * 100, 1),
            "correlation": round(correlation * 100, 1),
            "followed_total": followed_total,
            "ignored_total": ignored_total,
            "recommendation": recommendation
        }

    return {
        "observations": len(observations),
        "principles": results,
        "timestamp": datetime.now().isoformat()
    }


def generate_dharma_update(analysis: Dict) -> str:
    """Generate updated dharma section with RL-weighted principles."""
    if "error" in analysis:
        return f"<!-- RL Update Failed: {analysis['error']} -->"

    principles = analysis.get("principles", {})

    lines = ["<!-- Karma RL Update - " + analysis["timestamp"] + " -->"]
    lines.append("<!-- Principle weights based on " + str(analysis["observations"]) + " observations -->")
    lines.append("")

    # Sort by weight (highest first)
    sorted_principles = sorted(
        principles.items(),
        key=lambda x: x[1]["weight"],
        reverse=True
    )

    lines.append("## RL-Weighted Principles (Auto-Updated)")
    lines.append("")

    for principle, data in sorted_principles:
        weight = data["weight"]
        rec = data["recommendation"]
        name = data["name"]

        # Emoji-free markers
        if rec == "EMPHASIZE":
            marker = "[CRITICAL]"
        elif rec == "DE_EMPHASIZE":
            marker = "[OPTIONAL]"
        else:
            marker = "[STANDARD]"

        lines.append(f"{marker} **{name}** (weight: {weight})")
        lines.append(f"  - Success when followed: {data['followed_success_rate']}% ({data['followed_total']} obs)")
        if data['ignored_total'] > 0:
            lines.append(f"  - Success when ignored: {data['ignored_success_rate']}% ({data['ignored_total']} obs)")
        lines.append(f"  - Correlation: {data['correlation']}%")
        lines.append("")

    return "\n".join(lines)


def apply_rl_update(dry_run: bool = False) -> bool:
    """Apply RL update to dharma.md."""
    analysis = analyze_karma_for_rl()

    if "error" in analysis:
        print(f"[karma_rl] Error: {analysis['error']}")
        return False

    update_section = generate_dharma_update(analysis)

    if dry_run:
        print("[karma_rl] DRY RUN - Would add to dharma.md:")
        print(update_section)
        return True

    # Read current dharma
    if not DHARMA_FILE.exists():
        print(f"[karma_rl] Error: {DHARMA_FILE} not found")
        return False

    with open(DHARMA_FILE, 'r', encoding='utf-8') as f:
        dharma_content = f.read()

    # Check if RL section already exists
    if "<!-- Karma RL Update -" in dharma_content:
        # Replace existing section
        pattern = r'<!-- Karma RL Update -.*?-->\n.*?(?=\n## |$)'
        dharma_content = re.sub(pattern, update_section, dharma_content, flags=re.DOTALL)
    else:
        # Append new section
        dharma_content += "\n\n" + update_section

    # Write back
    with open(DHARMA_FILE, 'w', encoding='utf-8') as f:
        f.write(dharma_content)

    # Log update
    with open(RL_LOG, 'a') as f:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "observations": analysis["observations"],
            "principles_updated": len(analysis["principles"]),
            "changes": {
                p: d["recommendation"]
                for p, d in analysis["principles"].items()
                if d["recommendation"] != "MAINTAIN"
            }
        }
        f.write(json.dumps(log_entry) + "\n")

    print(f"[karma_rl] Updated dharma.md with {len(analysis['principles'])} weighted principles")
    return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Karma RL - Update dharma with karma weights")
    parser.add_argument("--check", action="store_true", help="Check what would change (dry run)")
    parser.add_argument("--apply", action="store_true", help="Apply update to dharma.md")
    parser.add_argument("--stats", action="store_true", help="Show principle statistics")

    args = parser.parse_args()

    if args.stats or args.check:
        analysis = analyze_karma_for_rl()

        if "error" in analysis:
            print(f"Error: {analysis['error']}")
            return

        print("=" * 60)
        print("KARMA RL ANALYSIS")
        print("=" * 60)
        print(f"\nObservations: {analysis['observations']}")
        print("\nPrinciple Weights:\n")

        for principle, data in sorted(
            analysis["principles"].items(),
            key=lambda x: x[1]["weight"],
            reverse=True
        ):
            print(f"{data['recommendation']:12} {data['name']:30} weight={data['weight']:.2f}")

        if args.check:
            print("\n" + "=" * 60)
            print("PREVIEW OF DHARMA UPDATE:")
            print("=" * 60)
            print(generate_dharma_update(analysis))

    elif args.apply:
        apply_rl_update(dry_run=False)

    else:
        # Default: check
        analysis = analyze_karma_for_rl()
        if "error" in analysis:
            print(f"Error: {analysis['error']}")
        else:
            print(f"Ready to update: {len(analysis['principles'])} principles from {analysis['observations']} observations")
            print("Use --check to preview, --apply to update dharma.md")


if __name__ == "__main__":
    main()
