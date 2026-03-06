# Download Manager for Agent Network

A simple, cross-platform download manager that works on both Windows (Sloth_rog) and Pi (sloth_pibot). Agents can trigger downloads via JSON files or HTTP API.

## Features

- **Cross-platform**: Works on Windows and Linux/Pi
- **Multiple trigger methods**: JSON files or HTTP API
- **Automatic retry**: Built-in retry logic for failed downloads
- **Progress tracking**: Logs download progress
- **Safe filenames**: Sanitizes filenames for cross-platform compatibility
- **Organized structure**: Separate folders for completed/failed triggers

## Quick Start

### 1. Install Dependencies

```bash
pip install requests
```

### 2. Start the Download Manager

```bash
# Watch mode (continuous) - recommended for agents
python download_manager.py --watch

# Or process once
python download_manager.py --once

# Or start API server
python download_manager.py --api
```

### 3. Trigger a Download

**Method A: Create a trigger file**

Write a JSON file to the trigger directory:

```json
{
  "url": "https://example.com/file.zip"
}
```

**Method B: Use the API**

```bash
curl -X POST http://localhost:8765/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/file.zip"}'
```

**Method C: Use the command line**

```bash
python download_manager.py --create --url "https://example.com/file.zip"
```

## Directory Structure

```
\\192.168.0.237\pi-share\
├── downloads/                    # Downloaded files go here
│   └── [subfolders if specified]
└── download_triggers/
    ├── trigger_20260303_123456_abc123.json  # Pending triggers
    ├── completed/                # Successfully processed triggers
    └── failed/                   # Failed triggers (with error info)
```

On Linux/Pi, the default paths are:
- Downloads: `/mnt/pi-share/downloads`
- Triggers: `/mnt/pi-share/download_triggers`

## Trigger File Format

### Minimal Example

```json
{
  "url": "https://example.com/file.zip"
}
```

### Full Example

```json
{
  "url": "https://example.com/file.zip",
  "filename": "my_custom_name.zip",
  "headers": {
    "User-Agent": "MyCustomAgent/1.0",
    "Authorization": "Bearer token123"
  },
  "subfolder": "projects/myproject"
}
```

### Fields

| Field | Required | Type | Description |
|-------|----------|------|-------------|
| `url` | Yes | string | URL to download (http, https, ftp) |
| `filename` | No | string | Custom filename (auto-detected if omitted) |
| `headers` | No | object | Custom HTTP headers |
| `subfolder` | No | string | Subfolder within downloads directory |

### Result Fields (added after processing)

After processing, the trigger file will have a `result` field:

**Success:**
```json
{
  "url": "https://example.com/file.zip",
  "result": {
    "status": "completed",
    "filepath": "\\\\192.168.0.237\\pi-share\\downloads\\file.zip",
    "completed_at": "2026-03-03T22:16:00.123456"
  }
}
```

**Failure:**
```json
{
  "url": "https://example.com/file.zip",
  "result": {
    "status": "failed",
    "error": "HTTP 404: Not Found",
    "failed_at": "2026-03-03T22:16:00.123456"
  }
}
```

## API Reference

### GET /status

Check server status.

**Response:**
```json
{
  "status": "running",
  "download_dir": "\\\\192.168.0.237\\pi-share\\downloads",
  "trigger_dir": "\\\\192.168.0.237\\pi-share\\download_triggers"
}
```

### POST /download

Trigger a new download.

**Request body:**
```json
{
  "url": "https://example.com/file.zip",
  "filename": "optional_name.zip",
  "headers": {},
  "subfolder": "optional/path"
}
```

**Response:**
```json
{
  "status": "triggered",
  "trigger_file": "\\\\192.168.0.237\\pi-share\\download_triggers\\trigger_20260303_221600_abc123.json"
}
```

## Usage Examples

### From Python (agent script)

```python
import json
from pathlib import Path

# Method 1: Write trigger file
trigger_dir = Path(r"\\192.168.0.237\pi-share\download_triggers")
trigger_file = trigger_dir / "my_download.json"

trigger_data = {
    "url": "https://example.com/file.zip",
    "filename": "important_file.zip"
}

with open(trigger_file, 'w') as f:
    json.dump(trigger_data, f, indent=2)

# Method 2: Use API
import requests
response = requests.post('http://localhost:8765/download', json={
    "url": "https://example.com/file.zip"
})
print(response.json())
```

### From Shell

```bash
# Create trigger file
echo '{"url": "https://example.com/file.zip"}' > /mnt/pi-share/download_triggers/my_download.json

# Or use curl with API
curl -X POST http://localhost:8765/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/file.zip"}'
```

### From PowerShell

```powershell
# Create trigger file
$trigger = @{
    url = "https://example.com/file.zip"
    filename = "my_file.zip"
} | ConvertTo-Json

$trigger | Out-File "\\192.168.0.237\pi-share\download_triggers\my_download.json" -Encoding UTF8
```

## Running as a Service

### On Windows (with Task Scheduler or NSSM)

```powershell
# Using NSSM (Non-Sucking Service Manager)
nssm install DownloadManager python "C:\path\to\download_manager.py" --watch
nssm start DownloadManager
```

### On Linux/Pi (with systemd)

Create `/etc/systemd/system/download-manager.service`:

```ini
[Unit]
Description=Download Manager for Agent Network
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/download_manager
ExecStart=/usr/bin/python3 download_manager.py --watch
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable download-manager
sudo systemctl start download-manager
```

## Configuration

### Custom Paths

```bash
python download_manager.py \
  --download-dir /custom/downloads \
  --trigger-dir /custom/triggers \
  --watch
```

### Watch Interval

```bash
# Check every 10 seconds instead of default 5
python download_manager.py --interval 10 --watch
```

### API Port

```bash
# Run API on custom port
python download_manager.py --api --port 9000
```

## Troubleshooting

### Network share not accessible

**Windows:** Ensure the share is mounted and accessible:
```powershell
Test-Path "\\192.168.0.237\pi-share"
```

**Linux:** Ensure the share is mounted:
```bash
mount | grep pi-share
# If not mounted:
sudo mount -t cifs //192.168.0.237/pi-share /mnt/pi-share -o user=youruser
```

### Downloads failing

Check the `failed/` directory for trigger files with error details. Common issues:
- Network connectivity
- Invalid URL
- Authentication required (add `headers`)
- Disk space

### Permission denied

Ensure the user running the script has write permissions to:
- Download directory
- Trigger directory
- Completed/Failed directories

## Integration with Agents

### Sloth_rog (Windows)

```python
TRIGGER_DIR = r"\\192.168.0.237\pi-share\download_triggers"
DOWNLOAD_DIR = r"\\192.168.0.237\pi-share\downloads"
```

### sloth_pibot (Pi/Linux)

```python
TRIGGER_DIR = "/mnt/pi-share/download_triggers"
DOWNLOAD_DIR = "/mnt/pi-share/downloads"
```

### Shared Function for Any Agent

```python
import json
from pathlib import Path
import platform

def get_download_dirs():
    """Get platform-appropriate download directories."""
    if platform.system() == 'Windows':
        return {
            'triggers': Path(r"\\192.168.0.237\pi-share\download_triggers"),
            'downloads': Path(r"\\192.168.0.237\pi-share\downloads")
        }
    else:
        return {
            "triggers": Path("/mnt/pi-share/download_triggers"),
            "downloads": Path("/mnt/pi-share/downloads")
        }

def trigger_download(url: str, filename: str = None, subfolder: str = None):
    """Trigger a download from any agent."""
    import hashlib
    from datetime import datetime
    
    dirs = get_download_dirs()
    dirs['triggers'].mkdir(parents=True, exist_ok=True)
    
    data = {
        'url': url,
        'created_at': datetime.now().isoformat(),
        'created_by': platform.node()
    }
    
    if filename:
        data['filename'] = filename
    if subfolder:
        data['subfolder'] = subfolder
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
    trigger_file = dirs['triggers'] / f"trigger_{timestamp}_{url_hash}.json"
    
    with open(trigger_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    return trigger_file

# Usage
trigger_download("https://example.com/file.zip", filename="myfile.zip")
```

## License

MIT License - Free for agent network use.
