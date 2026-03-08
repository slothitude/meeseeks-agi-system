#!/usr/bin/env python3
"""
Fractal Mirror Analysis - Ratios Between Coordinates

Since sum = (6n)², the ratio of any two sums is (n/m)².
This creates a fractal structure of perfect square ratios.
"""

from sympy import isprime
import math

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

def is_perfect_square(n):
    """Check if n is a perfect square"""
    if n < 0:
        return False
    root = int(math.sqrt(n))
    return root * root == n

def analyze_ratios(coords):
    """Analyze ratios between coordinate sums"""
    ratios = []
    
    for i, n in enumerate(coords):
        for m in coords[:i]:  # Only pairs where n > m
            # Ratio of sums = (n/m)²
            numerator = n * n
            denominator = m * m
            
            # Check if it reduces to a perfect square ratio
            from math import gcd
            g = gcd(numerator, denominator)
            simplified_num = numerator // g
            simplified_den = denominator // g
            
            ratios.append({
                'n': n,
                'm': m,
                'ratio': (numerator, denominator),
                'simplified': (simplified_num, simplified_den),
                'is_square_ratio': is_perfect_square(simplified_num) and is_perfect_square(simplified_den)
            })
    
    return ratios

if __name__ == "__main__":
    print("=" * 70)
    print("FRACTAL MIRROR ANALYSIS - Ratios Between Coordinates")
    print("=" * 70)
    
    coords = find_all_coordinates(100)  # First 18 coordinates
    ratios = analyze_ratios(coords)
    
    print(f"\nCoordinates: {coords}")
    print(f"Total pairs: {len(ratios)}")
    
    # Check if all ratios are square ratios
    square_ratios = [r for r in ratios if r['is_square_ratio']]
    print(f"Square ratios: {len(square_ratios)}/{len(ratios)} (100% expected)")
    
    print("\n" + "=" * 70)
    print("EXAMPLE RATIOS")
    print("=" * 70)
    
    # Show some interesting ratios
    examples = [
        (2, 1),   # k=12 / k=3
        (8, 2),   # k=192 / k=12
        (8, 1),   # k=192 / k=3
        (12, 8),  # k=432 / k=192
        (15, 12), # k=675 / k=432
    ]
    
    for n, m in examples:
        if n in coords and m in coords:
            sum_n = (6 * n) ** 2
            sum_m = (6 * m) ** 2
            ratio = sum_n / sum_m
            expected_ratio = (n / m) ** 2
            
            print(f"\nn={n} / m={m}:")
            print(f"  sum({n}) / sum({m}) = {sum_n} / {sum_m}")
            print(f"  Ratio = {ratio:.4f} = ({n}/{m})² = {expected_ratio:.4f}")
            print(f"  This is (n/m)^2 = ({n/m:.4f})^2")
    
    print("\n" + "=" * 70)
    print("THE FRACTAL PATTERN")
    print("=" * 70)
    
    print("""
Since sum = (6n)² for every coordinate:

  sum(n) / sum(m) = (6n)² / (6m)² = (n/m)²

EVERY ratio between coordinate sums is a perfect square ratio!

This creates a FRACTAL structure:
  - Each coordinate is a mirror (sum = perfect square)
  - Each ratio is a mirror (ratio = perfect square)
  - The pattern repeats at every scale

The lattice is fractally mirrors all the way down.
""")
    
    # Power-of-2 bloodline ratios
    print("\n" + "=" * 70)
    print("POWER-OF-2 BLOODLINE RATIOS")
    print("=" * 70)
    
    power2_coords = [n for n in coords if (n & (n-1)) == 0]
    print(f"\nPower-of-2 coordinates in range: {power2_coords}")
    
    if len(power2_coords) >= 2:
        print("\nRatios within power-of-2 bloodline:")
        for i in range(len(power2_coords)):
            for j in range(i):
                n, m = power2_coords[i], power2_coords[j]
                ratio = (n / m) ** 2
                # Express as power of 4
                power = int(math.log2(n/m) * 2) if (n/m) == int(n/m) else None
                print(f"  {n}/{m}: ratio = {ratio} = 2^{int(math.log2(ratio)) if is_perfect_square(ratio) else '?'}")
    
    print("\n" + "=" * 70)
    print("THE GOLDEN RATIO?")
    print("=" * 70)
    
    # Check if any ratios approximate phi
    phi = (1 + math.sqrt(5)) / 2
    print(f"\nGolden ratio phi ~= {phi:.6f}")
    print(f"phi^2 ~= {phi**2:.6f}")
    
    close_ratios = []
    for r in ratios:
        ratio_val = r['ratio'][0] / r['ratio'][1]
        if abs(ratio_val - phi) < 0.01 or abs(ratio_val - phi**2) < 0.01:
            close_ratios.append(r)
    
    if close_ratios:
        print(f"\nRatios close to phi or phi^2:")
        for r in close_ratios[:5]:
            ratio_val = r['ratio'][0] / r['ratio'][1]
            target = "phi" if abs(ratio_val - phi) < 0.01 else "phi^2"
            print(f"  {r['n']}/{r['m']}: {ratio_val:.6f} ~= {target}")
    else:
        print(f"\nNo ratios close to phi or phi^2 (within 1%)")
        print("This is expected - the lattice is built on squares, not the golden ratio")
