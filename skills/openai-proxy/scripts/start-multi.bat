@echo off
REM Start OpenAI Multi-Agent Proxy
REM Automatically routes between OpenClaw and Goose

echo Starting OpenAI Multi-Agent Proxy...
echo.

REM Check if port is already in use
netstat -ano | findstr ":3001" >nul 2>&1
if %errorLevel% EQU 0 (
    echo WARNING: Port 3001 is already in use
    echo Trying port 3002...
    node "C:\Users\aaron\.openclaw\workspace\skills\openai-proxy\scripts\openai-proxy-multi.js" --port 3002
) else (
    node "C:\Users\aaron\.openclaw\workspace\skills\openai-proxy\scripts\openai-proxy-multi.js" --port 3001
)

pause
