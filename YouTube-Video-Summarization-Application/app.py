import gradio as gr
from main import run


def process(youtube_url):
    print(f"[INFO] Received URL from UI: {youtube_url}")
    if not youtube_url.strip():
        return "Please enter a valid YouTube URL.", ""
    transcript, summary = run(youtube_url)
    return transcript, summary


with gr.Blocks() as app:
    gr.Markdown("# YouTube Video Summarizer 🎥")
    gr.Markdown("Powered by Whisper + Llama 2 via Ollama and Haystack")

    with gr.Row():
        url_input = gr.Textbox(label="YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
        submit_btn = gr.Button("Summarize")

    with gr.Row():
        transcript_output = gr.Textbox(label="Transcript", lines=10)
        summary_output = gr.Textbox(label="Summary", lines=10)

    submit_btn.click(fn=process, inputs=url_input, outputs=[transcript_output, summary_output])


if __name__ == "__main__":
    print("[INFO] Launching Gradio app...")
    app.launch()
