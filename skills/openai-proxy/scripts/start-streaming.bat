@echo off
REM Start OpenAI Multi-Agent Proxy with Streaming Support
REM Real SSE streaming via OpenClaw Gateway WebSocket

echo.
echo ============================================
echo   OpenAI Multi-Agent Proxy
        Real-Time Streaming
echo ============================================
echo.

echo Starting proxy with OpenClaw Gateway streaming...
echo.

cd /d "C:\Users\aaron\.openclaw\workspace\skills\openai-proxy\scripts"

REM Start with Gateway streaming mode
node openai-proxy-agentic.js --mode gateway --verbose

echo.
echo Proxy started!
echo.
echo ============================================
echo.
echo 🚀 Real-Time Streaming Features:
echo   ✅ SSE (Server-Sent Events) format
echo   ✅ OpenClaw Gateway WebSocket
echo   ✅ Agentic Mode (Function Calling)
echo   ✅ Tool streaming (as it happens)
echo.
echo 📡 Available at: http://localhost:3001/v1
echo 📝 Chat: http://localhost:3001/v1/chat/completions
echo 🛠️ Tools: http://localhost:3001/v1/tools
echo 📊 Models: http://localhost:3001/v1/models
echo.
echo Configure OpenWebUI:
echo   - Base URL: http://localhost:3001/v1
echo   - Model: openclaw
echo   - Enable: Agentic Mode (Native Function Calling)
echo   - Enable: Tools
echo.
echo For streaming, use: "stream": true in requests
echo The proxy will now stream responses in real-time!
echo.
echo ============================================
echo.
pause
