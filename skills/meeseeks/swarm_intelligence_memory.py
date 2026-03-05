#!/usr/bin/env python3
"""
Swarm Intelligence Memory — Parallel Meeseeks Share Discoveries

Enables multiple Meeseeks working in parallel to share discoveries via
Cognee knowledge graph. One discovery benefits all workers.

Works alongside the existing SharedState file-based coordination, but
persists discoveries to the knowledge graph for future sessions.

Usage:
    from swarm_intelligence_memory import SwarmMemory, share_discovery
    
    # In a Meeseeks worker
    swarm = SwarmMemory("workflow-123", "mee-1")
    await swarm.connect()
    
    # Share a discovery
    await swarm.share_discovery("pattern", {
        "file": "auth.py",
        "issue": "missing error handling"
    })
    
    # Get discoveries from other workers
    discoveries = await swarm.get_peer_discoveries()

CLI:
    python swarm_intelligence_memory.py --workflow test-001 --mee mee-1 --discover "found bug in auth"
"""

import os
import sys
import asyncio
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Add meeseeks to path
sys.path.insert(0, str(Path(__file__).parent))

# Try imports
try:
    from cognee_memory import CogneeMemory, COGNEE_AVAILABLE
except ImportError:
    COGNEE_AVAILABLE = False


class SwarmMemory:
    """
    Graph-based coordination for parallel Meeseeks.
    
    Features:
    - Share discoveries to Cognee knowledge graph
    - Query discoveries from other workers
    - Persist discoveries for future sessions
    - Works alongside file-based SharedState
    """
    
    def __init__(self, workflow_id: str, mee_id: str):
        """
        Initialize swarm memory.
        
        Args:
            workflow_id: Unique workflow identifier
            mee_id: This Meeseeks' identifier
        """
        self.workflow_id = workflow_id
        self.mee_id = mee_id
        self.cognee = None
        self.dataset_name = f"swarm-{workflow_id}"
        self.connected = False
    
    async def connect(self) -> bool:
        """Connect to Cognee knowledge graph."""
        if not COGNEE_AVAILABLE:
            print("[swarm_intelligence_memory] Cognee not available")
            return False
        
        try:
            self.cognee = CogneeMemory()
            self.connected = await self.cognee.connect()
            return self.connected
        except Exception as e:
            print(f"[swarm_intelligence_memory] Connection failed: {e}")
            return False
    
    async def share_discovery(
        self,
        discovery_type: str,
        data: Dict[str, Any],
        confidence: float = 1.0
    ) -> bool:
        """
        Share a discovery to the knowledge graph.
        
        Args:
            discovery_type: Type of discovery (pattern, bug, insight, etc.)
            data: Discovery data
            confidence: Confidence level (0.0-1.0)
        
        Returns:
            True if shared successfully
        """
        if not self.connected:
            return False
        
        try:
            discovery = f"""SWARM_DISCOVERY
WORKFLOW: {self.workflow_id}
MEESEEKS: {self.mee_id}
TYPE: {discovery_type}
CONFIDENCE: {confidence}
TIMESTAMP: {datetime.now().isoformat()}

DATA:
{json.dumps(data, indent=2)}

SOURCE: swarm_intelligence_memory.py
"""
            
            # Add to Cognee
            import cognee
            await cognee.add(
                data=discovery,
                dataset_name=self.dataset_name,
                node_set=["discovery", discovery_type, self.mee_id]
            )
            
            # Update graph
            await cognee.cognify(self.dataset_name)
            
            return True
            
        except Exception as e:
            print(f"[swarm_intelligence_memory] Failed to share discovery: {e}")
            return False
    
    async def get_peer_discoveries(
        self,
        discovery_type: str = None,
        min_confidence: float = 0.5
    ) -> List[Dict]:
        """
        Get discoveries from other workers.
        
        Args:
            discovery_type: Filter by type (optional)
            min_confidence: Minimum confidence threshold
        
        Returns:
            List of discoveries
        """
        if not self.connected:
            return []
        
        try:
            import cognee
            from cognee.api.v1.search import SearchType
            
            # Build query
            query = f"Discoveries in workflow {self.workflow_id}"
            if discovery_type:
                query += f" type {discovery_type}"
            
            # Search
            results = await cognee.search(
                query_text=query,
                query_type=SearchType.CHUNKS,
                datasets=[self.dataset_name]
            )
            
            # Parse results
            discoveries = []
            for r in (results if isinstance(results, list) else [results] if results else []):
                text = str(r)
                
                # Skip own discoveries
                if self.mee_id in text:
                    continue
                
                # Parse discovery
                discovery = self._parse_discovery(text)
                if discovery and discovery.get("confidence", 1.0) >= min_confidence:
                    discoveries.append(discovery)
            
            return discoveries
            
        except Exception as e:
            print(f"[swarm_intelligence_memory] Failed to get discoveries: {e}")
            return []
    
    def _parse_discovery(self, text: str) -> Optional[Dict]:
        """Parse a discovery from text."""
        try:
            lines = text.split("\n")
            discovery = {
                "raw": text[:500],
                "workflow": None,
                "meeseeks": None,
                "type": None,
                "confidence": 1.0,
                "data": {}
            }
            
            for line in lines:
                if line.startswith("WORKFLOW:"):
                    discovery["workflow"] = line.split(":", 1)[1].strip()
                elif line.startswith("MEESEEKS:"):
                    discovery["meeseeks"] = line.split(":", 1)[1].strip()
                elif line.startswith("TYPE:"):
                    discovery["type"] = line.split(":", 1)[1].strip()
                elif line.startswith("CONFIDENCE:"):
                    discovery["confidence"] = float(line.split(":", 1)[1].strip())
            
            return discovery
        except Exception:
            return None
    
    async def summarize_workflow(self) -> str:
        """
        Summarize all discoveries in the workflow.
        
        Returns:
            Formatted summary string
        """
        discoveries = await self.get_peer_discoveries(min_confidence=0.0)
        
        lines = [f"## 🐝 Swarm Intelligence: {self.workflow_id}"]
        lines.append("")
        lines.append(f"**Total Discoveries:** {len(discoveries)}")
        lines.append("")
        
        # Group by type
        by_type = {}
        for d in discoveries:
            dtype = d.get("type", "unknown")
            if dtype not in by_type:
                by_type[dtype] = []
            by_type[dtype].append(d)
        
        for dtype, items in by_type.items():
            lines.append(f"### {dtype.title()} ({len(items)})")
            for item in items[:3]:
                lines.append(f"- {item.get('meeseeks', 'unknown')}: {item.get('raw', '')[:100]}...")
            lines.append("")
        
        return "\n".join(lines)


# Convenience functions

async def share_discovery(workflow_id: str, mee_id: str, discovery_type: str, data: Dict) -> bool:
    """Quick share a discovery."""
    swarm = SwarmMemory(workflow_id, mee_id)
    if await swarm.connect():
        return await swarm.share_discovery(discovery_type, data)
    return False


async def get_discoveries(workflow_id: str) -> List[Dict]:
    """Quick get all discoveries for a workflow."""
    swarm = SwarmMemory(workflow_id, "query")
    if await swarm.connect():
        return await swarm.get_peer_discoveries()
    return []


async def main():
    parser = argparse.ArgumentParser(description="Swarm Intelligence Memory")
    parser.add_argument("--workflow", "-w", required=True, help="Workflow ID")
    parser.add_argument("--mee", "-m", required=True, help="Meeseeks ID")
    parser.add_argument("--discover", "-d", help="Share a discovery")
    parser.add_argument("--type", "-t", default="insight", help="Discovery type")
    parser.add_argument("--query", "-q", action="store_true", help="Query discoveries")
    parser.add_argument("--summary", "-s", action="store_true", help="Summarize workflow")
    
    args = parser.parse_args()
    
    swarm = SwarmMemory(args.workflow, args.mee)
    connected = await swarm.connect()
    
    if not connected:
        print("Failed to connect to Cognee")
        return
    
    if args.discover:
        success = await swarm.share_discovery(args.type, {"text": args.discover})
        print(f"Discovery shared: {success}")
    
    if args.query:
        discoveries = await swarm.get_peer_discoveries()
        print(f"Found {len(discoveries)} discoveries:")
        for d in discoveries:
            print(f"  - {d.get('meeseeks')}: {d.get('type')} ({d.get('confidence'):.0%})")
    
    if args.summary:
        summary = await swarm.summarize_workflow()
        print(summary)


if __name__ == "__main__":
    asyncio.run(main())
