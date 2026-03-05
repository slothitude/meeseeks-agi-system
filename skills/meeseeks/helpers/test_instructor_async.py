"""Test async instructor with Ollama"""
import os
os.environ["COGNEE_SKIP_CONNECTION_TEST"] = "true"

import instructor
from openai import AsyncOpenAI
import asyncio

print("Testing async instructor + Ollama...")

# Create async instructor client
aclient = instructor.from_openai(
    AsyncOpenAI(base_url="http://localhost:11434/v1", api_key="ollama"),
    mode=instructor.Mode.JSON,
)

async def test():
    print("Calling acreate...")
    try:
        result = await asyncio.wait_for(
            aclient.chat.completions.create(
                model="llama3.2:latest",
                messages=[
                    {"role": "user", "content": "test"},
                    {"role": "system", "content": 'Respond with the string "test"'},
                ],
                response_model=str,
                max_retries=1,
            ),
            timeout=15
        )
        print(f"Success: {result}")
    except asyncio.TimeoutError:
        print("Timed out after 15s")
    except Exception as e:
        print(f"Failed: {type(e).__name__}: {e}")

asyncio.run(test())
