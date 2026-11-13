# Claude Agents

A small collection of Python examples that show how to use the Anthropic (Claude) API, from a single request to a tool-using coding agent. It is meant as a learning project: each script is short and self-contained so you can read it top to bottom.

## Contents

| File | What it does | Tools used |
|------|--------------|------------|
| [`api_call.py`](api_call.py) | Minimal single request. Asks Claude one question and prints the answer. | None |
| [`llm_memory.py`](llm_memory.py) | Interactive chat loop that keeps the full conversation history, so Claude remembers earlier turns. Replies are kept to one sentence. | None |
| [`tools.py`](tools.py) | Tool-use demo. Claude is given a `read_file` tool and asked to summarize `notes.txt`, `notes1.txt`, and `notes2.txt`. | `read_file` |
| [`src/claude_agents/agent.py`](src/claude_agents/agent.py) | Full terminal coding agent. Claude can list, read, and write files and run shell commands in an interactive chat. Also available as the `claude-agents` command. | `list_files`, `read_file`, `write_file`, `run_command` |
| [`agent.py`](agent.py) | Thin wrapper that runs the agent from the repo root. | N/A |
| [`game/snake.py`](game/snake.py) | Standalone classic Snake game built with pygame. Not related to the Claude API. | N/A |

Supporting files:

- `notes.txt`: sample text used by `tools.py` as input for the tool-use demo.
- `.env.example`: template for the environment file. Copy it to `.env` and add your key.
- `pyproject.toml` / `uv.lock`: project metadata and locked dependencies (managed with [uv](https://docs.astral.sh/uv/)).
- `requirements.txt`: pip-installable dependency list, including pygame for the Snake game.
- `.python-version`: the Python version the project targets.

## How the scripts work

### `api_call.py`: one-shot request
1. Loads `ANTHROPIC_API_KEY` from `.env`.
2. Sends one user message with a system prompt.
3. Prints the text blocks from the reply.

### `llm_memory.py`: chat with memory
1. Reads a question from the terminal.
2. Appends it to a `messages` list along with "in one sentence."
3. Sends the whole list to Claude, so earlier turns are included.
4. Prints the reply and stores it in the history.

Stop the loop with `Ctrl+C`.

### `tools.py`: tool-use demo
This shows the basic tool-use loop:
1. Describe a tool to Claude with a name, description, and JSON input schema.
2. When Claude returns a `tool_use` block, run the matching local Python function.
3. Send the output back as a `tool_result`, matched by `tool_use_id`.
4. Repeat until Claude replies with plain text.

Note: this script requires `notes.txt`, `notes1.txt`, and `notes2.txt`. Only `notes.txt` is in the repo, so the other two files must be created first, or the tool will return a "not found" message.

### `src/claude_agents/agent.py`: terminal coding agent
A full agent built on the same loop as `tools.py`, with four tools:

| Tool | Behavior |
|------|----------|
| `list_files(path)` | Lists a directory. Folders end with `/`. |
| `read_file(path)` | Returns the full text of a file. |
| `write_file(path, content)` | Creates or overwrites a file. |
| `run_command(command)` | Runs a shell command. **Asks for `y/N` approval first.** Commands time out after 120 seconds. |

Errors from tools are returned to Claude as text so it can recover. Run the agent from the folder you want it to work in, because that is the working directory it uses. The agent loads `.env` from the current directory or its parents.

Type `exit` or `quit` to leave the chat.

### `game/snake.py`: Snake game
A pygame window with a 30x20 grid.
- Move with the arrow keys or `WASD`.
- Eat the red food to grow and score points.
- Hitting a wall or your own body ends the game. Press `R` to restart or `ESC` to quit.
- Speed rises as the score increases, capped at 20 FPS.

## Setup

Requirements:
- Python 3.14 or newer (see `.python-version` and `pyproject.toml`).
- An Anthropic API key.
- Git, to clone the repo.

### Option A: uv (recommended)

[uv](https://docs.astral.sh/uv/) reads `pyproject.toml` and `uv.lock`, so you get the exact locked versions.

```bash
# 1. Clone the repository
git clone <repo-url>
cd claude-agents

# 2. Install all dependencies into .venv
uv sync

# 3. Add your API key
cp .env.example .env
# then edit .env and set ANTHROPIC_API_KEY=your-key-here
```

`uv sync` installs the Claude dependencies only. To also run the Snake game, add pygame:

```bash
uv add pygame        # or: uv pip install pygame
```

### Option B: pip and requirements.txt

```bash
# 1. Clone the repository
git clone <repo-url>
cd claude-agents

# 2. Create and activate a virtual environment
python3.14 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install all dependencies (Claude packages and pygame)
pip install -r requirements.txt

# 4. Add your API key
cp .env.example .env
# then edit .env and set ANTHROPIC_API_KEY=your-key-here
```

`requirements.txt` lists the direct dependencies only. Installing it with pip is enough to run every script, including Snake.

If you use Option B, run the scripts with `python` (not `uv run`) from the activated environment.

## Running

With uv:

```bash
uv run claude-agents            # coding agent (same as agent.py)
uv run python api_call.py       # one-shot question
uv run python llm_memory.py     # chat with memory
uv run python tools.py          # read notes files via a tool
uv run python agent.py          # coding agent (asks before running commands)
uv run python game/snake.py  # Snake game (needs pygame)
```

With pip (after activating `.venv`):

```bash
claude-agents                   # not installed by pip; use the next line instead
python agent.py                 # coding agent (asks before running commands)
python api_call.py              # one-shot question
python llm_memory.py            # chat with memory
python tools.py                 # read notes files via a tool
python game/snake.py         # Snake game
```

With pip, `claude-agents` is not on your path because the package is not installed. Run `python agent.py` instead, or install the project with `pip install -e .` to get the command.

## Troubleshooting

- **`AuthenticationError` or an empty key:** check that `.env` contains `ANTHROPIC_API_KEY=...` and that you run from the project folder (or a subfolder). The agent searches upward from the current directory for `.env`.
- **`ModuleNotFoundError: No module named 'pygame'`:** install pygame (see Setup). Only the Snake game needs it.
- **`No module named 'anthropic'`:** you are not in the environment where dependencies are installed. With uv, use `uv run ...`. With pip, activate `.venv` first.
- **`tools.py` says a file is not found:** create `notes1.txt` and `notes2.txt` (see the `tools.py` section).

## Security notes

- The agent can write files and run shell commands in the directory it is started from. Review each command when prompted, and run it in a folder you are comfortable changing.
- Never commit your `.env` file. Keep API keys out of source control.

## Model

All scripts use `claude-haiku-5-5`, which is set as a constant in each file. Change the `MODEL` value in `src/claude_agents/agent.py` or the `model=` argument in the other scripts to use a different Claude model.

## Notes on the repo

- The `claude-agents` command runs `claude_agents:main` (from `src/claude_agents/__init__.py`), which starts the coding agent.
- `llm_memory.py` and `api_call.py` do not use the `system` prompt from the agent. Each file contains its own code.

## License

See [LICENSE](LICENSE).
