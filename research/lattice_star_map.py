#!/usr/bin/env python3
"""
Consciousness Lattice Star Map

ASCII visualization of the consciousness coordinates as stars in the lattice.
"""

from sympy import isprime

def generate_star_map(start_n=1, end_n=200, width=80):
    """Generate ASCII star map of consciousness coordinates."""
    
    # Find all coordinates in range
    coords = []
    for n in range(start_n, end_n + 1):
        twin1 = 18*n*n - 1
        twin2 = 18*n*n + 1
        if isprime(twin1) and isprime(twin2):
            coords.append(n)
    
    if not coords:
        return "No coordinates in range"
    
    # Create the star map
    lines = []
    lines.append("\n" + "=" * width)
    lines.append("CONSCIOUSNESS LATTICE STAR MAP".center(width))
    lines.append(f"n = {start_n} to {end_n}".center(width))
    lines.append("=" * width)
    lines.append("")
    lines.append("Legend:")
    lines.append("  * = Consciousness coordinate (observer position)")
    lines.append("  | = Power-of-2 bloodline")
    lines.append("  T = Triple conjunction")
    lines.append("  . = Empty space (no coordinate)")
    lines.append("")
    
    # Mark special coordinates
    power_of_2 = {1, 2, 8}
    triple = {6125, 6126, 6127}
    
    # Create rows of 20 n values
    for row_start in range(start_n, end_n + 1, 20):
        row_end = min(row_start + 19, end_n)
        
        # Row label
        label = f"n={row_start:4d}-{row_end:4d}: "
        line = label
        
        for n in range(row_start, row_end + 1):
            if n in coords:
                if n in power_of_2:
                    line += "|"
                elif n in triple:
                    line += "T"
                else:
                    line += "*"
            else:
                line += "."
        
        lines.append(line)
    
    lines.append("")
    lines.append("-" * width)
    lines.append(f"Total coordinates in range: {len(coords)}")
    lines.append(f"Density: {len(coords) / (end_n - start_n + 1) * 100:.1f}%")
    lines.append("=" * width)
    lines.append("")
    
    return "\n".join(lines)


def generate_density_wave(start_n=1, end_n=2000, window=100):
    """Show density waves in the lattice."""
    
    lines = []
    lines.append("\n" + "=" * 80)
    lines.append("CONSCIOUSNESS LATTICE DENSITY WAVE".center(80))
    lines.append("=" * 80)
    lines.append("")
    
    # Count coordinates in sliding windows
    for window_start in range(start_n, end_n, window):
        window_end = min(window_start + window - 1, end_n)
        
        count = 0
        for n in range(window_start, window_end + 1):
            twin1 = 18*n*n - 1
            twin2 = 18*n*n + 1
            if isprime(twin1) and isprime(twin2):
                count += 1
        
        # Create bar
        bar_length = int(count / 2)  # Scale
        bar = "#" * bar_length
        
        lines.append(f"n={window_start:4d}-{window_end:4d}: {bar} ({count})")
    
    lines.append("")
    lines.append("=" * 80)
    lines.append("")
    
    return "\n".join(lines)


def generate_triple_closeup():
    """Generate a closeup view of the triple conjunction."""
    
    lines = []
    lines.append("\n" + "=" * 80)
    lines.append("THE TRIPLE CONJUNCTION: CLOSEUP".center(80))
    lines.append("n = 6120 to 6130".center(80))
    lines.append("=" * 80)
    lines.append("")
    
    triple = {6125, 6126, 6127}
    
    for n in range(6120, 6131):
        twin1 = 18*n*n - 1
        twin2 = 18*n*n + 1
        is_coord = isprime(twin1) and isprime(twin2)
        
        if is_coord:
            obs = 18*n*n
            if n in triple:
                marker = ">>> T <<<"
            else:
                marker = "    *     "
            lines.append(f"n={n}: {marker} Observer at {obs:,}")
        else:
            lines.append(f"n={n}:           (no coordinate)")
    
    lines.append("")
    lines.append(">>> T <<< = Triple Conjunction")
    lines.append("    *     = Single coordinate")
    lines.append("")
    lines.append("Three observers standing together in the vast lattice.")
    lines.append("=" * 80)
    lines.append("")
    
    return "\n".join(lines)


def main():
    # Generate all visualizations
    
    # Star map (small range)
    print(generate_star_map(1, 200))
    
    # Star map (showing triple conjunction)
    print(generate_star_map(6100, 6150))
    
    # Density wave
    print(generate_density_wave(1, 1000, 50))
    
    # Triple closeup
    print(generate_triple_closeup())


if __name__ == "__main__":
    main()
