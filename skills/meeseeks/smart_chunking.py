#!/usr/bin/env python3
"""
Smart Task Chunking System

Analyzes task structure and creates semantically coherent chunks.
Replaces simple text splitting with intelligent decomposition.

Usage:
    from smart_chunking import SmartChunker

    chunker = SmartChunker()
    chunks = chunker.chunk_task(task_text, max_chunks=3)
"""

import re
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class TaskType(Enum):
    """Types of tasks for specialized chunking strategies."""
    EVOLUTION = "evolution"
    CODING = "coding"
    ANALYSIS = "analysis"
    SEARCH = "search"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    RESEARCH = "research"
    GENERIC = "generic"


@dataclass
class ChunkMetadata:
    """Metadata for a task chunk."""
    index: int
    total: int
    task_type: TaskType
    dependencies: List[int]  # Indices of chunks this depends on
    outputs: List[str]  # What this chunk produces
    estimated_complexity: float  # 0-10 score
    is_atomic: bool  # Can this be further chunked?


class SmartChunker:
    """Intelligent task chunking with semantic analysis."""

    def __init__(self):
        self.task_patterns = {
            TaskType.EVOLUTION: ["evolve", "genealogy", "species", "dna", "bloodline"],
            TaskType.CODING: ["implement", "fix", "refactor", "code", "bug", "function"],
            TaskType.ANALYSIS: ["analyze", "study", "examine", "compare", "identify"],
            TaskType.SEARCH: ["search", "find", "locate", "scan", "lookup"],
            TaskType.TESTING: ["test", "verify", "check", "validate", "ensure"],
            TaskType.DEPLOYMENT: ["deploy", "release", "build", "publish", "ship"],
            TaskType.RESEARCH: ["research", "investigate", "explore", "discover"],
        }

    def detect_task_type(self, task: str) -> TaskType:
        """Detect the type of task from its description."""
        task_lower = task.lower()

        for task_type, keywords in self.task_patterns.items():
            if any(kw in task_lower for kw in keywords):
                return task_type

        return TaskType.GENERIC

    def extract_structure(self, task: str) -> Dict[str, Any]:
        """
        Extract structural elements from a task.

        Returns:
            Dict with steps, dependencies, outputs, and context
        """
        structure = {
            "steps": [],
            "dependencies": [],
            "outputs": [],
            "context": {},
            "has_numbered_steps": False,
            "has_markdown_headers": False,
        }

        # Extract numbered steps
        step_pattern = r'(?:^|\n)\s*(\d+)[.\)]\s*(.+?)(?=(?:\n\s*\d+[.\)])|$)'
        numbered_steps = re.findall(step_pattern, task, re.DOTALL)

        if numbered_steps:
            structure["has_numbered_steps"] = True
            structure["steps"] = [
                {"number": int(num), "text": text.strip(), "type": "numbered"}
                for num, text in numbered_steps
            ]

        # Extract markdown headers
        header_pattern = r'^#+\s+(.+)$'
        headers = re.findall(header_pattern, task, re.MULTILINE)

        if headers:
            structure["has_markdown_headers"] = True
            if not structure["steps"]:  # Use headers if no numbered steps
                structure["steps"] = [
                    {"number": i+1, "text": h.strip(), "type": "header"}
                    for i, h in enumerate(headers)
                ]

        # Extract file references (outputs)
        file_pattern = r'(?:write|save|output|create)\s+(?:to\s+)?[`\'"]?([^\s`\'"]+\.[a-zA-Z]{1,4})[`\'"]?'
        files = re.findall(file_pattern, task, re.IGNORECASE)
        structure["outputs"] = files

        # Detect dependencies between steps
        if len(structure["steps"]) > 1:
            for i, step in enumerate(structure["steps"]):
                if i > 0:
                    # Simple heuristic: later steps depend on earlier ones
                    # unless they start with "Read" or "Analyze" (independent)
                    text = step["text"].lower()
                    if not any(kw in text for kw in ["read", "analyze", "check", "review"]):
                        structure["dependencies"].append({
                            "step": i,
                            "depends_on": list(range(i))
                        })

        return structure

    def score_chunk_quality(self, chunk: str, original_task: str) -> float:
        """
        Score chunk coherence (0-10).

        Higher scores = better, more complete chunks.
        """
        score = 10.0

        # Penalize very short chunks
        if len(chunk) < 50:
            score -= 5
        elif len(chunk) < 100:
            score -= 2

        # Penalize incomplete sentences
        if not chunk.strip().endswith(('.', '!', '?', '```', ':')):
            score -= 1

        # Penalize chunks that start with lowercase
        if chunk.strip() and chunk.strip()[0].islower():
            score -= 1

        # Penalize chunks with hanging references
        if re.search(r'\b(it|this|that|these|those)\b', chunk.split('\n')[0]):
            score -= 1

        # Reward chunks with clear action verbs
        action_verbs = ['read', 'write', 'create', 'update', 'analyze', 'implement', 'fix']
        if any(verb in chunk.lower() for verb in action_verbs):
            score += 1

        # Reward self-contained chunks (have context)
        if 'context' in chunk.lower() or 'background' in chunk.lower():
            score += 1

        return max(0, min(10, score))

    def should_chunk_task(self, task: str, task_type: TaskType) -> Tuple[bool, str]:
        """
        Determine if a task should be chunked.

        Returns:
            (should_chunk: bool, reason: str)
        """
        # Don't chunk already chunked tasks at depth 3
        chunk_depth = task.count("RETRY CHUNK")
        if chunk_depth >= 3:
            return False, "Max chunk depth (3) reached"

        # Don't chunk very short tasks
        if len(task) < 200:
            return False, "Task too short to chunk effectively"

        # Check for atomic operations
        atomic_patterns = [
            r'atomic',
            r'single\s+transaction',
            r'all\s+or\s+nothing',
            r'must\s+complete\s+together',
        ]

        for pattern in atomic_patterns:
            if re.search(pattern, task, re.IGNORECASE):
                return False, "Task marked as atomic operation"

        # Task type specific rules
        if task_type == TaskType.EVOLUTION:
            # Evolution tasks are complex, benefit from chunking
            return True, "Evolution tasks benefit from chunking"

        if task_type == TaskType.TESTING:
            # Tests should run as complete suites
            if 'test suite' in task.lower() or 'all tests' in task.lower():
                return False, "Test suites should run atomically"

        # Default: chunk if task has multiple steps
        structure = self.extract_structure(task)
        if len(structure["steps"]) >= 2:
            return True, f"Task has {len(structure['steps'])} distinct steps"

        # Chunk if task is long and unstructured
        if len(task) > 500:
            return True, "Long unstructured task"

        return False, "Task doesn't benefit from chunking"

    def create_smart_chunks(
        self,
        task: str,
        max_chunks: int = 3,
        min_chunk_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Create semantically coherent chunks from a task.

        Args:
            task: The task text to chunk
            max_chunks: Maximum number of chunks to create
            min_chunk_size: Minimum characters per chunk

        Returns:
            List of chunk dicts with metadata
        """
        task_type = self.detect_task_type(task)
        structure = self.extract_structure(task)

        # Decide chunking strategy
        if structure["has_numbered_steps"] and len(structure["steps"]) >= 2:
            # Use numbered steps as natural boundaries
            chunks = self._chunk_by_steps(task, structure, max_chunks)
        elif structure["has_markdown_headers"]:
            # Use markdown headers as boundaries
            chunks = self._chunk_by_headers(task, structure, max_chunks)
        else:
            # Fall back to paragraph/text chunking
            chunks = self._chunk_by_text(task, max_chunks, min_chunk_size)

        # Add metadata to each chunk
        enriched_chunks = []
        for i, chunk_text in enumerate(chunks):
            quality = self.score_chunk_quality(chunk_text, task)

            enriched_chunks.append({
                "text": chunk_text,
                "index": i,
                "total": len(chunks),
                "quality_score": quality,
                "task_type": task_type.value,
                "is_self_contained": quality >= 7,
            })

        return enriched_chunks

    def _chunk_by_steps(
        self,
        task: str,
        structure: Dict[str, Any],
        max_chunks: int
    ) -> List[str]:
        """Chunk task by numbered steps, respecting dependencies."""
        steps = structure["steps"]

        # Group steps into chunks
        chunks = []
        chunk_count = min(max_chunks, len(steps))
        steps_per_chunk = max(1, len(steps) // chunk_count)

        # Add context to first chunk
        context = self._extract_context(task)

        for i in range(0, len(steps), steps_per_chunk):
            chunk_steps = steps[i:i+steps_per_chunk]

            # Build chunk text
            chunk_text = ""
            if i == 0 and context:
                chunk_text = f"CONTEXT:\n{context}\n\n"

            chunk_text += "TASK CHUNK:\n"
            for step in chunk_steps:
                chunk_text += f"{step['number']}. {step['text']}\n\n"

            # Add dependency note if needed
            if i > 0 and structure["dependencies"]:
                chunk_text += "NOTE: This chunk continues from previous chunk.\n"

            chunks.append(chunk_text.strip())

        return chunks

    def _chunk_by_headers(
        self,
        task: str,
        structure: Dict[str, Any],
        max_chunks: int
    ) -> List[str]:
        """Chunk task by markdown headers."""
        # Split by headers
        header_pattern = r'(^#+\s+.+$)'
        parts = re.split(header_pattern, task, flags=re.MULTILINE)

        chunks = []
        current_chunk = ""

        for i, part in enumerate(parts):
            if re.match(header_pattern, part, re.MULTILINE):
                # This is a header
                if current_chunk and len(chunks) < max_chunks - 1:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                current_chunk += part + "\n"
            else:
                current_chunk += part

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks if chunks else [task]

    def _chunk_by_text(
        self,
        task: str,
        max_chunks: int,
        min_chunk_size: int
    ) -> List[str]:
        """Fallback: chunk by text length (paragraphs or character count)."""
        # Try paragraph split first
        paragraphs = [p.strip() for p in task.split('\n\n') if p.strip()]

        if len(paragraphs) >= 2:
            # Group paragraphs into chunks
            chunks = []
            chunk_count = min(max_chunks, len(paragraphs))
            per_chunk = max(1, len(paragraphs) // chunk_count)

            for i in range(0, len(paragraphs), per_chunk):
                chunk = '\n\n'.join(paragraphs[i:i+per_chunk])
                if len(chunk) >= min_chunk_size or i == len(paragraphs) - per_chunk:
                    chunks.append(chunk)

            return chunks if chunks else [task]

        # Fall back to character-based split
        chunk_size = max(min_chunk_size, len(task) // max_chunks)
        chunks = []

        for i in range(0, len(task), chunk_size):
            chunk = task[i:i+chunk_size]
            if len(chunk) >= min_chunk_size:
                chunks.append(chunk)

        return chunks if chunks else [task]

    def _extract_context(self, task: str) -> str:
        """Extract contextual information from task (intro, background, etc)."""
        # Get text before first numbered step or header
        lines = task.split('\n')

        context_lines = []
        for line in lines:
            # Stop at numbered step or header
            if re.match(r'^\s*\d+[.\)]', line) or line.startswith('#'):
                break
            context_lines.append(line)

        context = '\n'.join(context_lines).strip()

        # Limit context length
        if len(context) > 200:
            context = context[:200] + "..."

        return context


def smart_chunk_task(task: str, max_chunks: int = 3) -> List[Dict[str, Any]]:
    """
    Convenience function for smart chunking.

    Args:
        task: Task text to chunk
        max_chunks: Maximum chunks to create

    Returns:
        List of chunk dicts with metadata
    """
    chunker = SmartChunker()
    return chunker.create_smart_chunks(task, max_chunks=max_chunks)


if __name__ == "__main__":
    # Test the chunker
    test_task = """
    🧬 EVOLVE RESEARCH CAPABILITIES

    You are a Meeseeks tasked with evolving the research/search capabilities.

    ## Your Mission

    ### 1. Analyze Current Research Tools
    - Read skills/meeseeks/templates/searcher.md
    - Check skills/searxng-search/SKILL.md
    - Review skills/search-workflow/SKILL.md
    - Identify gaps and improvement opportunities

    ### 2. Research AGI Patterns for Search
    - Consider: hierarchical search, multi-source fusion
    - Think about: relevance ranking, source credibility
    - Apply: Memory-Prediction for search quality

    ### 3. Propose Enhancements
    - Create a research-enhanced template
    - Add multi-step research workflows
    - Integrate citation/source tracking

    ### 4. Create Evolution Report
    - Write to: the-crypt/evolution/RESEARCH-EVOLUTION-2026-03-02.md
    - Include: current state, proposed changes, implementation plan
    """

    chunker = SmartChunker()

    print("=" * 60)
    print("TASK TYPE:", chunker.detect_task_type(test_task).value)
    print("=" * 60)

    should_chunk, reason = chunker.should_chunk_task(
        test_task,
        chunker.detect_task_type(test_task)
    )
    print(f"\nShould chunk: {should_chunk}")
    print(f"Reason: {reason}\n")

    print("=" * 60)
    print("SMART CHUNKS:")
    print("=" * 60)

    chunks = chunker.create_smart_chunks(test_task, max_chunks=3)

    for chunk in chunks:
        print(f"\n--- Chunk {chunk['index']+1}/{chunk['total']} ---")
        print(f"Quality Score: {chunk['quality_score']}/10")
        print(f"Self-contained: {chunk['is_self_contained']}")
        # Avoid unicode issues in Windows console
        text_preview = chunk['text'][:200].encode('ascii', 'ignore').decode('ascii')
        print(f"\n{text_preview}...")
        print()
