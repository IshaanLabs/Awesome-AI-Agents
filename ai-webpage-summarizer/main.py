import requests
from bs4 import BeautifulSoup
import ollama

MODEL = "llama3.2"
CHUNK_SIZE = 5000
OVERLAP_LINES = 3


def scrape(url):
    print(f"Scraping URL: {url}")
    response = requests.get(url, timeout=10)
    print(f"Status code: {response.status_code}")
    return response.text


def clean(html):
    print("Cleaning HTML content...")
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned = "\n".join(lines)
    print(f"Cleaned text length: {len(cleaned)} characters")
    return cleaned


def chunk_text(text):
    print("Chunking text at paragraph/line boundaries with overlap...")
    lines = text.splitlines()
    chunks = []
    current_lines = []
    current_size = 0
    overlap_buffer = []

    for line in lines:
        current_lines.append(line)
        current_size += len(line)

        if current_size >= CHUNK_SIZE:
            chunks.append("\n".join(current_lines))
            overlap_buffer = current_lines[-OVERLAP_LINES:]
            current_lines = overlap_buffer.copy()
            current_size = sum(len(l) for l in current_lines)

    if current_lines:
        chunks.append("\n".join(current_lines))

    print(f"Total chunks: {len(chunks)}")
    return chunks


def call_llm(prompt):
    response = ollama.chat(model=MODEL, messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]


def summarise(text):
    print("Starting map_reduce summarisation...")
    chunks = chunk_text(text)

    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        print(f"Summarising chunk {i+1}/{len(chunks)}...")
        prompt = f"""You are reading a section of a webpage. Extract the key information clearly and concisely.
                Focus on: main topics, important facts, key arguments, and conclusions.

                Section:
                {chunk}

                Key information from this section:"""
        chunk_summaries.append(call_llm(prompt))

    print("Combining chunk summaries into final summary...")
    combined = "\n\n".join(chunk_summaries)
    final_prompt = f"""You have been given summaries of different sections of a webpage.
                    Combine them into a final, coherent response with:

                    1. A clear paragraph summary (3-5 sentences) covering the main purpose and key takeaways.
                    2. Bullet points (5-7 bullets) highlighting the most important facts.

                    Section summaries:
                    {combined}

                    Final Summary:"""

    result = call_llm(final_prompt)
    print("Summarisation complete.")
    return result


def run(url):
    html = scrape(url)
    text = clean(html)
    summary = summarise(text)
    return summary
