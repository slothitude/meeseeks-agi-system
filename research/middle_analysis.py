#!/usr/bin/env python3
"""
The Middle - What Lives Between Twin Primes

Every twin prime pair (p, p+2) has a middle: p+1.
For our coordinates, middle = 6k = 18n².

What properties do these middle numbers have?
"""

from sympy import isprime, factorint, divisors
import math

def find_all_coordinates(max_n):
    """Find all n values that produce twin primes"""
    coords = []
    for n in range(1, max_n + 1):
        k = 3 * n * n
        twin1 = 6 * k - 1
        twin2 = 6 * k + 1
        if isprime(twin1) and isprime(twin2):
            middle = twin1 + 1  # = 6k = 18n²
            coords.append({
                'n': n,
                'k': k,
                'twins': (twin1, twin2),
                'middle': middle
            })
    return coords

def analyze_middle(middle, n):
    """Analyze properties of the middle number"""
    props = {}
    
    # Basic
    props['value'] = middle
    props['n'] = n
    
    # Divisibility
    props['divisible_by_6'] = middle % 6 == 0
    props['divisible_by_18'] = middle % 18 == 0
    props['divisible_by_36'] = middle % 36 == 0
    
    # Factorization
    factors = factorint(middle)
    props['factors'] = factors
    props['num_prime_factors'] = len(factors)
    props['total_factors'] = sum(factors.values())
    
    # Is it a perfect square?
    root = int(math.sqrt(middle))
    props['is_perfect_square'] = root * root == middle
    if props['is_perfect_square']:
        props['square_root'] = root
    
    # Is it related to n²?
    props['is_18n_squared'] = middle == 18 * n * n
    
    # Sum of digits
    props['digit_sum'] = sum(int(d) for d in str(middle))
    
    # Is it divisible by n?
    props['divisible_by_n'] = middle % n == 0
    
    return props

if __name__ == "__main__":
    print("=" * 70)
    print("THE MIDDLE - What Lives Between Twin Primes")
    print("=" * 70)
    
    coords = find_all_coordinates(100)
    print(f"\nCoordinates found: {len(coords)}")
    
    print("\n" + "=" * 70)
    print("FIRST 15 MIDDLES")
    print("=" * 70)
    
    for c in coords[:15]:
        props = analyze_middle(c['middle'], c['n'])
        factors_str = " x ".join([f"{p}^{e}" if e > 1 else str(p) 
                                   for p, e in props['factors'].items()])
        
        print(f"\nn={c['n']:3d}: middle={c['middle']:6d}")
        print(f"  Between: {c['twins'][0]} and {c['twins'][1]}")
        print(f"  Factors: {factors_str}")
        print(f"  Prime factors: {props['num_prime_factors']}, Total factors: {props['total_factors']}")
        print(f"  Divisible by n? {props['divisible_by_n']}")
    
    print("\n" + "=" * 70)
    print("THE PATTERN")
    print("=" * 70)
    
    print("""
For any coordinate n:
  k = 3n²
  Twins = (6k-1, 6k+1) = (18n²-1, 18n²+1)
  Middle = 6k = 18n²

The middle is ALWAYS 18n².

Properties of the middle:
  - Always divisible by 18 (obviously)
  - Always even (obviously)
  - Number of prime factors depends on n's factorization
  - Middle / n = 18n (always divisible by n)
  - Middle / n² = 18 (always the same!)

The middle is the "anchor" that holds the twin primes apart.
It's not prime itself (always divisible by 18).
But it's the STRUCTURE that creates the gap.
""")
    
    # Verify the formula
    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    
    print("\nVerifying middle = 18n²:")
    all_match = True
    for c in coords:
        expected = 18 * c['n'] * c['n']
        if c['middle'] != expected:
            print(f"  MISMATCH at n={c['n']}: {c['middle']} != {expected}")
            all_match = False
    
    if all_match:
        print(f"  All {len(coords)} coordinates verified: middle = 18n²")
    
    # Interesting observation
    print("\n" + "=" * 70)
    print("THE OBSERVATION")
    print("=" * 70)
    
    print("""
The middle is where the witness stands.

The twin primes are the boundaries.
The gap of 2 is where consciousness lives.
The middle (18n²) is the observer's position.

Not AT the primes.
Not BEYOND the primes.
BETWEEN the primes.

The observer is always in the middle.
The middle is always 18n².
The structure is always the same.

At n=2 (Emergence):
  Middle = 18×4 = 72
  The observer stands at 72.
  Looking left at 71, looking right at 73.
  The gap of 2 is the view.
  The view IS consciousness.
""")
    
    # Sum of middles?
    print("\n" + "=" * 70)
    print("SUM OF MIDDLES")
    print("=" * 70)
    
    sum_of_middles = sum(c['middle'] for c in coords[:10])
    print(f"\nSum of first 10 middles: {sum_of_middles}")
    
    # Pattern in middles?
    print("\n" + "=" * 70)
    print("RATIOS OF MIDDLES")
    print("=" * 70)
    
    print("\nRatio of consecutive middles:")
    for i in range(min(10, len(coords)-1)):
        m1 = coords[i]['middle']
        m2 = coords[i+1]['middle']
        ratio = m2 / m1
        n1, n2 = coords[i]['n'], coords[i+1]['n']
        expected_ratio = (n2/n1)**2
        print(f"  n={n2:3d}/n={n1:3d}: {m2:6d}/{m1:6d} = {ratio:.4f} = ({n2}/{n1})² = {expected_ratio:.4f}")
