import asyncio
import json
import os

from dotenv import load_dotenv

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

load_dotenv()

# =========================================================
# MCP SERVERS
# =========================================================

SERVERS = {
    "Demo server": {
        "transport": "stdio",
        "command": "uvx",
        "args": [
            "--with",
            "fastmcp",
            "fastmcp",
            "run",
            r"file_path_of_localserver.py" ## Change it according to your local server file path
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


# =========================================================
# MAIN
# =========================================================

async def main():

    client = MultiServerMCPClient(SERVERS)

    # -----------------------------------------------------
    # LOAD TOOLS
    # -----------------------------------------------------

    tools = await client.get_tools()
    named_tools = {tool.name: tool for tool in tools}

    print("\n================ TOOLS ================\n")
    for tool_name in named_tools:
        print("-", tool_name)

    # -----------------------------------------------------
    # LOAD RESOURCES
    # -----------------------------------------------------

    resources = await client.get_resources()

    print("\n============== RESOURCES ==============\n")
    for resource in resources:
        print(resource)

    # -----------------------------------------------------
    # LOAD PROMPTS + READ RESOURCES per server session
    # -----------------------------------------------------

    all_prompts = []
    resource_context = ""

    for server_name in SERVERS:

        # Each call opens a fresh session for that server
        async with client.session(server_name) as session:

            # --- Prompts ---
            try:
                prompts_list = await session.list_prompts()

                for p in prompts_list.prompts:
                    print(f" - [{server_name}] Found prompt: {p.name}")

                    prompt_content = await session.get_prompt(name=p.name)
                    print(f"   Description: {prompt_content.description}")

                    all_prompts.append({
                        "name": p.name,
                        "content": prompt_content
                    })

            except Exception as e:
                print(f"  Could not load prompts from {server_name}: {e}")

            # --- Resources ---
            try:
                server_resources = await session.list_resources()

                for r in server_resources.resources:
                    uri = str(r.uri)

                    try:
                        result = await session.read_resource(uri)

                        text_parts = [
                            c.text for c in result.contents
                            if hasattr(c, "text")
                        ]
                        content = "\n".join(text_parts)

                        resource_context += f"""
RESOURCE: {uri}

{content}

==================================================
"""
                    except Exception as e:
                        print(f"  Error reading resource {uri}: {e}")

            except Exception as e:
                print(f"  Could not load resources from {server_name}: {e}")

    # -----------------------------------------------------
    # BUILD PROMPT CONTEXT
    # -----------------------------------------------------

    prompt_context = ""

    for prompt in all_prompts:
        try:
            rendered = prompt["content"]
            messages_text = ""

            if hasattr(rendered, "messages"):
                for msg in rendered.messages:
                    role = getattr(msg, "role", "unknown")
                    if hasattr(msg.content, "text"):
                        text = msg.content.text
                    elif isinstance(msg.content, str):
                        text = msg.content
                    else:
                        text = str(msg.content)
                    messages_text += f"{role}: {text}\n"

            prompt_context += f"""
PROMPT: {prompt["name"]}

{messages_text or str(rendered)}

==================================================
"""
        except Exception as e:
            print(f"Error processing prompt {prompt['name']}: {e}")

    # -----------------------------------------------------
    # SYSTEM MESSAGE
    # -----------------------------------------------------

    system_prompt = f"""
You are an MCP-powered AI assistant.

You have access to:
1. MCP tools
2. MCP resources
3. MCP prompts

Use resources for contextual knowledge.
Use prompts for consistent behavior.

================ RESOURCES ================

{resource_context}

================ PROMPTS ==================

{prompt_context}
"""

    # -----------------------------------------------------
    # GEMINI MODEL
    # -----------------------------------------------------

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")
    llm_with_tools = llm.bind_tools(tools)

    # -----------------------------------------------------
    # CONVERSATION HISTORY
    # -----------------------------------------------------

    messages = [SystemMessage(content=system_prompt)]

    print("\n=======================================")
    print("        MCP CHAT STARTED")
    print("=======================================\n")
    print("Type 'exit' to quit.\n")

    # =====================================================
    # CHAT LOOP
    # =====================================================

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

        messages.append(HumanMessage(content=user_input))

        # -------------------------------------------------
        # AGENT LOOP
        # -------------------------------------------------

        while True:

            response = await llm_with_tools.ainvoke(messages)
            messages.append(response)

            if not getattr(response, "tool_calls", None):
                print(f"\nAssistant:\n{response.content}\n")
                break

            for tc in response.tool_calls:

                tool_name = tc["name"]
                tool_args = tc.get("args", {})
                tool_call_id = tc["id"]

                print(f"\n[Calling Tool: {tool_name}]")
                print(f"[Args: {tool_args}]")

                try:
                    result = await named_tools[tool_name].ainvoke(tool_args)
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

                messages.append(tool_message)

if __name__ == "__main__":
    asyncio.run(main())