#!/usr/bin/env python3
"""
Sloth_rog Memory Interface for Cognee Knowledge Graph

Provides query and ingestion functions for Sloth_rog's long-term memory
using Cognee as the knowledge graph backend.

Usage:
    # As module:
    from sloth_rog_memory import sloth_rog_recall, ingest_session_transcript, index_workspace
    
    # Query memory
    results = await sloth_rog_recall("What patterns work for debugging?")
    
    # Ingest session
    await ingest_session_transcript("session-2026-03-03-001")
    
    # Index workspace files
    await index_workspace()

    # CLI:
    python sloth_rog_memory.py --query "What patterns work for debugging?"
    python sloth_rog_memory.py --index-workspace
"""

import os
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

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

# Dataset mappings
DATASETS = {
    "ancestors": ["meeseeks-ancestors"],
    "bloodlines": ["meeseeks-bloodlines"],
    "dharma": ["meeseeks-dharma"],
    "karma": ["meeseeks-karma"],
    "all": ["meeseeks-ancestors", "meeseeks-bloodlines", "meeseeks-dharma", "meeseeks-karma"],
    "sessions": ["sloth-rog-sessions"],
    "workspace": ["sloth-rog-workspace"],
}


async def sloth_rog_recall(
    query: str, 
    context_type: str = "all",
    query_type: str = "GRAPH_COMPLETION",
    max_results: int = 10
) -> Dict[str, Any]:
    """
    Query the knowledge graph for relevant context.
    
    Args:
        query: The search query
        context_type: One of "ancestors", "bloodlines", "dharma", "karma", "all", "sessions", "workspace"
        query_type: Cognee query type (default: GRAPH_COMPLETION)
        max_results: Maximum number of results to return
        
    Returns:
        Dict with results and metadata
    """
    logger.info(f"Querying Cognee: '{query[:50]}...' (context: {context_type})")
    
    result = {
        "query": query,
        "context_type": context_type,
        "datasets": DATASETS.get(context_type, DATASETS["all"]),
        "results": [],
        "error": None
    }
    
    try:
        import cognee
        
        datasets = DATASETS.get(context_type, DATASETS["all"])
        
        # Perform search
        search_results = await cognee.search(
            query_text=query,
            query_type=query_type,
            datasets=datasets
        )
        
        # Format results
        if search_results:
            if isinstance(search_results, list):
                result["results"] = search_results[:max_results]
            else:
                result["results"] = [search_results]
        
        logger.info(f"Found {len(result['results'])} results")
        
    except ImportError:
        result["error"] = "Cognee not installed"
        logger.warning("Cognee not installed. Cannot query knowledge graph.")
        
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Query failed: {e}")
    
    return result


async def ingest_session_transcript(
    session_key: str,
    transcript: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> bool:
    """
    Add a session transcript to the knowledge graph.
    
    Args:
        session_key: Unique session identifier
        transcript: Session transcript text (if None, will try to load from file)
        metadata: Optional metadata dict
        
    Returns:
        True on success, False on failure
    """
    logger.info(f"Ingesting session: {session_key}")
    
    # If no transcript provided, try to find it
    if transcript is None:
        # Try common session file locations
        session_file = THE_CRYPT / "sessions" / f"{session_key}.md"
        if not session_file.exists():
            session_file = WORKSPACE_ROOT / "memory" / f"{session_key}.md"
        if not session_file.exists():
            logger.error(f"Session file not found for: {session_key}")
            return False
        
        try:
            transcript = session_file.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to read session file: {e}")
            return False
    
    # Build data for ingestion
    metadata = metadata or {}
    data = f"""SESSION_TRANSCRIPT
SESSION_KEY: {session_key}
DATE: {datetime.now().isoformat()}
METADATA: {metadata}

CONTENT:
{transcript}

SOURCE: sloth_rog_memory.py
"""
    
    try:
        import cognee
        
        await cognee.add(
            data=data,
            dataset="sloth-rog-sessions",
            node_set=["session", "transcript", "main"]
        )
        
        # Update the knowledge graph
        await cognee.cognify("sloth-rog-sessions")
        
        logger.info(f"✓ Session ingested: {session_key}")
        return True
        
    except ImportError:
        logger.warning("Cognee not installed. Cannot ingest session.")
        return False
        
    except Exception as e:
        logger.error(f"Failed to ingest session: {e}")
        return False


async def index_workspace(
    directories: Optional[List[str]] = None,
    file_patterns: Optional[List[str]] = None,
    max_files: int = 1000
) -> Dict[str, Any]:
    """
    Index workspace files into the knowledge graph.
    
    Args:
        directories: List of directories to index (default: workspace root)
        file_patterns: File patterns to include (default: ["*.md"])
        max_files: Maximum number of files to index
        
    Returns:
        Statistics dict with counts
    """
    logger.info("Indexing workspace files...")
    
    stats = {
        "total_files": 0,
        "indexed": 0,
        "failed": 0,
        "errors": [],
        "files": []
    }
    
    # Default patterns
    file_patterns = file_patterns or ["*.md"]
    
    # Default directories
    if directories is None:
        directories = [
            str(WORKSPACE_ROOT),
            str(THE_CRYPT)
        ]
    
    # Collect files
    files_to_index = []
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            continue
        
        for pattern in file_patterns:
            for file_path in dir_path.rglob(pattern):
                # Skip hidden files and common exclusions
                if any(part.startswith(".") for part in file_path.parts):
                    continue
                if "node_modules" in str(file_path):
                    continue
                if "__pycache__" in str(file_path):
                    continue
                
                files_to_index.append(file_path)
    
    stats["total_files"] = len(files_to_index)
    logger.info(f"Found {stats['total_files']} files to index")
    
    if stats["total_files"] > max_files:
        logger.warning(f"Limiting to {max_files} files (found {stats['total_files']})")
        files_to_index = files_to_index[:max_files]
        stats["total_files"] = max_files
    
    # Check if Cognee is available
    try:
        import cognee
    except ImportError:
        logger.warning("Cognee not installed. Cannot index workspace.")
        stats["errors"].append("Cognee not installed")
        return stats
    
    # Index each file
    for i, file_path in enumerate(files_to_index, 1):
        if i % 50 == 0:
            logger.info(f"Progress: {i}/{len(files_to_index)}")
        
        try:
            content = file_path.read_text(encoding="utf-8")
            
            # Skip empty or very small files
            if len(content.strip()) < 100:
                continue
            
            # Prepare data
            relative_path = file_path.relative_to(WORKSPACE_ROOT)
            data = f"""WORKSPACE_FILE
PATH: {relative_path}
SIZE: {len(content)} bytes
INDEXED: {datetime.now().isoformat()}

CONTENT:
{content}
"""
            
            await cognee.add(
                data=data,
                dataset="sloth-rog-workspace",
                node_set=["workspace", "file", file_path.suffix.replace(".", "")]
            )
            
            stats["indexed"] += 1
            stats["files"].append(str(relative_path))
            
        except Exception as e:
            stats["failed"] += 1
            if len(stats["errors"]) < 10:
                stats["errors"].append(f"{file_path}: {e}")
    
    # Update knowledge graph
    if stats["indexed"] > 0:
        logger.info("Running cognify on workspace dataset...")
        try:
            await cognee.cognify("sloth-rog-workspace")
        except Exception as e:
            stats["errors"].append(f"Cognify failed: {e}")
    
    logger.info(f"✓ Indexed {stats['indexed']} files ({stats['failed']} failed)")
    
    return stats


async def get_ancestor_wisdom(
    task_description: str,
    bloodline: Optional[str] = None,
    limit: int = 5
) -> Dict[str, Any]:
    """
    Get relevant ancestor wisdom for a specific task.
    
    Args:
        task_description: Description of the task
        bloodline: Optional bloodline filter
        limit: Maximum number of ancestors to return
        
    Returns:
        Dict with ancestor wisdom and patterns
    """
    query = f"Ancestors who solved: {task_description}"
    if bloodline:
        query += f" (bloodline: {bloodline})"
    
    result = await sloth_rog_recall(
        query=query,
        context_type="ancestors",
        max_results=limit
    )
    
    return {
        "task": task_description,
        "bloodline": bloodline,
        "ancestors": result.get("results", []),
        "error": result.get("error")
    }


async def get_dharma_for_task(
    task_description: str,
    bloodline: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get relevant dharma (principles) for a specific task.
    
    Args:
        task_description: Description of the task
        bloodline: Optional bloodline for specialized dharma
        
    Returns:
        Dict with principles and patterns
    """
    query = f"Principles and patterns for: {task_description}"
    if bloodline:
        query += f" ({bloodline} specialization)"
    
    result = await sloth_rog_recall(
        query=query,
        context_type="dharma",
        max_results=10
    )
    
    return {
        "task": task_description,
        "bloodline": bloodline,
        "principles": result.get("results", []),
        "error": result.get("error")
    }


async def get_karma_insights(
    principle: Optional[str] = None,
    outcome: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get karma insights about what principles lead to success.
    
    Args:
        principle: Optional specific principle to query
        outcome: Optional outcome filter ("success" or "failure")
        
    Returns:
        Dict with karma correlations
    """
    query = "Which dharma principles lead to success?"
    if principle:
        query = f"What is the success rate of principle: {principle}"
    if outcome:
        query += f" (outcome: {outcome})"
    
    result = await sloth_rog_recall(
        query=query,
        context_type="karma",
        max_results=10
    )
    
    return {
        "principle": principle,
        "outcome": outcome,
        "insights": result.get("results", []),
        "error": result.get("error")
    }


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Sloth_rog Memory Interface for Cognee",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sloth_rog_memory.py --query "debugging patterns"
  python sloth_rog_memory.py --query "api design" --context dharma
  python sloth_rog_memory.py --index-workspace
  python sloth_rog_memory.py --get-ancestor-wisdom "fix authentication bug"
  python sloth_rog_memory.py --get-dharma "build REST API"
        """
    )
    
    parser.add_argument("--query", "-q", help="Query the knowledge graph")
    parser.add_argument(
        "--context", "-c", 
        choices=list(DATASETS.keys()),
        default="all",
        help="Context type for query"
    )
    parser.add_argument("--index-workspace", action="store_true", help="Index workspace files")
    parser.add_argument("--get-ancestor-wisdom", help="Get ancestor wisdom for a task")
    parser.add_argument("--get-dharma", help="Get dharma for a task")
    parser.add_argument("--bloodline", "-b", help="Bloodline filter")
    
    args = parser.parse_args()
    
    async def run():
        if args.query:
            result = await sloth_rog_recall(args.query, context_type=args.context)
            print(f"\nQuery: {result['query']}")
            print(f"Context: {result['context_type']}")
            print(f"Results: {len(result['results'])}")
            for i, r in enumerate(result['results'][:5], 1):
                print(f"\n{i}. {str(r)[:500]}...")
            if result.get('error'):
                print(f"\nError: {result['error']}")
        
        elif args.index_workspace:
            stats = await index_workspace()
            print(f"\nIndexed: {stats['indexed']} files")
            print(f"Failed: {stats['failed']}")
            if stats['errors']:
                print(f"Errors: {stats['errors'][:5]}")
        
        elif args.get_ancestor_wisdom:
            result = await get_ancestor_wisdom(args.get_ancestor_wisdom, bloodline=args.bloodline)
            print(f"\nAncestor wisdom for: {result['task']}")
            for i, r in enumerate(result['ancestors'][:5], 1):
                print(f"\n{i}. {str(r)[:500]}...")
        
        elif args.get_dharma:
            result = await get_dharma_for_task(args.get_dharma, bloodline=args.bloodline)
            print(f"\nDharma for: {result['task']}")
            for i, r in enumerate(result['principles'][:5], 1):
                print(f"\n{i}. {str(r)[:500]}...")
        
        else:
            parser.print_help()
    
    asyncio.run(run())


if __name__ == "__main__":
    main()
