# Quick Start - Agent Network Download Manager

## For Agents

### Trigger a Download (Python)

```python
from agent_helper import trigger_download

# Simple
trigger_download("https://example.com/file.zip")

# With custom filename
trigger_download("https://example.com/file.zip", filename="myfile.zip")

# To subfolder
trigger_download("https://example.com/file.zip", subfolder="projects")
```

### Trigger a Download (Shell)

```bash
# Write JSON to trigger directory
echo '{"url": "https://example.com/file.zip"}' > /mnt/pi-share/download_triggers/my_download.json
```

### Trigger a Download (PowerShell)

```powershell
# Write JSON to trigger directory
$json = @{url = "https://example.com/file.zip"} | ConvertTo-Json
$json | Out-File "\\192.168.0.237\pi-share\download_triggers\my_download.json"
```

## For Humans

### Start Download Manager

```bash
# Watch mode (runs continuously)
python download_manager.py --watch

# Process once and exit
python download_manager.py --once

# Start API server
python download_manager.py --api
```

### Paths

| Platform | Downloads | Triggers |
|----------|-----------|----------|
| Windows (Sloth_rog) | `\\192.168.0.237\pi-share\downloads` | `\\192.168.0.237\pi-share\download_triggers` |
| Linux/Pi (sloth_pibot) | `/mnt/pi-share/downloads` | `/mnt/pi-share/download_triggers` |

### Trigger Format

```json
{
  "url": "https://example.com/file.zip",
  "filename": "optional_name.zip",
  "subfolder": "optional/path",
  "headers": {"Authorization": "Bearer token"}
}
```

### After Processing

- ✅ Success → trigger moved to `completed/`
- ❌ Failure → trigger moved to `failed/` with error info

### API Endpoints

- `GET /status` - Check server status
- `POST /download` - Trigger a download

```bash
curl -X POST http://localhost:8765/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/file.zip"}'
```

## Troubleshooting

**Network share not accessible:**
- Windows: Check `Test-Path "\\192.168.0.237\pi-share"`
- Linux: Check `mount | grep pi-share`

**Downloads failing:**
- Check `failed/` directory for trigger files with error details
- Common issues: network, auth, disk space

**Permission denied:**
- Ensure write access to download and trigger directories
