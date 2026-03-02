# 🚀 Quick Setup Guide

## 1. Get Your Bot Token

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow the instructions
3. Copy your bot token (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

## 2. Configure the System

Edit `config.json` and replace `YOUR_BOT_TOKEN_HERE`:

```json
{
  "botToken": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
  ...
}
```

## 3. Get Your Chat ID

1. Start a chat with your bot
2. Send any message
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Find `"chat":{"id":123456789}` in the response
5. That number is your chat ID

## 4. Test the System

### Option A: Run as Service
```bash
cd C:\Users\aaron\.openclaw\workspace\hooks\telegram-buttons
node index.js
```

### Option B: Use Programmatically
```javascript
const TelegramButtonHelper = require('../../telegram_button_helper');
const helper = new TelegramButtonHelper('YOUR_BOT_TOKEN');

// Send a test message with buttons
const keyboard = helper.createConfirmation('test', { foo: 'bar' });
await helper.sendMessage(CHAT_ID, 'Test message with buttons!', keyboard);
```

## 5. Send Your First Quiz

```javascript
const helper = new TelegramButtonHelper('YOUR_BOT_TOKEN');

const options = ['Paris', 'London', 'Berlin', 'Madrid'];
const keyboard = helper.createQuizButtons('capitals_q1', options);

await helper.sendMessage(
  YOUR_CHAT_ID,
  '❓ What is the capital of France?',
  keyboard
);
```

## 6. Start Handling Callbacks

```bash
node index.js
```

Now when users click buttons, the handler will:
- ✅ Process the callback
- 📝 Log the interaction
- 💬 Respond appropriately

## Troubleshooting

### "Bot token not configured"
→ Edit `config.json` and set your actual bot token

### "Chat not found"
→ Make sure you've started a conversation with your bot first

### "Unauthorized"
→ Verify your bot token is correct

### "No updates received"
→ Click a button in your bot, then check the console

## Next Steps

- Add custom quiz questions to `config.json`
- Create custom menu structures
- Register custom callback handlers
- Integrate with your existing bot logic

See `README.md` for full documentation.
