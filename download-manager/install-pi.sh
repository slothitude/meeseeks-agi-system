#!/bin/bash
#
# Download Manager Installation Script for Raspberry Pi
# Run this on sloth_pibot (192.168.0.237)
#
# Usage: curl -sSL https://your-server/install-pi.sh | bash
# Or: scp install-pi.sh pi@192.168.0.237:~ && ssh pi@192.168.0.237 "bash install-pi.sh"
#

set -e  # Exit on error

echo "🦥 Download Manager Installation for sloth_pibot"
echo "================================================"
echo ""

# Configuration
ARIA2_SECRET="${ARIA2_SECRET:-sloth_download_token}"
DOWNLOAD_DIR="${DOWNLOAD_DIR:-/home/pi/downloads}"
LOG_DIR="${LOG_DIR:-/home/pi/logs/aria2}"
CONFIG_DIR="${CONFIG_DIR:-/home/pi/.aria2}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as pi user
if [ "$USER" != "pi" ]; then
    log_warn "Not running as 'pi' user. Current user: $USER"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 1: Update system
log_info "Updating package lists..."
sudo apt update -qq

# Step 2: Install aria2
log_info "Installing aria2..."
if ! command -v aria2c &> /dev/null; then
    sudo apt install -y aria2
else
    log_info "aria2 already installed: $(aria2c --version | head -1)"
fi

# Step 3: Create directories
log_info "Creating directories..."
mkdir -p "$DOWNLOAD_DIR"
mkdir -p "$LOG_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$DOWNLOAD_DIR/games"
mkdir -p "$DOWNLOAD_DIR/software"
mkdir -p "$DOWNLOAD_DIR/media"
mkdir -p "$DOWNLOAD_DIR/other"

# Step 4: Create aria2 configuration
log_info "Creating aria2 configuration..."
cat > "$CONFIG_DIR/aria2.conf" << EOF
# Download Manager Configuration for sloth_pibot
# Generated: $(date)

# === Basic Settings ===
dir=$DOWNLOAD_DIR
continue=true
max-concurrent-downloads=3
max-connection-per-server=4

# === RPC Settings (for remote control by agents) ===
enable-rpc=true
rpc-listen-all=false
rpc-listen-port=6800
rpc-secret=$ARIA2_SECRET
rpc-allow-origin-all=true

# === Logging ===
log=$LOG_DIR/aria2.log
log-level=warn

# === Performance ===
min-split-size=10M
split=4

# === File Allocation ===
# Use 'none' for faster start on SD cards
file-allocation=none

# === Session Management ===
save-session-interval=30
input-file=$CONFIG_DIR/aria2.session
save-session=$CONFIG_DIR/aria2.session

# === Connection Settings ===
timeout=60
connect-timeout=30
max-tries=5
retry-wait=10

# === BT/Torrent Settings ===
bt-enable-lpd=true
bt-max-peers=50
seed-time=0
# Don't seed after download (Pi has limited storage)

# === User Agent ===
user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

# === Auto File Renaming ===
auto-file-renaming=true

# === Check Certificate ===
check-certificate=true

# === Disk Cache ===
disk-cache=16M
EOF

# Create session file if it doesn't exist
touch "$CONFIG_DIR/aria2.session"

log_info "Configuration created at $CONFIG_DIR/aria2.conf"

# Step 5: Create systemd service
log_info "Creating systemd service..."
sudo tee /etc/systemd/system/aria2.service > /dev/null << EOF
[Unit]
Description=aria2 Download Manager
Documentation=https://aria2.github.io/manual/en/html/
After=network.target
Wants=network-online.target

[Service]
Type=forking
ExecStart=/usr/bin/aria2c --daemon --conf-path=$CONFIG_DIR/aria2.conf
ExecReload=/bin/kill -HUP \$MAINPID
ExecStop=/bin/kill -s STOP \$MAINPID
RestartSec=5
Restart=on-failure
User=$USER
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF

log_info "Systemd service created"

# Step 6: Enable and start aria2
log_info "Enabling and starting aria2 service..."
sudo systemctl daemon-reload
sudo systemctl enable aria2
sudo systemctl restart aria2

# Wait a moment for service to start
sleep 2

# Check if service is running
if sudo systemctl is-active --quiet aria2; then
    log_info "aria2 service started successfully"
else
    log_error "aria2 service failed to start"
    log_info "Check logs: sudo journalctl -u aria2 -n 50"
    exit 1
fi

# Step 7: Configure firewall (if ufw is installed)
if command -v ufw &> /dev/null; then
    log_info "Configuring firewall..."
    sudo ufw allow from 192.168.0.0/24 to any port 6800 comment 'aria2 RPC'
    log_info "Firewall rule added for aria2 RPC"
fi

# Step 8: Verify installation
log_info "Verifying installation..."
sleep 1

# Test RPC
if curl -s -d '{"jsonrpc":"2.0","method":"aria2.getVersion","id":"test"}' \
    http://localhost:6800/jsonrpc | grep -q "aria2"; then
    log_info "aria2 RPC is responding correctly"
else
    log_warn "aria2 RPC might not be responding. Check configuration."
fi

# Show status
echo ""
echo "================================================"
log_info "Installation Complete!"
echo ""
echo "Configuration:"
echo "  - Config file: $CONFIG_DIR/aria2.conf"
echo "  - Download dir: $DOWNLOAD_DIR"
echo "  - Log file: $LOG_DIR/aria2.log"
echo "  - RPC port: 6800"
echo "  - RPC secret: $ARIA2_SECRET"
echo ""
echo "Commands:"
echo "  - Check status: sudo systemctl status aria2"
echo "  - View logs: tail -f $LOG_DIR/aria2.log"
echo "  - Restart: sudo systemctl restart aria2"
echo "  - Stop: sudo systemctl stop aria2"
echo ""
echo "Integration:"
echo "  - RPC URL: http://192.168.0.237:6800/jsonrpc"
echo "  - Use trigger.py from Sloth_rog to control downloads"
echo ""
echo "⚠️  IMPORTANT: Save your RPC secret: $ARIA2_SECRET"
echo "   Set this in your agent's environment: ARIA2_SECRET=$ARIA2_SECRET"
echo ""
