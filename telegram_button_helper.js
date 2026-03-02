/**
 * Telegram Button Helper Module
 * Provides utilities for creating and managing inline button callbacks
 */

class TelegramButtonHelper {
  constructor(botToken) {
    this.botToken = botToken;
    this.apiUrl = `https://api.telegram.org/bot${botToken}`;
    this.callbackHandlers = new Map();
    this.lastUpdateId = 0;
  }

  /**
   * Create an inline keyboard button
   */
  createButton(text, callbackData, options = {}) {
    const button = {
      text,
      callback_data: callbackData
    };
    
    if (options.url) {
      button.url = options.url;
      delete button.callback_data;
    }
    
    return button;
  }

  /**
   * Create a row of buttons
   */
  createRow(...buttons) {
    return buttons;
  }

  /**
   * Create a full inline keyboard
   */
  createKeyboard(...rows) {
    return {
      inline_keyboard: rows
    };
  }

  /**
   * Encode callback data with type and payload
   */
  encodeCallback(type, payload = {}) {
    const data = JSON.stringify({ type, payload, t: Date.now() });
    // Telegram callback_data limit is 64 bytes
    if (data.length > 64) {
      // Use compression for larger payloads
      return this.compressCallback(type, payload);
    }
    return data;
  }

  /**
   * Decode callback data
   */
  decodeCallback(callbackData) {
    try {
      const parsed = JSON.parse(callbackData);
      return {
        type: parsed.type,
        payload: parsed.payload,
        timestamp: parsed.t
      };
    } catch (e) {
      // Handle compressed callbacks
      return this.decompressCallback(callbackData);
    }
  }

  /**
   * Compress callback data for longer payloads
   */
  compressCallback(type, payload) {
    // Simple compression: type:id format
    const id = Math.random().toString(36).substr(2, 9);
    this.callbackHandlers.set(id, { type, payload });
    return `${type}:${id}`;
  }

  /**
   * Decompress callback data
   */
  decompressCallback(callbackData) {
    const parts = callbackData.split(':');
    if (parts.length === 2) {
      const [type, id] = parts;
      const stored = this.callbackHandlers.get(id);
      if (stored) {
        return stored;
      }
      return { type, payload: {} };
    }
    return { type: callbackData, payload: {} };
  }

  /**
   * Create Yes/No confirmation buttons
   */
  createConfirmation(action, context = {}) {
    return this.createKeyboard(
      this.createRow(
        this.createButton('✅ Yes', this.encodeCallback('confirm', { action, value: true, ...context })),
        this.createButton('❌ No', this.encodeCallback('confirm', { action, value: false, ...context }))
      )
    );
  }

  /**
   * Create quiz answer buttons
   */
  createQuizButtons(questionId, options) {
    const rows = options.map((option, index) => {
      return this.createRow(
        this.createButton(option, this.encodeCallback('quiz_answer', { questionId, optionIndex: index }))
      );
    });
    return this.createKeyboard(...rows);
  }

  /**
   * Create navigation menu
   */
  createMenu(items, backAction = null) {
    const rows = items.map(item => {
      return this.createRow(
        this.createButton(item.label, this.encodeCallback('menu', { action: item.action }))
      );
    });
    
    if (backAction) {
      rows.push(this.createRow(
        this.createButton('⬅️ Back', this.encodeCallback('menu', { action: backAction }))
      ));
    }
    
    return this.createKeyboard(...rows);
  }

  /**
   * Make API request to Telegram
   */
  async apiRequest(method, params = {}) {
    const url = `${this.apiUrl}/${method}`;
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      });
      
      const data = await response.json();
      
      if (!data.ok) {
        throw new Error(`Telegram API error: ${data.description}`);
      }
      
      return data.result;
    } catch (error) {
      console.error(`API request failed (${method}):`, error.message);
      throw error;
    }
  }

  /**
   * Send message with inline keyboard
   */
  async sendMessage(chatId, text, keyboard = null, options = {}) {
    const params = {
      chat_id: chatId,
      text,
      parse_mode: options.parseMode || 'Markdown',
      ...options
    };
    
    if (keyboard) {
      params.reply_markup = keyboard;
    }
    
    return this.apiRequest('sendMessage', params);
  }

  /**
   * Edit message text and keyboard
   */
  async editMessage(chatId, messageId, text, keyboard = null) {
    const params = {
      chat_id: chatId,
      message_id: messageId,
      text,
      parse_mode: 'Markdown'
    };
    
    if (keyboard) {
      params.reply_markup = keyboard;
    }
    
    return this.apiRequest('editMessageText', params);
  }

  /**
   * Answer callback query (remove loading state)
   */
  async answerCallback(callbackQueryId, options = {}) {
    return this.apiRequest('answerCallbackQuery', {
      callback_query_id: callbackQueryId,
      text: options.text || '',
      show_alert: options.showAlert || false,
      cache_time: options.cacheTime || 0
    });
  }

  /**
   * Poll for updates
   */
  async getUpdates(timeout = 30, allowedUpdates = ['callback_query']) {
    const params = {
      timeout,
      allowed_updates: allowedUpdates
    };
    
    if (this.lastUpdateId > 0) {
      params.offset = this.lastUpdateId + 1;
    }
    
    const updates = await this.apiRequest('getUpdates', params);
    
    if (updates.length > 0) {
      this.lastUpdateId = updates[updates.length - 1].update_id;
    }
    
    return updates;
  }

  /**
   * Start polling loop
   */
  startPolling(handler, interval = 1000) {
    console.log('🔄 Starting callback polling...');
    
    this.polling = true;
    
    const poll = async () => {
      if (!this.polling) return;
      
      try {
        const updates = await this.getUpdates(30);
        
        for (const update of updates) {
          if (update.callback_query) {
            await handler(update.callback_query);
          }
        }
      } catch (error) {
        console.error('Polling error:', error.message);
      }
      
      if (this.polling) {
        setTimeout(poll, interval);
      }
    };
    
    poll();
  }

  /**
   * Stop polling
   */
  stopPolling() {
    console.log('⏹️ Stopping callback polling...');
    this.polling = false;
  }

  /**
   * Log button interaction
   */
  logInteraction(userId, username, callbackType, payload, result) {
    const logEntry = {
      timestamp: new Date().toISOString(),
      userId,
      username: username || 'unknown',
      type: callbackType,
      payload,
      result
    };
    
    console.log('🔘 Button Interaction:', JSON.stringify(logEntry, null, 2));
    
    // Could also write to file:
    // fs.appendFileSync('button_interactions.log', JSON.stringify(logEntry) + '\n');
    
    return logEntry;
  }
}

module.exports = TelegramButtonHelper;
