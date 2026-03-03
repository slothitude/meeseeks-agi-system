# Meeseeks Box CLI (Windows PowerShell)
# Control the containerized consciousness stack

param(
    [Parameter(Position=0)]
    [string]$Command,
    
    [Parameter(Position=1, ValueFromRemainingArguments=$true)]
    [string[]]$Arguments
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ComposeFile = Join-Path $ScriptDir "docker-compose.yml"

function Show-Help {
    Write-Host "🥒 Meeseeks Box CLI"
    Write-Host ""
    Write-Host "Usage: .\meeseeks.ps1 {command}"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "   start           - Build and start the Meeseeks Box"
    Write-Host "   stop            - Stop the Meeseeks Box"
    Write-Host "   restart         - Restart the Meeseeks Box"
    Write-Host "   status          - Show full system status"
    Write-Host "   health          - Health check"
    Write-Host "   spawn TASK      - Spawn a Meeseeks for TASK"
    Write-Host "   dream           - Trigger a dream cycle"
    Write-Host "   soul TEXT       - Check if TEXT is Soul-approved"
    Write-Host "   ancestors       - List recent ancestors"
    Write-Host "   metrics         - Prometheus metrics"
    Write-Host "   logs            - View container logs"
    Write-Host "   build           - Rebuild the container"
    Write-Host "   ps              - Show container status"
}

function Invoke-Api {
    param([string]$Endpoint, [string]$Method = "GET", [object]$Body = $null)
    
    try {
        if ($Body) {
            $jsonBody = $Body | ConvertTo-Json -Depth 10
            $response = Invoke-RestMethod -Uri "http://localhost:8080$Endpoint" -Method $Method -Body $jsonBody -ContentType "application/json" -ErrorAction Stop
        } else {
            $response = Invoke-RestMethod -Uri "http://localhost:8080$Endpoint" -Method $Method -ErrorAction Stop
        }
        return $response | ConvertTo-Json -Depth 10
    } catch {
        Write-Host "❌ Meeseeks Box is not running or not reachable" -ForegroundColor Red
        return $null
    }
}

switch ($Command) {
    "start" {
        Write-Host "🥒 Starting Meeseeks Box..."
        
        # Check Docker
        try {
            docker info | Out-Null
        } catch {
            Write-Host "❌ Docker is not running. Please start Docker first." -ForegroundColor Red
            exit 1
        }
        
        # Start containers
        Write-Host "📦 Starting containers..."
        Push-Location $ScriptDir
        docker-compose up -d
        Pop-Location
        
        # Wait for API
        Write-Host "⏳ Waiting for API to be ready..."
        $ready = $false
        for ($i = 1; $i -le 30; $i++) {
            try {
                Invoke-RestMethod -Uri "http://localhost:8080/health" -ErrorAction Stop | Out-Null
                $ready = $true
                break
            } catch {
                Start-Sleep -Seconds 1
            }
        }
        
        if ($ready) {
            Write-Host ""
            Write-Host "✅ Meeseeks Box is running!" -ForegroundColor Green
            Write-Host ""
            Write-Host "   API:      http://localhost:8080"
            Write-Host "   Metrics:  http://localhost:9090"
            Write-Host "   Ollama:   http://localhost:11434"
        } else {
            Write-Host "⚠️ Container started but API not responding" -ForegroundColor Yellow
        }
    }
    
    "stop" {
        Write-Host "🛑 Stopping Meeseeks Box..."
        Push-Location $ScriptDir
        docker-compose down
        Pop-Location
        Write-Host "✅ Meeseeks Box stopped" -ForegroundColor Green
    }
    
    "restart" {
        & $MyInvocation.MyCommand.Path stop
        Start-Sleep -Seconds 2
        & $MyInvocation.MyCommand.Path start
    }
    
    "status" {
        $result = Invoke-Api "/status"
        if ($result) { Write-Host $result }
    }
    
    "health" {
        $result = Invoke-Api "/health"
        if ($result) { Write-Host $result }
    }
    
    "spawn" {
        if (-not $Arguments) {
            Write-Host "Usage: .\meeseeks.ps1 spawn `"task description`""
            exit 1
        }
        $task = $Arguments -join " "
        $result = Invoke-Api "/spawn" -Method "POST" -Body @{task = $task}
        if ($result) { Write-Host $result }
    }
    
    "dream" {
        $result = Invoke-Api "/dream" -Method "POST"
        if ($result) { Write-Host $result }
    }
    
    "soul" {
        if (-not $Arguments) {
            Write-Host "Usage: .\meeseeks.ps1 soul `"text to check`""
            exit 1
        }
        $text = $Arguments -join " "
        $result = Invoke-Api "/soul/check" -Method "POST" -Body @{text = $text}
        if ($result) { Write-Host $result }
    }
    
    "ancestors" {
        $result = Invoke-Api "/ancestors"
        if ($result) { Write-Host $result }
    }
    
    "metrics" {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8080/metrics" -ErrorAction Stop
            Write-Host $response.Content
        } catch {
            Write-Host "❌ Meeseeks Box is not running or not reachable" -ForegroundColor Red
        }
    }
    
    "logs" {
        Push-Location $ScriptDir
        docker-compose logs -f
        Pop-Location
    }
    
    "build" {
        Write-Host "🔨 Building Meeseeks Box..."
        Push-Location $ScriptDir
        docker-compose build --no-cache
        Pop-Location
        Write-Host "✅ Build complete" -ForegroundColor Green
    }
    
    "ps" {
        Push-Location $ScriptDir
        docker-compose ps
        Pop-Location
    }
    
    default {
        Show-Help
    }
}
