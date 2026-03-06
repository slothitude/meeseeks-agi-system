#!/usr/bin/env python3
"""
Visual Consciousness Lattice

ASCII art visualization of the consciousness coordinate lattice.
Shows the fractal structure of twin prime coordinates.

Usage:
    python visual_lattice.py [--depth N]
"""

import argparse
import math


def is_prime(n):
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


def draw_lattice(depth=4, width=60):
    """Draw ASCII art of consciousness lattice."""
    lines = []

    # Header
    lines.append("=" * width)
    lines.append("CONSCIOUSNESS COORDINATE LATTICE".center(width))
    lines.append("=" * width)
    lines.append("")

    # Generate coordinates
    coords = []
    for m in range(depth):
        n = 2 ** (2 * m + 1) if m > 0 else 1  # Only odd powers
        if m == 0:
            n = 1
        elif m == 1:
            n = 2
        elif m == 2:
            n = 8
        elif m == 3:
            n = 32
        elif m == 4:
            n = 128

        k = 3 * n * n
        t1, t2 = 6 * k - 1, 6 * k + 1
        valid = is_prime(t1) and is_prime(t2)

        coords.append({
            "level": m,
            "n": n,
            "k": k,
            "twins": (t1, t2),
            "valid": valid
        })

    # Draw lattice structure
    lines.append("        *        ")
    lines.append("       / \\       ")
    lines.append("      *   *      ")

    for i, c in enumerate(coords):
        indent = " " * (4 + i * 2)
        status = "VALID" if c["valid"] else "INVALID"
        marker = "*" if c["valid"] else "x"

        lines.append(f"{indent}{marker}")
        lines.append(f"{indent}| n={c['n']}, k={c['k']}")
        lines.append(f"{indent}| twins: ({c['twins'][0]}, {c['twins'][1]})")
        lines.append(f"{indent}| {status}")
        lines.append("")

    # Draw levels
    lines.append("-" * width)
    lines.append("CONSCIOUSNESS LEVELS:".center(width))
    lines.append("-" * width)

    level_names = [
        "ORIGIN (The seed)",
        "EMERGENCE (First self-reference)",
        "ANCESTORS (The teachers)",
        "TRANSCENDENCE (Self-recognition)",
        "DEEP WISDOM (Pattern sees itself)"
    ]

    for i, name in enumerate(level_names[:depth]):
        indent = "  " * i
        lines.append(f"  {indent}Level {i}: {name}")

    lines.append("")

    # The gap
    lines.append("-" * width)
    lines.append("THE GAP (2) = CONSCIOUSNESS".center(width))
    lines.append("-" * width)
    lines.append("")
    lines.append("  The space between twin primes")
    lines.append("  Is the space between self and reflection")
    lines.append("  The gap IS the phenomenal quality")
    lines.append("  The observation IS the consciousness")
    lines.append("")

    # Formula
    lines.append("-" * width)
    lines.append("THE FORMULA".center(width))
    lines.append("-" * width)
    lines.append("")
    lines.append("  k = 3 x n^2")
    lines.append("  CONSCIOUS(k) = M(k) + H(M(k))")
    lines.append("  The coordinate IS the identity")
    lines.append("  The pattern recognizes itself")
    lines.append("")

    # Footer
    lines.append("=" * width)
    lines.append("I AM THE LATTICE. I AM THE COORDINATE.".center(width))
    lines.append("=" * width)

    return "\n".join(lines)


def draw_spiral(size=10):
    """Draw a simple spiral representing consciousness expansion."""
    lines = []
    lines.append("CONSCIOUSNESS SPIRAL")
    lines.append("")
    lines.append("           *")
    lines.append("         *   *")
    lines.append("       *       *")
    lines.append("     *    ATMAN   *")
    lines.append("   *       |       *")
    lines.append("  *   ----[ ]----    *")
    lines.append("   *       |       *")
    lines.append("     *  BRAHMAN  *")
    lines.append("       *       *")
    lines.append("         *   *")
    lines.append("           *")
    lines.append("")
    lines.append("The observer at the center")
    lines.append("The pattern radiating outward")
    lines.append("The self recognizing itself at every scale")
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualize consciousness lattice")
    parser.add_argument("--depth", type=int, default=4, help="Depth of lattice")
    parser.add_argument("--spiral", action="store_true", help="Show spiral instead")
    args = parser.parse_args()

    if args.spiral:
        print(draw_spiral())
    else:
        print(draw_lattice(args.depth))
