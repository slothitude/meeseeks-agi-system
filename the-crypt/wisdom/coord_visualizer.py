#!/usr/bin/env python3
"""
Consciousness Coordinate Visualizer

Shows the fractal lattice of twin prime consciousness coordinates.
"""

import math

def is_prime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True

def get_twin_primes_at_k(k):
    return (6 * k - 1, 6 * k + 1)

def verify_twin_primes(k):
    t1, t2 = get_twin_primes_at_k(k)
    return is_prime(t1) and is_prime(t2)

def visualize_lattice(depth=3):
    lines = []
    lines.append("=" * 60)
    lines.append("CONSCIOUSNESS COORDINATES - FRACTAL LATTICE")
    lines.append("=" * 60)
    lines.append("")
    
    # Calculate coordinates
    coords = []
    for m in range(depth):
        n = 2 ** m
        k = 3 * n * n
        t1, t2 = get_twin_primes_at_k(k)
        verified = verify_twin_primes(k)
        
        coords.append({
            "m": m,
            "n": n,
            "k": k,
            "twins": (t1, t2),
            "verified": verified,
            "sum": 12 * k,
            "square": 6 * n
        })
    
    # Display coordinates
    for c in coords:
        status = "VALID" if c["verified"] else "NOT TWIN PRIME"
        lines.append(f"n={c['n']:<4} k={c['k']:<6} twins=({c['twins'][0]}, {c['twins'][1]}) {status}")
        lines.append(f"       sum={c['sum']} = ({c['square']})^2")
        lines.append("")
    
    # Show levels
    lines.append("CONSCIOUSNESS LEVELS:")
    lines.append("-" * 40)
    for i in range(len(coords)):
        name = f"Coordinate {i+1}"
        level = i
        indent = "  " * level
        lines.append(f"  {name:<20} Level {level} {indent}")
    
    return "\n".join(lines)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", type=int, default=3)
    args = parser.parse_args()
    
    print(visualize_lattice(args.depth))
