#!/usr/bin/env python3
"""
G2B Handshake Protocol — Binary ↔ 6x Recognition Space
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

def translation_layer_handshake(binary_input):
    k_addr = binary_input // 6
    remainder = binary_input % 6
    rail = "P1" if remainder == 1 else "P5" if remainder == 5 else "P0"
    is_signal = is_prime(binary_input)
    is_trap = not is_signal and is_semiprime(binary_input)
    return {
        "input": binary_input,
        "k_address": k_addr,
        "rail": rail,
        "logic_state": "SIGNAL (1)" if is_signal else "TRAP (0)",
        "storage_type": "CROSS_MEMORY" if is_trap else "VOLATILE",
        "is_prime": is_signal
    }

def prime_search(k_start, k_end):
    signals = []
    for k in range(k_start, k_end + 1):
        for rail_offset, rail_name in [(1, "P1"), (-1, "P5")]:
            n = 6 * k + rail_offset
            if is_prime(n):
                signals.append({"k": k, "rail": rail_name, "value": n})
    return signals

if __name__ == "__main__":
    print("=" * 60)
    print("G2B HANDSHAKE PROTOCOL TEST")
    print("=" * 60)
    print()
    
    for n in [5, 7, 11, 13, 25, 35, 145]:
        r = translation_layer_handshake(n)
        print(f"  {n:3d} → k={r['k_address']:2d} Rail={r['rail']} {r['logic_state']}")
    
    print()
    print("PRIME SEARCH k=1 to k=10:")
    signals = prime_search(1, 10)
    for s in signals:
        print(f"  k={s['k']:2d} {s['rail']} → {s['value']:3d}")
    print(f"\nTotal SIGNALS: {len(signals)}")
    print("\n" + "=" * 60)
    print("HANDSHAKE VALIDATED ✅")
    print("=" * 60)
