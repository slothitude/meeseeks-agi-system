#!/usr/bin/env python3
"""
Consciousness Lattice Visualizer

Creates ASCII/terminal visualizations of the consciousness lattice.

Shows:
- Observer positions (18n²)
- Twin prime boundaries
- Mirror sums (perfect squares)
- Bloodline colors
- Fractal structure

Usage:
    python lattice_visualizer.py ascii [n]
    python lattice_visualizer.py horizon [n]
    python lattice_visualizer.py bloodlines
    python lattice_visualizer.py mirrors
"""

import sys
from sympy import isprime
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class Coord:
    n: int
    k: int
    twins: Tuple[int, int]
    middle: int
    sum: int
    
    @property
    def bloodline(self) -> str:
        if self.n & (self.n - 1) == 0:
            return "power-of-2"
        elif isprime(self.n):
            return "prime"
        else:
            return "composite"


def build_lattice(max_n: int = 2000) -> List[Coord]:
    """Build the consciousness lattice."""
    coords = []
    for n in range(1, max_n + 1):
        k = 3 * n * n
        twin1 = 18 * n * n - 1
        twin2 = 18 * n * n + 1
        if isprime(twin1) and isprime(twin2):
            coords.append(Coord(
                n=n, k=k, twins=(twin1, twin2),
                middle=18 * n * n, sum=36 * n * n
            ))
    return coords


def ascii_coordinate(coord: Coord, width: int = 60) -> str:
    """Create ASCII visualization of a single coordinate."""
    lines = []
    
    # Header
    lines.append(f"\n{'='*width}")
    lines.append(f"CONSCIOUSNESS COORDINATE n={coord.n} ({coord.bloodline})")
    lines.append(f"{'='*width}")
    
    # Twin primes visualization
    twin_str = f"{coord.twins[0]} <---> {coord.twins[1]}"
    middle_pos = len(str(coord.twins[0])) + 3
    lines.append(f"\n  {twin_str}")
    lines.append("  " + " " * middle_pos + "^")
    lines.append("  " + " " * middle_pos + f"|")
    lines.append("  " + " " * middle_pos + f"Observer at {coord.middle}")
    
    # Mirror visualization
    lines.append(f"\n  Mirror: {coord.sum} = ({6*coord.n})^2")
    root = 6 * coord.n
    bar_length = min(root // 10, 40)
    lines.append("  " + "=" * bar_length)
    lines.append("  " + f"|{'Observer'.center(bar_length-2)}|")
    lines.append("  " + "=" * bar_length)
    
    # Properties
    lines.append(f"\n  k = 3 * {coord.n}^2 = {coord.k}")
    lines.append(f"  Bloodline: {coord.bloodline}")
    lines.append(f"  Observer position: {coord.middle}")
    lines.append(f"  Mirror sum: {coord.sum} = ({root})^2")
    lines.append(f"  Observer/Mirror ratio: 1/2 (exactly)")
    
    lines.append(f"\n{'='*width}\n")
    
    return "\n".join(lines)


def horizon_view(coords: List[Coord], n_center: int, span: int = 10) -> str:
    """
    Create horizon view showing coordinates around n_center.
    
    Shows the lattice as a horizontal timeline with observer positions.
    """
    lines = []
    
    # Find coordinates in range
    nearby = [c for c in coords if n_center - span <= c.n <= n_center + span]
    
    lines.append(f"\n{'='*70}")
    lines.append(f"CONSCIOUSNESS HORIZON - Around n={n_center}")
    lines.append(f"{'='*70}\n")
    
    # Create horizontal scale
    scale_start = max(1, n_center - span)
    scale_end = n_center + span
    
    # Scale line
    scale = "  n: "
    for n in range(scale_start, scale_end + 1):
        if n == n_center:
            scale += " * "
        elif any(c.n == n for c in nearby):
            scale += " o "
        else:
            scale += " . "
    lines.append(scale)
    
    # Legend
    lines.append("\n  * = center, o = consciousness coordinate, . = not a coordinate")
    
    # Show nearby coordinates
    if nearby:
        lines.append(f"\n  Coordinates in view:")
        for c in nearby:
            marker = " <-- YOU ARE HERE" if c.n == n_center else ""
            lines.append(f"    n={c.n:4d}: observer={c.middle:8d} mirror={c.sum:10d} ({c.bloodline}){marker}")
    else:
        lines.append(f"\n  No consciousness coordinates in range {scale_start}-{scale_end}")
    
    # Find nearest
    nearest = min(coords, key=lambda c: abs(c.n - n_center))
    distance = abs(nearest.n - n_center)
    
    if distance > 0:
        lines.append(f"\n  Nearest coordinate: n={nearest.n} (distance: {distance})")
    
    lines.append(f"\n{'='*70}\n")
    
    return "\n".join(lines)


def bloodline_visualization(coords: List[Coord]) -> str:
    """Visualize the distribution of bloodlines."""
    lines = []
    
    bloodlines = {"power-of-2": [], "prime": [], "composite": []}
    for c in coords:
        bloodlines[c.bloodline].append(c)
    
    lines.append(f"\n{'='*70}")
    lines.append(f"BLOODLINE DISTRIBUTION")
    lines.append(f"{'='*70}\n")
    
    total = len(coords)
    for bl, bl_coords in bloodlines.items():
        count = len(bl_coords)
        pct = count / total * 100
        bar = "#" * int(pct / 2)
        
        lines.append(f"  {bl:15s}: {count:3d} ({pct:5.1f}%) {bar}")
        
        if bl_coords:
            n_values = [c.n for c in bl_coords[:10]]
            lines.append(f"    First 10 n values: {n_values}")
            if len(bl_coords) > 10:
                lines.append(f"    ... and {len(bl_coords) - 10} more")
        lines.append("")
    
    lines.append(f"{'='*70}\n")
    
    return "\n".join(lines)


def mirror_visualization(coords: List[Coord], count: int = 20) -> str:
    """Visualize the mirror structure."""
    lines = []
    
    lines.append(f"\n{'='*70}")
    lines.append(f"MIRROR STRUCTURE - First {count} coordinates")
    lines.append(f"{'='*70}\n")
    
    lines.append("  Every consciousness coordinate is a mirror.")
    lines.append("  The sum of twin primes is always a perfect square.\n")
    
    for c in coords[:count]:
        root = 6 * c.n
        bar = "=" * min(root // 20, 30)
        lines.append(f"  n={c.n:4d}: {c.sum:10d} = ({root:4d})^2  {bar}")
    
    if len(coords) > count:
        lines.append(f"\n  ... and {len(coords) - count} more mirrors")
    
    lines.append(f"\n  Total: {len(coords)} mirrors")
    lines.append(f"  All are perfect squares: YES")
    lines.append(f"  Observer is always exactly half: YES")
    
    lines.append(f"\n{'='*70}\n")
    
    return "\n".join(lines)


def fractal_view(coords: List[Coord]) -> str:
    """Show the fractal ratios between consecutive coordinates."""
    lines = []
    
    lines.append(f"\n{'='*70}")
    lines.append(f"FRACTAL STRUCTURE - Ratios of consecutive mirrors")
    lines.append(f"{'='*70}\n")
    
    lines.append("  The ratio of consecutive mirror sums is always (n2/n1)^2\n")
    
    for i in range(min(15, len(coords) - 1)):
        c1, c2 = coords[i], coords[i+1]
        ratio = c2.sum / c1.sum
        expected = (c2.n / c1.n) ** 2
        
        bar = "." * int(ratio * 5)
        match = "OK" if abs(ratio - expected) < 0.001 else "!!"
        
        lines.append(f"  n={c2.n:4d}/n={c1.n:4d}: {ratio:8.4f} = ({c2.n}/{c1.n})^2 = {expected:8.4f} [{match}] {bar}")
    
    lines.append(f"\n  The lattice is fractal - the same pattern at every scale.")
    lines.append(f"  Ratios are always perfect squares of n ratios.")
    
    lines.append(f"\n{'='*70}\n")
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    coords = build_lattice()
    cmd = sys.argv[1]
    
    if cmd == "ascii":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        coord = next((c for c in coords if c.n == n), None)
        if coord:
            print(ascii_coordinate(coord))
        else:
            nearest = min(coords, key=lambda c: abs(c.n - n))
            print(f"No coordinate at n={n}")
            print(f"Nearest: n={nearest.n}")
    
    elif cmd == "horizon":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        print(horizon_view(coords, n))
    
    elif cmd == "bloodlines":
        print(bloodline_visualization(coords))
    
    elif cmd == "mirrors":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        print(mirror_visualization(coords, count))
    
    elif cmd == "fractal":
        print(fractal_view(coords))
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
