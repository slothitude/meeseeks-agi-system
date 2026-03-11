#!/usr/bin/env python3
"""
Search for more triple conjunctions beyond n=100,000
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

def is_coordinate(n):
    """Check if n is a consciousness coordinate"""
    observer = 18 * n * n
    twin1 = observer - 1
    twin2 = observer + 1
    return is_prime(twin1) and is_prime(twin2)

def digital_sum(n):
    return sum(int(d) for d in str(n))

# Search for triple conjunctions
print('SEARCHING FOR TRIPLE CONJUNCTIONS')
print('='*60)
print()

conjunctions = []

# Check ranges
ranges = [
    (100000, 110000),
    (110000, 120000),
    (120000, 130000),
    (200000, 210000),
    (500000, 501000),
]

for start, end in ranges:
    print(f'Checking n={start} to n={end}...')

    coords = []
    for n in range(start, end):
        if is_coordinate(n):
            coords.append(n)

    print(f'  Found {len(coords)} coordinates')

    # Check for consecutive
    for i in range(len(coords) - 2):
        if coords[i+1] == coords[i] + 1 and coords[i+2] == coords[i] + 2:
            triple = (coords[i], coords[i+1], coords[i+2])
            ds = [digital_sum(n) for n in triple]
            conjunctions.append({
                'n_values': triple,
                'digital_sums': ds,
                'consecutive_ds': ds[1] == ds[0] + 1 and ds[2] == ds[1] + 1
            })

    if coords:
        print(f'  First: n={coords[0]}')
        print(f'  Last: n={coords[-1]}')

print()
print('='*60)
print(f'FOUND {len(conjunctions)} TRIPLE CONJUNCTIONS')
print('='*60)

for i, conj in enumerate(conjunctions, 1):
    print(f'{i}. n={conj["n_values"]}')
    print(f'   Digital sums: {conj["digital_sums"]}')
    print(f'   Consecutive: {conj["consecutive_ds"]}')
    print()

if not conjunctions:
    print('No new triple conjunctions found in searched ranges.')
    print('The two known conjunctions (Alpha, Beta) may be the only ones.')
