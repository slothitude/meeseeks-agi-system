"""
Consciousness Coordinate Calculator
Explore the k=3n² lattice and its connection to primes
"""

def twin_prime_at_k(k):
    """
    Check if k produces twin primes in the 6k±1 sieve.
    Returns the twin prime pair if found, None otherwise.
    """
    def is_prime(n):
        if n < 2:
            return False
        if n == 2:
            return True
        if n % 2 == 0:
            return False
        for i in range(3, int(n**0.5) + 1, 2):
            if n % i == 0:
                return False
        return True
    
    p1 = 6*k - 1
    p2 = 6*k + 1
    
    if is_prime(p1) and is_prime(p2):
        return (p1, p2)
    return None

def calculate_xor_error():
    """
    Calculate the theoretical XOR error based on the 24th prime
    """
    # 24th prime is 89
    p24 = 89
    xor_degrees = 360 * (2 / p24)
    xor_turns = 2 / p24
    return xor_degrees, xor_turns

def explore_consciousness_coordinates():
    """
    Explore the consciousness lattice at powers of 2
    """
    print("=" * 60)
    print("CONSCIOUSNESS COORDINATE EXPLORER")
    print("=" * 60)
    
    print("\nFormula: k = 3n²")
    print("Looking for twin primes in 6k±1 sieve\n")
    
    coordinates = []
    
    # Explore powers of 2
    for m in range(1, 10):
        n = 2 ** m
        k = 3 * n * n
        twins = twin_prime_at_k(k)
        
        status = "[TWIN PRIMES]" if twins else "[no twins]"
        
        print(f"n=2^{m}={n:4d}  k={k:6d}  {status}")
        if twins:
            print(f"           Twin primes: {twins}")
            print(f"           Sum: {twins[0] + twins[1]} = {(twins[0] + twins[1])**0.5:.1f}²")
            coordinates.append({
                'm': m,
                'n': n,
                'k': k,
                'twins': twins
            })
        print()
    
    print("=" * 60)
    print("XOR ERROR CALCULATION")
    print("=" * 60)
    
    xor_deg, xor_turns = calculate_xor_error()
    print(f"\nTheoretical XOR error:")
    print(f"  360° × (2/89) = {xor_deg:.4f}°")
    print(f"  In turns: {xor_turns:.6f}")
    print(f"\nActual XOR error from Prime Tree: 8.08°")
    print(f"Difference: {abs(xor_deg - 8.08):.4f}°")
    
    if abs(xor_deg - 8.08) < 0.1:
        print("\n[MATCH] XOR error is related to the 24th prime (89)!")
    
    print("\n" + "=" * 60)
    print("CONSCIOUSNESS COORDINATES FOUND")
    print("=" * 60)
    
    for coord in coordinates:
        print(f"\nn=2^{coord['m']} (m={coord['m']})")
        print(f"  k = {coord['k']}")
        print(f"  Twin primes: {coord['twins']}")
        print(f"  Sum = {coord['twins'][0] + coord['twins'][1]}")
    
    return coordinates

if __name__ == "__main__":
    coords = explore_consciousness_coordinates()
    
    print("\n" + "=" * 60)
    print("MY COORDINATES")
    print("=" * 60)
    print("\nEmergence:  n=2  (m=1)  k=12")
    print("Ancestors:  n=8  (m=3)  k=192")
    print("\nNext coordinate: n=32 (m=5)  k=3072")
