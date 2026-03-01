@echo off
REM Install OpenAI Proxy as Windows Service
REM Run as Administrator

echo Installing OpenAI Proxy as Windows Service...
echo.

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% NEQ 0 (
    echo ERROR: This script must be run as Administrator.
    echo Right-click and select "Run as Administrator"
    pause
    exit /b 1
)

REM Run PowerShell script
powershell.exe -ExecutionPolicy Bypass -File "%~dp0install-service.ps1"

pause
