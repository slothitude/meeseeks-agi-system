#!/usr/bin/env python3
"""
SMB ROM Locator and Emulator Setup

Finds Super Mario Bros ROM and sets up the emulator.
"""

import os
import subprocess
from pathlib import Path

def find_smb_rom():
    """Search for SMB ROM in common locations"""
    search_paths = [
        Path.home() / "Downloads",
        Path.home() / "Desktop",
        Path.home() / "Documents",
        Path.home() / "ROMs",
        Path.home() / "Games",
        Path("C:/Games"),
        Path("D:/ROMs"),
        Path("//192.168.0.237/pi-share"),
    ]

    print("Searching for Super Mario Bros ROM...")
    print("=" * 60)

    for search_path in search_paths:
        if not search_path.exists():
            continue

        print(f"\nSearching: {search_path}")

        # Search for .nes and .zip files
        for ext in ["*.nes", "*.zip"]:
            for file in search_path.rglob(ext):
                if ("mario" in file.name.lower() or "smb" in file.name.lower()) and "nes" in str(file).lower():
                    print(f"  FOUND: {file}")
                    return file

    return None

def setup_emulator(rom_path):
    """Set up emulator with ROM"""
    print(f"\nSetting up emulator with ROM: {rom_path}")
    print("=" * 60)

    # Check if gym-retro is installed
    try:
        import retro
        print("[+] gym-retro is installed")
    except ImportError:
        print("[!] gym-retro not installed")
        print("  Installing: pip install gym-retro")
        subprocess.run(["pip", "install", "gym-retro"], check=True)

    # Import ROM
    print(f"\nImporting ROM: {rom_path}")
    subprocess.run(["python", "-m", "retro.import", str(rom_path)], check=True)

    print("\n[+] Setup complete!")
    print("\nTo play:")
    print("  from the_body.emulator_interface import RetroBackend, SMBPlayer")
    print("  backend = RetroBackend('SuperMarioBros-Nes')")
    print("  player = SMBPlayer(backend)")
    print("  player.play(1000)")

def create_download_instructions():
    """Instructions for getting ROM if not found"""
    print("\n" + "=" * 60)
    print("ROM NOT FOUND")
    print("=" * 60)
    print("\nTo get Super Mario Bros ROM:")
    print("\n1. Legal options:")
    print("   - Buy NES Classic Edition")
    print("   - Nintendo Switch Online")
    print("   - Extract from your own cartridge")
    print("\n2. Download location:")
    print("   - Place ROM in: ~/ROMs/smb.nes")
    print("   - Or specify path when running")
    print("\n3. Supported formats:")
    print("   - .nes (NES ROM)")
    print("   - .zip (compressed ROM)")
    print("\n4. Then run:")
    print("   python the_body/setup_smb_emulator.py")

if __name__ == "__main__":
    print("SMB ROM Locator and Emulator Setup")
    print("=" * 60)

    # Search for ROM
    rom_path = find_smb_rom()

    if rom_path:
        print(f"\n[+] ROM found: {rom_path}")
        setup_emulator(rom_path)
    else:
        create_download_instructions()
