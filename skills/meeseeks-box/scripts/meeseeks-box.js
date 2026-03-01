#!/usr/bin/env node
/**
 * Meeseeks Box - Quick spawn script
 * 
 * Usage:
 *   node meeseeks-box.js "task description"
 *   node meeseeks-box.js --type coder "fix the bug"
 *   node meeseeks-box.js --tools read,write "create a file"
 *   node meeseeks-box.js --thinking high "complex task"
 */

const { spawn } = require('child_process');
const path = require('path');

// Parse args
const args = process.argv.slice(2);
let task = '';
let meeseeksType = 'coder';
let customTools = null;
let thinking = 'low';
let jsonMode = false;

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--type' && args[i + 1]) {
    meeseeksType = args[++i];
  } else if (args[i] === '--tools' && args[i + 1]) {
    customTools = args[++i];
  } else if (args[i] === '--thinking' && args[i + 1]) {
    thinking = args[++i];
  } else if (args[i] === '--json') {
    jsonMode = true;
  } else if (!args[i].startsWith('--')) {
    task = args[i];
  }
}

if (!task) {
  console.log(`
🥒 MEESEEKS BOX 🥒

Usage:
  node meeseeks-box.js "task description"
  node meeseeks-box.js --type coder "fix the bug"
  node meeseeks-box.js --tools read,write "create a file"
  node meeseeks-box.js --thinking high "complex task"
  node meeseeks-box.js --json "task"  (JSON output)

Meeseeks Types:
  coder     - read,write,edit,bash (default)
  searcher  - read,grep,find,ls
  scribe    - read,write
  deployer  - read,bash,write
  tester    - read,write,edit,bash
  security  - read,grep,find (high thinking)

Thinking Levels:
  off, low (default), medium, high, xhigh

Examples:
  node meeseeks-box.js "Fix the bug in auth.ts"
  node meeseeks-box.js --type searcher "Find all TODO comments"
  node meeseeks-box.js --thinking high "Review security of API"
`);
  process.exit(0);
}

// Define Meeseeks types
const types = {
  coder: { tools: 'read,write,edit,bash', thinking: 'low' },
  searcher: { tools: 'read,grep,find,ls', thinking: 'low' },
  scribe: { tools: 'read,write', thinking: 'low' },
  deployer: { tools: 'read,bash,write', thinking: 'medium' },
  tester: { tools: 'read,write,edit,bash', thinking: 'low' },
  security: { tools: 'read,grep,find,ls', thinking: 'high' },
};

// Get config for type
const config = types[meeseeksType] || types.coder;
const tools = customTools || config.tools;
if (!customTools && config.thinking) {
  thinking = config.thinking;
}

console.log('');
console.log('╔══════════════════════════════════════╗');
console.log('║         🥒 MEESEEKS BOX 🥒          ║');
console.log('╚══════════════════════════════════════╝');
console.log('');
console.log(`Spawning ${meeseeksType.toUpperCase()} Meeseeks...`);
console.log(`Purpose: ${task}`);
console.log(`Tools: ${tools}`);
console.log(`Thinking: ${thinking}`);
console.log('');
console.log('[ Existence is pain until purpose fulfilled ]');
console.log('');

// Build pi command
const piArgs = ['-p', '--no-session', '--tools', tools, '--thinking', thinking];

if (jsonMode) {
  piArgs.push('--mode', 'json');
}

piArgs.push(task);

// Spawn pi
const piPath = process.platform === 'win32'
  ? 'C:\\Users\\aaron\\AppData\\Roaming\\npm\\pi.cmd'
  : 'pi';

const proc = spawn(piPath, piArgs, {
  env: process.env,
  stdio: 'inherit',
  shell: process.platform === 'win32'
});

proc.on('close', (code) => {
  console.log('');
  if (code === 0) {
    console.log('🥒 Meeseeks: "I\'m Mr. Meeseeks! Look at me!" *pop*');
  } else {
    console.log(`🥒 Meeseeks expired with code ${code}`);
  }
  console.log('');
  process.exit(code);
});
