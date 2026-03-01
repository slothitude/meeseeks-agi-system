# Uninstall OpenAI Proxy Windows Service
#
# Usage: Run as Administrator
# .\uninstall-service.ps1

#Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"

$SERVICE_NAME = "OpenClawOpenAIProxy"

Write-Host "🦥 Uninstalling OpenAI Proxy Windows Service..." -ForegroundColor Green

# Check if service exists
try {
    $SERVICE = Get-Service -Name $SERVICE_NAME -ErrorAction SilentlyContinue

    if (-not $SERVICE) {
        Write-Host "⚠️  Service $SERVICE_NAME not found" -ForegroundColor Yellow
        Write-Host "   It may have already been uninstalled" -ForegroundColor Gray
        exit 0
    }

    # Stop service if running
    if ($SERVICE.Status -eq "Running") {
        Write-Host "🛑 Stopping service..." -ForegroundColor Yellow
        Stop-Service -Name $SERVICE_NAME -Force
        Start-Sleep -Seconds 2
    }

    # Remove service
    Write-Host "🗑️  Removing service..." -ForegroundColor Yellow
    Remove-Service -Name $SERVICE_NAME

    if ($?) {
        Write-Host "✅ Service removed successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to remove service" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red

    # Try sc.exe remove as fallback
    Write-Host "🔄 Trying sc.exe remove..." -ForegroundColor Yellow
    sc.exe delete $SERVICE_NAME
}
