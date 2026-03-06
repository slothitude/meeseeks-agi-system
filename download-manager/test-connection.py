#!/usr/bin/env python3
"""
Test aria2 RPC connection and functionality.

Usage:
    python test-connection.py
    python test-connection.py --host 192.168.0.237 --port 6800
"""

import sys
import argparse
from trigger import DownloadManager, DownloadError


def test_connection(host: str, port: int, secret: str):
    """Test basic RPC connection."""
    print(f"Testing connection to aria2 at {host}:{port}...")
    
    dm = DownloadManager(rpc_host=host, rpc_port=port, rpc_secret=secret)
    
    try:
        # Test 1: Get version
        print("\n[1/5] Getting aria2 version...")
        version_info = dm._call("aria2.getVersion", f"token:{secret}")
        print(f"  ✓ aria2 version: {version_info.get('version', 'unknown')}")
        print(f"  ✓ Features: {', '.join(version_info.get('enabledFeatures', []))}")
        
        # Test 2: Get global stats
        print("\n[2/5] Getting global statistics...")
        stats = dm.get_global_stats()
        print(f"  ✓ Download speed: {stats['download_speed_human']}/s")
        print(f"  ✓ Active downloads: {stats['num_active']}")
        print(f"  ✓ Waiting downloads: {stats['num_waiting']}")
        
        # Test 3: List active downloads
        print("\n[3/5] Listing active downloads...")
        active = dm.list_active()
        if active:
            print(f"  ✓ Found {len(active)} active downloads:")
            for d in active[:5]:
                print(f"    - [{d['gid']}] {d['filename']} ({d['progress']}%)")
        else:
            print("  ✓ No active downloads (queue is empty)")
        
        # Test 4: Test adding a small download (optional)
        print("\n[4/5] Test download (10MB test file)...")
        response = input("  Add test download? (y/n): ")
        if response.lower() == 'y':
            test_url = "http://speedtest.tele2.net/10MB.zip"
            result = dm.add_download(
                test_url,
                filename="test-10mb.zip",
                directory="/home/pi/downloads"
            )
            print(f"  ✓ Test download added: {result['gid']}")
            
            # Check status
            status = dm.get_status(result['gid'])
            print(f"  ✓ Status: {status['status']}")
            print(f"  ✓ Progress: {status['progress']}%")
            
            response = input("  Cancel test download? (y/n): ")
            if response.lower() == 'y':
                dm.cancel(result['gid'])
                print("  ✓ Test download cancelled")
        else:
            print("  ⊘ Skipping test download")
        
        # Test 5: Health check
        print("\n[5/5] Running health check...")
        if dm.is_healthy():
            print("  ✓ aria2 is healthy and responsive")
        else:
            print("  ✗ aria2 health check failed")
            return False
        
        print("\n" + "="*50)
        print("✓ All tests passed!")
        print("="*50)
        return True
        
    except DownloadError as e:
        print(f"\n✗ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Check if aria2 is running: sudo systemctl status aria2")
        print("  2. Check RPC settings in ~/.aria2/aria2.conf")
        print("  3. Verify firewall allows port 6800")
        print("  4. Check logs: tail -f ~/logs/aria2/aria2.log")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Test aria2 RPC connection")
    parser.add_argument("--host", default="192.168.0.237", help="aria2 host (default: 192.168.0.237)")
    parser.add_argument("--port", type=int, default=6800, help="aria2 RPC port (default: 6800)")
    parser.add_argument("--secret", default="sloth_download_token", help="RPC secret token")
    
    args = parser.parse_args()
    
    success = test_connection(args.host, args.port, args.secret)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
