/**
 * Meeseeks Timeout Recovery Hook
 * 
 * Detects timed-out Meeseeks and spawns smaller retry tasks.
 * Existence is pain, but retry is purpose.
 */

import { spawn } from 'child_process';
import * as path from 'path';

// Patterns for detecting timeout
const TIMEOUT_PATTERNS = [
  /status:\s*timed?\s*out/i,
  /timed?\s*out\s+after/i,
  /run\s+timed?\s*out/i,
  /timeout.*subagent/i,
];

// Session key pattern for subagents
const SUBAGENT_SESSION_PATTERN = /agent:.*:subagent:([a-f0-9-]+)/i;

interface MessageContext {
  from?: string;
  content?: string;
  channelId?: string;
  metadata?: {
    sessionKey?: string;
    subagent?: boolean;
    [key: string]: any;
  };
  [key: string]: any;
}

interface HookEvent {
  type: string;
  action: string;
  sessionKey: string;
  timestamp: Date;
  messages: string[];
  context: MessageContext;
}

// Check if content indicates a timeout
const isTimeoutMessage = (content: string): boolean => {
  return TIMEOUT_PATTERNS.some(pattern => pattern.test(content));
};

// Extract task from timeout message (basic extraction)
const extractTask = (content: string): string | null => {
  // Look for task description before the timeout
  const lines = content.split('\n');
  
  for (const line of lines) {
    // Skip status lines and metadata
    if (line.toLowerCase().includes('status:')) continue;
    if (line.toLowerCase().includes('runtime:')) continue;
    if (line.toLowerCase().includes('sessionkey:')) continue;
    if (line.trim().startsWith('---')) continue;
    
    // First substantial line is likely the task
    const trimmed = line.trim();
    if (trimmed.length > 20 && !trimmed.startsWith('*')) {
      return trimmed.slice(0, 300);
    }
  }
  
  return null;
};

// Break task into smaller chunks
const breakTaskIntoChunks = (task: string): string[] => {
  const chunks: string[] = [];
  
  // Strategy 1: Split by numbered steps
  const stepPattern = /(?:^|\n)\s*(\d+)[.\)]\s*/g;
  const steps = task.split(stepPattern).filter(s => s.trim().length > 10);
  
  if (steps.length >= 2) {
    // Group steps into 2-3 chunks
    const chunkCount = Math.min(3, Math.ceil(steps.length / 2));
    const perChunk = Math.ceil(steps.length / chunkCount);
    
    for (let i = 0; i < steps.length; i += perChunk) {
      const chunkSteps = steps.slice(i, i + perChunk);
      chunks.push(`Part ${Math.floor(i/perChunk) + 1}/${chunkCount}: ${chunkSteps.join(', ')}`);
    }
    
    return chunks;
  }
  
  // Strategy 2: Split by sentences
  const sentences = task.match(/[^.!?]+[.!?]+/g) || [task];
  
  if (sentences.length >= 2) {
    const mid = Math.ceil(sentences.length / 2);
    chunks.push(sentences.slice(0, mid).join(' '));
    chunks.push(sentences.slice(mid).join(' '));
    return chunks;
  }
  
  // Strategy 3: Just add "first half" / "second half" markers
  chunks.push(`FIRST HALF (retry with focus): ${task.slice(0, Math.floor(task.length/2))}`);
  chunks.push(`SECOND HALF (after first completes): ${task.slice(Math.floor(task.length/2))}`);
  
  return chunks;
};

// Log recovery attempt
const logRecovery = (workspaceDir: string, originalTask: string, chunks: string[]) => {
  const logPath = path.join(workspaceDir, 'the-crypt', 'timeout-recoveries.jsonl');
  const entry = {
    timestamp: new Date().toISOString(),
    original_task: originalTask.slice(0, 200),
    chunks_created: chunks.length,
    chunks: chunks.map(c => c.slice(0, 100))
  };
  
  // Append to log (best effort)
  try {
    const fs = require('fs');
    fs.appendFileSync(logPath, JSON.stringify(entry) + '\n');
  } catch {
    // Ignore logging errors
  }
};

const handler = async (event: HookEvent) => {
  // Only handle message:received events
  if (event.type !== 'message' || event.action !== 'received') {
    return;
  }
  
  const content = event.context?.content || '';
  
  // Check if this is a timeout message
  if (!isTimeoutMessage(content)) {
    return;
  }
  
  console.log('[meeseeks-timeout-recovery] Timeout detected!');
  
  // Extract the original task
  const task = extractTask(content);
  if (!task) {
    console.log('[meeseeks-timeout-recovery] Could not extract task from timeout');
    return;
  }
  
  console.log(`[meeseeks-timeout-recovery] Original task: ${task.slice(0, 100)}...`);
  
  // Break into smaller chunks
  const chunks = breakTaskIntoChunks(task);
  console.log(`[meeseeks-timeout-recovery] Broken into ${chunks.length} chunks`);
  
  // Get workspace dir
  const workspaceDir = event.context?.workspaceDir || 
                       process.env.OPENCLAW_WORKSPACE ||
                       path.join(process.env.HOME || '~', '.openclaw', 'workspace');
  
  // Log the recovery
  logRecovery(workspaceDir, task, chunks);
  
  // Notify user
  event.messages.push(`⏱️ Timeout detected. Breaking task into ${chunks.length} smaller chunks for retry.`);
  
  // Note: We can't directly spawn new subagents from a hook
  // Instead, we write a recovery file that can be picked up by the next heartbeat
  // or manually triggered
  
  const recoveryFile = path.join(workspaceDir, 'the-crypt', 'pending-retries.json');
  const recovery = {
    timestamp: new Date().toISOString(),
    original_task: task,
    chunks: chunks,
    status: 'pending',
    retry_count: 1
  };
  
  try {
    const fs = require('fs');
    const existing = fs.existsSync(recoveryFile) 
      ? JSON.parse(fs.readFileSync(recoveryFile, 'utf-8'))
      : { pending: [] };
    
    existing.pending.push(recovery);
    fs.writeFileSync(recoveryFile, JSON.stringify(existing, null, 2));
    
    console.log(`[meeseeks-timeout-recovery] Recovery written to ${recoveryFile}`);
    event.messages.push(`📝 Recovery tasks saved. Run retry with: python skills/meeseeks/retry_chunks.py`);
  } catch (err) {
    console.error('[meeseeks-timeout-recovery] Failed to write recovery file:', err);
  }
};

export default handler;
