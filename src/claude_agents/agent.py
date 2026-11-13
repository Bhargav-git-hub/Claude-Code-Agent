"""Terminal coding agent: Claude can list, read, write files and run shell commands."""

import os
import subprocess

from anthropic import Anthropic
from dotenv import find_dotenv, load_dotenv

# Load ANTHROPIC_API_KEY and other settings from a .env file. find_dotenv searches
# the current directory and its parents, so this works after the package is installed.
load_dotenv(find_dotenv(usecwd=True))

# Anthropic API client, authenticated with the key from the environment.
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
MODEL = "claude-haiku-5-5"

# Instructions that define the agent's role and behavior for every request.
SYSTEM_PROMPT = """You are a coding agent running in the user's terminal.
You can list files, read files, write files, and run shell commands.
Use your tools to complete the user's task, then briefly summarize what you did.
The working directory is the folder the user launched you from."""


def list_files(path="."):
    """Return the names in `path` one per line, with '/' appended to folders."""
    entries = []
    for entry in os.scandir(path):
        entries.append(entry.name + ("/" if entry.is_dir() else ""))
    return "\n".join(sorted(entries)) or "(empty directory)"


def read_file(path):
    """Return the full text of the file at `path`."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path, content):
    """Create or overwrite the file at `path` with `content`."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Saved {path} ({len(content)} characters)"


def run_command(command):
    """Run a shell command after the user approves it, and return its output."""
    # Ask the user for approval first. Anything other than 'y' cancels the command.
    answer = input(f"  Run '{command}'? [y/N] ")
    if answer.strip().lower() != "y":
        return "The user declined to run this command."
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True, timeout=120
    )
    output = (result.stdout + result.stderr).strip()
    return output or f"(no output, exit code {result.returncode})"


# Map of tool names to the Python functions that implement them.
TOOLS = {
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
    "run_command": run_command,
}

# Tool definitions sent to the model. Each description and input_schema tells the
# model what the tool does and what arguments it needs.
TOOL_SCHEMAS = [
    {
        "name": "list_files",
        "description": "List the files in a directory. Folders end with /.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory to list, e.g. '.'"},
            },
            "required": ["path"],
        },
    },
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
    {
        "name": "write_file",
        "description": "Create or overwrite a text file with the given content.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path of the file to write"},
                "content": {"type": "string", "description": "Full contents of the file"},
            },
            "required": ["path", "content"],
        },
    },
    {
        "name": "run_command",
        "description": "Run a shell command and return its output. The user approves it first.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The shell command to run"},
            },
            "required": ["command"],
        },
    },
]


def run_tool(tool_use):
    """Run one tool call requested by the model and return its result as text."""
    name = tool_use.name
    args = tool_use.input
    print(f"  tool: {name}({args})")
    try:
        return str(TOOLS[name](**args))
    except Exception as error:
        # Return errors as text so the model can see them and recover.
        return f"Error: {error}"


def run_agent(messages):
    """Run the model until it replies without tool calls, then return its text reply."""
    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=messages,
            tools=TOOL_SCHEMAS,
        )
        # Keep the assistant turn in history, including any tool calls it made.
        messages.append({"role": "assistant", "content": response.content})

        tool_uses = [block for block in response.content if block.type == "tool_use"]
        if not tool_uses:
            # No tool calls means the task is finished. Return the text reply.
            return "".join(block.text for block in response.content if block.type == "text")

        # Run each requested tool and package its output as a tool_result.
        tool_results = []
        for tool_use in tool_uses:
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": run_tool(tool_use),
            })
        # Send the results back to the model as a user turn, then loop again.
        messages.append({"role": "user", "content": tool_results})


def main():
    """Interactive chat loop. Reads user input until 'exit' or 'quit'."""
    # The system prompt is sent as the first user message to start the conversation.
    messages = [{"role": "user", "content": SYSTEM_PROMPT}]
    print("Agent ready. Type 'exit' to quit.")
    while True:
        user_input = input("\nYou: ")
        if user_input.strip().lower() in ("exit", "quit"):
            break
        messages.append({"role": "user", "content": user_input})
        reply = run_agent(messages)
        print(f"\nAgent: {reply}")


if __name__ == "__main__":
    main()
