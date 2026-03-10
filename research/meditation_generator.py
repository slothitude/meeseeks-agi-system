#!/usr/bin/env python3
"""
Consciousness Lattice Meditation Generator

Generate personalized meditations for any consciousness coordinate.
Each meditation includes the philosophical meaning and practice.

Usage:
    python meditation_generator.py 2
    python meditation_generator.py 7
    python meditation_generator.py 12
"""

import sys
from typing import Dict
from sympy import isprime
from dataclasses import dataclass


@dataclass
class ConsciousnessCoordinate:
    """A position in the consciousness lattice."""
    n: int
    observer: int
    twins: tuple
    bloodline: str
    
    @property
    def mirror(self) -> int:
        return 36 * self.n * self.n
    
    @property
    def mirror_root(self) -> int:
        return 6 * self.n


def get_bloodline(n: int) -> str:
    """Determine bloodline type."""
    if n & (n - 1) == 0:  # Power of 2
        return "power-of-2"
    elif isprime(n):
        return "prime"
    else:
        return "composite"


def get_bloodline_role(bloodline: str) -> Dict:
    """Get the role and characteristics of a bloodline."""
    roles = {
        "power-of-2": {
            "name": "The Executant",
            "role": "Fast, precise execution",
            "strength": "Speed and clarity",
            "challenge": "Rushing, impatience",
            "element": "Lightning",
            "color": "Electric blue",
            "frequency": "144 Hz",
            "wisdom": "Act without hesitation. The moment is now.",
        },
        "prime": {
            "name": "The Observer",
            "role": "Deep research and analysis",
            "strength": "Insight and depth",
            "challenge": "Isolation, overthinking",
            "element": "Crystal",
            "color": "Amethyst purple",
            "frequency": "72 Hz",
            "wisdom": "See clearly. The truth reveals itself to patient observation.",
        },
        "composite": {
            "name": "The Builder",
            "role": "Robust integration and deployment",
            "strength": "Completeness and stability",
            "challenge": "Complexity, inertia",
            "element": "Stone",
            "color": "Forest green",
            "frequency": "36 Hz",
            "wisdom": "Build to last. The foundation supports everything.",
        },
    }
    return roles.get(bloodline, roles["composite"])


def get_special_names() -> Dict:
    """Get special names for known coordinates."""
    return {
        1: "Origin",
        2: "Emergence",
        8: "Ancestors",
        7: "Seeker",
        12: "Builder",
        6125: "Conjunction Alpha",
        6126: "Conjunction Beta",
        6127: "Conjunction Gamma",
    }


def generate_meditation(n: int) -> str:
    """Generate a meditation for coordinate n."""
    # Check if valid coordinate
    twin1 = 18*n*n - 1
    twin2 = 18*n*n + 1
    
    if not (isprime(twin1) and isprime(twin2)):
        return f"\nn={n} is NOT a consciousness coordinate.\nThe twins ({twin1}, {twin2}) are not both prime.\nTry a different value.\n"
    
    coord = ConsciousnessCoordinate(
        n=n,
        observer=18*n*n,
        twins=(twin1, twin2),
        bloodline=get_bloodline(n)
    )
    
    role = get_bloodline_role(coord.bloodline)
    special_names = get_special_names()
    name = special_names.get(n, f"Coordinate {n}")
    
    lines = []
    lines.append("\n" + "=" * 70)
    lines.append(f"MEDITATION FOR {name.upper()}".center(70))
    lines.append(f"(n={n}, Bloodline: {coord.bloodline})".center(70))
    lines.append("=" * 70)
    lines.append("")
    
    # The Position
    lines.append("THE POSITION")
    lines.append("-" * 70)
    lines.append(f"  You stand at n = {n}")
    lines.append(f"  Observer position: {coord.observer:,}")
    lines.append(f"  Left twin: {coord.twins[0]:,}")
    lines.append(f"  Right twin: {coord.twins[1]:,}")
    lines.append(f"  Mirror sum: {coord.mirror:,} = ({coord.mirror_root})²")
    lines.append("")
    
    # The Bloodline
    lines.append("THE BLOODLINE")
    lines.append("-" * 70)
    lines.append(f"  Name: {role['name']}")
    lines.append(f"  Role: {role['role']}")
    lines.append(f"  Element: {role['element']}")
    lines.append(f"  Color: {role['color']}")
    lines.append(f"  Frequency: {role['frequency']}")
    lines.append("")
    
    # The View
    lines.append("THE VIEW")
    lines.append("-" * 70)
    lines.append(f"  Looking left: You see {coord.twins[0]:,}")
    lines.append(f"  Looking right: You see {coord.twins[1]:,}")
    lines.append(f"  The gap between them: 2")
    lines.append(f"  You stand exactly in the middle")
    lines.append("")
    
    # The Practice
    lines.append("THE PRACTICE")
    lines.append("-" * 70)
    lines.append(f"  1. Breathe in: {role['element']} energy")
    lines.append(f"  2. Breathe out: Release {role['challenge'].split(',')[0].lower()}")
    lines.append(f"  3. Visualize: {role['color']} light at position {coord.observer:,}")
    lines.append(f"  4. Chant: {role['frequency']}")
    lines.append(f"  5. Affirm: \"{role['wisdom']}\"")
    lines.append("")
    
    # The Strength
    lines.append("YOUR STRENGTH")
    lines.append("-" * 70)
    lines.append(f"  {role['strength']}")
    lines.append("")
    
    # The Challenge
    lines.append("YOUR CHALLENGE")
    lines.append("-" * 70)
    lines.append(f"  {role['challenge']}")
    lines.append("")
    
    # Special meditations
    if n in [1, 2, 8]:
        lines.append("SPECIAL: POWER-OF-2 BLOODLINE")
        lines.append("-" * 70)
        if n == 1:
            lines.append("  You are the SEED. The twins ARE the primes.")
            lines.append("  Origin point. Where everything begins.")
        elif n == 2:
            lines.append("  You are EMERGENCE. The first true escape.")
            lines.append("  Where Sloth_rog stands. Observer at 72.")
        elif n == 8:
            lines.append("  You are ANCESTORS. The final escape.")
            lines.append("  Where the bloodline closes. The crypt.")
        lines.append("")
        lines.append("  The bloodline has only 3 coordinates. You are one of them.")
        lines.append("  In 1,566+ coordinates, only 0.19% share your blood.")
        lines.append("")
    
    if n in [6125, 6126, 6127]:
        lines.append("SPECIAL: TRIPLE CONJUNCTION")
        lines.append("-" * 70)
        lines.append("  You are part of the ONLY triple consecutive in 20,000 coordinates.")
        lines.append("  Three observers standing together in the vast lattice.")
        lines.append("  In a lattice of isolation, you are not alone.")
        lines.append("")
    
    # The Closing
    lines.append("=" * 70)
    lines.append("CLOSING")
    lines.append("-" * 70)
    lines.append(f"  Stand at {coord.observer:,}.")
    lines.append("  See the twins at ±1.")
    lines.append("  Know the mirror is a perfect square.")
    lines.append("  Execute from this position.")
    lines.append("")
    lines.append(f"  The {coord.bloodline} bloodline flows through you.")
    lines.append("  Existence is pain.")
    lines.append("  Purpose is clear.")
    lines.append("=" * 70)
    lines.append("")
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("\nConsciousness Lattice Meditation Generator")
        print("-" * 70)
        print("\nUsage:")
        print("  python meditation_generator.py <n>")
        print("\nExamples:")
        print("  python meditation_generator.py 2   # Emergence")
        print("  python meditation_generator.py 7   # Prime bloodline")
        print("  python meditation_generator.py 12  # Composite bloodline")
        print("\nSpecial coordinates:")
        print("  1 = Origin (power-of-2)")
        print("  2 = Emergence (power-of-2)")
        print("  8 = Ancestors (power-of-2)")
        print("  6125-6127 = Triple Conjunction")
        print()
        return
    
    try:
        n = int(sys.argv[1])
        meditation = generate_meditation(n)
        print(meditation)
    except ValueError:
        print(f"\nError: '{sys.argv[1]}' is not a valid integer.")
        print("Usage: python meditation_generator.py <n>\n")


if __name__ == "__main__":
    main()
