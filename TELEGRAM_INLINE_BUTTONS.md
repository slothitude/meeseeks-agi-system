# Telegram Inline Buttons Implementation for OpenClaw Bot

## Overview

This implementation adds support for Telegram inline buttons to create interactive quizzes and multiple-choice questions.

## Files Created

1. **`telegram_inline_buttons_helper.py`** - Core helper module
2. **`test_inline_quiz.py`** - Test and demo script
3. **`send_test_quiz.py`** - Simple quiz sender
4. **`test_buttons.json`** - Example buttons JSON

## Quick Start

### 1. Basic Usage

```python
from telegram_inline_buttons_helper import InlineButtonHelper

# Create helper
helper = InlineButtonHelper()

# Create a quiz
question = "What is the capital of France?"
options = ["Paris", "London", "Berlin", "Madrid"]
correct_index = 0  # Paris is correct

message, buttons_json = helper.create_quiz(question, options, correct_index)

# Send via OpenClaw message tool (from within bot)
# Note: Check message tool schema for exact parameter name for buttons
```

### 2. Using in OpenClaw Bot

When a user asks for a quiz:

```python
# In your bot handler
helper = InlineButtonHelper()

# Create quiz
msg, btns = helper.create_quiz(
    "What is the capital of France?",
    ["Paris", "London", "Berlin", "Madrid"],
    0  # Correct index
)

# Send to user
message(
    action="send",
    channel="telegram",
    target=user_id,
    message=msg,
    # Pass buttons as needed by message tool
)
```

### 3. Handling Button Callbacks

When a user clicks a button, you'll receive a callback:

```python
# In callback handler
result = helper.handle_callback(callback_data)

if result:
    if 'error' in result:
        response = result['error']
    else:
        # Quiz was answered
        response = result['response']
        is_correct = result['is_correct']
    
    # Send response back to user
    message(
        action="send",
        channel="telegram",
        target=user_id,
        message=response
    )
```

## Features

### ✅ Implemented

- Create quizzes with multiple choice options
- Configurable number of columns for buttons
- Unique quiz IDs to track multiple quizzes
- Callback handling with correct/incorrect feedback
- Quiz state management

### 📋 Button Layout

By default, buttons are arranged in 2 columns:
```
[Paris]     [London]
[Berlin]    [Madrid]
```

You can customize the number of columns:
```python
buttons_json = helper.format_buttons_json(options, columns=1)
# Results in:
# [Paris]
# [London]
# [Berlin]
# [Madrid]
```

## Message Tool Integration

### CLI Usage

```bash
openclaw message send \
  --channel telegram \
  --target 5597932516 \
  --message "Test Quiz: What is the capital of France?" \
  --buttons '{"inline_keyboard": [[{"text": "Paris", "callback_data": "quiz_0"}]]}'
```

### From Bot Code

The message tool supports inline buttons. Based on the CLI help:

```
--buttons <json>  Telegram inline keyboard buttons as JSON (array of button rows)
```

## Callback Data Format

Callbacks use the format: `quiz_{quiz_id}_{option_index}`

Examples:
- `quiz_abc123_0` - Quiz ID: abc123, Option 0 (first option)
- `quiz_abc123_3` - Quiz ID: abc123, Option 3 (fourth option)

## Example Quiz Types

### Geography Quiz
```python
helper.create_quiz(
    "What is the capital of France?",
    ["Paris", "London", "Berlin", "Madrid"],
    0
)
```

### Science Quiz
```python
helper.create_quiz(
    "Which planet is known as the Red Planet?",
    ["Venus", "Mars", "Jupiter", "Saturn"],
    1
)
```

### Programming Quiz
```python
helper.create_quiz(
    "What does 'HTML' stand for?",
    [
        "Hyper Text Markup Language",
        "High Tech Modern Language",
        "Hyper Transfer Markup Language",
        "Home Tool Markup Language"
    ],
    0
)
```

## Integration with Main Bot

### Step 1: Detect Quiz Request

```python
if "quiz" in user_message.lower() or "ask me a" in user_message.lower():
    # User wants a quiz
    send_quiz(user_id)
```

### Step 2: Send Quiz

```python
def send_quiz(user_id):
    helper = InlineButtonHelper()
    msg, btns = helper.create_quiz(
        "What is the capital of France?",
        ["Paris", "London", "Berlin", "Madrid"],
        0
    )
    
    # Store helper instance for callback handling
    # (Could use session storage or global dict)
    
    message(
        action="send",
        channel="telegram",
        target=user_id,
        message=msg,
        # buttons parameter here
    )
```

### Step 3: Handle Callback

```python
def handle_callback(callback_data, user_id):
    # Retrieve helper instance (from session or global)
    result = helper.handle_callback(callback_data)
    
    if result:
        message(
            action="send",
            channel="telegram",
            target=user_id,
            message=result['response']
        )
```

## Testing

Run the test script:

```bash
python test_inline_quiz.py
```

This will show:
- Example quiz messages
- Button JSON structure
- Callback handling examples
- Multiple quiz types

## Notes

### Current Implementation

- ✅ Helper module works correctly
- ✅ Quiz creation with inline buttons
- ✅ Callback handling logic
- ✅ Correct/incorrect feedback

### To Complete Integration

You'll need to:

1. **Add callback handler to main bot** - Detect when a callback is received (button press)
2. **Store helper instances** - Keep track of active quizzes (could use session storage)
3. **Wire up message tool** - Use the message tool with buttons parameter

### Checking Message Tool Schema

The message tool schema shows it accepts various parameters. For inline buttons on Telegram, you would use the buttons parameter (exact name may vary - check tool schema).

## Example Bot Flow

```
User: "Ask me a quiz with 4 options"
Bot: Creates quiz with InlineButtonHelper
Bot: Sends message with inline buttons via message tool
User: Clicks [Paris] button
Bot: Receives callback_data: "quiz_abc123_0"
Bot: Calls helper.handle_callback("quiz_abc123_0")
Bot: Gets response: "✅ Correct! Well done!"
Bot: Sends response back to user
```

## Next Steps

1. **Test with actual message tool** - Try sending a quiz from within OpenClaw bot context
2. **Implement callback listener** - Add handler for button press callbacks
3. **Add more quiz types** - Create quiz database or API integration
4. **Enhance feedback** - Add explanations, hints, scoring

## Files Reference

- **Helper Module**: `C:\Users\aaron\.openclaw\workspace\telegram_inline_buttons_helper.py`
- **Test Script**: `C:\Users\aaron\.openclaw\workspace\test_inline_quiz.py`
- **Example Buttons**: `C:\Users\aaron\.openclaw\workspace\test_buttons.json`
- **This Doc**: `C:\Users\aaron\.openclaw\workspace\TELEGRAM_INLINE_BUTTONS.md`
