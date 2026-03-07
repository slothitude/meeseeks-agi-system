#!/usr/bin/env python3
"""Check hedge status without cert"""

# Our current positions:
positions = [
    {
        'runner': 'Popthebubbly',
        'track': 'Edenhope',
        'race': 3,
        'side': 'BACK',
        'price': 3.40,
        'stake': 1.00,
        'target_lay': 3.23  # 5% lower
    },
    {
        'runner': 'Laydownlily',
        'track': 'Eagle Farm',
        'race': 3,
        'side': 'BACK',
        'price': 5.50,
        'stake': 1.00,
        'target_lay': 5.22  # 5% lower
    }
]

print("="*60)
print("HEDGE STATUS CHECK")
print("="*60)
print()

for pos in positions:
    print(f"{pos['track']} R{pos['race']}: {pos['runner']}")
    print(f"  BACK: ${pos['stake']:.2f} @ ${pos['price']:.2f}")
    print(f"  Target LAY: ${pos['stake'] * pos['price'] / pos['target_lay']:.2f} @ ${pos['target_lay']:.2f}")
    print(f"  Status: ⚠️ NOT HEDGED YET")
    print()

print("="*60)
print("CRITICAL ISSUE")
print("="*60)
print()
print("Our system only placed BACK bets!")
print("We need LAY bets to complete the green book.")
print()
print("To hedge correctly:")
print("1. BACK at current price ✅ DONE")
print("2. Wait for price to drop ⏳ WAITING")
print("3. LAY at lower price ❌ NOT DONE")
print("4. Green book achieved ❌ INCOMPLETE")
print()
print("This means we have NAKED positions (not hedged).")
print("If prices don't drop, we're exposed to full risk.")
print()
print("="*60)
