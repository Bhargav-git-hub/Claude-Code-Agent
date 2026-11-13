"""Package entry point for claude_agents.

The `claude-agents` command (see [project.scripts] in pyproject.toml) runs `main`,
which starts the interactive terminal coding agent defined in `agent.py`.
"""

from claude_agents.agent import main

__all__ = ["main"]
