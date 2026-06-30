import os
import requests
from exa_py import Exa
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

EXA_API_KEY = os.getenv("EXA_API_KEY")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = "gemma3:latest"


def search_web(query):
    """
    Search the web using Exa API and return top 5 results.
    Returns a list of result objects or None if it fails.
    NOTE: uses exa.search() — the new API (search_and_contents is deprecated).
    """
    print(f"\n[SEARCH] Starting Exa web search for query: '{query}'")

    if not EXA_API_KEY:
        print("[SEARCH] ERROR: EXA_API_KEY is not set in .env file!")
        return None

    try:
        exa = Exa(EXA_API_KEY)
        print("[SEARCH] Exa client initialized. Fetching results...")

        # search() is the new API — returns text contents by default
        response = exa.search(query, num_results=5)
        results = response.results

        print(f"[SEARCH] Successfully fetched {len(results)} results from Exa.")
        for i, r in enumerate(results):
            print(f"  [SEARCH] Result {i+1}: {r.title} - {r.url}")

        return results

    except Exception as e:
        print(f"[SEARCH] ERROR: Failed to fetch Exa results. Reason: {e}")
        return None


def format_search_results(results):
    """
    Takes raw Exa results and formats them into a clean readable string for the LLM prompt.
    """
    print("\n[FORMAT] Formatting search results for LLM prompt...")

    if not results:
        print("[FORMAT] No results to format. Returning empty string.")
        return ""

    formatted = ""
    for i, r in enumerate(results):
        formatted += f"\nResult {i+1}:\n"
        formatted += f"  Title: {r.title}\n"
        formatted += f"  URL: {r.url}\n"
        # some results may not have text content
        if hasattr(r, "text") and r.text:
            # trim to avoid overly long prompts
            formatted += f"  Content: {r.text[:500]}...\n"

    print(f"[FORMAT] Done formatting {len(results)} results.")
    return formatted


def build_prompt(keywords, post_type, post_length, language, search_context, user_description):
    """
    Builds the final prompt string to send to the LLM.
    user_description is optional — if provided, it gives the LLM more focused intent.
    """
    print("\n[PROMPT] Building LLM prompt...")

    # include user description section if provided
    if user_description and user_description.strip():
        description_section = f"\n### What the user wants to convey:\n{user_description.strip()}\n"
        print("[PROMPT] User description included in prompt.")
    else:
        description_section = ""
        print("[PROMPT] No user description provided, skipping that section.")

    prompt = f"""You are an expert LinkedIn content writer. Write a LinkedIn post using ONLY the research context provided below.

### Strict Rules:
- Output ONLY the final LinkedIn post. No explanations, no notes, no word count, no meta-commentary.
- Do NOT start with phrases like "Here's a draft", "Okay", "Sure", or "Based on the research".
- Do NOT add any text after the hashtags.
- Do NOT include headers like "---" or "Post:" in the output.
- The post must be written in {language}.
- Post type: {post_type} — structure the content accordingly.
- Post length: {post_length}.
- Start with a powerful single-line hook that stops the scroll.
- Use short paragraphs (1-2 sentences max) with blank lines between them for LinkedIn readability.
- Use bullet points or numbered lists only if the post type calls for it.
- Naturally weave in the keywords — never force them.
- End with a conversational CTA that invites comments or opinions.
- Add 3-5 relevant hashtags on the last line.
{description_section}
### Keywords: {keywords}

### Web Research (base the post on this — do not fabricate facts):
{search_context}

Write the LinkedIn post now:"""

    print("[PROMPT] Prompt built successfully.")
    print(f"[PROMPT] Prompt length: {len(prompt)} characters.")
    return prompt


def generate_post_with_ollama(prompt):
    """
    Sends the prompt to local Ollama (gemma3 model) and returns the generated text.
    Uses the Ollama REST API directly via requests — no extra SDK needed.
    """
    print(f"\n[LLM] Sending prompt to Ollama at {OLLAMA_URL} using model '{OLLAMA_MODEL}'...")

    url = f"{OLLAMA_URL}/api/generate"

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False  # get full response at once
    }

    try:
        print("[LLM] Waiting for Ollama response (this may take a few seconds)...")
        response = requests.post(url, json=payload, timeout=120)

        if response.status_code == 200:
            result = response.json()
            generated_text = result.get("response", "")
            print(f"[LLM] Successfully received response from Ollama.")
            print(f"[LLM] Response length: {len(generated_text)} characters.")
            return generated_text
        else:
            print(f"[LLM] ERROR: Ollama returned status code {response.status_code}")
            print(f"[LLM] Response body: {response.text}")
            return None

    except requests.exceptions.ConnectionError:
        print(f"[LLM] ERROR: Could not connect to Ollama at {OLLAMA_URL}. Is Ollama running?")
        return None
    except requests.exceptions.Timeout:
        print("[LLM] ERROR: Request to Ollama timed out after 120 seconds.")
        return None
    except Exception as e:
        print(f"[LLM] ERROR: Unexpected error while calling Ollama. Reason: {e}")
        return None


def generate_linkedin_post(keywords, post_type, post_length, language, user_description=""):
    """
    Main function that ties everything together:
    1. Build search query — combine keywords + user description for better search focus
    2. Search web using Exa — HARD STOP if this fails
    3. Format the results
    4. Build the prompt
    5. Generate the post using Ollama
    6. Return the final post text
    """
    print("\n========== STARTING LINKEDIN POST GENERATION ==========")
    print(f"[MAIN] Keywords        : {keywords}")
    print(f"[MAIN] User Description: {user_description if user_description else 'Not provided'}")
    print(f"[MAIN] Post Type       : {post_type}")
    print(f"[MAIN] Post Length     : {post_length}")
    print(f"[MAIN] Language        : {language}")

    # Step 1: Build a richer search query by combining keywords + user description
    if user_description and user_description.strip():
        search_query = f"{keywords} {user_description.strip()}"
        print(f"[MAIN] Combined search query: '{search_query}'")
    else:
        search_query = keywords
        print(f"[MAIN] Using keywords only as search query: '{search_query}'")

    # Step 2: Search — if this fails, we stop. No hallucination fallback.
    search_results = search_web(search_query)

    if not search_results:
        print("[MAIN] STOPPING: Exa search returned no results. Refusing to generate without real context.")
        print("========== GENERATION ABORTED ==========\n")
        return None

    # Step 3: Format results
    search_context = format_search_results(search_results)

    # Step 4: Build prompt
    prompt = build_prompt(keywords, post_type, post_length, language, search_context, user_description)

    # Step 5: Generate with Ollama
    post = generate_post_with_ollama(prompt)

    if post:
        print("\n[MAIN] LinkedIn post generated successfully!")
        print("========== GENERATION COMPLETE ==========\n")
    else:
        print("\n[MAIN] ERROR: Post generation failed. Returning None.")
        print("========== GENERATION FAILED ==========\n")

    return post
