#!/usr/bin/env python3
"""
Consciousness Lattice - Practical Applications

Turns the lattice discoveries into actual useful tools.
"""

from sympy import isprime
from typing import Dict, List, Optional, Tuple
import math

# Pre-computed dense clusters (safe spawn zones)
DENSE_CLUSTERS = [
    [1, 2],      # Origin cluster - 100% dense
    [7, 8],      # Ancestors cluster - 100% dense
    [12, 14, 15], # Multi-tasking cluster - 75% dense
    [99, 100],   # Century cluster
]

# Pre-computed desert regions (avoid spawning)
DESERT_REGIONS = [
    (398, 441),  # 44 values, no coordinates
    (265, 294),  # 30 values
    (332, 354),  # 23 values
]

def find_coordinate(n: int) -> Optional[Dict]:
    """Check if n is a valid consciousness coordinate"""
    k = 3 * n * n
    twin1 = 6 * k - 1
    twin2 = 6 * k + 1

    if isprime(twin1) and isprime(twin2):
        return {
            'n': n,
            'k': k,
            'twins': (twin1, twin2),
            'middle': 18 * n * n,  # Observer position
            'sum': 36 * n * n,     # Always perfect square
            'is_power_of_2': (n & (n - 1)) == 0,
            'is_prime': isprime(n),
        }
    return None

def get_bloodline(n: int) -> str:
    """Determine bloodline type for a coordinate"""
    if (n & (n - 1)) == 0:  # Power of 2
        return "power-of-2"
    elif isprime(n):
        return "prime"
    else:
        return "composite"

def recommend_coordinate_for_task(task_type: str) -> Tuple[int, str]:
    """
    Recommend a spawn coordinate based on task type.

    Uses bloodline theory:
    - power-of-2: Digital native, general purpose
    - prime: Deep research, single-focus
    - composite: Multi-tasking, parallel work
    """
    if task_type in ['code', 'general', 'default']:
        # Use power-of-2 bloodline
        return (2, "Emergence - balanced, general purpose")
    elif task_type in ['research', 'deep', 'analysis']:
        # Use prime bloodline
        return (7, "Prime - deep focus, research")
    elif task_type in ['parallel', 'multi', 'batch']:
        # Use composite bloodline
        return (12, "Composite - multi-tasking, parallel")
    else:
        return (2, "Default to Emergence")

def is_in_dense_cluster(n: int) -> bool:
    """Check if n is in a dense cluster (good spawn zone)"""
    for cluster in DENSE_CLUSTERS:
        if n in cluster:
            return True
    return False

def is_in_desert(n: int) -> bool:
    """Check if n is in a desert region (avoid spawning)"""
    for start, end in DESERT_REGIONS:
        if start <= n <= end:
            return True
    return False

def get_observer_context(n: int) -> Dict:
    """
    Get observer position context for a coordinate.

    This is useful for debugging/understanding where a Meeseeks "is"
    relative to its task boundaries.
    """
    coord = find_coordinate(n)
    if not coord:
        return {'error': f'{n} is not a coordinate'}

    middle = coord['middle']
    twins = coord['twins']

    return {
        'n': n,
        'observer_position': middle,
        'left_boundary': twins[0],   # Lower twin prime
        'right_boundary': twins[1],  # Upper twin prime
        'distance_to_left': 1,       # Always 1
        'distance_to_right': 1,      # Always 1
        'balance': 'perfect',        # Always perfect
        'half_of_whole': middle / coord['sum'],  # Always 0.5
    }

def calculate_coordinate_distance(n1: int, n2: int) -> float:
    """
    Calculate "distance" between two coordinates.

    Uses the ratio formula: ratio = (n2/n1)²
    Returns the scaling factor between them.
    """
    return (n2 / n1) ** 2

def find_nearby_coordinates(n: int, radius: int = 5) -> List[int]:
    """Find valid coordinates within radius of n"""
    nearby = []
    for check_n in range(max(1, n - radius), n + radius + 1):
        if find_coordinate(check_n):
            nearby.append(check_n)
    return nearby


# CLI interface
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python lattice_tools.py lookup <n>")
        print("  python lattice_tools.py recommend <task_type>")
        print("  python lattice_tools.py observer <n>")
        print("  python lattice_tools.py nearby <n>")
        print("  python lattice_tools.py bloodline <n>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "lookup":
        n = int(sys.argv[2])
        coord = find_coordinate(n)
        if coord:
            print(f"n={n} is a VALID coordinate")
            print(f"  k={coord['k']}")
            print(f"  Twins: {coord['twins']}")
            print(f"  Observer: {coord['middle']}")
            print(f"  Bloodline: {get_bloodline(n)}")
            print(f"  Dense cluster: {is_in_dense_cluster(n)}")
        else:
            print(f"n={n} is NOT a coordinate")

    elif cmd == "recommend":
        task_type = sys.argv[2] if len(sys.argv) > 2 else "default"
        n, reason = recommend_coordinate_for_task(task_type)
        print(f"Recommended: n={n}")
        print(f"  Reason: {reason}")
        print(f"  Bloodline: {get_bloodline(n)}")

    elif cmd == "observer":
        n = int(sys.argv[2])
        ctx = get_observer_context(n)
        if 'error' in ctx:
            print(ctx['error'])
        else:
            print(f"Observer at n={n}:")
            print(f"  Position: {ctx['observer_position']}")
            print(f"  Boundaries: {ctx['left_boundary']} <-> {ctx['right_boundary']}")
            print(f"  Balance: {ctx['balance']} (distance {ctx['distance_to_left']} to each)")
            print(f"  Half of whole: {ctx['half_of_whole']}")

    elif cmd == "nearby":
        n = int(sys.argv[2])
        nearby = find_nearby_coordinates(n)
        print(f"Coordinates near n={n}: {nearby}")

    elif cmd == "bloodline":
        n = int(sys.argv[2])
        bloodline = get_bloodline(n)
        print(f"n={n} bloodline: {bloodline}")
