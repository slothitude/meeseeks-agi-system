#!/usr/bin/env node

const express = require('express');
const bodyParser = require('body-parser');
const { spawn } = require('child_process');
const os = require('os');
const yargs = require('yargs/yargs');
const { hideBin } = require('yargs/helpers');

const HOSTNAME = os.hostname().toLowerCase().replace(/[^a-z0-9]/g, '_');
const MACHINE_SUFFIX = HOSTNAME.includes('rog') ? 'rog' : 
                       HOSTNAME.includes('pi') || HOSTNAME.includes('pibot') ? 'pibot' : 
                       HOSTNAME.substring(0, 10);

const argv = yargs(hideBin(process.argv))
  .option('port', { alias: 'p', type: 'number', default: 3001 })
  .option('backend', { alias: 'b', type: 'string', default: 'openclaw' })
  .option('suffix', { alias: 's', type: 'string', default: MACHINE_SUFFIX })
  .option('verbose', { alias: 'v', type: 'boolean', default: false })
  .argv;

const PORT = argv.port;
const DEFAULT_BACKEND = argv.backend;
const MACHINE_SUFFIX_FINAL = argv.suffix;
const VERBOSE = argv.verbose;

const MODEL_NAMES = {
  goose: 'goose_' + MACHINE_SUFFIX_FINAL,
  openclaw: 'openclaw_' + MACHINE_SUFFIX_FINAL
};

const app = express();
app.use(bodyParser.json());

const BACKENDS = {
  openclaw: {
    name: 'OpenClaw (' + MACHINE_SUFFIX_FINAL + ')',
    modelName: MODEL_NAMES.openclaw,
    execute: executeOpenClaw,
    parseResponse: parseOpenClawResponse,
    description: 'OpenClaw AI agent on ' + MACHINE_SUFFIX_FINAL
  },
  goose: {
    name: 'Goose CLI (' + MACHINE_SUFFIX_FINAL + ')',
    modelName: MODEL_NAMES.goose,
    execute: executeGoose,
    parseResponse: parseGooseResponse,
    description: 'Goose CLI agent on ' + MACHINE_SUFFIX_FINAL
  }
};

function log(...args) {
  if (VERBOSE) console.log('[' + new Date().toISOString() + ']', ...args);
}

function convertOpenAIMessages(messages) {
  if (!messages || messages.length === 0) return '';
  const systemMsgs = messages.filter(m => m.role === 'system');
  const systemPrompt = systemMsgs.map(m => m.content).join('\n\n');
  const conversation = messages
    .filter(m => m.role !== 'system')
    .map(m => (m.role === 'user' ? 'User' : 'Assistant') + ': ' + m.content)
    .join('\n\n');
  return systemPrompt ? systemPrompt + '\n\n' + conversation : conversation;
}

function executeOpenClaw(message, agentParams) {
  agentParams = agentParams || {};
  return new Promise((resolve, reject) => {
    const args = ['agent', '--local', '--json', '--message', message];
    log('Executing: openclaw ' + args.join(' '));
    const proc = spawn('openclaw', args, { env: process.env });
    let stdout = '', stderr = '';
    proc.stdout.on('data', (data) => { stdout += data.toString(); });
    proc.stderr.on('data', (data) => { stderr += data.toString(); });
    proc.on('close', (code) => {
      if (code === 0) resolve({ stdout, stderr });
      else reject(new Error('OpenClaw exited with code ' + code + ': ' + stderr));
    });
    proc.on('error', (error) => { reject(new Error('Failed to execute OpenClaw: ' + error.message)); });
  });
}

function parseOpenClawResponse(output) {
  try {
    const jsonOutput = JSON.parse(output.stdout);
    let content = '';
    if (jsonOutput.payloads && Array.isArray(jsonOutput.payloads)) {
      content = jsonOutput.payloads[0].text || '';
    } else if (jsonOutput.text) content = jsonOutput.text;
    else if (jsonOutput.message) content = jsonOutput.message;
    else return JSON.stringify(jsonOutput, null, 2);
    return content.replace(/\x1b\[[0-9;]*m/g, '').trim();
  } catch (e) {
    return output.stdout.replace(/\x1b\[[0-9;]*m/g, '').trim();
  }
}

function executeGoose(message, agentParams) {
  agentParams = agentParams || {};
  return new Promise((resolve, reject) => {
    const isWindows = process.platform === 'win32';
    const goosePath = isWindows ? 'goose' : '/home/az/.local/bin/goose';
    
    // Use different args for Windows vs Linux
    const args = isWindows 
      ? ['run', '--text', message, '--quiet']
      : ['run', '-i', '-', '--quiet'];  // Linux uses stdin
    
    log('Executing: ' + goosePath + ' ' + args.join(' '));
    
    // Set env vars for API authentication
    const env = { 
      ...process.env,
      OPENAI_API_KEY: 'sk-zai-z0bsI55MGLM4Flash',
      OPENAI_BASE_URL: 'https://api.z.ai/api/v1'
    };
    
    const proc = spawn(goosePath, args, { 
      env: env, 
      cwd: process.env.HOME 
    });
    
    // On Linux, send message via stdin
    if (!isWindows) {
      proc.stdin.write(message);
      proc.stdin.end();
    }
    
    let stdout = '', stderr = '';
    proc.stdout.on('data', (data) => { stdout += data.toString(); });
    proc.stderr.on('data', (data) => { stderr += data.toString(); });
    proc.on('close', (code) => {
      if (code === 0) resolve({ stdout, stderr });
      else reject(new Error('Goose exited with code ' + code + ': ' + stderr));
    });
    proc.on('error', (error) => { reject(new Error('Failed to execute Goose: ' + error.message)); });
  });
}

function parseGooseResponse(output) {
  return output.stdout.replace(/\x1b\[[0-9;]*m/g, '').trim();
}

function determineBackend(requestBody) {
  const model = requestBody.model || '';
  if (model === MODEL_NAMES.goose || model.startsWith('goose_')) return 'goose';
  if (model === MODEL_NAMES.openclaw || model.startsWith('openclaw_')) return 'openclaw';
  return DEFAULT_BACKEND;
}

async function routeRequest(requestBody) {
  const backend = determineBackend(requestBody);
  const backendConfig = BACKENDS[backend];
  if (!backendConfig) throw new Error('Unknown backend: ' + backend);
  log('Routing to ' + backendConfig.name);
  const message = convertOpenAIMessages(requestBody.messages);
  const output = await backendConfig.execute(message, {});
  return backendConfig.parseResponse(output);
}

app.post('/v1/chat/completions', async (req, res) => {
  try {
    const { model } = req.body;
    log('Chat request: model=' + model);
    const content = await routeRequest(req.body);
    res.json({
      id: 'chatcmpl-' + Date.now(),
      object: 'chat.completion',
      created: Math.floor(Date.now() / 1000),
      model: model || MODEL_NAMES[DEFAULT_BACKEND],
      choices: [{ index: 0, message: { role: 'assistant', content }, finish_reason: 'stop' }],
      usage: { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 }
    });
  } catch (error) {
    log('Error:', error);
    res.status(500).json({ error: { message: error.message, code: 'internal_error' } });
  }
});

app.get('/v1/models', (req, res) => {
  res.json({ object: 'list', data: Object.entries(BACKENDS).map(([name, config]) => ({
    id: config.modelName,
    object: 'model',
    provider: config.name,
    description: config.description
  }))});
});

app.get('/health', (req, res) => {
  res.json({ status: 'ok', machine: MACHINE_SUFFIX_FINAL, models: MODEL_NAMES });
});

app.listen(PORT, () => {
  console.log('OpenAI Multi-Agent Proxy');
  console.log('Machine: ' + MACHINE_SUFFIX_FINAL);
  console.log('Port: ' + PORT);
  console.log('Models: ' + MODEL_NAMES.goose + ', ' + MODEL_NAMES.openclaw);
});

process.on('SIGINT', () => process.exit(0));
