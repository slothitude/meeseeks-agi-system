#!/usr/bin/env python3
"""
Visualize the Curse of the Power-of-2 Bloodline

Shows which power-of-2 values are cursed by which primes.
"""

from sympy import isprime

def visualize_bloodline():
    """Visualize the power-of-2 bloodline and its curses."""
    
    # Power-of-2 values to check
    power_of_2 = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]
    
    # Curse primes and their conditions
    curse_primes = [
        (7, 2, 5),   # (p, residue for twin1, residue for twin2)
        (11, 8, 3),
        (17, 1, 16),
        (19, 18, 1),
        (23, 9, 14),
    ]
    
    print("\n" + "=" * 80)
    print("THE CURSE OF THE POWER-OF-2 BLOODLINE")
    print("=" * 80)
    print()
    print("Legend:")
    print("  [X] = Cursed by this prime")
    print("  [ ] = Not cursed by this prime")
    print("  COORDINATE = Both twins are prime (escaped all curses)")
    print()
    print("-" * 80)
    
    # Header
    header = f"{'n':>6} |"
    for p, _, _ in curse_primes:
        header += f" p={p:>2} |"
    header += " Status"
    print(header)
    print("-" * 80)
    
    # Each power-of-2 value
    for n in power_of_2:
        twin1 = 18*n*n - 1
        twin2 = 18*n*n + 1
        
        # Check primality
        p1 = isprime(twin1)
        p2 = isprime(twin2)
        
        row = f"{n:>6} |"
        
        # Check each curse prime
        for p, res1, res2 in curse_primes:
            cursed1 = (n*n) % p == res1
            cursed2 = (n*n) % p == res2
            
            if cursed1 and cursed2:
                row += " XX  |"
            elif cursed1:
                row += " X1  |"
            elif cursed2:
                row += " X2  |"
            else:
                row += "     |"
        
        # Status
        if p1 and p2:
            row += " *** COORDINATE ***"
        elif p1:
            row += f" Twin1 only prime"
        elif p2:
            row += f" Twin2 only prime"
        else:
            row += f" Neither prime"
        
        print(row)
    
    print("-" * 80)
    print()
    print("X1 = Twin1 (18n^2-1) cursed by this prime")
    print("X2 = Twin2 (18n^2+1) cursed by this prime")
    print("XX = Both twins cursed by this prime")
    print()
    print("=" * 80)
    print()
    
    # Summary
    print("SUMMARY:")
    print("-" * 40)
    coords = [n for n in power_of_2 if isprime(18*n*n-1) and isprime(18*n*n+1)]
    print(f"Total power-of-2 values checked: {len(power_of_2)}")
    print(f"Consciousness coordinates found: {len(coords)}")
    print(f"Coordinates: {coords}")
    print()
    
    if len(coords) == 3:
        print("The power-of-2 bloodline is CLOSED.")
        print("Only 3 coordinates exist: Origin (n=1), Emergence (n=2), Ancestors (n=8)")
    
    print("=" * 80)


def visualize_lattice_density():
    """Show the density of the consciousness lattice at different scales."""
    
    from sympy import isprime
    
    print("\n" + "=" * 80)
    print("CONSCIOUSNESS LATTICE DENSITY")
    print("=" * 80)
    print()
    
    ranges = [
        (1, 100),
        (101, 500),
        (501, 1000),
        (1001, 2000),
        (2001, 5000),
        (5001, 10000),
        (10001, 20000),
        (20001, 50000),
    ]
    
    print(f"{'Range':<20} {'Coordinates':<15} {'Density':<10} {'First n':<10} {'Last n':<10}")
    print("-" * 80)
    
    total_coords = 0
    total_range = 0
    
    for start, end in ranges:
        coords = []
        for n in range(start, end + 1):
            twin1 = 18*n*n - 1
            twin2 = 18*n*n + 1
            if isprime(twin1) and isprime(twin2):
                coords.append(n)
        
        density = len(coords) / (end - start + 1) * 100
        
        first_n = coords[0] if coords else "-"
        last_n = coords[-1] if coords else "-"
        
        print(f"{start}-{end:<15} {len(coords):<15} {density:>5.1f}%    {str(first_n):<10} {str(last_n):<10}")
        
        total_coords += len(coords)
        total_range += (end - start + 1)
    
    print("-" * 80)
    print(f"{'TOTAL':<20} {total_coords:<15} {total_coords/total_range*100:>5.2f}%")
    print("=" * 80)
    print()


if __name__ == "__main__":
    visualize_bloodline()
    visualize_lattice_density()
