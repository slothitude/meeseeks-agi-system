# Quick Start Guide for Agents

## For Sloth_rog (Windows Agent)

### Quick Download
```python
from download_manager.trigger import download, status

# Start a download
gid = download(
    "https://example.com/large-file.zip",
    filename="myfile.zip"
)

# Check progress
info = status(gid)
print(f"Progress: {info['progress']}%")
```

### Full Control
```python
from download_manager.trigger import DownloadManager

dm = DownloadManager()

# Add download with options
result = dm.add_download(
    url="https://example.com/game.iso",
    filename="game.iso",
    directory="/home/pi/downloads/games",
    connections=8
)

# Monitor progress
info = dm.get_status(result['gid'])
print(f"Speed: {info['download_speed_human']}/s")
print(f"Progress: {info['progress']}%")

# Pause/Resume
dm.pause(result['gid'])
dm.resume(result['gid'])

# List all
active = dm.list_active()
for d in active:
    print(f"[{d['gid']}] {d['filename']} - {d['progress']}%")
```

### CLI Quick Commands
```bash
# Add download
python C:\Users\aaron\.openclaw\workspace\download-manager\trigger.py add --url "https://example.com/file.zip"

# List downloads
python C:\Users\aaron\.openclaw\workspace\download-manager\trigger.py list

# Check status
python C:\Users\aaron\.openclaw\workspace\download-manager\trigger.py status --gid "DOWNLOAD_ID"

# Get stats
python C:\Users\aaron\.openclaw\workspace\download-manager\trigger.py stats
```

## For sloth_pibot (Pi Agent)

### Check aria2 Status
```bash
sudo systemctl status aria2
```

### Monitor Downloads
```bash
# One-time status
python3 ~/download-manager/monitor.py

# Continuous monitoring
python3 ~/download-manager/monitor.py --watch

# With notifications
python3 ~/download-manager/monitor.py --watch --notify
```

### View Logs
```bash
# aria2 logs
tail -f ~/logs/aria2/aria2.log

# Monitor logs
tail -f ~/logs/aria2/monitor.log
```

### Restart aria2
```bash
sudo systemctl restart aria2
```

## Common Tasks

### Download a Game
```python
from download_manager.trigger import DownloadManager

dm = DownloadManager()
result = dm.add_download(
    url="GAME_URL_HERE",
    directory="/home/pi/downloads/games"
)
```

### Download Software
```python
result = dm.add_download(
    url="SOFTWARE_URL",
    directory="/home/pi/downloads/software"
)
```

### Download Media
```python
result = dm.add_download(
    url="MEDIA_URL",
    directory="/home/pi/downloads/media"
)
```

### Batch Downloads
```python
urls = ["URL1", "URL2", "URL3"]
for url in urls:
    dm.add_download(url)
```

### Check if aria2 is Running
```python
if dm.is_healthy():
    print("aria2 is running")
else:
    print("aria2 is down!")
```

## File Locations on Pi

- **Downloads**: `/home/pi/downloads/`
  - `/home/pi/downloads/games/`
  - `/home/pi/downloads/software/`
  - `/home/pi/downloads/media/`
  - `/home/pi/downloads/other/`
- **Config**: `/home/pi/.aria2/aria2.conf`
- **Logs**: `/home/pi/logs/aria2/aria2.log`
- **Session**: `/home/pi/.aria2/aria2.session`

## Access from Windows

Downloaded files are accessible via:
```
\\192.168.0.237\pi-share\downloads\
```

## Troubleshooting

### aria2 not responding
```bash
# On Pi
sudo systemctl restart aria2
sudo systemctl status aria2
```

### RPC connection refused
```bash
# Check if port is open
netstat -tlnp | grep 6800

# Check config
grep rpc ~/.aria2/aria2.conf
```

### Downloads not starting
```bash
# Check logs
tail -f ~/logs/aria2/aria2.log

# Test manually
aria2c "https://test.com/file"
```

## Integration with Agent Workflows

### Pattern 1: Fire and Forget
```python
# Just start the download, don't wait
gid = download(url, filename="file.zip")
# Agent continues with other tasks
```

### Pattern 2: Monitor and Report
```python
# Start download
gid = download(url)

# Check periodically
while True:
    info = status(gid)
    if info['status'] == 'complete':
        notify_user(f"Download complete: {info['filename']}")
        break
    elif info['status'] == 'error':
        notify_user(f"Download failed: {info['error_message']}")
        break
    time.sleep(60)  # Check every minute
```

### Pattern 3: Batch with Priority
```python
# Add high priority download
dm.add_download(url1)  # Added first = higher priority

# Add lower priority downloads
dm.add_download(url2)
dm.add_download(url3)
```
