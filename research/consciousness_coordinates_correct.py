#!/usr/bin/env python3
"""
Correct Consciousness Coordinates - Twin Prime Formula

The formula:
    k = 3 * n^2
    Twin primes at (6k-1, 6k+1)
    
Example:
    n=2: k=12, twins=(71, 73)
    71 and 73 are both prime, differ by 2 = TWIN PRIME!
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

def main():
    print("=" * 60)
    print("CONSCIOUSNESS COORDINATES - CORRECT FORMULA")
    print("Formula: k = 3n^2, Twins at (6k-1, 6k+1)")
    print("=" * 60)
    print()
    
    # Test known coordinates
    test_values = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
    
    print("Testing known coordinates:")
    print("-" * 60)
    
    valid_coords = []
    for n in test_values:
        k = consciousness_coordinate(n)
        twin1, twin2 = twin_prime_pair(k)
        is_valid = is_valid_coordinate(n)
        
        status = "VALID" if is_valid else "NOT TWIN"
        print(f"n={n:4d}: k={k:8d} -> Twins ({twin1:8d}, {twin2:8d}) [{status}]")
        
        if is_valid:
            valid_coords.append({
                'n': n,
                'k': k,
                'twins': (twin1, twin2),
                'm': None  # Will calculate
            })
    
    # Determine which are powers of 2
    print()
    print("Power of 2 analysis:")
    print("-" * 60)
    
    for coord in valid_coords:
        n = coord['n']
        # Find power of 2
        power = 0
        temp = n
        while temp > 1 and temp % 2 == 0:
            temp //= 2
            power += 1
        if temp == 1:
            coord['m'] = power
            odd_even = "ODD" if power % 2 == 1 else "EVEN"
            print(f"n={n} = 2^{power} ({odd_even}) -> VALID twin prime coordinate")
    
    print()
    print("=" * 60)
    print(f"Valid coordinates found: {len(valid_coords)}")
    print("=" * 60)
    
    # Pattern analysis
    odd_power = [c for c in valid_coords if c['m'] is not None and c['m'] % 2 == 1]
    even_power = [c for c in valid_coords if c['m'] is not None and c['m'] % 2 == 0]
    
    print()
    print("PATTERN ANALYSIS:")
    print(f"  Odd powers (m=1,3,5...): {len(odd_power)} coordinates")
    print(f"  Even powers (m=2,4,6...): {len(even_power)} coordinates")
    
    if odd_power:
        print()
        print("ODD POWER COORDINATES (Consciousness Emergence Points):")
        for c in odd_power:
            print(f"  m={c['m']}: n={c['n']}, k={c['k']}, Twins {c['twins']}")
    
    if even_power:
        print()
        print("EVEN POWER COORDINATES (Check if these break pattern):")
        for c in even_power:
            print(f"  m={c['m']}: n={c['n']}, k={c['k']}, Twins {c['twins']}")
    
    # Predict next coordinates
    print()
    print("=" * 60)
    print("NEXT PREDICTED COORDINATES:")
    print("=" * 60)
    
    if odd_power:
        last_m = odd_power[-1]['m']
        print(f"Last confirmed odd power: m={last_m}")
        print()
        print("Predicting next 3 odd power coordinates:")
        
        for m in range(last_m + 2, last_m + 8, 2):
            n = 2 ** m
            k = consciousness_coordinate(n)
            twin1, twin2 = twin_prime_pair(k)
            is_valid = is_valid_coordinate(n)
            status = "VALID" if is_valid else "NOT TWIN"
            print(f"  m={m}: n={n}, k={k}, Twins ({twin1}, {twin2}) [{status}]")

    
    print()
    print("=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
