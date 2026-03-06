"""
Agent Helper for Download Manager
==================================
Simple module for agents to trigger downloads.

Usage:
    from agent_helper import trigger_download, get_download_path
    
    # Trigger a download
    trigger_download("https://example.com/file.zip")
    
    # Trigger with custom filename
    trigger_download("https://example.com/file.zip", filename="myfile.zip")
    
    # Trigger with subfolder
    trigger_download("https://example.com/file.zip", subfolder="projects")
    
    # Check where downloads go
    print(get_download_path())
"""

import json
import hashlib
import platform
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict


# Platform-specific default paths
if platform.system() == 'Windows':
    DEFAULT_TRIGGER_DIR = r"\\192.168.0.237\pi-share\download_triggers"
    DEFAULT_DOWNLOAD_DIR = r"\\192.168.0.237\pi-share\downloads"
    DEFAULT_API_URL = "http://localhost:8765"
else:  # Linux/Pi
    DEFAULT_TRIGGER_DIR = "/mnt/pi-share/download_triggers"
    DEFAULT_DOWNLOAD_DIR = "/mnt/pi-share/downloads"
    DEFAULT_API_URL = "http://localhost:8765"


def get_platform_dirs() -> Dict[str, Path]:
    """Get platform-appropriate directories.
    
    Returns:
        Dict with 'triggers' and 'downloads' paths
    """
    return {
        'triggers': Path(DEFAULT_TRIGGER_DIR),
        'downloads': Path(DEFAULT_DOWNLOAD_DIR)
    }


def get_download_path() -> Path:
    """Get the download directory path.
    
    Returns:
        Path to download directory
    """
    return Path(DEFAULT_DOWNLOAD_DIR)


def get_trigger_path() -> Path:
    """Get the trigger directory path.
    
    Returns:
        Path to trigger directory
    """
    return Path(DEFAULT_TRIGGER_DIR)


def trigger_download(
    url: str,
    filename: Optional[str] = None,
    subfolder: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
    trigger_dir: Optional[str] = None,
    use_api: bool = False,
    api_url: Optional[str] = None
) -> Path:
    """Trigger a download.
    
    Args:
        url: URL to download
        filename: Optional custom filename
        subfolder: Optional subfolder within downloads
        headers: Optional HTTP headers
        trigger_dir: Optional custom trigger directory
        use_api: Use HTTP API instead of file (requires API server running)
        api_url: API server URL (default: http://localhost:8765)
    
    Returns:
        Path to trigger file (or response info if using API)
    
    Example:
        >>> trigger_download("https://example.com/file.zip")
        PosixPath('/mnt/pi-share/download_triggers/trigger_20260303_221600_abc123.json')
        
        >>> trigger_download("https://example.com/file.zip", filename="myfile.zip")
        PosixPath('/mnt/pi-share/download_triggers/trigger_20260303_221601_def456.json')
    """
    if use_api:
        return _trigger_via_api(url, filename, subfolder, headers, api_url)
    else:
        return _trigger_via_file(url, filename, subfolder, headers, trigger_dir)


def _trigger_via_file(
    url: str,
    filename: Optional[str],
    subfolder: Optional[str],
    headers: Optional[Dict[str, str]],
    trigger_dir: Optional[str]
) -> Path:
    """Trigger download by creating a file."""
    trigger_path = Path(trigger_dir) if trigger_dir else Path(DEFAULT_TRIGGER_DIR)
    trigger_path.mkdir(parents=True, exist_ok=True)
    
    # Build trigger data
    data = {
        'url': url,
        'created_at': datetime.now().isoformat(),
        'created_by': platform.node()
    }
    
    if filename:
        data['filename'] = filename
    if subfolder:
        data['subfolder'] = subfolder
    if headers:
        data['headers'] = headers
    
    # Generate unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    trigger_file = trigger_path / f"trigger_{timestamp}_{url_hash}.json"
    
    # Write trigger
    with open(trigger_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    return trigger_file


def _trigger_via_api(
    url: str,
    filename: Optional[str],
    subfolder: Optional[str],
    headers: Optional[Dict[str, str]],
    api_url: Optional[str]
) -> Dict:
    """Trigger download via HTTP API."""
    try:
        import requests
    except ImportError:
        raise ImportError("requests library required for API mode. Install with: pip install requests")
    
    api = api_url or DEFAULT_API_URL
    
    payload = {'url': url}
    if filename:
        payload['filename'] = filename
    if subfolder:
        payload['subfolder'] = subfolder
    if headers:
        payload['headers'] = headers
    
    response = requests.post(f"{api}/download", json=payload, timeout=10)
    response.raise_for_status()
    
    return response.json()


def check_api_status(api_url: Optional[str] = None) -> Dict:
    """Check if the download manager API is running.
    
    Args:
        api_url: API server URL (default: http://localhost:8765)
    
    Returns:
        Status dict from API
    
    Raises:
        requests.RequestException: If API is not reachable
    """
    try:
        import requests
    except ImportError:
        raise ImportError("requests library required. Install with: pip install requests")
    
    api = api_url or DEFAULT_API_URL
    response = requests.get(f"{api}/status", timeout=5)
    response.raise_for_status()
    return response.json()


# Convenience functions for common use cases

def download_to_subfolder(url: str, subfolder: str, filename: Optional[str] = None) -> Path:
    """Download to a specific subfolder.
    
    Args:
        url: URL to download
        subfolder: Subfolder path (e.g., "projects/myproject")
        filename: Optional custom filename
    
    Returns:
        Path to trigger file
    """
    return trigger_download(url, filename=filename, subfolder=subfolder)


def download_with_auth(url: str, token: str, filename: Optional[str] = None) -> Path:
    """Download with Bearer token authentication.
    
    Args:
        url: URL to download
        token: Bearer token
        filename: Optional custom filename
    
    Returns:
        Path to trigger file
    """
    headers = {'Authorization': f'Bearer {token}'}
    return trigger_download(url, filename=filename, headers=headers)


def download_github_release(repo: str, tag: str, asset: str, subfolder: str = "tools") -> Path:
    """Download a GitHub release asset.
    
    Args:
        repo: Repository (e.g., "owner/repo")
        tag: Release tag (e.g., "v1.0.0")
        asset: Asset filename (e.g., "tool-windows.zip")
        subfolder: Subfolder for download (default: "tools")
    
    Returns:
        Path to trigger file
    
    Example:
        >>> download_github_release("owner/repo", "v1.0.0", "tool.zip")
    """
    url = f"https://github.com/{repo}/releases/download/{tag}/{asset}"
    return trigger_download(url, filename=asset, subfolder=subfolder)


if __name__ == '__main__':
    # Demo/test
    print("Download Manager - Agent Helper")
    print(f"Platform: {platform.system()}")
    print(f"Trigger dir: {DEFAULT_TRIGGER_DIR}")
    print(f"Download dir: {DEFAULT_DOWNLOAD_DIR}")
    print()
    
    # Example: Create a test trigger
    test_url = "https://httpbin.org/json"
    print(f"Creating test trigger for: {test_url}")
    trigger_file = trigger_download(test_url, filename="test.json", subfolder="tests")
    print(f"Trigger created: {trigger_file}")
