const https = require('https');

const botToken = '7971019788:AAE-XzCbpoIS3Z8JN9d2PwdC4hbvATgiyYg';
const chatId = '5597932516';

const message = {
  chat_id: chatId,
  text: '🧪 BUTTON TEST #2',
  reply_markup: {
    inline_keyboard: [
      [
        { text: '🔴 Red', callback_data: 'red' },
        { text: '🔵 Blue', callback_data: 'blue' }
      ]
    ]
  }
};

const data = JSON.stringify(message);

console.log('Sending:', data);

const options = {
  hostname: 'api.telegram.org',
  port: 443,
  path: `/bot${botToken}/sendMessage`,
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(data)
  }
};

const req = https.request(options, (res) => {
  let body = '';
  res.on('data', (chunk) => body += chunk);
  res.on('end', () => {
    console.log('\nFull response:', body);
    const result = JSON.parse(body);
    if (result.ok) {
      console.log('\n✅ Success!');
      console.log('Message has reply_markup:', !!result.result.reply_markup);
    } else {
      console.log('\n❌ Error:', result.description);
    }
  });
});

req.on('error', (e) => console.error('Error:', e));
req.write(data);
req.end();
