# VPN Connection Issues - Troubleshooting

## Current Status

❌ PureVPN via Gluetun is not connecting

## Errors

1. **UDP (port 53):** TLS handshake failed
2. **TCP (port 80):** Connection refused

## Possible Causes

1. **Firewall/Router blocking** - Ports 53, 80 might be blocked
2. **PureVPN account issues** - Credentials may need verification
3. **Server availability** - PureVPN servers may be down
4. **Protocol/port combination** - Need different settings

## Solutions to Try

### 1. Verify PureVPN Account
- Login to https://my.purevpn.com/
- Check if account is active
- Verify credentials are correct

### 2. Try Different Ports
Add to docker-compose environment:
```yaml
- OPENVPN_PROTOCOL=udp
- OPENVPN_PORT=53
# Or try:
- OPENVPN_PORT=80
- OPENVPN_PORT=443
- OPENVPN_PORT=1194
```

### 3. Try Specific Server
```yaml
- SERVER_HOSTNAMES=nl-ams.purevpn.net
```

### 4. Check Firewall
```powershell
# Test if ports are blocked
Test-NetConnection -ComputerName purevpn.net -Port 53
Test-NetConnection -ComputerName purevpn.net -Port 80
Test-NetConnection -ComputerName purevpn.net -Port 443
```

### 5. Alternative: Use HTTP Proxy
If VPN doesn't work, use PureVPN's HTTP proxy instead:
```yaml
environment:
  - HTTP_PROXY=http://username:password@proxy.purevpn.net:8080
```

## Current Workaround

SearXNG is running WITHOUT VPN on port 8888:
```bash
curl -s "http://localhost:8888/search?q=test&format=json"
```

This works but traffic is not anonymized.

## Next Steps

1. Check if PureVPN account is active
2. Try different server locations
3. Test firewall connectivity
4. Consider alternative VPN providers

---

**VPN Status: NOT WORKING** ⚠️
**SearXNG Status: WORKING (no VPN)** ✅
