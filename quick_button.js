const https = require('https');

const BOT_TOKEN = '7971019788:AAE-XzCbpoIS3Z8JN9d2PwdC4hbvATgiyYg';
const CHAT_ID = '5597932516';

const buttons = {
  inline_keyboard: [
    [
      { text: '🔴 Red', callback_data: 'color:red' },
      { text: '🔵 Blue', callback_data: 'color:blue' }
    ],
    [
      { text: '🟢 Green', callback_data: 'color:green' },
      { text: '🟡 Yellow', callback_data: 'color:yellow' }
    ]
  ]
};

const message = {
  chat_id: CHAT_ID,
  text: '🎨 *Pick a color!*\n\nClick a button below:',
  parse_mode: 'Markdown',
  reply_markup: JSON.stringify(buttons)
};

const postData = JSON.stringify(message);

const options = {
  hostname: 'api.telegram.org',
  path: `/bot${BOT_TOKEN}/sendMessage`,
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(postData)
  }
};

const req = https.request(options, (res) => {
  let data = '';
  res.on('data', (chunk) => { data += chunk; });
  res.on('end', () => {
    const result = JSON.parse(data);
    if (result.ok) {
      console.log('✅ Buttons sent! Message ID:', result.result.message_id);
      console.log('📱 Check your Telegram!');
    } else {
      console.error('❌ Error:', result.description);
    }
  });
});

req.on('error', (e) => {
  console.error('❌ Request failed:', e.message);
});

req.write(postData);
req.end();
