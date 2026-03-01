@echo off
REM Start OpenAI Multi-Agent Proxy with Agentic Mode (Function Calling)
REM Supports OpenWebUI Native Mode for tool calling

echo.
echo ===========================================
echo   OpenAI Multi-Agent Proxy
echo        Agentic Mode
echo ===========================================
echo.

REM Check if port is already in use
netstat -ano | findstr ":3001" >nul 2>&1
if %errorLevel% EQU 0 (
    echo WARNING: Port 3001 is already in use
    echo Trying port 3002...
    node "C:\Users\aaron\.openclaw\workspace\skills\openai-proxy\scripts\openai-proxy-agentic.js" --port 3002
) else (
    node "C:\Users\aaron\.openclaw\workspace\skills\openai-proxy\scripts\openai-proxy-agentic.js"
)

echo.
echo Proxy started!
echo.
echo Tools Endpoint:     http://localhost:3001/v1/tools
echo Models Endpoint:     http://localhost:3001/v1/models
echo Chat Completions:    http://localhost:3001/v1/chat/completions
echo.
echo OpenWebUI Configuration:
echo   Base URL:          http://localhost:3001/v1
echo   Model (OpenClaw):   openclaw
echo   Model (Goose):      goose
echo.
echo Agentic Mode Enabled:
echo   - OpenClaw tools (browser, canvas, nodes, files)
echo   - Goose tools (memory, filesystem, chatrecall)
echo   - Function calling support
echo.
pause
