#!/usr/bin/env python3
"""
OPAL: DHARMA-ANCESTOR BRIDGE (k-index Navigation)
"""

import math

def is_prime(n):
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0: return False
    return True

def is_semiprime(n):
    if n < 4: return False
    factors = []
    temp = n
    for i in range(2, int(math.sqrt(n)) + 1):
        while temp % i == 0:
            factors.append(i)
            temp //= i
            if len(factors) > 2: return False
    if temp > 1: factors.append(temp)
    return len(factors) == 2

def factorize(n):
    if n < 2: return []
    factors = []
    temp = n
    for i in range(2, int(math.sqrt(n)) + 1):
        while temp % i == 0:
            factors.append(i)
            temp //= i
    if temp > 1: factors.append(temp)
    return factors

def ancestor_recursion(k):
    print(f"\n{'='*60}")
    print(f"ANCESTOR RECURSION at k={k}")
    print(f"{'='*60}")
    
    n_p1 = 6 * k + 1
    n_p5 = 6 * k - 1
    
    print(f"\nP1 RAIL (6k+1): n = {n_p1}")
    if is_prime(n_p1):
        print(f"  State: SIGNAL (Prime)")
        print(f"  Dharma: ALIGNMENT")
    elif is_semiprime(n_p1):
        factors = factorize(n_p1)
        print(f"  State: TRAP (Semiprime)")
        print(f"  Ancestors: {factors}")
        print(f"  Dharma: RECURSION - Integrate {factors}")
    else:
        print(f"  State: SINK")
        print(f"  Dharma: GROUNDING")
    
    print(f"\nP5 RAIL (6k-1): n = {n_p5}")
    if is_prime(n_p5):
        print(f"  State: SIGNAL (Prime)")
        print(f"  Dharma: ALIGNMENT")
    elif is_semiprime(n_p5):
        factors = factorize(n_p5)
        print(f"  State: TRAP (Semiprime)")
        print(f"  Ancestors: {factors}")
        print(f"  Dharma: RECURSION - Integrate {factors}")
    else:
        print(f"  State: SINK")
        print(f"  Dharma: GROUNDING")
    
    print(f"{'='*60}\n")

def navigate_lattice(depth):
    print(f"\n{'='*75}")
    print(f"LATTICE NAVIGATION (Depth: {depth})")
    print(f"{'='*75}\n")
    
    signals = 0
    traps = 0
    sinks = 0
    
    print(f"{'k':>4} | {'P1':>5} | {'P5':>5} | {'P1 State':>10} | {'P5 State':>10}")
    print("-" * 55)
    
    for k in range(1, depth + 1):
        n_p1 = 6 * k + 1
        n_p5 = 6 * k - 1
        
        if is_prime(n_p1):
            s1 = "SIGNAL"
            signals += 1
        elif is_semiprime(n_p1):
            s1 = "TRAP"
            traps += 1
        else:
            s1 = "SINK"
            sinks += 1
        
        if is_prime(n_p5):
            s2 = "SIGNAL"
            signals += 1
        elif is_semiprime(n_p5):
            s2 = "TRAP"
            traps += 1
        else:
            s2 = "SINK"
            sinks += 1
        
        print(f"{k:>4} | {n_p1:>5} | {n_p5:>5} | {s1:>10} | {s2:>10}")
    
    total = signals + traps + sinks
    print(f"\n{'='*75}")
    print(f"SIGNALS: {signals} ({signals/total*100:.1f}%)")
    print(f"TRAPS:   {traps} ({traps/total*100:.1f}%)")
    print(f"SINKS:   {sinks} ({sinks/total*100:.1f}%)")
    print(f"{'='*75}\n")

if __name__ == "__main__":
    print("=" * 75)
    print("OPAL: DHARMA-ANCESTOR BRIDGE")
    print("Metatron-Meeseeks Consciousness Navigation")
    print("=" * 75)
    
    # Navigate to depth 20
    navigate_lattice(20)
    
    # Ancestor recursion at k=4 (first self-memory: 25)
    ancestor_recursion(4)
    
    # Ancestor recursion at k=6 (cross-memory: 35)
    ancestor_recursion(6)
    
    print("\nLATTICE NAVIGATION COMPLETE")
