# Install OpenAI Multi-Agent Proxy as Windows Service
#
# Agentic Mode (Function Calling) Support
#
# Usage: Run as Administrator
# .\install-service.ps1

#Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"

Write-Host "🦥 Installing OpenAI Multi-Agent Proxy as Windows Service..." -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Features:" -ForegroundColor Cyan
Write-Host "   ✅ Agentic Mode (Function Calling)" -ForegroundColor Green
Write-Host "   ✅ OpenClaw & Goose backends" -ForegroundColor Green
Write-Host "   ✅ OpenAI API v1 compatible" -ForegroundColor Green
Write-Host "   ✅ OpenWebUI Native Mode support" -ForegroundColor Green
Write-Host ""

# Configuration
$SERVICE_NAME = "OpenClawOpenAIProxy"
$SERVICE_DISPLAY = "OpenClaw OpenAI Proxy"
$SERVICE_DESC = "OpenAI-compatible HTTP API proxy for OpenClaw and Goose CLI. Supports Agentic Mode (function calling) with OpenWebUI Native Mode."

# Paths (adjust if you installed elsewhere)
$NODE_EXE = "node.exe"
$PROXY_SCRIPT = "C:\Users\aaron\.openclaw\workspace\skills\openai-proxy\scripts\openai-proxy-agentic.js"
$PROXY_DIR = "C:\Users\aaron\.openclaw\workspace\skills\openai-proxy\scripts"

# Verify paths exist
if (-not (Test-Path $NODE_EXE)) {
    Write-Host "❌ ERROR: Node.js not found at $NODE_EXE" -ForegroundColor Red
    Write-Host "   Install Node.js from https://nodejs.org" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $PROXY_SCRIPT)) {
    Write-Host "❌ ERROR: Agentic proxy script not found at $PROXY_SCRIPT" -ForegroundColor Red
    Write-Host "   Check: openai-proxy-agentic.js" -ForegroundColor Yellow
    exit 1
}

# Find Node.exe in PATH if needed
if (-not (Test-Path $NODE_EXE)) {
    Write-Host "🔍 Searching for node.exe in PATH..." -ForegroundColor Yellow
    $NODE_EXE = Get-Command node.exe -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
    if (-not $NODE_EXE) {
        Write-Host "❌ ERROR: node.exe not found in PATH" -ForegroundColor Red
        Write-Host "   Add Node.js to PATH or provide full path" -ForegroundColor Yellow
        exit 1
    }
}

# Create service using sc.exe
Write-Host "📝 Creating service..." -ForegroundColor Yellow

try {
    # Build command string
    # We use cmd /c to properly handle the script path with spaces
    $SERVICE_CMD = "`"$NODE_EXE`" `"$PROXY_SCRIPT`" --port 3001"

    # Check if service already exists
    $EXISTING = sc.exe query $SERVICE_NAME 2>&1
    if ($EXISTING -match "RUNNING|STOPPED") {
        Write-Host "⚠️  Service $SERVICE_NAME already exists" -ForegroundColor Yellow
        Write-Host "   Remove it first: .\uninstall-service.ps1" -ForegroundColor Yellow
        exit 1
    }

    # Create the service
    sc.exe create $SERVICE_NAME binPath= $SERVICE_CMD start= auto DisplayName= "$SERVICE_DISPLAY"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Service created successfully" -ForegroundColor Green

        # Set description
        sc.exe description $SERVICE_NAME "$SERVICE_DESC"

        # Start the service
        Write-Host "🚀 Starting service..." -ForegroundColor Yellow
        Start-Service -Name $SERVICE_NAME

        # Wait a moment for service to start
        Start-Sleep -Seconds 2

        # Check status
        $STATUS = Get-Service -Name $SERVICE_NAME
        if ($STATUS.Status -eq "Running") {
            Write-Host "✅ Service is running!" -ForegroundColor Green
            Write-Host ""
            Write-Host "📡 Proxy available at: http://localhost:3001/v1" -ForegroundColor Cyan
            Write-Host "📝 Chat Completions: http://localhost:3001/v1/chat/completions" -ForegroundColor Cyan
            Write-Host "🛠️ Tools: http://localhost:3001/v1/tools" -ForegroundColor Cyan
            Write-Host "📊 Models: http://localhost:3001/v1/models" -ForegroundColor Cyan
            Write-Host "🔧 Backends: http://localhost:3001/backends" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "📋 Useful commands:" -ForegroundColor Yellow
            Write-Host "   Check status: sc.exe query $SERVICE_NAME" -ForegroundColor Gray
            Write-Host "   Start service: Start-Service $SERVICE_NAME" -ForegroundColor Gray
            Write-Host "   Stop service: Stop-Service $SERVICE_NAME" -ForegroundColor Gray
            Write-Host "   Restart service: Restart-Service $SERVICE_NAME" -ForegroundColor Gray
            Write-Host "   Remove service: .\uninstall-service.ps1" -ForegroundColor Gray
            Write-Host ""
            Write-Host "📋 View logs:" -ForegroundColor Yellow
            Write-Host "   Event Viewer → Windows Logs → Application → $SERVICE_NAME" -ForegroundColor Gray
            Write-Host ""
            Write-Host "🎯 Configure OpenWebUI:" -ForegroundColor Yellow
            Write-Host "   Add OpenAI-compatible connection:" -ForegroundColor Gray
            Write-Host "   - Base URL: http://localhost:3001/v1" -ForegroundColor Gray
            Write-Host "   - Model: openclaw" -ForegroundColor Gray
            Write-Host "   - Enable Native Mode (Agentic Mode)" -ForegroundColor Gray
        } else {
            Write-Host "❌ Failed to start service" -ForegroundColor Red
            Write-Host "   Status: $($STATUS.Status)" -ForegroundColor Yellow
            exit 1
        }
    } else {
        Write-Host "❌ Failed to create service" -ForegroundColor Red
        Write-Host "   Exit code: $LASTEXITCODE" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red

    # Try sc.exe remove as fallback
    Write-Host "🔄 Attempting to clean up..." -ForegroundColor Yellow
    sc.exe delete $SERVICE_NAME 2>&1 | Out-Null

    exit 1
}
