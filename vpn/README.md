# VPN Setup Instructions

## Quick Start

1. **Get your OVPN config** from your VPN provider
2. **Save it** to `vpn/config.ovpn`
3. **Run** the VPN-enabled SearXNG

## VPN Providers

### NordVPN
1. Go to: https://nordvpn.com/ovpn/
2. Download a server config (e.g., Australia)
3. Save as `vpn/config.ovpn`

### ProtonVPN (Free)
1. Go to: https://account.protonvpn.com/downloads
2. Download OpenVPN config
3. Save as `vpn/config.ovpn`

### Mullvad
1. Go to: https://mullvad.net/en/download/vpn
2. Download OpenVPN config
3. Save as `vpn/config.ovpn`

## Starting with VPN

```powershell
# Stop existing SearXNG
cd C:\Users\aaron\.openclaw\workspace\searxng
docker-compose down

# Start with VPN
cd C:\Users\aaron\.openclaw\workspace
docker-compose -f docker-compose.vpn.yml up -d
```

## Verify VPN

```powershell
# Check your real IP
curl -s ifconfig.me

# Check SearXNG's IP (should be different)
docker exec searxng curl -s ifconfig.me
```

## Troubleshooting

If it doesn't work, check:
```powershell
# OpenVPN logs
docker logs openvpn-client

# SearXNG logs
docker logs searxng
```

## Current Status

- ✅ OpenVPN Docker image pulled
- ✅ VPN directory created
- ✅ Docker compose file ready
- ⏳ Waiting for .ovpn config file

Place your `.ovpn` file at:
```
C:\Users\aaron\.openclaw\workspace\vpn\config.ovpn
```
