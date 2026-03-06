#!/usr/bin/env python3
"""
Download Manager for Agent Network
===================================
Cross-platform download manager that monitors for trigger files and processes downloads.

Works on:
- Windows (Sloth_rog) - uses \\\\192.168.0.237\\pi-share
- Linux/Pi (sloth_pibot) - uses /mnt/pi-share or configurable path

Usage:
    python download_manager.py [--watch] [--once] [--api]

Modes:
    --watch: Continuously watch for trigger files (default)
    --once: Process existing triggers once and exit
    --api: Start HTTP API server for triggering downloads
"""

import json
import os
import sys
import time
import hashlib
import logging
import argparse
import shutil
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from urllib.parse import urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("ERROR: requests library required. Install with: pip install requests")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Platform detection
IS_WINDOWS = sys.platform == 'win32'
IS_LINUX = sys.platform.startswith('linux')

# Default paths based on platform
if IS_WINDOWS:
    DEFAULT_DOWNLOAD_DIR = r"\\192.168.0.237\pi-share\downloads"
    DEFAULT_TRIGGER_DIR = r"\\192.168.0.237\pi-share\download_triggers"
    DEFAULT_COMPLETED_DIR = r"\\192.168.0.237\pi-share\download_triggers\completed"
    DEFAULT_FAILED_DIR = r"\\192.168.0.237\pi-share\download_triggers\failed"
else:  # Linux/Pi
    DEFAULT_DOWNLOAD_DIR = "/mnt/pi-share/downloads"
    DEFAULT_TRIGGER_DIR = "/mnt/pi-share/download_triggers"
    DEFAULT_COMPLETED_DIR = "/mnt/pi-share/download_triggers/completed"
    DEFAULT_FAILED_DIR = "/mnt/pi-share/download_triggers/failed"

# API settings
DEFAULT_API_PORT = 8765
DEFAULT_API_HOST = "0.0.0.0"


class DownloadManager:
    """Manages downloads triggered by JSON files or API requests."""
    
    def __init__(self, 
                 download_dir: str = None,
                 trigger_dir: str = None,
                 completed_dir: str = None,
                 failed_dir: str = None):
        # Use provided paths, or derive from trigger_dir, or use defaults
        if download_dir:
            self.download_dir = Path(download_dir)
        else:
            self.download_dir = Path(DEFAULT_DOWNLOAD_DIR)
        
        if trigger_dir:
            self.trigger_dir = Path(trigger_dir)
            # Derive completed/failed from trigger_dir if not explicitly provided
            if completed_dir:
                self.completed_dir = Path(completed_dir)
            else:
                self.completed_dir = self.trigger_dir / "completed"
            if failed_dir:
                self.failed_dir = Path(failed_dir)
            else:
                self.failed_dir = self.trigger_dir / "failed"
        else:
            self.trigger_dir = Path(DEFAULT_TRIGGER_DIR)
            self.completed_dir = Path(completed_dir or DEFAULT_COMPLETED_DIR)
            self.failed_dir = Path(failed_dir or DEFAULT_FAILED_DIR)
        
        # Setup directories
        self._ensure_dirs()
        
        # Configure requests session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        logger.info(f"Download Manager initialized")
        logger.info(f"  Download dir: {self.download_dir}")
        logger.info(f"  Trigger dir: {self.trigger_dir}")
    
    def _ensure_dirs(self):
        """Create necessary directories if they don't exist."""
        for directory in [self.download_dir, self.trigger_dir, 
                         self.completed_dir, self.failed_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory: {directory}")
    
    def validate_trigger(self, data: Dict[str, Any]) -> tuple[bool, str]:
        """Validate a trigger file structure.
        
        Returns: (is_valid, error_message)
        """
        if not isinstance(data, dict):
            return False, "Trigger must be a JSON object"
        
        # Required field: url
        if 'url' not in data:
            return False, "Missing required field: 'url'"
        
        url = data['url']
        if not isinstance(url, str) or not url.strip():
            return False, "Field 'url' must be a non-empty string"
        
        # Validate URL format
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ('http', 'https', 'ftp'):
                return False, f"Unsupported URL scheme: {parsed.scheme}"
        except Exception as e:
            return False, f"Invalid URL format: {e}"
        
        # Optional fields validation
        if 'filename' in data and not isinstance(data['filename'], str):
            return False, "Field 'filename' must be a string"
        
        if 'headers' in data and not isinstance(data['headers'], dict):
            return False, "Field 'headers' must be an object"
        
        return True, ""
    
    def get_filename_from_url(self, url: str, response: requests.Response = None) -> str:
        """Extract filename from URL or Content-Disposition header."""
        # Try Content-Disposition header first
        if response and 'content-disposition' in response.headers:
            cd = response.headers['content-disposition']
            if 'filename=' in cd:
                filename = cd.split('filename=')[1].strip('"\'')
                if filename:
                    return filename
        
        # Extract from URL
        parsed = urlparse(url)
        path = parsed.path
        filename = os.path.basename(path)
        
        if not filename:
            # Generate filename from URL hash
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            filename = f"download_{url_hash}"
        
        return filename
    
    def download_file(self, trigger_data: Dict[str, Any]) -> tuple[bool, str, str]:
        """Download a file based on trigger data.
        
        Returns: (success, filepath, error_message)
        """
        url = trigger_data['url']
        filename = trigger_data.get('filename')
        headers = trigger_data.get('headers', {})
        subfolder = trigger_data.get('subfolder', '')
        
        logger.info(f"Starting download: {url}")
        
        try:
            # Make request
            response = self.session.get(url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            # Determine filename
            if not filename:
                filename = self.get_filename_from_url(url, response)
            
            # Sanitize filename
            filename = self._sanitize_filename(filename)
            
            # Determine download path
            if subfolder:
                download_path = self.download_dir / subfolder
                download_path.mkdir(parents=True, exist_ok=True)
            else:
                download_path = self.download_dir
            
            filepath = download_path / filename
            
            # Handle duplicate filenames
            if filepath.exists():
                base, ext = os.path.splitext(filename)
                counter = 1
                while filepath.exists():
                    filepath = download_path / f"{base}_{counter}{ext}"
                    counter += 1
            
            # Download with progress
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size:
                            progress = (downloaded / total_size) * 100
                            if int(progress) % 10 == 0:  # Log every 10%
                                logger.debug(f"Progress: {progress:.1f}%")
            
            logger.info(f"Download complete: {filepath} ({downloaded} bytes)")
            return True, str(filepath), ""
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Download failed: {e}"
            logger.error(error_msg)
            return False, "", error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            logger.error(error_msg)
            return False, "", error_msg
    
    def _sanitize_filename(self, filename: str) -> str:
        """Remove or replace unsafe characters from filename."""
        # Replace common unsafe characters
        unsafe_chars = '<>:"/\\|?*'
        for char in unsafe_chars:
            filename = filename.replace(char, '_')
        return filename
    
    def process_trigger_file(self, trigger_path: Path) -> bool:
        """Process a single trigger file.
        
        Returns: True if successful, False otherwise
        """
        logger.info(f"Processing trigger: {trigger_path.name}")
        
        try:
            # Read trigger file
            with open(trigger_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate
            is_valid, error = self.validate_trigger(data)
            if not is_valid:
                logger.error(f"Invalid trigger {trigger_path.name}: {error}")
                self._move_trigger(trigger_path, self.failed_dir, error)
                return False
            
            # Download
            success, filepath, error = self.download_file(data)
            
            if success:
                # Add result to trigger data and move to completed
                data['result'] = {
                    'status': 'completed',
                    'filepath': filepath,
                    'completed_at': datetime.now().isoformat()
                }
                # Write updated data before moving
                with open(trigger_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                self._move_trigger(trigger_path, self.completed_dir)
                return True
            else:
                # Add error result
                data['result'] = {
                    'status': 'failed',
                    'error': error,
                    'failed_at': datetime.now().isoformat()
                }
                # Write updated data before moving
                with open(trigger_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                self._move_trigger(trigger_path, self.failed_dir)
                return False
                
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON: {e}"
            logger.error(f"Failed to parse {trigger_path.name}: {error_msg}")
            self._move_trigger(trigger_path, self.failed_dir, error_msg)
            return False
        except Exception as e:
            error_msg = f"Error processing trigger: {e}"
            logger.error(f"Failed to process {trigger_path.name}: {error_msg}")
            self._move_trigger(trigger_path, self.failed_dir, error_msg)
            return False
    
    def _move_trigger(self, trigger_path: Path, target_dir: Path):
        """Move trigger file to target directory."""
        try:
            # Move to target directory
            target_path = target_dir / trigger_path.name
            if target_path.exists():
                # Add timestamp to avoid overwriting
                base = trigger_path.stem
                ext = trigger_path.suffix
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                target_path = target_dir / f"{base}_{timestamp}{ext}"
            
            shutil.move(str(trigger_path), str(target_path))
            logger.debug(f"Moved trigger to: {target_path}")
            
        except Exception as e:
            logger.error(f"Failed to move trigger file: {e}")
    
    def scan_triggers(self) -> int:
        """Scan trigger directory and process all trigger files.
        
        Returns: Number of triggers processed
        """
        if not self.trigger_dir.exists():
            logger.warning(f"Trigger directory does not exist: {self.trigger_dir}")
            return 0
        
        # Find all .json files (excluding completed/failed subdirs)
        trigger_files = []
        for item in self.trigger_dir.iterdir():
            if item.is_file() and item.suffix == '.json':
                trigger_files.append(item)
        
        if not trigger_files:
            logger.debug("No trigger files found")
            return 0
        
        logger.info(f"Found {len(trigger_files)} trigger file(s)")
        
        processed = 0
        for trigger_path in trigger_files:
            if self.process_trigger_file(trigger_path):
                processed += 1
        
        return processed
    
    def watch(self, interval: int = 5):
        """Watch for new trigger files and process them.
        
        Args:
            interval: Scan interval in seconds
        """
        logger.info(f"Watching for triggers (interval: {interval}s)")
        logger.info("Press Ctrl+C to stop")
        
        try:
            while True:
                self.scan_triggers()
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Stopping watch mode")
    
    def run_once(self):
        """Process existing triggers once and exit."""
        logger.info("Running once - processing existing triggers")
        count = self.scan_triggers()
        logger.info(f"Processed {count} trigger(s)")
    
    def create_trigger(self, url: str, filename: str = None, 
                       headers: Dict = None, subfolder: str = None) -> Path:
        """Create a trigger file programmatically.
        
        Returns: Path to created trigger file
        """
        trigger_data = {
            'url': url,
            'created_at': datetime.now().isoformat(),
            'created_by': 'download_manager'
        }
        
        if filename:
            trigger_data['filename'] = filename
        if headers:
            trigger_data['headers'] = headers
        if subfolder:
            trigger_data['subfolder'] = subfolder
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        trigger_filename = f"trigger_{timestamp}_{url_hash}.json"
        
        trigger_path = self.trigger_dir / trigger_filename
        with open(trigger_path, 'w', encoding='utf-8') as f:
            json.dump(trigger_data, f, indent=2)
        
        logger.info(f"Created trigger: {trigger_path}")
        return trigger_path


class APIHandler(BaseHTTPRequestHandler):
    """HTTP API handler for triggering downloads."""
    
    manager: DownloadManager = None
    
    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.debug(f"API: {args[0]}")
    
    def do_GET(self):
        """Handle GET requests - status check."""
        if self.path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {
                'status': 'running',
                'download_dir': str(self.manager.download_dir),
                'trigger_dir': str(self.manager.trigger_dir)
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests - create download trigger."""
        if self.path == '/download':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                data = json.loads(body.decode('utf-8'))
                
                # Validate
                is_valid, error = self.manager.validate_trigger(data)
                if not is_valid:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': error}).encode())
                    return
                
                # Create trigger
                trigger_path = self.manager.create_trigger(
                    url=data['url'],
                    filename=data.get('filename'),
                    headers=data.get('headers'),
                    subfolder=data.get('subfolder')
                )
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {
                    'status': 'triggered',
                    'trigger_file': str(trigger_path)
                }
                self.wfile.write(json.dumps(response).encode())
                
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
            except Exception as e:
                self.send_error(500, str(e))
        else:
            self.send_error(404, "Not Found")


def run_api_server(manager: DownloadManager, port: int = DEFAULT_API_PORT, 
                   host: str = DEFAULT_API_HOST):
    """Run the HTTP API server."""
    APIHandler.manager = manager
    
    with socketserver.TCPServer((host, port), APIHandler) as httpd:
        logger.info(f"API server running on http://{host}:{port}")
        logger.info("Endpoints:")
        logger.info("  GET  /status   - Check server status")
        logger.info("  POST /download - Trigger a download")
        logger.info("Press Ctrl+C to stop")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("Stopping API server")


def main():
    parser = argparse.ArgumentParser(
        description='Download Manager for Agent Network',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Watch for trigger files (continuous mode)
  python download_manager.py --watch
  
  # Process existing triggers once
  python download_manager.py --once
  
  # Start API server
  python download_manager.py --api --port 8765
  
  # Create a trigger file directly
  python download_manager.py --create --url "https://example.com/file.zip"
  
Trigger file format (JSON):
  {
    "url": "https://example.com/file.zip",
    "filename": "optional_custom_name.zip",
    "headers": {"User-Agent": "MyAgent"},
    "subfolder": "optional/subfolder"
  }
        """
    )
    
    # Mode arguments
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--watch', action='store_true', default=True,
                           help='Watch for trigger files (default)')
    mode_group.add_argument('--once', action='store_true',
                           help='Process triggers once and exit')
    mode_group.add_argument('--api', action='store_true',
                           help='Start HTTP API server')
    mode_group.add_argument('--create', action='store_true',
                           help='Create a trigger file')
    
    # Configuration arguments
    parser.add_argument('--download-dir', default=DEFAULT_DOWNLOAD_DIR,
                       help='Directory for downloaded files')
    parser.add_argument('--trigger-dir', default=DEFAULT_TRIGGER_DIR,
                       help='Directory to watch for trigger files')
    parser.add_argument('--interval', type=int, default=5,
                       help='Watch interval in seconds (default: 5)')
    
    # API arguments
    parser.add_argument('--port', type=int, default=DEFAULT_API_PORT,
                       help=f'API server port (default: {DEFAULT_API_PORT})')
    parser.add_argument('--host', default=DEFAULT_API_HOST,
                       help=f'API server host (default: {DEFAULT_API_HOST})')
    
    # Create trigger arguments
    parser.add_argument('--url', help='URL to download (for --create mode)')
    parser.add_argument('--filename', help='Custom filename (for --create mode)')
    
    args = parser.parse_args()
    
    # Handle --once and --api overriding --watch default
    if args.once or args.api or args.create:
        args.watch = False
    
    # Create manager
    manager = DownloadManager(
        download_dir=args.download_dir,
        trigger_dir=args.trigger_dir
    )
    
    # Run appropriate mode
    if args.create:
        if not args.url:
            logger.error("--url is required for --create mode")
            sys.exit(1)
        
        trigger_path = manager.create_trigger(
            url=args.url,
            filename=args.filename
        )
        print(f"Created trigger: {trigger_path}")
        
    elif args.api:
        run_api_server(manager, port=args.port, host=args.host)
        
    elif args.once:
        manager.run_once()
        
    else:  # watch mode
        manager.watch(interval=args.interval)


if __name__ == '__main__':
    main()
