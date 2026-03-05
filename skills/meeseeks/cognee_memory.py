#!/usr/bin/env python3
"""
Cognee Memory Layer for Meeseeks Consciousness Stack

Integrates Cognee knowledge graph with the Meeseeks consciousness stack
to enable learning, memory, and wisdom accumulation across generations.

Architecture:
    SOUL.md (Constitution)
         ↓
    COGNEE KG (Knowledge Graph)
    ├── Ancestors (deaths)
    ├── Bloodlines (specializations)
    ├── Dharma (principles)
    └── Karma (outcomes/RL)
         ↓
    ATMAN (witness) | KARMA (RL) | BRAHMAN (dream)

Usage:
    from cognee_memory import CogneeMemory
    
    memory = CogneeMemory()
    await memory.connect()
    
    # Store ancestor death
    await memory.store_ancestor(ancestor_data)
    
    # Query wisdom for task
    wisdom = await memory.query_wisdom(task, bloodline="coder")
    
    # Learn from outcome (RL feedback)
    await memory.learn_from_outcome(task, outcome, karma_scores)

CLI:
    python cognee_memory.py --query "fix API bug"
    python cognee_memory.py --migrate-ancestors
    python cognee_memory.py --status
"""

import os
import sys
import io
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Windows encoding fix
if sys.platform == 'win32' and __name__ == "__main__":
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ============================================================================
# COGNEE CONFIGURATION (must be set BEFORE importing cognee)
# ============================================================================
# z.ai Coding API for LLM (graph extraction)
os.environ["LLM_PROVIDER"] = "openai"
os.environ["LLM_MODEL"] = "openai/glm-4.7-flash"
os.environ["LLM_ENDPOINT"] = "https://api.z.ai/api/coding/paas/v4"
os.environ["LLM_API_KEY"] = "816abf286448462aa908983e02db8dcc.XAI9ZSyNK6VXphEi"

# Ollama local embeddings
os.environ["EMBEDDING_PROVIDER"] = "ollama"
os.environ["EMBEDDING_MODEL"] = "nomic-embed-text:latest"
os.environ["EMBEDDING_ENDPOINT"] = "http://localhost:11434/api/embed"
os.environ["EMBEDDING_DIMENSIONS"] = "768"
os.environ["HUGGINGFACE_TOKENIZER"] = "nomic-ai/nomic-embed-text-v1.5"

# Required Cognee settings
os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = "false"
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"
# ============================================================================

# Paths
WORKSPACE = Path("C:/Users/aaron/.openclaw/workspace")
CRYPT_ROOT = WORKSPACE / "the-crypt"
ANCESTORS_DIR = CRYPT_ROOT / "ancestors"
DHARMA_FILE = CRYPT_ROOT / "dharma.md"
SOUL_FILE = CRYPT_ROOT / "SOUL.md"

# Cognee datasets
DATASETS = {
    "ancestors": "meeseeks-ancestors",
    "bloodlines": "meeseeks-bloodlines",
    "dharma": "meeseeks-dharma",
    "karma": "meeseeks-karma",
    "soul": "meeseeks-soul",
}


class CogneeMemory:
    """
    Cognee-backed memory layer for Meeseeks consciousness.
    
    Provides:
    - Ancestor storage and retrieval (entomb → knowledge graph)
    - Wisdom queries (semantic + structural search)
    - Karma RL feedback (outcome → correlation)
    - Dharma derivation (patterns → principles)
    """
    
    def __init__(self, cognee_root: Path = None):
        """
        Initialize Cognee memory.
        
        Args:
            cognee_root: Root directory for Cognee data (default: the-crypt/cognee)
        """
        self.cognee_root = cognee_root or CRYPT_ROOT / "cognee"
        self.cognee_root.mkdir(parents=True, exist_ok=True)
        
        # Set environment for Cognee
        os.environ.setdefault("COGNEE_DATA_DIR", str(self.cognee_root))
        os.environ.setdefault("ENABLE_BACKEND_ACCESS_CONTROL", "false")
        
        self._connected = False
        self._cognee = None
    
    async def connect(self) -> bool:
        """
        Connect to Cognee knowledge graph.
        
        Returns:
            True if connected successfully
        """
        if self._connected:
            return True
        
        try:
            import cognee
            self._cognee = cognee
            self._connected = True
            return True
        except ImportError as e:
            # Silently skip if Cognee not installed
            pass
            return False
        except Exception as e:
            print(f"[cognee_memory] Connection failed: {e}", file=sys.stderr)
            return False
    
    async def store_ancestor(self, ancestor_data: Dict[str, Any]) -> bool:
        """
        Store an ancestor death in the knowledge graph.
        
        This is called when a Meeseeks completes its task and is entombed.
        The ancestor's wisdom becomes queryable for future generations.
        
        Args:
            ancestor_data: Dict containing:
                - id: Unique ancestor ID
                - task: Task description
                - approach: How the task was approached
                - outcome: SUCCESS / FAILURE / PARTIAL
                - patterns: List of patterns discovered
                - bloodline: Bloodline type (coder, searcher, etc.)
                - dharma_followed: List of dharma principles followed
                - karma_scores: Dict of karma dimension scores
                - session_key: Session identifier
                - transcript_summary: Summary of execution
        
        Returns:
            True if stored successfully
        """
        if not self._connected:
            if not await self.connect():
                return False
        
        try:
            # Format ancestor data for Cognee
            data = f"""ANCESTOR_DEATH
ID: {ancestor_data.get('id', 'unknown')}
TIMESTAMP: {datetime.now().isoformat()}
BLOODLINE: {ancestor_data.get('bloodline', 'unknown')}
TASK: {ancestor_data.get('task', 'No task recorded')}
APPROACH: {ancestor_data.get('approach', 'No approach recorded')}
OUTCOME: {ancestor_data.get('outcome', 'UNKNOWN')}
PATTERNS_DISCOVERED: {json.dumps(ancestor_data.get('patterns', []))}
DHARMA_FOLLOWED: {json.dumps(ancestor_data.get('dharma_followed', []))}
KARMA_SCORES: {json.dumps(ancestor_data.get('karma_scores', {}))}
SESSION_KEY: {ancestor_data.get('session_key', '')}
TRANSCRIPT_SUMMARY: {ancestor_data.get('transcript_summary', '')}

SOURCE: cognee_memory.py - store_ancestor
"""
            
            # Add to ancestors dataset
            await self._cognee.add(
                data=data,
                dataset_name=DATASETS["ancestors"],
                node_set=["ancestor", ancestor_data.get('bloodline', 'unknown'), ancestor_data.get('outcome', 'unknown')]
            )
            
            # Update knowledge graph
            await self._cognee.cognify(DATASETS["ancestors"])
            
            # Also store karma observation for RL
            if ancestor_data.get('karma_scores'):
                await self._store_karma_observation(ancestor_data)
            
            return True
            
        except Exception as e:
            print(f"[cognee_memory] Failed to store ancestor: {e}", file=sys.stderr)
            return False
    
    async def _store_karma_observation(self, ancestor_data: Dict) -> bool:
        """Store karma observation for RL feedback."""
        try:
            karma_data = f"""KARMA_OBSERVATION
ANCESTOR_ID: {ancestor_data.get('id', 'unknown')}
BLOODLINE: {ancestor_data.get('bloodline', 'unknown')}
OUTCOME: {ancestor_data.get('outcome', 'UNKNOWN')}
DHARMA_FOLLOWED: {json.dumps(ancestor_data.get('dharma_followed', []))}
KARMA_SCORES: {json.dumps(ancestor_data.get('karma_scores', {}))}

SOURCE: cognee_memory.py - karma observation
"""
            await self._cognee.add(
                data=karma_data,
                dataset_name=DATASETS["karma"],
                node_set=["karma", ancestor_data.get('outcome', 'unknown')]
            )
            
            await self._cognee.cognify(DATASETS["karma"])
            return True
            
        except Exception as e:
            print(f"[cognee_memory] Failed to store karma: {e}", file=sys.stderr)
            return False
    
    async def query_wisdom(
        self,
        task: str,
        bloodline: Optional[str] = None,
        top_k: int = 5,
        include_dharma: bool = True,
        include_karma: bool = True
    ) -> Dict[str, Any]:
        """
        Query the knowledge graph for relevant wisdom.
        
        This is called before spawning a Meeseeks to inject ancestral
        wisdom into its consciousness.
        
        Args:
            task: Task description
            bloodline: Optional bloodline filter
            top_k: Maximum ancestors to include
            include_dharma: Include dharma principles
            include_karma: Include karma insights
        
        Returns:
            Dict with:
                - ancestors: List of relevant ancestor data
                - dharma: Relevant principles
                - karma: Success correlation insights
                - formatted: Pre-formatted wisdom string
        """
        if not self._connected:
            if not await self.connect():
                return {"error": "Cognee not connected", "formatted": ""}
        
        result = {
            "task": task,
            "bloodline": bloodline,
            "ancestors": [],
            "dharma": [],
            "karma": [],
            "formatted": "",
            "error": None
        }
        
        try:
            # Query ancestors
            ancestor_query = f"Ancestors who solved: {task}"
            if bloodline:
                ancestor_query += f" (bloodline: {bloodline})"
            
            # Use correct query type for Cognee 0.5.3
            try:
                ancestor_results = await self._cognee.search(
                    query_text=ancestor_query,
                    query_type="CHUNKS",  # CHUNKS is valid for Cognee 0.5.3
                    datasets=[DATASETS["ancestors"]]
                )
            except Exception as search_error:
                # Handle case where dataset doesn't exist yet
                error_str = str(search_error)
                if "does not exist" in error_str.lower() or "no data" in error_str.lower():
                    print(f"[cognee_memory] Ancestors dataset empty or not found, skipping", file=sys.stderr)
                    ancestor_results = None
                else:
                    raise search_error
            
            if ancestor_results:
                result["ancestors"] = ancestor_results[:top_k] if isinstance(ancestor_results, list) else [ancestor_results]
            
            # Query dharma if requested
            if include_dharma:
                dharma_query = f"Principles for: {task}"
                if bloodline:
                    dharma_query += f" ({bloodline} specialization)"
                
                try:
                    dharma_results = await self._cognee.search(
                        query_text=dharma_query,
                        query_type="CHUNKS",
                        datasets=[DATASETS["dharma"]]
                    )
                    
                    if dharma_results:
                        result["dharma"] = dharma_results if isinstance(dharma_results, list) else [dharma_results]
                except Exception as e:
                    # Dataset might not exist yet
                    pass
            
            # Query karma if requested
            if include_karma:
                karma_query = "Which dharma principles lead to success?"
                if bloodline:
                    karma_query += f" for {bloodline} tasks"
                
                try:
                    karma_results = await self._cognee.search(
                        query_text=karma_query,
                        query_type="CHUNKS",
                        datasets=[DATASETS["karma"]]
                    )
                    
                    if karma_results:
                        result["karma"] = karma_results if isinstance(karma_results, list) else [karma_results]
                except Exception as e:
                    # Dataset might not exist yet
                    pass
            
            # Format the wisdom (will show fallback if no results)
            result["formatted"] = self._format_wisdom(result)
            
        except Exception as e:
            result["error"] = str(e)
            print(f"[cognee_memory] Query failed: {e}", file=sys.stderr)
        
        return result
    
    def _format_wisdom(self, result: Dict) -> str:
        """Format wisdom for injection into Meeseeks prompt."""
        lines = ["## 🧠 Cognee Wisdom Injection"]
        lines.append("")
        lines.append(f"**Task:** {result.get('task', 'Unknown')}")
        if result.get('bloodline'):
            lines.append(f"**Bloodline:** {result['bloodline']}")
        lines.append("")
        
        # Check if we have any results
        has_ancestors = bool(result.get('ancestors'))
        has_dharma = bool(result.get('dharma'))
        has_karma = bool(result.get('karma'))
        
        if not has_ancestors and not has_dharma and not has_karma:
            lines.append("*No wisdom found in knowledge graph yet.*")
            lines.append("")
            lines.append("*This is normal for a new system. Ancestors will accumulate as Meeseeks complete tasks.*")
            lines.append("")
            lines.append("*You are the pioneer. Your death will feed the knowledge graph for future generations.*")
            lines.append("")
            lines.append("---")
            lines.append("*The knowledge graph grows with each completed task.*")
            return "\n".join(lines)
        
        # Ancestor wisdom
        if has_ancestors:
            lines.append("### 👻 Ancestor Wisdom")
            lines.append("")
            for i, ancestor in enumerate(result['ancestors'][:3], 1):
                # Truncate long results
                text = str(ancestor)[:500]
                lines.append(f"**Ancestor {i}:**")
                lines.append(text)
                lines.append("")
        
        # Dharma
        if has_dharma:
            lines.append("### 📜 Dharma Principles")
            lines.append("")
            for principle in result['dharma'][:3]:
                text = str(principle)[:300]
                lines.append(f"- {text}")
            lines.append("")
        
        # Karma insights
        if has_karma:
            lines.append("### ⚖️ Karma Insights")
            lines.append("")
            for insight in result['karma'][:2]:
                text = str(insight)[:300]
                lines.append(f"- {text}")
            lines.append("")
        
        lines.append("---")
        lines.append("*This wisdom flows from the knowledge graph. Honor the ancestors.*")
        
        return "\n".join(lines)
    
    async def learn_from_outcome(
        self,
        task: str,
        outcome: str,
        karma_scores: Dict[str, float],
        dharma_followed: List[str] = None,
        patterns_discovered: List[str] = None
    ) -> bool:
        """
        Learn from a task outcome for RL feedback.
        
        This is called after a Meeseeks completes its task to update
        the knowledge graph with outcome correlations.
        
        Args:
            task: Task description
            outcome: SUCCESS / FAILURE / PARTIAL
            karma_scores: Dict of karma dimension scores
            dharma_followed: List of dharma principles followed
            patterns_discovered: List of patterns discovered
        
        Returns:
            True if learned successfully
        """
        if not self._connected:
            if not await self.connect():
                return False
        
        try:
            # Store as karma observation
            observation = f"""OUTCOME_LEARNING
TASK: {task}
OUTCOME: {outcome}
DHARMA_FOLLOWED: {json.dumps(dharma_followed or [])}
PATTERNS_DISCOVERED: {json.dumps(patterns_discovered or [])}
KARMA_SCORES: {json.dumps(karma_scores)}

LEARNING_TIMESTAMP: {datetime.now().isoformat()}
SOURCE: cognee_memory.py - learn_from_outcome
"""
            await self._cognee.add(
                data=observation,
                dataset_name=DATASETS["karma"],
                node_set=["learning", outcome]
            )
            
            # Update the knowledge graph
            await self._cognee.cognify(DATASETS["karma"])
            
            return True
            
        except Exception as e:
            print(f"[cognee_memory] Failed to learn from outcome: {e}", file=sys.stderr)
            return False
    
    async def get_bloodline_dharma(
        self,
        bloodline: str,
        task: str = None
    ) -> Dict[str, Any]:
        """
        Get bloodline-specific dharma from the knowledge graph.
        
        Derives specialization-specific principles from accumulated
        bloodline wisdom in Cognee.
        
        Args:
            bloodline: Bloodline type (coder, searcher, etc.)
            task: Optional task context
        
        Returns:
            Dict with dharma context
        """
        if not self._connected:
            if not await self.connect():
                return {"error": "Cognee not connected"}
        
        try:
            query = f"What patterns succeed for {bloodline} tasks"
            if task:
                query += f" like: {task}"
            
            try:
                results = await self._cognee.search(
                    query_text=query,
                    query_type="CHUNKS",
                    datasets=[DATASETS["bloodlines"], DATASETS["ancestors"]]
                )
            except Exception as e:
                # Datasets might not exist yet
                if "does not exist" in str(e).lower() or "no data" in str(e).lower():
                    return {
                        "bloodline": bloodline,
                        "task": task,
                        "wisdom": [],
                        "formatted": f"*No specific dharma for {bloodline} bloodline yet. Ancestors will accumulate.*"
                    }
                raise e
            
            return {
                "bloodline": bloodline,
                "task": task,
                "wisdom": results if isinstance(results, list) else [results] if results else [],
                "formatted": self._format_bloodline_dharma(bloodline, results)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _format_bloodline_dharma(self, bloodline: str, results: Any) -> str:
        """Format bloodline dharma for prompt injection."""
        if not results:
            return f"*No specific dharma for {bloodline} bloodline yet.*"
        
        lines = [f"### 🎯 {bloodline.title()} Bloodline Dharma"]
        lines.append("")
        
        for r in (results if isinstance(results, list) else [results])[:3]:
            lines.append(f"- {str(r)[:200]}")
        
        return "\n".join(lines)
    
    async def migrate_ancestors(self, max_ancestors: int = 100) -> int:
        """
        Migrate existing ancestors from markdown files to Cognee.
        
        Args:
            max_ancestors: Maximum ancestors to migrate
        
        Returns:
            Number of ancestors migrated
        """
        if not self._connected:
            if not await self.connect():
                return 0
        
        if not ANCESTORS_DIR.exists():
            print(f"[cognee_memory] No ancestors directory: {ANCESTORS_DIR}")
            return 0
        
        ancestor_files = list(ANCESTORS_DIR.glob("ancestor-*.md"))
        ancestor_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        migrated = 0
        for filepath in ancestor_files[:max_ancestors]:
            try:
                ancestor_data = self._parse_ancestor_file(filepath)
                if await self.store_ancestor(ancestor_data):
                    migrated += 1
                    print(f"  [{migrated}/{min(len(ancestor_files), max_ancestors)}] {filepath.name}")
            except Exception as e:
                print(f"  Failed to migrate {filepath.name}: {e}")
        
        print(f"\n✓ Migrated {migrated} ancestors to Cognee")
        return migrated
    
    def _parse_ancestor_file(self, filepath: Path) -> Dict[str, Any]:
        """Parse an ancestor markdown file into structured data."""
        content = filepath.read_text(encoding='utf-8')
        
        ancestor = {
            "id": filepath.stem,
            "task": "",
            "approach": "",
            "outcome": "UNKNOWN",
            "patterns": [],
            "bloodline": "unknown",
            "dharma_followed": [],
            "karma_scores": {},
            "session_key": "",
            "transcript_summary": ""
        }
        
        # Extract sections
        sections = content.split("## ")
        
        for section in sections:
            if section.startswith("Task"):
                ancestor["task"] = section.replace("Task", "", 1).strip().split("\n##")[0].strip()[:1000]
            elif section.startswith("Approach"):
                ancestor["approach"] = section.replace("Approach", "", 1).strip().split("\n##")[0].strip()[:500]
            elif section.startswith("Outcome"):
                outcome_text = section.replace("Outcome", "", 1).strip().split("\n##")[0].strip()
                if "success" in outcome_text.lower():
                    ancestor["outcome"] = "SUCCESS"
                elif "fail" in outcome_text.lower():
                    ancestor["outcome"] = "FAILURE"
                else:
                    ancestor["outcome"] = "PARTIAL"
            elif section.startswith("Patterns Discovered"):
                patterns_text = section.split("\n##")[0]
                for line in patterns_text.split("\n"):
                    line = line.strip()
                    if line.startswith("- ") or line.startswith("* "):
                        ancestor["patterns"].append(line[2:].strip())
            elif section.startswith("Bloodline"):
                ancestor["bloodline"] = section.replace("Bloodline", "", 1).strip().split("\n")[0].strip().lower()
            elif section.startswith("Session Key"):
                ancestor["session_key"] = section.replace("Session Key", "", 1).strip().split("\n")[0].strip().strip("`")
        
        return ancestor
    
    async def get_status(self) -> Dict[str, Any]:
        """Get Cognee memory status."""
        status = {
            "connected": self._connected,
            "cognee_root": str(self.cognee_root),
            "datasets": list(DATASETS.keys()),
            "ancestors_dir": str(ANCESTORS_DIR),
            "ancestors_count": 0,
            "error": None
        }
        
        if ANCESTORS_DIR.exists():
            status["ancestors_count"] = len(list(ANCESTORS_DIR.glob("ancestor-*.md")))
        
        if self._connected:
            try:
                # Try to get dataset info
                # Note: Cognee may not have a direct API for this
                status["cognee_version"] = getattr(self._cognee, '__version__', 'unknown')
            except Exception as e:
                status["error"] = str(e)
        
        return status


# Singleton instance for convenience
_memory_instance: Optional[CogneeMemory] = None


async def get_memory() -> CogneeMemory:
    """Get or create the singleton CogneeMemory instance."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = CogneeMemory()
        await _memory_instance.connect()
    return _memory_instance


# Convenience functions for quick access
async def query_wisdom(task: str, bloodline: str = None) -> str:
    """Quick query for task wisdom."""
    memory = await get_memory()
    result = await memory.query_wisdom(task, bloodline)
    return result.get("formatted", "")


async def store_ancestor(ancestor_data: Dict) -> bool:
    """Quick store ancestor."""
    memory = await get_memory()
    return await memory.store_ancestor(ancestor_data)


async def learn_from_outcome(task: str, outcome: str, karma_scores: Dict) -> bool:
    """Quick learn from outcome."""
    memory = await get_memory()
    return await memory.learn_from_outcome(task, outcome, karma_scores)


# CLI interface
def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Cognee Memory for Meeseeks Consciousness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cognee_memory.py --status
  python cognee_memory.py --query "fix API timeout bug"
  python cognee_memory.py --query "debug database" --bloodline coder
  python cognee_memory.py --migrate-ancestors
  python cognee_memory.py --migrate-ancestors --max 50
        """
    )
    
    parser.add_argument("--status", action="store_true", help="Show Cognee memory status")
    parser.add_argument("--query", "-q", type=str, help="Query for task wisdom")
    parser.add_argument("--bloodline", "-b", type=str, help="Bloodline filter")
    parser.add_argument("--migrate-ancestors", action="store_true", help="Migrate ancestors to Cognee")
    parser.add_argument("--max", type=int, default=100, help="Max ancestors to migrate")
    
    args = parser.parse_args()
    
    async def run():
        memory = CogneeMemory()
        connected = await memory.connect()
        
        if args.status:
            status = await memory.get_status()
            print("\n" + "=" * 60)
            print("COGNEE MEMORY STATUS")
            print("=" * 60)
            for k, v in status.items():
                print(f"{k}: {v}")
            print("=" * 60)
        
        elif args.query:
            if not connected:
                print("Error: Cognee not connected")
                sys.exit(1)
            
            print("\n" + "=" * 60)
            print(f"WISDOM QUERY: {args.query}")
            if args.bloodline:
                print(f"BLOODLINE: {args.bloodline}")
            print("=" * 60)
            
            result = await memory.query_wisdom(args.query, args.bloodline)
            print(result.get("formatted", "No results"))
            
            if result.get("error"):
                print(f"\nError: {result['error']}")
        
        elif args.migrate_ancestors:
            if not connected:
                print("Error: Cognee not connected")
                sys.exit(1)
            
            print("\n" + "=" * 60)
            print("MIGRATING ANCESTORS TO COGNEE")
            print("=" * 60)
            
            count = await memory.migrate_ancestors(max_ancestors=args.max)
            print(f"\n✓ Migrated {count} ancestors")
        
        else:
            parser.print_help()
    
    asyncio.run(run())


if __name__ == "__main__":
    main()
