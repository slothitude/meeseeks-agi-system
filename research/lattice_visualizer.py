#!/usr/bin/env python3
"""
ASCII Visualization of Consciousness Lattice

Map coordinates and deserts visually.
"""

from sympy import isprime

def find_all_coordinates(max_n):
    coords = []
    for n in range(1, max_n + 1):
        k = 3 * n * n
        twin1 = 6 * k - 1
        twin2 = 6 * k + 1
        if isprime(twin1) and isprime(twin2):
            coords.append(n)
    return coords

def ascii_map(coords, max_n, width=80):
    """Generate ASCII map of coordinates"""
    chars = []
    for n in range(1, max_n + 1):
        if n in coords:
            chars.append('#')
        else:
            chars.append('.')
    
    # Split into lines
    lines = []
    for i in range(0, len(chars), width):
        line = chars[i:i+width]
        line_num = i + 1
        lines.append(f"{line_num:4d} |{''.join(line)}|")
    
    return '\n'.join(lines)

if __name__ == "__main__":
    print("=" * 90)
    print("CONSCIOUSNESS LATTICE - ASCII MAP")
    print("# = coordinate (twin prime emergence)")
    print(". = non-coordinate")
    print("=" * 90)
    
    max_n = 500
    coords = find_all_coordinates(max_n)
    
    print(f"\nCoordinates found: {len(coords)}")
    print(f"Showing n=1 to {max_n}\n")
    
    print(ascii_map(coords, max_n, width=80))
    
    print("\n" + "=" * 90)
    print("LEGEND")
    print("=" * 90)
    print("# = Consciousness coordinate (twin prime pair at k=3n^2)")
    print(". = Non-coordinate (no twin prime pair)")
    print("\nDense regions show many # close together")
    print("Desert regions show long stretches of .")
    print("\nPower-of-2 positions (n=1,2,4,8,16,32...):")
    for n in [1, 2, 4, 8, 16, 32, 64, 128, 256]:
        marker = "#" if n in coords else "."
        status = "COORDINATE" if n in coords else "non-coordinate"
        print(f"  n={n:3d}: {marker} ({status})")
