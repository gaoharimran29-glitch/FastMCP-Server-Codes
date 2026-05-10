from fastmcp import FastMCP
import random

# Create MCP server
mcp = FastMCP("Remote Demo Server")

# ---------------- TOOLS ---------------- #

@mcp.tool()
def subtract_numbers(a: int, b: int) -> int:
    """
    Add two numbers
    """
    return a - b

# ---------------- RUN SERVER ---------------- #

if __name__ == "__main__":
    # Runs HTTP server
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000
    )