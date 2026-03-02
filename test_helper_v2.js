const TelegramButtonHelper = require('./telegram_button_helper');

const BOT_TOKEN = '7971019788:AAE-XzCbpoIS3Z8JN9d2PwdC4hbvATgiyYg';
const CHAT_ID = '5597932516';

async function test() {
  const helper = new TelegramButtonHelper(BOT_TOKEN);
  
  console.log('🧪 Testing Telegram Button Helper\n');
  
  // Create keyboard
  const keyboard = {
    inline_keyboard: [
    [
      { text: '🔴 Red', callback_data: 'color_red' },
      { text: '🔵 Blue', callback_data: 'color_blue' }
    ],
    [
      { text: '🟢 Green', callback_data: 'color_green' }
    ]
  ]
  };
  
  // Send message with buttons
  console.log('Sending message with buttons...');
  const result = await helper.sendMessage(CHAT_ID, '🧪 *Button Test*\n\nClick a color!', JSON.stringify(keyboard));
  console.log(`✅ Sent! Message ID: ${result.message_id}`);
  
  // Start polling for callbacks
  console.log('\nWaiting for button click (30 seconds)...\n');
  
  let handled = false;
  const startTime = Date.now();
  
  const pollHandler = async (callbackQuery) => {
    console.log('\n🔔 Callback received!');
    console.log('   From:', callbackQuery.from.username || callbackQuery.from.first_name);
    console.log('   Data:', callbackQuery.data);
    
    // Answer the callback
    await helper.answerCallback(callbackQuery.id, {
      text: `You clicked: ${callbackQuery.data.replace('color_', '').toUpperCase()}! 🎨`
      cacheTime: 5
    });
    
    console.log('   Answered!');
    handled = true;
    helper.stopPolling();
  };
  
  helper.startPolling(pollHandler, 1000);
  
  // Wait for handling
  while (!handled && Date.now() - startTime < 30000) {
    await new Promise(r => setTimeout(r, 1000));
  }
  
  if (handled) {
    console.log('\n✅ Test complete!');
  } else {
    console.log('\n⏱️ Timeout - no button clicked');
  }
}

test().catch(console.error);
