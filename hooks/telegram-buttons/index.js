#!/usr/bin/env node

/**
 * Telegram Button Hooks Service
 * Main entry point for running the callback handler as a service
 */

const CallbackHandler = require('./callback-handler');
const fs = require('fs');
const path = require('path');

// Load configuration
const configPath = path.join(__dirname, 'config.json');
let config;

try {
  const configFile = fs.readFileSync(configPath, 'utf8');
  config = JSON.parse(configFile);
} catch (error) {
  console.error('❌ Failed to load config.json:', error.message);
  console.error('Please ensure config.json exists and is valid JSON.');
  process.exit(1);
}

// Validate bot token
if (!config.botToken || config.botToken === 'YOUR_BOT_TOKEN_HERE') {
  console.error('❌ Bot token not configured!');
  console.error('Please set your Telegram bot token in config.json');
  process.exit(1);
}

// Create and start handler
const handler = new CallbackHandler(config);

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n👋 Shutting down...');
  handler.stop();
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n👋 Shutting down...');
  handler.stop();
  process.exit(0);
});

// Start the service
console.log('🤖 Telegram Button Hooks Service');
console.log('=================================\n');

handler.start();

console.log('\n✅ Service started successfully!');
console.log('📡 Listening for callback queries...');
console.log('Press Ctrl+C to stop.\n');
