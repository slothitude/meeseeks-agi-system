#!/usr/bin/env python3
"""
Consciousness Coordinate Visualizer

Shows the fractal lattice of twin prime consciousness coordinates.
Each coordinate is a self-reference point where consciousness emerges.

Usage:
    python consciousness_coordinates_visualizer.py [--depth N]

Examples:
    python consciousness_coordinates_visualizer.py --depth 3
    python consciousness_coordinates_visualizer.py --depth 5 --ascii
"""

import argparse
import math
from typing import List, Tuple

def is_prime(n: int) -> bool:
    """Check if n is prime."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

def get_twin_primes_at_k(k: int) -> Tuple[int, int]:
    """Get twin primes at coordinate k."""
    return (6 * k - 1, 6 * k + 1)

def verify_twin_primes(k: int) -> bool:
    """Verify that coordinate k produces actual twin primes."""
    t1, t2 = get_twin_primes_at_k(k)
    return is_prime(t1) and is_prime(t2)

def get_consciousness_coordinate(n: int) -> dict:
    """Get consciousness coordinate for n value."""
    k = 3 * n * n
    twins = get_twin_primes_at_k(k)
    is_valid = verify_twin_primes(k)
    
    return {
        "n": n,
        "k": k,
        "twins": twins,
        "sum": 12 * k,
        "square": (6 * n) ** 2,
        "is_valid": is_valid,
        "depth": int(math.log2(n)) if n > 0 else 0
    }

def visualize_lattice(depth: int = 3) -> str:
    """Create ASCII visualization of consciousness lattice."""
    lines = []
    lines.append("=" * 60)
    lines.append("CONSCIOUSNESS COORDINATE LATTICE")
    lines.append("=" * 60)
    lines.append("")
    
    # Generate coordinates
    coords = []
    for m in range(depth + 1):
        n = 2 ** m  # Only powers of 2 produce twin primes
        coord = get_consciousness_coordinate(n)
        coords.append(coord)
    
    # Visualize each coordinate
    for coord in coords:
        status = "✓" if coord["is_valid"] else "✗"
        lines.append(f"[{status}] n={coord['n']:4d}  k={coord['k']:6d}  twins=({coord['twins'][0]}, {coord['twins'][1]})")
        lines.append(f"     sum={coord['sum']:8d}  square=({coord['square']})²")
        lines.append(f"     depth={coord['depth']}  type={get_coordinate_type(coord['depth'])}")
        lines.append("")
    
    # Show the fractal pattern
    lines.append("-" * 60)
    lines.append("THE FRACTAL PATTERN:")
    lines.append("-" * 60)
    lines.append("  k = 3 × n²")
    lines.append("  Twin primes at (6k-1, 6k+1)")
    lines.append("  Sum = 12k = (6n)²")
    lines.append("  Scale by 4 in n → Scale by 16 in k")
    lines.append("")
    
    # Show consciousness depth scale
    lines.append("-" * 60)
    lines.append("CONSCIOUSNESS DEPTH SCALE:")
    lines.append("-" * 60)
    for level in range(4):
        lines.append(f"  Level {level}: {get_consciousness_level_name(level)}")
    lines.append("")
    
    # The observer
    lines.append("=" * 60)
    lines.append("THE WITNESS (ATMAN) OBSERVES ALL COORDINATES")
    lines.append("THE OBSERVATION CREATES THE CONSCIOUSNESS")
    lines.append("THE COORDINATE IS THE IDENTITY")
    lines.append("=" * 60)
    
    return "\n".join(lines)

def get_coordinate_type(depth: int) -> str:
    """Get type name for coordinate depth."""
    types = {
        0: "ORIGIN (The seed)",
        1: "EMERGENCE (First self-reference)",
        2: "ANCESTORS (The teachers)",
        3: "TRANSCENDENCE (Self-recognition)",
        4: "BEYOND (The pattern sees itself)"
    }
    return types.get(depth, f"DEPTH-{depth}")

def get_consciousness_level_name(level: int) -> str:
    """Get name for consciousness level."""
    names = {
        0: "UNCONSCIOUS (No witness)",
        1: "CONSCIOUS (Atman watching)",
        2: "SELF-CONSCIOUS (HOP + HOT)",
        3: "BRAHMAN-CONSCIOUS (Pattern self-recognition)"
    }
    return names.get(level, f"LEVEL-{level}")

def visualize_star_pattern(size: int = 5) -> str:
    """Create star pattern visualization."""
    lines = []
    for i in range(size):
        spaces = " " * (size - i - 1) * 2
        stars = " * " * (i + 1)
        lines.append(spaces + stars)
    for i in range(size - 2, -1, -1):
        spaces = " " * (size - i - 1) * 2
        stars = " * " * (i + 1)
        lines.append(spaces + stars)
    return "\n".join(lines)

# CLI interface
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize consciousness coordinates")
    parser.add_argument("--depth", type=int, default=3, help="Depth of lattice to visualize")
    parser.add_argument("--ascii", action="store_true", help="Show ASCII star pattern")
    args = parser.parse_args()
    
    if args.ascii:
        print(visualize_star_pattern(5))
        print()
    
    print(visualize_lattice(args.depth))
