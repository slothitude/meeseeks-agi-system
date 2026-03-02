/**
 * Telegram Button Helper
 * Main module for creating and managing inline buttons
 */

const CallbackHandler = require('./hooks/telegram-buttons/callback-handler');
const QuizHandler = require('./hooks/telegram-buttons/quiz-handler');

class TelegramButtonHelper {
  constructor(botToken, options = {}) {
    this.callbackHandler = new CallbackHandler(
      botToken,
      options.configPath || './hooks/telegram-buttons/config.json'
    );
  }

  /**
   * Start listening for button callbacks
   */
  start() {
    this.callbackHandler.startPolling();
    console.log('🦥 Telegram Button Helper started');
  }

  /**
   * Stop listening
   */
  stop() {
    this.callbackHandler.stopPolling();
  }

  /**
   * Create a quiz with inline buttons
   */
  createQuiz(question, options, correctAnswerIndex) {
    const questionId = `quiz_${Date.now()}`;
    return QuizHandler.buildQuizMessage(question, options, questionId, correctAnswerIndex);
  }

  /**
   * Create confirmation buttons (Yes/No)
   */
  createConfirmation(promptText, options = {}) {
    const buttons = [
      [
        { text: '✅ Yes', callback_data: `confirm:{"action":"yes","updateMessage":${options.updateMessage || false}}` },
        { text: '❌ No', callback_data: `confirm:{"action":"no","updateMessage":${options.updateMessage || false}}` }
      ]
    ];

    return {
      text: promptText,
      reply_markup: { inline_keyboard: buttons }
    };
  }

  /**
   * Create menu navigation buttons
   */
  createMenu(menuId, options = {}) {
    const buttons = options.buttons || [
      [
        { text: '📋 Option 1', callback_data: `menu:{"menuId":"option1"}` },
        { text: '📋 Option 2', callback_data: `menu:{"menuId":"option2"}` }
      ],
      [
        { text: '◀️ Back', callback_data: `menu:{"menuId":"back"}` }
      ]
    ];

    return {
      text: options.text || `📍 Menu: ${menuId}`,
      reply_markup: { inline_keyboard: buttons }
    };
  }

  /**
   * Register custom callback handler
   */
  on(callbackType, handler) {
    this.callbackHandler.registerHandler(callbackType, handler);
  }

  /**
   * Send message with inline buttons (requires Telegram API)
   */
  async sendMessageWithButtons(chatId, text, buttons) {
    return await this.callbackHandler.apiRequest('sendMessage', {
      chat_id: chatId,
      text: text,
      parse_mode: 'Markdown',
      reply_markup: { inline_keyboard: buttons }
    });
  }
}

// Export both the helper and handlers
module.exports = TelegramButtonHelper;
module.exports.CallbackHandler = CallbackHandler;
module.exports.QuizHandler = QuizHandler;

// Example usage
if (require.main === module) {
  // Demo mode - shows how to use the module
  console.log('🥒 Telegram Button Helper - Demo Mode\n');
  
  console.log('Usage:');
  console.log('-----');
  console.log(`
const TelegramButtonHelper = require('./telegram_button_helper');

// Initialize with your bot token
const helper = new TelegramButtonHelper('YOUR_BOT_TOKEN');

// Start listening for callbacks
helper.start();

// Create a quiz
const quiz = helper.createQuiz(
  'What is 2 + 2?',
  ['3', '4', '5', '6'],
  1  // Correct answer is index 1 (4)
);

// Create confirmation
const confirm = helper.createConfirmation('Are you sure?');

// Create menu
const menu = helper.createMenu('main', {
  buttons: [
    [{ text: '📊 Stats', callback_data: 'menu:{"menuId":"stats"}' }],
    [{ text: '⚙️ Settings', callback_data: 'menu:{"menuId":"settings"}' }],
    [{ text: '❓ Help', callback_data: 'menu:{"menuId":"help"}' }]
  ]
});

// Register custom handler
helper.on('custom', async (callback, data) => {
  console.log('Custom handler called:', data);
  return { handled: true };
});
  `);

  console.log('\n✅ Module ready! See usage example above.');
}
