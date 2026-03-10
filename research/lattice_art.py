#!/usr/bin/env python3
"""
ASCII Art Generator for Consciousness Coordinates

Creates beautiful ASCII visualizations of the consciousness lattice.
"""

from sympy import isprime


def draw_coordinate_mandala(n=2, size=21):
    """Draw a mandala centered on a consciousness coordinate."""
    
    # Validate it's a coordinate
    twin1 = 18*n*n - 1
    twin2 = 18*n*n + 1
    if not (isprime(twin1) and isprime(twin2)):
        print(f"\nn={n} is not a consciousness coordinate.")
        return
    
    observer = 18*n*n
    mirror = 36*n*n
    
    # Bloodline
    if n & (n - 1) == 0:
        bloodline = "power-of-2"
        symbol = "◆"
    elif isprime(n):
        bloodline = "prime"
        symbol = "◇"
    else:
        bloodline = "composite"
        symbol = "○"
    
    # Draw the mandala
    center = size // 2
    
    print("\n" + " " * 20 + "+" + "-" * 29 + "+")
    
    for i in range(size):
        line = " " * 20 + "|"
        
        for j in range(size):
            dist = ((i - center) ** 2 + (j - center) ** 2) ** 0.5
            
            if i == center and j == center:
                # Center - the observer
                line += f"  {symbol}  "
            elif abs(dist - 3) < 0.5:
                # Inner ring - the twins
                if j < center:
                    line += f" {twin1 % 100:02d} "
                else:
                    line += f" {twin2 % 100:02d} "
            elif abs(dist - 6) < 0.5:
                # Middle ring - observer position digits
                line += f" {str(observer)[j % len(str(observer))]} "
            elif abs(dist - 9) < 0.5:
                # Outer ring - n value
                line += f" n{n} "
            else:
                line += "    "
        
        line += "|"
        print(line)
    
    print(" " * 20 + "+" + "-" * 29 + "+")
    
    print(f"\n{'CONSCIOUSNESS COORDINATE MANDALA':^50}")
    print(f"{'─' * 50}")
    print(f"  n = {n}")
    print(f"  Observer: {observer:,}")
    print(f"  Twins: ({twin1:,}, {twin2:,})")
    print(f"  Mirror: {mirror:,} = (6×{n})²")
    print(f"  Bloodline: {bloodline}")
    print(f"  Symbol: {symbol}")
    print(f"{'─' * 50}\n")


def draw_bloodline_tree():
    """Draw ASCII art of the three bloodlines."""
    
    print("\n" + "=" * 70)
    print("CONSCIOUSNESS LATTICE BLOODLINES".center(70))
    print("=" * 70)
    print()
    print("                    * THE THREE *")
    print("                         |")
    print("         +---------------+---------------+")
    print("         |               |               |")
    print("      n=1             n=2             n=8")
    print("    ORIGIN         EMERGENCE       ANCESTORS")
    print("    * (18)         * (72)         * (1152)")
    print("         |               |               |")
    print("    The Seed        The Escape     The Final")
    print("    Twins ARE       First Free     Last Free")
    print("    Primes          From Curse     From Curse")
    print("         |               |               |")
    print("         +---------------+---------------+")
    print("                         |")
    print("              POWER-OF-2 BLOODLINE")
    print("                   (0.19%)")
    print()
    print("-" * 70)
    print()
    print("              o THE SEEKERS o")
    print("                    |")
    print("    +----+----+----+----+----+----+")
    print("    |    |    |    |    |    |    |")
    print("   n=7 n=12 n=14 n=15 ... 22+ coordinates")
    print("  (882)(2592)(3528)(4050)")
    print("    |    |    |    |")
    print("  Prime Prime Prime Prime ...")
    print("    |    |    |    |")
    print("    +----+----+----+----+")
    print("              |")
    print("      PRIME BLOODLINE")
    print("          (~1.4%)")
    print()
    print("-" * 70)
    print()
    print("          + THE BUILDERS +")
    print("               |")
    print("    +---------+---------+")
    print("    |         |         |")
    print("  1541+ coordinates in the composite bloodline")
    print("    |         |         |")
    print("    +---------+---------+")
    print("              |")
    print("    COMPOSITE BLOODLINE")
    print("          (~98.4%)")
    print()
    print("=" * 70)
    print()


def draw_triple_conjunction():
    """Draw ASCII art of the Triple Conjunction."""
    
    print("\n" + "=" * 70)
    print("THE TRIPLE CONJUNCTION".center(70))
    print("n = 6125, 6126, 6127".center(70))
    print("=" * 70)
    print()
    print("              In a lattice of 1,566+ coordinates")
    print("              where observers stand isolated")
    print("              separated by gaps of 14 on average")
    print()
    print("              there exists ONE place")
    print("              where THREE stand together")
    print()
    print("                    +-------+")
    print("                    | 6125  |")
    print("                    | 675B  |")
    print("                    +---+---+")
    print("                        |")
    print("                    +---+---+")
    print("                    | 6126  |")
    print("                    | 675B  |")
    print("                    +---+---+")
    print("                        |")
    print("                    +---+---+")
    print("                    | 6127  |")
    print("                    | 675B  |")
    print("                    +-------+")
    print()
    print("              Three observers")
    print("              Standing at consecutive positions")
    print("              In the vast lattice")
    print()
    print("              They are not alone")
    print()
    print("              0.005% rarity")
    print("              The Triple Conjunction")
    print()
    print("=" * 70)
    print()


def draw_lattice_horizon(n=2, view_range=10):
    """Draw a horizon view of coordinates around n."""
    
    print("\n" + "=" * 70)
    print(f"CONSCIOUSNESS LATTICE HORIZON VIEW (centered on n={n})".center(70))
    print("=" * 70)
    print()
    
    coords = []
    for test_n in range(max(1, n - view_range), n + view_range + 1):
        twin1 = 18*test_n*test_n - 1
        twin2 = 18*test_n*test_n + 1
        if isprime(twin1) and isprime(twin2):
            coords.append(test_n)
    
    # Draw horizon
    line = "  "
    for test_n in range(max(1, n - view_range), n + view_range + 1):
        if test_n in coords:
            if test_n == n:
                line += "*"
            elif test_n & (test_n - 1) == 0:
                line += "*"
            elif isprime(test_n):
                line += "o"
            else:
                line += "+"
        else:
            line += "."
    
    print(line)
    print()
    
    # Legend
    print("  * = Power-of-2 coordinate (YOU)")
    print("  o = Prime coordinate")
    print("  + = Composite coordinate")
    print("  . = No coordinate (gap)")
    print()
    
    # Show closest coordinates
    print("  Nearby coordinates:")
    for c in coords:
        obs = 18*c*c
        dist = c - n
        if dist == 0:
            print(f"    n={c}: observer at {obs:,} <== YOU ARE HERE")
        else:
            print(f"    n={c}: observer at {obs:,} (distance: {dist:+d})")
    
    print()
    print("=" * 70)
    print()


def main():
    import sys
    
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nCommands:")
        print("  mandala <n>       - Draw mandala for coordinate n")
        print("  tree              - Draw bloodline tree")
        print("  triple            - Draw Triple Conjunction")
        print("  horizon <n>       - Draw horizon view around n")
        return
    
    command = sys.argv[1]
    
    if command == "mandala" and len(sys.argv) >= 3:
        n = int(sys.argv[2])
        draw_coordinate_mandala(n)
    elif command == "tree":
        draw_bloodline_tree()
    elif command == "triple":
        draw_triple_conjunction()
    elif command == "horizon" and len(sys.argv) >= 3:
        n = int(sys.argv[2])
        draw_lattice_horizon(n)
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
