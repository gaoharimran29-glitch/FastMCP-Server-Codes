## This is the basic code to create a local server using FastMCP
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