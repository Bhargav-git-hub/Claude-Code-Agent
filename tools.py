"""Tool-use demo: asks Claude to read several notes files via a read_file tool."""

import json
import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

# Load ANTHROPIC_API_KEY and other settings from a .env file next to this script.
load_dotenv(Path(__file__).resolve().parent / ".env")

# Anthropic API client, authenticated with the key from the environment.
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))


def read_file(path):
    """Return the text of the file at `path`, or a message if it does not exist."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"File {path} not found"


# Tool definitions sent to the model. The model reads the description and
# input_schema to decide when and how to call each tool.
TOOLS = [
    {
        "name": "read_file",
        "description": "Read a text file and return its contents.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path of the file to read"},
            },
            "required": ["path"],
        },
    },
]

# Maps each tool name the model may request to the local Python function that runs it.
TOOL_HANDLERS = {
    "read_file": read_file,
}


def _json_default(value):
    """Fallback serializer for json.dumps on objects it cannot handle (used by the debug print)."""
    if hasattr(value, "model_dump"):
        return value.model_dump(exclude_none=True)
    return str(value)

# Conversation history. Starts with a single user question about three files.
messages = [
    {"role": "user", "content": "What is inside notes.txt, notes1.txt and notes2.txt? Summarize it in one line."},
]

# Agent loop: call the model, run any requested tools, feed results back,
# and stop once the model replies with plain text.
while True:
    response = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=1024,
        tools=TOOLS,
        messages=messages,
    )

    # Send the assistant turn back exactly as the model produced it, tool calls included.
    messages.append({"role": "assistant", "content": response.content})

    # Collect any tool calls the model made in this turn.
    tool_uses = [block for block in response.content if block.type == "tool_use"]
    if not tool_uses:
        # No tool calls means the model is done. Print its text reply and exit the loop.
        print("".join(block.text for block in response.content if block.type == "text"))
        break

    tool_results = []
    for tool_use in tool_uses:
        handler = TOOL_HANDLERS.get(tool_use.name)
        print(f"Model wants to run: {tool_use.name}({tool_use.input})")
        if handler is None:
            # The model asked for a tool we do not have. Report that back to it.
            result = f"Unknown tool: {tool_use.name}"
        else:
            result = handler(**tool_use.input)

        tool_results.append({
            "type": "tool_result",
            "tool_use_id": tool_use.id,
            "content": result,
        })

    # Tool results are a user turn. Each result is matched to its tool call by id.
    messages.append({"role": "user", "content": tool_results})
    #print(json.dumps(messages, default=_json_default, indent=2))
