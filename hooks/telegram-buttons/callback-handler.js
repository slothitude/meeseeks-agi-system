/**
 * Telegram Callback Handler
 * Main handler for processing inline button callbacks
 */

const TelegramButtonHelper = require('../../telegram_button_helper');
const QuizHandler = require('./quiz-handler');
const fs = require('fs');
const path = require('path');

class CallbackHandler {
  constructor(config) {
    this.config = config;
    this.helper = new TelegramButtonHelper(config.botToken);
    this.quizHandler = new QuizHandler(this.helper, config.quizzes);
    
    // Register callback type handlers
    this.handlers = new Map();
    this.registerHandler('confirm', this.handleConfirmation.bind(this));
    this.registerHandler('quiz_answer', this.handleQuizAnswer.bind(this));
    this.registerHandler('menu', this.handleMenu.bind(this));
    
    // Logging
    this.logFile = path.join(__dirname, 'interactions.log');
  }

  /**
   * Register a callback type handler
   */
  registerHandler(type, handler) {
    this.handlers.set(type, handler);
    console.log(`✅ Registered handler for: ${type}`);
  }

  /**
   * Main callback processing function
   */
  async processCallback(callbackQuery) {
    const { id, from, message, data } = callbackQuery;
    const userId = from.id;
    const username = from.username || from.first_name;
    
    try {
      // Decode callback data
      const decoded = this.helper.decodeCallback(data);
      const { type, payload } = decoded;
      
      console.log(`📩 Callback received: ${type} from ${username} (${userId})`);
      
      // Find handler
      const handler = this.handlers.get(type);
      
      if (!handler) {
        console.warn(`⚠️ No handler for callback type: ${type}`);
        await this.helper.answerCallback(id, { text: 'Unknown action' });
        return;
      }
      
      // Execute handler
      const result = await handler({
        callbackQueryId: id,
        userId,
        username,
        chatId: message.chat.id,
        messageId: message.message_id,
        payload
      });
      
      // Log interaction
      this.logInteraction(userId, username, type, payload, result);
      
    } catch (error) {
      console.error('❌ Error processing callback:', error);
      await this.helper.answerCallback(id, { text: 'Error processing request' });
    }
  }

  /**
   * Handle confirmation callbacks (Yes/No)
   */
  async handleConfirmation({ callbackQueryId, userId, username, chatId, messageId, payload }) {
    const { action, value, ...context } = payload;
    
    console.log(`💭 Confirmation: ${action} = ${value} by ${username}`);
    
    // Acknowledge the callback
    await this.helper.answerCallback(callbackQueryId, {
      text: value ? '✅ Confirmed!' : '❌ Cancelled',
      cacheTime: 5
    });
    
    // Update message based on confirmation
    let responseText = '';
    let result = 'confirmed';
    
    if (value) {
      responseText = `✅ *Confirmed*\n\nAction: ${action}\nStatus: Completed`;
      
      // Execute the confirmed action
      await this.executeConfirmedAction(action, context, userId);
    } else {
      responseText = `❌ *Cancelled*\n\nAction: ${action}\nStatus: Cancelled`;
      result = 'cancelled';
    }
    
    // Edit message to show result
    await this.helper.editMessage(chatId, messageId, responseText);
    
    return result;
  }

  /**
   * Handle quiz answer callbacks
   */
  async handleQuizAnswer({ callbackQueryId, userId, username, chatId, messageId, payload }) {
    const { questionId, optionIndex } = payload;
    
    // Delegate to quiz handler
    const result = await this.quizHandler.handleAnswer({
      callbackQueryId,
      userId,
      username,
      chatId,
      messageId,
      questionId,
      optionIndex
    });
    
    return result;
  }

  /**
   * Handle menu navigation callbacks
   */
  async handleMenu({ callbackQueryId, userId, username, chatId, messageId, payload }) {
    const { action } = payload;
    
    console.log(`🍽️ Menu navigation: ${action} by ${username}`);
    
    // Acknowledge callback
    await this.helper.answerCallback(callbackQueryId);
    
    // Get menu configuration
    const menuConfig = this.config.menus[action];
    
    if (!menuConfig) {
      console.warn(`⚠️ No menu config for: ${action}`);
      return 'menu_not_found';
    }
    
    // Send menu response
    await this.helper.editMessage(
      chatId,
      messageId,
      menuConfig.text,
      menuConfig.keyboard
    );
    
    return `navigated_to_${action}`;
  }

  /**
   * Execute a confirmed action (customizable)
   */
  async executeConfirmedAction(action, context, userId) {
    console.log(`🎯 Executing action: ${action} for user ${userId}`);
    
    // This is where you would implement specific actions
    // Example: delete message, send notification, update database, etc.
    
    switch (action) {
      case 'delete':
        // Handle delete action
        break;
      case 'subscribe':
        // Handle subscription
        break;
      case 'reset':
        // Handle reset
        break;
      default:
        console.log(`⚠️ Unhandled action: ${action}`);
    }
  }

  /**
   * Log interaction to file
   */
  logInteraction(userId, username, type, payload, result) {
    const logEntry = {
      timestamp: new Date().toISOString(),
      userId,
      username,
      type,
      payload,
      result
    };
    
    const logLine = JSON.stringify(logEntry) + '\n';
    
    try {
      fs.appendFileSync(this.logFile, logLine);
    } catch (error) {
      console.error('Failed to write log:', error.message);
    }
    
    // Also log to console
    this.helper.logInteraction(userId, username, type, payload, result);
  }

  /**
   * Start the callback polling service
   */
  start() {
    console.log('🚀 Starting Telegram Callback Handler...');
    console.log(`📊 Registered handlers: ${Array.from(this.handlers.keys()).join(', ')}`);
    
    // Start polling for callbacks
    this.helper.startPolling(async (callbackQuery) => {
      await this.processCallback(callbackQuery);
    }, 1000);
  }

  /**
   * Stop the service
   */
  stop() {
    console.log('🛑 Stopping Telegram Callback Handler...');
    this.helper.stopPolling();
  }
}

module.exports = CallbackHandler;
