/**
 * Example Usage of Telegram Button Helper
 * Demonstrates how to create buttons, quizzes, and menus programmatically
 */

const TelegramButtonHelper = require('../../telegram_button_helper');

// Initialize with your bot token
const BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE';
const helper = new TelegramButtonHelper(BOT_TOKEN);

// Example chat ID (replace with actual chat ID)
const CHAT_ID = 123456789;

/**
 * Example 1: Send a simple confirmation
 */
async function sendConfirmation() {
  console.log('Example 1: Sending confirmation...');
  
  const keyboard = helper.createConfirmation('delete_message', { itemId: 123 });
  
  await helper.sendMessage(
    CHAT_ID,
    '⚠️ *Confirm Action*\n\nAre you sure you want to delete this item?',
    keyboard
  );
  
  console.log('✅ Confirmation sent!\n');
}

/**
 * Example 2: Send a quiz question
 */
async function sendQuizQuestion() {
  console.log('Example 2: Sending quiz question...');
  
  const questionId = 'example_q1';
  const options = ['London', 'Berlin', 'Paris', 'Madrid'];
  
  const keyboard = helper.createQuizButtons(questionId, options);
  
  await helper.sendMessage(
    CHAT_ID,
    '📝 *Quiz Time!*\n\nWhat is the capital of France?',
    keyboard
  );
  
  console.log('✅ Quiz question sent!\n');
}

/**
 * Example 3: Send a custom menu
 */
async function sendMenu() {
  console.log('Example 3: Sending menu...');
  
  const menuItems = [
    { label: '📊 View Stats', action: 'view_stats' },
    { label: '⚙️ Settings', action: 'settings' },
    { label: '❓ Help', action: 'help' }
  ];
  
  const keyboard = helper.createMenu(menuItems, 'main');
  
  await helper.sendMessage(
    CHAT_ID,
    '🏠 *Main Menu*\n\nChoose an option:',
    keyboard
  );
  
  console.log('✅ Menu sent!\n');
}

/**
 * Example 4: Custom inline buttons
 */
async function sendCustomButtons() {
  console.log('Example 4: Sending custom buttons...');
  
  const keyboard = helper.createKeyboard(
    helper.createRow(
      helper.createButton('🔴 Red', helper.encodeCallback('color', { color: 'red' })),
      helper.createButton('🟢 Green', helper.encodeCallback('color', { color: 'green' })),
      helper.createButton('🔵 Blue', helper.encodeCallback('color', { color: 'blue' }))
    ),
    helper.createRow(
      helper.createButton('🎨 Choose Custom Color', helper.encodeCallback('color', { custom: true }))
    )
  );
  
  await helper.sendMessage(
    CHAT_ID,
    '🎨 *Color Picker*\n\nSelect your favorite color:',
    keyboard
  );
  
  console.log('✅ Custom buttons sent!\n');
}

/**
 * Example 5: URL buttons
 */
async function sendUrlButtons() {
  console.log('Example 5: Sending URL buttons...');
  
  const keyboard = helper.createKeyboard(
    helper.createRow(
      helper.createButton('📖 Documentation', '', { url: 'https://core.telegram.org/bots/api' })
    ),
    helper.createRow(
      helper.createButton('💻 GitHub', '', { url: 'https://github.com' })
    )
  );
  
  await helper.sendMessage(
    CHAT_ID,
    '🔗 *Useful Links*\n\nClick to open:',
    keyboard
  );
  
  console.log('✅ URL buttons sent!\n');
}

/**
 * Example 6: Polling for callbacks
 */
function startPollingExample() {
  console.log('Example 6: Starting callback polling...\n');
  
  helper.startPolling(async (callbackQuery) => {
    const { id, from, data } = callbackQuery;
    const decoded = helper.decodeCallback(data);
    
    console.log(`📩 Callback from ${from.username || from.first_name}:`);
    console.log(`   Type: ${decoded.type}`);
    console.log(`   Payload:`, decoded.payload);
    
    // Answer the callback
    await helper.answerCallback(id, {
      text: `Received: ${decoded.type}`,
      cacheTime: 5
    });
    
    // Log the interaction
    helper.logInteraction(
      from.id,
      from.username,
      decoded.type,
      decoded.payload,
      'processed'
    );
  }, 2000);
  
  console.log('✅ Polling started! Press Ctrl+C to stop.\n');
}

/**
 * Run all examples
 */
async function runExamples() {
  try {
    console.log('🤖 Telegram Button Helper Examples\n');
    console.log('================================\n');
    
    // Note: These require a valid BOT_TOKEN and CHAT_ID
    // Uncomment the ones you want to test:
    
    // await sendConfirmation();
    // await sendQuizQuestion();
    // await sendMenu();
    // await sendCustomButtons();
    // await sendUrlButtons();
    
    // Start polling (this will run indefinitely)
    // startPollingExample();
    
    console.log('✨ Examples ready!');
    console.log('📝 Uncomment the example functions you want to run.');
    console.log('⚠️  Remember to set BOT_TOKEN and CHAT_ID first.\n');
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

// Export for use as module
module.exports = {
  sendConfirmation,
  sendQuizQuestion,
  sendMenu,
  sendCustomButtons,
  sendUrlButtons,
  startPollingExample
};

// Run if executed directly
if (require.main === module) {
  runExamples();
}
