"""
Test script for Telegram inline button quizzes

This demonstrates how to:
1. Create a quiz with inline buttons
2. Send it via OpenClaw's message tool
3. Handle callback responses
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from telegram_inline_buttons_helper import InlineButtonHelper
import subprocess
import json


def send_quiz_via_openclaw(target: str, question: str, options: list, correct_index: int):
    """
    Send a quiz with inline buttons via OpenClaw CLI.
    
    Args:
        target: Telegram chat ID or username
        question: Quiz question
        options: List of answer options
        correct_index: Index of correct answer (0-based)
    """
    helper = InlineButtonHelper()
    message, buttons_json = helper.create_quiz(question, options, correct_index)
    
    # Build OpenClaw command
    cmd = [
        "openclaw", "message", "send",
        "--channel", "telegram",
        "--target", target,
        "--message", message,
        "--buttons", buttons_json
    ]
    
    print(f"Sending quiz to {target}...")
    print(f"Command: {' '.join(cmd)}")
    
    # Execute command
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Quiz sent successfully!")
        print(result.stdout)
    else:
        print("✗ Error sending quiz:")
        print(result.stderr)
    
    return helper


def demo_quiz_geography():
    """Demo: Geography quiz about France"""
    return {
        "question": "What is the capital of France?",
        "options": ["Paris", "London", "Berlin", "Madrid"],
        "correct_index": 0
    }


def demo_quiz_science():
    """Demo: Science quiz about planets"""
    return {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Venus", "Mars", "Jupiter", "Saturn"],
        "correct_index": 1
    }


def demo_quiz_programming():
    """Demo: Programming quiz"""
    return {
        "question": "What does 'HTML' stand for?",
        "options": [
            "Hyper Text Markup Language",
            "High Tech Modern Language",
            "Hyper Transfer Markup Language",
            "Home Tool Markup Language"
        ],
        "correct_index": 0
    }


if __name__ == "__main__":
    # Example usage
    print("=== Telegram Inline Button Quiz Demo ===\n")
    
    # Get target (in real usage, this would come from the user message)
    # For testing, we'll use the configured Telegram ID from openclaw.json
    TARGET = "5597932516"  # Slothitude's Telegram ID
    
    # Create helper
    helper = InlineButtonHelper()
    
    # Demo 1: Show what the quiz looks like
    quiz = demo_quiz_geography()
    message, buttons_json = helper.create_quiz(
        quiz["question"],
        quiz["options"],
        quiz["correct_index"]
    )
    
    print("Quiz Message:")
    print(message)
    print("\nButtons JSON (formatted):")
    print(json.dumps(json.loads(buttons_json), indent=2))
    
    # Demo 2: Show how to handle callbacks
    print("\n=== Callback Handling Examples ===")
    
    # Store the quiz
    from telegram_inline_buttons_helper import QuizOption
    helper.active_quizzes["test123"] = {
        "question": quiz["question"],
        "options": [
            QuizOption(text=opt, callback_data=f"quiz_test123_{i}", correct=(i == quiz["correct_index"]))
            for i, opt in enumerate(quiz["options"])
        ],
        "correct_index": quiz["correct_index"]
    }
    
    # Test correct answer
    print("\nUser clicks 'Paris' (correct answer):")
    result = helper.handle_callback("quiz_test123_0")
    print(f"Response: {result['response']}")
    
    # Test wrong answer
    print("\nUser clicks 'London' (wrong answer):")
    result = helper.handle_callback("quiz_test123_1")
    print(f"Response: {result['response']}")
    
    # Demo 3: Multiple quizzes
    print("\n=== Multiple Quiz Types ===")
    
    quizzes = [
        demo_quiz_geography(),
        demo_quiz_science(),
        demo_quiz_programming()
    ]
    
    for i, quiz in enumerate(quizzes, 1):
        msg, btns = helper.create_quiz(
            quiz["question"],
            quiz["options"],
            quiz["correct_index"]
        )
        print(f"\nQuiz {i}: {quiz['question']}")
        print(f"Options: {', '.join(quiz['options'])}")
        print(f"Correct: {quiz['options'][quiz['correct_index']]}")
    
    print("\n=== Integration with OpenClaw Bot ===")
    print("""
To use in the main bot:
1. When user asks for a quiz, create quiz using InlineButtonHelper
2. Send via message tool with --buttons parameter
3. When callback is received, use helper.handle_callback()
4. Send response back to user

Example:
    helper = InlineButtonHelper()
    msg, btns = helper.create_quiz("Question?", ["A", "B", "C"], 0)
    
    # Send via message tool
    message(
        action="send",
        channel="telegram",
        target="5597932516",
        message=msg,
        # For message tool, buttons would need to be passed as a parameter
    )
    
    # Handle callback (when user clicks button)
    result = helper.handle_callback(callback_data)
    if result:
        # Send response
        message(
            action="send",
            channel="telegram",
            target="5597932516",
            message=result['response']
        )
    """)
