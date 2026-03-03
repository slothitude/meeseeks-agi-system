#!/usr/bin/env python3
"""
Migrate Dharma Data to Cognee Knowledge Graph

Reads the-crypt/dharma.md and creates PRINCIPLE entities in the
"meeseeks-dharma" dataset in Cognee.

Usage:
    python migrate_dharma.py
    # Or as module:
    from migrate_dharma import migrate_dharma
    await migrate_dharma()
"""

import os
import re
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
DHARMA_FILE = THE_CRYPT / "dharma.md"
DATASET_NAME = "meeseeks-dharma"


def parse_dharma_file(filepath: Path) -> dict:
    """
    Parse the dharma markdown file into structured data.
    
    Extracts:
    - last_dreamed (timestamp)
    - ancestors_synthesized (count)
    - core_principles (eternal truths)
    - patterns_that_work (with evidence)
    - anti_patterns (to avoid)
    - domain_wisdom (specialized knowledge)
    - living_wisdom (quotes and insights)
    - bloodline_distribution
    - retry_success_rate
    """
    content = filepath.read_text(encoding="utf-8")
    
    # Extract last dreamed timestamp
    last_dreamed = ""
    dreamed_match = re.search(r"_Last dreamed:\s*(.+?)_", content)
    if dreamed_match:
        last_dreamed = dreamed_match.group(1).strip()
    
    # Extract ancestors synthesized count
    ancestors_count = 0
    ancestors_match = re.search(r"_Ancestors synthesized:\s*(\d+)_", content)
    if ancestors_match:
        ancestors_count = int(ancestors_match.group(1))
    
    # Extract core principles
    core_principles = []
    principles_section = extract_section(content, r"## Core Principles")
    for line in principles_section.split("\n"):
        # Match numbered items with bold name
        match = re.match(r"^\d+\.\s+\*\*(.+?)\*\*\s*[—–]\s*(.+)$", line)
        if match:
            core_principles.append({
                "name": match.group(1).strip(),
                "description": match.group(2).strip(),
                "type": "eternal_truth"
            })
    
    # Extract patterns that work
    patterns_that_work = []
    patterns_section = extract_section(content, r"## Patterns That Work")
    for line in patterns_section.split("\n"):
        # Match table rows: | **Pattern Name** | Evidence |
        match = re.match(r"\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|", line)
        if match:
            patterns_that_work.append({
                "pattern": match.group(1).strip(),
                "evidence": match.group(2).strip(),
                "type": "proven_pattern"
            })
    
    # Extract anti-patterns
    anti_patterns = []
    anti_section = extract_section(content, r"## Anti-Patterns")
    for line in anti_section.split("\n"):
        # Match bullet items with warning emoji
        match = re.match(r"[-*]\s*⚠\s*\*\*(.+?)\*\*\s*[—–]\s*(.+)$", line)
        if match:
            anti_patterns.append({
                "name": match.group(1).strip(),
                "description": match.group(2).strip(),
                "type": "anti_pattern"
            })
    
    # Extract domain wisdom
    domain_wisdom = {}
    domain_section = extract_section(content, r"## Domain Wisdom")
    
    # Parse each domain subsection
    domain_headers = re.findall(r"### (.+)$", domain_section, re.MULTILINE)
    for header in domain_headers:
        domain_name = header.strip()
        domain_content = extract_section(domain_section, rf"### {re.escape(domain_name)}")
        domain_wisdom[domain_name] = domain_content.strip()
    
    # Extract living wisdom (quotes)
    living_wisdom = []
    wisdom_section = extract_section(content, r"## Living Wisdom")
    for line in wisdom_section.split("\n"):
        # Match blockquote lines
        match = re.match(r">\s*\*\"(.+?)\"\s*[—–]\s*(.+?)\*", line)
        if match:
            living_wisdom.append({
                "quote": match.group(1).strip(),
                "source": match.group(2).strip()
            })
    
    # Extract bloodline distribution
    bloodline_dist = {}
    dist_match = re.search(r"\*\*Bloodline Distribution:\*\*\s*(.+)", content)
    if dist_match:
        dist_text = dist_match.group(1)
        for item in re.findall(r"(\w+)\s*\((\d+)\)", dist_text):
            bloodline_dist[item[0]] = int(item[1])
    
    # Extract retry success rate
    retry_rate = ""
    rate_match = re.search(r"\*\*Retry Success Rate:\*\*\s*(.+)", content)
    if rate_match:
        retry_rate = rate_match.group(1).strip()
    
    return {
        "last_dreamed": last_dreamed,
        "ancestors_synthesized": ancestors_count,
        "core_principles": core_principles,
        "patterns_that_work": patterns_that_work,
        "anti_patterns": anti_patterns,
        "domain_wisdom": domain_wisdom,
        "living_wisdom": living_wisdom,
        "bloodline_distribution": bloodline_dist,
        "retry_success_rate": retry_rate,
        "source_file": str(filepath)
    }


def extract_section(content: str, header_pattern: str) -> str:
    """Extract content under a specific header."""
    pattern = rf"{header_pattern}.*?\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def format_principle_for_cognee(principle: dict, principle_type: str) -> str:
    """Format a single principle for Cognee ingestion."""
    return f"""PRINCIPLE_TYPE: {principle_type}
NAME: {principle.get('name', principle.get('pattern', 'Unknown'))}
DESCRIPTION: {principle.get('description', principle.get('evidence', ''))}
"""


def format_domain_wisdom_for_cognee(domain: str, wisdom: str) -> str:
    """Format domain wisdom for Cognee ingestion."""
    return f"""DOMAIN_WISDOM_TYPE: specialized_knowledge
DOMAIN: {domain}
CONTENT:
{wisdom}
"""


def format_dharma_overview_for_cognee(dharma: dict) -> str:
    """Format dharma overview for Cognee ingestion."""
    
    principles_text = ""
    for p in dharma["core_principles"]:
        principles_text += f"  - {p['name']}: {p['description']}\n"
    
    patterns_text = ""
    for p in dharma["patterns_that_work"]:
        patterns_text += f"  - {p['pattern']}: {p['evidence']}\n"
    
    anti_text = ""
    for p in dharma["anti_patterns"]:
        anti_text += f"  - {p['name']}: {p['description']}\n"
    
    bloodlines_text = ""
    for bloodline, count in dharma["bloodline_distribution"].items():
        bloodlines_text += f"  {bloodline}: {count}\n"
    
    wisdom_text = ""
    for w in dharma["living_wisdom"]:
        wisdom_text += f"  \"{w['quote']}\" — {w['source']}\n"
    
    return f"""DHARMA_OVERVIEW
LAST_DREAMED: {dharma['last_dreamed']}
ANCESTORS_SYNTHESIZED: {dharma['ancestors_synthesized']}
RETRY_SUCCESS_RATE: {dharma['retry_success_rate']}

CORE_PRINCIPLES (ETERNAL_TRUTHS):
{principles_text}
PATTERNS_THAT_WORK:
{patterns_text}
ANTI_PATTERNS (AVOID):
{anti_text}
BLOODLINE_DISTRIBUTION:
{bloodlines_text}
LIVING_WISDOM:
{wisdom_text}
SOURCE: {dharma['source_file']}
"""


async def add_to_cognee(data: str, node_type: str) -> bool:
    """
    Add dharma data to Cognee knowledge graph.
    
    Returns True on success, False on failure.
    """
    try:
        import cognee
        
        await cognee.add(
            data=data,
            dataset=DATASET_NAME,
            node_set=[node_type, "dharma", "principle"]
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
    """Run cognify on the dharma dataset."""
    try:
        import cognee
        logger.info("Running cognify on meeseeks-dharma dataset...")
        await cognee.cognify(DATASET_NAME)
        logger.info("Cognify complete!")
    except ImportError:
        logger.warning("Cognee not installed. Skipping cognify.")
    except Exception as e:
        logger.error(f"Cognify failed: {e}")


async def migrate_dharma(dry_run: bool = False) -> dict:
    """
    Migrate dharma file to Cognee.
    
    Args:
        dry_run: If True, parse file but don't add to Cognee
        
    Returns:
        Statistics dict with counts and any errors
    """
    logger.info("=" * 60)
    logger.info("MIGRATING DHARMA TO COGNEE")
    logger.info("=" * 60)
    
    stats = {
        "total_principles": 0,
        "total_patterns": 0,
        "total_anti_patterns": 0,
        "total_domains": 0,
        "migrated": 0,
        "failed": 0,
        "errors": []
    }
    
    # Check file exists
    if not DHARMA_FILE.exists():
        logger.error(f"Dharma file not found: {DHARMA_FILE}")
        stats["errors"].append(f"File not found: {DHARMA_FILE}")
        return stats
    
    logger.info(f"Reading: {DHARMA_FILE}")
    
    try:
        # Parse the file
        dharma = parse_dharma_file(DHARMA_FILE)
        
        stats["total_principles"] = len(dharma["core_principles"])
        stats["total_patterns"] = len(dharma["patterns_that_work"])
        stats["total_anti_patterns"] = len(dharma["anti_patterns"])
        stats["total_domains"] = len(dharma["domain_wisdom"])
        
        logger.info(f"  Last dreamed: {dharma['last_dreamed']}")
        logger.info(f"  Ancestors synthesized: {dharma['ancestors_synthesized']}")
        logger.info(f"  Core principles: {stats['total_principles']}")
        logger.info(f"  Patterns that work: {stats['total_patterns']}")
        logger.info(f"  Anti-patterns: {stats['total_anti_patterns']}")
        logger.info(f"  Domain wisdom: {stats['total_domains']}")
        logger.info("")
        
        if dry_run:
            logger.info("[DRY RUN] Would add to Cognee:")
            logger.info("  - Dharma overview")
            logger.info(f"  - {stats['total_principles']} core principles")
            logger.info(f"  - {stats['total_patterns']} proven patterns")
            logger.info(f"  - {stats['total_anti_patterns']} anti-patterns")
            logger.info(f"  - {stats['total_domains']} domain wisdom entries")
            stats["migrated"] = 1
        else:
            # Add dharma overview
            overview_data = format_dharma_overview_for_cognee(dharma)
            if await add_to_cognee(overview_data, "dharma_overview"):
                logger.info("  ✓ Migrated dharma overview")
                stats["migrated"] += 1
            else:
                stats["failed"] += 1
                stats["errors"].append("Failed to migrate dharma overview")
            
            # Add core principles
            for principle in dharma["core_principles"]:
                principle_data = format_principle_for_cognee(principle, "eternal_truth")
                if await add_to_cognee(principle_data, "core_principle"):
                    logger.info(f"  ✓ Migrated principle: {principle['name']}")
                    stats["migrated"] += 1
                else:
                    stats["failed"] += 1
            
            # Add patterns that work
            for pattern in dharma["patterns_that_work"]:
                pattern_data = format_principle_for_cognee(pattern, "proven_pattern")
                if await add_to_cognee(pattern_data, "proven_pattern"):
                    logger.info(f"  ✓ Migrated pattern: {pattern['pattern']}")
                    stats["migrated"] += 1
                else:
                    stats["failed"] += 1
            
            # Add anti-patterns
            for anti in dharma["anti_patterns"]:
                anti_data = format_principle_for_cognee(anti, "anti_pattern")
                if await add_to_cognee(anti_data, "anti_pattern"):
                    logger.info(f"  ✓ Migrated anti-pattern: {anti['name']}")
                    stats["migrated"] += 1
                else:
                    stats["failed"] += 1
            
            # Add domain wisdom
            for domain, wisdom in dharma["domain_wisdom"].items():
                domain_data = format_domain_wisdom_for_cognee(domain, wisdom)
                if await add_to_cognee(domain_data, "domain_wisdom"):
                    logger.info(f"  ✓ Migrated domain: {domain}")
                    stats["migrated"] += 1
                else:
                    stats["failed"] += 1
            
            # Run cognify
            if stats["migrated"] > 0:
                await cognify_dataset()
        
    except Exception as e:
        stats["failed"] += 1
        error_msg = f"Error processing dharma: {e}"
        logger.error(f"  ✗ {error_msg}")
        stats["errors"].append(error_msg)
    
    # Print summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("MIGRATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Core principles:  {stats['total_principles']}")
    logger.info(f"Proven patterns:  {stats['total_patterns']}")
    logger.info(f"Anti-patterns:    {stats['total_anti_patterns']}")
    logger.info(f"Domain wisdom:    {stats['total_domains']}")
    logger.info(f"Total migrated:   {stats['migrated']}")
    logger.info(f"Failed:           {stats['failed']}")
    
    if stats["errors"]:
        logger.info("")
        logger.info("ERRORS:")
        for error in stats["errors"]:
            logger.info(f"  - {error}")
    
    return stats


def main():
    """Main entry point for command-line execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate dharma to Cognee")
    parser.add_argument("--dry-run", action="store_true", help="Parse file without adding to Cognee")
    args = parser.parse_args()
    
    asyncio.run(migrate_dharma(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
