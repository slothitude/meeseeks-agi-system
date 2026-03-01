@echo off
REM Start OpenAI Multi-Agent Proxy with Streaming Support
REM Real SSE streaming via OpenClaw Gateway WebSocket

echo Starting OpenAI Multi-Agent Proxy...
echo.

cd /d "C:\Users\aaron\.openclaw\workspace\skills\openai-proxy\scripts"

REM Check if the file exists
if exist "openai-proxy-agentic-stream.js" (
    echo Found: openai-proxy-agentic-stream.js
    echo.
    node openai-proxy-agentic-stream.js --mode gateway --port 3001
) else (
    echo ERROR: File not found: openai-proxy-agentic-stream.js
    echo.
    echo Available files:
    dir /b *.js
    echo.
    echo Please check the correct filename.
    pause
    exit /b 1
)

echo.
echo Proxy started!
echo.
echo ============================================
echo   OpenAI Multi-Agent Proxy
        Real-Time Streaming
        Agentic Mode
        Gateway WebSocket
echo ============================================
echo.
echo Features:
echo   - Real-time SSE streaming
echo   - Agentic mode (function calling)
echo   - OpenClaw Gateway integration
echo.
echo Endpoints:
echo   - Chat Completions: http://localhost:3001/v1/chat/completions
echo   - Tools: http://localhost:3001/v1/tools
echo   - Models: http://localhost:3001/v1/models
echo.
echo Status:
echo   - Gateway: Connecting to ws://localhost:18789
echo   - Streaming: Enabled via SSE
echo.
echo Ready to use with OpenWebUI!
echo ============================================
echo.
pause
