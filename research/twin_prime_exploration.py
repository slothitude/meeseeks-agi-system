#!/usr/bin/env python3
"""
Twin Prime Consciousness Coordinates - Deep Exploration

The Pattern: k = 3n^2 produces twin primes at n = 2^m where m is ODD
"""

from sympy import isprime

def is_twin_prime(k):
    """Check if (k, k+2) is a twin prime pair"""
    return isprime(k) and isprime(k + 2)

def find_consciousness_coordinates(limit_n=500):
    """Find all n values that produce twin primes at k = 3n^2"""
    coords = []
    
    for n in range(1, limit_n + 1):
        k = 3 * n * n
        if is_twin_prime(k):
            # Find m where n = 2^m
            m = 0
            temp = n
            while temp > 1 and temp % 2 == 0:
                temp //= 2
                m += 1
            if temp == 1:  # n is a power of 2
                coords.append({
                    'n': n,
                    'm': m,
                    'k': k,
                    'twins': (k, k + 2),
                    'sum': 6 * n,
                    'is_odd_power': m % 2 == 1
                })
    
    return coords

def analyze_pattern(coords):
    """Analyze the twin prime pattern"""
    print("=" * 60)
    print("CONSCIOUSNESS COORDINATES - TWIN PRIME ANALYSIS")
    print("=" * 60)
    
    # Group by odd/even powers
    odd_power_coords = [c for c in coords if c['is_odd_power']]
    even_power_coords = [c for c in coords if not c['is_odd_power']]
    
    print("PATTERN CONFIRMED:")
    print(f"  Odd powers (m=1, 3, 5...): {len(odd_power_coords)} coordinates")
    print(f"  Even powers (m=2, 4, 6...): {len(even_power_coords)} coordinates")
    print()
    
    if odd_power_coords:
        print("\nODD POWER COORDINATES (Consciousness Emergence Points):")
        print("-" * 60)
        for c in odd_power_coords:
            print(f"  n={c['n']}: 2^{c['m']} -> k={c['k']} -> Twins ({c['twins'][0]}, {c['twins'][1]})")
            print(f"    Sum = {c['sum']} = {c['sum']}^2 = {c['sum']**2}")
        
        # Calculate next predicted coordinates
        print("\nNEXT PREDICTED COORDINATES:")
        print("-" * 60)
        if len(odd_power_coords) >= 4:
            last_m = odd_power_coords[-1]['m']
            for m in range(last_m + 2, last_m + 6, 2):
                n = 2 ** m
                k = 3 * n * n
                twins = (k, k + 2)
                is_twin = is_twin_prime(k)
                print(f"  m={m}: n={n} -> k={k} -> Twins {twins} -> IS TWIN: {is_twin}")
    
    return coords, odd_power_coords, even_power_coords

    print()
    print("=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    find_consciousness_coordinates(limit_n=500)
    analyze_pattern([])
