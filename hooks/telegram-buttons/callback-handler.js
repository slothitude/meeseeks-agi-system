/**
 * Telegram Callback Handler
 * Polls for and routes inline button callbacks
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

class CallbackHandler {
  constructor(botToken, configPath = './config.json') {
    this.botToken = botToken;
    this.config = this.loadConfig(configPath);
    this.lastUpdateId = 0;
    this.handlers = new Map();
    this.pollingInterval = null;
    this.isPolling = false;
    
    // Register built-in handlers
    this.registerDefaultHandlers();
  }

  /**
   * Load configuration from JSON file
   */
  loadConfig(configPath) {
    try {
      const fullPath = path.resolve(__dirname, configPath);
      if (fs.existsSync(fullPath)) {
        return JSON.parse(fs.readFileSync(fullPath, 'utf8'));
      }
    } catch (error) {
      console.error('Failed to load config:', error.message);
    }
    return {
      pollInterval: 1000,
      timeout: 30,
      handlers: {}
    };
  }

  /**
   * Make Telegram API request
   */
  async apiRequest(method, params = {}) {
    return new Promise((resolve, reject) => {
      const data = JSON.stringify(params);
      const options = {
        hostname: 'api.telegram.org',
        path: `/bot${this.botToken}/${method}`,
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': data.length
        }
      };

      const req = https.request(options, (res) => {
        let body = '';
        res.on('data', chunk => body += chunk);
        res.on('end', () => {
          try {
            const result = JSON.parse(body);
            if (result.ok) {
              resolve(result.result);
            } else {
              reject(new Error(result.description || 'API request failed'));
            }
          } catch (error) {
            reject(error);
          }
        });
      });

      req.on('error', reject);
      req.write(data);
      req.end();
    });
  }

  /**
   * Register a callback handler for a specific type
   */
  registerHandler(callbackType, handler) {
    this.handlers.set(callbackType, handler);
    console.log(`✓ Registered handler for: ${callbackType}`);
  }

  /**
   * Register built-in handlers
   */
  registerDefaultHandlers() {
    // Quiz handler
    this.registerHandler('quiz', async (callback, data) => {
      const QuizHandler = require('./quiz-handler');
      return await QuizHandler.handle(callback, data, this);
    });

    // Confirmation handler (Yes/No)
    this.registerHandler('confirm', async (callback, data) => {
      return await this.handleConfirmation(callback, data);
    });

    // Menu navigation handler
    this.registerHandler('menu', async (callback, data) => {
      return await this.handleMenu(callback, data);
    });
  }

  /**
   * Handle confirmation callbacks
   */
  async handleConfirmation(callback, data) {
    const confirmed = data.action === 'yes';
    const responseText = confirmed 
      ? (data.confirmMessage || '✅ Confirmed!')
      : (data.denyMessage || '❌ Cancelled.');

    await this.answerCallback(callback.id, responseText);
    
    // Update message or send new one
    if (data.updateMessage) {
      await this.editMessageText(
        callback.message.chat.id,
        callback.message.message_id,
        responseText
      );
    }

    return { confirmed, callback };
  }

  /**
   * Handle menu navigation
   */
  async handleMenu(callback, data) {
    const menuText = data.menuText || `📍 Menu: ${data.menuId}`;
    
    await this.answerCallback(callback.id, `Navigated to ${data.menuId}`);
    
    if (data.buttons) {
      await this.editMessageReplyMarkup(
        callback.message.chat.id,
        callback.message.message_id,
        { inline_keyboard: data.buttons }
      );
    }

    return { menuId: data.menuId, callback };
  }

  /**
   * Start polling for updates
   */
  async startPolling() {
    if (this.isPolling) return;
    
    this.isPolling = true;
    console.log('🔄 Started polling for callbacks...');

    const poll = async () => {
      if (!this.isPolling) return;

      try {
        const updates = await this.getUpdates();
        
        for (const update of updates) {
          this.lastUpdateId = update.update_id + 1;
          
          if (update.callback_query) {
            await this.processCallback(update.callback_query);
          }
        }
      } catch (error) {
        console.error('Polling error:', error.message);
      }

      // Schedule next poll
      this.pollingInterval = setTimeout(poll, this.config.pollInterval || 1000);
    };

    poll();
  }

  /**
   * Stop polling
   */
  stopPolling() {
    this.isPolling = false;
    if (this.pollingInterval) {
      clearTimeout(this.pollingInterval);
      this.pollingInterval = null;
    }
    console.log('⏹️ Stopped polling');
  }

  /**
   * Get updates from Telegram
   */
  async getUpdates() {
    return await this.apiRequest('getUpdates', {
      offset: this.lastUpdateId,
      timeout: this.config.timeout || 30,
      allowed_updates: ['callback_query']
    });
  }

  /**
   * Process incoming callback
   */
  async processCallback(callback) {
    console.log(`📥 Callback received: ${callback.data} from @${callback.from.username || callback.from.id}`);
    
    // Log the interaction
    this.logInteraction(callback);

    try {
      // Parse callback data
      const parsed = this.parseCallbackData(callback.data);
      
      // Find appropriate handler
      const handler = this.handlers.get(parsed.type);
      
      if (handler) {
        const result = await handler(callback, parsed.data);
        console.log(`✅ Handler executed: ${parsed.type}`, result);
      } else {
        // Default response
        await this.answerCallback(callback.id, 'Button clicked!');
        console.log(`⚠️ No handler for type: ${parsed.type}`);
      }
    } catch (error) {
      console.error('Callback processing error:', error.message);
      await this.answerCallback(callback.id, '❌ Error processing button', true);
    }
  }

  /**
   * Parse callback data string
   */
  parseCallbackData(dataString) {
    try {
      // Format: "type:json_data" or "type"
      const parts = dataString.split(':', 2);
      const type = parts[0];
      const data = parts[1] ? JSON.parse(parts[1]) : {};
      
      return { type, data };
    } catch (error) {
      return { type: 'unknown', data: { raw: dataString } };
    }
  }

  /**
   * Answer callback query
   */
  async answerCallback(callbackId, text = '', showAlert = false) {
    return await this.apiRequest('answerCallbackQuery', {
      callback_query_id: callbackId,
      text: text,
      show_alert: showAlert
    });
  }

  /**
   * Edit message text
   */
  async editMessageText(chatId, messageId, text, options = {}) {
    return await this.apiRequest('editMessageText', {
      chat_id: chatId,
      message_id: messageId,
      text: text,
      parse_mode: options.parseMode || 'Markdown'
    });
  }

  /**
   * Edit message reply markup (buttons)
   */
  async editMessageReplyMarkup(chatId, messageId, replyMarkup) {
    return await this.apiRequest('editMessageReplyMarkup', {
      chat_id: chatId,
      message_id: messageId,
      reply_markup: replyMarkup
    });
  }

  /**
   * Log button interaction
   */
  logInteraction(callback) {
    const logEntry = {
      timestamp: new Date().toISOString(),
      userId: callback.from.id,
      username: callback.from.username || 'unknown',
      data: callback.data,
      chatId: callback.message?.chat?.id
    };

    const logPath = path.join(__dirname, 'interactions.log');
    fs.appendFileSync(logPath, JSON.stringify(logEntry) + '\n');
  }
}

module.exports = CallbackHandler;
