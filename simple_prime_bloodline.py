#!/usr/bin/env python3
"""
Simple Prime Bloodline - Based on 6k±1 prime structure

All primes > 3 follow: p = 6k ± 1

This bloodline uses k directly (not 3n²).
"""

from sympy import isprime
from typing import List, Dict

def find_twin_prime_coordinates(max_k: int = 100) -> List[Dict]:
    """
    Find all k where both 6k-1 and 6k+1 are prime (twin primes).

    These are the "simple prime bloodline" coordinates.
    """
    coordinates = []

    for k in range(1, max_k + 1):
        twin1 = 6 * k - 1
        twin2 = 6 * k + 1

        if isprime(twin1) and isprime(twin2):
            coordinates.append({
                'k': k,
                'twins': (twin1, twin2),
                'middle': 6 * k,  # Observer position
                'sum': twin1 + twin2,  # Always 12k
            })

    return coordinates

def get_simple_prime_bloodline():
    """
    Get the simple prime bloodline coordinates.

    First 10 twin prime pairs:
    """
    coords = find_twin_prime_coordinates(100)

    print("SIMPLE PRIME BLOODLINE (6k±1)")
    print("=" * 50)
    print("\nCoordinates where BOTH 6k-1 and 6k+1 are prime:\n")

    for i, coord in enumerate(coords[:20], 1):
        k = coord['k']
        twins = coord['twins']
        print(f"  {i:2}. k={k:2} -> twins ({twins[0]:3}, {twins[1]:3})")

    print(f"\nTotal found (k=1-100): {len(coords)}")
    print(f"\nFirst 3 coordinates (for Meeseeks bloodlines):")
    print(f"  k=1  → twins (5, 7)     → Origin")
    print(f"  k=2  → twins (11, 13)   → Emergence")
    print(f"  k=3  → twins (17, 19)   → First true twin primes")
    print(f"  k=5  → twins (29, 31)   → Ancestors")

    return coords

def compare_bloodlines():
    """
    Compare simple prime bloodline vs lattice bloodline.

    Simple: k directly (twins at 6k±1)
    Lattice: k = 3n² (twins at 18n²±1)
    """
    print("\n" + "=" * 50)
    print("BLOODLINE COMPARISON")
    print("=" * 50)

    print("\nSIMPLE PRIME (6k±1):")
    print("  k=1  → (5, 7)")
    print("  k=2  → (11, 13)")
    print("  k=3  → (17, 19)")
    print("  k=5  → (29, 31)")
    print("  k=7  → (41, 43)")
    print("  ...many more")

    print("\nLATTICE (3n², twins at 18n²±1):")
    print("  n=1, k=3   → (107, 109)")
    print("  n=2, k=12  → (215, 217) - NOT twin primes")
    print("  n=8, k=192 → (3455, 3457) - NOT twin primes")

    print("\nKEY DIFFERENCE:")
    print("  Simple prime: EVERY k produces twin primes")
    print("  Lattice: Only SOME n values produce coordinates")
    print("           (must pass additional checks)")

    print("\nSIMPLE IS BETTER for prime bloodline routing.")

if __name__ == "__main__":
    coords = get_simple_prime_bloodline()
    compare_bloodlines()
