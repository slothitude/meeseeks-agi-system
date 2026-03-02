# 🥒 Telegram Button Hooks System

A complete system for handling Telegram inline button callbacks with support for quizzes, confirmations, and menu navigation.

## 📁 File Structure

```
hooks/telegram-buttons/
├── callback-handler.js    # Main callback handler
├── quiz-handler.js        # Quiz-specific logic
├── config.json           # Button configurations
├── index.js              # Service entry point
├── examples.js           # Usage examples
└── README.md             # This file

telegram_button_helper.js  # Main helper module (workspace root)
```

## 🚀 Quick Start

### 1. Configure Bot Token

Edit `config.json` and set your Telegram bot token:

```json
{
  "botToken": "YOUR_ACTUAL_BOT_TOKEN_HERE",
  ...
}
```

### 2. Run as Service

```bash
cd C:\Users\aaron\.openclaw\workspace\hooks\telegram-buttons
node index.js
```

The service will start polling for callback queries automatically.

### 3. Send Interactive Messages

Use the helper module to send messages with buttons:

```javascript
const TelegramButtonHelper = require('../../telegram_button_helper');
const helper = new TelegramButtonHelper('YOUR_BOT_TOKEN');

// Send a quiz
const keyboard = helper.createQuizButtons('q1', ['Option A', 'Option B', 'Option C']);
await helper.sendMessage(chatId, '❓ What is the answer?', keyboard);
```

## 📚 Features

### 1. ✅ Confirmation Buttons (Yes/No)

Create confirmation dialogs:

```javascript
const keyboard = helper.createConfirmation('delete_item', { itemId: 123 });
await helper.sendMessage(chatId, '⚠️ Delete this item?', keyboard);
```

Result:
```
⚠️ Delete this item?

[✅ Yes] [❌ No]
```

### 2. 📝 Quiz Questions

Create interactive quizzes:

```javascript
const options = ['Paris', 'London', 'Berlin', 'Madrid'];
const keyboard = helper.createQuizButtons('geography_q1', options);
await helper.sendMessage(chatId, 'What is the capital of France?', keyboard);
```

Features:
- ✅ Correct/incorrect feedback
- 📊 Score tracking
- 📈 Progress monitoring
- 🎯 Sequential questions

### 3. 🍽️ Menu Navigation

Create hierarchical menus:

```javascript
const menuItems = [
  { label: '📊 Stats', action: 'view_stats' },
  { label: '⚙️ Settings', action: 'settings' },
  { label: '❓ Help', action: 'help' }
];
const keyboard = helper.createMenu(menuItems, 'back_to_main');
await helper.sendMessage(chatId, '🏠 Menu', keyboard);
```

### 4. 🎨 Custom Buttons

Create any button layout:

```javascript
const keyboard = helper.createKeyboard(
  helper.createRow(
    helper.createButton('Red', helper.encodeCallback('color', { color: 'red' })),
    helper.createButton('Green', helper.encodeCallback('color', { color: 'green' }))
  ),
  helper.createRow(
    helper.createButton('Blue', helper.encodeCallback('color', { color: 'blue' }))
  )
);
```

### 5. 🔗 URL Buttons

Add external links:

```javascript
const keyboard = helper.createKeyboard(
  helper.createRow(
    helper.createButton('Visit Website', '', { url: 'https://example.com' })
  )
);
```

## 🔧 Callback Handler

The `CallbackHandler` class automatically routes callbacks:

### Register Custom Handlers

```javascript
const handler = new CallbackHandler(config);

handler.registerHandler('my_custom_type', async ({ userId, payload }) => {
  console.log(`Custom action from ${userId}:`, payload);
  return 'processed';
});
```

### Built-in Handlers

- `confirm` - Yes/No confirmations
- `quiz_answer` - Quiz responses
- `menu` - Menu navigation

## 📊 Quiz Handler

The `QuizHandler` manages quiz logic:

### Define Quizzes in config.json

```json
{
  "quizzes": {
    "geography_q1": {
      "question": "Capital of France?",
      "options": ["London", "Berlin", "Paris", "Madrid"],
      "correctIndex": 2,
      "explanation": "Paris is the capital of France."
    }
  }
}
```

### Quiz Features

- **Scoring**: Tracks correct/incorrect answers
- **Feedback**: Shows explanations after answering
- **Sequences**: Chain multiple questions together
- **Results**: Display final score with performance message

## 📝 Logging

All button interactions are logged:

- **Console**: Real-time logging
- **File**: `interactions.log` in the hooks directory
- **Format**: JSON with timestamps

Log entry example:
```json
{
  "timestamp": "2026-03-03T08:30:00.000Z",
  "userId": 123456789,
  "username": "johndoe",
  "type": "quiz_answer",
  "payload": { "questionId": "q1", "optionIndex": 2 },
  "result": "correct"
}
```

## 🎯 Integration with OpenClaw

### As a Hook

Integrate with OpenClaw's hook system:

```javascript
// In your OpenClaw hook
const CallbackHandler = require('./hooks/telegram-buttons/callback-handler');

module.exports = {
  name: 'telegram-buttons',
  init: async (config) => {
    const handler = new CallbackHandler(config);
    handler.start();
    return handler;
  }
};
```

### Programmatic Usage

```javascript
const TelegramButtonHelper = require('./telegram_button_helper');
const helper = new TelegramButtonHelper(process.env.TELEGRAM_BOT_TOKEN);

// Send message with buttons
await helper.sendMessage(chatId, text, keyboard);

// Edit message
await helper.editMessage(chatId, messageId, newText, newKeyboard);

// Answer callback
await helper.answerCallback(callbackQueryId, { text: 'Done!' });
```

## 🔌 API Reference

### TelegramButtonHelper

#### Constructor
```javascript
new TelegramButtonHelper(botToken)
```

#### Methods

- `createButton(text, callbackData, options)` - Create a single button
- `createRow(...buttons)` - Create a button row
- `createKeyboard(...rows)` - Create full keyboard
- `createConfirmation(action, context)` - Create Yes/No buttons
- `createQuizButtons(questionId, options)` - Create quiz buttons
- `createMenu(items, backAction)` - Create menu buttons
- `sendMessage(chatId, text, keyboard)` - Send message
- `editMessage(chatId, messageId, text, keyboard)` - Edit message
- `answerCallback(callbackQueryId, options)` - Answer callback
- `getUpdates(timeout, allowedUpdates)` - Poll for updates
- `startPolling(handler, interval)` - Start polling loop
- `stopPolling()` - Stop polling
- `logInteraction(userId, username, type, payload, result)` - Log interaction

### CallbackHandler

#### Constructor
```javascript
new CallbackHandler(config)
```

#### Methods

- `registerHandler(type, handler)` - Register custom handler
- `processCallback(callbackQuery)` - Process incoming callback
- `start()` - Start service
- `stop()` - Stop service

### QuizHandler

#### Constructor
```javascript
new QuizHandler(helper, quizConfig)
```

#### Methods

- `handleAnswer(params)` - Handle quiz answer
- `sendQuiz(chatId, questionId)` - Send quiz question
- `resetProgress(userId)` - Reset user progress
- `getUserProgress(userId)` - Get user stats

## ⚙️ Configuration

### config.json Structure

```json
{
  "botToken": "YOUR_BOT_TOKEN",
  
  "quizzes": {
    "question_id": {
      "question": "Question text?",
      "options": ["Option 1", "Option 2"],
      "correctIndex": 0,
      "explanation": "Why this is correct"
    }
  },
  
  "menus": {
    "menu_name": {
      "text": "Menu text",
      "keyboard": { "inline_keyboard": [...] }
    }
  },
  
  "confirmations": {
    "action_name": {
      "text": "Confirmation text",
      "action": "action_to_execute"
    }
  }
}
```

## 🧪 Testing

### Test with Examples

```bash
cd hooks/telegram-buttons
node examples.js
```

### Manual Testing

1. Send a message with buttons to your bot
2. Click the buttons
3. Check console output for callback logs
4. Verify `interactions.log` file

## 🐛 Troubleshooting

### Bot not responding?
- Check bot token is correct
- Verify bot has been started with `/start`
- Check console for errors

### Buttons not working?
- Ensure callback handler is running
- Check callback_data is properly encoded
- Verify handler is registered for callback type

### Polling issues?
- Check network connectivity
- Verify bot token has correct permissions
- Look for rate limiting errors in console

## 📦 Dependencies

- Node.js 14+
- No external dependencies (uses native fetch)

## 📄 License

MIT

## 🤝 Contributing

Feel free to extend the system with:
- More callback types
- Database integration for progress tracking
- Webhook support (alternative to polling)
- Multi-language support
- Advanced quiz features (timed questions, hints)

---

**Built with ❤️ for OpenClaw**
