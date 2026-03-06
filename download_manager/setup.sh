#!/bin/bash
# Setup script for Linux/Pi (sloth_pibot)

echo "🦥 Setting up Download Manager for Pi..."

# Install dependencies
pip3 install -r requirements.txt

# Create systemd service (optional)
SERVICE_FILE="/etc/systemd/system/download-manager.service"

echo ""
echo "To run as a systemd service (auto-start on boot):"
echo "  sudo cp download-manager.service /etc/systemd/system/"
echo "  sudo systemctl enable download-manager"
echo "  sudo systemctl start download-manager"
echo ""
echo "To run manually:"
echo "  python3 download_manager.py --watch"
echo ""
echo "To test:"
echo "  python3 download_manager.py --once"
