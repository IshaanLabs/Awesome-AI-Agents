# agent.py
# The core ReAct loop. This is the entire agent architecture.
# It takes a task, talks to the LLM, executes tools, and loops
# until the LLM has a final answer with no more tool calls.

import json
from openai import OpenAI

from tools import TOOLS, TOOL_FUNCTIONS


def run_agent(task: str, client: OpenAI, model: str) -> str:
    print(f"\n{'='*50}")
    print(f"Task: {task}")
    print(f"Model: {model}")
    print(f"{'='*50}\n")

    # messages is the agent's memory — everything the LLM has seen lives here
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant. Use the available tools when needed to answer the user's task. "
                "When you have gathered all the information you need, respond with a final answer without calling any tools."
            ),
        },
        {"role": "user", "content": task},
    ]

    iteration = 0

    while True:
        iteration += 1
        print(f"--- Iteration {iteration} ---")
        print("  [agent] sending messages to LLM...")

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        message = response.choices[0].message
        messages.append(message)

        # Decision point: no tool calls means the LLM has a final answer
        if not message.tool_calls:
            print("\n  [agent] LLM returned final answer — done.\n")
            return message.content

        # LLM wants to call one or more tools
        print(f"  [agent] LLM requested {len(message.tool_calls)} tool call(s)")

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            print(f"\n  > calling tool: {name}  args: {args}")

            fn = TOOL_FUNCTIONS.get(name)
            if fn:
                result = fn(**args)
            else:
                result = f"Unknown tool: {name}"
                print(f"  [agent] warning — unknown tool requested: {name}")

            # Append tool result to messages so the LLM sees it next iteration
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

        print(f"\n  [agent] all tools executed — looping back to LLM...\n")
