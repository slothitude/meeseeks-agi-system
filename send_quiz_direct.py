"""
Send quiz using direct API call to demonstrate inline buttons
"""

import json

# This would be called from within the OpenClaw bot context
# For now, we'll show the structure

def send_quiz_via_message_tool():
    """
    Example of how to send a quiz using the message tool from within OpenClaw
    
    This demonstrates the parameters needed for inline buttons
    """
    
    # Quiz data
    question = "What is the capital of France?"
    options = ["Paris", "London", "Berlin", "Madrid"]
    
    # Create inline keyboard structure
    buttons = {
        "inline_keyboard": [
            [
                {"text": "Paris", "callback_data": "quiz_test_0"},
                {"text": "London", "callback_data": "quiz_test_1"}
            ],
            [
                {"text": "Berlin", "callback_data": "quiz_test_2"},
                {"text": "Madrid", "callback_data": "quiz_test_3"}
            ]
        ]
    }
    
    # Convert to JSON string
    buttons_json = json.dumps(buttons)
    
    print("=== Message Tool Call Example ===\n")
    print("In OpenClaw bot context, you would call:")
    print("""
message(
    action="send",
    channel="telegram",
    target="5597932516",
    message="Test Quiz: What is the capital of France?",
    # Note: The message tool may need a 'buttons' parameter
    # Check tool documentation for exact parameter name
)
    """)
    
    print("\nButtons JSON to pass:")
    print(json.dumps(buttons, indent=2))
    
    print("\n=== For CLI Usage ===")
    print("Save buttons to file and use:")
    print("openclaw message send --channel telegram --target 5597932516 \\")
    print('  --message "Test Quiz: What is the capital of France?" \\')
    print(f"  --buttons '{buttons_json}'")


if __name__ == "__main__":
    send_quiz_via_message_tool()
