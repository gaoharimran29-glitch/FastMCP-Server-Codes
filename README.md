# Local MCP Server Setup Guide

## Prerequisites

Install `uv` first:

```bash
pip install uv
```

---

# Step 1 — Create Project Folder

Create a new folder for your MCP project and open terminal inside it.

Initialize the project:

```bash
uv init .
```

---

# Step 2 — Install FastMCP

Install FastMCP dependency:

```bash
uv add fastmcp
```

Now create your Python file (example: `local_server.py`) and write your MCP server code.

Example:

```python
from fastmcp import FastMCP
import random

mcp = FastMCP(name="Demo server")

@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """
    Add two numbers and return the result
    """
    return a + b

@mcp.tool()
def throw_dice() -> int:
    """
    Simulate a dice roll (1–6)
    """
    return random.randint(1, 6)

if __name__ == "__main__":
    mcp.run()
```

---

# Step 3 — Test the MCP Server

Use MCP Inspector to test your server:

```bash
fastmcp dev inspector local_server.py
```

This opens the MCP Inspector interface where you can test tools manually.

---

# Step 4 — Run the MCP Server

Run your local MCP server:

```bash
fastmcp run local_server.py
```

---

# Step 5 — Integrate with Claude Desktop

Open Claude Desktop settings:

1. Open Claude Desktop
2. Go to **Settings**
3. Open **Developer**
4. Click **Edit Config**

Add the following configuration inside `config.json`:

```json
{
  "mcpServers": {
    "Demo server": {
      "command": "C:\\Users\\hp\\AppData\\Local\\Programs\\Python\\Python310\\Scripts\\uvx.exe",
      "args": [
        "--with",
        "fastmcp",
        "fastmcp",
        "run",
        "C:\\Users\\hp\\Desktop\\my-mcp-server\\local_server.py"
      ]
    }
  },
  "preferences": {
    "coworkScheduledTasksEnabled": false,
    "ccdScheduledTasksEnabled": false,
    "coworkWebSearchEnabled": true,
    "epitaxyPrefs": {
      "starred-local-code-sessions": [],
      "starred-cowork-spaces": [],
      "starred-session-groups": [],
      "dframe-local-slice": {
        "pinnedOrder": [],
        "customGroupAssignments": {},
        "customGroupOrder": {}
      }
    }
  }
}
```

---

# Step 6 — Restart Claude Desktop

Completely close and reopen Claude Desktop.

Your MCP tools should now appear automatically inside Claude.

---
