# main.py
# Entry point. Wires together the Ollama client, the model config,
# and the agent loop. Run this file to start the agent.
#
# Usage:
#   python main.py
#
# Make sure Ollama is running:
#   ollama serve
#   ollama pull qwen2.5

from openai import OpenAI

from config import OLLAMA_BASE_URL, OLLAMA_API_KEY, OLLAMA_MODEL
from agent import run_agent


def main():
    # Build the Ollama client using the OpenAI-compatible API
    client = OpenAI(
        base_url=OLLAMA_BASE_URL,
        api_key=OLLAMA_API_KEY,
    )

    print("Mini Agent — powered by Ollama"  + str(OLLAMA_MODEL))
    print("Type 'exit' to quit.\n")

    while True:
        task = input("You: ").strip()

        if not task:
            continue

        if task.lower() == "exit":
            print("Goodbye!")
            break

        answer = run_agent(task, client, OLLAMA_MODEL)
        print(f"\nAnswer: {answer}\n")


if __name__ == "__main__":
    main()
