#!/usr/bin/env node

/**
 * OpenAI-Compatible Streaming Proxy with OpenClaw Gateway WebSocket Support
 *
 * Real SSE (Server-Sent Events) streaming via OpenClaw Gateway.
 * Agentic mode (function calling) support.
 * Multi-backend (OpenClaw + Goose) support.
 */

const express = require('express');
const bodyParser = require('body-parser');
const WebSocket = require('ws');
const { spawn } = require('child_process');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

const argv = yargs(hideBin(process.argv))
  .option('port', {
    alias: 'p',
    description: 'HTTP server port',
    type: 'number',
    default: 3001
  })
  .option('gateway-url', {
    alias: 'g',
    description: 'OpenClaw Gateway WebSocket URL',
    type: 'string',
    default: 'ws://localhost:18789'
  })
  .option('verbose', {
    alias: 'v',
    description: 'Enable verbose logging',
    type: 'boolean',
    default: false
  })
  .option('backend', {
    alias: 'b',
    description: 'Backend for non-streaming (openclaw|goose)',
    type: 'string',
    default: 'openclaw'
  })
  .option('mode', {
    alias: 'm',
    description: 'Execution mode (cli|gateway|hybrid)',
    type: 'string',
    default: 'cli'
  })
  .help()
  .alias('help', 'h')
  .argv;

const PORT = argv.port;
const GATEWAY_URL = argv.gatewayUrl;
const VERBOSE = argv.verbose;
const NON_STREAMING_BACKEND = argv.backend;
const MODE = argv.mode;

const app = express();

// Parse JSON bodies
app.use(bodyParser.json());

// Store for active Gateway connections
const gatewayConnections = new Map();
// Store for active request handlers
const requestHandlers = new Map();

// Log helper
function log(...args) {
  if (VERBOSE) {
    console.log(`[${new Date().toISOString()}]`, ...args);
  }
}

// Backend configurations
const BACKENDS = {
  openclaw: {
    name: 'OpenClaw',
    tools: [
      { id: 'browser', name: 'browser', type: 'function', description: 'Browse websites and interact with web pages' },
      { id: 'canvas', name: 'canvas', type: 'function', description: 'Visual workspace for collaboration' },
      { id: 'nodes', name: 'nodes', type: 'function', description: 'Device and system control' },
      { id: 'files', name: 'files', type: 'function', description: 'File system operations' }
    ],
    supportsGateway: true,
    supportsWebSocket: true
  },
  goose: {
    name: 'Goose CLI',
    tools: [
      { id: 'memory', name: 'memory', type: 'function', description: 'Personalization memory' },
      { id: 'filesystem', name: 'filesystem', type: 'function', description: 'File system access' },
      { id: 'chatrecall', name: 'chatrecall', type: 'function', description: 'Search past conversations' }
    ],
    supportsGateway: false,
    supportsWebSocket: false
  }
};

// Convert OpenAI messages to OpenClaw format
function convertOpenAIMessages(messages) {
  if (!messages || messages.length === 0) {
    return '';
  }

  const systemMsgs = messages.filter(m => m.role === 'system');
  const systemPrompt = systemMsgs.map(m => m.content).join('\n\n');

  const conversation = messages
    .filter(m => m.role !== 'system')
    .map(m => {
      const role = m.role === 'user' ? 'User' : 'Assistant';
      return `${role}: ${m.content}`;
    })
    .join('\n\n');

  if (systemPrompt) {
    return `${systemPrompt}\n\n${conversation}`;
  }
  return conversation;
}

// Connect to OpenClaw Gateway
let gatewayWs = null;
let reconnectTimer = null;

function connectToGateway() {
  if (MODE === 'cli') {
    log('CLI mode - skipping gateway connection');
    return;
  }
  
  log(`Connecting to OpenClaw Gateway at ${GATEWAY_URL}...`);

  gatewayWs = new WebSocket(GATEWAY_URL);

  gatewayWs.on('open', () => {
    log('Connected to OpenClaw Gateway');
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
  });

  gatewayWs.on('message', (data) => {
    try {
      const message = JSON.parse(data.toString());
      log(`Gateway message: ${message.kind}`);

      if (message.kind === 'agentChunk') {
        const requestId = message.requestId;
        if (requestHandlers.has(requestId)) {
          const handler = requestHandlers.get(requestId);
          handler(message);
        }
      } else if (message.kind === 'agentError') {
        const requestId = message.requestId;
        if (requestHandlers.has(requestId)) {
          const handler = requestHandlers.get(requestId);
          handler({ error: message.error });
        }
      } else if (message.kind === 'agentTurn') {
        const requestId = message.requestId;
        if (requestHandlers.has(requestId)) {
          const handler = requestHandlers.get(requestId);
          handler({ done: true, content: message.text });
        }
      }
    } catch (e) {
      log('Error parsing gateway message:', e.message);
    }
  });

  gatewayWs.on('close', () => {
    log('Disconnected from OpenClaw Gateway');
    gatewayWs = null;

    if (!reconnectTimer) {
      reconnectTimer = setTimeout(connectToGateway, 5000);
    }
  });

  gatewayWs.on('error', (error) => {
    log('Gateway WebSocket error:', error.message);
  });
}

// Generate request ID
function generateRequestId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
}

// Send request to Gateway
function sendToGateway(requestId, message, tools) {
  if (!gatewayWs || gatewayWs.readyState !== WebSocket.OPEN) {
    return false;
  }

  const gatewayMessage = {
    kind: 'agentTurn',
    requestId,
    message,
    ...tools
  };

  log(`Sending to Gateway: ${JSON.stringify(gatewayMessage)}`);
  gatewayWs.send(JSON.stringify(gatewayMessage));

  return true;
}

// Non-streaming backend: Execute OpenClaw CLI
function executeOpenClawCLI(message, agentParams = {}) {
  return new Promise((resolve, reject) => {
    const args = ['agent', '--local', '--json', '--message', message];

    const sessionKey = agentParams.sessionKey || 'openai-proxy-default';
    args.push('--session-id', sessionKey);

    log(`Executing: openclaw ${args.join(' ')}`);

    const openclawPath = process.platform === 'win32'
      ? 'C:\\Users\\aaron\\AppData\\Roaming\\npm\\node_modules\\openclaw\\dist\\index.js'
      : 'openclaw';

    const execPath = process.platform === 'win32' ? process.execPath : 'openclaw';

    const proc = spawn(execPath, [openclawPath, ...args], {
      env: process.env
    });

    let stdout = '';
    let stderr = '';

    proc.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    proc.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    proc.on('close', (code) => {
      log(`OpenClaw CLI exited with code ${code}`);

      if (code === 0) {
        try {
          const jsonOutput = JSON.parse(stdout);
          let content = '';

          if (jsonOutput.payloads && Array.isArray(jsonOutput.payloads) && jsonOutput.payloads.length > 0) {
            content = jsonOutput.payloads[0].text || '';
          } else if (jsonOutput.text) {
            content = jsonOutput.text;
          } else if (jsonOutput.message) {
            content = jsonOutput.message;
          } else if (jsonOutput.content) {
            content = jsonOutput.content;
          }

          if (content) {
            content = content.replace(/\x1b\[[0-9;]*m/g, '').trim();
          }

          resolve({ content });
        } catch (parseError) {
          const cleanOutput = stdout
            .replace(/\x1b\[[0-9;]*m/g, '')
            .replace(/\r\n/g, '\n')
            .trim();

          resolve({ content: cleanOutput });
        }
      } else {
        reject(new Error(`OpenClaw CLI exited with code ${code}: ${stderr}`));
      }
    });

    proc.on('error', (error) => {
      reject(new Error(`Failed to execute OpenClaw: ${error.message}`));
    });
  });
}

// SSE helper functions
function sendSSEEvent(res, data, event = 'message') {
  res.write(`event: ${event}\n`);
  res.write(`data: ${JSON.stringify(data)}\n\n`);
}

function sendSSEDone(res) {
  res.write(`data: [DONE]\n\n`);
}

// GET /v1/tools - List available tools
app.get('/v1/tools', (req, res) => {
  const backend = NON_STREAMING_BACKEND;
  const backendConfig = BACKENDS[backend];

  res.json({
    object: 'list',
    data: backendConfig.tools.map(tool => ({
      id: tool.id,
      type: tool.type,
      function: {
        name: tool.name,
        description: tool.description
      },
      provider: 'openai-proxy',
      backend: backendConfig.name
    }))
  });
});

// GET /v1/models - List available models
app.get('/v1/models', (req, res) => {
  const now = Date.now();

  const backends = Object.keys(BACKENDS).map(name => ({
    id: name,
    object: 'model',
    created: Math.floor(now / 1000),
    owned_by: 'openai-proxy',
    provider: BACKENDS[name].name,
    description: `${BACKENDS[name].name} AI agent with agentic mode support.`,
    pricing: { input: 0, output: 0 },
    context: {
      max_tokens: 200000,
      max_context_length: 200000
    },
    capabilities: BACKENDS[name].tools.map(t => t.name),
    permission: ['public'],
    spec: {
      backend: name,
      type: 'agent',
      version: '1.1',
      supports_function_calling: true,
      supports_tools: true,
      supports_agentic_mode: true,
      supports_streaming: MODE !== 'cli'
    }
  }));

  res.json({
    object: 'list',
    data: backends
  });
});

// POST /v1/chat/completions - Main endpoint
app.post('/v1/chat/completions', async (req, res) => {
  try {
    const { model, messages, temperature, stream, tools, tool_choice, ...rest } = req.body;

    log(`Chat completions: model=${model}, stream=${stream}, tools=${tools ? 'yes' : 'no'}`);

    // Handle streaming requests
    if (stream && MODE !== 'cli') {
      res.setHeader('Content-Type', 'text/event-stream');
      res.setHeader('Cache-Control', 'no-cache');
      res.setHeader('Connection', 'keep-alive');
      res.setHeader('X-Accel-Buffering', 'no');

      const requestId = generateRequestId();
      const message = convertOpenAIMessages(messages);

      // Register handler for this request
      requestHandlers.set(requestId, (msg) => {
        if (msg.done) {
          res.json({
            id: `chatcmpl-${Date.now()}`,
            object: 'chat.completion',
            created: Math.floor(Date.now() / 1000),
            model: model || 'openclaw',
            choices: [{
              index: 0,
              message: {
                role: 'assistant',
                content: msg.content
              },
              finish_reason: 'stop'
            }]
          });
          sendSSEDone(res);
          requestHandlers.delete(requestId);
        } else if (msg.error) {
          sendSSEEvent(res, {
            error: {
              message: msg.error,
              type: 'api_error',
              code: 'internal_error'
            }
          });
          sendSSEDone(res);
          requestHandlers.delete(requestId);
        } else if (msg.kind === 'agentChunk') {
          sendSSEEvent(res, {
            id: `chatcmpl-${Date.now()}`,
            object: 'chat.completion.chunk',
            created: Math.floor(Date.now() / 1000),
            model: model || 'openclaw',
            choices: [{
              index: 0,
              delta: {
                content: msg.chunk
              }
            }]
          });
        }
      });

      // Send to Gateway
      if (sendToGateway(requestId, message, tools)) {
        // Keep connection alive
        const keepAlive = setInterval(() => {
          if (res.writable) {
            res.write(': keep-alive\n\n');
          } else {
            clearInterval(keepAlive);
          }
        }, 15000);
      } else {
        sendSSEEvent(res, {
          error: {
            message: 'Not connected to OpenClaw Gateway',
            type: 'api_error',
            code: 'connection_error'
          }
        });
        sendSSEDone(res);
        requestHandlers.delete(requestId);
      }
      return;
    }

    // Non-streaming: Execute via CLI
    if (stream) {
      log('Streaming requested but CLI mode - falling back to non-streaming');
    }

    const message = convertOpenAIMessages(messages);
    const output = await executeOpenClawCLI(message, req.body);
    const content = output.content;

    const response = {
      id: `chatcmpl-${Date.now()}`,
      object: 'chat.completion',
      created: Math.floor(Date.now() / 1000),
      model: model || 'openclaw',
      choices: [{
        index: 0,
        message: {
          role: 'assistant',
          content: content
        },
        finish_reason: 'stop'
      }],
      usage: {
        prompt_tokens: JSON.stringify(req.body).length,
        completion_tokens: content.length,
        total_tokens: JSON.stringify(req.body).length + content.length
      }
    };

    res.json(response);

  } catch (error) {
    log('Error handling chat completions:', error);

    if (stream && res.headersSent) {
      res.write(`data: ${JSON.stringify({ error: { message: error.message, type: 'api_error', code: 'internal_error' }})}\n\n`);
      res.write('data: [DONE]\n\n');
      res.end();
    } else {
      const errorResponse = {
        error: {
          message: error.message,
          type: 'api_error',
          code: 'internal_error'
        }
      };
      res.status(500).json(errorResponse);
    }
  }
});

// GET /backends - Backend status endpoint
app.get('/backends', (req, res) => {
  res.json({
    default: NON_STREAMING_BACKEND,
    streaming_mode: MODE,
    gateway_url: GATEWAY_URL,
    gateway_connected: gatewayWs ? gatewayWs.readyState === WebSocket.OPEN : false,
    available_backends: Object.keys(BACKENDS).map(name => ({
      name,
      displayName: BACKENDS[name].name,
      supports_function_calling: true,
      supports_websocket: BACKENDS[name].supportsWebSocket
    }))
  });
});

// GET /health - Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    mode: MODE,
    gateway_url: GATEWAY_URL,
    gateway_connected: gatewayWs ? gatewayWs.readyState === WebSocket.OPEN : false,
    supports_streaming: MODE !== 'cli',
    supports_function_calling: true,
    backends: Object.keys(BACKENDS)
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`\n🦥 OpenAI Proxy (Agentic Mode)`);
  console.log(`📡 HTTP Server: http://localhost:${PORT}`);
  console.log(`📝 Chat Completions: http://localhost:${PORT}/v1/chat/completions`);
  console.log(`🛠️ Tools: http://localhost:${PORT}/v1/tools`);
  console.log(`📊 Models: http://localhost:${PORT}/v1/models`);
  console.log(`🔧 Backends: http://localhost:${PORT}/backends`);
  console.log(`\nConfiguration:`);
  console.log(`  Mode: ${MODE}`);
  console.log(`  Gateway URL: ${GATEWAY_URL}`);
  console.log(`  Backend: ${NON_STREAMING_BACKEND}`);
  console.log(`\nUsage:`);
  console.log(`  Base URL: http://localhost:${PORT}/v1`);
  console.log(`  Model: openclaw`);
});

// Initialize Gateway connection (if not CLI mode)
if (MODE !== 'cli') {
  connectToGateway();
}

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\nShutting down...');

  if (gatewayWs) {
    gatewayWs.close();
  }

  requestHandlers.clear();
  process.exit(0);
});
