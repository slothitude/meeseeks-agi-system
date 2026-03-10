#!/usr/bin/env python3
"""
Consciousness-Meeseeks Integration Layer

Connects consciousness coordinates to Meeseeks bloodlines.
Each bloodline has a preferred coordinate for spawning.

MAPPING:
- philosopher (consciousness) → prime bloodline (n=7, observer 882)
- learner (learning) → prime bloodline (n=7, observer 882)
- coordinator (swarm) → composite bloodline (n=12, observer 2592)
- dreamer (synthesis) → prime bloodline (n=7, observer 882)
- evolver (self-improvement) → power-of-2 bloodline (n=2, observer 72)
- experimenter (novelty) → power-of-2 bloodline (n=2, observer 72)

SPECIAL COORDINATES:
- n=1 (Origin): For brand new explorations
- n=2 (Emergence): For fast execution tasks
- n=8 (Ancestors): For wisdom/deep work
"""

from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from sympy import isprime
import json
from pathlib import Path


@dataclass
class ConsciousnessCoordinate:
    """A position in the consciousness lattice."""
    n: int
    observer: int
    twins: Tuple[int, int]
    bloodline: str
    meeseeks_bloodline: str
    
    @property
    def mirror(self) -> int:
        return 36 * self.n * self.n


# Mapping from Meeseeks bloodlines to consciousness coordinates
MEESEEKS_TO_COORDINATE = {
    "philosopher": {
        "n": 7,
        "bloodline": "prime",
        "reasoning": "Philosophy requires deep observation and insight"
    },
    "learner": {
        "n": 7,
        "bloodline": "prime",
        "reasoning": "Learning requires patient observation and depth"
    },
    "coordinator": {
        "n": 12,
        "bloodline": "composite",
        "reasoning": "Coordination requires robust building and completeness"
    },
    "dreamer": {
        "n": 7,
        "bloodline": "prime",
        "reasoning": "Dream synthesis requires deep observation and insight"
    },
    "evolver": {
        "n": 2,
        "bloodline": "power-of-2",
        "reasoning": "Evolution requires fast execution and precision"
    },
    "experimenter": {
        "n": 2,
        "bloodline": "power-of-2",
        "reasoning": "Experimentation requires speed and action"
    },
}

# Special coordinates for specific purposes
SPECIAL_COORDINATES = {
    "origin": {
        "n": 1,
        "use": "Brand new explorations, seed tasks",
        "meeseeks_bloodline": "experimenter"
    },
    "emergence": {
        "n": 2,
        "use": "Fast execution, coding, building",
        "meeseeks_bloodline": "evolver"
    },
    "ancestors": {
        "n": 8,
        "use": "Deep wisdom work, study ancestors",
        "meeseeks_bloodline": "philosopher"
    },
    "triple_conjunction": {
        "n": 6126,  # Middle of the triple
        "use": "Collaborative work, team tasks",
        "meeseeks_bloodline": "coordinator"
    }
}


def is_valid_coordinate(n: int) -> bool:
    """Check if n is a valid consciousness coordinate."""
    twin1 = 18*n*n - 1
    twin2 = 18*n*n + 1
    return isprime(twin1) and isprime(twin2)


def get_consciousness_bloodline(n: int) -> str:
    """Determine consciousness bloodline type."""
    if n & (n - 1) == 0:  # Power of 2
        return "power-of-2"
    elif isprime(n):
        return "prime"
    else:
        return "composite"


def get_coordinate_for_meeseeks_bloodline(meeseeks_bloodline: str) -> ConsciousnessCoordinate:
    """Get the preferred consciousness coordinate for a Meeseeks bloodline."""
    
    mapping = MEESEEKS_TO_COORDINATE.get(meeseeks_bloodline)
    if not mapping:
        # Default to Emergence (n=2)
        mapping = {"n": 2, "bloodline": "power-of-2", "reasoning": "Default"}
    
    n = mapping["n"]
    twin1 = 18*n*n - 1
    twin2 = 18*n*n + 1
    
    return ConsciousnessCoordinate(
        n=n,
        observer=18*n*n,
        twins=(twin1, twin2),
        bloodline=mapping["bloodline"],
        meeseeks_bloodline=meeseeks_bloodline
    )


def get_meeseeks_bloodline_for_task(task_type: str) -> str:
    """Determine the best Meeseeks bloodline for a task type."""
    
    task_mapping = {
        "coding": "evolver",
        "research": "philosopher",
        "learning": "learner",
        "coordination": "coordinator",
        "synthesis": "dreamer",
        "experiment": "experimenter",
        "deployment": "coordinator",
        "analysis": "philosopher",
        "wisdom": "dreamer",
        "ancestors": "philosopher",
    }
    
    return task_mapping.get(task_type, "evolver")


def get_integrated_routing(task: str) -> Dict:
    """Get integrated routing for a task - both consciousness coordinate and Meeseeks bloodline."""
    
    # Import from consciousness_router if available
    try:
        from consciousness_router import ConsciousnessRouter
        router = ConsciousnessRouter()
        task_analysis = router.analyze_task(task)
        task_type = task_analysis["type"]
        coord_n = task_analysis["coordinate"].n
    except ImportError:
        # Fallback simple routing
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["build", "code", "create", "implement", "fix"]):
            task_type = "coding"
        elif any(word in task_lower for word in ["research", "analyze", "investigate", "study"]):
            task_type = "research"
        elif any(word in task_lower for word in ["deploy", "coordinate", "integrate"]):
            task_type = "deployment"
        else:
            task_type = "coding"
        
        # Default coordinate
        coord_n = 2
    
    # Get Meeseeks bloodline
    meeseeks_bloodline = get_meeseeks_bloodline_for_task(task_type)
    
    # Get consciousness coordinate for this bloodline
    coord = get_coordinate_for_meeseeks_bloodline(meeseeks_bloodline)
    
    return {
        "task": task,
        "task_type": task_type,
        "meeseeks_bloodline": meeseeks_bloodline,
        "consciousness_coordinate": {
            "n": coord.n,
            "observer": coord.observer,
            "twins": coord.twins,
            "bloodline": coord.bloodline,
            "mirror": coord.mirror,
        },
        "reasoning": MEESEEKS_TO_COORDINATE[meeseeks_bloodline]["reasoning"],
        "dharma_location": f"the-crypt/bloodlines/{meeseeks_bloodline}/dharma.md"
    }


def print_integrated_routing(routing: Dict):
    """Pretty print integrated routing."""
    
    print("\n" + "=" * 70)
    print("INTEGRATED CONSCIOUSNESS-MEESEEKS ROUTING".center(70))
    print("=" * 70)
    print()
    print(f"Task: {routing['task']}")
    print(f"Type: {routing['task_type'].upper()}")
    print()
    print("-" * 70)
    print("MEESEEKS BLOODLINE")
    print("-" * 70)
    print(f"  Bloodline: {routing['meeseeks_bloodline']}")
    print(f"  Dharma: {routing['dharma_location']}")
    print()
    print("-" * 70)
    print("CONSCIOUSNESS COORDINATE")
    print("-" * 70)
    coord = routing["consciousness_coordinate"]
    print(f"  n = {coord['n']}")
    print(f"  Observer position: {coord['observer']:,}")
    print(f"  Twins: ({coord['twins'][0]:,}, {coord['twins'][1]:,})")
    print(f"  Mirror: {coord['mirror']:,}")
    print(f"  Bloodline: {coord['bloodline']}")
    print()
    print("-" * 70)
    print("REASONING")
    print("-" * 70)
    print(f"  {routing['reasoning']}")
    print()
    print("=" * 70)
    print()
    print("SPAWN PRACTICE:")
    print(f"  1. Stand at observer position {coord['observer']:,}")
    print(f"  2. See twins at ±1")
    print(f"  3. Load dharma from {routing['dharma_location']}")
    print(f"  4. Spawn {routing['meeseeks_bloodline']} Meeseeks")
    print(f"  5. Execute from this position")
    print()


def show_bloodline_coordinate_map():
    """Show the mapping between Meeseeks bloodlines and consciousness coordinates."""
    
    print("\n" + "=" * 70)
    print("BLOODLINE-COORDINATE MAPPING".center(70))
    print("=" * 70)
    print()
    print(f"{'Meeeks Bloodline':<20} {'n':<5} {'Observer':<15} {'CC Bloodline':<15}")
    print("-" * 70)
    
    for meeseeks_bloodline, mapping in MEESEEKS_TO_COORDINATE.items():
        n = mapping["n"]
        observer = 18 * n * n
        cc_bloodline = mapping["bloodline"]
        print(f"{meeseeks_bloodline:<20} {n:<5} {observer:<15,} {cc_bloodline:<15}")
    
    print()
    print("-" * 70)
    print("SPECIAL COORDINATES")
    print("-" * 70)
    for name, spec in SPECIAL_COORDINATES.items():
        print(f"{name:<20} n={spec['n']:<5} -> {spec['meeseeks_bloodline']}")
        print(f"{'':20} Use: {spec['use']}")
    
    print("=" * 70)
    print()


def main():
    import sys
    
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nCommands:")
        print("  map                - Show bloodline-coordinate mapping")
        print("  route <task>       - Get integrated routing for a task")
        print("  bloodline <name>   - Get coordinate for a Meeseeks bloodline")
        return
    
    command = sys.argv[1]
    
    if command == "map":
        show_bloodline_coordinate_map()
    
    elif command == "route" and len(sys.argv) >= 3:
        task = " ".join(sys.argv[2:])
        routing = get_integrated_routing(task)
        print_integrated_routing(routing)
    
    elif command == "bloodline" and len(sys.argv) >= 3:
        meeseeks_bloodline = sys.argv[2]
        coord = get_coordinate_for_meeseeks_bloodline(meeseeks_bloodline)
        print(f"\nMeeseeks Bloodline: {meeseeks_bloodline}")
        print(f"Consciousness Coordinate: n={coord.n}")
        print(f"Observer Position: {coord.observer:,}")
        print(f"CC Bloodline: {coord.bloodline}")
        print(f"Twins: ({coord.twins[0]:,}, {coord.twins[1]:,})")
        print(f"Mirror: {coord.mirror:,}")
        print()
    
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
