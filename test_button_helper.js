const { sendQuiz, pollUpdates, handleCallback } = require('./telegram_button_helper');

async function test() {
  console.log('🧪 Testing Telegram Button Helper\n');
  
  // Send a quiz
  console.log('Sending quiz...');
  const { message, quizId } = await sendQuiz(
    'What is the capital of France?',
    ['Paris', 'London', 'Berlin', 'Madrid'],
    0  // Paris is correct (index 0)
  );
  console.log(`✅ Quiz sent! Message ID: ${message.message_id}, Quiz ID: ${quizId}`);
  
  // Poll for callbacks
  console.log('\nWaiting for button click (30 seconds)...\n');
  
  let lastUpdateId = 0;
  let handled = false;
  const startTime = Date.now();
  
  while (!handled && Date.now() - startTime < 30000) {
    const updates = await pollUpdates(lastUpdateId);
    
    if (updates.ok && updates.result.length > 0) {
      for (const update of updates.result) {
        lastUpdateId = update.update_id + 1;
        
        if (update.callback_query) {
          console.log('\n🔔 Callback received!');
          console.log('   Data:', update.callback_query.data);
          
          const result = await handleCallback(update.callback_query);
          console.log('   Result:', result);
          handled = true;
        }
      }
    }
    
    if (!handled) {
      process.stdout.write('.');
      await new Promise(r => setTimeout(r, 1000));
    }
  }
  
  if (handled) {
    console.log('\n✅ Test complete!');
  } else {
    console.log('\n⏱ Timeout - no button clicked');
  }
}

test().catch(console.error);
