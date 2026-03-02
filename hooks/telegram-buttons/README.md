# Telegram Button Hooks System

Complete hooks system for handling Telegram inline button callbacks.

## Structure

```
hooks/telegram-buttons/
├── callback-handler.js    # Main callback handler (polls & routes)
├── quiz-handler.js        # Quiz-specific logic
├── config.json            # Button configurations
└── README.md              # This file

telegram_button_helper.js  # Main helper module (workspace root)
```

## Features

✅ Polls for Telegram callback updates
✅ Routes callbacks by type (quiz, confirm, menu)
✅ Quiz questions with correct/incorrect feedback
✅ Confirmations (Yes/No) with callbacks
✅ Menu navigation support
✅ Interaction logging
✅ Custom handler registration

## Quick Start

```javascript
const TelegramButtonHelper = require('./telegram_button_helper');

// Initialize with bot token
const helper = new TelegramButtonHelper(process.env.TELEGRAM_BOT_TOKEN);

// Start polling for callbacks
helper.start();

// Create a quiz
const quiz = helper.createQuiz(
  'What is the capital of France?',
  ['London', 'Paris', 'Berlin', 'Madrid'],
  1  // Correct answer: Paris (index 1)
);

// Send to chat (using your existing send logic)
// await bot.sendMessage(chatId, quiz.text, { reply_markup: quiz.reply_markup });

// Create confirmation dialog
const confirm = helper.createConfirmation('Delete this file?', {
  updateMessage: true
});

// Create menu
const menu = helper.createMenu('settings', {
  text: '⚙️ Settings Menu',
  buttons: [
    [{ text: '🔔 Notifications', callback_data: 'menu:{"menuId":"notifications"}' }],
    [{ text: '🎨 Theme', callback_data: 'menu:{"menuId":"theme"}' }],
    [{ text: '◀️ Back', callback_data: 'menu:{"menuId":"main"}' }]
  ]
});
```

## Callback Format

Callbacks use format: `type:json_data`

Examples:
- `quiz:{"questionId":"quiz_123","answerId":1,"correctAnswer":2}`
- `confirm:{"action":"yes","updateMessage":true}`
- `menu:{"menuId":"settings"}`

## Built-in Handlers

### Quiz Handler
Handles quiz answers with correct/incorrect feedback.

### Confirmation Handler
Handles Yes/No confirmations.

### Menu Handler
Handles menu navigation.

## Custom Handlers

```javascript
helper.on('custom', async (callback, data) => {
  // Your custom logic here
  console.log('Custom action:', data.action);
  
  // Answer the callback
  await helper.callbackHandler.answerCallback(callback.id, 'Action completed!');
  
  return { success: true };
});

// Button: { text: 'Custom', callback_data: 'custom:{"action":"doThing"}' }
```

## Integration with OpenClaw

To integrate with OpenClaw's hook system:

1. Import the helper in your bot code
2. Start the callback handler alongside your message polling
3. Use the helper methods to create button layouts
4. Register custom handlers for your specific needs

## Logging

All button interactions are logged to `interactions.log`:
```json
{"timestamp":"2025-01-16T10:30:00Z","userId":123456,"username":"user","data":"quiz:{...}","chatId":789}
```

## Configuration

Edit `config.json` to customize:
- Poll interval
- Timeout
- Button text defaults
- Handler settings

---

Created by Meeseeks Worker 🥒
