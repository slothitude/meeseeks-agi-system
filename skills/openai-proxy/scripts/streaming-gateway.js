#!/usr/bin/env node

/**
 * OpenAI-Compatible Streaming Proxy with OpenClaw Gateway WebSocket Support
 *
 * Real SSE (Server-Sent Events) streaming via OpenClaw Gateway.
 * Agentic mode (function calling) support.
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
    description: 'Execution mode (gateway|hybrid)',
    type: 'string',
    default: 'hybrid'
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

// Backend configurations with tool definitions
const BACKENDS = {
  openclaw: {
    name: 'OpenClaw',
    tools: [
      {
        id: 'browser',
        name: 'browser',
        type: 'function',
        description: 'Browse websites, take screenshots, and interact with web pages',
        parameters: {
          type: 'object',
          properties: {
            url: { type: 'string', description: 'URL to browse' },
            action: {
              type: 'string',
              enum: ['screenshot', 'extract_text', 'search'],
              description: 'Action to perform'
            },
            selector: { type: 'string', description: 'CSS selector for click/scroll (optional)' }
          },
          required: ['url']
        }
      },
      {
        id: 'canvas',
        name: 'canvas',
        type: 'function',
        description: 'Visual workspace for collaboration and diagramming',
        parameters: {
          type: 'object',
          properties: {
            action: {
              type: 'string',
              enum: ['create', 'update', 'clear', 'screenshot'],
              description: 'Action to perform'
            },
            data: { type: 'object', description: 'Canvas data (optional)' }
          },
          required: ['action']
        }
      },
      {
        id: 'nodes',
        name: 'nodes',
        type: 'function',
        description: 'Device and system control (camera, screen recording, location, notifications)',
        parameters: {
          type: 'object',
          properties: {
            action: {
              type: 'string',
              enum: ['camera_snap', 'screen_record', 'location_get', 'system_notify'],
              description: 'Action to perform'
            },
            params: { type: 'object', description: 'Additional parameters (optional)' }
          },
          required: ['action']
        }
      },
      {
        id: 'files',
        name: 'files',
        type: 'function',
        description: 'File system operations (read, write, list, search)',
        parameters: {
          type: 'object',
          properties: {
            action: {
              type: 'string',
              enum: ['read', 'write', 'list', 'search', 'delete'],
              description: 'Action to perform'
            },
            path: { type: 'string', description: 'File path (for read/write)' },
            pattern: { type: 'string', description: 'Search pattern (for search)' }
          },
          required: ['action']
        }
      }
    ]
  },
  goose: {
    name: 'Goose CLI',
    tools: [
      {
        id: 'memory',
        name: 'memory',
        type: 'function',
        description: 'Personalization memory for preferences and facts',
        parameters: {
          type: 'object',
          properties: {
            action: {
              type: 'string',
              enum: ['search', 'add', 'get'],
              description: 'Action to perform'
            },
            key: { type: 'string', description: 'Memory key (for get)' },
            value: { type: 'string', description: 'Memory value (for add)' }
          },
          required: ['action']
        }
      },
      {
        id: 'filesystem',
        name: 'filesystem',
        type: 'function',
        description: 'File system access via Goose extensions',
        parameters: {
          type: 'object',
          properties: {
            action: {
              type: 'string',
              enum: ['read', 'write', 'list', 'search'],
              description: 'Action to perform'
            },
            path: { type: 'string', description: 'File path' }
          },
          required: ['action']
        }
      },
      {
        id: 'chatrecall',
        name: 'chatrecall',
        type: 'function',
        description: 'Search and retrieve from past conversations',
        parameters: {
          type: 'object',
          properties: {
            query: { type: 'string', description: 'Search query' },
            count: { type: 'number', description: 'Number of results (default: 5)' }
          },
          required: ['query']
        }
      }
    ]
  }
};

// Connect to OpenClaw Gateway
let gatewayWs = null;
let reconnectTimer = null;

function connectToGateway() {
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
    const message = JSON.parse(data.toString());
    log(`Gateway message: ${message.kind}`);

    if (message.kind === 'agentChunk') {
      // Stream the chunk to the appropriate request handler
      const requestId = message.requestId;
      if (requestHandlers.has(requestId)) {
        const handler = requestHandlers.get(requestId);
        handler(message);
      }
    } else if (message.kind === 'agentError') {
      // Handle error
      const requestId = message.requestId;
      if (requestHandlers.has(requestId)) {
        const handler = requestHandlers.get(requestId);
        handler({ error: message.error });
      }
    } else if (message.kind === 'agentTurn') {
      // Handle complete response
      const requestId = message.requestId;
      if (requestHandlers.has(requestId)) {
        const handler = requestHandlers.get(requestId);
        handler({ done: true, content: message.text });
      }
    } else if (message.kind === 'agentMessage') {
      // Handle system messages
      log(`Agent message: ${message.text}`);
    }
  });

  gatewayWs.on('close', () => {
    log('Disconnected from OpenClaw Gateway');
    gatewayWs = null;

    // Auto-reconnect after 5 seconds
    if (!reconnectTimer) {
      reconnectTimer = setTimeout(connectToGateway, 5000);
    }
  });

  gatewayWs.on('error', (error) => {
    log('Gateway WebSocket error:', error);
  });
}

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

// Non-streaming backend implementations
function executeOpenClawCLI(message, agentParams = {}) {
  return new Promise((resolve, reject) => {
    const args = ['agent', '--local', '--json', '--message', message];

    const sessionKey = agentParams.sessionKey || 'openai-proxy-default';
    args.push('--session-id', sessionKey);

    if (agentParams.thinking) {
      args.push('--thinking', agentParams.thinking);
    }

    log(`Executing OpenClaw CLI: openclaw ${args.join(' ')}`);

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

// Determine backend for non-streaming requests
function determineBackendForRequest(request) {
  if (MODE === 'gateway') {
    return 'gateway';
  }

  const model = request.model || '';
  if (model === 'goose' || model === 'goose-fast') {
    return 'goose-cli';
  }

  return NON_STREAMING_BACKEND;
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
  const backend = 'gateway'; // Always show Gateway tools for Agentic mode
  const backendConfig = BACKENDS[backend];

  res.json({
    object: 'list',
    data: backendConfig.tools.map(tool => ({
      id: tool.id,
      type: tool.type,
      function: {
        name: tool.name,
        description: tool.description,
        parameters: tool.parameters
      },
      provider: 'openai-proxy',
      backend: backendConfig.name
    }))
  });
});

// GET /v1/models - List available models with provider metadata
app.get('/v1/models', (req, res) => {
  const now = Date.now();

  const backends = Object.keys(BACKENDS).map(name => ({
    id: name,
    object: 'model',
    created: Math.floor(now / 1000),
    owned_by: 'openai-proxy',
    provider: BACKENDS[name].name,
    description: `${BACKENDS[name].name} AI agent with agentic mode (function calling) support via OpenClaw Gateway WebSocket.`,
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
      supports_streaming: true
    }
  }));

  res.json({
    object: 'list',
    data: backends
  });
});

// POST /v1/chat/completions - Main endpoint with streaming support
app.post('/v1/chat/completions', async (req, res) => {
  const { model, messages, temperature, stream, tools, tool_choice, ...rest } = req.body;

  log(`Chat completions: model=${model}, stream=${stream}, tools=${tools ? 'yes' : 'no'}, tool_choice=${tool_choice}`);

  // Set SSE headers for streaming
  if (stream) {
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.setHeader('X-Accel-Buffering', 'no');

    // Create a request ID
    const requestId = generateRequestId();

    // Convert OpenAI messages to backend format
    const message = convertOpenAIMessages(messages);

    // Handle streaming requests via Gateway (Agentic Mode)
    if (MODE === 'gateway' || (MODE === 'hybrid' && stream)) {
      // Gateway streaming
      const backendConfig = BACKENDS[model] || BACKENDS['gateway'];
      const availableTools = backendConfig.tools || [];

      // Build system message with tool context
      const toolsMessage = `You have access to these tools:\n${JSON.stringify(availableTools, null, 2)}\n\nUse them when appropriate. The tools are:\n${availableTools.map(t => `- ${t.name}: ${t.description}`).join('\n')}`;

      // Combine with system prompt if provided
      const systemMsgs = messages.filter(m => m.role === 'system');
      const fullSystemMessage = systemMsgs.map(m => m.content).concat(toolsMessage).join('\n\n');

      // Build request with tools support
      const request = {
        kind: 'agentTurn',
        requestId,
        message: fullSystemMessage + message,
        ...tools
      };

      log(`Gateway streaming request: ${JSON.stringify(request)}`);

      // Register handler for this request
      requestHandlers.set(requestId, (message) => {
        if (message.done) {
          // Request complete
          sendSSEEvent(res, {
            id: `chatcmpl-${Date.now()}`,
            object: 'chat.completion',
            created: Math.floor(Date.now() / 1000),
            model: model || 'openclaw',
            choices: [{
              index: 0,
              message: {
                role: 'assistant',
                content: message.content
              },
              finish_reason: 'stop'
            }]
          });

          sendSSEDone(res);
          requestHandlers.delete(requestId);
        } else if (message.error) {
          // Error occurred
          sendSSEEvent(res, {
            error: {
              message: message.error,
              type: 'api_error',
              code: 'internal_error'
            }
          });

          sendSSEDone(res);
          requestHandlers.delete(requestId);
        } else if (message.kind === 'agentChunk') {
          // Stream the chunk
          sendSSEEvent(res, {
            id: `chatcmpl-${Date.now()}`,
            object: 'chat.completion.chunk',
            created: Math.floor(Date.now() / 1000),
            model: model || 'openclaw',
            choices: [{
              index: 0,
              delta: {
                content: message.chunk
              }
            }]
          });
        } else if (message.kind === 'agentMessage') {
          // System message - could be ignored or streamed
          log(`System message: ${message.text}`);
        } else if (message.kind === 'agentTurn') {
          // Another agentTurn (shouldn't happen)
          log(`Unexpected agentTurn in response`);
        }
      };

      // Send to Gateway
      if (sendToGateway(requestId, request, tools)) {
        // Keep connection alive
        setInterval(() => {
          if (res.writable) {
            res.write(': keep-alive\n\n');
          }
        }, 15000);

      } else {
        // Gateway not connected
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

    // Handle tool_choice: 'required' (force tool use)
    if (tool_choice === 'required' && tools && tools.length > 0) {
      const tool = tools[0];
      const requestId = generateRequestId();

      const requestHandler = (message) => {
        if (message.done) {
          sendSSEEvent(res, {
            id: `chatcmpl-${Date.now()}`,
            object: 'chat.completion',
            created: Math.floor(Date.now() / 1000),
            model: model || 'openclaw',
            choices: [{
              index: 0,
              message: {
                role: 'assistant',
                content: `Executed tool: ${tool.name}\n\n${message.content}`
              },
              tool_calls: [{
                id: `call_${Date.now()}`,
                type: 'function',
                function: {
                  name: tool.name,
                  arguments: JSON.stringify(tool.arguments)
                }
              }],
              finish_reason: 'tool_calls'
            }]
          });

          sendSSEDone(res);
        } else if (message.error) {
          sendSSEEvent(res, {
            error: {
              message: message.error,
              type: 'api_error',
              code: 'internal_error'
            }
          });

          sendSSEDone(res);
        } else if (message.kind === 'agentChunk') {
          // Stream the tool execution progress
          sendSSEEvent(res, {
            id: `chatcmpl-${Date.now()}`,
            object: 'chat.completion.chunk',
            created: Math.floor(Date.now() / 1000),
            model: model || 'openclaw',
            choices: [{
              index: 0,
              delta: {
                content: message.chunk
              }
            }]
          });
        }
      };

      requestHandlers.set(requestId, requestHandler);

      // Send tool request
      sendToGateway(requestId, message, {
        [tool.name]: tool.arguments || {}
      });

      return;
    }

    // Handle non-streaming requests
    if (!stream) {
      const backend = determineBackendForRequest({ model });

      if (backend === 'gateway') {
        // Gateway non-streaming
        const requestId = generateRequestId();
        const availableTools = (BACKENDS[model] || BACKENDS['gateway']).tools || [];

        const requestHandler = (message) => {
          if (message.done) {
            res.json({
              id: `chatcmpl-${Date.now()}`,
              object: 'chat.completion',
              created: Math.floor(Date.now() / 1000),
              model: model || 'openclaw',
              choices: [{
                index: 0,
                message: {
                  role: 'assistant',
                  content: message.content
                },
                finish_reason: 'stop'
              }]
            });
          } else if (message.error) {
            res.status(500).json({
              error: {
                message: message.error,
                type: 'api_error',
                code: 'internal_error'
              }
            });
          }
        };

        requestHandlers.set(requestId, requestHandler);

        const systemMsgs = messages.filter(m => m.role === 'system');
        const fullSystemMessage = systemMsgs.map(m => m.content).join('\n\n');

        if (!sendToGateway(requestId, fullSystemMessage + message, availableTools)) {
          res.status(503).json({
            error: {
              message: 'Not connected to OpenClaw Gateway',
              type: 'api_error',
              code: 'connection_error'
            }
          });
        }

      } else if (backend === 'goose-cli') {
        // Goose CLI non-streaming
        const output = await executeGooseCLI(message, req.body);
        res.json({
          id: `chatcmpl-${Date.now()}`,
          object: 'chat.completion',
          created: Math.floor(Date.now() / 1000),
          model: model || 'goose',
          choices: [{
            index: 0,
            message: {
              role: 'assistant',
              content: output
            },
            finish_reason: 'stop'
          }]
        });
      } else {
        // OpenClaw CLI non-streaming
        const output = await executeOpenClawCLI(message, req.body);
        res.json({
          id: `chatcmpl-${Date.now()}`,
          object: 'chat.completion',
          created: Math.floor(Date.now() / 1000),
          model: model || 'openclaw',
          choices: [{
            index: 0,
            message: {
              role: 'assistant',
              content: output
            },
            finish_reason: 'stop'
          }]
        });
      }
    }
  } catch (error) {
    log('Error in chat completions:', error);

    if (stream && res.headersSent) {
      // If already streaming, can't send JSON error
      res.write(`data: ${JSON.stringify({ error: { message: error.message, type: 'api_error', code: 'internal_error' }})}\n\n`);
      res.write('data: [DONE]\n\n');
      res.end();
    } else {
      res.status(500).json({
        error: {
          message: error.message,
          type: 'api_error',
          code: 'internal_error'
        }
      });
    }
  }
});

// Goose CLI implementation
function executeGooseCLI(message, agentParams = {}) {
  return new Promise((resolve, reject) => {
    const sessionName = agentParams.sessionKey || 'openai-proxy';
    const args = ['run', message];

    log(`Executing Goose CLI: goose ${args.join(' ')}`);

    const workDir = process.platform === 'win32'
      ? 'C:\\Users\\aaron\\AppData\\Roaming\\Block\\goose'
      : process.env.HOME + '/.goose';

    const proc = spawn('goose', args, {
      env: process.env,
      cwd: workDir
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
      if (code === 0) {
        const cleanOutput = stdout
          .replace(/\x1b\[[0-9;]*m/g, '')
          .replace(/\r\n/g, '\n')
          .trim();

        resolve({ content: cleanOutput });
      } else {
        reject(new Error(`Goose exited with code ${code}: ${stderr}`));
      }
    });

    proc.on('error', (error) => {
      reject(new Error(`Failed to execute Goose: ${error.message}`));
    });
  });
}

// Backend status endpoint
app.get('/backends', (req, res) => {
  res.json({
    default: NON_STREAMING_BACKEND,
    streaming_mode: MODE,
    gateway_url: GATEWAY_URL,
    gateway_connected: gatewayWs ? gatewayWs.readyState === WebSocket.OPEN : false,
    available_backends: Object.keys(BACKENDS).map(name => ({
      name,
      displayName: BACKENDS[name].name
    }))
  });
});

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    mode: MODE,
    gateway_connected: gatewayWs ? gatewayWs.readyState === WebSocket.OPEN : false,
    supports_streaming: true,
    supports_function_calling: true,
    gateway_url: GATEWAY_URL,
    available_backends: Object.keys(BACKENDS)
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`\n🦥 OpenAI Streaming Proxy (Agentic Mode)`);
  console.log(`📡 HTTP Server: http://localhost:${PORT}`);
  console.log(`📝 Chat Completions: http://localhost:${PORT}/v1/chat/completions`);
  console.log(`🛠️ Tools: http://localhost:${PORT}/v1/tools`);
  console.log(`📊 Models: http://localhost:${PORT}/v1/models`);
  console.log(`🔧 Backends: http://localhost:${PORT}/backends`);
  console.log(`\nConfiguration:`);
  console.log(`  Mode: ${MODE} (${MODE === 'hybrid' ? 'Gateway for streaming, CLI for non-streaming' : 'Gateway only'})`);
  console.log(`  Gateway URL: ${GATEWAY_URL}`);
  console.log(`  Non-streaming Backend: ${NON_STREAMING_BACKEND}`);
  console.log(`\nStreaming: ✅ Enabled via OpenClaw Gateway WebSocket`);
  console.log(`\nAvailable Backends:`);
  Object.entries(BACKENDS).forEach(([name, config]) => {
    const toolsList = config.tools ? `${config.tools.length} tools` : '0 tools';
    console.log(`  - ${name}: ${config.name} (${toolsList})`);
  });
  console.log(`\nConfigure your client:`);
  console.log(`  Base URL: http://localhost:${PORT}/v1`);
  console.log(`  Model: openclaw`);
  console.log(`  Streaming: true (real-time!)`);
  console.log(`  Agentic Mode: true (function calling)\n`);
});

// Initialize Gateway connection
connectToGateway();

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\nShutting down...');

  if (gatewayWs) {
    gatewayWs.close();
  }

  // Clean up request handlers
  requestHandlers.clear();

  process.exit(0);
});
