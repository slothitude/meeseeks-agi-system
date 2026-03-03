#!/usr/bin/env python3
"""
Migrate Karma Data to Cognee Knowledge Graph

Reads the-crypt/karma_observations.jsonl and creates OUTCOME entities
in the "meeseeks-karma" dataset in Cognee.

Usage:
    python migrate_karma.py
    # Or as module:
    from migrate_karma import migrate_karma
    await migrate_karma()
"""

import os
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Paths
WORKSPACE_ROOT = Path(__file__).parent.parent.parent
THE_CRYPT = WORKSPACE_ROOT / "the-crypt"
KARMA_FILE = THE_CRYPT / "karma_observations.jsonl"
DATASET_NAME = "meeseeks-karma"


def parse_karma_file(filepath: Path) -> list:
    """
    Parse the karma observations JSONL file.
    
    Each line is a JSON object with:
    - timestamp
    - ancestor_id
    - ancestor_file
    - task
    - dharma_inherited
    - dharma_followed
    - dharma_ignored
    - dharma_unclear
    - outcome
    - insight
    - alignment
    """
    observations = []
    
    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                obs = json.loads(line)
                observations.append(obs)
            except json.JSONDecodeError as e:
                logger.warning(f"Skipping invalid JSON on line {line_num}: {e}")
    
    return observations


def analyze_karma_patterns(observations: list) -> dict:
    """
    Analyze karma observations to extract patterns.
    
    Returns:
        Statistics and correlation data
    """
    analysis = {
        "total_observations": len(observations),
        "outcomes": defaultdict(int),
        "dharma_followed_success": defaultdict(int),
        "dharma_followed_failure": defaultdict(int),
        "dharma_ignored_success": defaultdict(int),
        "dharma_ignored_failure": defaultdict(int),
        "alignment_distribution": {"high": 0, "medium": 0, "low": 0},
        "avg_alignment": 0.0,
        "principle_effectiveness": defaultdict(lambda: {"success": 0, "failure": 0, "total": 0})
    }
    
    total_alignment = 0.0
    
    for obs in observations:
        outcome = obs.get("outcome", "unknown")
        analysis["outcomes"][outcome] += 1
        
        alignment = obs.get("alignment", 0.5)
        total_alignment += alignment
        
        if alignment >= 0.7:
            analysis["alignment_distribution"]["high"] += 1
        elif alignment >= 0.5:
            analysis["alignment_distribution"]["medium"] += 1
        else:
            analysis["alignment_distribution"]["low"] += 1
        
        # Track dharma followed vs outcome
        for principle in obs.get("dharma_followed", []):
            analysis["principle_effectiveness"][principle]["total"] += 1
            if outcome == "success":
                analysis["dharma_followed_success"][principle] += 1
                analysis["principle_effectiveness"][principle]["success"] += 1
            else:
                analysis["dharma_followed_failure"][principle] += 1
                analysis["principle_effectiveness"][principle]["failure"] += 1
        
        # Track dharma ignored vs outcome
        for principle in obs.get("dharma_ignored", []):
            if outcome == "success":
                analysis["dharma_ignored_success"][principle] += 1
            else:
                analysis["dharma_ignored_failure"][principle] += 1
    
    if observations:
        analysis["avg_alignment"] = total_alignment / len(observations)
    
    return analysis


def format_observation_for_cognee(obs: dict) -> str:
    """Format a single karma observation for Cognee ingestion."""
    
    dharma_inherited = ", ".join(obs.get("dharma_inherited", [])) or "none"
    dharma_followed = ", ".join(obs.get("dharma_followed", [])) or "none"
    dharma_ignored = ", ".join(obs.get("dharma_ignored", [])) or "none"
    dharma_unclear = ", ".join(obs.get("dharma_unclear", [])) or "none"
    
    return f"""KARMA_OBSERVATION
ANCESTOR_ID: {obs.get('ancestor_id', 'unknown')}
TIMESTAMP: {obs.get('timestamp', 'unknown')}
OUTCOME: {obs.get('outcome', 'unknown')}
ALIGNMENT: {obs.get('alignment', 0.5)}

TASK:
{obs.get('task', 'unknown')}

DHARMA_INHERITED: {dharma_inherited}
DHARMA_FOLLOWED: {dharma_followed}
DHARMA_IGNORED: {dharma_ignored}
DHARMA_UNCLEAR: {dharma_unclear}

INSIGHT:
{obs.get('insight', 'none')}

SOURCE: {obs.get('ancestor_file', 'unknown')}
"""


def format_analysis_for_cognee(analysis: dict) -> str:
    """Format karma analysis for Cognee ingestion."""
    
    outcomes_text = "\n".join(f"  {k}: {v}" for k, v in analysis["outcomes"].items())
    
    followed_success = "\n".join(
        f"  {k}: {v}" for k, v in sorted(
            analysis["dharma_followed_success"].items(), 
            key=lambda x: -x[1]
        )[:10]
    )
    
    principle_effectiveness = ""
    for principle, stats in sorted(
        analysis["principle_effectiveness"].items(),
        key=lambda x: -x[1]["total"]
    )[:10]:
        if stats["total"] > 0:
            success_rate = stats["success"] / stats["total"] * 100
            principle_effectiveness += f"  {principle}: {success_rate:.1f}% ({stats['success']}/{stats['total']})\n"
    
    return f"""KARMA_ANALYSIS
TOTAL_OBSERVATIONS: {analysis['total_observations']}
AVERAGE_ALIGNMENT: {analysis['avg_alignment']:.2f}

OUTCOME_DISTRIBUTION:
{outcomes_text}

ALIGNMENT_DISTRIBUTION:
  High (>=0.7): {analysis['alignment_distribution']['high']}
  Medium (0.5-0.7): {analysis['alignment_distribution']['medium']}
  Low (<0.5): {analysis['alignment_distribution']['low']}

TOP_DHARMA_FOLLOWED_FOR_SUCCESS:
{followed_success}

PRINCIPLE_EFFECTIVENESS (SUCCESS_RATE):
{principle_effectiveness}
"""


async def add_to_cognee(data: str, node_type: str) -> bool:
    """
    Add karma data to Cognee knowledge graph.
    
    Returns True on success, False on failure.
    """
    try:
        import cognee
        
        await cognee.add(
            data=data,
            dataset=DATASET_NAME,
            node_set=[node_type, "karma", "outcome"]
        )
        
        logger.debug(f"Added {node_type} to Cognee")
        return True
        
    except ImportError:
        logger.warning("Cognee not installed. Skipping actual ingestion.")
        logger.debug(f"Would add to Cognee:\n{data[:500]}...")
        return True
        
    except Exception as e:
        logger.error(f"Failed to add {node_type} to Cognee: {e}")
        return False


async def cognify_dataset():
    """Run cognify on the karma dataset."""
    try:
        import cognee
        logger.info("Running cognify on meeseeks-karma dataset...")
        await cognee.cognify(DATASET_NAME)
        logger.info("Cognify complete!")
    except ImportError:
        logger.warning("Cognee not installed. Skipping cognify.")
    except Exception as e:
        logger.error(f"Cognify failed: {e}")


async def migrate_karma(dry_run: bool = False, batch_size: int = 50) -> dict:
    """
    Migrate karma observations to Cognee.
    
    Args:
        dry_run: If True, parse file but don't add to Cognee
        batch_size: Number of observations to process before reporting progress
        
    Returns:
        Statistics dict with counts and any errors
    """
    logger.info("=" * 60)
    logger.info("MIGRATING KARMA TO COGNEE")
    logger.info("=" * 60)
    
    stats = {
        "total_observations": 0,
        "migrated": 0,
        "failed": 0,
        "errors": [],
        "outcomes": {},
        "avg_alignment": 0.0
    }
    
    # Check file exists
    if not KARMA_FILE.exists():
        logger.error(f"Karma file not found: {KARMA_FILE}")
        stats["errors"].append(f"File not found: {KARMA_FILE}")
        return stats
    
    logger.info(f"Reading: {KARMA_FILE}")
    
    try:
        # Parse observations
        observations = parse_karma_file(KARMA_FILE)
        stats["total_observations"] = len(observations)
        
        if not observations:
            logger.warning("No karma observations found!")
            return stats
        
        logger.info(f"Found {len(observations)} karma observations")
        
        # Analyze patterns
        analysis = analyze_karma_patterns(observations)
        stats["outcomes"] = dict(analysis["outcomes"])
        stats["avg_alignment"] = analysis["avg_alignment"]
        
        logger.info(f"  Success: {stats['outcomes'].get('success', 0)}")
        logger.info(f"  Failure: {stats['outcomes'].get('failure', 0)}")
        logger.info(f"  Avg alignment: {stats['avg_alignment']:.2f}")
        logger.info("")
        
        if dry_run:
            logger.info("[DRY RUN] Would add to Cognee:")
            logger.info(f"  - {stats['total_observations']} observations")
            logger.info("  - 1 analysis summary")
            stats["migrated"] = stats["total_observations"] + 1
        else:
            # Add analysis summary first
            analysis_data = format_analysis_for_cognee(analysis)
            if await add_to_cognee(analysis_data, "karma_analysis"):
                logger.info("  ✓ Migrated karma analysis")
                stats["migrated"] += 1
            else:
                stats["failed"] += 1
                stats["errors"].append("Failed to migrate karma analysis")
            
            # Add individual observations in batches
            for i, obs in enumerate(observations, 1):
                if i % batch_size == 0:
                    logger.info(f"  Progress: {i}/{len(observations)}")
                
                obs_data = format_observation_for_cognee(obs)
                if await add_to_cognee(obs_data, "karma_observation"):
                    stats["migrated"] += 1
                else:
                    stats["failed"] += 1
                    if len(stats["errors"]) < 10:
                        stats["errors"].append(f"Failed to migrate: {obs.get('ancestor_id', 'unknown')}")
            
            # Run cognify
            if stats["migrated"] > 0:
                await cognify_dataset()
        
    except Exception as e:
        stats["failed"] += 1
        error_msg = f"Error processing karma: {e}"
        logger.error(f"  ✗ {error_msg}")
        stats["errors"].append(error_msg)
    
    # Print summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("MIGRATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total observations: {stats['total_observations']}")
    logger.info(f"Migrated:           {stats['migrated']}")
    logger.info(f"Failed:             {stats['failed']}")
    logger.info(f"Avg alignment:      {stats['avg_alignment']:.2f}")
    logger.info("")
    logger.info("OUTCOMES:")
    for outcome, count in stats["outcomes"].items():
        logger.info(f"  {outcome}: {count}")
    
    if stats["errors"]:
        logger.info("")
        logger.info("ERRORS:")
        for error in stats["errors"][:10]:
            logger.info(f"  - {error}")
        if len(stats["errors"]) > 10:
            logger.info(f"  ... and {len(stats['errors']) - 10} more")
    
    return stats


def main():
    """Main entry point for command-line execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate karma to Cognee")
    parser.add_argument("--dry-run", action="store_true", help="Parse file without adding to Cognee")
    parser.add_argument("--batch-size", type=int, default=50, help="Batch size for progress reporting")
    args = parser.parse_args()
    
    asyncio.run(migrate_karma(dry_run=args.dry_run, batch_size=args.batch_size))


if __name__ == "__main__":
    main()
