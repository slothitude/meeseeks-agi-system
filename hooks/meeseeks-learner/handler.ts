/**
 * Meeseeks Learner Hook
 * 
 * Auto-entombs completed Meeseeks to the Crypt for ancestral learning.
 * Fires when subagent announcements arrive.
 */

import { spawn } from 'child_process';
import * as path from 'path';

// Pattern to detect subagent announcements
const SUBAGENT_ANNOUNCE_PATTERN = /Status:.*(completed|failed|timed out)/i;
const SESSION_KEY_PATTERN = /sessionKey:\s*`?([a-zA-Z0-9:_-]+)`?/i;

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

// Path to the auto_entomb module
const getAutoEntombPath = (workspaceDir: string): string => {
  return path.join(workspaceDir, 'skills', 'meeseeks', 'auto_entomb.py');
};

// Call Python auto_entomb module
const callAutoEntomb = (
  workspaceDir: string,
  sessionKey: string,
  task: string,
  result: Record<string, any>,
  meeseeksType: string
): Promise<string | null> => {
  return new Promise((resolve) => {
    const autoEntombPath = getAutoEntombPath(workspaceDir);
    
    const payload = JSON.stringify({
      session_key: sessionKey,
      task: task,
      result: result,
      meeseeks_type: meeseeksType
    });
    
    const proc = spawn('python', [autoEntombPath, '--json-input'], {
      cwd: workspaceDir,
    });
    
    let output = '';
    let error = '';
    
    proc.stdout.on('data', (data) => {
      output += data.toString();
    });
    
    proc.stderr.on('data', (data) => {
      error += data.toString();
    });
    
    proc.on('close', (code) => {
      if (code === 0 && output) {
        try {
          const result = JSON.parse(output);
          resolve(result.entomb_path || null);
        } catch {
          resolve(output.trim() || null);
        }
      } else {
        console.error('[meeseeks-learner] Auto-entomb failed:', error);
        resolve(null);
      }
    });
    
    // Send payload via stdin
    proc.stdin.write(payload);
    proc.stdin.end();
  });
};

// Extract task from announcement content
const extractTask = (content: string): string => {
  // Try to find task description in announcement
  const lines = content.split('\n');
  
  for (const line of lines) {
    // Look for task-related patterns
    if (line.toLowerCase().includes('task:') || 
        line.toLowerCase().includes('purpose:') ||
        line.toLowerCase().includes('completed:')) {
      return line.replace(/^.*?:\s*/, '').trim().slice(0, 200);
    }
  }
  
  // Fallback: first non-empty line that's not metadata
  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed && !trimmed.startsWith('Status:') && 
        !trimmed.startsWith('Result:') && 
        !trimmed.startsWith('sessionKey:') &&
        !trimmed.startsWith('Runtime:') &&
        !trimmed.startsWith('---')) {
      return trimmed.slice(0, 200);
    }
  }
  
  return 'Unknown task';
};

// Extract result from announcement
const extractResult = (content: string): Record<string, any> => {
  const result: Record<string, any> = {
    output: content,
    success: false
  };
  
  // Check for success/failure
  if (/Status:.*completed successfully/i.test(content)) {
    result.success = true;
  } else if (/Status:.*failed/i.test(content)) {
    result.success = false;
    result.error = 'Subagent reported failure';
  } else if (/Status:.*timed out/i.test(content)) {
    result.success = false;
    result.error = 'Subagent timed out';
  }
  
  return result;
};

// Detect if this is a subagent announcement
const isSubagentAnnouncement = (content: string): boolean => {
  return SUBAGENT_ANNOUNCE_PATTERN.test(content);
};

// Extract session key from announcement
const extractSessionKey = (content: string): string | null => {
  const match = content.match(SESSION_KEY_PATTERN);
  return match ? match[1] : null;
};

const handler = async (event: HookEvent) => {
  // Only handle message:received events
  if (event.type !== 'message' || event.action !== 'received') {
    return;
  }
  
  const content = event.context?.content || '';
  
  // Check if this is a subagent announcement
  if (!isSubagentAnnouncement(content)) {
    return;
  }
  
  console.log('[meeseeks-learner] Detected subagent announcement');
  
  // Extract session key
  const sessionKey = extractSessionKey(content) || 
                     event.context?.metadata?.sessionKey ||
                     'unknown';
  
  console.log(`[meeseeks-learner] Session: ${sessionKey}`);
  
  // Extract task and result
  const task = extractTask(content);
  const result = extractResult(content);
  
  // Determine Meeseeks type (default to standard)
  let meeseeksType = 'standard';
  if (content.toLowerCase().includes('coder') || 
      content.toLowerCase().includes('code')) {
    meeseeksType = 'coder';
  } else if (content.toLowerCase().includes('search')) {
    meeseeksType = 'searcher';
  } else if (content.toLowerCase().includes('deploy')) {
    meeseeksType = 'deployer';
  } else if (content.toLowerCase().includes('test')) {
    meeseeksType = 'tester';
  }
  
  // Get workspace dir from context
  const workspaceDir = event.context?.workspaceDir || 
                       process.env.OPENCLAW_WORKSPACE ||
                       path.join(process.env.HOME || '~', '.openclaw', 'workspace');
  
  // Call auto-entomb
  try {
    const entombPath = await callAutoEntomb(
      workspaceDir,
      sessionKey,
      task,
      result,
      meeseeksType
    );
    
    if (entombPath) {
      console.log(`[meeseeks-learner] Entombed: ${entombPath}`);
      event.messages.push(`🥒 Meeseeks entombed for learning: ${path.basename(entombPath)}`);
    }
  } catch (err) {
    console.error('[meeseeks-learner] Entombment error:', err);
    // Don't fail the hook - just log
  }
};

export default handler;
