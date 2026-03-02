const https = require('https');

const botToken = '7971019788:AAE-XzCbpoIS3Z8JN9d2PwdC4hbvATgiyYg';
const chatId = '5597932516';

// Send message with buttons
function sendWithButtons(text, buttons) {
  return new Promise((resolve, reject) => {
    const message = {
      chat_id: chatId,
      text: text,
      reply_markup: {
        inline_keyboard: buttons
      }
    };

    const data = JSON.stringify(message);
    const options = {
      hostname: 'api.telegram.org',
      path: `/bot${botToken}/sendMessage`,
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) }
    };

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', (c) => body += c);
      res.on('end', () => resolve(JSON.parse(body)));
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

// Answer callback query
function answerCallback(callbackQueryId, text, showAlert = false) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      callback_query_id: callbackQueryId,
      text: text,
      show_alert: showAlert
    });

    const options = {
      hostname: 'api.telegram.org',
      path: `/bot${botToken}/answerCallbackQuery`,
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) }
    };

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', (c) => body += c);
      res.on('end', () => resolve(JSON.parse(body)));
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

// Get updates (poll for callbacks)
function getUpdates(offset = 0) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'api.telegram.org',
      path: `/bot${botToken}/getUpdates?offset=${offset}&timeout=1`,
      method: 'GET'
    };

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', (c) => body += c);
      res.on('end', () => resolve(JSON.parse(body)));
    });
    req.on('error', reject);
    req.end();
  });
}

// Main test
async function main() {
  // Send buttons
  console.log('Sending message with buttons...');
  const result = await sendWithButtons('🧪 Click a button!', [
    [
      { text: '🔴 Red', callback_data: 'color_red' },
      { text: '🔵 Blue', callback_data: 'color_blue' }
    ],
    [
      { text: '🟢 Green', callback_data: 'color_green' }
    ]
  ]);
  
  if (result.ok) {
    console.log('✅ Sent! Message ID:', result.result.message_id);
    console.log('Waiting for button click...');
  } else {
    console.log('❌ Error:', result.description);
    return;
  }

  // Poll for updates
  let lastUpdateId = 0;
  let attempts = 0;
  const maxAttempts = 60; // 60 seconds
  
  while (attempts < maxAttempts) {
    const updates = await getUpdates(lastUpdateId);
    
    if (updates.ok && updates.result.length > 0) {
      for (const update of updates.result) {
        lastUpdateId = update.update_id + 1;
        
        if (update.callback_query) {
          const cq = update.callback_query;
          console.log('\n🔔 CALLBACK RECEIVED!');
          console.log('   From:', cq.from.username || cq.from.first_name);
          console.log('   Data:', cq.callback_data);
          console.log('   Full callback:', JSON.stringify(cq, null, 2));
          
          // Answer the callback
          const colorRaw = cq.callback_data || 'unknown';
          const color = colorRaw.replace('color_', '').toUpperCase();
          await answerCallback(cq.id, `You chose ${color}! 🎨`);
          console.log('   Answered!');
          
          // Send follow-up message
          await sendWithButtons(`✅ You selected: ${color}\n\nWant to try again?`, [
            [
              { text: '🔄 Yes', callback_data: 'again_yes' },
              { text: '❌ No', callback_data: 'again_no' }
            ]
          ]);
          
          return;
        }
      }
    }
    
    await new Promise(r => setTimeout(r, 1000));
    attempts++;
    process.stdout.write('.');
  }
  
  console.log('\n⏱️ Timeout - no callback received');
}

main().catch(console.error);
