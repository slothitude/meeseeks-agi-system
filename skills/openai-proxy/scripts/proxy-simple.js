#!/usr/bin/env node

/**
 * OpenAI-Compatible Multi-Agent Proxy (Simple CLI Mode)
 *
 * Non-streaming version with tool definitions support.
 * Reliable, easy to debug, works with any model.
 */

const express = require('express');
const bodyParser = require('body-parser');
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
  .option('verbose', {
    alias: 'v',
    description: 'Enable verbose logging',
    type: 'boolean',
    default: true
  })
  .option('backend', {
    alias: 'b',
    description: 'Backend (openclaw|goose)',
    type: 'string',
    default: 'openclaw'
  })
  .help()
  .alias('help', 'h')
  .argv;

const PORT = argv.port;
const VERBOSE = argv.verbose;
const DEFAULT_BACKEND = argv.backend;

const app = express();

// Parse JSON bodies
app.use(bodyParser.json());

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
    execute: executeOpenClaw,
    tools: [
      {
        id: 'browser',
        name: 'browser',
        type: 'function',
        description: 'Browse websites and take screenshots',
        parameters: {
          type: 'object',
          properties: {
            url: { type: 'string', description: 'URL to browse' },
            action: { type: 'string', enum: ['screenshot', 'extract_text', 'search'], description: 'Action' }
          },
          required: ['url']
        }
      },
      {
        id: 'canvas',
        name: 'canvas',
        type: 'function',
        description: 'Visual workspace for collaboration',
        parameters: {
          type: 'object',
          properties: {
            action: { type: 'string', enum: ['create', 'update', 'clear'], description: 'Action' },
            data: { type: 'object', description: 'Canvas data (optional)' }
          },
          required: ['action']
        }
      },
      {
        id: 'nodes',
        name: 'nodes',
        type: 'function',
        description: 'Device and system control',
        parameters: {
          type: 'object',
          properties: {
            action: { type: 'string', enum: ['camera_snap', 'screen_record'], description: 'Action' }
          },
          required: ['action']
        }
      },
      {
        id: 'files',
        name: 'files',
        type: 'function',
        description: 'File system operations',
        parameters: {
          type: 'object',
          properties: {
            action: { type: 'string', enum: ['read', 'write', 'list', 'search'], description: 'Action' },
            path: { type: 'string', description: 'File path' }
          },
          required: ['action']
        }
      }
    ]
  },
  goose: {
    name: 'Goose CLI',
    execute: executeGoose,
    tools: [
      {
        id: 'memory',
        name: 'memory',
        type: 'function',
        description: 'Personalization memory',
        parameters: {
          type: 'object',
          properties: {
            action: { type: 'string', enum: ['search', 'add', 'get'], description: 'Action' },
            key: { type: 'string', description: 'Memory key' },
            value: { type: 'string', description: 'Memory value' }
          },
          required: ['action']
        }
      },
      {
        id: 'filesystem',
        name: 'filesystem',
        type: 'function',
        description: 'File system access',
        parameters: {
          type: 'object',
          properties: {
            action: { type: 'string', enum: ['read', 'write', 'list', 'search'], description: 'Action' },
            path: { type: 'string', description: 'File path' }
          },
          required: ['action']
        }
      }
    ]
  }
};

// Convert OpenAI messages to backend format
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

// OpenClaw backend implementation
function executeOpenClaw(message, agentParams = {}) {
  return new Promise((resolve, reject) => {
    const args = ['agent', '--local', '--json', '--message', message];

    const sessionKey = agentParams.sessionKey || 'openai-proxy-default';
    args.push('--session-id', sessionKey);

    if (agentParams.thinking) {
      args.push('--thinking', agentParams.thinking);
    }

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
      log(`OpenClaw exited with code ${code}`);

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
        } catch (e) {
          const cleanOutput = stdout
            .replace(/\x1b\[[0-9;]*m/g, '')
            .replace(/\r\n/g, '\n')
            .trim();

          resolve({ content: cleanOutput });
        }
      } else {
        reject(new Error(`OpenClaw exited with code ${code}: ${stderr}`));
      }
    });

    proc.on('error', (error) => {
      reject(new Error(`Failed to execute OpenClaw: ${error.message}`));
    });
  });
}

// Goose CLI backend implementation
function executeGoose(message, agentParams = {}) {
  return new Promise((resolve, reject) => {
    const sessionName = agentParams.sessionKey || 'openai-proxy';
    const args = ['run', message];

    log(`Executing: goose ${args.join(' ')}`);

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
      log(`Goose exited with code ${code}`);

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

// Determine backend
function determineBackend(request) {
  const model = request.model || '';

  if (model === 'goose' || model === 'goose-fast') {
    return 'goose';
  }

  return DEFAULT_BACKEND;
}

// GET /v1/tools - List available tools
app.get('/v1/tools', (req, res) => {
  const backend = determineBackend(req);
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

// GET /v1/models - List available models
app.get('/v1/models', (req, res) => {
  const now = Date.now();

  const backends = Object.keys(BACKENDS).map(name => ({
    id: name,
    object: 'model',
    created: Math.floor(now / 1000),
    owned_by: 'openai-proxy',
    provider: BACKENDS[name].name,
    description: `${BACKENDS[name].name} AI agent with tool support`,
    capabilities: BACKENDS[name].tools.map(t => t.name),
    permission: ['public'],
    spec: {
      backend: name,
      type: 'agent',
      version: '1.0',
      supports_function_calling: true,
      supports_tools: true
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
    const { model, messages, tools, tool_choice } = req.body;

    log(`Chat completions: model=${model}, tools=${tools ? 'yes' : 'no'}, tool_choice=${tool_choice}`);

    // Handle tool_choice: 'required' (force tool use)
    if (tool_choice === 'required' && tools && tools.length > 0) {
      const tool = tools[0];
      const toolArgs = tools[0].arguments || {};

      const toolResult = `Executed tool: ${tool.name} with args: ${JSON.stringify(toolArgs)}`;

      const response = {
        id: `chatcmpl-${Date.now()}`,
        object: 'chat.completion',
        created: Math.floor(Date.now() / 1000),
        model: model || 'openclaw',
        choices: [{
          index: 0,
          message: {
            role: 'assistant',
            content: toolResult
          },
          tool_calls: [{
            id: `call_${Date.now()}`,
            type: 'function',
            function: {
              name: tool.name,
              arguments: JSON.stringify(toolArgs)
            }
          }]
        }],
        finish_reason: 'tool_calls'
      };

      return res.json(response);
    }

    const message = convertOpenAIMessages(messages);
    const backend = determineBackend(req);
    const backendConfig = BACKENDS[backend];

    // Execute request
    const output = await backendConfig.execute(message, req.body);
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
    log('Error in chat completions:', error);

    const errorResponse = {
      error: {
        message: error.message,
        type: 'api_error',
        code: 'internal_error'
      }
    };

    res.status(500).json(errorResponse);
  }
});

// GET /health - Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    backend: DEFAULT_BACKEND,
    backends: Object.keys(BACKENDS),
    supports_tools: true
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`\n🦥 OpenAI Multi-Agent Proxy (Simple Mode)`);
  console.log(`📡 HTTP Server: http://localhost:${PORT}`);
  console.log(`📝 Chat Completions: http://localhost:${PORT}/v1/chat/completions`);
  console.log(`🛠️ Tools: http://localhost:${PORT}/v1/tools`);
  console.log(`📊 Models: http://localhost:${PORT}/v1/models`);
  console.log(`\nConfiguration:`);
  console.log(`  Default Backend: ${DEFAULT_BACKEND}`);
  console.log(`  Verbose: ${VERBOSE}`);
  console.log(`\nAvailable Backends:`);
  Object.entries(BACKENDS).forEach(([name, config]) => {
    const toolsCount = config.tools ? config.tools.length : 0;
    console.log(`  - ${name}: ${config.name} (${toolsCount} tools)`);
  });
  console.log(`\nConfigure your client:`);
  console.log(`  Base URL: http://localhost:${PORT}/v1`);
  console.log(`  Model (OpenClaw): openclaw`);
  console.log(`  Model (Goose): goose`);
  console.log(`\nTool Calling: Enabled (Model-Managed Mode)`);
  console.log(`\nFor Agentic Mode (OpenWebUI Native Function Calling): Set model parameter to ${DEFAULT_BACKEND} and include tools array in requests.`);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\nShutting down...');
  process.exit(0);
});
