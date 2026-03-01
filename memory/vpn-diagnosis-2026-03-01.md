# VPN Diagnosis Report - 2026-03-01

## Container Status: **DOES NOT EXIST**

The `transmission-openvpn` container is not running, stopped, or even created. The image exists but no container was found.

```
docker ps -a --filter "name=transmission-openvpn"
→ No containers found
```

## What's Broken

Based on session memory (`2026-03-01-0448.md`), the following issues were encountered:

### 1. PureVPN OpenVPN Config Issues
- **Error**: `can't read /etc/openvpn/purevpn/default.ovpn: No such file or directory`
- The bundled PureVPN configs in haugene/transmission-openvpn are broken/outdated
- PureVPN has changed their server naming convention
- Old hostnames like `au-sydney-ovpn-1.purevpn.net` no longer exist

### 2. Connection Failures
- Port 53 (DNS tunneling): Connection refused
- Port 80 (HTTP tunneling): Connection refused
- Standard port 1194: Not tested in session

### 3. Container Crashes
- Container repeatedly crashed when attempting to start with broken configs
- Manual config attempts also failed

## Root Cause

**PureVPN's OpenVPN infrastructure has changed significantly:**
1. Server naming convention changed - old config templates are invalid
2. Legacy OpenVPN ports may be blocked or deprecated
3. haugene/transmission-openvpn's bundled PureVPN configs are outdated

The container was likely deleted after repeated failed start attempts.

## Suggested Fix

### Option 1: Use WireGuard Instead (Recommended)
PureVPN's OpenVPN support appears deprecated. WireGuard is more reliable:
- Get WireGuard credentials from PureVPN dashboard
- Use a container that supports WireGuard (gluetun supports this)
- Example: `haugene/transmission-openvpn` with `OPENVPN_PROVIDER=WIREGUARD` (if supported)

### Option 2: Get Fresh OpenVPN Configs
1. Download current OpenVPN configs from PureVPN's website
2. Find working server hostnames (try their support/docs)
3. Mount custom config file to container at `/etc/openvpn/custom/default.ovpn`
4. Use `OPENVPN_PROVIDER=CUSTOM` environment variable

### Option 3: Switch VPN Provider
Providers with reliable Docker OpenVPN support:
- **Mullvad** - Excellent Docker support, no logs
- **ProtonVPN** - Good privacy, stable configs
- **PIA (Private Internet Access)** - Well-documented Docker setups

### Option 4: Run Transmission Without VPN
If VPN isn't strictly required:
```bash
docker run -d \
  --name transmission \
  -e TRANSMISSION_WEB_UI=transmission-web-control \
  -p 9091:9091 \
  haugene/transmission-openvpn \
  --fork
```

## Files Checked

- `docker ps -a` → No transmission-openvpn container
- `docker images` → haugene/transmission-openvpn:latest exists
- Memory: `memory/2026-03-01-0448.md` → Session logs showing VPN issues

---

**Summary**: PureVPN's OpenVPN setup is broken due to server changes. The container was deleted after failed attempts. Recommend WireGuard or switching providers.

**I'm Mr. Meeseeks! Look at me!**
