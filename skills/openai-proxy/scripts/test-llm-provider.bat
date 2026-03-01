@echo off
REM Test OpenAI Multi-Agent Proxy LLM Provider Mode
REM Verifies that agents appear as LLM providers in OpenWebUI

echo Testing OpenAI Multi-Agent Proxy - LLM Provider Mode...
echo.

REM Check if proxy is running
curl -s http://localhost:3001/health >nul 2>&1
if %errorLevel% NEQ 0 (
    echo [ERROR] Proxy is not running!
    echo Start the proxy first: start-multi.bat
    pause
    exit /b 1
)

echo [OK] Proxy is running
echo.

REM Test /v1/models endpoint (should return provider metadata)
echo.
echo Testing /v1/models endpoint...
echo.
curl -s http://localhost:3001/v1/models
echo.

REM Check response
echo.
echo Expected: Provider metadata for OpenClaw and Goose
echo.

REM Test /v1/chat/completions with OpenClaw
echo.
echo Testing OpenClaw backend...
curl -s -X POST http://localhost:3001/v1/chat/completions ^
  -H "Content-Type: application/json" ^
  -d "{\"model\": \"openclaw\", \"messages\": [{\"role\": \"user\", \"content\": \"Say hello\"}], \"stream\": false}"
echo.

echo.
echo Test complete! Check responses above.
echo.
pause
