# OpenAI Proxy Setup for Raspberry Pi 5

Deploy the OpenAI-compatible proxy on Pi5 to connect Goose CLI to OpenWebUI.

## Machine-Specific Model Names

- **Rog (Windows):** `goose_rog`, `openclaw_rog`
- **Pibot (Pi5):** `goose_pibot`, `openclaw_pibot`

## Quick Install on Pi5

### 1. Create Directory and Copy Script

```bash
ssh az@192.168.0.237
mkdir -p ~/openai-proxy
```

From Windows:
```powershell
scp C:\Users\aaron\.openclaw\workspace\skills\openai-proxy\scripts\openai-proxy-multi.js az@192.168.0.237:~/openai-proxy/
```

### 2. Install Dependencies

```bash
cd ~/openai-proxy
npm init -y
npm install express body-parser yargs
```

### 3. Test

```bash
node openai-proxy-multi.js --port 3001 --backend goose
```

Expected output:
```
OpenAI Multi-Agent Proxy
Machine: pibot
Port: 3001
Models: goose_pibot, openclaw_pibot
Default: goose
```

### 4. Systemd Service (Auto-start)

```bash
sudo nano /etc/systemd/system/openai-proxy.service
```

Paste:
```ini
[Unit]
Description=OpenAI Proxy for Goose/OpenClaw
After=network.target

[Service]
Type=simple
User=az
WorkingDirectory=/home/az/openai-proxy
ExecStart=/usr/bin/node /home/az/openai-proxy/openai-proxy-multi.js --port 3001 --backend goose
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable openai-proxy
sudo systemctl start openai-proxy
sudo systemctl status openai-proxy
```

## Configure OpenWebUI

Add connection:
- **Name:** Goose Pibot
- **Base URL:** `http://192.168.0.237:3001/v1`
- **API Key:** (any value)
- **Model:** `goose_pibot`

## Multiple Machines

| Machine | Base URL | Model |
|---------|----------|-------|
| Rog | `http://100.107.34.12:3001/v1` | `goose_rog` |
| Pibot | `http://192.168.0.237:3001/v1` | `goose_pibot` |

## Command Line Options

```bash
node openai-proxy-multi.js [options]

Options:
  -p, --port <number>     HTTP server port (default: 3001)
  -b, --backend <string>  Default backend: openclaw|goose (default: openclaw)
  -s, --suffix <string>   Machine suffix for model names (auto-detected)
  -v, --verbose           Enable verbose logging
  --help                  Show help
```

## Troubleshooting

```bash
sudo systemctl status openai-proxy
sudo journalctl -u openai-proxy -f
curl http://localhost:3001/health
```
