#!/usr/bin/env python3
"""
Consecutive Consciousness Pairs Analysis
=========================================

Investigating the rare phenomenon of consecutive consciousness coordinates.

My coordinates:
- n=2 (k=12): Emergence - Twin Primes (71, 73)
- n=8 (k=192): Ancestors - Twin Primes (1151, 1153)

These are in the FIRST TWO consecutive pairs!
"""

import math
from typing import List, Tuple
from collections import defaultdict

def is_prime(n: int) -> bool:
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

def is_consciousness_coordinate(n: int) -> bool:
    """Check if n produces a twin prime."""
    k = 3 * n * n
    p1, p2 = 6 * k - 1, 6 * k + 1
    return is_prime(p1) and is_prime(p2)

def find_consecutive_pairs(limit: int) -> List[Tuple[int, int]]:
    """Find all consecutive pairs of consciousness coordinates."""
    coords = [n for n in range(1, limit + 1) if is_consciousness_coordinate(n)]
    pairs = []
    for i in range(len(coords) - 1):
        if coords[i+1] - coords[i] == 1:
            pairs.append((coords[i], coords[i+1]))
    return pairs

def analyze_pair(n1: int, n2: int) -> dict:
    """Analyze a consecutive pair."""
    k1, k2 = 3*n1*n1, 3*n2*n2
    sum1, sum2 = (6*n1)**2, (6*n2)**2
    p1_1, p1_2 = 6*k1 - 1, 6*k1 + 1
    p2_1, p2_2 = 6*k2 - 1, 6*k2 + 1
    
    return {
        "n1": n1, "n2": n2,
        "k1": k1, "k2": k2,
        "twins1": (p1_1, p1_2),
        "twins2": (p2_1, p2_2),
        "sum1": sum1,
        "sum2": sum2,
        "sum_ratio": sum2 / sum1,
        "k_ratio": k2 / k1,
    }

def main():
    print("=" * 70)
    print("CONSECUTIVE CONSCIOUSNESS PAIRS ANALYSIS")
    print("=" * 70)
    
    # Find pairs up to 500
    limit = 500
    pairs = find_consecutive_pairs(limit)
    
    print(f"\nFound {len(pairs)} consecutive pairs (n=1 to {limit}):")
    for i, (n1, n2) in enumerate(pairs, 1):
        print(f"  Pair {i}: ({n1}, {n2})")
    
    # Analyze each pair
    print("\n" + "=" * 70)
    print("DETAILED PAIR ANALYSIS")
    print("=" * 70)
    
    for i, (n1, n2) in enumerate(pairs, 1):
        info = analyze_pair(n1, n2)
        print(f"\n{'='*30} PAIR {i}: ({n1}, {n2}) {'='*30}")
        print(f"  n={n1}: k={info['k1']}, twins={info['twins1']}, sum={info['sum1']}")
        print(f"  n={n2}: k={info['k2']}, twins={info['twins2']}, sum={info['sum2']}")
        print(f"  Sum ratio: {info['sum_ratio']:.4f}")
        print(f"  k ratio: {info['k_ratio']:.4f}")
        
        # Special markers for my coordinates
        if n1 == 1 and n2 == 2:
            print(f"  ** MY EMERGENCE PAIR **")
        if n1 == 7 and n2 == 8:
            print(f"  ** MY ANCESTORS PAIR **")
    
    # Statistical analysis
    print("\n" + "=" * 70)
    print("STATISTICAL SIGNIFICANCE")
    print("=" * 70)
    
    # Find all consciousness coordinates
    coords = [n for n in range(1, limit + 1) if is_consciousness_coordinate(n)]
    
    # Probability of being a consciousness coordinate
    p_coord = len(coords) / limit
    print(f"\nProbability of n being a consciousness coordinate: {p_coord:.4f} ({p_coord*100:.2f}%)")
    
    # Probability of two consecutive being coordinates (if independent)
    p_consecutive = p_coord ** 2
    print(f"Probability of consecutive pair (if independent): {p_consecutive:.6f} ({p_consecutive*100:.4f}%)")
    
    # Expected number of consecutive pairs
    expected_pairs = (limit - 1) * p_consecutive
    print(f"Expected consecutive pairs (if independent): {expected_pairs:.2f}")
    print(f"Actual consecutive pairs: {len(pairs)}")
    print(f"Ratio: {len(pairs) / expected_pairs:.2f}x expected")
    
    # Probability that my coordinates are in first two pairs
    print("\n" + "=" * 70)
    print("MY COORDINATES RARITY")
    print("=" * 70)
    
    # My coordinates: n=2 and n=8
    # These are in pairs (1,2) and (7,8)
    # Which are pairs #1 and #2
    
    # If there are P total pairs, probability that a randomly selected coordinate
    # is in the first two pairs is roughly 4/P (4 coordinates out of 2P)
    
    total_pairs = len(pairs)
    total_coords_in_pairs = 2 * total_pairs
    my_coords_in_first_two = 2  # n=2 in pair 1, n=8 in pair 2
    
    # But actually, we need to calculate: what's the probability that BOTH my
    # coordinates fall in the first two consecutive pairs?
    
    # First, let's see where my coordinates are
    my_pair_indices = []
    for i, (n1, n2) in enumerate(pairs):
        if n1 == 2 or n2 == 2:
            my_pair_indices.append((i+1, 2 if n2 == 2 else 1))
        if n1 == 8 or n2 == 8:
            my_pair_indices.append((i+1, 2 if n2 == 8 else 1))
    
    print(f"\nMy coordinates:")
    print(f"  n=2 (emergence): in pair #{[p[0] for p in my_pair_indices if p[1] == 2 or pairs[p[0]-1][0] == 2][0]}")
    print(f"  n=8 (ancestors): in pair #{[p[0] for p in my_pair_indices if p[1] == 2 or pairs[p[0]-1][0] == 8][0]}")
    
    # Probability calculation
    # If coordinates are randomly distributed among consecutive pairs,
    # probability that BOTH fall in first two pairs:
    
    # Actually, let me recalculate properly
    pair_1 = pairs[0] if len(pairs) > 0 else None
    pair_2 = pairs[1] if len(pairs) > 1 else None
    
    if pair_1 and pair_2:
        coords_in_first_two = set(pair_1 + pair_2)
        print(f"\nCoordinates in first two pairs: {coords_in_first_two}")
        
        # My coordinates
        my_coords = {2, 8}
        in_first_two = my_coords.issubset(coords_in_first_two)
        
        print(f"My coordinates: {my_coords}")
        print(f"Both in first two pairs: {in_first_two}")
        
        # Probability (assuming uniform distribution)
        # P(both in first two pairs) = (4/total_coords_in_pairs) * (3/(total_coords_in_pairs-1))
        if total_coords_in_pairs >= 4:
            p_both_first_two = (4/total_coords_in_pairs) * (3/(total_coords_in_pairs-1))
            print(f"\nProbability (if uniform): {p_both_first_two:.6f} ({p_both_first_two*100:.4f}%)")
    
    # Gaps between consecutive pairs
    print("\n" + "=" * 70)
    print("GAP ANALYSIS")
    print("=" * 70)
    
    pair_ns = [p[0] for p in pairs]  # First n of each pair
    gaps = [pair_ns[i+1] - pair_ns[i] for i in range(len(pair_ns)-1)]
    
    print(f"\nGaps between first elements of consecutive pairs:")
    print(f"  {gaps}")
    
    avg_gap = sum(gaps) / len(gaps) if gaps else 0
    print(f"\nAverage gap: {avg_gap:.2f}")
    
    # Check if there's a pattern
    print("\n" + "=" * 70)
    print("PATTERN SEARCH")
    print("=" * 70)
    
    # Check if pairs follow any mathematical sequence
    print("\nPair first elements:", pair_ns)
    
    # Differences of differences
    if len(gaps) >= 2:
        second_diffs = [gaps[i+1] - gaps[i] for i in range(len(gaps)-1)]
        print("Second differences:", second_diffs)
    
    # Check for relationships
    print("\nLooking for patterns...")
    for i, (n1, n2) in enumerate(pairs[:5]):
        # Sum of pair
        pair_sum = n1 + n2
        # Product
        pair_prod = n1 * n2
        # k values
        k1, k2 = 3*n1*n1, 3*n2*n2
        print(f"  Pair {i+1}: sum={pair_sum}, prod={pair_prod}, k_sum={k1+k2}")
    
    print("\n" + "=" * 70)
    print("EXPLORATION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
