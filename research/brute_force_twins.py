#!/usr/bin/env python3
"""
Direct twin prime check - brute force exploration
"""

from sympy import isprime

def is_twin_prime(k):
    """Check if (k, k+2) is a twin prime pair"""
    return isprime(k) and isprime(k + 2)

def main():
    print("=" * 60)
    print("BRUTE FORCE TWIN PRIME SEARCH")
    print("Formula: k = 3n^2")
    print("=" * 60)
    
    # Check first 100 n values
    twin_count = 0
    twins_found = []
    
    for n in range(1, 101):
        k = 3 * n * n
        if is_twin_prime(k):
            twin_count += 1
            twins_found.append((n, k, k+2))
            print(f"n={n}: k={k} -> Twins ({k}, {k+2})")
    
    print()
    print(f"Total twin primes found: {twin_count} out of 100 n values")
    print()
    
    if twins_found:
        print("Twin prime coordinates found:")
        for n, k, k2 in twins_found:
            # Check if n is power of 2
            import math
            if n & (n - 1) == 0:  # power of 2 check
                m = int(math.log2(n))
                print(f"  n={n} = 2^{m} -> k={k} -> Twins ({k}, {k2})")
            else:
                print(f"  n={n} (not power of 2) -> k={k} -> Twins ({k}, {k2})")

if __name__ == "__main__":
    main()
