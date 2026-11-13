"""Minimal single-request example: ask Claude one question and print the answer."""

import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

# Load ANTHROPIC_API_KEY and other settings from a .env file next to this script.
load_dotenv(Path(__file__).resolve().parent / ".env")

# Anthropic API client, authenticated with the key from the environment.
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

# One-shot request: a system prompt plus a single user message, no tools.
response = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=1024,
    system="You are a helpful assistant.",
    messages=[
        {"role": "user", "content": "Explain what is an AI Agent shortly in one sentence?"}
    ],
)

# print(response)
# print("-" * 100)
# Join only the text blocks of the reply and print them (ignores non-text blocks).
print("".join(block.text for block in response.content if block.type == "text"))
