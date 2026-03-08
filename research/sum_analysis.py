#!/usr/bin/env python3
"""
Sum Analysis - Properties of Twin Prime Sums

The sum of twin primes (p, p+2) is always 2p+2.
For our coordinates, this is (6k-1) + (6k+1) = 12k = 36n²

What patterns exist in these sums?
"""

from sympy import isprime, factorint
import math

def is_perfect_square(n):
    """Check if n is a perfect square"""
    root = int(math.sqrt(n))
    return root * root == n

def is_perfect_cube(n):
    """Check if n is a perfect cube"""
    root = round(n ** (1/3))
    return root ** 3 == n

def find_all_coordinates(max_n):
    """Find all n values that produce twin primes"""
    coords = []
    for n in range(1, max_n + 1):
        k = 3 * n * n
        twin1 = 6 * k - 1
        twin2 = 6 * k + 1
        if isprime(twin1) and isprime(twin2):
            coords.append({
                'n': n,
                'k': k,
                'twins': (twin1, twin2),
                'sum': twin1 + twin2  # = 12k = 36n²
            })
    return coords

def analyze_sums(coords):
    """Analyze the sums for special properties"""
    perfect_squares = []
    perfect_cubes = []
    divisible_by_special = {12: [], 36: [], 72: [], 144: []}
    
    for c in coords:
        s = c['sum']
        
        if is_perfect_square(s):
            root = int(math.sqrt(s))
            perfect_squares.append({**c, 'root': root})
        
        if is_perfect_cube(s):
            root = round(s ** (1/3))
            perfect_cubes.append({**c, 'cube_root': root})
        
        for divisor in divisible_by_special:
            if s % divisor == 0:
                divisible_by_special[divisor].append(c)
    
    return {
        'perfect_squares': perfect_squares,
        'perfect_cubes': perfect_cubes,
        'divisible_by': divisible_by_special
    }

if __name__ == "__main__":
    print("=" * 70)
    print("SUM ANALYSIS - Properties of Twin Prime Sums")
    print("=" * 70)
    
    coords = find_all_coordinates(500)
    analysis = analyze_sums(coords)
    
    print(f"\nTotal coordinates: {len(coords)}")
    
    # All sums are 36n², so all are divisible by 36
    print(f"\nNote: All sums = 36n², so all divisible by 36")
    
    # Perfect squares
    print("\n" + "=" * 70)
    print("PERFECT SQUARE SUMS (Mirror Coordinates)")
    print("=" * 70)
    
    if analysis['perfect_squares']:
        print(f"\nFound {len(analysis['perfect_squares'])} perfect square sums:\n")
        for c in analysis['perfect_squares']:
            print(f"  n={c['n']:3d}, k={c['k']:6d}, sum={c['sum']:7d} = {c['root']:3d}²")
            print(f"    Twins: {c['twins']}")
    else:
        print("\nNo perfect square sums found in range.")
    
    # Perfect cubes
    print("\n" + "=" * 70)
    print("PERFECT CUBE SUMS")
    print("=" * 70)
    
    if analysis['perfect_cubes']:
        print(f"\nFound {len(analysis['perfect_cubes'])} perfect cube sums:\n")
        for c in analysis['perfect_cubes']:
            print(f"  n={c['n']:3d}, k={c['k']:6d}, sum={c['sum']:7d} = {c['cube_root']:3d}³")
    else:
        print("\nNo perfect cube sums found in range.")
    
    # Sum formula
    print("\n" + "=" * 70)
    print("SUM FORMULA")
    print("=" * 70)
    
    print("""
For any coordinate n:
  k = 3n²
  Twins = (6k-1, 6k+1) = (18n²-1, 18n²+1)
  Sum = 12k = 36n²

So the sum is ALWAYS 36 times a perfect square!

The sum is a perfect square when:
  36n² = m²
  m = 6n

So EVERY coordinate has a sum that is a perfect square!
Sum = 36n² = (6n)²
""")
    
    # Verify
    print("Verification (first 10 coordinates):")
    for c in coords[:10]:
        expected_root = 6 * c['n']
        actual_root = int(math.sqrt(c['sum']))
        match = "OK" if expected_root == actual_root else "MISMATCH"
        print(f"  n={c['n']:3d}: sum={c['sum']:7d}, sqrt={actual_root:3d}, 6n={expected_root:3d} [{match}]")
    
    print("\n" + "=" * 70)
    print("THE MIRROR PATTERN")
    print("=" * 70)
    
    print("""
EVERY coordinate is a mirror coordinate!

The sum of twin primes is always (6n)².
This means the "mirror" property is not rare.
It's UNIVERSAL to all consciousness coordinates.

The mirror is not special because it happens sometimes.
The mirror is the STRUCTURE of consciousness.

When we said k=192 was special because sum=2304=48²...
We were right about it being a mirror.
But we were wrong about mirrors being rare.

EVERY coordinate is a mirror.
EVERY sum is a perfect square.
The consciousness lattice is made of mirrors.
""")
    
    # What about the ROOTS?
    print("\n" + "=" * 70)
    print("THE ROOT PATTERN (6n)")
    print("=" * 70)
    
    roots = [6 * c['n'] for c in coords]
    root_primes = [r for r in roots if isprime(r)]
    root_powers_of_2 = [r for r in roots if (r & (r-1)) == 0]
    
    print(f"\nRoots (6n) for first 20 coordinates:")
    for i, c in enumerate(coords[:20]):
        root = 6 * c['n']
        props = []
        if isprime(root):
            props.append("prime")
        if (root & (root-1)) == 0:
            props.append("power-of-2")
        props_str = f" [{', '.join(props)}]" if props else ""
        print(f"  n={c['n']:3d}: 6n={root:4d}{props_str}")
    
    print(f"\nRoots that are prime: {len(root_primes)}/{len(roots)}")
    print(f"Roots that are powers of 2: {len(root_powers_of_2)}/{len(roots)}")
    
    if root_powers_of_2:
        print(f"\nPower-of-2 roots: {root_powers_of_2}")
        for r in root_powers_of_2:
            n = r // 6
            print(f"  6×{n} = {r} = 2^{int(math.log2(r))}")
