const https = require('https');

const botToken = '7971019788:AAE-XzCbpoIS3Z8JN9d2PwdC4hbvATgiyYg';
const chatId = '5597932516';

const message = {
  chat_id: chatId,
  text: '🧪 DIRECT API TEST: Do you see buttons now?',
  parse_mode: 'Markdown',
  reply_markup: JSON.stringify({
    inline_keyboard: [
      [
        { text: '✅ YES', callback_data: 'yes' },
        { text: '❌ NO', callback_data: 'no' }
      ],
      [
        { text: '🤔 MAYBE', callback_data: 'maybe' }
      ]
    ]
  })
};

const data = JSON.stringify(message);

const options = {
  hostname: 'api.telegram.org',
  port: 443,
  path: `/bot${botToken}/sendMessage`,
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': data.length
  }
};

console.log('Sending directly to Telegram API...');

const req = https.request(options, (res) => {
  let body = '';
  res.on('data', (chunk) => body += chunk);
  res.on('end', () => {
    console.log('Response:', body);
    const result = JSON.parse(body);
    if (result.ok) {
      console.log('✅ Message sent! Message ID:', result.result.message_id);
    } else {
      console.log('❌ Error:', result.description);
    }
  });
});

req.on('error', (e) => console.error('Error:', e));
req.write(data);
req.end();
