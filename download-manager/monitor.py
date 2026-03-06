#!/usr/bin/env python3
"""
Download Monitor - Runs on sloth_pibot

Monitors aria2 downloads and reports status. Can be run as a service or on-demand.

Usage:
    python monitor.py              # Show current status
    python monitor.py --watch      # Continuously monitor
    python monitor.py --notify     # Send notifications on completion
"""

import time
import json
import argparse
from datetime import datetime
from pathlib import Path
from trigger import DownloadManager, DownloadError


class DownloadMonitor:
    """Monitor aria2 downloads and report status."""
    
    def __init__(self, log_file: str = None):
        self.dm = DownloadManager()
        self.log_file = log_file or "/home/pi/logs/aria2/monitor.log"
        self.completed_cache = set()
        
        # Ensure log directory exists
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
    
    def get_all_downloads(self):
        """Get all downloads (active, waiting, stopped)."""
        downloads = []
        
        try:
            downloads.extend(self.dm.list_active())
        except DownloadError:
            pass
        
        try:
            downloads.extend(self.dm.list_waiting())
        except DownloadError:
            pass
        
        return downloads
    
    def print_status(self):
        """Print current download status."""
        try:
            # Get global stats
            stats = self.dm.get_global_stats()
            
            print("\n" + "="*60)
            print(f"Download Manager Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*60)
            print(f"\nGlobal Statistics:")
            print(f"  Download Speed: {stats['download_speed_human']}/s")
            print(f"  Upload Speed: {stats['upload_speed_human']}/s")
            print(f"  Active: {stats['num_active']}")
            print(f"  Waiting: {stats['num_waiting']}")
            print(f"  Completed: {stats['num_stopped']}")
            
            # Get active downloads
            downloads = self.get_all_downloads()
            
            if downloads:
                print(f"\nActive Downloads ({len(downloads)}):")
                for d in downloads:
                    print(f"\n  [{d['gid']}] {d['filename']}")
                    print(f"    Status: {d['status']}")
                    print(f"    Progress: {d['progress']}%")
                    print(f"    Downloaded: {d['completed_length_human']} / {d['total_length_human']}")
                    print(f"    Speed: {d['download_speed_human']}/s")
                    if d.get('error_message'):
                        print(f"    Error: {d['error_message']}")
            else:
                print("\nNo active downloads.")
            
            print("\n" + "="*60)
            
        except DownloadError as e:
            print(f"\nError: Cannot connect to aria2 - {e}")
            return False
        
        return True
    
    def watch(self, interval: int = 5, notify_on_complete: bool = False):
        """
        Continuously monitor downloads.
        
        Args:
            interval: Update interval in seconds
            notify_on_complete: Send notification when download completes
        """
        print(f"Starting download monitor (update every {interval}s)...")
        print("Press Ctrl+C to stop.\n")
        
        try:
            while True:
                # Clear screen for clean output
                print("\033[2J\033[H", end="")
                
                success = self.print_status()
                
                if not success:
                    print("\nRetrying in 10 seconds...")
                    time.sleep(10)
                    continue
                
                # Check for completed downloads
                if notify_on_complete:
                    self._check_completions()
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\nMonitor stopped.")
    
    def _check_completions(self):
        """Check for newly completed downloads and log them."""
        try:
            stopped = self.dm.list_stopped(max_results=10)
            
            for d in stopped:
                gid = d['gid']
                if gid not in self.completed_cache:
                    self.completed_cache.add(gid)
                    
                    # Log completion
                    self._log_completion(d)
                    
                    # Print notification
                    print(f"\n✓ Download Complete: {d['filename']}")
                    print(f"  Size: {d['total_length_human']}")
                    print(f"  Location: {d['directory']}")
                    
        except DownloadError:
            pass
    
    def _log_completion(self, download_info: dict):
        """Log download completion."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "gid": download_info['gid'],
            "filename": download_info['filename'],
            "size": download_info['total_length'],
            "status": download_info['status'],
            "directory": download_info['directory']
        }
        
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"Warning: Could not write to log file: {e}")
    
    def export_status(self, output_file: str):
        """Export current status to JSON file."""
        try:
            stats = self.dm.get_global_stats()
            downloads = self.get_all_downloads()
            
            data = {
                "timestamp": datetime.now().isoformat(),
                "global_stats": stats,
                "downloads": downloads
            }
            
            with open(output_file, "w") as f:
                json.dump(data, f, indent=2)
            
            print(f"Status exported to: {output_file}")
            return True
            
        except Exception as e:
            print(f"Error exporting status: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Download Monitor")
    parser.add_argument("--watch", action="store_true", help="Continuously monitor")
    parser.add_argument("--interval", type=int, default=5, help="Update interval in seconds")
    parser.add_argument("--notify", action="store_true", help="Notify on completion")
    parser.add_argument("--export", help="Export status to JSON file")
    parser.add_argument("--log", help="Monitor log file location")
    
    args = parser.parse_args()
    
    monitor = DownloadMonitor(log_file=args.log)
    
    if args.export:
        monitor.export_status(args.export)
    elif args.watch:
        monitor.watch(interval=args.interval, notify_on_complete=args.notify)
    else:
        monitor.print_status()


if __name__ == "__main__":
    main()
