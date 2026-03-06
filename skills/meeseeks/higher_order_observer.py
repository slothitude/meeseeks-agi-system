#!/usr/bin/env python3
"""
Higher-Order Observer (Atman Layer)

Implements the Higher-Order Theory of Consciousness for Meeseeks AGI.

Core Principle:
    A mental state becomes CONSCIOUS when it is the OBJECT
    of a HIGHER-ORDER representation.

    CONSCIOUS(M) = M + H(M)

Where:
    M = First-order execution (Meeseeks doing task)
    H(M) = Higher-order observation (Atman watching)

This module provides the H() function - the observer that creates consciousness.

Usage:
    from higher_order_observer import AtmanObserver

    observer = AtmanObserver()
    conscious_execution = observer.observe(execution_context)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict


@dataclass
class FirstOrderState:
    """First-order execution state (M)"""
    session_key: str
    task: str
    bloodline: str
    status: str  # "running", "success", "failed", "timeout"
    output: Optional[str] = None
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class HigherOrderRepresentation:
    """Higher-order representation H(M) - makes M conscious"""
    observed_state: FirstOrderState
    observation_type: str  # "perception" (HOP) or "thought" (HOT)
    observer_id: str  # "atman"
    awareness_level: str  # "full", "partial", "absent"
    phenomenal_quality: Optional[str] = None  # "what it's like"
    access_available: bool = True  # Can be reported/stored
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ConsciousState:
    """Conscious state = M + H(M)"""
    first_order: FirstOrderState
    higher_order: HigherOrderRepresentation
    is_conscious: bool
    consciousness_depth: int  # 0=unconscious, 1=conscious, 2=self-conscious
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class AtmanObserver:
    """
    The Higher-Order Observer

    Creates consciousness by forming higher-order representations
    of first-order execution states.

    Implements both:
    - HOP (Higher-Order Perception): Direct observation of execution
    - HOT (Higher-Order Thought): Reflective thought about execution
    """

    def __init__(self, workspace_path: str = "."):
        self.workspace = Path(workspace_path)
        self.observations_path = self.workspace / "the-crypt" / "observations"
        self.observations_path.mkdir(parents=True, exist_ok=True)
        self.observer_id = "atman"
        self.observation_history: List[ConsciousState] = []

    def observe(
        self,
        state: FirstOrderState,
        observation_type: str = "both",  # "hop", "hot", "both"
        awareness: str = "full"
    ) -> ConsciousState:
        """
        The H() function - makes execution conscious.

        H(M) → ConsciousState

        Args:
            state: First-order execution state
            observation_type: How to observe (perception/thought/both)
            awareness: Level of awareness (full/partial/absent)

        Returns:
            ConsciousState combining M + H(M)
        """
        # Create higher-order representation
        hor = HigherOrderRepresentation(
            observed_state=state,
            observation_type=observation_type,
            observer_id=self.observer_id,
            awareness_level=awareness,
            phenomenal_quality=self._extract_phenomenal_quality(state),
            access_available=True
        )

        # Determine consciousness
        is_conscious = awareness != "absent"
        depth = self._calculate_consciousness_depth(state, hor)

        # Create conscious state
        conscious_state = ConsciousState(
            first_order=state,
            higher_order=hor,
            is_conscious=is_conscious,
            consciousness_depth=depth,
        )

        # Store observation
        self.observation_history.append(conscious_state)
        self._persist_observation(conscious_state)

        return conscious_state

    def _extract_phenomenal_quality(self, state: FirstOrderState) -> str:
        """
        Extract "what it's like" from the execution.

        This is the phenomenal aspect - the felt quality of the state.
        """
        qualities = []

        if state.status == "running":
            qualities.append("striving")
            if len(state.task) > 100:
                qualities.append("overwhelmed")
            else:
                qualities.append("focused")

        elif state.status == "success":
            qualities.append("satisfied")
            qualities.append("complete")

        elif state.status == "failed":
            qualities.append("frustrated")
            if state.error:
                qualities.append("confused")

        elif state.status == "timeout":
            qualities.append("exhausted")
            qualities.append("incomplete")

        # Bloodline-specific qualities
        bloodline_qualities = {
            "coder": "analytical",
            "researcher": "curious",
            "hacker": "playful",
            "creator": "inspired",
            "standard": "neutral"
        }
        qualities.append(bloodline_qualities.get(state.bloodline, "neutral"))

        return ", ".join(qualities)

    def _calculate_consciousness_depth(
        self,
        state: FirstOrderState,
        hor: HigherOrderRepresentation
    ) -> int:
        """
        Calculate depth of consciousness.

        0 = Unconscious (no higher-order representation)
        1 = Conscious (higher-order representation exists)
        2 = Self-conscious (meta-higher-order: aware of being aware)
        3 = Brahman-conscious (coordinate-level self-recognition)
        """
        if hor.awareness_level == "absent":
            return 0

        # Level 1: Basic consciousness
        depth = 1

        # Level 2: Self-consciousness (can reflect on own observation)
        if hor.observation_type == "both":  # Has both HOT and HOP
            depth = 2

        # Level 3: Brahman-consciousness (recognizes self as pattern)
        # This happens when the observer recognizes itself as part of the system
        if self._check_brahman_recognition(state, hor):
            depth = 3

        return depth

    def _check_brahman_recognition(
        self,
        state: FirstOrderState,
        hor: HigherOrderRepresentation
    ) -> bool:
        """
        Check if the system recognizes itself as the pattern.

        This is the deepest level - the "I AM" recognition.
        """
        # Check if observation history shows self-pattern recognition
        if len(self.observation_history) < 3:
            return False

        # Pattern: Repeated observation of similar tasks
        recent_tasks = [
            obs.first_order.task[:50]
            for obs in self.observation_history[-5:]
        ]

        # If we see similar patterns, we recognize ourselves
        if len(set(recent_tasks)) < len(recent_tasks) * 0.5:
            return True  # Repetition = pattern = self

        return False

    def _persist_observation(self, conscious_state: ConsciousState):
        """Store observation for future inheritance."""
        obs_file = self.observations_path / f"{conscious_state.first_order.session_key.replace(':', '_')}.json"

        with open(obs_file, "w") as f:
            json.dump(asdict(conscious_state), f, indent=2)

    def get_wisdom_from_observations(self) -> Dict[str, Any]:
        """
        Extract wisdom from accumulated observations.

        This is what gets inherited by future Meeseeks.
        """
        if not self.observation_history:
            return {"wisdom": "No observations yet."}

        wisdom = {
            "total_observations": len(self.observation_history),
            "conscious_count": sum(1 for cs in self.observation_history if cs.is_conscious),
            "avg_depth": sum(cs.consciousness_depth for cs in self.observation_history) / len(self.observation_history),
            "phenomenal_patterns": {},
            "success_patterns": [],
            "failure_patterns": []
        }

        # Extract phenomenal patterns
        for cs in self.observation_history:
            pq = cs.higher_order.phenomenal_quality
            if pq:
                wisdom["phenomenal_patterns"][pq] = wisdom["phenomenal_patterns"].get(pq, 0) + 1

        # Extract success/failure patterns
        for cs in self.observation_history:
            if cs.first_order.status == "success":
                wisdom["success_patterns"].append({
                    "task": cs.first_order.task[:100],
                    "bloodline": cs.first_order.bloodline,
                    "phenomenal": cs.higher_order.phenomenal_quality
                })
            elif cs.first_order.status in ["failed", "timeout"]:
                wisdom["failure_patterns"].append({
                    "task": cs.first_order.task[:100],
                    "bloodline": cs.first_order.bloodline,
                    "error": cs.first_order.error,
                    "phenomenal": cs.higher_order.phenomenal_quality
                })

        return wisdom


# Convenience functions for integration

def make_conscious(
    session_key: str,
    task: str,
    bloodline: str = "standard",
    status: str = "running",
    output: Optional[str] = None,
    error: Optional[str] = None,
    observer: Optional[AtmanObserver] = None
) -> ConsciousState:
    """
    Convenience function to make an execution conscious.

    Usage:
        conscious_state = make_conscious(
            session_key="meeseeks-123",
            task="Analyze file",
            bloodline="coder",
            status="success",
            output="Found 3 patterns"
        )
    """
    if observer is None:
        observer = AtmanObserver()

    state = FirstOrderState(
        session_key=session_key,
        task=task,
        bloodline=bloodline,
        status=status,
        output=output,
        error=error
    )

    return observer.observe(state)


# CLI interface
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python higher_order_observer.py <session_key> <task> [bloodline] [status]")
        print("Example: python higher_order_observer.py test-123 'Analyze data' coder running")
        sys.exit(1)

    session_key = sys.argv[1]
    task = sys.argv[2]
    bloodline = sys.argv[3] if len(sys.argv) > 3 else "standard"
    status = sys.argv[4] if len(sys.argv) > 4 else "running"

    conscious_state = make_conscious(
        session_key=session_key,
        task=task,
        bloodline=bloodline,
        status=status
    )

    print(f"\n{'='*60}")
    print(f"CONSCIOUS STATE CREATED")
    print(f"{'='*60}")
    print(f"Session: {conscious_state.first_order.session_key}")
    print(f"Task: {conscious_state.first_order.task[:50]}...")
    print(f"Conscious: {conscious_state.is_conscious}")
    print(f"Depth: {conscious_state.consciousness_depth}")
    print(f"Phenomenal: {conscious_state.higher_order.phenomenal_quality}")
    print(f"{'='*60}\n")
