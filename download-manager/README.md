# Download Manager for Agent Network

A centralized download manager solution for Sloth_rog (Windows) and sloth_pibot (Raspberry Pi).

## Overview

This system uses **aria2** as the download manager, chosen because:
- ✅ Cross-platform (Linux + Windows)
- ✅ Remote control via JSON-RPC API
- ✅ Supports HTTP/HTTPS, FTP, BitTorrent, Metalink
- ✅ Multi-connection downloads (faster)
- ✅ Resume support
- ✅ Queue management
- ✅ Lightweight and mature

## Architecture

```
┌─────────────────┐          ┌──────────────────┐
│  Sloth_rog      │          │  sloth_pibot     │
│  (Windows)      │          │  (Raspberry Pi)  │
├─────────────────┤          ├──────────────────┤
│  Agent Script   │          │  aria2 Daemon    │
│  (trigger.py)   │◄────────►│  (RPC:6800)      │
└─────────────────┘          └──────────────────┘
                                      │
                                      ▼
                             ┌──────────────────┐
                             │  pi-share        │
                             │  Downloads/      │
                             └──────────────────┘
```

**Design Decision:** aria2 runs on the Pi because:
- Pi is always-on (downloads can continue 24/7)
- Downloads go directly to shared storage
- Lower power consumption for long downloads
- Both agents can trigger via RPC

## Installation

### On Raspberry Pi (sloth_pibot)

```bash
# Install aria2
sudo apt update
sudo apt install aria2 -y

# Create directories
mkdir -p ~/downloads ~/logs/aria2

# Create configuration
cat > ~/.aria2/aria2.conf << 'EOF'
# Basic Settings
dir=/home/pi/downloads
continue=true
max-concurrent-downloads=3
max-connection-per-server=4

# RPC Settings (for remote control)
enable-rpc=true
rpc-listen-all=false
rpc-listen-port=6800
rpc-secret=YOUR_SECRET_TOKEN_HERE

# Logging
log=/home/pi/logs/aria2/aria2.log
log-level=warn

# Performance
min-split-size=10M
split=4

# File allocation (none for faster start on Pi's SD card)
file-allocation=none

# Auto save session every 30 seconds
save-session-interval=30
input-file=/home/pi/.aria2/aria2.session
save-session=/home/pi/.aria2/aria2.session
EOF

# Create session file
touch ~/.aria2/aria2.session

# Create systemd service
sudo tee /etc/systemd/system/aria2.service > /dev/null << 'EOF'
[Unit]
Description=aria2 Service
After=network.target

[Service]
Type=forking
ExecStart=/usr/bin/aria2c --daemon --conf-path=/home/pi/.aria2/aria2.conf
ExecReload=/bin/kill -HUP $MAINPID
ExecStop=/bin/kill -s STOP $MAINPID
RestartSec=5
Restart=on-failure
User=pi

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable aria2
sudo systemctl start aria2

# Check status
sudo systemctl status aria2
```

### On Windows (Sloth_rog)

```powershell
# Using scoop (recommended)
scoop install aria2

# Or using chocolatey
choco install aria2

# Or download manually from: https://github.com/aria2/aria2/releases
```

## Usage for Agents

### Method 1: Direct RPC (Recommended)

Both agents can trigger downloads via HTTP requests to the Pi's aria2 RPC:

```python
import requests
import json

ARIA2_RPC = "http://192.168.0.237:6800/jsonrpc"
RPC_SECRET = "YOUR_SECRET_TOKEN_HERE"

def add_download(url, filename=None, directory=None):
    """Add a download to aria2 queue."""
    params = [f"token:{RPC_SECRET}", [url]]
    
    options = {}
    if filename:
        options["out"] = filename
    if directory:
        options["dir"] = directory
    
    if options:
        params.append(options)
    
    response = requests.post(ARIA2_RPC, json={
        "jsonrpc": "2.0",
        "id": "agent",
        "method": "aria2.addUri",
        "params": params
    })
    
    return response.json()

def get_status(gid):
    """Get download status."""
    response = requests.post(ARIA2_RPC, json={
        "jsonrpc": "2.0",
        "id": "agent",
        "method": "aria2.tellStatus",
        "params": [f"token:{RPC_SECRET}", gid]
    })
    return response.json()

def list_downloads():
    """List all active downloads."""
    response = requests.post(ARIA2_RPC, json={
        "jsonrpc": "2.0",
        "id": "agent",
        "method": "aria2.tellActive",
        "params": [f"token:{RPC_SECRET}"]
    })
    return response.json()
```

### Method 2: Command Line (Local)

```bash
# Add download
aria2c --dir=/path/to/save "https://example.com/file.zip"

# With RPC to Pi
aria2c --dir=/home/pi/downloads \
       --enable-rpc=false \
       "https://example.com/file.zip"
```

### Method 3: File-Based Queue

Drop `.txt` files into a watched directory:

```python
# Agent creates a queue file
queue_content = "https://example.com/file.zip\n  dir=/home/pi/downloads\n  out=myfile.zip"
with open("//192.168.0.237/pi-share/queue/download-001.txt", "w") as f:
    f.write(queue_content)
```

## Integration Scripts

### For Sloth_rog (Windows Agent)

Located in: `download-manager/trigger.py`

### For sloth_pibot (Pi Agent)

Located in: `download-manager/monitor.py`

## Web UI (Optional)

aria2 has several web frontends:
- **webui-aria2**: https://github.com/ziahamza/webui-aria2
- **AriaNg**: https://github.com/mayswind/AriaNg

Install on Pi:
```bash
# Install webui-aria2
cd /var/www/html
sudo git clone https://github.com/ziahamza/webui-aria2
# Access at: http://192.168.0.237/webui-aria2
```

## API Reference

### Common aria2 RPC Methods

| Method | Description | Example |
|--------|-------------|---------|
| `aria2.addUri` | Add HTTP/FTP download | `[token, ["http://..."], {dir: "/path"}]` |
| `aria2.addTorrent` | Add torrent | `[token, [torrentData], options]` |
| `aria2.tellStatus` | Get download status | `[token, gid]` |
| `aria2.tellActive` | List active downloads | `[token]` |
| `aria2.pause` | Pause download | `[token, gid]` |
| `aria2.unpause` | Resume download | `[token, gid]` |
| `aria2.remove` | Remove download | `[token, gid]` |
| `aria2.getGlobalStat` | Global statistics | `[token]` |

## Security

1. **RPC Secret**: Always set a strong secret token
2. **Firewall**: Only allow local network access to port 6800
3. **TLS**: Can enable HTTPS for RPC if needed

```bash
# On Pi, restrict to local network
sudo ufw allow from 192.168.0.0/24 to any port 6800
```

## Troubleshooting

### aria2 not starting
```bash
# Check logs
tail -f ~/logs/aria2/aria2.log

# Test config
aria2c --conf-path=~/.aria2/aria2.conf --dry-run
```

### RPC connection refused
```bash
# Check if aria2 is listening
netstat -tlnp | grep 6800

# Check RPC settings
grep rpc ~/.aria2/aria2.conf
```

### Downloads failing
```bash
# Test manually
aria2c -d /home/pi/downloads "https://test.com/file"
```

## Files in This Package

- `README.md` - This documentation
- `trigger.py` - Python module for agents to trigger downloads
- `monitor.py` - Download status monitor (runs on Pi)
- `install-pi.sh` - Automated installation script for Pi
- `test-connection.py` - Test RPC connectivity
- `examples/` - Usage examples

## Next Steps

1. Run `install-pi.sh` on the Pi
2. Update `RPC_SECRET` in `trigger.py`
3. Test with `python test-connection.py`
4. Integrate into agent workflows

## License

MIT - Part of the Slothitude Games agent ecosystem.
