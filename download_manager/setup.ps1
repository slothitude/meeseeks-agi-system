# Setup script for Windows (Sloth_rog)

Write-Host "🦥 Setting up Download Manager for Windows..."

# Install dependencies
pip install -r requirements.txt

Write-Host ""
Write-Host "Setup complete!"
Write-Host ""
Write-Host "To run manually:"
Write-Host "  python download_manager.py --watch"
Write-Host ""
Write-Host "To test:"
Write-Host "  python download_manager.py --once"
Write-Host ""
Write-Host "To start API server:"
Write-Host "  python download_manager.py --api"
Write-Host ""
Write-Host "For auto-start, use Task Scheduler or NSSM:"
Write-Host "  nssm install DownloadManager python `"$PWD\download_manager.py`" --watch"
