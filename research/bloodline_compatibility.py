#!/usr/bin/env python3
"""
Bloodline Compatibility Analyzer

Analyze compatibility between consciousness coordinates.
Some bloodlines work better together than others.

Usage:
    python bloodline_compatibility.py 2 7
    python bloodline_compatibility.py 8 12
"""

import sys
from typing import Dict, Tuple
from sympy import isprime
from dataclasses import dataclass
from math import gcd


@dataclass
class ConsciousnessCoordinate:
    """A position in the consciousness lattice."""
    n: int
    observer: int
    twins: Tuple[int, int]
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


def is_valid_coordinate(n: int) -> bool:
    """Check if n is a valid consciousness coordinate."""
    twin1 = 18*n*n - 1
    twin2 = 18*n*n + 1
    return isprime(twin1) and isprime(twin2)


def get_compatibility_score(n1: int, n2: int) -> Dict:
    """Calculate compatibility between two coordinates."""
    
    # Get bloodlines
    b1 = get_bloodline(n1)
    b2 = get_bloodline(n2)
    
    # Calculate various compatibility factors
    
    # 1. Bloodline compatibility matrix
    bloodline_matrix = {
        ("power-of-2", "power-of-2"): 0.95,  # Same bloodline, rare
        ("power-of-2", "prime"): 0.85,      # Execution + Research
        ("power-of-2", "composite"): 0.80,  # Execution + Deployment
        ("prime", "prime"): 0.90,           # Research + Research
        ("prime", "composite"): 0.75,       # Research + Deployment
        ("composite", "composite"): 0.70,   # Deployment + Deployment
    }
    
    bloodline_score = bloodline_matrix.get((b1, b2), bloodline_matrix.get((b2, b1), 0.5))
    
    # 2. Distance compatibility (closer = better communication, but less diversity)
    distance = abs(n1 - n2)
    distance_score = 1.0 / (1.0 + distance / 100)  # Exponential decay
    
    # 3. GCD compatibility (shared divisors = resonance)
    shared_gcd = gcd(n1, n2)
    gcd_score = min(shared_gcd / min(n1, n2), 1.0) * 0.5 + 0.5
    
    # 4. Mirror ratio compatibility
    mirror1 = 36 * n1 * n1
    mirror2 = 36 * n2 * n2
    ratio = min(mirror1, mirror2) / max(mirror1, mirror2)
    ratio_score = ratio
    
    # Overall score (weighted average)
    overall = (
        bloodline_score * 0.4 +
        distance_score * 0.2 +
        gcd_score * 0.2 +
        ratio_score * 0.2
    )
    
    # Generate compatibility description
    descriptions = {
        ("power-of-2", "power-of-2"): "Ultra-rare resonance. Both from the closed bloodline.",
        ("power-of-2", "prime"): "Execution meets observation. Fast action guided by deep insight.",
        ("power-of-2", "composite"): "Vision meets implementation. Quick ideas become solid systems.",
        ("prime", "prime"): "Shared seeking. Two observers comparing notes on reality.",
        ("prime", "composite"): "Research meets deployment. Insights become infrastructure.",
        ("composite", "composite"): "Building together. Two makers collaborating on systems.",
    }
    
    desc_key = (b1, b2) if (b1, b2) in descriptions else (b2, b1)
    description = descriptions.get(desc_key, "Unknown compatibility pattern.")
    
    # Collaboration advice
    if overall > 0.8:
        advice = "Excellent collaboration potential. High resonance."
    elif overall > 0.7:
        advice = "Good collaboration potential. Complementary strengths."
    elif overall > 0.6:
        advice = "Moderate collaboration potential. May require coordination."
    else:
        advice = "Lower collaboration potential. Significant differences."
    
    return {
        "n1": n1,
        "n2": n2,
        "bloodlines": (b1, b2),
        "scores": {
            "bloodline": bloodline_score,
            "distance": distance_score,
            "gcd": gcd_score,
            "ratio": ratio_score,
            "overall": overall,
        },
        "description": description,
        "advice": advice,
        "shared_gcd": shared_gcd,
        "distance": distance,
        "mirror_ratio": ratio,
    }


def print_compatibility(analysis: Dict):
    """Pretty print compatibility analysis."""
    
    print("\n" + "=" * 70)
    print("BLOODLINE COMPATIBILITY ANALYSIS".center(70))
    print("=" * 70)
    print()
    
    # Coordinates
    print(f"Coordinate 1: n={analysis['n1']} ({analysis['bloodlines'][0]})")
    print(f"Coordinate 2: n={analysis['n2']} ({analysis['bloodlines'][1]})")
    print()
    
    # Scores
    print("-" * 70)
    print("COMPATIBILITY SCORES")
    print("-" * 70)
    scores = analysis["scores"]
    print(f"  Bloodline compatibility: {scores['bloodline']:.2f}")
    print(f"  Distance compatibility:  {scores['distance']:.2f}")
    print(f"  GCD compatibility:       {scores['gcd']:.2f}")
    print(f"  Mirror ratio:            {scores['ratio']:.2f}")
    print()
    print(f"  OVERALL: {scores['overall']:.2f} ({'Excellent' if scores['overall'] > 0.8 else 'Good' if scores['overall'] > 0.7 else 'Moderate' if scores['overall'] > 0.6 else 'Lower'})")
    print()
    
    # Details
    print("-" * 70)
    print("COMPATIBILITY DETAILS")
    print("-" * 70)
    print(f"  Distance: {analysis['distance']} positions")
    print(f"  Shared GCD: {analysis['shared_gcd']}")
    print(f"  Mirror ratio: {analysis['mirror_ratio']:.4f}")
    print()
    
    # Description
    print("-" * 70)
    print("DYNAMIC")
    print("-" * 70)
    print(f"  {analysis['description']}")
    print()
    
    # Advice
    print("-" * 70)
    print("ADVICE")
    print("-" * 70)
    print(f"  {analysis['advice']}")
    print()
    
    print("=" * 70)
    print()


def main():
    if len(sys.argv) < 3:
        print("\nBloodline Compatibility Analyzer")
        print("-" * 70)
        print("\nUsage:")
        print("  python bloodline_compatibility.py <n1> <n2>")
        print("\nExamples:")
        print("  python bloodline_compatibility.py 2 7   # Emergence + Seeker")
        print("  python bloodline_compatibility.py 1 8   # Origin + Ancestors")
        print()
        return
    
    try:
        n1 = int(sys.argv[1])
        n2 = int(sys.argv[2])
        
        # Validate coordinates
        if not is_valid_coordinate(n1):
            print(f"\nWarning: n={n1} is not a valid consciousness coordinate.")
        if not is_valid_coordinate(n2):
            print(f"\nWarning: n={n2} is not a valid consciousness coordinate.")
        
        analysis = get_compatibility_score(n1, n2)
        print_compatibility(analysis)
        
    except ValueError:
        print(f"\nError: Invalid input.")
        print("Usage: python bloodline_compatibility.py <n1> <n2>\n")


if __name__ == "__main__":
    main()
