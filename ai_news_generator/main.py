import os
import gradio as gr
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
from ddgs import DDGS
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

@tool("DuckDuckGo Search")
def duckduckgo_search(query: str) -> str:
    """Search the web using DuckDuckGo and return top results."""
    print(f"[SEARCH] Searching for: {query}")
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=10):
                results.append(f"Title: {r['title']}\nURL: {r['href']}\nSummary: {r['body']}\n")
        if not results:
            print("[SEARCH] No results found")
            return "NO_RESULTS: The search returned no results. Do not proceed or make up information. Stop and report that no data was found."
        print(f"[SEARCH] Found {len(results)} results")
        return "\n---\n".join(results)
    except Exception as e:
        print(f"[SEARCH ERROR] {str(e)}")
        return f"SEARCH_FAILED: Search encountered an error: {str(e)}. Do not make up information. Stop and report the failure."


def generate_content(topic, temperature):
    print(f"[START] Generating content for topic: {topic}")

    llm = LLM(
        model="ollama/qwen3:4b-q4_K_M",
        base_url=f"{OLLAMA_BASE_URL}/v1",
        api_key="ollama",
        temperature=temperature
    )
    print(f"[LLM] Connected to Ollama at {OLLAMA_BASE_URL}")

    research_analyst = Agent(
        role="Senior Research Analyst",
        goal=f"Research and synthesize comprehensive information on {topic} from the web",
        backstory="You're an expert research analyst who finds, analyzes, and synthesizes "
                  "information from the internet. You fact-check, cross-reference, and "
                  "provide well-organized research briefs with proper citations.",
        allow_delegation=False,
        verbose=True,
        tools=[duckduckgo_search],
        llm=llm
    )
    print("[AGENT] Research Analyst created")

    content_writer = Agent(
        role="Content Writer",
        goal="Transform research findings into engaging blog posts while maintaining accuracy",
        backstory="You're a skilled content writer who creates engaging, accessible content "
                  "from technical research, maintaining factual accuracy and proper citations.",
        allow_delegation=False,
        verbose=True,
        llm=llm
    )
    print("[AGENT] Content Writer created")

    research_task = Task(
        description=f"""
            Research the topic: {topic} using the DuckDuckGo Search tool.
            1. You MUST call the search tool at least once before writing anything
            2. If the tool returns NO_RESULTS or SEARCH_FAILED, stop immediately and return exactly: "RESEARCH_FAILED: Could not retrieve data for this topic."
            3. Do NOT make up, invent, or hallucinate any information
            4. Only use facts found in the search results
            5. Organize findings with citations and source URLs from the search results
        """,
        expected_output="""A detailed research report with:
            - Executive summary based only on search results
            - Key trends and developments from sources
            - Verified facts and statistics with source URLs
            - All citations linking to original URLs
            If no results were found, return: RESEARCH_FAILED: Could not retrieve data.""",
        agent=research_analyst
    )
    print("[TASK] Research task created")

    writing_task = Task(
        description="""
            Using the research brief, write an engaging blog post that:
            1. Makes technical content accessible
            2. Keeps all facts and citations accurate
            3. Has a strong intro, structured body, and conclusion
            4. Includes inline citations hyperlinked to source URLs
            5. Ends with a References section
        """,
        expected_output="""A polished blog post in markdown format with:
            - H1 for title, H3 for sub-sections
            - Inline citations linked to source URLs
            - A References section at the end""",
        agent=content_writer
    )
    print("[TASK] Writing task created")

    crew = Crew(
        agents=[research_analyst, content_writer],
        tasks=[research_task, writing_task],
        verbose=True
    )
    print("[CREW] Starting crew execution...")

    result = crew.kickoff()
    print("[DONE] Content generation complete")
    return result.raw


CSS = """
/* ── Reset & full-screen ── */
html, body { margin: 0; padding: 0; }
.gradio-container {
    min-height: 100vh !important;
    max-width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
    background: #0d1117 !important;
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
}

/* hide default gradio footer */
footer { display: none !important; }

/* ── Header ── */
.header {
    background: #161b22;
    padding: 20px 36px;
    border-bottom: 2px solid #238636;
    display: flex;
    align-items: center;
    gap: 14px;
}
.header-title  { font-size: 1.7rem; font-weight: 700; color: #f0f6fc; margin: 0; }
.header-subtitle { font-size: 0.88rem; color: #8b949e; margin: 3px 0 0 0; }

/* ── Sidebar ── */
.sidebar {
    background: #161b22 !important;
    border-right: 1px solid #30363d !important;
    padding: 20px !important;
    min-height: calc(100vh - 80px);
}
.sidebar label, .sidebar .svelte-1gfkn6j {
    color: #c9d1d9 !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
}
.sidebar textarea, .sidebar input[type=text] {
    background: #0d1117 !important;
    border: 1px solid #30363d !important;
    color: #f0f6fc !important;
    border-radius: 6px !important;
    font-size: 0.95rem !important;
}
.sidebar textarea:focus {
    border-color: #238636 !important;
    box-shadow: 0 0 0 3px rgba(35,134,54,0.2) !important;
    outline: none !important;
}

/* ── Generate button ── */
.generate-btn button {
    background: #238636 !important;
    border: 1px solid #2ea043 !important;
    color: #ffffff !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    border-radius: 6px !important;
    padding: 10px 0 !important;
    width: 100% !important;
    transition: background 0.2s !important;
}
.generate-btn button:hover { background: #2ea043 !important; }

/* ── Section labels ── */
.section-label {
    color: #8b949e;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 18px 0 6px 0;
    border-bottom: 1px solid #21262d;
    padding-bottom: 4px;
}

/* ── Output panel ── */
.output-panel {
    background: #ffffff !important;
    padding: 48px 56px !important;
    min-height: calc(100vh - 80px);
    overflow-y: auto;
}

/* Force ALL markdown text to be dark and readable */
.output-panel *,
.output-panel p,
.output-panel li,
.output-panel span,
.output-panel div {
    color: #1a1a1a !important;
}
.output-panel h1 { font-size: 2rem !important; font-weight: 700 !important; color: #111 !important; margin-bottom: 8px !important; border-bottom: 2px solid #238636; padding-bottom: 10px; }
.output-panel h2 { font-size: 1.4rem !important; font-weight: 700 !important; color: #1a1a1a !important; margin-top: 28px !important; }
.output-panel h3 { font-size: 1.15rem !important; font-weight: 600 !important; color: #1a1a1a !important; margin-top: 22px !important; }
.output-panel a  { color: #0969da !important; text-decoration: underline !important; }
.output-panel a:hover { color: #0550ae !important; }
.output-panel strong { color: #111 !important; font-weight: 700 !important; }
.output-panel code {
    background: #f3f4f6 !important;
    color: #d63384 !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    font-size: 0.88em !important;
}
.output-panel blockquote {
    border-left: 4px solid #238636 !important;
    padding-left: 16px !important;
    color: #444 !important;
    margin: 16px 0 !important;
}
.output-panel ul, .output-panel ol { padding-left: 24px !important; }
.output-panel li { margin-bottom: 6px !important; line-height: 1.7 !important; }
.output-panel p  { line-height: 1.8 !important; margin-bottom: 14px !important; }

/* ── Status ── */
.status-idle    { color: #8b949e; font-size: 0.82rem; text-align: center; padding: 6px 0; }
.status-running { color: #d29922; font-size: 0.82rem; text-align: center; padding: 6px 0; }
.status-done    { color: #3fb950; font-size: 0.82rem; text-align: center; padding: 6px 0; }

/* ── Placeholder ── */
.output-placeholder {
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; height: 65vh; gap: 10px; text-align: center;
}
.output-placeholder .icon    { font-size: 3.5rem; }
.output-placeholder .text    { font-size: 1.1rem; font-weight: 600; color: #555; }
.output-placeholder .subtext { font-size: 0.88rem; color: #999; }

/* ── Footer ── */
.footer {
    background: #161b22;
    border-top: 1px solid #30363d;
    padding: 10px 36px;
    text-align: center;
    color: #484f58;
    font-size: 0.78rem;
}

/* ── Slider track ── */
.sidebar input[type=range] { accent-color: #238636; }
"""

def run_ui():
    def on_generate(topic, temperature):
        if not topic.strip():
            return gr.update(), gr.update(visible=False), "⚠️ Please enter a topic."
        try:
            content = generate_content(topic, temperature)
            filepath = f"{topic.lower().replace(' ', '_')}_article.md"
            with open(filepath, "w") as f:
                f.write(content)
            return content, gr.File(value=filepath, visible=True), "✅ Article generated successfully!"
        except Exception as e:
            print(f"[ERROR] {str(e)}")
            return f"An error occurred: {str(e)}", gr.update(visible=False), "❌ Generation failed."

    with gr.Blocks(title="AI News Generator", css=CSS, theme=gr.themes.Base()) as app:

        # Header
        gr.HTML("""
        <div class="header">
            <div>
                <div class="header-title">🤖 AI News Generator</div>
                <div class="header-subtitle">Powered by CrewAI · Qwen3 4B via Ollama · DuckDuckGo Search</div>
            </div>
        </div>
        """)

        with gr.Row(equal_height=True):

            # Left sidebar
            with gr.Column(scale=1, elem_classes="sidebar"):
                gr.HTML('<div class="section-label">📝 Topic</div>')
                topic = gr.Textbox(
                    label="",
                    placeholder="e.g. Kimi K3 newly launched model...",
                    lines=4
                )

                gr.HTML('<div class="section-label">⚙️ Settings</div>')
                temperature = gr.Slider(
                    minimum=0.0, maximum=1.0, value=0.7, step=0.1,
                    label="Temperature",
                    info="Higher = more creative"
                )

                gr.HTML('<div style="margin-top: 24px;"></div>')
                generate_btn = gr.Button("🚀 Generate Article", variant="primary", elem_classes="generate-btn")

                status = gr.Markdown("<div class='status-idle'>Ready to generate</div>")

                gr.HTML('<div class="section-label" style="margin-top:24px;">📥 Export</div>')
                download = gr.File(label="Download Markdown", visible=False, elem_classes="download-btn")

                gr.HTML("""
                <div style="margin-top: 28px; padding: 14px; background: #0d1117; border-radius: 6px; border-left: 3px solid #238636;">
                    <div style="color: #3fb950; font-size: 0.72rem; font-weight: 700; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.08em;">How to use</div>
                    <div style="color: #8b949e; font-size: 0.82rem; line-height: 1.7;">
                        1. Enter a topic above<br>
                        2. Adjust temperature if needed<br>
                        3. Click Generate Article<br>
                        4. Download the result as .md
                    </div>
                </div>
                """)

            # Right output panel
            with gr.Column(scale=3, elem_classes="output-panel"):
                output = gr.Markdown(
                    value="""
<div class="output-placeholder">
    <div class="icon">📰</div>
    <div class="text">Your article will appear here</div>
    <div class="subtext">Enter a topic and click Generate Article to get started</div>
</div>
                    """
                )

        # Footer
        gr.HTML("""
        <div class="footer">
            Built with CrewAI · Gradio · Ollama (Qwen3 4B) · DuckDuckGo
        </div>
        """)

        generate_btn.click(
            fn=lambda: "<div class='status-running'>⏳ Generating... this may take a minute</div>",
            outputs=status
        ).then(
            fn=on_generate,
            inputs=[topic, temperature],
            outputs=[output, download, status]
        )

    print("[UI] Launching Gradio app...")
    app.launch()


if __name__ == "__main__":
    run_ui()
