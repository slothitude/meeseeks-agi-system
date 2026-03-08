#!/usr/bin/env python3
"""
SMB Game Player - Browser-based with local ROM

Direct approach that works even with network issues.
"""

import webbrowser
from pathlib import Path

ROM_PATH = r"C:\Users\aaron\ROMs\smb.nes"

print("SMB Game Player")
print("=" * 60)
print(f"\nROM: {ROM_PATH}")

if not Path(ROM_PATH).exists():
    print(f"ERROR: ROM not found!")
    exit(1)

print("\nOpening browser emulator...")
print("\nInstructions:")
print("1. Open https://nesbox.org/")
print("2. Click 'Load ROM'")
print("3. Select your ROM file:")
print(f"   {ROM_PATH}")
print("4. Click Play!")
print("\nOpening nesbox.org...")

webbrowser.open("https://nesbox.org/")

print("\nAlternative: Try these online emulators:")
print("  - https://nesbox.org/")
print("  - https://emulatorjs.org/")
print("  - https://www.retrogames.cc/")
