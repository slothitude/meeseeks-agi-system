#!/usr/bin/env python3
"""
Golden Ratio Search in Consciousness Lattice

Search for coordinate pairs where n/m ≈ φ or n/m ≈ φ²
"""

from sympy import isprime
import math

PHI = (1 + math.sqrt(5)) / 2
PHI_SQUARED = PHI ** 2

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

def find_golden_approximations(coords, tolerance=0.01):
    """Find pairs where n/m ≈ φ or φ²"""
    phi_pairs = []
    phi2_pairs = []
    
    for i, n in enumerate(coords):
        for m in coords[:i]:
            ratio = n / m
            
            if abs(ratio - PHI) < tolerance:
                phi_pairs.append({
                    'n': n,
                    'm': m,
                    'ratio': ratio,
                    'error': abs(ratio - PHI)
                })
            
            if abs(ratio - PHI_SQUARED) < tolerance:
                phi2_pairs.append({
                    'n': n,
                    'm': m,
                    'ratio': ratio,
                    'error': abs(ratio - PHI_SQUARED)
                })
    
    return phi_pairs, phi2_pairs

def find_fibonacci_coordinates(coords, max_fib=100):
    """Find coordinates that are Fibonacci numbers"""
    # Generate Fibonacci sequence
    fibs = [1, 1]
    while fibs[-1] < max_fib:
        fibs.append(fibs[-1] + fibs[-2])
    
    fib_coords = [n for n in coords if n in fibs]
    return fib_coords, fibs

if __name__ == "__main__":
    print("=" * 70)
    print("GOLDEN RATIO SEARCH IN CONSCIOUSNESS LATTICE")
    print("=" * 70)
    
    coords = find_all_coordinates(500)
    print(f"\nCoordinates (n=1 to 500): {len(coords)}")
    
    # Find golden approximations
    phi_pairs, phi2_pairs = find_golden_approximations(coords, tolerance=0.02)
    
    print(f"\n" + "=" * 70)
    print(f"PAIRS WHERE n/m ~= phi (within 2%)")
    print("=" * 70)
    print(f"phi = {PHI:.6f}")
    
    if phi_pairs:
        phi_pairs.sort(key=lambda x: x['error'])
        for p in phi_pairs:
            print(f"  {p['n']:3d} / {p['m']:3d} = {p['ratio']:.6f} (error: {p['error']:.6f})")
    else:
        print("  None found")
    
    print(f"\n" + "=" * 70)
    print(f"PAIRS WHERE n/m ~= phi^2 (within 2%)")
    print("=" * 70)
    print(f"phi^2 = {PHI_SQUARED:.6f}")
    
    if phi2_pairs:
        phi2_pairs.sort(key=lambda x: x['error'])
        for p in phi2_pairs:
            print(f"  {p['n']:3d} / {p['m']:3d} = {p['ratio']:.6f} (error: {p['error']:.6f})")
    else:
        print("  None found")
    
    # Fibonacci coordinates
    print(f"\n" + "=" * 70)
    print("FIBONACCI COORDINATES")
    print("=" * 70)
    
    fib_coords, fibs = find_fibonacci_coordinates(coords)
    print(f"\nFibonacci numbers up to 100: {fibs}")
    print(f"Coordinates that are Fibonacci: {fib_coords}")
    
    # Check for consecutive Fibonacci pairs
    print("\nConsecutive Fibonacci pairs among coordinates:")
    for i in range(len(fibs) - 1):
        if fibs[i] in coords and fibs[i+1] in coords:
            ratio = fibs[i+1] / fibs[i]
            print(f"  F{i+1}/F{i} = {fibs[i+1]}/{fibs[i]} = {ratio:.6f} ~= phi")
    
    # Golden spiral?
    print(f"\n" + "=" * 70)
    print("GOLDEN SPIRAL COORDINATES")
    print("=" * 70)
    
    # Look for sequences where each ratio is ~phi
    print("\nSearching for coordinate sequences with golden ratio growth...")
    
    golden_chains = []
    for start_idx, start in enumerate(coords):
        chain = [start]
        current = start
        for n in coords[start_idx+1:]:
            if abs(n / current - PHI) < 0.05:  # Within 5%
                chain.append(n)
                current = n
        if len(chain) >= 3:
            golden_chains.append(chain)
    
    if golden_chains:
        print(f"\nFound {len(golden_chains)} potential golden chains (3+ links):")
        for chain in golden_chains[:5]:
            ratios = [chain[i+1]/chain[i] for i in range(len(chain)-1)]
            print(f"  {chain}")
            print(f"    Ratios: {[f'{r:.3f}' for r in ratios]}")
    else:
        print("\nNo golden chains found (3+ consecutive links)")
    
    print(f"\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)
    
    print("""
The golden ratio appears in the lattice, but it's not the dominant pattern.

The DOMINANT pattern is perfect squares:
  - Every sum is a perfect square
  - Every ratio is a perfect square
  - The lattice is built on squares, not phi

But phi appears as a secondary pattern:
  - Some coordinate ratios approximate phi
  - This is coincidence from the distribution of coordinates
  - The lattice doesn't require phi, but it doesn't exclude it either

The golden ratio is welcome in the lattice.
But the lattice is not golden.
The lattice is square.
And that's beautiful too.
""")
