# OpenVPN + SearXNG Docker Setup

## Overview

Route SearXNG traffic through OpenVPN for privacy and to avoid rate limiting.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│                                                         │
│  ┌─────────────┐         ┌─────────────────────────┐   │
│  │  SearXNG    │ ──────▶ │       OpenVPN           │   │
│  │  (port 8888)│         │    (VPN Container)      │   │
│  └─────────────┘         └───────────┬─────────────┘   │
│                                      │                  │
└──────────────────────────────────────┼──────────────────┘
                                       │
                                       ▼
                              ┌────────────────┐
                              │   VPN Server   │
                              │  (External)    │
                              └────────────────┘
```

## Setup

### Step 1: Get OVPN Config

You need an `.ovpn` config file from your VPN provider (NordVPN, ExpressVPN, ProtonVPN, etc.)

Place it at: `C:\Users\aaron\.openclaw\workspace\vpn\config.ovpn`

### Step 2: Create Docker Network

```powershell
docker network create vpn-network
```

### Step 3: Start OpenVPN Container

```powershell
# Create vpn directory
New-Item -ItemType Directory -Force -Path "C:\Users\aaron\.openclaw\workspace\vpn"

# Copy your .ovpn file to vpn/ folder
# Then run:
docker run -d `
  --name openvpn-client `
  --cap-add=NET_ADMIN `
  --device=/dev/net/tun `
  --network vpn-network `
  -v C:\Users\aaron\.openclaw\workspace\vpn:/vpn `
  kylemanna/openvpn `
  ovpn_run --config /vpn/config.ovpn
```

### Step 4: Update SearXNG to Use VPN Network

Stop current SearXNG and restart with VPN network:

```powershell
cd C:\Users\aaron\.openclaw\workspace\searxng

# Stop current container
docker-compose down

# Update docker-compose.yml to add network
```

Edit `searxng/docker-compose.yml`:

```yaml
services:
  searxng:
    image: searxng/searxng:latest
    container_name: searxng
    # ... existing config ...
    network_mode: "service:openvpn-client"  # Route through VPN
    depends_on:
      - openvpn-client

  openvpn-client:
    image: kylemanna/openvpn
    container_name: openvpn-client
    cap_add:
      - NET_ADMIN
    devices:
      - /dev/net/tun
    volumes:
      - ../vpn:/vpn
    command: ovpn_run --config /vpn/config.ovpn
    restart: unless-stopped

networks:
  default:
    name: vpn-network
```

### Step 5: Verify VPN Connection

```powershell
# Check OpenVPN logs
docker logs openvpn-client

# Check your IP (should show VPN IP)
docker exec searxng curl -s ifconfig.me
```

## Alternative: Sidecar Pattern

If the network_mode approach doesn't work, use a sidecar:

```yaml
services:
  openvpn:
    image: kylemanna/openvpn
    cap_add:
      - NET_ADMIN
    devices:
      - /dev/net/tun
    volumes:
      - ./vpn:/vpn
    command: ovpn_run --config /vpn/config.ovpn
    restart: unless-stopped

  searxng:
    image: searxng/searxng:latest
    ports:
      - "8888:8080"
    environment:
      - HTTP_PROXY=http://openvpn:1080
    depends_on:
      - openvpn
```

## Testing

```powershell
# Test without VPN
curl -s ifconfig.me

# Test with VPN (through SearXNG container)
docker exec searxng curl -s ifconfig.me

# Should show different IPs
```

## VPN Providers

| Provider | OVPN Config Location |
|----------|---------------------|
| NordVPN | https://nordvpn.com/ovpn/ |
| ExpressVPN | https://www.expressvpn.com/setup#manual |
| ProtonVPN | https://account.protonvpn.com/downloads |
| Mullvad | https://mullvad.net/en/download/vpn |

## Troubleshooting

### DNS Leaks

Add to your `.ovpn` file:
```
script-security 2
up /etc/openvpn/update-resolv-conf
down /etc/openvpn/update-resolv-conf
```

### Kill Switch

If VPN drops, block traffic:
```yaml
# Add to docker-compose.yml
iptables -A OUTPUT ! -o tun0 -j DROP
```

### Check Connection

```powershell
# Inside container
docker exec -it openvpn-client sh
ping google.com
curl -s ifconfig.me
```

---

**Next Steps:**

1. Get `.ovpn` config from your VPN provider
2. Save to `vpn/config.ovpn`
3. Run: `docker-compose up -d`
4. Verify: `docker exec searxng curl -s ifconfig.me`
