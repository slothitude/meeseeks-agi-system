#!/usr/bin/env node

/**
 * Pi Worker Bridge
 * 
 * Spawns pi-coding-agent in RPC mode and provides a simple API
 * for OpenClaw to use it as a programmable worker.
 */

const { spawn } = require('child_process');
const readline = require('readline');

class PiWorker {
  constructor(options = {}) {
    this.options = {
      model: options.model || 'glm-5',
      thinking: options.thinking || 'low',
      tools: options.tools || ['read', 'bash', 'edit', 'write'],
      ...options
    };
    this.process = null;
    this.pendingRequests = new Map();
    this.requestId = 0;
  }

  /**
   * Start the pi worker process
   */
  async start() {
    return new Promise((resolve, reject) => {
      const args = [
        '--mode', 'rpc',
        '--model', this.options.model,
        '--thinking', this.options.thinking,
        '--tools', this.options.tools.join(',')
      ];

      // On Windows, use pi.cmd
      const piPath = process.platform === 'win32'
        ? 'C:\\Users\\aaron\\AppData\\Roaming\\npm\\pi.cmd'
        : 'pi';

      this.process = spawn(piPath, args, {
        env: process.env,
        stdio: ['pipe', 'pipe', 'pipe'],
        shell: process.platform === 'win32'
      });

      // Handle stdout (JSON-RPC responses)
      const rl = readline.createInterface({
        input: this.process.stdout,
        crlfDelay: Infinity
      });

      rl.on('line', (line) => {
        try {
          const response = JSON.parse(line);
          this._handleResponse(response);
        } catch (e) {
          console.error('Failed to parse pi response:', line);
        }
      });

      // Handle stderr (logs)
      this.process.stderr.on('data', (data) => {
        if (this.options.verbose) {
          console.error('[pi]', data.toString());
        }
      });

      this.process.on('error', (error) => {
        reject(error);
      });

      this.process.on('close', (code) => {
        if (this.options.verbose) {
          console.log('[pi] Process closed with code', code);
        }
      });

      // Wait for pi to be ready
      setTimeout(() => resolve(), 1000);
    });
  }

  /**
   * Send a prompt to pi and get the response
   */
  async prompt(text, options = {}) {
    return new Promise((resolve, reject) => {
      const requestId = ++this.requestId;
      
      this.pendingRequests.set(requestId, {
        resolve,
        reject,
        response: '',
        timeout: setTimeout(() => {
          this.pendingRequests.delete(requestId);
          reject(new Error('Request timeout'));
        }, options.timeout || 120000)
      });

      const command = {
        command: 'prompt',
        params: { text }
      };

      this.process.stdin.write(JSON.stringify(command) + '\n');
    });
  }

  /**
   * Abort current operation
   */
  abort() {
    const command = { command: 'abort' };
    this.process.stdin.write(JSON.stringify(command) + '\n');
  }

  /**
   * Get available tools
   */
  async getTools() {
    return new Promise((resolve, reject) => {
      const requestId = ++this.requestId;
      
      this.pendingRequests.set(requestId, { resolve, reject });

      const command = { command: 'get_tools' };
      this.process.stdin.write(JSON.stringify(command) + '\n');
    });
  }

  /**
   * Set active tools
   */
  async setTools(tools) {
    return new Promise((resolve, reject) => {
      const requestId = ++this.requestId;
      
      this.pendingRequests.set(requestId, { resolve, reject });

      const command = {
        command: 'set_tools',
        params: { tools }
      };
      this.process.stdin.write(JSON.stringify(command) + '\n');
    });
  }

  /**
   * Stop the worker
   */
  stop() {
    if (this.process) {
      this.process.kill();
      this.process = null;
    }
    
    // Clear pending requests
    for (const [id, { reject, timeout }] of this.pendingRequests) {
      clearTimeout(timeout);
      reject(new Error('Worker stopped'));
    }
    this.pendingRequests.clear();
  }

  /**
   * Handle incoming responses
   */
  _handleResponse(response) {
    // Find the most recent pending request
    // (pi doesn't include request IDs, so we match by order)
    const entries = Array.from(this.pendingRequests.entries());
    if (entries.length === 0) return;

    const [requestId, pending] = entries[0];

    if (response.type === 'done') {
      clearTimeout(pending.timeout);
      this.pendingRequests.delete(requestId);
      pending.resolve(pending.response);
    } else if (response.type === 'assistant_message') {
      if (response.delta?.content) {
        pending.response += response.delta.content;
      }
    } else if (response.type === 'error') {
      clearTimeout(pending.timeout);
      this.pendingRequests.delete(requestId);
      pending.reject(new Error(response.message || 'Unknown error'));
    }
  }
}

// CLI interface
if (require.main === module) {
  const worker = new PiWorker({ verbose: true });
  
  worker.start()
    .then(() => console.log('Pi worker started'))
    .then(() => worker.prompt('What files are in the current directory?'))
    .then(response => console.log('Response:', response))
    .then(() => worker.stop())
    .catch(err => {
      console.error('Error:', err);
      worker.stop();
      process.exit(1);
    });
}

module.exports = { PiWorker };
