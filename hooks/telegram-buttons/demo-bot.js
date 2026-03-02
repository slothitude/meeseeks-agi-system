/**
 * Complete Working Bot Example
 * Demonstrates a fully functional bot with interactive buttons
 * 
 * Usage:
 * 1. Set your bot token below
 * 2. Run: node demo-bot.js
 * 3. Send /start to your bot
 */

const TelegramButtonHelper = require('../../telegram_button_helper');

// ⚠️ REPLACE WITH YOUR ACTUAL BOT TOKEN
const BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE';

// Create helper instance
const helper = new TelegramButtonHelper(BOT_TOKEN);

// Track which users have started the bot
const activeUsers = new Set();

// Sample quiz data
const quizzes = {
  geography: {
    current: 0,
    questions: [
      {
        id: 'geo_1',
        question: 'What is the capital of France?',
        options: ['London', 'Berlin', 'Paris', 'Madrid'],
        correct: 2
      },
      {
        id: 'geo_2',
        question: 'What is the capital of Japan?',
        options: ['Seoul', 'Tokyo', 'Beijing', 'Bangkok'],
        correct: 1
      },
      {
        id: 'geo_3',
        question: 'What is the capital of Australia?',
        options: ['Sydney', 'Melbourne', 'Canberra', 'Brisbane'],
        correct: 2
      }
    ]
  }
};

// User progress tracking
const userProgress = new Map();

/**
 * Handle incoming messages
 */
async function handleMessage(message) {
  const chatId = message.chat.id;
  const text = message.text;
  const userId = message.from.id;
  
  console.log(`📩 Message from ${message.from.username || message.from.first_name}: ${text}`);
  
  // Track active users
  activeUsers.add(userId);
  
  switch (text) {
    case '/start':
      await sendWelcome(chatId);
      break;
    
    case '/menu':
      await sendMainMenu(chatId);
      break;
    
    case '/quiz':
      await startQuiz(chatId, userId);
      break;
    
    case '/confirm':
      await sendTestConfirmation(chatId);
      break;
    
    case '/help':
      await sendHelp(chatId);
      break;
    
    default:
      await helper.sendMessage(chatId, '🤔 Unknown command. Try /help');
  }
}

/**
 * Send welcome message
 */
async function sendWelcome(chatId) {
  const text = `👋 *Welcome to the Button Demo Bot!*

I can demonstrate different types of interactive buttons:

• 📝 Quizzes with feedback
• ✅ Confirmations (Yes/No)
• 🍽️ Menu navigation
• 🎨 Custom buttons

Tap the buttons below or use these commands:
/menu - Main menu
/quiz - Take a quiz
/confirm - Test confirmation
/help - Get help`;

  const keyboard = helper.createMenu([
    { label: '📝 Take Quiz', action: 'start_quiz' },
    { label: '🍽️ Open Menu', action: 'main_menu' },
    { label: 'ℹ️ Help', action: 'help' }
  ]);
  
  await helper.sendMessage(chatId, text, keyboard);
}

/**
 * Send main menu
 */
async function sendMainMenu(chatId) {
  const text = '🏠 *Main Menu*\n\nChoose an option:';
  
  const keyboard = helper.createKeyboard(
    helper.createRow(
      helper.createButton('📊 My Stats', helper.encodeCallback('menu', { action: 'stats' })),
      helper.createButton('⚙️ Settings', helper.encodeCallback('menu', { action: 'settings' }))
    ),
    helper.createRow(
      helper.createButton('📝 Start Quiz', helper.encodeCallback('menu', { action: 'start_quiz' }))
    ),
    helper.createRow(
      helper.createButton('❓ Help', helper.encodeCallback('menu', { action: 'help' }))
    )
  );
  
  await helper.sendMessage(chatId, text, keyboard);
}

/**
 * Start quiz
 */
async function startQuiz(chatId, userId) {
  // Initialize progress
  userProgress.set(userId, {
    quiz: 'geography',
    current: 0,
    score: 0,
    total: 0
  });
  
  await sendQuizQuestion(chatId, userId);
}

/**
 * Send quiz question
 */
async function sendQuizQuestion(chatId, userId) {
  const progress = userProgress.get(userId);
  const quiz = quizzes[progress.quiz];
  const question = quiz.questions[progress.current];
  
  const text = `📝 *Quiz Question ${progress.current + 1}/${quiz.questions.length}*\n\n${question.question}`;
  const keyboard = helper.createQuizButtons(question.id, question.options);
  
  await helper.sendMessage(chatId, text, keyboard);
}

/**
 * Send test confirmation
 */
async function sendTestConfirmation(chatId) {
  const text = '⚠️ *Test Confirmation*\n\nDo you want to proceed with this action?';
  const keyboard = helper.createConfirmation('test_action', { 
    timestamp: Date.now(),
    userId: chatId
  });
  
  await helper.sendMessage(chatId, text, keyboard);
}

/**
 * Send help
 */
async function sendHelp(chatId) {
  const text = `❓ *Help - Available Commands*

/start - Start the bot
/menu - Open main menu
/quiz - Take a geography quiz
/confirm - Test confirmation dialog
/help - Show this help

💡 *Tips:*
• Click buttons to interact
• Take quizzes to test your knowledge
• Navigate through menus`;

  await helper.sendMessage(chatId, text);
}

/**
 * Handle callback queries
 */
async function handleCallback(callbackQuery) {
  const { id, from, message, data } = callbackQuery;
  const decoded = helper.decodeCallback(data);
  const chatId = message.chat.id;
  const userId = from.id;
  
  console.log(`🔘 Callback: ${decoded.type} from ${from.username || from.first_name}`);
  
  switch (decoded.type) {
    case 'menu':
      await handleMenuCallback(id, chatId, userId, message.message_id, decoded.payload);
      break;
    
    case 'quiz_answer':
      await handleQuizAnswer(id, chatId, userId, message.message_id, decoded.payload);
      break;
    
    case 'confirm':
      await handleConfirmation(id, chatId, message.message_id, decoded.payload);
      break;
    
    default:
      await helper.answerCallback(id, { text: 'Unknown action' });
  }
}

/**
 * Handle menu callbacks
 */
async function handleMenuCallback(callbackId, chatId, userId, messageId, payload) {
  await helper.answerCallback(callbackId);
  
  switch (payload.action) {
    case 'start_quiz':
      await startQuiz(chatId, userId);
      break;
    
    case 'main_menu':
      await sendMainMenu(chatId);
      break;
    
    case 'stats':
      await sendStats(chatId, userId, messageId);
      break;
    
    case 'settings':
      await sendSettings(chatId, messageId);
      break;
    
    case 'help':
      await helper.editMessage(chatId, messageId, 
        '❓ Help is here! Use /help command for full list.');
      break;
    
    default:
      console.log(`Unknown menu action: ${payload.action}`);
  }
}

/**
 * Handle quiz answer
 */
async function handleQuizAnswer(callbackId, chatId, userId, messageId, payload) {
  const progress = userProgress.get(userId);
  
  if (!progress) {
    await helper.answerCallback(callbackId, { 
      text: '⚠️ No active quiz. Start with /quiz',
      showAlert: true
    });
    return;
  }
  
  const quiz = quizzes[progress.quiz];
  const question = quiz.questions[progress.current];
  const isCorrect = payload.optionIndex === question.correct;
  
  // Update score
  progress.total++;
  if (isCorrect) progress.score++;
  
  // Provide feedback
  const feedback = isCorrect 
    ? '✅ Correct!' 
    : `❌ Incorrect. The answer was: ${question.options[question.correct]}`;
  
  await helper.answerCallback(callbackId, {
    text: feedback,
    showAlert: true
  });
  
  // Update message
  const resultEmoji = isCorrect ? '✅' : '❌';
  const chosenAnswer = question.options[payload.optionIndex];
  
  await helper.editMessage(chatId, messageId,
    `${resultEmoji} *Question ${progress.current + 1}*\n\n` +
    `Your answer: ${chosenAnswer}\n` +
    `Result: ${isCorrect ? 'Correct!' : 'Incorrect'}`
  );
  
  // Next question or finish
  progress.current++;
  
  if (progress.current < quiz.questions.length) {
    setTimeout(() => sendQuizQuestion(chatId, userId), 1500);
  } else {
    setTimeout(() => finishQuiz(chatId, userId), 1500);
  }
}

/**
 * Finish quiz and show results
 */
async function finishQuiz(chatId, userId) {
  const progress = userProgress.get(userId);
  const percentage = Math.round((progress.score / progress.total) * 100);
  
  let emoji = '💪';
  if (percentage === 100) emoji = '🏆';
  else if (percentage >= 80) emoji = '🎉';
  else if (percentage >= 60) emoji = '👍';
  
  const text = `📊 *Quiz Complete!*\n\n` +
    `✅ Correct: ${progress.score}/${progress.total}\n` +
    `📈 Score: ${percentage}%\n\n` +
    `${emoji} ${getPerformanceMessage(percentage)}`;
  
  const keyboard = helper.createKeyboard(
    helper.createRow(
      helper.createButton('🔄 Try Again', helper.encodeCallback('menu', { action: 'start_quiz' }))
    ),
    helper.createRow(
      helper.createButton('🏠 Main Menu', helper.encodeCallback('menu', { action: 'main_menu' }))
    )
  );
  
  await helper.sendMessage(chatId, text, keyboard);
  
  // Clear progress
  userProgress.delete(userId);
}

/**
 * Get performance message
 */
function getPerformanceMessage(percentage) {
  if (percentage === 100) return 'Perfect score! Outstanding!';
  if (percentage >= 80) return 'Great job! Excellent work!';
  if (percentage >= 60) return 'Good effort! Keep practicing!';
  if (percentage >= 40) return 'Not bad, but room for improvement.';
  return 'Keep studying, you\'ll get better!';
}

/**
 * Handle confirmation
 */
async function handleConfirmation(callbackId, chatId, messageId, payload) {
  const { action, value } = payload;
  
  await helper.answerCallback(callbackId, {
    text: value ? '✅ Confirmed!' : '❌ Cancelled',
    cacheTime: 5
  });
  
  const text = value
    ? `✅ *Confirmed*\n\nAction: ${action}\nStatus: Completed\nTime: ${new Date().toLocaleString()}`
    : `❌ *Cancelled*\n\nAction: ${action}\nStatus: Cancelled`;
  
  await helper.editMessage(chatId, messageId, text);
}

/**
 * Send stats
 */
async function sendStats(chatId, userId, messageId) {
  const text = `📊 *Your Stats*\n\n` +
    `🆔 User ID: ${userId}\n` +
    `📅 Active: Yes\n` +
    `📝 Quizzes: Available\n\n` +
    `Use /quiz to test your knowledge!`;
  
  await helper.editMessage(chatId, messageId, text);
}

/**
 * Send settings
 */
async function sendSettings(chatId, messageId) {
  const keyboard = helper.createKeyboard(
    helper.createRow(
      helper.createButton('🔔 Notifications', helper.encodeCallback('menu', { action: 'notifications' }))
    ),
    helper.createRow(
      helper.createButton('🌐 Language', helper.encodeCallback('menu', { action: 'language' }))
    ),
    helper.createRow(
      helper.createButton('⬅️ Back', helper.encodeCallback('menu', { action: 'main_menu' }))
    )
  );
  
  await helper.editMessage(chatId, messageId, '⚙️ *Settings*\n\nConfigure your preferences:', keyboard);
}

/**
 * Main polling loop
 */
async function startBot() {
  console.log('🤖 Demo Bot Starting...\n');
  console.log('⚠️  Make sure to set your BOT_TOKEN at the top of this file!\n');
  
  if (BOT_TOKEN === 'YOUR_BOT_TOKEN_HERE') {
    console.error('❌ Please set your bot token!');
    process.exit(1);
  }
  
  console.log('✅ Bot started!');
  console.log('📢 Send /start to your bot to begin\n');
  console.log('🔄 Listening for messages and callbacks...\n');
  
  // Start polling for both messages and callbacks
  let lastUpdateId = 0;
  
  while (true) {
    try {
      const params = {
        timeout: 30,
        allowed_updates: ['message', 'callback_query']
      };
      
      if (lastUpdateId > 0) {
        params.offset = lastUpdateId + 1;
      }
      
      const updates = await helper.apiRequest('getUpdates', params);
      
      for (const update of updates) {
        lastUpdateId = update.update_id;
        
        if (update.message) {
          await handleMessage(update.message);
        } else if (update.callback_query) {
          await handleCallback(update.callback_query);
        }
      }
    } catch (error) {
      console.error('❌ Polling error:', error.message);
      await new Promise(resolve => setTimeout(resolve, 5000));
    }
  }
}

// Handle shutdown
process.on('SIGINT', () => {
  console.log('\n👋 Bot shutting down...');
  process.exit(0);
});

// Start the bot
startBot();
