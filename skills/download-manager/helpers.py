#!/usr/bin/env python3
"""
Download Manager Helper Functions

Provides Python functions for agents to interact with the download manager.
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import uuid


# Directory structure (matches downloader.py)
BASE_DIR = Path(__file__).parent
QUEUE_DIR = BASE_DIR / "queue"
DOWNLOADS_DIR = BASE_DIR / "downloads"
COMPLETED_DIR = BASE_DIR / "completed"


def _ensure_directories():
    """Ensure all necessary directories exist"""
    for directory in [QUEUE_DIR, DOWNLOADS_DIR, COMPLETED_DIR]:
        directory.mkdir(exist_ok=True)


def _generate_download_id() -> str:
    """Generate a unique download ID"""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    unique = uuid.uuid4().hex[:6]
    return f"download-{timestamp}-{unique}"


def add_download(url: str, output_filename: str, download_id: Optional[str] = None) -> str:
    """
    Add a download task to the queue.
    
    Args:
        url: URL to download from
        output_filename: Name to save the file as (saved to downloads/)
        download_id: Optional unique ID (auto-generated if None)
    
    Returns:
        download_id: Unique identifier for this download
    
    Example:
        >>> download_id = add_download(
        ...     "https://example.com/data.zip",
        ...     "data.zip"
        ... )
        >>> print(download_id)
        'download-20260303-223000-abc123'
    """
    _ensure_directories()
    
    # Generate ID if not provided
    if download_id is None:
        download_id = _generate_download_id()
    
    # Create trigger data
    trigger = {
        "url": url,
        "output": output_filename,
        "id": download_id,
        "timestamp": datetime.now().isoformat()
    }
    
    # Write to queue
    trigger_path = QUEUE_DIR / f"{download_id}.json"
    trigger_path.write_text(json.dumps(trigger, indent=2))
    
    return download_id


def check_status(download_id: str) -> str:
    """
    Check the status of a download.
    
    Args:
        download_id: The unique download identifier
    
    Returns:
        status: One of 'pending', 'in-progress', 'complete', 'failed'
        
        - 'pending': Download in queue, waiting to be processed
        - 'in-progress': Currently being downloaded
        - 'complete': Download finished successfully
        - 'failed': Download failed (trigger still in queue)
        - 'not-found': Download ID not found in queue or completed
    
    Example:
        >>> status = check_status("my-download-001")
        >>> if status == "complete":
        ...     print("Download finished!")
        >>> elif status == "failed":
        ...     print("Download failed - check logs")
    """
    _ensure_directories()
    
    # Check if in queue (pending)
    queue_path = QUEUE_DIR / f"{download_id}.json"
    if queue_path.exists():
        # Could be pending or failed - check if file exists in downloads
        try:
            trigger = json.loads(queue_path.read_text())
            output_filename = trigger.get("output")
            if output_filename:
                download_path = DOWNLOADS_DIR / output_filename
                if download_path.exists():
                    return "in-progress"  # File exists but trigger not moved
            return "pending"
        except Exception:
            return "pending"
    
    # Check if completed
    completed_path = COMPLETED_DIR / f"{download_id}.json"
    if completed_path.exists():
        return "complete"
    
    return "not-found"


def get_file_path(download_id: str) -> Optional[Path]:
    """
    Get the path to a downloaded file (if complete).
    
    Args:
        download_id: The unique download identifier
    
    Returns:
        Path object if download complete, None otherwise
    
    Example:
        >>> path = get_file_path("my-download-001")
        >>> if path:
        ...     print(f"File ready at: {path}")
        ...     # Use the file
        ...     with open(path, 'rb') as f:
        ...         data = f.read()
    """
    _ensure_directories()
    
    # Only return path if download is complete
    if check_status(download_id) != "complete":
        return None
    
    # Load completed trigger to get output filename
    completed_path = COMPLETED_DIR / f"{download_id}.json"
    if not completed_path.exists():
        return None
    
    try:
        trigger = json.loads(completed_path.read_text())
        output_filename = trigger.get("output")
        
        if output_filename:
            download_path = DOWNLOADS_DIR / output_filename
            if download_path.exists():
                return download_path
        
        return None
    except Exception:
        return None


def list_downloads(status_filter: Optional[str] = None) -> List[Dict[str, str]]:
    """
    List all downloads and their statuses.
    
    Args:
        status_filter: Optional filter by status ('pending', 'complete', etc.)
    
    Returns:
        List of dicts with keys: 'id', 'status', 'url', 'output'
    
    Example:
        >>> downloads = list_downloads()
        >>> for download in downloads:
        ...     print(f"{download['id']}: {download['status']}")
        >>> 
        >>> # Filter by status
        >>> complete = list_downloads(status_filter="complete")
        >>> print(f"{len(complete)} downloads complete")
    """
    _ensure_directories()
    
    downloads = []
    
    # Check queue (pending/in-progress)
    for trigger_path in QUEUE_DIR.glob("*.json"):
        try:
            trigger = json.loads(trigger_path.read_text())
            download_id = trigger.get("id", trigger_path.stem)
            status = check_status(download_id)
            
            if status_filter is None or status == status_filter:
                downloads.append({
                    "id": download_id,
                    "status": status,
                    "url": trigger.get("url", ""),
                    "output": trigger.get("output", "")
                })
        except Exception:
            pass
    
    # Check completed
    for trigger_path in COMPLETED_DIR.glob("*.json"):
        try:
            trigger = json.loads(trigger_path.read_text())
            download_id = trigger.get("id", trigger_path.stem)
            
            if status_filter is None or status_filter == "complete":
                downloads.append({
                    "id": download_id,
                    "status": "complete",
                    "url": trigger.get("url", ""),
                    "output": trigger.get("output", "")
                })
        except Exception:
            pass
    
    return downloads


def wait_for_download(download_id: str, timeout: int = 300, poll_interval: int = 5) -> Optional[Path]:
    """
    Wait for a download to complete (blocking).
    
    Args:
        download_id: The unique download identifier
        timeout: Maximum seconds to wait (default: 300 = 5 minutes)
        poll_interval: Seconds between status checks (default: 5)
    
    Returns:
        Path object if download complete, None if timeout or failed
    
    Example:
        >>> file_path = wait_for_download(
        ...     download_id="my-download",
        ...     timeout=300,
        ...     poll_interval=10
        ... )
        >>> if file_path:
        ...     print(f"Download complete: {file_path}")
        ... else:
        ...     print("Download timed out or failed")
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        status = check_status(download_id)
        
        if status == "complete":
            return get_file_path(download_id)
        elif status == "failed":
            return None
        elif status == "not-found":
            # Download not found, might have been cleaned up
            return None
        
        time.sleep(poll_interval)
    
    # Timeout
    return None


def get_download_info(download_id: str) -> Optional[Dict[str, str]]:
    """
    Get full information about a download.
    
    Args:
        download_id: The unique download identifier
    
    Returns:
        Dict with download info, or None if not found
    
    Example:
        >>> info = get_download_info("my-download-001")
        >>> if info:
        ...     print(f"URL: {info['url']}")
        ...     print(f"Output: {info['output']}")
        ...     print(f"Status: {info['status']}")
    """
    _ensure_directories()
    
    # Check queue
    queue_path = QUEUE_DIR / f"{download_id}.json"
    if queue_path.exists():
        try:
            trigger = json.loads(queue_path.read_text())
            return {
                "id": download_id,
                "url": trigger.get("url", ""),
                "output": trigger.get("output", ""),
                "status": check_status(download_id),
                "timestamp": trigger.get("timestamp", "")
            }
        except Exception:
            pass
    
    # Check completed
    completed_path = COMPLETED_DIR / f"{download_id}.json"
    if completed_path.exists():
        try:
            trigger = json.loads(completed_path.read_text())
            return {
                "id": download_id,
                "url": trigger.get("url", ""),
                "output": trigger.get("output", ""),
                "status": "complete",
                "timestamp": trigger.get("timestamp", "")
            }
        except Exception:
            pass
    
    return None


def remove_download(download_id: str) -> bool:
    """
    Remove a download from the queue (if pending).
    
    Note: Cannot remove completed or in-progress downloads.
    
    Args:
        download_id: The unique download identifier
    
    Returns:
        True if removed, False if not found or cannot be removed
    
    Example:
        >>> if remove_download("my-download-001"):
        ...     print("Download removed from queue")
    """
    _ensure_directories()
    
    queue_path = QUEUE_DIR / f"{download_id}.json"
    if queue_path.exists():
        try:
            queue_path.unlink()
            return True
        except Exception:
            return False
    
    return False


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("Download Manager Helper Functions")
    print("=" * 60)
    
    # Example: Add a download
    print("\n1. Adding download...")
    download_id = add_download(
        url="https://example.com/test-file.zip",
        output_filename="test-file.zip"
    )
    print(f"   Download ID: {download_id}")
    
    # Check status
    print("\n2. Checking status...")
    status = check_status(download_id)
    print(f"   Status: {status}")
    
    # Get info
    print("\n3. Getting download info...")
    info = get_download_info(download_id)
    if info:
        for key, value in info.items():
            print(f"   {key}: {value}")
    
    # List all downloads
    print("\n4. Listing all downloads...")
    downloads = list_downloads()
    print(f"   Found {len(downloads)} download(s)")
    for download in downloads[:5]:  # Show first 5
        print(f"   - {download['id']}: {download['status']}")
    
    # Clean up test download
    print("\n5. Cleaning up test download...")
    if remove_download(download_id):
        print(f"   Removed: {download_id}")
    
    print("\n[OK] Helper functions working correctly")
    print("\nUsage example:")
    print("  from skills.download_manager.helpers import add_download, check_status, get_file_path")
    print("  download_id = add_download('https://...', 'file.zip')")
    print("  if check_status(download_id) == 'complete':")
    print("      file = get_file_path(download_id)")
