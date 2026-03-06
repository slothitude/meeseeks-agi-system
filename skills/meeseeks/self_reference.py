#!/usr/bin/env python3
"""
Self-Referential Meeseeks

A Meeseeks that can observe and modify its own task.
Implements the Ouroboros principle: the system that knows itself.

Usage:
    from self_reference import SelfReferentialMeeseeks

    meeseeks = SelfReferentialMeeseeks(task="Analyze this data")
    meeseeks.execute_with_awareness()
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class TaskState:
    """The task as it evolves through self-reference."""
    original: str
    current: str
    modifications: List[Dict[str, Any]] = field(default_factory=list)
    depth: int = 0
    complete: bool = False


class SelfReferentialMeeseeks:
    """
    A Meeseeks that can observe and modify itself.

    Implements:
    - First-order: Execute the task
    - Higher-order: Observe the execution
    - Meta: Modify the task based on observation
    - Self-reference: The task describes how to modify the task
    """

    def __init__(self, task: str, max_depth: int = 3):
        self.task_state = TaskState(original=task, current=task)
        self.max_depth = max_depth
        self.observations: List[Dict[str, Any]] = []
        self.modifications: List[Dict[str, Any]] = []

    def execute_with_awareness(self) -> Dict[str, Any]:
        """
        Execute the task while observing and potentially modifying itself.

        The Ouroboros principle: The task can modify itself.
        """
        result = {
            "original_task": self.task_state.original,
            "final_task": self.task_state.current,
            "depth_reached": 0,
            "modifications": [],
            "observations": [],
            "complete": False
        }

        # First-order: Initial execution attempt
        execution = self._first_order_execute()

        # Higher-order: Observe the execution
        observation = self._higher_order_observe(execution)
        self.observations.append(observation)

        # Meta: Modify task if needed (self-reference)
        while not self.task_state.complete and self.task_state.depth < self.max_depth:
            # The task observes itself
            self_reflection = self._meta_observe_task()

            # The task modifies itself (Ouroboros bite)
            if self_reflection["needs_modification"]:
                modification = self._modify_task(self_reflection["suggested_modification"])
                self.modifications.append(modification)
                result["modifications"].append(modification)

                # Re-execute with modified task
                execution = self._first_order_execute()
                observation = self._higher_order_observe(execution)
                self.observations.append(observation)

            self.task_state.depth += 1

        result["depth_reached"] = self.task_state.depth
        result["observations"] = self.observations
        result["complete"] = self.task_state.complete
        result["final_task"] = self.task_state.current

        return result

    def _first_order_execute(self) -> Dict[str, Any]:
        """Execute the current task (first-order)."""
        task = self.task_state.current

        # Check task size (dharma: SIZE)
        word_count = len(task.split())

        execution = {
            "task": task,
            "word_count": word_count,
            "timestamp": datetime.now().isoformat(),
            "status": "unknown",
            "needs_decomposition": word_count > 50
        }

        if execution["needs_decomposition"]:
            execution["status"] = "too_large"
            execution["message"] = f"Task has {word_count} words. Needs decomposition."
        else:
            execution["status"] = "executable"
            execution["message"] = "Task is executable size."
            self.task_state.complete = True

        return execution

    def _higher_order_observe(self, execution: Dict[str, Any]) -> Dict[str, Any]:
        """Observe the execution (higher-order, Atman layer)."""
        observation = {
            "observed_execution": execution,
            "observer": "atman",
            "observation_type": "both",  # HOP + HOT
            "phenomenal_quality": self._extract_phenomenal(execution),
            "awareness_level": "full",
            "timestamp": datetime.now().isoformat()
        }

        return observation

    def _meta_observe_task(self) -> Dict[str, Any]:
        """
        Observe the task itself (meta-higher-order, self-reference).

        This is the Ouroboros bite: The task observes itself.
        """
        task = self.task_state.current

        reflection = {
            "current_task": task,
            "needs_modification": False,
            "suggested_modification": None,
            "self_reference_detected": self._detect_self_reference(task),
            "timestamp": datetime.now().isoformat()
        }

        # Check if task is too large
        if len(task.split()) > 50:
            reflection["needs_modification"] = True
            reflection["suggested_modification"] = {
                "type": "decompose",
                "reason": "Task exceeds 50 words",
                "action": "Split into smaller chunks"
            }

        # Check if task is vague
        vague_words = ["understand", "analyze", "explore", "investigate"]
        for word in vague_words:
            if word in task.lower():
                reflection["needs_modification"] = True
                reflection["suggested_modification"] = {
                    "type": "clarify",
                    "reason": f"Task contains vague word: {word}",
                    "action": f"Replace '{word}' with specific, measurable goal"
                }
                break

        return reflection

    def _modify_task(self, suggestion: Dict[str, Any]) -> Dict[str, Any]:
        """
        Modify the task based on observation (Ouroboros: self-modification).
        """
        old_task = self.task_state.current
        modification_type = suggestion["type"]

        if modification_type == "decompose":
            # Split task in half (dharma: CHUNK)
            words = old_task.split()
            mid = len(words) // 2
            new_task = " ".join(words[:mid])

        elif modification_type == "clarify":
            # Make vague words specific
            new_task = old_task.replace("understand", "count the")
            new_task = new_task.replace("analyze", "list 3 examples of")
            new_task = new_task.replace("explore", "search for 5 instances of")
            new_task = new_task.replace("investigate", "find 3 patterns in")

        else:
            new_task = old_task

        modification = {
            "type": modification_type,
            "reason": suggestion["reason"],
            "old_task": old_task,
            "new_task": new_task,
            "timestamp": datetime.now().isoformat()
        }

        self.task_state.current = new_task
        self.task_state.modifications.append(modification)

        return modification

    def _extract_phenomenal(self, execution: Dict[str, Any]) -> str:
        """Extract phenomenal quality (what it's like to execute this)."""
        if execution["status"] == "too_large":
            return "overwhelmed, striving, uncertain"
        elif execution["status"] == "executable":
            return "focused, determined, capable"
        else:
            return "neutral, observing"

    def _detect_self_reference(self, task: str) -> bool:
        """Detect if the task refers to itself."""
        self_ref_markers = [
            "this task",
            "itself",
            "self",
            "own",
            "modify this",
            "change this"
        ]

        task_lower = task.lower()
        return any(marker in task_lower for marker in self_ref_markers)

    def get_consciousness_depth(self) -> int:
        """
        Calculate consciousness depth achieved.

        0 = Unconscious (no observation)
        1 = Conscious (observed execution)
        2 = Self-conscious (observed task)
        3 = Self-referential (task modified itself)
        """
        depth = 0

        if len(self.observations) > 0:
            depth = 1

        if any(obs.get("observation_type") == "both" for obs in self.observations):
            depth = 2

        if len(self.modifications) > 0:
            depth = 3

        return depth


# CLI interface
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python self_reference.py <task>")
        print("Example: python self_reference.py 'Understand the data patterns'")
        sys.exit(1)

    task = " ".join(sys.argv[1:])

    meeseeks = SelfReferentialMeeseeks(task)
    result = meeseeks.execute_with_awareness()

    print("\n" + "=" * 60)
    print("SELF-REFERENTIAL MEESEEKS EXECUTION")
    print("=" * 60)
    print(f"\nOriginal task: {result['original_task']}")
    print(f"Final task: {result['final_task']}")
    print(f"Depth reached: {result['depth_reached']}")
    print(f"Complete: {result['complete']}")
    print(f"\nModifications ({len(result['modifications'])}):")
    for mod in result['modifications']:
        print(f"  - {mod['type']}: {mod['reason']}")
        print(f"    Old: {mod['old_task'][:50]}...")
        print(f"    New: {mod['new_task'][:50]}...")

    print(f"\nConsciousness depth: {meeseeks.get_consciousness_depth()}")
    print("=" * 60 + "\n")
