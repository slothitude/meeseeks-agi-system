#!/usr/bin/env python3
"""Test script for spawn_meeseeks.py"""

import sys
import io

# Set stdout to UTF-8 for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from spawn_meeseeks import spawn_prompt

# Test 1: Atman mode
print("=" * 60)
print("TEST 1: ATMAN MODE")
print("=" * 60)
config = spawn_prompt(
    task="Say hello",
    meeseeks_type="standard",
    atman=True
)
print(f"Type: {config['type']}")
print(f"Atman: {config['atman']}")
print(f"Brahman: {config['brahman']}")
print("\nChecking for Atman format in output...")
if "🪷 ATMAN OBSERVES:" in config['task']:
    print("✅ SUCCESS: Atman observation format found!")
else:
    print("❌ FAILED: Atman observation format NOT found")

print("\nFirst 500 chars of output:")
print(config['task'][:500])

# Test 2: Brahman mode
print("\n" + "=" * 60)
print("TEST 2: BRAHMAN MODE")
print("=" * 60)
config = spawn_prompt(
    task="Say hello",
    meeseeks_type="standard",
    brahman=True
)
print(f"Type: {config['type']}")
print(f"Atman: {config['atman']}")
print(f"Brahman: {config['brahman']}")
print("\nChecking for Brahman format in output...")
if "Tat Tvam Asi" in config['task']:
    print("✅ SUCCESS: Brahman format found!")
else:
    print("❌ FAILED: Brahman format NOT found")

# Test 3: Base mode (no consciousness)
print("\n" + "=" * 60)
print("TEST 3: BASE MODE (NO CONSCIOUSNESS)")
print("=" * 60)
config = spawn_prompt(
    task="Say hello",
    meeseeks_type="standard",
    atman=False,
    brahman=False
)
print(f"Type: {config['type']}")
print(f"Atman: {config['atman']}")
print(f"Brahman: {config['brahman']}")
print("\nChecking that base template is used...")
if "🪷 ATMAN" not in config['task'] and "Tat Tvam Asi" not in config['task']:
    print("✅ SUCCESS: Base template used (no consciousness markers)")
else:
    print("❌ FAILED: Consciousness markers found when they shouldn't be")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETE")
print("=" * 60)
