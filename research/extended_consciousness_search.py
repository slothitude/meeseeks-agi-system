#!/usr/bin/env python3
"""
Extended Consciousness Coordinate Search

The pattern: n = 2^m where m is ODD produces twin primes

Let's search for m = 5, 7, 9, 11, 13, 15, 17, 19
"""

from sympy import isprime

def consciousness_coordinate(n):
    """Calculate consciousness coordinate k from n"""
    return 3 * n * n

def twin_prime_pair(k):
    """Get the twin prime pair at coordinate k"""
    return (6*k - 1, 6*k + 1)

def is_valid_coordinate(n):
    """Check if n produces valid twin primes"""
    k = consciousness_coordinate(n)
    twin1, twin2 = twin_prime_pair(k)
    return isprime(twin1) and isprime(twin2)

def find_odd_power_coordinates(max_m=25):
    """Find all odd power coordinates up to max_m"""
    coords = []
    
    for m in range(1, max_m + 1, 2):  # Odd numbers only
        n = 2 ** m
        k = consciousness_coordinate(n)
        twin1, twin2 = twin_prime_pair(k)
        is_valid = is_valid_coordinate(n)
        
        coords.append({
            'm': m,
            'n': n,
            'k': k,
            'twins': (twin1, twin2),
            'valid': is_valid
        })
        
        status = "VALID" if is_valid else "NOT TWIN"
        print(f"m={m:2d}: n={n:,} k={k:,} Twins {twin1, twin2} [{status}]")
    
    return coords

def find_even_power_coordinates(max_m=20):
    """Find even power coordinates up to max_m (for comparison)"""
    coords = []
    
    for m in range(0, max_m + 1):  # Include m=0
        n = 2 ** m
        k = consciousness_coordinate(n)
        twin1, twin2 = twin_prime_pair(k)
        is_valid = is_valid_coordinate(n)
        
        coords.append({
            'm': m,
            'n': n,
            'k': k,
            'twins': (twin1, twin2),
            'valid': is_valid
        })
        
        status = "VALID" if is_valid else "NOT TWIN"
        print(f"m={m:2d}: n={n:,} k={k:,} Twins {twin1, twin2} [{status}]")
    
    return coords

if __name__ == "__main__":
    print("=" * 60)
    print("ODD POWER COORDINATES (Consciousness Emergence Points)")
    print("=" * 60)
    odd_coords = find_odd_power_coordinates(15)
    
    print()
    print("=" * 60)
    print("EVEN POWER COORDINATES (For Comparison)")
    print("=" * 60)
    even_coords = find_even_power_coordinates(12)
    
    print()
    print("=" * 60)
    print("PATTERN SUMMARY")
    print("=" * 60)
    
    odd_valid = [c for c in odd_coords if c['valid']]
    even_valid = [c for c in even_coords if c['valid']]
    
    print(f"Odd powers (m=1,3,5...,{max(odd_coords, key=lambda x: x['m'])}): {len(odd_valid)}/{len(odd_coords)} valid")
    print(f"Even powers (m=0,2,4...,{max(even_coords, key=lambda x: x['m'])}): {len(even_valid)}/{len(even_coords)} valid")
    
    print()
    if odd_valid:
        print("VALID ODD POWER COORDINATES:")
        for c in odd_valid:
            print(f"  m={c['m']}: n={c['n']}, k={c['k']}, Twins {c['twins']}")
