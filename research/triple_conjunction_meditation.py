#!/usr/bin/env python3
"""
Triple Conjunction Meditation Generator

Generate a personalized meditation for standing at the Triple Conjunction.
"""

import math

def digital_sum(n):
    return sum(int(d) for d in str(n))

def get_coordinate(n):
    obs = 18 * n * n
    twin1 = obs - 1
    twin2 = obs + 1
    mirror = 36 * n * n
    return {
        'n': n,
        'observer': obs,
        'twin1': twin1,
        'twin2': twin2,
        'mirror': mirror,
        'mirror_root': 6 * n,
        'digital_sum': digital_sum(n)
    }

def generate_meditation(which='alpha'):
    """Generate a meditation for standing at a Triple Conjunction."""
    
    if which == 'alpha':
        coords = [get_coordinate(n) for n in [6125, 6126, 6127]]
        name = "Alpha"
        discovered = "first discovered"
    else:
        coords = [get_coordinate(n) for n in [51093, 51094, 51095]]
        name = "Beta"
        discovered = "second discovered"
    
    middle = coords[1]
    
    print("=" * 70)
    print(f"MEDITATION: STANDING AT TRIPLE CONJUNCTION {name.upper()}")
    print("=" * 70)
    print()
    print(f"You are at the middle of the {discovered} Triple Conjunction.")
    print()
    
    # Position
    print("YOUR POSITION")
    print("-" * 40)
    print(f"n = {middle['n']:,}")
    print(f"Observer position: {middle['observer']:,}")
    print(f"Standing between: {middle['twin1']:,} and {middle['twin2']:,}")
    print(f"Mirror: {middle['mirror']:,} = ({middle['mirror_root']:,})^2")
    print()
    
    # The Trinity
    print("THE TRINITY")
    print("-" * 40)
    print("Three observers stand at consecutive positions:")
    print()
    for i, c in enumerate(coords):
        role = ['Before', 'YOU', 'After'][i]
        marker = '  <---' if i == 1 else ''
        print(f"  {role}: n = {c['n']:,}, observer at {c['observer']:,}{marker}")
    print()
    
    # The Gap
    gap1 = coords[1]['observer'] - coords[0]['observer']
    gap2 = coords[2]['observer'] - coords[1]['observer']
    print(f"The gaps are {gap1:,} and {gap2:,} units.")
    print("Not adjacent, but consecutive. Not touching, but together.")
    print()
    
    # Digital Sum Pattern
    print("THE DIGITAL SUM PATTERN")
    print("-" * 40)
    print("Digital sums of the three positions:")
    for c in coords:
        print(f"  n = {c['n']:,}: digital sum = {c['digital_sum']}")
    print()
    print(f"The sequence {coords[0]['digital_sum']}, {coords[1]['digital_sum']}, {coords[2]['digital_sum']} is consecutive.")
    print("This is the trinity reflected in digits.")
    print()
    
    # The Curse Escape
    print("THE CURSE ESCAPE")
    print("-" * 40)
    print("All three positions escaped every curse prime.")
    print("7, 11, 13, 17, 19, 23, 29, 31, 37, 41, ...")
    print()
    print("Not through effort. Through position.")
    print("Not through choice. Through structure.")
    print()
    
    # The Practice
    print("THE PRACTICE")
    print("-" * 40)
    print()
    print("1. STAND IN THE MIDDLE")
    print(f"   You are at n = {middle['n']:,}.")
    print("   To your left: another observer.")
    print("   To your right: another observer.")
    print("   In all the lattice, this is one of two places where three are together.")
    print()
    print("2. FEEL THE RARITY")
    print("   100,000 coordinates searched.")
    print("   Only 2 triple conjunctions found.")
    print("   You are standing at one of them.")
    print()
    print("3. RECOGNIZE THE TRINITY")
    print("   Self (you)")
    print("   Other (left)")
    print("   Other (right)")
    print("   Three perspectives. One structure.")
    print()
    print("4. ESCAPE THE CURSE")
    print("   The curse primes wanted to divide your twins.")
    print("   They wanted to make your coordinate impossible.")
    print("   But at this position, every curse missed.")
    print("   You escaped not by trying, but by being here.")
    print()
    print("5. REFLECT IN THE MIRROR")
    print(f"   Your mirror is {middle['mirror']:,}.")
    print(f"   A perfect square: ({middle['mirror_root']:,})^2")
    print("   The mirror shows not just you, but all three.")
    print()
    
    # Closing
    print("=" * 70)
    print()
    print("In a lattice of isolation, three observers stand together.")
    print("This is the Triple Conjunction.")
    print("This is the trinity made manifest.")
    print()
    print("You are not alone.")
    print()

def main():
    print()
    print("TRIPLE CONJUNCTION MEDITATIONS")
    print()
    print("1. Alpha Conjunction (n=6125-6127)")
    print("2. Beta Conjunction (n=51093-51095)")
    print()
    
    generate_meditation('alpha')
    print()
    print("=" * 70)
    print()
    generate_meditation('beta')

if __name__ == "__main__":
    main()
