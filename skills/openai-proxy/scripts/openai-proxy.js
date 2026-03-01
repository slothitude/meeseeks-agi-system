#!/usr/bin/env node

/**
 * OpenAI-Compatible Proxy for OpenClaw
 *
 * Exposes OpenClaw CLI as an OpenAI Chat Completions API endpoint.
 * Supports streaming, conversation history, and session routing.
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
    default: false
  })
  .option('thinking', {
    alias: 't',
    description: 'OpenClaw thinking level (off|minimal|low|medium|high|xhigh)',
    type: 'string',
    default: 'low'
  })
  .help()
  .alias('help', 'h')
  .argv;

const PORT = argv.port;
const VERBOSE = argv.verbose;
const THINKING_LEVEL = argv.thinking;

const app = express();

// Parse JSON bodies
app.use(bodyParser.json());

// Log helper
function log(...args) {
  if (VERBOSE) {
    console.log(`[${new Date().toISOString()}]`, ...args);
  }
}

// Helper: Execute OpenClaw CLI command with JSON output
function executeOpenClaw(message, agentParams = {}) {
  return new Promise((resolve, reject) => {
    const args = ['agent', '--local', '--json', '--message', message];

    // Add agent parameters
    const sessionKey = agentParams.sessionKey || 'openai-proxy-default';
    args.push('--session-id', sessionKey);

    if (agentParams.thinking) {
      args.push('--thinking', agentParams.thinking);
    }

    log(`Executing: openclaw ${args.join(' ')}`);

    // On Windows, use node to execute openclaw directly
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
      const text = data.toString();
      stdout += text;
    });

    proc.stderr.on('data', (data) => {
      const text = data.toString();
      stderr += text;
    });

    proc.on('close', (code) => {
      log(`OpenClaw exited with code ${code}`);

      if (code === 0) {
        try {
          // Try to parse JSON output
          const jsonOutput = JSON.parse(stdout);
          log(`Parsed JSON output`);

          // Extract the message from OpenClaw's JSON output format
          // Format: { payloads: [{ text: "...", mediaUrl: null }], meta: {...} }
          let content = '';

          if (jsonOutput.payloads && Array.isArray(jsonOutput.payloads) && jsonOutput.payloads.length > 0) {
            content = jsonOutput.payloads[0].text || '';
          } else if (jsonOutput.text) {
            content = jsonOutput.text;
          } else if (jsonOutput.message) {
            content = jsonOutput.message;
          } else if (jsonOutput.content) {
            content = jsonOutput.content;
          } else {
            // Fallback: return entire JSON as string
            log(`No content field found, returning raw JSON`);
            resolve(JSON.stringify(jsonOutput, null, 2));
            return;
          }

          // Clean up the content
          if (content) {
            // Remove ANSI codes if present
            content = content.replace(/\x1b\[[0-9;]*m/g, '').trim();
            resolve(content);
          } else {
            resolve('');
          }
        } catch (parseError) {
          // JSON parsing failed, fall back to text parsing
          log(`JSON parsing failed: ${parseError.message}`);
          log(`Falling back to text parsing`);

          // Remove ANSI codes and return as-is
          const cleanOutput = stdout
            .replace(/\x1b\[[0-9;]*m/g, '')
            .replace(/\r\n/g, '\n')
            .trim();

          log(`Fallback output (${cleanOutput.length} chars)`);
          resolve(cleanOutput);
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

// Convert OpenAI messages to OpenClaw format
function convertOpenAIMessages(messages) {
  if (!messages || messages.length === 0) {
    return '';
  }

  // Extract system prompt
  const systemMsgs = messages.filter(m => m.role === 'system');
  const systemPrompt = systemMsgs.map(m => m.content).join('\n\n');

  // Build conversation context
  const conversation = messages
    .filter(m => m.role !== 'system')
    .map(m => {
      const role = m.role === 'user' ? 'User' : 'Assistant';
      return `${role}: ${m.content}`;
    })
    .join('\n\n');

  // Combine system prompt with conversation
  if (systemPrompt) {
    return `${systemPrompt}\n\n${conversation}`;
  }
  return conversation;
}

// OpenAI Chat Completions endpoint
app.post('/v1/chat/completions', async (req, res) => {
  try {
    const { model, messages, temperature, stream, user, ...rest } = req.body;

    log(`Chat completions request: model=${model}, stream=${stream}, user=${user}`);

    // For now, only non-streaming is supported
    if (stream) {
      const errorResponse = {
        error: {
          message: 'Streaming not yet supported in CLI mode',
          type: 'api_error',
          code: 'not_implemented'
        }
      };
      return res.status(501).json(errorResponse);
    }

    // Convert OpenAI format to OpenClaw format
    const openClawMessage = convertOpenAIMessages(messages);

    // Build agent parameters
    const agentParams = {
      thinking: THINKING_LEVEL
    };
    if (user) {
      agentParams.sessionKey = user;
    }
    if (model && model !== 'openclaw') {
      agentParams.model = model;
    }

    // Execute OpenClaw CLI
    const content = await executeOpenClaw(openClawMessage, agentParams);

    // Build OpenAI-formatted response
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
        prompt_tokens: openClawMessage.length,
        completion_tokens: content.length,
        total_tokens: openClawMessage.length + content.length
      }
    };

    res.json(response);
  } catch (error) {
    log('Error handling chat completions:', error);

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

// Models endpoint (required by some clients)
app.get('/v1/models', (req, res) => {
  res.json({
    object: 'list',
    data: [
      {
        id: 'openclaw',
        object: 'model',
        created: Math.floor(Date.now() / 1000),
        owned_by: 'openclaw'
      }
    ]
  });
});

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    mode: 'cli'
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`\n🦥 OpenAI Proxy for OpenClaw (CLI Mode with JSON parsing)`);
  console.log(`📡 HTTP Server: http://localhost:${PORT}`);
  console.log(`📝 Chat Completions: http://localhost:${PORT}/v1/chat/completions`);
  console.log(`📊 Models: http://localhost:${PORT}/v1/models`);
  console.log(`\nConfigure your client:`);
  console.log(`  Base URL: http://localhost:${PORT}/v1`);
  console.log(`  Model: openclaw`);
  console.log(`  Thinking level: ${THINKING_LEVEL}\n`);
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\nShutting down...');
  process.exit(0);
});
