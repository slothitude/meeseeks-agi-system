# Download Manager

Simple Python-based download manager that watches a queue directory for trigger files and downloads URLs automatically.

## Directory Structure

```
download-manager/
├── downloader.py         # Main script
├── trigger_example.json  # Example trigger format
├── README.md            # This file
├── queue/               # Drop trigger files here
├── downloads/           # Downloaded files appear here
├── completed/           # Processed triggers moved here
└── logs/                # Log files
```

## Requirements

- Python 3.6+
- `requests` library (already available)

## Usage

### 1. Start the Downloader

```bash
python downloader.py
```

The script will:
- Create necessary directories if they don't exist
- Start watching the `queue/` directory
- Process any JSON trigger files found

### 2. Add Download Tasks

Create a JSON file in the `queue/` directory:

```json
{
  "url": "https://example.com/file.zip",
  "output": "file.zip",
  "id": "unique-download-id"
}
```

**Fields:**
- `url` (required): URL to download from
- `output` (required): Filename to save as (saved to `downloads/`)
- `id` (required): Unique identifier for this download
- `notes` (optional): Any additional context

### 3. Monitoring

**Logs:** Check `logs/downloader_YYYYMMDD.log` for detailed logs

**Console:** The script prints status messages to stdout

### 4. Stop the Downloader

Press `Ctrl+C` to gracefully stop the script

## Example Workflow

### For Agents/Automation

```python
import json
from pathlib import Path

# Create trigger file
trigger = {
    "url": "https://releases.ubuntu.com/22.04/ubuntu-22.04.3-desktop-amd64.iso",
    "output": "ubuntu-22.04.iso",
    "id": "ubuntu-download-001"
}

# Write to queue
queue_path = Path("skills/download-manager/queue/download-001.json")
queue_path.write_text(json.dumps(trigger, indent=2))
```

### Manual Usage

1. Copy `trigger_example.json` to `queue/my-download.json`
2. Edit the fields as needed
3. The downloader will pick it up within 5 seconds
4. Check `downloads/` for the file
5. Check `completed/` for the processed trigger

## Features

- **Automatic directory creation**: Creates queue, downloads, completed, and logs directories
- **Streaming downloads**: Handles large files efficiently
- **Logging**: Both file and console logging
- **Retry-friendly**: Failed downloads stay in queue for retry
- **Simple trigger format**: Just JSON with url, output, and id

## Configuration

Edit the variables at the top of `downloader.py` to customize:

- `poll_interval`: How often to check for new triggers (default: 5 seconds)
- Timeout settings in the `requests.get()` call

## Troubleshooting

**Download fails:**
- Check the URL is accessible
- Check network connectivity
- Review logs for error details

**Trigger not processed:**
- Ensure JSON is valid
- Check all required fields are present
- Verify file has `.json` extension

**Permission errors:**
- Ensure script has write access to all directories
- Check file permissions on queue/downloads/completed directories

## Integration with OpenClaw

This download manager is designed to work with OpenClaw agents:

1. Agent creates trigger file in `queue/`
2. Downloader processes it automatically
3. Agent can check `downloads/` for completed files
4. Agent can check `completed/` for status

Perfect for:
- Downloading large files asynchronously
- Batch download operations
- Automated file retrieval workflows
