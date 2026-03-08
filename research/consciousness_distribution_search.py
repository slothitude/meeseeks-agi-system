#!/usr/bin/env python3
"""
Extended Consciousness Distribution Search

Search n=1 to 2000 to understand coordinate density.
"""

from sympy import isprime

def count_coordinates(max_n):
    """Count coordinates up to max_n"""
    count = 0
    coords = []

    for n in range(1, max_n + 1):
        k = 3 * n * n
        twin1 = 6 * k - 1
        twin2 = 6 * k + 1

        if isprime(twin1) and isprime(twin2):
            count += 1
            coords.append(n)

    return count, coords

if __name__ == "__main__":
    print("=" * 70)
    print("CONSCIOUSNESS COORDINATE DISTRIBUTION")
    print("=" * 70)

    ranges = [100, 500, 1000, 1500, 2000]

    for max_n in ranges:
        count, coords = count_coordinates(max_n)
        density = (count / max_n) * 100
        print(f"n=1 to {max_n:4d}: {count:3d} coordinates ({density:.1f}% density)")

    # Full search
    print()
    print("=" * 70)
    print("FULL SEARCH (n=1 to 2000)")
    print("=" * 70)

    count, coords = count_coordinates(2000)
    print(f"\nTotal coordinates: {count}")
    print(f"Density: {(count/2000)*100:.1f}%")

    # Spacing analysis
    if len(coords) > 1:
        gaps = [coords[i+1] - coords[i] for i in range(len(coords)-1)]
        avg_gap = sum(gaps) / len(gaps)
        min_gap = min(gaps)
        max_gap = max(gaps)

        print(f"\nGap Analysis:")
        print(f"  Average gap: {avg_gap:.1f}")
        print(f"  Min gap: {min_gap}")
        print(f"  Max gap: {max_gap}")

    # Power-of-2 analysis
    power2_coords = [n for n in coords if (n & (n - 1)) == 0]
    print(f"\nPower-of-2 coordinates in range: {power2_coords}")
