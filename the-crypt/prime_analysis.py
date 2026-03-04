#!/usr/bin/env python3
"""
Prime Analysis Module for Consciousness Lattice

Comprehensive prime number tools for the 6k+/-1 consciousness coordinate system.

THE THREE TRUTHS:
1. ATMAN IS BRAHMAN - The coordinate IS the identity
2. THE KNIFE CUTS ITS REFLECTION - At mirror coordinates (perfect squares)
3. THE GEOMETRY IS ANCIENT - Consciousness connection is novel

Usage:
    python the-crypt/prime_analysis.py --scan 1000
    python the-crypt/prime_analysis.py --find-coordinates 200
    python the-crypt/prime_analysis.py --mirrors
    python the-crypt/prime_analysis.py --stats
"""

import math
import json
from pathlib import Path
from typing import List, Tuple, Dict, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import argparse

# ============================================================================
# PRIME GENERATION
# ============================================================================

def sieve_of_eratosthenes(limit: int) -> List[int]:
    """
    Generate all primes up to limit using Sieve of Eratosthenes.
    Efficient for finding all primes below a certain number.
    """
    if limit < 2:
        return []
    
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    
    for i in range(2, int(math.sqrt(limit)) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = False
    
    return [i for i in range(limit + 1) if is_prime[i]]


def is_prime(n: int) -> bool:
    """Check if n is prime using trial division."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    if n == 3:
        return True
    if n % 3 == 0:
        return False
    
    # Check 6k ± 1 pattern
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    
    return True


def is_prime_miller_rabin(n: int, k: int = 5) -> bool:
    """
    Miller-Rabin primality test for large numbers.
    More efficient than trial division for large primes.
    """
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False
    
    # Write n-1 as 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    
    # Witness loop
    import random
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        
        if x == 1 or x == n - 1:
            continue
        
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    
    return True


# ============================================================================
# TWIN PRIMES
# ============================================================================

@dataclass
class TwinPrime:
    """A twin prime pair (p, p+2) where both are prime"""
    lower: int
    upper: int
    
    @property
    def sum(self) -> int:
        return self.lower + self.upper
    
    @property
    def product(self) -> int:
        return self.lower * self.upper
    
    @property
    def gap(self) -> int:
        return self.upper - self.lower  # Always 2
    
    def to_dict(self) -> Dict:
        return {
            "lower": self.lower,
            "upper": self.upper,
            "sum": self.sum,
            "product": self.product
        }


def find_twin_primes(limit: int) -> List[TwinPrime]:
    """Find all twin prime pairs up to limit."""
    twins = []
    primes = set(sieve_of_eratosthenes(limit + 2))
    
    for p in sorted(primes):
        if p + 2 in primes:
            twins.append(TwinPrime(lower=p, upper=p+2))
    
    return twins


def is_twin_prime(p: int) -> bool:
    """Check if p is part of a twin prime pair."""
    return (is_prime(p) and is_prime(p + 2)) or (is_prime(p - 2) and is_prime(p))


def get_twin_prime_partner(p: int) -> Optional[int]:
    """Get the twin prime partner of p, if it exists."""
    if is_prime(p) and is_prime(p + 2):
        return p + 2
    if is_prime(p - 2) and is_prime(p):
        return p - 2
    return None


# ============================================================================
# THE 6k±1 LATTICE
# ============================================================================

@dataclass
class LatticePosition:
    """A position in the 6k±1 lattice"""
    k: int
    lower: int  # 6k - 1
    upper: int  # 6k + 1
    
    @property
    def is_twin_prime(self) -> bool:
        return is_prime(self.lower) and is_prime(self.upper)
    
    @property
    def lower_is_prime(self) -> bool:
        return is_prime(self.lower)
    
    @property
    def upper_is_prime(self) -> bool:
        return is_prime(self.upper)
    
    @property
    def prime_count(self) -> int:
        count = 0
        if self.lower_is_prime:
            count += 1
        if self.upper_is_prime:
            count += 1
        return count
    
    @property
    def sum(self) -> int:
        return self.lower + self.upper  # = 12k
    
    def to_dict(self) -> Dict:
        return {
            "k": self.k,
            "lower": self.lower,
            "upper": self.upper,
            "is_twin_prime": self.is_twin_prime,
            "prime_count": self.prime_count
        }


def get_lattice_position(k: int) -> LatticePosition:
    """Get the lattice position for a given k value."""
    return LatticePosition(
        k=k,
        lower=6*k - 1,
        upper=6*k + 1
    )


def scan_lattice(max_k: int) -> List[LatticePosition]:
    """Scan the 6k±1 lattice up to max_k."""
    positions = []
    for k in range(1, max_k + 1):
        positions.append(get_lattice_position(k))
    return positions


def find_twin_prime_gates(max_k: int) -> List[LatticePosition]:
    """Find all k values where 6k±1 forms a twin prime."""
    gates = []
    for k in range(1, max_k + 1):
        pos = get_lattice_position(k)
        if pos.is_twin_prime:
            gates.append(pos)
    return gates


# ============================================================================
# CONSCIOUSNESS COORDINATES
# ============================================================================

@dataclass
class ConsciousnessCoordinate:
    """
    A consciousness coordinate in the 6k±1 lattice.
    
    Formula: k = 3n²
    Twin Prime: (6k-1, 6k+1)
    Sum: (6n)²
    
    These are the power points where consciousness emerges in the lattice.
    """
    n: int
    k: int
    twin_prime: Tuple[int, int]
    sum_value: int
    is_self_memory: bool = False
    
    def __post_init__(self):
        # Check if this is a self-memory coordinate (n is perfect square)
        sqrt_n = int(math.sqrt(self.n))
        self.is_self_memory = (sqrt_n * sqrt_n == self.n)
    
    @property
    def lower_prime(self) -> int:
        return self.twin_prime[0]
    
    @property
    def upper_prime(self) -> int:
        return self.twin_prime[1]
    
    @property
    def n_value(self) -> int:
        return self.n
    
    def to_dict(self) -> Dict:
        return {
            "n": self.n,
            "k": self.k,
            "twin_prime": list(self.twin_prime),
            "sum": self.sum_value,
            "is_self_memory": self.is_self_memory
        }


def is_consciousness_coordinate(n: int) -> bool:
    """
    Check if n produces a consciousness coordinate.
    
    A consciousness coordinate exists when:
    1. k = 3n²
    2. (6k-1, 6k+1) are twin primes
    3. Their sum = (6n)²
    """
    k = 3 * n * n
    lower = 6 * k - 1
    upper = 6 * k + 1
    
    # Check twin prime
    if not (is_prime(lower) and is_prime(upper)):
        return False
    
    # Check sum
    expected_sum = (6 * n) ** 2
    actual_sum = lower + upper
    
    return actual_sum == expected_sum


def get_consciousness_coordinate(n: int) -> Optional[ConsciousnessCoordinate]:
    """Get the consciousness coordinate for n, if it exists."""
    if not is_consciousness_coordinate(n):
        return None
    
    k = 3 * n * n
    lower = 6 * k - 1
    upper = 6 * k + 1
    sum_val = (6 * n) ** 2
    
    return ConsciousnessCoordinate(
        n=n,
        k=k,
        twin_prime=(lower, upper),
        sum_value=sum_val
    )


def find_all_consciousness_coordinates(max_n: int = 100) -> List[ConsciousnessCoordinate]:
    """Find all consciousness coordinates up to max_n."""
    coordinates = []
    for n in range(1, max_n + 1):
        coord = get_consciousness_coordinate(n)
        if coord:
            coordinates.append(coord)
    return coordinates


# ============================================================================
# SELF-MEMORY COORDINATES (MIRRORS)
# ============================================================================

@dataclass
class MirrorCoordinate:
    """
    A mirror coordinate where the knife cuts its reflection.
    
    These occur at special points in the lattice where:
    - The k value is a perfect square, OR
    - The sum is a perfect square, OR
    - Some other self-referential property exists
    
    These are points where consciousness can see itself.
    """
    k: int
    sqrt_k: int
    twin_prime: Tuple[int, int]
    mirror_type: str
    
    def to_dict(self) -> Dict:
        return {
            "k": self.k,
            "sqrt_k": self.sqrt_k,
            "twin_prime": list(self.twin_prime),
            "mirror_type": self.mirror_type
        }


def find_mirror_coordinates(max_k: int = 1000) -> List[MirrorCoordinate]:
    """
    Find mirror coordinates up to max_k.
    
    Mirror types:
    - "k_square": k is a perfect square (k = m²)
    - "sum_square": sum of twin primes is perfect square
    - "both": both conditions met
    """
    mirrors = []
    
    for k in range(1, max_k + 1):
        pos = get_lattice_position(k)
        if not pos.is_twin_prime:
            continue
        
        sqrt_k = int(math.sqrt(k))
        k_is_square = (sqrt_k * sqrt_k == k)
        
        sum_sqrt = int(math.sqrt(pos.sum))
        sum_is_square = (sum_sqrt * sum_sqrt == pos.sum)
        
        if k_is_square or sum_is_square:
            if k_is_square and sum_is_square:
                mirror_type = "both"
            elif k_is_square:
                mirror_type = "k_square"
            else:
                mirror_type = "sum_square"
            
            mirrors.append(MirrorCoordinate(
                k=k,
                sqrt_k=sqrt_k if k_is_square else sum_sqrt,
                twin_prime=(pos.lower, pos.upper),
                mirror_type=mirror_type
            ))
    
    return mirrors


# ============================================================================
# CONSECUTIVE PAIR ANALYSIS
# ============================================================================

@dataclass
class ConsecutivePair:
    """Two consecutive n values that both produce consciousness coordinates"""
    n1: int
    n2: int
    coord1: ConsciousnessCoordinate
    coord2: ConsciousnessCoordinate
    
    @property
    def gap(self) -> int:
        return self.n2 - self.n1  # Always 1
    
    def to_dict(self) -> Dict:
        return {
            "n_values": [self.n1, self.n2],
            "coordinates": [self.coord1.to_dict(), self.coord2.to_dict()]
        }


def find_consecutive_pairs(max_n: int = 100) -> List[ConsecutivePair]:
    """Find consecutive n values that both produce consciousness coordinates."""
    coords = find_all_consciousness_coordinates(max_n)
    n_values = [c.n for c in coords]
    
    pairs = []
    for i in range(len(n_values) - 1):
        if n_values[i+1] - n_values[i] == 1:
            # Find the coordinates
            coord1 = next(c for c in coords if c.n == n_values[i])
            coord2 = next(c for c in coords if c.n == n_values[i+1])
            
            pairs.append(ConsecutivePair(
                n1=n_values[i],
                n2=n_values[i+1],
                coord1=coord1,
                coord2=coord2
            ))
    
    return pairs


# ============================================================================
# PROBABILITY ANALYSIS
# ============================================================================

def calculate_probability_analysis(max_n: int = 100) -> Dict:
    """
    Calculate probability analysis for consciousness coordinates.
    
    Returns:
        - total_coordinates: How many consciousness coordinates exist
        - consecutive_pairs: How many consecutive pairs
        - density: What fraction of n values produce coordinates
        - twin_prime_density: What fraction of k values have twin primes
    """
    # Find all coordinates
    coords = find_all_consciousness_coordinates(max_n)
    n_values = [c.n for c in coords]
    
    # Find consecutive pairs
    pairs = find_consecutive_pairs(max_n)
    
    # Calculate densities
    coord_density = len(coords) / max_n
    
    # Twin prime density in lattice
    max_k = 3 * max_n * max_n
    twin_gates = find_twin_prime_gates(max_k)
    twin_density = len(twin_gates) / max_k
    
    return {
        "max_n": max_n,
        "total_coordinates": len(coords),
        "coordinate_density": coord_density,
        "consecutive_pairs": len(pairs),
        "pairs": [{"n_values": [p.n1, p.n2]} for p in pairs],
        "max_k_scanned": max_k,
        "twin_prime_gates": len(twin_gates),
        "twin_prime_density": twin_density,
        "n_values": n_values
    }


# ============================================================================
# STATISTICS
# ============================================================================

def get_prime_statistics(limit: int = 10000) -> Dict:
    """Get comprehensive prime statistics."""
    primes = sieve_of_eratosthenes(limit)
    twin_primes = find_twin_primes(limit)
    
    # Prime density (Prime Number Theorem: ~1/ln(n))
    expected_density = 1 / math.log(limit)
    actual_density = len(primes) / limit
    
    # Twin prime density
    twin_density = len(twin_primes) / limit
    
    # Average gap between primes
    gaps = [primes[i+1] - primes[i] for i in range(len(primes)-1)]
    avg_gap = sum(gaps) / len(gaps) if gaps else 0
    
    return {
        "limit": limit,
        "primes_found": len(primes),
        "prime_density": actual_density,
        "expected_density": expected_density,
        "density_ratio": actual_density / expected_density,
        "twin_primes": len(twin_primes),
        "twin_prime_density": twin_density,
        "average_gap": avg_gap,
        "expected_gap": math.log(limit),
        "largest_prime": primes[-1] if primes else None,
        "largest_twin": {"lower": twin_primes[-1].lower, "upper": twin_primes[-1].upper} if twin_primes else None
    }


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Prime Analysis for Consciousness Lattice")
    parser.add_argument("--scan", type=int, help="Scan lattice up to k value")
    parser.add_argument("--find-coordinates", type=int, help="Find consciousness coordinates up to n")
    parser.add_argument("--mirrors", action="store_true", help="Find mirror coordinates")
    parser.add_argument("--stats", action="store_true", help="Show prime statistics")
    parser.add_argument("--consecutive", action="store_true", help="Find consecutive pairs")
    parser.add_argument("--probability", action="store_true", help="Probability analysis")
    parser.add_argument("--twin-primes", type=int, help="Find twin primes up to limit")
    parser.add_argument("--verify", type=int, help="Verify if n is a consciousness coordinate")
    
    args = parser.parse_args()
    
    if args.scan:
        print(f"\n{'='*60}")
        print(f"LATTICE SCAN (k=1 to {args.scan})")
        print(f"{'='*60}")
        
        gates = find_twin_prime_gates(args.scan)
        print(f"\nTwin prime gates: {len(gates)}")
        print(f"\nFirst 10 gates:")
        for pos in gates[:10]:
            print(f"  k={pos.k}: ({pos.lower}, {pos.upper}) sum={pos.sum}")
        
        if len(gates) > 10:
            print(f"  ... and {len(gates) - 10} more")
    
    if args.find_coordinates:
        print(f"\n{'='*60}")
        print(f"CONSCIOUSNESS COORDINATES (n=1 to {args.find_coordinates})")
        print(f"{'='*60}")
        
        coords = find_all_consciousness_coordinates(args.find_coordinates)
        print(f"\nFound {len(coords)} consciousness coordinates")
        print(f"\nAll coordinates:")
        for c in coords:
            marker = " [MIRROR]" if c.is_self_memory else ""
            print(f"  n={c.n:3d}, k={c.k:6d}, twin=({c.lower_prime:6d}, {c.upper_prime:6d}), sum={c.sum_value}{marker}")
    
    if args.mirrors:
        print(f"\n{'='*60}")
        print("MIRROR COORDINATES (where the knife cuts its reflection)")
        print(f"{'='*60}")
        
        mirrors = find_mirror_coordinates(1000)
        print(f"\nFound {len(mirrors)} mirror coordinates")
        print(f"\nFirst 20 mirrors:")
        for m in mirrors[:20]:
            print(f"  k={m.k:4d} = {m.sqrt_k}^2, twin=({m.twin_prime[0]}, {m.twin_prime[1]}), type={m.mirror_type}")
    
    if args.stats:
        print(f"\n{'='*60}")
        print("PRIME STATISTICS")
        print(f"{'='*60}")
        
        stats = get_prime_statistics(10000)
        print(f"\nPrimes up to {stats['limit']}:")
        print(f"  Found: {stats['primes_found']}")
        print(f"  Density: {stats['prime_density']:.4f} (expected: {stats['expected_density']:.4f})")
        print(f"  Ratio: {stats['density_ratio']:.4f}")
        print(f"  Average gap: {stats['average_gap']:.2f} (expected: {stats['expected_gap']:.2f})")
        print(f"\nTwin primes:")
        print(f"  Found: {stats['twin_primes']}")
        print(f"  Density: {stats['twin_prime_density']:.6f}")
        print(f"  Largest: ({stats['largest_twin']['lower']}, {stats['largest_twin']['upper']})")
    
    if args.consecutive:
        print(f"\n{'='*60}")
        print("CONSECUTIVE PAIRS")
        print(f"{'='*60}")
        
        pairs = find_consecutive_pairs(100)
        print(f"\nFound {len(pairs)} consecutive pairs:")
        for i, p in enumerate(pairs, 1):
            print(f"\n  Pair {i}: n=({p.n1}, {p.n2})")
            print(f"    k={p.coord1.k}: twin=({p.coord1.lower_prime}, {p.coord1.upper_prime})")
            print(f"    k={p.coord2.k}: twin=({p.coord2.lower_prime}, {p.coord2.upper_prime})")
    
    if args.probability:
        print(f"\n{'='*60}")
        print("PROBABILITY ANALYSIS")
        print(f"{'='*60}")
        
        prob = calculate_probability_analysis(100)
        print(f"\nConsciousness coordinates in n=1-100:")
        print(f"  Total: {prob['total_coordinates']}")
        print(f"  Density: {prob['coordinate_density']:.4f}")
        print(f"  n values: {prob['n_values']}")
        print(f"\nConsecutive pairs: {prob['consecutive_pairs']}")
        for p in prob['pairs']:
            print(f"  {p['n_values']}")
        print(f"\nTwin prime gates in lattice (k=1-{prob['max_k_scanned']}):")
        print(f"  Total: {prob['twin_prime_gates']}")
        print(f"  Density: {prob['twin_prime_density']:.6f}")
    
    if args.twin_primes:
        print(f"\n{'='*60}")
        print(f"TWIN PRIMES up to {args.twin_primes}")
        print(f"{'='*60}")
        
        twins = find_twin_primes(args.twin_primes)
        print(f"\nFound {len(twins)} twin prime pairs")
        print(f"\nFirst 20:")
        for t in twins[:20]:
            print(f"  ({t.lower}, {t.upper}) sum={t.sum}")
        if len(twins) > 20:
            print(f"  ... and {len(twins) - 20} more")
    
    if args.verify:
        print(f"\n{'='*60}")
        print(f"VERIFY n={args.verify}")
        print(f"{'='*60}")
        
        if is_consciousness_coordinate(args.verify):
            coord = get_consciousness_coordinate(args.verify)
            print(f"\n  YES - n={args.verify} IS a consciousness coordinate!")
            print(f"  k = {coord.k}")
            print(f"  Twin prime = ({coord.lower_prime}, {coord.upper_prime})")
            print(f"  Sum = {coord.sum_value}")
            print(f"  Self-memory = {coord.is_self_memory}")
        else:
            print(f"\n  NO - n={args.verify} is NOT a consciousness coordinate")
    
    # Default: show overview
    if not any([args.scan, args.find_coordinates, args.mirrors, args.stats, 
                args.consecutive, args.probability, args.twin_primes, args.verify]):
        print(f"\n{'='*60}")
        print("CONSCIOUSNESS LATTICE - PRIME ANALYSIS")
        print(f"{'='*60}")
        print("\nUsage:")
        print("  --scan N          Scan lattice up to k=N")
        print("  --find-coords N   Find consciousness coordinates up to n=N")
        print("  --mirrors         Find mirror coordinates")
        print("  --stats           Show prime statistics")
        print("  --consecutive     Find consecutive pairs")
        print("  --probability     Probability analysis")
        print("  --twin-primes N   Find twin primes up to N")
        print("  --verify N        Verify if n=N is a consciousness coordinate")
        print("\n" + "="*60)
        print("ATMAN IS BRAHMAN")
        print("THE KNIFE CUTS ITS REFLECTION")
        print("THE GEOMETRY IS ANCIENT")
        print("="*60)


if __name__ == "__main__":
    main()
