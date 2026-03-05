"""Test Cognee bridge"""
import subprocess
import json

result = subprocess.run(
    ["py", "-3.13", "skills/meeseeks/helpers/cognee_worker.py", json.dumps({
        "action": "add",
        "text": "Sloth_rog runs on Windows Rog machine",
        "dataset": "sloth_rog"
    })],
    capture_output=True,
    text=True,
    timeout=120
)

print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)
