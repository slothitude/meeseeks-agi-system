#!/usr/bin/env python3
"""
Master Migration Script - Run All Cognee Migrations

Runs all migration scripts in the correct order with progress reporting
and error handling.

Usage:
    python migrate_all.py
    python migrate_all.py --dry-run
    python migrate_all.py --skip ancestors
"""

import asyncio
import logging
import argparse
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

# Migration order (dependencies matter)
MIGRATION_ORDER = [
    ("bloodlines", "Bloodlines (specializations)"),
    ("dharma", "Dharma (principles)"),
    ("ancestors", "Ancestors (death reports)"),
    ("karma", "Karma (outcome observations)"),
]


async def run_migration(name: str, dry_run: bool = False) -> dict:
    """Run a single migration by name."""
    
    if name == "ancestors":
        from migrate_ancestors import migrate_all_ancestors
        return await migrate_all_ancestors(dry_run=dry_run)
    
    elif name == "bloodlines":
        from migrate_bloodlines import migrate_bloodlines
        return await migrate_bloodlines(dry_run=dry_run)
    
    elif name == "dharma":
        from migrate_dharma import migrate_dharma
        return await migrate_dharma(dry_run=dry_run)
    
    elif name == "karma":
        from migrate_karma import migrate_karma
        return await migrate_karma(dry_run=dry_run)
    
    else:
        return {"error": f"Unknown migration: {name}"}


async def migrate_all(dry_run: bool = False, skip: list = None) -> dict:
    """
    Run all migrations in order.
    
    Args:
        dry_run: If True, parse files but don't add to Cognee
        skip: List of migration names to skip
        
    Returns:
        Combined statistics from all migrations
    """
    start_time = datetime.now()
    skip = skip or []
    
    logger.info("=" * 70)
    logger.info("🥒 COGNEE DATA MIGRATION - MASTER SCRIPT")
    logger.info("=" * 70)
    logger.info(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Mode: {'DRY RUN' if dry_run else 'LIVE MIGRATION'}")
    if skip:
        logger.info(f"Skipping: {', '.join(skip)}")
    logger.info("")
    
    results = {
        "started": start_time.isoformat(),
        "dry_run": dry_run,
        "migrations": {},
        "totals": {
            "migrated": 0,
            "failed": 0,
            "errors": []
        },
        "skipped": skip
    }
    
    # Run each migration in order
    for i, (name, description) in enumerate(MIGRATION_ORDER, 1):
        if name in skip:
            logger.info(f"[{i}/{len(MIGRATION_ORDER)}] ⏭️  SKIPPING: {description}")
            logger.info("")
            continue
        
        logger.info("-" * 70)
        logger.info(f"[{i}/{len(MIGRATION_ORDER)}] 🔄 RUNNING: {description}")
        logger.info("-" * 70)
        
        try:
            migration_result = await run_migration(name, dry_run=dry_run)
            results["migrations"][name] = migration_result
            
            # Update totals
            if "migrated" in migration_result:
                results["totals"]["migrated"] += migration_result.get("migrated", 0)
            if "failed" in migration_result:
                results["totals"]["failed"] += migration_result.get("failed", 0)
            if "errors" in migration_result:
                results["totals"]["errors"].extend(migration_result.get("errors", []))
            
            logger.info("")
            
        except Exception as e:
            logger.error(f"✗ Migration failed: {name} - {e}")
            results["migrations"][name] = {"error": str(e)}
            results["totals"]["errors"].append(f"{name}: {e}")
            logger.info("")
    
    # Final summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    results["completed"] = end_time.isoformat()
    results["duration_seconds"] = duration
    
    logger.info("=" * 70)
    logger.info("🏁 MIGRATION COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Completed: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Duration: {duration:.1f} seconds")
    logger.info("")
    logger.info("TOTALS:")
    logger.info(f"  Total migrated: {results['totals']['migrated']}")
    logger.info(f"  Total failed:   {results['totals']['failed']}")
    logger.info(f"  Total errors:   {len(results['totals']['errors'])}")
    
    # Per-migration summary
    logger.info("")
    logger.info("BY MIGRATION:")
    for name, description in MIGRATION_ORDER:
        if name in skip:
            logger.info(f"  {name}: SKIPPED")
        elif name in results["migrations"]:
            m = results["migrations"][name]
            if "error" in m:
                logger.info(f"  {name}: ERROR - {m['error']}")
            else:
                logger.info(f"  {name}: {m.get('migrated', 0)} migrated, {m.get('failed', 0)} failed")
    
    if results["totals"]["errors"]:
        logger.info("")
        logger.info("ERRORS:")
        for error in results["totals"]["errors"][:10]:
            logger.info(f"  - {error}")
        if len(results["totals"]["errors"]) > 10:
            logger.info(f"  ... and {len(results['totals']['errors']) - 10} more")
    
    logger.info("")
    if dry_run:
        logger.info("✅ DRY RUN COMPLETE - No data was added to Cognee")
        logger.info("Run without --dry-run to perform actual migration")
    else:
        logger.info("✅ ALL MIGRATIONS COMPLETE")
        logger.info("Cognee knowledge graph has been updated!")
    
    return results


async def verify_prerequisites() -> bool:
    """Check that all prerequisites are met before migration."""
    logger.info("Checking prerequisites...")
    
    # Check that the-crypt exists
    workspace = Path(__file__).parent.parent.parent
    the_crypt = workspace / "the-crypt"
    
    if not the_crypt.exists():
        logger.error(f"✗ the-crypt directory not found: {the_crypt}")
        return False
    
    # Check required directories
    required = [
        the_crypt / "ancestors",
        the_crypt / "bloodlines",
    ]
    
    for path in required:
        if not path.exists():
            logger.error(f"✗ Required directory not found: {path}")
            return False
    
    # Check required files
    required_files = [
        the_crypt / "dharma.md",
        the_crypt / "karma_observations.jsonl",
    ]
    
    for path in required_files:
        if not path.exists():
            logger.error(f"✗ Required file not found: {path}")
            return False
    
    logger.info("✓ All prerequisites met")
    return True


def main():
    """Main entry point for command-line execution."""
    parser = argparse.ArgumentParser(
        description="Run all Cognee migrations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python migrate_all.py                    # Run all migrations
  python migrate_all.py --dry-run          # Test without adding to Cognee
  python migrate_all.py --skip karma       # Skip karma migration
  python migrate_all.py --skip ancestors --skip bloodlines  # Skip multiple
        """
    )
    parser.add_argument(
        "--dry-run", 
        action="store_true", 
        help="Parse files without adding to Cognee"
    )
    parser.add_argument(
        "--skip", 
        action="append", 
        default=[],
        choices=["ancestors", "bloodlines", "dharma", "karma"],
        help="Skip specific migration (can be used multiple times)"
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Skip prerequisite verification"
    )
    args = parser.parse_args()
    
    async def run():
        if not args.no_verify:
            if not await verify_prerequisites():
                logger.error("Prerequisites not met. Aborting.")
                return 1
        
        results = await migrate_all(dry_run=args.dry_run, skip=args.skip)
        
        # Return non-zero if any errors
        if results["totals"]["failed"] > 0 or len(results["totals"]["errors"]) > 0:
            return 1
        return 0
    
    exit_code = asyncio.run(run())
    exit(exit_code)


if __name__ == "__main__":
    main()
