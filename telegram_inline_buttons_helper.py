"""
Telegram Inline Buttons Helper for OpenClaw Bot

This module provides functionality to send messages with inline buttons
and handle callback queries from button presses.
"""

import json
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass


@dataclass
class QuizOption:
    """Represents a single quiz option"""
    text: str
    callback_data: str
    correct: bool = False


class InlineButtonHelper:
    """Helper class for creating and managing Telegram inline buttons"""
    
    def __init__(self):
        self.active_quizzes = {}  # Track active quizzes by message_id
    
    @staticmethod
    def create_inline_keyboard(options: List[QuizOption], columns: int = 2) -> Dict:
        """
        Create a Telegram inline keyboard from quiz options.
        
        Args:
            options: List of QuizOption objects
            columns: Number of buttons per row (default 2)
        
        Returns:
            Dictionary with inline_keyboard structure
        """
        keyboard = []
        row = []
        
        for option in options:
            button = {
                "text": option.text,
                "callback_data": option.callback_data
            }
            row.append(button)
            
            if len(row) >= columns:
                keyboard.append(row)
                row = []
        
        # Add remaining buttons
        if row:
            keyboard.append(row)
        
        return {"inline_keyboard": keyboard}
    
    @staticmethod
    def format_buttons_json(options: List[QuizOption], columns: int = 2) -> str:
        """
        Format inline keyboard as JSON string for OpenClaw CLI.
        
        Args:
            options: List of QuizOption objects
            columns: Number of buttons per row
        
        Returns:
            JSON string of inline keyboard
        """
        keyboard = InlineButtonHelper.create_inline_keyboard(options, columns)
        return json.dumps(keyboard)
    
    def create_quiz(
        self,
        question: str,
        options: List[str],
        correct_index: int,
        quiz_id: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Create a quiz with inline buttons.
        
        Args:
            question: The quiz question
            options: List of answer options
            correct_index: Index of the correct answer (0-based)
            quiz_id: Optional unique identifier for the quiz
        
        Returns:
            Tuple of (message text, buttons JSON)
        """
        if quiz_id is None:
            import uuid
            quiz_id = str(uuid.uuid4())[:8]
        
        # Create quiz options
        quiz_options = [
            QuizOption(
                text=option,
                callback_data=f"quiz_{quiz_id}_{i}",
                correct=(i == correct_index)
            )
            for i, option in enumerate(options)
        ]
        
        # Format message
        message = f"❓ *Quiz*\n\n{question}"
        
        # Create buttons
        buttons_json = self.format_buttons_json(quiz_options)
        
        # Store quiz for later reference
        self.active_quizzes[quiz_id] = {
            "question": question,
            "options": quiz_options,
            "correct_index": correct_index
        }
        
        return message, buttons_json
    
    def handle_callback(self, callback_data: str) -> Optional[Dict]:
        """
        Handle a callback from inline button press.
        
        Args:
            callback_data: The callback_data from the button
        
        Returns:
            Dictionary with response info, or None if not a quiz callback
        """
        if not callback_data.startswith("quiz_"):
            return None
        
        parts = callback_data.split("_")
        if len(parts) != 3:
            return None
        
        quiz_id = parts[1]
        answer_index = int(parts[2])
        
        if quiz_id not in self.active_quizzes:
            return {"error": "Quiz not found or expired"}
        
        quiz = self.active_quizzes[quiz_id]
        is_correct = answer_index == quiz["correct_index"]
        
        if is_correct:
            response = "✅ Correct! Well done!"
        else:
            correct_option = quiz["options"][quiz["correct_index"]]
            response = f"❌ Incorrect. The correct answer was: {correct_option.text}"
        
        return {
            "quiz_id": quiz_id,
            "answer_index": answer_index,
            "is_correct": is_correct,
            "response": response
        }


# Example usage functions
def example_quiz_geography():
    """Example: Create a geography quiz"""
    helper = InlineButtonHelper()
    message, buttons = helper.create_quiz(
        question="What is the capital of France?",
        options=["Paris", "London", "Berlin", "Madrid"],
        correct_index=0
    )
    return message, buttons


def example_quiz_multiple_choice():
    """Example: Create a multiple choice quiz"""
    helper = InlineButtonHelper()
    message, buttons = helper.create_quiz(
        question="Which planet is known as the Red Planet?",
        options=["Venus", "Mars", "Jupiter", "Saturn"],
        correct_index=1
    )
    return message, buttons


if __name__ == "__main__":
    # Demo
    helper = InlineButtonHelper()
    
    print("=== Example Quiz 1: Geography ===")
    msg1, btns1 = example_quiz_geography()
    print(f"Message: {msg1}")
    print(f"Buttons JSON: {btns1}")
    
    print("\n=== Example Quiz 2: Science ===")
    msg2, btns2 = example_quiz_multiple_choice()
    print(f"Message: {msg2}")
    print(f"Buttons JSON: {btns2}")
    
    print("\n=== Testing Callback Handling ===")
    # Simulate callback from button press
    result = helper.handle_callback("quiz_paris_0")
    print(f"Callback result: {result}")
