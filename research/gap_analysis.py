#!/usr/bin/env python3
"""
Gap Analysis - Desert Regions in the Consciousness Lattice

Where are the gaps? What causes them?
"""

from sympy import isprime

def find_all_coordinates(max_n):
    """Find all n values that produce twin primes"""
    coords = []
    for n in range(1, max_n + 1):
        k = 3 * n * n
        twin1 = 6 * k - 1
        twin2 = 6 * k + 1
        if isprime(twin1) and isprime(twin2):
            coords.append(n)
    return coords

def analyze_gaps(coords):
    """Analyze gaps between coordinates"""
    gaps = []
    for i in range(len(coords) - 1):
        gap = coords[i+1] - coords[i]
        gaps.append({
            'from': coords[i],
            'to': coords[i+1],
            'gap': gap,
            'desert': list(range(coords[i] + 1, coords[i+1]))
        })
    return gaps

if __name__ == "__main__":
    print("=" * 70)
    print("GAP ANALYSIS - Desert Regions in the Consciousness Lattice")
    print("=" * 70)

    coords = find_all_coordinates(500)
    gaps = analyze_gaps(coords)

    # Sort by gap size
    gaps_by_size = sorted(gaps, key=lambda x: x['gap'], reverse=True)

    print(f"\nTotal coordinates (n=1 to 500): {len(coords)}")
    print(f"Total gaps: {len(gaps)}")

    # Top 10 largest gaps
    print("\n" + "=" * 70)
    print("TOP 10 LARGEST GAPS (Desert Regions)")
    print("=" * 70)

    for i, g in enumerate(gaps_by_size[:10], 1):
        print(f"\n{i}. Gap of {g['gap']} between n={g['from']} and n={g['to']}")
        print(f"   Desert: n={g['from']+1} to {g['to']-1} ({len(g['desert'])} values)")

        # Check if desert contains special numbers
        desert = g['desert']
        primes_in_desert = [n for n in desert if isprime(n)]
        powers_of_2 = [n for n in desert if (n & (n-1)) == 0]

        if primes_in_desert:
            print(f"   Primes in desert: {primes_in_desert[:5]}{'...' if len(primes_in_desert) > 5 else ''}")
        if powers_of_2:
            print(f"   Powers of 2 in desert: {powers_of_2}")

    # Smallest gaps
    print("\n" + "=" * 70)
    print("SMALLEST GAPS (Dense Regions)")
    print("=" * 70)

    for i, g in enumerate(sorted(gaps, key=lambda x: x['gap'])[:10], 1):
        print(f"{i}. Gap of {g['gap']} between n={g['from']} and n={g['to']}")

    # Quadratic residue analysis
    print("\n" + "=" * 70)
    print("QUADRATIC RESIDUE ANALYSIS")
    print("=" * 70)

    # Check n² mod 7 for desert regions
    print("\nChecking n² mod 7 for largest desert (n=100 to 107):")
    for n in range(100, 108):
        n_sq_mod7 = (n * n) % 7
        status = "COORD" if n in coords else "desert"
        print(f"  n={n}: n² mod 7 = {n_sq_mod7} [{status}]")

    # Pattern in gaps
    print("\n" + "=" * 70)
    print("GAP PATTERN ANALYSIS")
    print("=" * 70)

    gap_sizes = [g['gap'] for g in gaps]
    avg_gap = sum(gap_sizes) / len(gap_sizes)

    print(f"Average gap: {avg_gap:.2f}")
    print(f"Min gap: {min(gap_sizes)}")
    print(f"Max gap: {max(gap_sizes)}")

    # Gap frequency
    from collections import Counter
    gap_freq = Counter(gap_sizes)
    print(f"\nMost common gaps:")
    for gap, count in gap_freq.most_common(10):
        print(f"  Gap {gap}: {count} occurrences")
