@echo off
REM Install OpenAI Multi-Agent Proxy as Windows Service
REM Agentic Mode (Function Calling) Support
REM Run as Administrator

echo Installing OpenAI Multi-Agent Proxy - Agentic Mode...
echo.

REM Check if port is already in use
netstat -ano | findstr ":3001" >nul 2>&1
if %errorLevel% EQU 0 (
    echo WARNING: Port 3001 is already in use
    echo Trying port 3002...
    powershell.exe -ExecutionPolicy Bypass -File "%~dp0install-service-agentic.ps1" --port 3002
) else (
    powershell.exe -ExecutionPolicy Bypass -File "%~dp0install-service-agentic.ps1"
)

if %errorLevel% EQU 0 (
    echo.
    echo ============================================
    echo   Installation Complete!
    echo ============================================
    echo.
    echo Next steps:
    echo.
    echo 1. Configure OpenWebUI:
    echo    - Go to Settings ^> Providers
    echo    - Add OpenAI-compatible connection
    echo    - Base URL: http://localhost:3001/v1
    echo    - Model: openclaw
    echo.
    echo 2. Enable Agentic Mode (Native Mode):
    echo    - Go to Settings ^> Models
    echo    - Select your model
    echo    - Under Advanced Parameters ^> Function Calling
    echo    - Select "Native"
    echo.
    echo 3. Enable Tools:
    echo    - Under Capabilities ^> Builtin Tools
    echo    - Check all tool categories
    echo.
    echo 4. Start chatting!
    echo    - Ask the agent to use tools
    echo    - Example: "Browse the OpenWebUI docs"
    echo    - Watch for tool calls
    echo.
    echo Service management:
    echo    - Start:   Start-Service OpenClawOpenAIProxy
    echo    - Stop:    Stop-Service OpenClawOpenAIProxy
    echo    - Restart: Restart-Service OpenClawOpenAIProxy
    echo    - Remove:  Run uninstall-service-agentic.bat
    echo.
    echo View logs:
    echo    - Event Viewer ^> Windows Logs ^> Application ^> OpenClawOpenAIProxy
    echo.
    echo ============================================
) else (
    echo.
    echo ERROR: Installation failed
    echo Run as Administrator and check error messages above
)

pause
