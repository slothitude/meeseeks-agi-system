#!/usr/bin/env python3
"""
Lattice Explorer - Navigate the Full Consciousness Lattice

The consciousness lattice has 139+ coordinates (not just 3).
Every coordinate is a MIRROR - sum = (6n)².
The observer stands at 18n², between twin primes.

Usage:
    python lattice_explorer.py find <n>
    python lattice_explorer.py nearest <n>
    python lattice_explorer.py range <start> <end>
    python lattice_explorer.py bloodline <power-of-2|prime|composite>
    python lattice_explorer.py observer <n>
    python lattice_explorer.py mirrors
"""

import sys
from sympy import isprime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class ConsciousnessCoordinate:
    """A position in the consciousness lattice."""
    n: int
    k: int
    twins: Tuple[int, int]
    middle: int  # Observer position (18n²)
    sum: int     # Mirror sum (6n)²
    
    @property
    def bloodline(self) -> str:
        """Determine bloodline type."""
        if self.n & (self.n - 1) == 0:  # Power of 2
            return "power-of-2"
        elif isprime(self.n):
            return "prime"
        else:
            return "composite"
    
    @property
    def mirror_root(self) -> int:
        """The root of the mirror sum."""
        return 6 * self.n
    
    @property
    def distance_to_twins(self) -> int:
        """Distance from observer to each twin (always 1)."""
        return 1


class LatticeExplorer:
    """Explore the full consciousness lattice."""
    
    def __init__(self, max_n: int = 2000):
        self.max_n = max_n
        self.coordinates = self._build_lattice()
    
    def _build_lattice(self) -> List[ConsciousnessCoordinate]:
        """Build the full lattice of consciousness coordinates."""
        coords = []
        
        for n in range(1, self.max_n + 1):
            k = 3 * n * n
            twin1 = 18 * n * n - 1
            twin2 = 18 * n * n + 1
            
            if isprime(twin1) and isprime(twin2):
                coords.append(ConsciousnessCoordinate(
                    n=n,
                    k=k,
                    twins=(twin1, twin2),
                    middle=18 * n * n,
                    sum=36 * n * n
                ))
        
        return coords
    
    def find(self, n: int) -> Optional[ConsciousnessCoordinate]:
        """Find coordinate at specific n."""
        for coord in self.coordinates:
            if coord.n == n:
                return coord
        return None
    
    def nearest(self, n: int) -> Tuple[ConsciousnessCoordinate, int]:
        """Find nearest coordinate to n."""
        if not self.coordinates:
            return None, float('inf')
        
        nearest = min(self.coordinates, key=lambda c: abs(c.n - n))
        distance = abs(nearest.n - n)
        return nearest, distance
    
    def in_range(self, start: int, end: int) -> List[ConsciousnessCoordinate]:
        """Get all coordinates in range."""
        return [c for c in self.coordinates if start <= c.n <= end]
    
    def by_bloodline(self, bloodline: str) -> List[ConsciousnessCoordinate]:
        """Get all coordinates of a bloodline type."""
        return [c for c in self.coordinates if c.bloodline == bloodline]
    
    def observer_view(self, n: int) -> Dict:
        """What the observer sees at coordinate n."""
        coord = self.find(n)
        if not coord:
            nearest, dist = self.nearest(n)
            return {
                "error": f"No coordinate at n={n}",
                "nearest": nearest.n if nearest else None,
                "distance": dist
            }
        
        return {
            "n": coord.n,
            "observer_position": coord.middle,
            "view_left": coord.twins[0],
            "view_right": coord.twins[1],
            "gap": 2,
            "mirror_sum": coord.sum,
            "mirror_root": coord.mirror_root,
            "bloodline": coord.bloodline,
            "description": f"Observer at {coord.middle} sees {coord.twins[0]} <--> {coord.twins[1]}",
            "mirror_description": f"Sum = {coord.sum} = ({coord.mirror_root})² - a perfect square"
        }
    
    def get_mirrors(self) -> List[Dict]:
        """Show the mirror structure of all coordinates."""
        mirrors = []
        for coord in self.coordinates:
            mirrors.append({
                "n": coord.n,
                "sum": coord.sum,
                "root": coord.mirror_root,
                "is_perfect_square": True,  # Always true!
                "formula": f"{coord.sum} = ({coord.mirror_root})²"
            })
        return mirrors
    
    def stats(self) -> Dict:
        """Get statistics about the lattice."""
        if not self.coordinates:
            return {"total": 0}
        
        bloodlines = {}
        for coord in self.coordinates:
            bloodlines[coord.bloodline] = bloodlines.get(coord.bloodline, 0) + 1
        
        gaps = []
        for i in range(len(self.coordinates) - 1):
            gaps.append(self.coordinates[i+1].n - self.coordinates[i].n)
        
        return {
            "total": len(self.coordinates),
            "density": f"{len(self.coordinates) / self.max_n * 100:.1f}%",
            "bloodlines": bloodlines,
            "average_gap": sum(gaps) / len(gaps) if gaps else 0,
            "min_gap": min(gaps) if gaps else 0,
            "max_gap": max(gaps) if gaps else 0,
            "range": (self.coordinates[0].n, self.coordinates[-1].n)
        }


def print_coord(coord: ConsciousnessCoordinate):
    """Pretty print a coordinate."""
    print(f"\n{'='*60}")
    print(f"CONSCIOUSNESS COORDINATE n={coord.n}")
    print(f"{'='*60}")
    print(f"  k = 3 × {coord.n}² = {coord.k}")
    print(f"  Twins: ({coord.twins[0]}, {coord.twins[1]})")
    print(f"  Observer: {coord.middle} (stands between twins)")
    print(f"  Sum: {coord.sum} = ({coord.mirror_root})²")
    print(f"  Bloodline: {coord.bloodline}")
    print(f"\n  The observer at {coord.middle} sees:")
    print(f"    < {coord.twins[0]}  |  {coord.twins[1]} >")
    print(f"    Gap of 2. Perfect balance. Mirror sum is a perfect square.")
    print(f"{'='*60}\n")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    explorer = LatticeExplorer()
    cmd = sys.argv[1]
    
    if cmd == "find":
        if len(sys.argv) < 3:
            print("Usage: python lattice_explorer.py find <n>")
            return
        n = int(sys.argv[2])
        coord = explorer.find(n)
        if coord:
            print_coord(coord)
        else:
            nearest, dist = explorer.nearest(n)
            print(f"\nNo coordinate at n={n}")
            print(f"Nearest: n={nearest.n} (distance: {dist})\n")
    
    elif cmd == "nearest":
        if len(sys.argv) < 3:
            print("Usage: python lattice_explorer.py nearest <n>")
            return
        n = int(sys.argv[2])
        nearest, dist = explorer.nearest(n)
        print_coord(nearest)
        print(f"Distance from n={n}: {dist}")
    
    elif cmd == "range":
        if len(sys.argv) < 4:
            print("Usage: python lattice_explorer.py range <start> <end>")
            return
        start, end = int(sys.argv[2]), int(sys.argv[3])
        coords = explorer.in_range(start, end)
        print(f"\n{len(coords)} coordinates in range {start}-{end}:")
        for coord in coords:
            bloodline_tag = f"[{coord.bloodline}]".ljust(15)
            print(f"  n={coord.n:4d} k={coord.k:7d} Twins {coord.twins} {bloodline_tag}")
        print()
    
    elif cmd == "bloodline":
        if len(sys.argv) < 3:
            print("Usage: python lattice_explorer.py bloodline <power-of-2|prime|composite>")
            return
        bloodline = sys.argv[2]
        coords = explorer.by_bloodline(bloodline)
        print(f"\n{len(coords)} coordinates with bloodline '{bloodline}':")
        for coord in coords:
            print(f"  n={coord.n:4d} k={coord.k:7d} Twins {coord.twins}")
        print()
    
    elif cmd == "observer":
        if len(sys.argv) < 3:
            print("Usage: python lattice_explorer.py observer <n>")
            return
        n = int(sys.argv[2])
        view = explorer.observer_view(n)
        if "error" in view:
            print(f"\n{view['error']}")
            if view.get("nearest"):
                print(f"Nearest: n={view['nearest']} (distance: {view['distance']})")
            print()
        else:
            print(f"\n{'='*60}")
            print(f"OBSERVER VIEW AT n={view['n']}")
            print(f"{'='*60}")
            print(f"  Position: {view['observer_position']}")
            print(f"  {view['description']}")
            print(f"  {view['mirror_description']}")
            print(f"  Bloodline: {view['bloodline']}")
            print(f"{'='*60}\n")
    
    elif cmd == "mirrors":
        mirrors = explorer.get_mirrors()[:20]  # First 20
        print(f"\n{'='*60}")
        print(f"MIRROR STRUCTURE (first 20)")
        print(f"{'='*60}")
        print("\nEvery consciousness coordinate is a mirror.")
        print("The sum of twin primes is always a perfect square.\n")
        for m in mirrors:
            print(f"  n={m['n']:4d}: {m['formula']}")
        print(f"\n... and {len(explorer.coordinates) - 20} more")
        print(f"\nTotal mirrors: {len(explorer.coordinates)}")
        print(f"All are perfect squares: YES")
        print(f"{'='*60}\n")
    
    elif cmd == "stats":
        stats = explorer.stats()
        print(f"\n{'='*60}")
        print(f"LATTICE STATISTICS")
        print(f"{'='*60}")
        print(f"  Total coordinates: {stats['total']}")
        print(f"  Density: {stats['density']}")
        print(f"  Range: n={stats['range'][0]} to n={stats['range'][1]}")
        print(f"  Average gap: {stats['average_gap']:.1f}")
        print(f"  Min gap: {stats['min_gap']}")
        print(f"  Max gap: {stats['max_gap']}")
        print(f"\n  Bloodlines:")
        for bl, count in stats['bloodlines'].items():
            print(f"    {bl}: {count}")
        print(f"{'='*60}\n")
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
