# Download Manager - Agent Workflow Guide

Complete guide for using the download manager as a tool in agent workflows.

## Quick Start

### 1. Start the Downloader

The downloader runs as a background process that watches for new download tasks.

**Start the daemon:**
```bash
cd skills/download-manager
python downloader.py
```

**What happens:**
- Creates necessary directories (queue/, downloads/, completed/, logs/)
- Starts polling the queue/ directory every 5 seconds
- Logs activity to both console and logs/downloader_YYYYMMDD.log
- Runs until stopped with Ctrl+C

**Verify it's running:**
- Console shows "Watching queue directory: ..."
- Check logs: `tail -f logs/downloader_*.log`

### 2. Add a Download Task

**Using Python helper (recommended):**
```python
from skills.download_manager.helpers import add_download

download_id = add_download(
    url="https://example.com/dataset.zip",
    output_filename="dataset.zip"
)
print(f"Download queued with ID: {download_id}")
```

**Manual method (create JSON file):**
```python
import json
from pathlib import Path

trigger = {
    "url": "https://example.com/file.zip",
    "output": "file.zip",
    "id": "my-download-001"
}

queue_file = Path("skills/download-manager/queue/my-download-001.json")
queue_file.write_text(json.dumps(trigger, indent=2))
```

**The download will start within 5 seconds!**

---

## Agent Integration

### Python Functions

Import the helper module:
```python
from skills.download_manager.helpers import add_download, check_status, get_file_path
```

#### 1. Add Download to Queue

```python
def add_download(url, output_filename, download_id=None):
    """
    Add a download task to the queue.
    
    Args:
        url: URL to download from
        output_filename: Name to save the file as
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
```

#### 2. Check Download Status

```python
def check_status(download_id):
    """
    Check the status of a download.
    
    Args:
        download_id: The unique download identifier
    
    Returns:
        status: One of 'pending', 'in-progress', 'complete', 'failed'
    
    Example:
        >>> status = check_status("my-download-001")
        >>> if status == "complete":
        ...     print("Download finished!")
        >>> elif status == "failed":
        ...     print("Download failed - check logs")
    """
```

#### 3. Get Downloaded File Path

```python
def get_file_path(download_id):
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
```

### Complete Integration Example

```python
import time
from skills.download_manager.helpers import add_download, check_status, get_file_path

# Step 1: Add download
download_id = add_download(
    url="https://example.com/large-dataset.tar.gz",
    output_filename="dataset.tar.gz"
)
print(f"Queued download: {download_id}")

# Step 2: Poll for completion
max_wait = 300  # 5 minutes
start_time = time.time()

while time.time() - start_time < max_wait:
    status = check_status(download_id)
    
    if status == "complete":
        file_path = get_file_path(download_id)
        print(f"✓ Download complete: {file_path}")
        break
    elif status == "failed":
        print("✗ Download failed")
        break
    else:
        print(f"Status: {status}...")
        time.sleep(10)  # Wait before checking again
else:
    print("Timeout waiting for download")
```

---

## Example Scenarios

### 1. Download Dataset for Analysis

```python
from skills.download_manager.helpers import add_download, check_status, get_file_path
import pandas as pd
import time

# Download a CSV dataset
download_id = add_download(
    url="https://example.com/data/sales-2025.csv",
    output_filename="sales-2025.csv"
)

# Wait for completion
while check_status(download_id) != "complete":
    time.sleep(5)

# Load and analyze
file_path = get_file_path(download_id)
df = pd.read_csv(file_path)
print(f"Loaded {len(df)} rows of data")
print(df.head())
```

### 2. Download Code Repository

```python
from skills.download_manager.helpers import add_download, check_status, get_file_path
import zipfile
import time

# Download a GitHub repository archive
download_id = add_download(
    url="https://github.com/user/repo/archive/refs/heads/main.zip",
    output_filename="repo-main.zip"
)

# Wait for download
while check_status(download_id) != "complete":
    time.sleep(5)

# Extract and use
zip_path = get_file_path(download_id)
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall("extracted-repo")
    
print("Repository extracted to extracted-repo/")
```

### 3. Download Model Weights

```python
from skills.download_manager.helpers import add_download, check_status, get_file_path
import time

# Download large model file (can take a while)
download_id = add_download(
    url="https://example.com/models/bert-base-uncased.pt",
    output_filename="bert-base-uncased.pt"
)

print("Download started (this may take several minutes)...")

# Poll with progress updates
last_check = time.time()
while True:
    status = check_status(download_id)
    
    if status == "complete":
        model_path = get_file_path(download_id)
        print(f"✓ Model downloaded: {model_path}")
        print(f"  Size: {model_path.stat().st_size / 1024 / 1024:.1f} MB")
        break
    elif status == "failed":
        print("✗ Download failed")
        break
    elif time.time() - last_check > 30:
        print(f"  Still downloading... (status: {status})")
        last_check = time.time()
    
    time.sleep(10)
```

### 4. Batch Downloads

```python
from skills.download_manager.helpers import add_download, check_status, get_file_path
import time

# Queue multiple downloads
files_to_download = [
    ("https://example.com/data1.csv", "data1.csv"),
    ("https://example.com/data2.csv", "data2.csv"),
    ("https://example.com/data3.csv", "data3.csv"),
]

download_ids = []
for url, filename in files_to_download:
    download_id = add_download(url, filename)
    download_ids.append(download_id)
    print(f"Queued: {filename}")

# Wait for all to complete
print("\nWaiting for downloads to complete...")
while True:
    statuses = [check_status(did) for did in download_ids]
    complete_count = sum(1 for s in statuses if s == "complete")
    
    print(f"Progress: {complete_count}/{len(download_ids)} complete")
    
    if all(s in ["complete", "failed"] for s in statuses):
        break
    
    time.sleep(10)

# Get all completed files
completed_files = []
for download_id in download_ids:
    if check_status(download_id) == "complete":
        file_path = get_file_path(download_id)
        completed_files.append(file_path)

print(f"\n✓ {len(completed_files)} files downloaded successfully")
```

---

## Helper Functions

See `helpers.py` for the complete implementation. The module provides:

1. **add_download()** - Queue a new download task
2. **check_status()** - Check if download is complete/in-progress/failed
3. **get_file_path()** - Get path to downloaded file if complete
4. **list_downloads()** - List all downloads and their statuses
5. **wait_for_download()** - Blocking wait for download completion

All functions are designed to be agent-friendly with clear return values and error handling.

---

## Usage Example

```python
from skills.download_manager.helpers import add_download, check_status, get_file_path

# Add download
download_id = add_download("https://example.com/file.zip", "file.zip")

# Later, check status
if check_status(download_id) == "complete":
    file = get_file_path(download_id)
    print(f"File ready at: {file}")
```

---

## Advanced Usage

### Custom Download ID

```python
# Use custom ID for tracking
download_id = add_download(
    url="https://example.com/data.json",
    output_filename="data.json",
    download_id="critical-dataset-v1"
)
```

### Wait with Timeout

```python
from skills.download_manager.helpers import wait_for_download

# Wait up to 5 minutes
file_path = wait_for_download(
    download_id="my-download",
    timeout=300,
    poll_interval=10
)

if file_path:
    print(f"Download complete: {file_path}")
else:
    print("Download timed out or failed")
```

### List All Downloads

```python
from skills.download_manager.helpers import list_downloads

downloads = list_downloads()
for download in downloads:
    print(f"{download['id']}: {download['status']}")
```

---

## Troubleshooting

### Download Stuck in "pending"

- Check if downloader.py is running
- Check logs in logs/downloader_*.log
- Verify the queue file is valid JSON

### Download Failed

- Check URL is accessible
- Check network connectivity
- Review error in logs
- Trigger file remains in queue/ for retry

### File Not Found After Completion

- Verify download_id matches
- Check the completed/ directory for the trigger
- Ensure output_filename doesn't include path separators

---

## Architecture

```
Agent Code
    ↓
add_download() → Creates JSON in queue/
    ↓
downloader.py (background process)
    ↓
Downloads to downloads/
    ↓
Moves trigger to completed/
    ↓
check_status() → Reads queue/ and completed/
    ↓
get_file_path() → Returns Path from downloads/
```

The file-based queue system provides:
- **Decoupling**: Agent and downloader run independently
- **Persistence**: Downloads survive restarts
- **Observability**: Easy to inspect queue, downloads, and completed
- **Simplicity**: No database or complex IPC needed
