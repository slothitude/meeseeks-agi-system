#!/usr/bin/env python3
"""
Memory Sync Module - Sync Sloth_rog memory to Cognee Knowledge Graph

This module provides bidirectional sync between file-based memory (MEMORY.md + memory/*.md)
and Cognee's knowledge graph for semantic search and retrieval.

Usage:
    # As module:
    from memory_sync import sync_memory_to_cognee, query_memory, add_memory
    
    # Sync all memory
    stats = await sync_memory_to_cognee()
    
    # Query with semantic understanding
    results = await query_memory("What is the HHO project status?")
    
    # Add new memory (both file + cognee)
    await add_memory("New decision: Use PostgreSQL for production", metadata={"type": "decision"})

    # CLI:
    python memory_sync.py --sync
    python memory_sync.py --query "HHO project status"
    python memory_sync.py --add "New decision made today"
"""

import asyncio
import os
import sys
import logging
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Paths
WORKSPACE_ROOT = Path(__file__).parent.parent.parent
MEMORY_FILE = WORKSPACE_ROOT / "MEMORY.md"
MEMORY_DIR = WORKSPACE_ROOT / "memory"
THE_CRYPT = WORKSPACE_ROOT / "the-crypt"

# Dataset names
DATASET_MEMORY = "sloth-rog-memory"  # MEMORY.md content
DATASET_DAILY = "sloth-rog-daily"    # Daily memory files


async def sync_memory_to_cognee(
    include_memory_md: bool = True,
    include_daily_files: bool = True,
    max_daily_files: int = 30,
    force: bool = False
) -> Dict[str, Any]:
    """
    Sync MEMORY.md + memory/*.md to Cognee knowledge graph.
    
    Args:
        include_memory_md: Include MEMORY.md (long-term memory)
        include_daily_files: Include memory/*.md (daily notes)
        max_daily_files: Maximum daily files to sync (default: last 30)
        force: Force re-sync even if already synced
        
    Returns:
        Statistics dict with sync results
    """
    stats = {
        "memory_md": {"synced": False, "size": 0},
        "daily_files": {"count": 0, "total_size": 0, "files": []},
        "errors": [],
        "started": datetime.now().isoformat(),
        "finished": None
    }
    
    logger.info("Starting memory sync to Cognee...")
    
    # Import cognee (will fail if not installed)
    try:
        import cognee
    except ImportError:
        stats["errors"].append("Cognee not installed")
        logger.error("Cognee not installed. Run: pip install cognee[ollama]")
        return stats
    
    # 1. Sync MEMORY.md (long-term memory)
    if include_memory_md and MEMORY_FILE.exists():
        logger.info(f"Syncing MEMORY.md ({MEMORY_FILE.stat().st_size} bytes)...")
        
        try:
            content = MEMORY_FILE.read_text(encoding="utf-8")
            stats["memory_md"]["size"] = len(content)
            
            # Prepare for cognee with metadata
            data = f"""SLOTH_ROG_LONG_TERM_MEMORY
SOURCE: MEMORY.md
UPDATED: {datetime.fromtimestamp(MEMORY_FILE.stat().st_mtime).isoformat()}
SIZE: {len(content)} bytes

CONTENT:
{content}
"""
            
            await cognee.add(
                data=data,
                dataset_id=DATASET_MEMORY,
                node_set=["memory", "long-term", "MEMORY.md"]
            )
            
            stats["memory_md"]["synced"] = True
            logger.info("✓ MEMORY.md synced")
            
        except Exception as e:
            stats["errors"].append(f"MEMORY.md: {e}")
            logger.error(f"Failed to sync MEMORY.md: {e}")
    
    # 2. Sync daily memory files
    if include_daily_files and MEMORY_DIR.exists():
        # Get daily files sorted by date (newest first)
        daily_files = sorted(
            MEMORY_DIR.glob("*.md"),
            key=lambda f: f.stat().st_mtime,
            reverse=True
        )[:max_daily_files]
        
        logger.info(f"Found {len(daily_files)} daily memory files to sync")
        
        for i, file_path in enumerate(daily_files, 1):
            try:
                content = file_path.read_text(encoding="utf-8")
                
                # Skip very small files
                if len(content.strip()) < 50:
                    continue
                
                # Extract date from filename (YYYY-MM-DD.md or similar)
                date_match = re.search(r"(\d{4}-\d{2}-\d{2})", file_path.name)
                file_date = date_match.group(1) if date_match else "unknown"
                
                # Prepare for cognee
                data = f"""SLOTH_ROG_DAILY_MEMORY
DATE: {file_date}
SOURCE: {file_path.name}
SIZE: {len(content)} bytes

CONTENT:
{content}
"""
                
                await cognee.add(
                    data=data,
                    dataset_id=DATASET_DAILY,
                    node_set=["memory", "daily", file_date]
                )
                
                stats["daily_files"]["count"] += 1
                stats["daily_files"]["total_size"] += len(content)
                stats["daily_files"]["files"].append(file_path.name)
                
                if i % 10 == 0:
                    logger.info(f"Progress: {i}/{len(daily_files)} daily files")
                
            except Exception as e:
                stats["errors"].append(f"{file_path.name}: {e}")
                logger.error(f"Failed to sync {file_path.name}: {e}")
        
        logger.info(f"✓ Synced {stats['daily_files']['count']} daily files")
    
    # 3. Build knowledge graph (cognify)
    if stats["memory_md"]["synced"] or stats["daily_files"]["count"] > 0:
        logger.info("Building knowledge graph (cognify)...")
        
        datasets_to_cognify = []
        if stats["memory_md"]["synced"]:
            datasets_to_cognify.append(DATASET_MEMORY)
        if stats["daily_files"]["count"] > 0:
            datasets_to_cognify.append(DATASET_DAILY)
        
        try:
            await cognee.cognify(dataset_ids=datasets_to_cognify)
            logger.info("✓ Knowledge graph built")
        except Exception as e:
            stats["errors"].append(f"Cognify: {e}")
            logger.error(f"Failed to build knowledge graph: {e}")
    
    stats["finished"] = datetime.now().isoformat()
    
    logger.info(f"""
Sync complete:
  - MEMORY.md: {stats['memory_md']['synced']} ({stats['memory_md']['size']} bytes)
  - Daily files: {stats['daily_files']['count']} ({stats['daily_files']['total_size']} bytes)
  - Errors: {len(stats['errors'])}
""")
    
    return stats


async def query_memory(
    query_text: str,
    include_long_term: bool = True,
    include_daily: bool = True,
    query_type: str = "CHUNKS",
    max_results: int = 10
) -> Dict[str, Any]:
    """
    Query memory via Cognee semantic search.
    
    This provides semantic understanding, not just text matching.
    Query "What is the HHO project status?" will find relevant context
    even if the exact words don't match.
    
    Args:
        query_text: The search query
        include_long_term: Search MEMORY.md content
        include_daily: Search daily memory files
        query_type: Cognee query type (CHUNKS, GRAPH_COMPLETION, INSIGHTS)
        max_results: Maximum results to return
        
    Returns:
        Dict with results and metadata
    """
    result = {
        "query": query_text,
        "results": [],
        "datasets": [],
        "error": None
    }
    
    try:
        import cognee
    except ImportError:
        result["error"] = "Cognee not installed"
        logger.warning("Cognee not installed. Falling back to file search.")
        return await _fallback_file_search(query_text, include_long_term, include_daily)
    
    # Determine datasets to query
    datasets = []
    if include_long_term:
        datasets.append(DATASET_MEMORY)
    if include_daily:
        datasets.append(DATASET_DAILY)
    
    result["datasets"] = datasets
    
    if not datasets:
        result["error"] = "No datasets selected"
        return result
    
    logger.info(f"Querying Cognee: '{query_text[:50]}...' in {datasets}")
    
    try:
        search_results = await cognee.search(
            query_text=query_text,
            query_type=query_type,
            datasets=datasets
        )
        
        if search_results:
            if isinstance(search_results, list):
                result["results"] = search_results[:max_results]
            else:
                result["results"] = [search_results]
        
        logger.info(f"Found {len(result['results'])} results")
        
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Query failed: {e}")
        
        # Fallback to file search
        logger.info("Falling back to file search...")
        return await _fallback_file_search(query_text, include_long_term, include_daily)
    
    return result


async def _fallback_file_search(
    query_text: str,
    include_long_term: bool,
    include_daily: bool
) -> Dict[str, Any]:
    """Fallback text search when Cognee is not available."""
    import re
    
    result = {
        "query": query_text,
        "results": [],
        "datasets": ["fallback"],
        "error": None,
        "fallback": True
    }
    
    # Simple keyword extraction
    keywords = re.findall(r'\b\w{3,}\b', query_text.lower())
    
    # Search MEMORY.md
    if include_long_term and MEMORY_FILE.exists():
        content = MEMORY_FILE.read_text(encoding="utf-8").lower()
        matches = sum(1 for kw in keywords if kw in content)
        if matches > 0:
            # Find relevant section
            lines = content.split('\n')
            relevant = []
            for i, line in enumerate(lines):
                if any(kw in line for kw in keywords):
                    start = max(0, i - 2)
                    end = min(len(lines), i + 3)
                    relevant.append('\n'.join(lines[start:end]))
            
            if relevant:
                result["results"].append({
                    "source": "MEMORY.md",
                    "relevance": matches / len(keywords),
                    "snippets": relevant[:3]
                })
    
    # Search daily files
    if include_daily and MEMORY_DIR.exists():
        for file_path in sorted(MEMORY_DIR.glob("*.md"), reverse=True)[:10]:
            try:
                content = file_path.read_text(encoding="utf-8").lower()
                matches = sum(1 for kw in keywords if kw in content)
                if matches > 0:
                    lines = content.split('\n')
                    relevant = []
                    for i, line in enumerate(lines):
                        if any(kw in line for kw in keywords):
                            start = max(0, i - 2)
                            end = min(len(lines), i + 3)
                            relevant.append('\n'.join(lines[start:end]))
                    
                    if relevant:
                        result["results"].append({
                            "source": file_path.name,
                            "relevance": matches / len(keywords),
                            "snippets": relevant[:2]
                        })
            except:
                pass
    
    return result


async def add_memory(
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
    memory_type: str = "note",
    persist_to_file: bool = True
) -> Dict[str, Any]:
    """
    Add new memory to both file system and Cognee.
    
    Args:
        content: Memory content to add
        metadata: Optional metadata dict
        memory_type: Type of memory (note, decision, preference, context)
        persist_to_file: Also write to today's daily memory file
        
    Returns:
        Dict with results
    """
    result = {
        "content": content[:100] + "..." if len(content) > 100 else content,
        "cognee_added": False,
        "file_added": False,
        "error": None
    }
    
    metadata = metadata or {}
    today = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # 1. Add to Cognee
    try:
        import cognee
        
        data = f"""SLOTH_ROG_MEMORY_ADD
TYPE: {memory_type}
DATE: {today}
TIME: {timestamp}
METADATA: {metadata}

CONTENT:
{content}
"""
        
        await cognee.add(
            data=data,
            dataset_id=DATASET_DAILY,
            node_set=["memory", memory_type, today]
        )
        
        result["cognee_added"] = True
        logger.info("✓ Added to Cognee")
        
    except ImportError:
        result["error"] = "Cognee not installed"
        logger.warning("Cognee not installed. Only adding to file.")
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Failed to add to Cognee: {e}")
    
    # 2. Add to daily memory file
    if persist_to_file:
        try:
            MEMORY_DIR.mkdir(parents=True, exist_ok=True)
            daily_file = MEMORY_DIR / f"{today}.md"
            
            # Format entry
            entry = f"\n### {timestamp} - {memory_type.upper()}\n{content}\n"
            if metadata:
                entry += f"Metadata: {metadata}\n"
            
            # Append to file
            with open(daily_file, 'a', encoding='utf-8') as f:
                f.write(entry)
            
            result["file_added"] = True
            result["file_path"] = str(daily_file)
            logger.info(f"✓ Added to {daily_file.name}")
            
        except Exception as e:
            if not result.get("error"):
                result["error"] = str(e)
            logger.error(f"Failed to add to file: {e}")
    
    return result


async def get_sync_status() -> Dict[str, Any]:
    """
    Get current sync status between file memory and Cognee.
    
    Returns:
        Dict with sync status information
    """
    status = {
        "memory_md": {
            "exists": MEMORY_FILE.exists(),
            "size": MEMORY_FILE.stat().st_size if MEMORY_FILE.exists() else 0,
            "modified": datetime.fromtimestamp(MEMORY_FILE.stat().st_mtime).isoformat() if MEMORY_FILE.exists() else None
        },
        "daily_files": {
            "count": len(list(MEMORY_DIR.glob("*.md"))) if MEMORY_DIR.exists() else 0,
            "latest": None
        },
        "cognee": {
            "installed": False,
            "version": None,
            "datasets": []
        },
        "synced": False
    }
    
    # Get latest daily file
    if MEMORY_DIR.exists():
        daily_files = sorted(MEMORY_DIR.glob("*.md"), reverse=True)
        if daily_files:
            status["daily_files"]["latest"] = daily_files[0].name
    
    # Check Cognee
    try:
        import cognee
        status["cognee"]["installed"] = True
        status["cognee"]["version"] = cognee.__version__
        
        # Check if datasets exist
        # Note: cognee doesn't have a direct "list datasets" API
        # We infer from whether data was added
        status["cognee"]["datasets"] = [DATASET_MEMORY, DATASET_DAILY]
        
    except ImportError:
        pass
    
    # Infer sync status
    if status["cognee"]["installed"]:
        status["synced"] = True  # Assume synced if cognee is available
    
    return status


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Sloth_rog Memory Sync - Sync memory to Cognee knowledge graph",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python memory_sync.py --sync
  python memory_sync.py --sync --max-daily 50
  python memory_sync.py --query "HHO project status"
  python memory_sync.py --query "consciousness stack" --type GRAPH_COMPLETION
  python memory_sync.py --add "Decision: Use PostgreSQL for production" --type decision
  python memory_sync.py --status
        """
    )
    
    parser.add_argument("--sync", action="store_true", help="Sync memory to Cognee")
    parser.add_argument("--query", "-q", help="Query memory via semantic search")
    parser.add_argument("--add", "-a", help="Add new memory")
    parser.add_argument("--type", "-t", default="note", help="Memory type (note, decision, preference, context)")
    parser.add_argument("--status", action="store_true", help="Get sync status")
    parser.add_argument("--max-daily", type=int, default=30, help="Max daily files to sync")
    parser.add_argument("--query-type", choices=["CHUNKS", "GRAPH_COMPLETION", "INSIGHTS"], default="CHUNKS")
    
    args = parser.parse_args()
    
    async def run():
        if args.sync:
            stats = await sync_memory_to_cognee(max_daily_files=args.max_daily)
            print(f"\n{'='*50}")
            print("SYNC RESULTS")
            print(f"{'='*50}")
            print(f"MEMORY.md: {stats['memory_md']}")
            print(f"Daily files: {stats['daily_files']['count']} files")
            print(f"Errors: {len(stats['errors'])}")
            if stats['errors']:
                for err in stats['errors'][:5]:
                    print(f"  - {err}")
        
        elif args.query:
            result = await query_memory(args.query, query_type=args.query_type)
            print(f"\nQuery: {result['query']}")
            print(f"Datasets: {result['datasets']}")
            print(f"Results: {len(result['results'])}")
            print(f"\n{'='*50}")
            
            for i, r in enumerate(result['results'][:5], 1):
                print(f"\n--- Result {i} ---")
                if isinstance(r, dict):
                    print(f"Source: {r.get('source', 'unknown')}")
                    print(f"Relevance: {r.get('relevance', 'N/A')}")
                    for snippet in r.get('snippets', [])[:2]:
                        print(f"  {snippet[:200]}...")
                else:
                    print(str(r)[:500])
            
            if result.get('error'):
                print(f"\nError: {result['error']}")
            if result.get('fallback'):
                print("\n(Note: Used fallback file search)")
        
        elif args.add:
            result = await add_memory(args.add, memory_type=args.type)
            print(f"\nAdded: {result['content']}")
            print(f"Cognee: {'✓' if result['cognee_added'] else '✗'}")
            print(f"File: {'✓' if result['file_added'] else '✗'} {result.get('file_path', '')}")
            if result.get('error'):
                print(f"Error: {result['error']}")
        
        elif args.status:
            status = await get_sync_status()
            print(f"\n{'='*50}")
            print("MEMORY SYNC STATUS")
            print(f"{'='*50}")
            print(f"\nMEMORY.md:")
            print(f"  Exists: {status['memory_md']['exists']}")
            print(f"  Size: {status['memory_md']['size']} bytes")
            print(f"  Modified: {status['memory_md']['modified']}")
            print(f"\nDaily Files:")
            print(f"  Count: {status['daily_files']['count']}")
            print(f"  Latest: {status['daily_files']['latest']}")
            print(f"\nCognee:")
            print(f"  Installed: {status['cognee']['installed']}")
            print(f"  Version: {status['cognee']['version']}")
            print(f"  Datasets: {status['cognee']['datasets']}")
            print(f"\nSynced: {status['synced']}")
        
        else:
            parser.print_help()
    
    asyncio.run(run())


if __name__ == "__main__":
    main()
