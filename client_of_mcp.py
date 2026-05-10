import asyncio
import json
from dotenv import load_dotenv
import os
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    ToolMessage,
)

load_dotenv()

SERVERS = {
    "Demo server": {
        "transport": "stdio",
        "command": "uvx",
        "args": [
            "--with",
            "fastmcp",
            "fastmcp",
            "run",
            r"C:\Users\hp\Desktop\my-mcp-server\local_server.py"
        ]
    },

  "github": {
        "transport": "http",
        "url": "https://api.githubcopilot.com/mcp/",
        "headers": {
            "Authorization": f"Bearer {os.getenv('GITHUB_PAT')}"
        }
    }
}

async def main():
    # MCP Client
    client = MultiServerMCPClient(SERVERS)

    # Get MCP tools
    tools = await client.get_tools()

    # Tool dictionary
    named_tools = {tool.name: tool for tool in tools}

    print("\nAvailable Tools:")
    for tool_name in named_tools:
        print("-", tool_name)

    # Gemini model
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite"
    )

    # Bind tools
    llm_with_tools = llm.bind_tools(tools)

    # Conversation history
    messages = []

    print("\nMCP Chat Started!")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ")

        except EOFError:
            print("\nInput stream closed.")
            break

        except KeyboardInterrupt:
            print("\nExiting...")
            break

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        # Add user message
        messages.append(HumanMessage(content=user_input))

        while True:
            # Call LLM
            response = await llm_with_tools.ainvoke(messages)

            # Store assistant response
            messages.append(response)

            # If no tool calls → print answer
            if not getattr(response, "tool_calls", None):
                print(f"\nAssistant: {response.content}\n")
                break

            # Execute tool calls
            for tc in response.tool_calls:
                tool_name = tc["name"]
                tool_args = tc.get("args", {})
                tool_call_id = tc["id"]

                print(f"\n[Calling Tool: {tool_name}]")
                print(f"[Args: {tool_args}]")

                try:
                    result = await named_tools[tool_name].ainvoke(
                        tool_args
                    )

                    print(f"[Tool Result: {result}]")

                    tool_message = ToolMessage(
                        tool_call_id=tool_call_id,
                        content=json.dumps(result, default=str)
                    )

                except Exception as e:
                    tool_message = ToolMessage(
                        tool_call_id=tool_call_id,
                        content=f"Tool Error: {str(e)}"
                    )

                # Add tool result to history
                messages.append(tool_message)


if __name__ == "__main__":
    asyncio.run(main())