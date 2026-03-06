"""
Example usage of the Download Manager for agents.

This file demonstrates how Sloth_rog (Windows) or sloth_pibot (Pi)
can use the download manager to trigger and manage downloads.
"""

from trigger import DownloadManager, download, status
import time


def example_basic_download():
    """Example 1: Basic download"""
    print("Example 1: Basic Download")
    print("-" * 40)
    
    # Quick download function
    gid = download(
        url="https://example.com/large-file.zip",
        filename="myfile.zip",
        directory="/home/pi/downloads/software"
    )
    
    print(f"Started download: {gid}")
    
    # Check status
    time.sleep(2)
    info = status(gid)
    print(f"Progress: {info['progress']}%")
    print(f"Speed: {info['download_speed_human']}/s")


def example_advanced_download():
    """Example 2: Advanced download with options"""
    print("\nExample 2: Advanced Download")
    print("-" * 40)
    
    dm = DownloadManager()
    
    # Add download with custom headers and multiple connections
    result = dm.add_download(
        url="https://example.com/game.iso",
        filename="game.iso",
        directory="/home/pi/downloads/games",
        connections=8,  # Use 8 connections for faster download
        headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://example.com"
        }
    )
    
    print(f"Download added: {result['gid']}")
    print(f"Saving to: {result['directory']}/{result['filename']}")


def example_batch_downloads():
    """Example 3: Batch downloads"""
    print("\nExample 3: Batch Downloads")
    print("-" * 40)
    
    dm = DownloadManager()
    
    urls = [
        "https://example.com/file1.zip",
        "https://example.com/file2.zip",
        "https://example.com/file3.zip"
    ]
    
    gids = []
    for url in urls:
        result = dm.add_download(url)
        gids.append(result['gid'])
        print(f"Added: {url} -> {result['gid']}")
    
    print(f"\n{len(gids)} downloads in queue")


def example_monitor_progress():
    """Example 4: Monitor download progress"""
    print("\nExample 4: Monitor Progress")
    print("-" * 40)
    
    dm = DownloadManager()
    
    # Add a download
    result = dm.add_download("https://example.com/large-file.zip")
    gid = result['gid']
    
    # Monitor until complete
    while True:
        info = dm.get_status(gid)
        
        print(f"[{info['status']}] {info['progress']}% - {info['download_speed_human']}/s")
        
        if info['status'] == 'complete':
            print("✓ Download complete!")
            print(f"File: {info['directory']}/{info['filename']}")
            break
        elif info['status'] == 'error':
            print(f"✗ Download failed: {info['error_message']}")
            break
        
        time.sleep(2)


def example_pause_resume():
    """Example 5: Pause and resume downloads"""
    print("\nExample 5: Pause and Resume")
    print("-" * 40)
    
    dm = DownloadManager()
    
    # Add download
    result = dm.add_download("https://example.com/large-file.zip")
    gid = result['gid']
    print(f"Started: {gid}")
    
    # Pause
    time.sleep(5)
    dm.pause(gid)
    print("Paused")
    
    # Resume
    time.sleep(5)
    dm.resume(gid)
    print("Resumed")


def example_list_downloads():
    """Example 6: List all downloads"""
    print("\nExample 6: List Downloads")
    print("-" * 40)
    
    dm = DownloadManager()
    
    # Get global stats
    stats = dm.get_global_stats()
    print(f"Download Speed: {stats['download_speed_human']}/s")
    print(f"Active: {stats['num_active']}")
    print(f"Waiting: {stats['num_waiting']}")
    
    # List active downloads
    active = dm.list_active()
    for d in active:
        print(f"\n[{d['gid']}] {d['filename']}")
        print(f"  Progress: {d['progress']}%")
        print(f"  Speed: {d['download_speed_human']}/s")
        print(f"  Size: {d['completed_length_human']} / {d['total_length_human']}")


def example_torrent_download():
    """Example 7: Torrent download"""
    print("\nExample 7: Torrent Download")
    print("-" * 40)
    
    dm = DownloadManager()
    
    # Add torrent
    result = dm.add_torrent(
        torrent_path="/path/to/file.torrent",
        directory="/home/pi/downloads/torrents"
    )
    
    print(f"Torrent added: {result['gid']}")


def example_agent_integration():
    """
    Example 8: Integration pattern for agents
    
    This shows how an agent might use the download manager in practice.
    """
    print("\nExample 8: Agent Integration Pattern")
    print("-" * 40)
    
    dm = DownloadManager()
    
    def download_file(url: str, category: str = "other") -> dict:
        """
        Download a file and return result.
        
        This is the kind of function an agent would expose.
        """
        # Map categories to directories
        category_dirs = {
            "games": "/home/pi/downloads/games",
            "software": "/home/pi/downloads/software",
            "media": "/home/pi/downloads/media",
            "other": "/home/pi/downloads/other"
        }
        
        directory = category_dirs.get(category, category_dirs["other"])
        
        try:
            result = dm.add_download(url, directory=directory)
            
            return {
                "success": True,
                "gid": result['gid'],
                "message": f"Download started: {result['gid']}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to start download: {e}"
            }
    
    def check_download(gid: str) -> dict:
        """Check download status."""
        try:
            info = dm.get_status(gid)
            
            return {
                "success": True,
                "status": info['status'],
                "progress": info['progress'],
                "speed": info['download_speed_human'],
                "filename": info['filename'],
                "location": f"{info['directory']}/{info['filename']}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # Example usage
    result = download_file("https://example.com/game.zip", category="games")
    print(f"Download result: {result}")
    
    if result['success']:
        status = check_download(result['gid'])
        print(f"Status: {status}")


def example_cli_usage():
    """Example 9: Using the CLI"""
    print("\nExample 9: CLI Usage")
    print("-" * 40)
    print("""
The trigger.py module can also be used as a CLI:

    # Add download
    python trigger.py add --url "https://example.com/file.zip" --filename "myfile.zip"
    
    # Check status
    python trigger.py status --gid "2089b05ecca3d829"
    
    # List downloads
    python trigger.py list
    
    # Pause download
    python trigger.py pause --gid "2089b05ecca3d829"
    
    # Resume download
    python trigger.py resume --gid "2089b05ecca3d829"
    
    # Cancel download
    python trigger.py cancel --gid "2089b05ecca3d829"
    
    # Get stats
    python trigger.py stats
""")


if __name__ == "__main__":
    print("="*60)
    print("Download Manager Examples")
    print("="*60)
    
    # Run examples (comment out ones you don't want to run)
    # example_basic_download()
    # example_advanced_download()
    # example_batch_downloads()
    # example_monitor_progress()
    # example_pause_resume()
    example_list_downloads()
    # example_torrent_download()
    example_agent_integration()
    example_cli_usage()
    
    print("\n" + "="*60)
    print("Examples complete!")
    print("="*60)
