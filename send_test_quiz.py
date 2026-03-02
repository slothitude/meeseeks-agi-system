"""
Send a test quiz to Telegram via OpenClaw message tool

This script demonstrates sending an inline button quiz to Telegram.
"""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(__file__))

from telegram_inline_buttons_helper import InlineButtonHelper


def send_test_quiz():
    """Send a test quiz to the configured Telegram user"""
    
    # Create helper
    helper = InlineButtonHelper()
    
    # Create a simple quiz
    question = "What is the capital of France?"
    options = ["Paris", "London", "Berlin", "Madrid"]
    correct_index = 0
    
    message, buttons_json = helper.create_quiz(question, options, correct_index)
    
    # Print what we're sending
    print("=== Sending Test Quiz ===")
    print(f"Question: {question}")
    print(f"Options: {options}")
    print(f"Correct: {options[correct_index]}")
    print(f"\nMessage:\n{message}")
    print(f"\nButtons JSON:\n{json.dumps(json.loads(buttons_json), indent=2)}")
    
    # Save quiz info for callback handling
    quiz_id = None
    # Extract quiz ID from first button's callback_data
    btns = json.loads(buttons_json)
    if btns['inline_keyboard'] and btns['inline_keyboard'][0]:
        callback_data = btns['inline_keyboard'][0][0]['callback_data']
        quiz_id = callback_data.split('_')[1]
        print(f"\nQuiz ID: {quiz_id}")
    
    # Show OpenClaw command
    print("\n=== OpenClaw Command ===")
    print("To send this quiz, run:")
    print(f'openclaw message send --channel telegram --target 5597932516 --message "{message}" --buttons \'{buttons_json}\'')
    
    return helper, quiz_id


if __name__ == "__main__":
    send_test_quiz()
