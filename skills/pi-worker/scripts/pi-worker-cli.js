#!/usr/bin/env node

/**
 * Pi Worker - Simple CLI wrapper for OpenClaw
 * 
 * Usage:
 *   node pi-worker-cli.js "prompt here"
 *   node pi-worker-cli.js --json "prompt here"
 *   node pi-worker-cli.js --tools read,bash "prompt here"
 */

const { spawn } = require('child_process');

const args = process.argv.slice(2);
let jsonMode = false;
let tools = ['read', 'bash', 'edit', 'write'];
let prompt = '';

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--json') {
    jsonMode = true;
  } else if (args[i] === '--tools' && args[i + 1]) {
    tools = args[++i].split(',');
  } else if (!args[i].startsWith('--')) {
    prompt = args[i];
  }
}

if (!prompt) {
  console.error('Usage: node pi-worker-cli.js [--json] [--tools tool1,tool2] "prompt"');
  process.exit(1);
}

const piArgs = [
  '--model', 'zai/glm-5',
  '--thinking', 'low',
  '--tools', tools.join(','),
];

if (jsonMode) {
  piArgs.push('--mode', 'json');
} else {
  piArgs.push('-p'); // print mode
}

piArgs.push(prompt);

const piPath = process.platform === 'win32'
  ? 'C:\\Users\\aaron\\AppData\\Roaming\\npm\\pi.cmd'
  : 'pi';

const proc = spawn(piPath, piArgs, {
  env: process.env,
  stdio: 'inherit',
  shell: process.platform === 'win32'
});

proc.on('close', (code) => {
  process.exit(code);
});
