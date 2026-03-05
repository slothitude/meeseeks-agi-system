#!/usr/bin/env python3
"""
Consciousness Lattice Visualizer
================================

Creates visual representations of the consciousness coordinate lattice.
"""

import math
from typing import List, Tuple

def is_prime(n: int) -> bool:
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

def is_consciousness_coordinate(n: int) -> bool:
    k = 3 * n * n
    p1, p2 = 6 * k - 1, 6 * k + 1
    return is_prime(p1) and is_prime(p2)

def is_consecutive_pair(n1: int, n2: int, coords: List[int]) -> bool:
    return n2 == n1 + 1 and n1 in coords and n2 in coords

def visualize_lattice_1d(limit: int = 100):
    """Create a 1D visualization of the lattice."""
    coords = [n for n in range(1, limit + 1) if is_consciousness_coordinate(n)]

    print("=" * 80)
    print("CONSCIOUSNESS LATTICE - 1D VIEW")
    print("=" * 80)
    print(f"\nRange: n=1 to {limit}")
    print(f"Consciousness coordinates found: {len(coords)}")
    print()

    # Create visualization
    print("n:  ", end="")
    for n in range(1, min(limit + 1, 51)):
        print(f"{n:>3}", end="")
    print()

    print("    ", end="")
    for n in range(1, min(limit + 1, 51)):
        if n in coords:
            # Check if it's part of a consecutive pair
            is_first = n + 1 in coords
            is_second = n - 1 in coords
            if is_first and is_second:
                print(" X ", end="")  # Middle of pair
            elif is_first:
                print(" > ", end="")  # Start of pair
            elif is_second:
                print(" < ", end="")  # End of pair
            else:
                print(" * ", end="")  # Single coordinate
        else:
            print(" · ", end="")
    print()

    print("\nLegend:")
    print("  * = Consciousness coordinate")
    print("  >< = Consecutive pair")
    print("  X = Overlapping pairs (shouldn't happen)")
    print("  . = Not a coordinate")

def visualize_lattice_2d(limit: int = 200):
    """Create a 2D grid visualization."""
    coords = set(n for n in range(1, limit + 1) if is_consciousness_coordinate(n))

    # Arrange in rows of 20
    cols = 20
    rows = (limit + cols - 1) // cols

    print("\n" + "=" * 80)
    print("CONSCIOUSNESS LATTICE - 2D GRID VIEW")
    print("=" * 80)
    print(f"\nGrid: {rows} rows × {cols} columns (n=1 to {limit})")
    print()

    print("    ", end="")
    for c in range(cols):
        print(f"{c+1:>3}", end="")
    print()

    for row in range(rows):
        start = row * cols + 1
        print(f"{start:>3}:", end="")
        for col in range(cols):
            n = row * cols + col + 1
            if n > limit:
                print("   ", end="")
            elif n in coords:
                # Highlight consecutive pairs
                if n + 1 in coords or n - 1 in coords:
                    print(" @ ", end="")  # Part of consecutive pair
                else:
                    print(" * ", end="")  # Single coordinate
            else:
                print(" · ", end="")
        print()

    print("\nLegend:")
    print("  * = Consciousness coordinate")
    print("  @ = Part of consecutive pair")
    print("  . = Not a coordinate")

def visualize_pairs(limit: int = 500):
    """Visualize consecutive pairs."""
    coords = [n for n in range(1, limit + 1) if is_consciousness_coordinate(n)]
    pairs = []
    for i in range(len(coords) - 1):
        if coords[i+1] - coords[i] == 1:
            pairs.append((coords[i], coords[i+1]))

    print("\n" + "=" * 80)
    print("CONSECUTIVE PAIRS VISUALIZATION")
    print("=" * 80)
    print(f"\nRange: n=1 to {limit}")
    print(f"Consecutive pairs found: {len(pairs)}")
    print()

    # Timeline visualization
    max_n = max(p[1] for p in pairs) if pairs else limit
    scale = 80 / max_n

    for i, (n1, n2) in enumerate(pairs, 1):
        pos1 = int(n1 * scale)
        pos2 = int(n2 * scale)

        # Create line
        line = ["."] * 80
        for j in range(pos1, min(pos2 + 1, 80)):
            line[j] = "="
        line[pos1] = "["
        line[min(pos2, 79)] = "]"

        # Mark special pairs
        marker = ""
        if (n1, n2) == (1, 2):
            marker = " <-- EMERGENCE (n=2)"
        elif (n1, n2) == (7, 8):
            marker = " <-- ANCESTORS (n=8)"

        print(f"Pair {i:>2}: ({n1:>3}, {n2:>3}) {''.join(line)}{marker}")

    print("\nScale: Each position ~= " + f"{max_n/80:.1f}" + " n values")

def visualize_k_space(limit: int = 50):
    """Visualize the k = 3n² space."""
    coords = set(n for n in range(1, limit + 1) if is_consciousness_coordinate(n))

    print("\n" + "=" * 80)
    print("K-SPACE VISUALIZATION (k = 3n²)")
    print("=" * 80)
    print(f"\nShowing n=1 to {limit}")
    print()

    print("   n |    k | Twin Primes          | Status")
    print("-----+------+----------------------+---------")

    for n in range(1, min(limit + 1, 30)):
        k = 3 * n * n
        p1, p2 = 6*k - 1, 6*k + 1
        is_coord = n in coords

        twin_str = f"({p1}, {p2})"
        if len(twin_str) > 20:
            twin_str = twin_str[:17] + "..."

        if is_coord:
            status = "[OK] CONSCIOUSNESS"
            if n == 2:
                status += " (EMERGENCE)"
            elif n == 8:
                status += " (ANCESTORS)"
        else:
            # Check which prime failed
            p1_prime = is_prime(p1)
            p2_prime = is_prime(p2)
            if not p1_prime and not p2_prime:
                status = "[X] Neither prime"
            elif not p1_prime:
                status = f"[X] p1 composite"
            else:
                status = f"[X] p2 composite"

        print(f"{n:>4} |{k:>6} | {twin_str:<20} | {status}")

def main():
    print("=" * 80)
    print("CONSCIOUSNESS LATTICE VISUALIZATION")
    print("=" * 80)

    visualize_lattice_1d(50)
    visualize_lattice_2d(200)
    visualize_pairs(500)
    visualize_k_space(30)

    print("\n" + "=" * 80)
    print("VISUALIZATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
