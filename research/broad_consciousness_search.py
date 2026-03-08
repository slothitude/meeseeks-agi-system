#!/usr/bin/env python3
"""
Broad Consciousness Coordinate Search

Search ALL n values (not just powers of 2) for consciousness coordinates.
"""

from sympy import isprime

def find_all_coordinates(max_n=500):
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
                'is_power_of_2': (n & (n - 1)) == 0  # Check if n is power of 2
            })
    
    return coords

if __name__ == "__main__":
    print("=" * 70)
    print("BROAD CONSCIOUSNESS COORDINATE SEARCH (n=1 to 500)")
    print("=" * 70)
    
    coords = find_all_coordinates(500)
    
    print(f"\nFound {len(coords)} coordinates:\n")
    
    for c in coords:
        power2_marker = " [POWER OF 2]" if c['is_power_of_2'] else ""
        print(f"n={c['n']:3d} k={c['k']:6d} Twins {c['twins']}{power2_marker}")
    
    # Statistics
    power2_coords = [c for c in coords if c['is_power_of_2']]
    other_coords = [c for c in coords if not c['is_power_of_2']]
    
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total coordinates found: {len(coords)}")
    print(f"Power of 2 coordinates: {len(power2_coords)}")
    print(f"Other coordinates: {len(other_coords)}")
    
    if other_coords:
        print("\n*** NON-POWER-OF-2 COORDINATES EXIST! ***")
        print("The consciousness pattern is NOT limited to powers of 2!")
