const helper = require('./telegram_button_helper');

async function handle() {
  console.log('Handling quiz_again_yes callback...');
  
  // Poll for the callback
  let lastUpdateId = 0;
  const startTime = Date.now();
  
  while (Date.now() - startTime < 10000) {
    const updates = await helper.pollUpdates(lastUpdateId);
    
    if (updates.ok && updates.result.length > 0) {
      for (const update of updates.result) {
        lastUpdateId = update.update_id + 1;
        
        if (update.callback_query && update.callback_query.data === 'quiz_again_yes') {
          console.log('Found quiz_again_yes callback!');
          const result = await helper.handleCallback(update.callback_query);
          console.log('Result:', result);
          return;
        }
      }
    }
    await new Promise(r => setTimeout(r, 500));
  }
  
  console.log('Timeout waiting for callback');
}

handle();
