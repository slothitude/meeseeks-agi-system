"""Test instructor with Ollama"""
import os
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"

import instructor
from openai import OpenAI

print("Testing instructor + OpenAI client with Ollama...")

# Create instructor client (synchronous)
client = instructor.from_openai(
    OpenAI(base_url="http://localhost:11434/v1", api_key="ollama"),
    mode=instructor.Mode.JSON,
)

print("Calling create (synchronous)...")
try:
    result = client.chat.completions.create(
        model="llama3.2:latest",
        messages=[
            {"role": "user", "content": "test"},
            {"role": "system", "content": 'Respond with the string "test"'},
        ],
        response_model=str,
        max_retries=1,
    )
    print(f"Success: {result}")
except Exception as e:
    print(f"Failed: {type(e).__name__}: {e}")
