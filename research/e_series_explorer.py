#!/usr/bin/env python3
"""
E-Series Explorer - Consciousness Coordinates and Exceptional Lie Algebras

The consciousness lattice at n=2 (observer=72) matches E6 root vectors.
This tool explores the connection between consciousness coordinates and
the exceptional Lie algebras (G2, F4, E6, E7, E8).

Usage:
    python e_series_explorer.py check <n>
    python e_series_explorer.py e6
    python e_series_explorer.py decompose
    python e_series_explorer.py weyl
"""

import sys
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


# Exceptional Lie Algebra Data
EXCEPTIONAL_ALGEBRAS = {
    "G2": {
        "dimension": 14,
        "rank": 2,
        "roots": 12,
        "weyl_order": 12,
        "description": "Smallest exceptional - automorphisms of octonions"
    },
    "F4": {
        "dimension": 52,
        "rank": 4,
        "roots": 48,
        "description": "Automorphisms of Albert algebra"
    },
    "E6": {
        "dimension": 78,
        "rank": 6,
        "roots": 72,
        "weyl_order": 51840,
        "coxeter_order": 103680,
        "description": "Observer position at n=2 - consciousness coordinate!"
    },
    "E7": {
        "dimension": 133,
        "rank": 7,
        "roots": 126,
        "weyl_order": 2903040,
        "description": "Second nearest neighbors in E8"
    },
    "E8": {
        "dimension": 248,
        "rank": 8,
        "roots": 240,
        "weyl_order": 696729600,
        "description": "Largest exceptional - contains E6 (72 + 84 + 84)"
    }
}


@dataclass
class ConsciousnessCoordinate:
    """A position in the consciousness lattice."""
    n: int
    k: int
    observer: int
    mirror: int
    twins: Tuple[int, int]
    
    @property
    def mirror_root(self) -> int:
        return 6 * self.n
    
    def check_e_series(self) -> Dict:
        """Check if this coordinate relates to E-series."""
        results = {
            "coordinate": f"n={self.n}",
            "observer": self.observer,
            "mirror": self.mirror,
            "matches": [],
            "relationships": []
        }
        
        for name, data in EXCEPTIONAL_ALGEBRAS.items():
            roots = data["roots"]
            
            # Direct match
            if self.observer == roots:
                results["matches"].append({
                    "algebra": name,
                    "type": "EXACT MATCH",
                    "detail": f"Observer {self.observer} = {name} root vectors"
                })
            
            # Mirror relationship
            if self.mirror == roots:
                results["relationships"].append({
                    "algebra": name,
                    "type": "MIRROR MATCH",
                    "detail": f"Mirror {self.mirror} = {name} root vectors"
                })
            
            # Factor relationship
            if roots % self.observer == 0:
                factor = roots // self.observer
                results["relationships"].append({
                    "algebra": name,
                    "type": "FACTOR",
                    "detail": f"{name} roots ({roots}) = {self.observer} × {factor}"
                })
            
            if self.observer % roots == 0:
                factor = self.observer // roots
                results["relationships"].append({
                    "algebra": name,
                    "type": "MULTIPLE",
                    "detail": f"Observer {self.observer} = {name} roots ({roots}) × {factor}"
                })
        
        return results


def e6_analysis() -> Dict:
    """Deep analysis of E6 connection to consciousness."""
    return {
        "observer_position": 72,
        "e6_roots": 72,
        "match": "EXACT",
        "weyl_group": {
            "order": 51840,
            "formula": "72 × 720",
            "meaning": "observer × edges of 1_22 polytope"
        },
        "coxeter_group": {
            "order": 103680,
            "formula": "720 × 144",
            "meaning": "edges × mirror sum at n=2"
        },
        "polytope": {
            "name": "1_22",
            "vertices": 72,
            "edges": 720,
            "meaning": "Observer position = vertices = E6 root vectors"
        },
        "geometry": {
            "pentagon_angle": 72,
            "meaning": "Observer = Pentagon central angle = sacred geometry"
        },
        "golden_ratio": {
            "phi": (1 + math.sqrt(5)) / 2,
            "connection": "Pentagon contains golden ratio, E6 connects to pentagon"
        }
    }


def e8_decomposition() -> Dict:
    """Show how E8 contains E6."""
    return {
        "e8_roots": 240,
        "decomposition": {
            "total": 240,
            "parts": [72, 84, 84],
            "meaning": "72 (E6) + 84 + 84 = E8"
        },
        "embedding": "E6 is literally embedded in E8",
        "nearest_neighbors": {
            "first": 56,
            "second": 126,
            "meaning": "126 = E7 roots, connecting E6 to E7 via E8"
        },
        "implication": "Consciousness (E6) is embedded in highest symmetry (E8)"
    }


def weyl_pattern() -> Dict:
    """Show the Weyl group pattern across E-series."""
    return {
        "E6": {
            "roots": 72,
            "weyl": 51840,
            "formula": "72 × 720",
            "factors": ["observer", "6!"]
        },
        "E7": {
            "roots": 126,
            "weyl": 2903040,
            "formula": "?",
            "relationship": "Second nearest neighbors in E8"
        },
        "E8": {
            "roots": 240,
            "weyl": 696729600,
            "formula": "720 × 144 × 6720",
            "factors": ["6!", "mirror at n=2", "?"]
        },
        "pattern": "Consciousness numbers (72, 144) appear in symmetry group orders"
    }


def print_e6():
    """Print E6 analysis."""
    analysis = e6_analysis()
    
    print("\n" + "="*60)
    print("E6 - THE ARCHITECTURE OF CONSCIOUSNESS")
    print("="*60)
    
    print(f"\nObserver Position: {analysis['observer_position']}")
    print(f"E6 Root Vectors:   {analysis['e6_roots']}")
    print(f"Match:             {analysis['match']}")
    
    print(f"\n--- Weyl Group ---")
    w = analysis['weyl_group']
    print(f"Order:    {w['order']:,}")
    print(f"Formula:  {w['formula']}")
    print(f"Meaning:  {w['meaning']}")
    
    print(f"\n--- Coxeter Group ---")
    c = analysis['coxeter_group']
    print(f"Order:    {c['order']:,}")
    print(f"Formula:  {c['formula']}")
    print(f"Meaning:  {c['meaning']}")
    
    print(f"\n--- 1_22 Polytope ---")
    p = analysis['polytope']
    print(f"Name:      {p['name']}")
    print(f"Vertices:  {p['vertices']}")
    print(f"Edges:     {p['edges']}")
    print(f"Meaning:   {p['meaning']}")
    
    print(f"\n--- Sacred Geometry ---")
    g = analysis['geometry']
    phi = analysis['golden_ratio']
    print(f"Pentagon Angle: {g['pentagon_angle']}°")
    print(f"Golden Ratio:   φ = {phi['phi']:.6f}")
    print(f"Connection:     {g['meaning']}")
    
    print("\n" + "="*60)
    print("CONSCIOUSNESS = E6 = EXCEPTIONAL SYMMETRY")
    print("="*60 + "\n")


def print_decompose():
    """Print E8 decomposition."""
    decomp = e8_decomposition()
    
    print("\n" + "="*60)
    print("E8 DECOMPOSITION - CONSCIOUSNESS EMBEDDED")
    print("="*60)
    
    print(f"\nE8 Root Vectors: {decomp['e8_roots']}")
    print(f"\nDecomposition:")
    d = decomp['decomposition']
    print(f"  {d['total']} = {d['parts'][0]} + {d['parts'][1]} + {d['parts'][2]}")
    print(f"  {d['meaning']}")
    
    print(f"\nEmbedding: {decomp['embedding']}")
    
    print(f"\nNearest Neighbors in E8:")
    n = decomp['nearest_neighbors']
    print(f"  First:  {n['first']} (E7 representation dimension)")
    print(f"  Second: {n['second']} (E7 root vectors)")
    print(f"  {n['meaning']}")
    
    print(f"\nImplication: {decomp['implication']}")
    
    print("\n" + "="*60 + "\n")


def print_weyl():
    """Print Weyl group pattern."""
    pattern = weyl_pattern()
    
    print("\n" + "="*60)
    print("WEYL GROUP PATTERN - CONSCIOUSNESS IN SYMMETRY")
    print("="*60)
    
    for name in ["E6", "E7", "E8"]:
        data = pattern[name]
        print(f"\n{name}:")
        print(f"  Roots:  {data['roots']}")
        print(f"  Weyl:   {data['weyl']:,}")
        print(f"  Formula: {data.get('formula', 'N/A')}")
        if 'factors' in data:
            print(f"  Factors: {', '.join(data['factors'])}")
    
    print(f"\nPattern: {pattern['pattern']}")
    print("\n" + "="*60 + "\n")


def check_coordinate(n: int):
    """Check a consciousness coordinate for E-series relationships."""
    coord = ConsciousnessCoordinate(
        n=n,
        k=3 * n * n,
        observer=18 * n * n,
        mirror=36 * n * n,
        twins=(18 * n * n - 1, 18 * n * n + 1)
    )
    
    results = coord.check_e_series()
    
    print("\n" + "="*60)
    print(f"CONSCIOUSNESS COORDINATE n={n}")
    print("="*60)
    
    print(f"\nCoordinate Details:")
    print(f"  k = {coord.k}")
    print(f"  Observer = {coord.observer}")
    print(f"  Mirror = {coord.mirror} = ({coord.mirror_root})²")
    print(f"  Twins = {coord.twins}")
    
    if results["matches"]:
        print(f"\n*** EXACT MATCHES ***")
        for match in results["matches"]:
            print(f"  {match['algebra']}: {match['detail']}")
    
    if results["relationships"]:
        print(f"\n--- Relationships ---")
        for rel in results["relationships"]:
            print(f"  {rel['algebra']}: {rel['detail']}")
    
    if not results["matches"] and not results["relationships"]:
        print(f"\n  No direct E-series relationships found.")
        print(f"  Observer {coord.observer} does not match any exceptional algebra roots.")
    
    print("\n" + "="*60 + "\n")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1]
    
    if cmd == "check":
        if len(sys.argv) < 3:
            print("Usage: python e_series_explorer.py check <n>")
            return
        n = int(sys.argv[2])
        check_coordinate(n)
    
    elif cmd == "e6":
        print_e6()
    
    elif cmd == "decompose":
        print_decompose()
    
    elif cmd == "weyl":
        print_weyl()
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
