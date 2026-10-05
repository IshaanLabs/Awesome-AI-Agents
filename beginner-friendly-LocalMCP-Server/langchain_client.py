import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_ollama import ChatOllama


async def main():
    print("Connecting to MCP server...")

    client = MultiServerMCPClient(
        {
            "superstore": {
                "command": "python",
                "args": ["server.py"],
                "transport": "stdio",
            }
        }
    )

    tools = await client.get_tools()
    print(f"Loaded {len(tools)} tools: {[t.name for t in tools]}")

    llm = ChatOllama(model="qwen2.5:7b", base_url="http://localhost:11434")

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt="You are a data analyst. Use the available tools to answer questions about the Superstore sales dataset.",
    )

    queries = [
        "What is the total sales and profit in the Superstore dataset?",
        "Which product category generates the most profit?",
        "Show me the top 5 products by sales.",
        "Which orders are losing money?",
        "Give me a sales summary for the Corporate segment.",
    ]

    for query in queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        result = await agent.ainvoke({"messages": [{"role": "user", "content": query}]})
        last_message = result["messages"][-1]
        print(f"Answer: {last_message.content}")


if __name__ == "__main__":
    asyncio.run(main())
