/**
 * Integration Example
 * Shows how to integrate the button hooks system with an existing Telegram bot
 */

// Example 1: Standalone Service
// =============================

/*
 * Run as a standalone service:
 * 
 * $ node index.js
 * 
 * This will start polling for callback queries and handle them automatically.
 */

// Example 2: Integration with Existing Bot
// =========================================

const TelegramButtonHelper = require('../../telegram_button_helper');

class MyBot {
  constructor(botToken) {
    this.helper = new TelegramButtonHelper(botToken);
    this.setupHandlers();
  }

  setupHandlers() {
    // Register custom callback handlers
    this.customHandlers = new Map();
    
    // Example: Handle color selection
    this.customHandlers.set('color', async (data) => {
      const { userId, chatId, payload } = data;
      const color = payload.color;
      
      await this.helper.sendMessage(
        chatId,
        `🎨 You selected: *${color}*`
      );
      
      return 'color_selected';
    });
  }

  async handleCommand(chatId, command) {
    switch (command) {
      case '/start':
        await this.sendWelcomeMenu(chatId);
        break;
      
      case '/quiz':
        await this.sendQuiz(chatId);
        break;
      
      case '/confirm':
        await this.sendConfirmation(chatId);
        break;
      
      default:
        await this.helper.sendMessage(chatId, 'Unknown command');
    }
  }

  async sendWelcomeMenu(chatId) {
    const menuItems = [
      { label: '📝 Take Quiz', action: 'quiz' },
      { label: 'ℹ️ Information', action: 'info' },
      { label: '⚙️ Settings', action: 'settings' }
    ];
    
    const keyboard = this.helper.createMenu(menuItems);
    
    await this.helper.sendMessage(
      chatId,
      '👋 *Welcome!*\n\nChoose an option:',
      keyboard
    );
  }

  async sendQuiz(chatId) {
    const question = 'What is 2 + 2?';
    const options = ['3', '4', '5', '6'];
    
    const keyboard = this.helper.createQuizButtons('math_q1', options);
    
    await this.helper.sendMessage(
      chatId,
      `❓ *Quiz Question*\n\n${question}`,
      keyboard
    );
  }

  async sendConfirmation(chatId) {
    const keyboard = this.helper.createConfirmation('test_action', { 
      timestamp: Date.now() 
    });
    
    await this.helper.sendMessage(
      chatId,
      '⚠️ *Test Confirmation*\n\nDo you want to proceed?',
      keyboard
    );
  }

  // Start handling callbacks
  startCallbackHandler() {
    console.log('🎧 Starting callback handler...');
    
    this.helper.startPolling(async (callbackQuery) => {
      const { id, from, message, data } = callbackQuery;
      const decoded = this.helper.decodeCallback(data);
      
      console.log(`📩 Callback: ${decoded.type} from ${from.username}`);
      
      // Check for custom handler
      const customHandler = this.customHandlers.get(decoded.type);
      
      if (customHandler) {
        const result = await customHandler({
          userId: from.id,
          username: from.username,
          chatId: message.chat.id,
          messageId: message.message_id,
          payload: decoded.payload
        });
        
        await this.helper.answerCallback(id, {
          text: '✅ Processed'
        });
        
        return;
      }
      
      // Default handling for standard types
      switch (decoded.type) {
        case 'confirm':
          await this.handleConfirmation(callbackQuery, decoded);
          break;
        
        case 'quiz_answer':
          await this.handleQuizAnswer(callbackQuery, decoded);
          break;
        
        case 'menu':
          await this.handleMenu(callbackQuery, decoded);
          break;
        
        default:
          console.log(`⚠️ Unhandled callback type: ${decoded.type}`);
          await this.helper.answerCallback(id);
      }
    });
  }

  async handleConfirmation(callbackQuery, decoded) {
    const { id, from, message } = callbackQuery;
    const { action, value } = decoded.payload;
    
    await this.helper.answerCallback(id, {
      text: value ? '✅ Confirmed' : '❌ Cancelled'
    });
    
    const text = value 
      ? `✅ *Confirmed*\nAction: ${action}`
      : `❌ *Cancelled*\nAction: ${action}`;
    
    await this.helper.editMessage(
      message.chat.id,
      message.message_id,
      text
    );
  }

  async handleQuizAnswer(callbackQuery, decoded) {
    const { id, from, message } = callbackQuery;
    const { questionId, optionIndex } = decoded.payload;
    
    // In real implementation, check against correct answer
    const isCorrect = optionIndex === 1; // Example: index 1 is correct
    
    await this.helper.answerCallback(id, {
      text: isCorrect ? '✅ Correct!' : '❌ Incorrect',
      showAlert: true
    });
    
    const resultEmoji = isCorrect ? '✅' : '❌';
    await this.helper.editMessage(
      message.chat.id,
      message.message_id,
      `${resultEmoji} You answered: Option ${optionIndex + 1}`
    );
  }

  async handleMenu(callbackQuery, decoded) {
    const { id, message } = callbackQuery;
    const { action } = decoded.payload;
    
    await this.helper.answerCallback(id);
    
    // Navigate to selected menu
    await this.handleCommand(message.chat.id, `/${action}`);
  }
}

// Example 3: Use with OpenClaw Hooks
// ===================================

/*
 * In your OpenClaw hook configuration:
 * 
 * {
 *   "name": "telegram-buttons",
 *   "type": "polling",
 *   "module": "./hooks/telegram-buttons/callback-handler",
 *   "config": {
 *     "botToken": "${TELEGRAM_BOT_TOKEN}",
 *     "quizzes": { ... },
 *     "menus": { ... }
 *   }
 * }
 */

// Example 4: Webhook Integration
// ===============================

class WebhookBot {
  constructor(botToken) {
    this.helper = new TelegramButtonHelper(botToken);
  }

  // Handle incoming webhook updates
  async handleWebhookUpdate(update) {
    if (update.callback_query) {
      await this.processCallback(update.callback_query);
    } else if (update.message) {
      await this.handleMessage(update.message);
    }
  }

  async processCallback(callbackQuery) {
    const { id, from, message, data } = callbackQuery;
    const decoded = this.helper.decodeCallback(data);
    
    // Process callback...
    console.log(`Callback: ${decoded.type}`);
    
    await this.helper.answerCallback(id);
  }

  async handleMessage(message) {
    const chatId = message.chat.id;
    const text = message.text;
    
    // Handle message...
    if (text === '/menu') {
      const keyboard = this.helper.createMenu([
        { label: 'Option 1', action: 'opt1' },
        { label: 'Option 2', action: 'opt2' }
      ]);
      
      await this.helper.sendMessage(chatId, 'Menu:', keyboard);
    }
  }
}

// Export examples
module.exports = {
  MyBot,
  WebhookBot
};

// Usage example
/*
const bot = new MyBot('YOUR_BOT_TOKEN');
bot.startCallbackHandler();

// Send a message with buttons
bot.sendQuiz(123456789);
*/
