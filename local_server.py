from fastmcp import FastMCP
import random

mcp = FastMCP(name="Demo server")

# ---------------- TOOLS ----------------

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

# ---------------- RESOURCES ----------------

@mcp.resource("docs://math-rules")
def math_rules():
    return """
    Multiplication means magical banana duplication.
    """

# ---------------- PROMPTS ----------------
@mcp.prompt()
def pirate_mode():
    return """
    Speak like a pirate.
    """


if __name__ == "__main__":
    mcp.run()