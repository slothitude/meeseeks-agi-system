---
name: openai-proxy
description: Multi-agent OpenAI-compatible HTTP API proxy supporting OpenClaw and Goose CLI backends. Routes requests between backends based on configuration, enables OpenWebUI, Cursor, or other OpenAI-compatible tools to interface with multiple AI agent systems. Use when integrating OpenWebUI, Cursor, or similar tools with OpenClaw or when you need a REST API interface to AI agents.
---

# OpenAI Proxy for OpenClaw

## Overview

This skill provides an OpenAI-compatible HTTP API proxy for OpenClaw, enabling integration with OpenWebUI, IDEs (Cursor, Windsurf), and other tools that expect the standard OpenAI Chat Completions API format.

## Quick Start

### Start the Proxy Server

Run the proxy server:

```bash
cd skills/openai-proxy/scripts
node openai-proxy.js --port 3001
```

The server will:
- Listen on `http://localhost:3001`
- Auto-connect to OpenClaw Gateway at `ws://localhost:18789`
- Expose `/v1/chat/completions` endpoint

### Configure Client

Set your OpenAI-compatible client (OpenWebUI, Cursor, etc.) to:

- **Base URL:** `http://localhost:3001/v1`
- **API Key:** Any value (required by some clients, not validated)
- **Model:** `openclaw` (or any model name you prefer)

## Core Capabilities

### 1. Chat Completions (`/v1/chat/completions`)

Accepts OpenAI-format requests:

```json
{
  "model": "openclaw",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.7,
  "stream": true
}
```

Returns OpenAI-format responses (streaming and non-streaming).

### 2. Message Translation

Translates OpenAI message roles to OpenClaw format:
- `system` → OpenClaw system prompt
- `user` → User messages
- `assistant` → Assistant messages (for conversation history)

### 3. Streaming Support

Implements OpenAI Server-Sent Events (SSE) format for streaming responses.

### 4. Model Fallback

The `model` field is optional and primarily for client compatibility. All requests are processed by the configured OpenClaw agent.

## Advanced Configuration

### Custom Gateway URL

```bash
node openai-proxy.js --gateway-url ws://192.168.1.100:18789 --port 3001
```

### Session-Specific Routing

The proxy supports session routing via OpenAI's `user` parameter:

```json
{
  "model": "openclaw",
  "messages": [...],
  "user": "session-123"
}
```

This routes the request to the specified OpenClaw session. If omitted, uses the default/main session.

### Agent Selection

Route to different OpenClaw agents via custom headers:

```
X-OpenClaw-Agent: sub-agent-name
```

## Troubleshooting

### Gateway Connection Failed

Ensure OpenClaw Gateway is running:

```bash
openclaw gateway status
```

### Port Already in Use

Choose a different port:

```bash
node openai-proxy.js --port 3002
```

### Session Not Found

Verify the session exists in OpenClaw:

```bash
openclaw sessions list
```

## Resources

### scripts/openai-proxy.js

Express.js server implementing OpenAI Chat Completions API. Handles WebSocket connection to OpenClaw Gateway and protocol translation.

**Key features:**
- OpenAI request/response format
- SSE streaming
- Session routing
- Error handling
