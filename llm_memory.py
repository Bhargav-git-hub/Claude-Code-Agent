"""Simple chat loop that keeps conversation history so Claude remembers earlier turns."""

from anthropic import Anthropic
import os
from pathlib import Path
from dotenv import load_dotenv

# Load ANTHROPIC_API_KEY and other settings from a .env file next to this script.
load_dotenv(Path(__file__).resolve().parent / ".env")

# Anthropic API client, authenticated with the key from the environment.
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
# Full conversation history, sent with every request so the model has memory.
messages = []

while True:
    user_input = input("You: ")
    # Append a "keep it short" instruction to each question.
    messages.append({"role": "user", "content": user_input+", in one sentence."})
    response = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=1024,
        system="You are a helpful assistant.",
        messages=messages,
    )
    print("BOT: ", "".join(block.text for block in response.content if block.type == "text"))
    # Save the bot's text reply to history so later turns can refer to it.
    messages.append({"role": "assistant", "content": "".join(block.text for block in response.content if block.type == "text")})
    # print("-" * 100)
    # print("Bot:",messages[-1])
