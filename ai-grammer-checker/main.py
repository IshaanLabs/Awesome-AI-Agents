import requests


def get_prompt(user_text):
    """
    Creates the prompt for grammar correction.
    """

    print("Creating prompt...")

    prompt = f"""
You are an expert English editor.

Your task is to improve the given text while preserving its original meaning.

Instructions:
- Correct grammar.
- Correct spelling.
- Fix punctuation.
- Improve sentence structure.
- Improve readability.
- Preserve the original meaning.
- Do not add any new information.
- Return ONLY the corrected text.
- Do not include explanations.
- Do not use markdown.

Text:

{user_text}
"""

    return prompt




def get_models(base_url):
    """
    Fetch all available models from Ollama.
    """

    print("=" * 50)
    print("Loading models from Ollama...")

    url = f"{base_url}/api/tags"

    try:
        response = requests.get(url)

        if response.status_code != 200:
            print("Failed to fetch models.")
            return []

        data = response.json()

        models = []

        for model in data.get("models", []):
            models.append(model["name"])

        print("Available Models:")
        print(models)

        return models

    except Exception as e:
        print(e)
        return []


def generate_text(base_url, model_name, prompt):
    """
    Send prompt to Ollama and return the response.
    """

    print("=" * 50)
    print("Sending prompt to Ollama...")

    url = f"{base_url}/api/generate"

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False
    }

    try:

        response = requests.post(url, json=payload)

        if response.status_code != 200:
            print("Generation failed.")
            return ""

        data = response.json()

        output = data.get("response", "").strip()

        print("Response received.")
        print(output)

        return output

    except Exception as e:
        print(e)
        return ""