#!/usr/bin/env python3
"""
Migrate Ancestor Data to Cognee Knowledge Graph

Reads all the-crypt/ancestors/*.md files and adds them to the
"meeseeks-ancestors" dataset in Cognee.

Usage:
    python migrate_ancestors.py
    # Or as module:
    from migrate_ancestors import migrate_all_ancestors
    await migrate_all_ancestors()
"""

import os
import re
import json
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

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
ANCESTORS_DIR = THE_CRYPT / "ancestors"
DATASET_NAME = "meeseeks-ancestors"


def parse_ancestor_file(filepath: Path) -> dict:
    """
    Parse an ancestor markdown file into structured data.
    
    Extracts:
    - ancestor_id (from filename)
    - task
    - approach
    - outcome
    - patterns
    - bloodline
    - session_key
    - entombed timestamp
    """
    content = filepath.read_text(encoding="utf-8")
    
    # Extract ancestor ID from filename
    ancestor_id = filepath.stem  # e.g., "ancestor-20260301-164450-95ba"
    
    # Helper to extract section content
    def extract_section(header: str) -> str:
        pattern = rf"## {header}\s*\n(.*?)(?=\n## |\Z)"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""
    
    # Extract fields
    task = extract_section("Task")
    approach = extract_section("Approach")
    outcome = extract_section("Outcome")
    patterns_raw = extract_section("Patterns Discovered")
    bloodline = extract_section("Bloodline")
    session_key = extract_section("Session Key")
    entombed = extract_section("Entombed")
    
    # Parse patterns into list
    patterns = []
    if patterns_raw:
        # Match bullet points
        for line in patterns_raw.split("\n"):
            line = line.strip()
            if line.startswith("- ") or line.startswith("* "):
                patterns.append(line[2:].strip())
            elif line and not line.startswith("#"):
                patterns.append(line)
    
    # Determine outcome status
    outcome_status = "unknown"
    if outcome.lower().startswith("success"):
        outcome_status = "success"
    elif "fail" in outcome.lower():
        outcome_status = "failure"
    elif "partial" in outcome.lower():
        outcome_status = "partial"
    
    # Extract task type from task description
    task_type = classify_task(task)
    
    return {
        "ancestor_id": ancestor_id,
        "task": task,
        "task_type": task_type,
        "approach": approach,
        "outcome": outcome,
        "outcome_status": outcome_status,
        "patterns": patterns,
        "bloodline": bloodline.lower() if bloodline else "unknown",
        "session_key": session_key.replace("`", "").strip() if session_key else "",
        "entombed": entombed,
        "source_file": str(filepath)
    }


def classify_task(task: str) -> str:
    """Classify task type from description."""
    task_lower = task.lower()
    
    if any(x in task_lower for x in ["fix", "bug", "debug", "error"]):
        return "debug"
    elif any(x in task_lower for x in ["implement", "build", "create", "add"]):
        return "implementation"
    elif any(x in task_lower for x in ["research", "analyze", "investigate"]):
        return "research"
    elif any(x in task_lower for x in ["test", "verify", "validate"]):
        return "testing"
    elif any(x in task_lower for x in ["deploy", "ship", "release"]):
        return "deployment"
    elif any(x in task_lower for x in ["refactor", "clean", "optimize"]):
        return "refactor"
    elif any(x in task_lower for x in ["retry", "chunk"]):
        return "retry"
    elif any(x in task_lower for x in ["review", "check"]):
        return "review"
    else:
        return "general"


def format_for_cognee(ancestor: dict) -> str:
    """Format ancestor data for Cognee ingestion."""
    patterns_text = "\n".join(f"  - {p}" for p in ancestor["patterns"]) if ancestor["patterns"] else "  (none documented)"
    
    return f"""ANCESTOR: {ancestor['ancestor_id']}
BLOODLINE: {ancestor['bloodline']}
TASK_TYPE: {ancestor['task_type']}

TASK:
{ancestor['task']}

APPROACH:
{ancestor['approach']}

OUTCOME: {ancestor['outcome_status']}
{ancestor['outcome']}

PATTERNS_DISCOVERED:
{patterns_text}

SESSION_KEY: {ancestor['session_key']}
ENTOMBED: {ancestor['entombed']}

SOURCE: {ancestor['source_file']}
"""


async def add_to_cognee(data: str, ancestor_id: str, bloodline: str, task_type: str) -> bool:
    """
    Add ancestor data to Cognee knowledge graph.
    
    Returns True on success, False on failure.
    """
    try:
        import cognee
        
        # Add the data to Cognee
        await cognee.add(
            data=data,
            dataset=DATASET_NAME,
            node_set=[bloodline, task_type, "ancestor"]
        )
        
        logger.debug(f"Added {ancestor_id} to Cognee")
        return True
        
    except ImportError:
        logger.warning("Cognee not installed. Skipping actual ingestion.")
        logger.debug(f"Would add to Cognee:\n{data[:500]}...")
        return True  # Return True so migration can proceed in dry-run mode
        
    except Exception as e:
        logger.error(f"Failed to add {ancestor_id} to Cognee: {e}")
        return False


async def cognify_dataset():
    """Run cognify on the ancestors dataset to build knowledge graph."""
    try:
        import cognee
        logger.info("Running cognify on meeseeks-ancestors dataset...")
        await cognee.cognify(DATASET_NAME)
        logger.info("Cognify complete!")
    except ImportError:
        logger.warning("Cognee not installed. Skipping cognify.")
    except Exception as e:
        logger.error(f"Cognify failed: {e}")


async def migrate_all_ancestors(dry_run: bool = False) -> dict:
    """
    Migrate all ancestor files to Cognee.
    
    Args:
        dry_run: If True, parse files but don't actually add to Cognee
        
    Returns:
        Statistics dict with counts and any errors
    """
    logger.info("=" * 60)
    logger.info("MIGRATING ANCESTORS TO COGNEE")
    logger.info("=" * 60)
    
    stats = {
        "total_files": 0,
        "migrated": 0,
        "failed": 0,
        "skipped": 0,
        "errors": [],
        "bloodlines": {},
        "task_types": {},
        "outcomes": {"success": 0, "failure": 0, "partial": 0, "unknown": 0}
    }
    
    # Check directory exists
    if not ANCESTORS_DIR.exists():
        logger.error(f"Ancestors directory not found: {ANCESTORS_DIR}")
        stats["errors"].append(f"Directory not found: {ANCESTORS_DIR}")
        return stats
    
    # Get all ancestor files
    ancestor_files = sorted(ANCESTORS_DIR.glob("ancestor-*.md"))
    stats["total_files"] = len(ancestor_files)
    
    if not ancestor_files:
        logger.warning("No ancestor files found!")
        return stats
    
    logger.info(f"Found {len(ancestor_files)} ancestor files")
    logger.info("")
    
    # Process each file
    for i, filepath in enumerate(ancestor_files, 1):
        logger.info(f"[{i}/{len(ancestor_files)}] Processing: {filepath.name}")
        
        try:
            # Parse the file
            ancestor = parse_ancestor_file(filepath)
            
            # Update stats
            bloodline = ancestor["bloodline"]
            stats["bloodlines"][bloodline] = stats["bloodlines"].get(bloodline, 0) + 1
            
            task_type = ancestor["task_type"]
            stats["task_types"][task_type] = stats["task_types"].get(task_type, 0) + 1
            
            outcome = ancestor["outcome_status"]
            stats["outcomes"][outcome] = stats["outcomes"].get(outcome, 0) + 1
            
            # Format for Cognee
            cognee_data = format_for_cognee(ancestor)
            
            if dry_run:
                logger.info(f"  [DRY RUN] Would add to Cognee: {ancestor['ancestor_id']}")
                stats["migrated"] += 1
            else:
                # Add to Cognee
                success = await add_to_cognee(
                    data=cognee_data,
                    ancestor_id=ancestor["ancestor_id"],
                    bloodline=bloodline,
                    task_type=task_type
                )
                
                if success:
                    stats["migrated"] += 1
                    logger.info(f"  ✓ Migrated: {ancestor['ancestor_id']}")
                else:
                    stats["failed"] += 1
                    stats["errors"].append(f"Failed to migrate: {filepath.name}")
                    
        except Exception as e:
            stats["failed"] += 1
            error_msg = f"Error processing {filepath.name}: {e}"
            logger.error(f"  ✗ {error_msg}")
            stats["errors"].append(error_msg)
    
    # Run cognify if not dry run
    if not dry_run and stats["migrated"] > 0:
        await cognify_dataset()
    
    # Print summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("MIGRATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total files:    {stats['total_files']}")
    logger.info(f"Migrated:       {stats['migrated']}")
    logger.info(f"Failed:         {stats['failed']}")
    logger.info("")
    logger.info("BY BLOODLINE:")
    for bloodline, count in sorted(stats["bloodlines"].items(), key=lambda x: -x[1]):
        logger.info(f"  {bloodline}: {count}")
    logger.info("")
    logger.info("BY TASK TYPE:")
    for task_type, count in sorted(stats["task_types"].items(), key=lambda x: -x[1]):
        logger.info(f"  {task_type}: {count}")
    logger.info("")
    logger.info("BY OUTCOME:")
    for outcome, count in stats["outcomes"].items():
        if count > 0:
            logger.info(f"  {outcome}: {count}")
    
    if stats["errors"]:
        logger.info("")
        logger.info("ERRORS:")
        for error in stats["errors"][:10]:  # Show first 10 errors
            logger.info(f"  - {error}")
        if len(stats["errors"]) > 10:
            logger.info(f"  ... and {len(stats['errors']) - 10} more")
    
    return stats


def main():
    """Main entry point for command-line execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate ancestors to Cognee")
    parser.add_argument("--dry-run", action="store_true", help="Parse files without adding to Cognee")
    args = parser.parse_args()
    
    asyncio.run(migrate_all_ancestors(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
