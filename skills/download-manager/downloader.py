#!/usr/bin/env python3
"""
Download Manager - Watches queue directory and downloads files
"""

import json
import time
import logging
import shutil
from pathlib import Path
from datetime import datetime
import requests

# Directory structure
BASE_DIR = Path(__file__).parent
QUEUE_DIR = BASE_DIR / "queue"
DOWNLOADS_DIR = BASE_DIR / "downloads"
COMPLETED_DIR = BASE_DIR / "completed"
LOG_DIR = BASE_DIR / "logs"

# Setup logging
LOG_DIR.mkdir(exist_ok=True)
log_file = LOG_DIR / f"downloader_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def ensure_directories():
    """Create necessary directories if they don't exist"""
    for directory in [QUEUE_DIR, DOWNLOADS_DIR, COMPLETED_DIR, LOG_DIR]:
        directory.mkdir(exist_ok=True)
    logger.info("Directories initialized")


def load_trigger(trigger_path: Path) -> dict:
    """Load and validate trigger file"""
    try:
        with open(trigger_path, 'r') as f:
            data = json.load(f)
        
        # Validate required fields
        required = ['url', 'output', 'id']
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {trigger_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading trigger {trigger_path}: {e}")
        raise


def download_file(url: str, output_path: Path, trigger_id: str) -> bool:
    """Download a file from URL to output path"""
    try:
        logger.info(f"[{trigger_id}] Starting download: {url}")
        
        # Stream download for large files
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Write to file
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        file_size = output_path.stat().st_size
        logger.info(f"[{trigger_id}] Download complete: {output_path} ({file_size} bytes)")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"[{trigger_id}] Download failed: {e}")
        return False
    except Exception as e:
        logger.error(f"[{trigger_id}] Unexpected error: {e}")
        return False


def process_trigger(trigger_path: Path):
    """Process a single trigger file"""
    trigger_file = trigger_path.name
    logger.info(f"Processing trigger: {trigger_file}")
    
    try:
        # Load trigger data
        trigger = load_trigger(trigger_path)
        
        # Determine output path
        output_path = DOWNLOADS_DIR / trigger['output']
        
        # Download the file
        success = download_file(
            url=trigger['url'],
            output_path=output_path,
            trigger_id=trigger['id']
        )
        
        if success:
            # Move trigger to completed
            completed_path = COMPLETED_DIR / trigger_file
            shutil.move(str(trigger_path), str(completed_path))
            logger.info(f"[{trigger['id']}] Trigger moved to completed: {completed_path}")
        else:
            # Leave in queue for retry (or could move to failed/ directory)
            logger.warning(f"[{trigger['id']}] Trigger left in queue for retry")
            
    except Exception as e:
        logger.error(f"Failed to process trigger {trigger_file}: {e}")


def watch_queue(poll_interval: int = 5):
    """Watch queue directory for new trigger files"""
    logger.info(f"Watching queue directory: {QUEUE_DIR}")
    logger.info(f"Poll interval: {poll_interval} seconds")
    
    while True:
        try:
            # Find all JSON files in queue
            trigger_files = list(QUEUE_DIR.glob("*.json"))
            
            if trigger_files:
                logger.info(f"Found {len(trigger_files)} trigger(s) in queue")
                
                for trigger_path in trigger_files:
                    process_trigger(trigger_path)
            
            # Wait before next poll
            time.sleep(poll_interval)
            
        except KeyboardInterrupt:
            logger.info("Shutting down by user request")
            break
        except Exception as e:
            logger.error(f"Error in watch loop: {e}")
            time.sleep(poll_interval)


def main():
    """Main entry point"""
    print("=" * 60)
    print("Download Manager")
    print("=" * 60)
    
    # Ensure directories exist
    ensure_directories()
    
    print(f"\nQueue directory: {QUEUE_DIR}")
    print(f"Downloads directory: {DOWNLOADS_DIR}")
    print(f"Completed directory: {COMPLETED_DIR}")
    print(f"Log file: {log_file}")
    print("\nPress Ctrl+C to stop\n")
    
    # Start watching
    watch_queue(poll_interval=5)


if __name__ == "__main__":
    main()
