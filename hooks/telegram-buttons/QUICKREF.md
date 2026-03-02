# 🥒 Telegram Button Hooks - Quick Reference

## 🚀 Quick Start

```bash
# 1. Configure bot token
cd C:\Users\aaron\.openclaw\workspace\hooks\telegram-buttons
# Edit config.json, set your bot token

# 2. Run the service
node index.js

# Or run the demo bot
node demo-bot.js
```

## 📝 Create Buttons

```javascript
const TelegramButtonHelper = require('../../telegram_button_helper');
const helper = new TelegramButtonHelper('YOUR_BOT_TOKEN');
```

### Confirmation (Yes/No)
```javascript
const keyboard = helper.createConfirmation('action_name', { context: 'data' });
await helper.sendMessage(chatId, 'Confirm?', keyboard);
```

### Quiz
```javascript
const options = ['Option A', 'Option B', 'Option C'];
const keyboard = helper.createQuizButtons('question_id', options);
await helper.sendMessage(chatId, 'Question?', keyboard);
```

### Menu
```javascript
const items = [
  { label: 'Settings', action: 'settings' },
  { label: 'Help', action: 'help' }
];
const keyboard = helper.createMenu(items, 'back_action');
await helper.sendMessage(chatId, 'Menu:', keyboard);
```

### Custom
```javascript
const keyboard = helper.createKeyboard(
  helper.createRow(
    helper.createButton('Button 1', helper.encodeCallback('type1', { data: 1 })),
    helper.createButton('Button 2', helper.encodeCallback('type2', { data: 2 }))
  )
);
await helper.sendMessage(chatId, 'Custom buttons:', keyboard);
```

## 🎯 Handle Callbacks

### Automatic (Service)
```bash
node index.js  # Uses built-in handlers
```

### Manual
```javascript
helper.startPolling(async (callbackQuery) => {
  const { id, from, message, data } = callbackQuery;
  const decoded = helper.decodeCallback(data);
  
  console.log(`Callback: ${decoded.type} from ${from.username}`);
  
  switch (decoded.type) {
    case 'confirm':
      // Handle confirmation
      break;
    case 'quiz_answer':
      // Handle quiz
      break;
    case 'menu':
      // Handle menu
      break;
    default:
      // Custom handling
  }
  
  await helper.answerCallback(id, { text: 'Done!' });
});
```

## 📊 Quiz Handler

```javascript
const QuizHandler = require('./quiz-handler');

const quizzes = {
  q1: {
    question: 'Question text?',
    options: ['A', 'B', 'C'],
    correctIndex: 1,
    explanation: 'Why B is correct'
  }
};

const quizHandler = new QuizHandler(helper, quizzes);

// Send quiz
await quizHandler.sendQuiz(chatId, 'q1');

// Get progress
const progress = quizHandler.getUserProgress(userId);
console.log(`Score: ${progress.correctAnswers}/${progress.totalAnswered}`);
```

## 🔧 Common Operations

### Send Message
```javascript
await helper.sendMessage(chatId, 'Hello!', keyboard);
```

### Edit Message
```javascript
await helper.editMessage(chatId, messageId, 'Updated text', newKeyboard);
```

### Answer Callback
```javascript
await helper.answerCallback(callbackQueryId, {
  text: 'Success!',
  showAlert: true,  // Show as popup
  cacheTime: 5      // Cache for 5 seconds
});
```

### Log Interaction
```javascript
helper.logInteraction(userId, username, 'type', { data: 'payload' }, 'result');
```

## 📁 File Structure

```
telegram_button_helper.js     # Main module
hooks/telegram-buttons/
├── callback-handler.js       # Main callback router
├── quiz-handler.js          # Quiz logic
├── config.json              # Configuration
├── index.js                 # Service entry
├── demo-bot.js              # Complete working bot
├── examples.js              # Code examples
├── test.js                  # Test suite
└── verify.js                # Verification script
```

## 🧪 Testing

```bash
# Run tests
node test.js

# Verify installation
node verify.js

# Run demo bot
node demo-bot.js
```

## 📚 Documentation

- **README.md** - Full documentation
- **SETUP.md** - Quick start guide
- **INTEGRATION.md** - Integration examples
- **SUMMARY.md** - Complete overview

## 🔑 Key Concepts

### Callback Data
```javascript
// Encode
const data = helper.encodeCallback('type', { payload: 'data' });

// Decode
const decoded = helper.decodeCallback(data);
// { type: 'type', payload: { payload: 'data' }, timestamp: 1234567890 }
```

### Button Types
- `callback_data` - Triggers callback to bot
- `url` - Opens external link

### Keyboard Structure
```javascript
{
  inline_keyboard: [
    [button1, button2],  // Row 1
    [button3]            // Row 2
  ]
}
```

## 💡 Tips

1. **Long polling**: Set timeout to 30-60 seconds
2. **Callback limit**: Max 64 bytes, auto-compressed if larger
3. **Answer callbacks**: Always call `answerCallback()` to remove loading state
4. **Edit vs new**: Edit messages to update, send new for fresh content
5. **Logging**: All interactions logged to console and file

## ⚠️ Common Issues

**Bot not responding?**
- Check bot token
- Verify bot started with `/start`
- Check console for errors

**Buttons not working?**
- Ensure callback handler is running
- Check callback_data is valid
- Verify handler registered for callback type

**Polling errors?**
- Check network connectivity
- Verify bot permissions
- Look for rate limiting

## 📞 Support

- Check README.md for detailed docs
- Run test.js to verify setup
- Check console logs for errors
- See demo-bot.js for complete example

---

**Quick Reference v1.0 | Telegram Button Hooks System**
