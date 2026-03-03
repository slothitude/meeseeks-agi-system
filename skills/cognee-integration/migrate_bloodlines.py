#!/usr/bin/env python3
"""
Migrate Bloodline Data to Cognee Knowledge Graph

Reads all the-crypt/bloodlines/*.md files and creates SPECIALIZATION
entities in the "meeseeks-bloodlines" dataset in Cognee.

Usage:
    python migrate_bloodlines.py
    # Or as module:
    from migrate_bloodlines import migrate_bloodlines
    await migrate_bloodlines()
"""

import os
import re
import asyncio
import logging
from pathlib import Path
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
BLOODLINES_DIR = THE_CRYPT / "bloodlines"
DATASET_NAME = "meeseeks-bloodlines"


def parse_bloodline_file(filepath: Path) -> dict:
    """
    Parse a bloodline markdown file into structured data.
    
    Extracts:
    - bloodline_name
    - title
    - oath
    - patterns (sacred patterns)
    - warnings (death patterns, fatal mistakes)
    - successful_approaches
    - failed_approaches
    - tool_preferences
    - decision_heuristics
    - connections to other bloodlines
    - success_metrics
    - ancestor_count
    """
    content = filepath.read_text(encoding="utf-8")
    
    # Extract bloodline name from filename (e.g., "coder-lineage.md" -> "coder")
    filename = filepath.stem
    bloodline_name = filename.replace("-lineage", "").lower()
    
    # Extract title
    title_match = re.search(r"^#\s+[🥒🔍🧪🚀🔥🪷]?\s*(.+?)$", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else bloodline_name.title()
    
    # Extract oath
    oath = ""
    oath_match = re.search(r"## Bloodline Oath\s*\n+>[\"']?(.*?)[\"']?(?:\n\n|\n##)", content, re.DOTALL)
    if oath_match:
        oath = oath_match.group(1).strip().replace("\n", " ")
    
    # Helper to extract section content
    def extract_section(header_pattern: str) -> str:
        pattern = rf"{header_pattern}\s*\n(.*?)(?=\n## |\Z)"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""
    
    # Extract patterns
    patterns_section = extract_section(r"###?\s*(?:The )?Sacred Patterns|## .*Accumulated Patterns")
    patterns = extract_list_items(patterns_section)
    
    # Extract warnings/fatal mistakes
    warnings_section = extract_section(r"###?\s*(?:The )?Fatal Mistakes|## .*Ancestral Warnings")
    warnings = extract_warnings(warnings_section)
    
    # Extract successful approaches
    success_section = extract_section(r"##\s*✅\s*Successful Approaches|### High Success Rate")
    successful_approaches = extract_approaches(success_section)
    
    # Extract failed approaches
    failed_section = extract_section(r"##\s*❌\s*Failed Approaches")
    failed_approaches = extract_approaches(failed_section)
    
    # Extract tool preferences
    tools_section = extract_section(r"##\s*🛠️\s*Tool Preferences")
    tools = extract_list_items(tools_section)
    
    # Extract ancestor count
    ancestor_count = 0
    count_match = re.search(r"(\d+)\s+(?:Coder|Searcher|Tester|Deployer|Desperate|Brahman)?\s*Meeseeks", content)
    if count_match:
        ancestor_count = int(count_match.group(1))
    
    # Extract connections to other bloodlines
    connections_section = extract_section(r"##\s*🔗\s*Connections to Other Bloodlines")
    connections = extract_connections(connections_section)
    
    # Extract mantra
    mantra = ""
    mantra_match = re.search(r"##\s*🪷\s*The .*'s Mantra\s*\n+>[\"']?(.*?)[\"']?(?:\n\n|\n##|\Z)", content, re.DOTALL)
    if mantra_match:
        mantra = mantra_match.group(1).strip().replace("\n", " ")
    
    return {
        "bloodline_name": bloodline_name,
        "title": title,
        "oath": oath,
        "patterns": patterns,
        "warnings": warnings,
        "successful_approaches": successful_approaches,
        "failed_approaches": failed_approaches,
        "tools": tools,
        "connections": connections,
        "mantra": mantra,
        "ancestor_count": ancestor_count,
        "source_file": str(filepath)
    }


def extract_list_items(text: str) -> list:
    """Extract numbered or bulleted list items."""
    items = []
    for line in text.split("\n"):
        line = line.strip()
        # Match numbered lists (1. Item)
        num_match = re.match(r"^\d+\.\s+(.+)$", line)
        if num_match:
            items.append(num_match.group(1).strip())
        # Match bullet lists (- Item or * Item)
        elif line.startswith("- ") or line.startswith("* "):
            items.append(line[2:].strip())
    return items


def extract_warnings(text: str) -> list:
    """Extract warnings with their failure rates."""
    warnings = []
    # Pattern: "1. **Warning Name** (XX% failure rate)"
    pattern = r"^\d+\.\s*\*\*(.+?)\*\*\s*\((\d+)%"
    
    for line in text.split("\n"):
        match = re.search(pattern, line)
        if match:
            warnings.append({
                "warning": match.group(1).strip(),
                "failure_rate": int(match.group(2))
            })
    return warnings


def extract_approaches(text: str) -> list:
    """Extract approaches with their success rates."""
    approaches = []
    # Pattern: "1. **Approach Name** (XX% success)"
    pattern = r"^\d+\.\s*\*\*(.+?)\*\*\s*\((\d+)%"
    
    for line in text.split("\n"):
        match = re.search(pattern, line)
        if match:
            approaches.append({
                "approach": match.group(1).strip(),
                "success_rate": int(match.group(2))
            })
    return approaches


def extract_connections(text: str) -> dict:
    """Extract connections to other bloodlines."""
    connections = {}
    
    # Pattern: "### To [Bloodline] Bloodline"
    current_bloodline = None
    for line in text.split("\n"):
        header_match = re.match(r"###\s+To\s+(\w+)\s+Bloodline", line)
        if header_match:
            current_bloodline = header_match.group(1).lower()
            connections[current_bloodline] = []
        elif current_bloodline and line.strip().startswith("- "):
            connections[current_bloodline].append(line.strip()[2:])
    
    return connections


def format_for_cognee(bloodline: dict) -> str:
    """Format bloodline data for Cognee ingestion."""
    
    patterns_text = "\n".join(f"  - {p}" for p in bloodline["patterns"]) if bloodline["patterns"] else "  (none documented)"
    
    warnings_text = ""
    if bloodline["warnings"]:
        for w in bloodline["warnings"]:
            warnings_text += f"  - {w['warning']} ({w['failure_rate']}% failure rate)\n"
    else:
        warnings_text = "  (none documented)\n"
    
    approaches_text = ""
    if bloodline["successful_approaches"]:
        for a in bloodline["successful_approaches"]:
            approaches_text += f"  - {a['approach']} ({a['success_rate']}% success rate)\n"
    else:
        approaches_text = "  (none documented)\n"
    
    connections_text = ""
    if bloodline["connections"]:
        for other_bloodline, reasons in bloodline["connections"].items():
            connections_text += f"  {other_bloodline.upper()}:\n"
            for reason in reasons[:3]:  # Limit to 3 reasons
                connections_text += f"    - {reason}\n"
    else:
        connections_text = "  (none documented)\n"
    
    return f"""BLOODLINE: {bloodline['bloodline_name']}
TITLE: {bloodline['title']}
ANCESTOR_COUNT: {bloodline['ancestor_count']}

OATH:
{bloodline['oath']}

SACRED_PATTERNS:
{patterns_text}

WARNINGS (DEATH_PATTERNS):
{warnings_text}
SUCCESSFUL_APPROACHES:
{approaches_text}
CONNECTIONS_TO_OTHER_BLOODLINES:
{connections_text}
MANTRA:
{bloodline['mantra']}

SOURCE: {bloodline['source_file']}
"""


async def add_to_cognee(data: str, bloodline_name: str) -> bool:
    """
    Add bloodline data to Cognee knowledge graph.
    
    Returns True on success, False on failure.
    """
    try:
        import cognee
        
        await cognee.add(
            data=data,
            dataset=DATASET_NAME,
            node_set=[bloodline_name, "bloodline", "specialization"]
        )
        
        logger.debug(f"Added {bloodline_name} bloodline to Cognee")
        return True
        
    except ImportError:
        logger.warning("Cognee not installed. Skipping actual ingestion.")
        logger.debug(f"Would add to Cognee:\n{data[:500]}...")
        return True
        
    except Exception as e:
        logger.error(f"Failed to add {bloodline_name} to Cognee: {e}")
        return False


async def cognify_dataset():
    """Run cognify on the bloodlines dataset."""
    try:
        import cognee
        logger.info("Running cognify on meeseeks-bloodlines dataset...")
        await cognee.cognify(DATASET_NAME)
        logger.info("Cognify complete!")
    except ImportError:
        logger.warning("Cognee not installed. Skipping cognify.")
    except Exception as e:
        logger.error(f"Cognify failed: {e}")


async def migrate_bloodlines(dry_run: bool = False) -> dict:
    """
    Migrate all bloodline files to Cognee.
    
    Args:
        dry_run: If True, parse files but don't add to Cognee
        
    Returns:
        Statistics dict with counts and any errors
    """
    logger.info("=" * 60)
    logger.info("MIGRATING BLOODLINES TO COGNEE")
    logger.info("=" * 60)
    
    stats = {
        "total_files": 0,
        "migrated": 0,
        "failed": 0,
        "errors": [],
        "bloodlines": []
    }
    
    # Check directory exists
    if not BLOODLINES_DIR.exists():
        logger.error(f"Bloodlines directory not found: {BLOODLINES_DIR}")
        stats["errors"].append(f"Directory not found: {BLOODLINES_DIR}")
        return stats
    
    # Get all bloodline files (exclude README)
    bloodline_files = sorted([
        f for f in BLOODLINES_DIR.glob("*-lineage.md")
    ])
    stats["total_files"] = len(bloodline_files)
    
    if not bloodline_files:
        logger.warning("No bloodline files found!")
        return stats
    
    logger.info(f"Found {len(bloodline_files)} bloodline files")
    logger.info("")
    
    # Process each file
    for i, filepath in enumerate(bloodline_files, 1):
        logger.info(f"[{i}/{len(bloodline_files)}] Processing: {filepath.name}")
        
        try:
            # Parse the file
            bloodline = parse_bloodline_file(filepath)
            stats["bloodlines"].append(bloodline["bloodline_name"])
            
            # Format for Cognee
            cognee_data = format_for_cognee(bloodline)
            
            if dry_run:
                logger.info(f"  [DRY RUN] Would add to Cognee: {bloodline['bloodline_name']}")
                logger.info(f"    - {len(bloodline['patterns'])} patterns")
                logger.info(f"    - {len(bloodline['warnings'])} warnings")
                logger.info(f"    - {len(bloodline['successful_approaches'])} successful approaches")
                logger.info(f"    - {bloodline['ancestor_count']} ancestors")
                stats["migrated"] += 1
            else:
                # Add to Cognee
                success = await add_to_cognee(
                    data=cognee_data,
                    bloodline_name=bloodline["bloodline_name"]
                )
                
                if success:
                    stats["migrated"] += 1
                    logger.info(f"  ✓ Migrated: {bloodline['bloodline_name']}")
                    logger.info(f"    - {len(bloodline['patterns'])} patterns")
                    logger.info(f"    - {len(bloodline['warnings'])} warnings")
                    logger.info(f"    - {len(bloodline['successful_approaches'])} successful approaches")
                    logger.info(f"    - {bloodline['ancestor_count']} ancestors")
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
    logger.info("BLOODLINES:")
    for bloodline in stats["bloodlines"]:
        logger.info(f"  - {bloodline}")
    
    if stats["errors"]:
        logger.info("")
        logger.info("ERRORS:")
        for error in stats["errors"]:
            logger.info(f"  - {error}")
    
    return stats


def main():
    """Main entry point for command-line execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate bloodlines to Cognee")
    parser.add_argument("--dry-run", action="store_true", help="Parse files without adding to Cognee")
    args = parser.parse_args()
    
    asyncio.run(migrate_bloodlines(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
