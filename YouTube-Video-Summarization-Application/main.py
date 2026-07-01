import yt_dlp
import whisper
from haystack import Pipeline, Document
from haystack.components.builders import PromptBuilder
from haystack_integrations.components.generators.ollama import OllamaGenerator


def download_audio(url):
    print(f"[INFO] Downloading audio from: {url}")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "audio.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
        }],
        "quiet": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print("[INFO] Audio downloaded to: audio.mp3")
    return "audio.mp3"


def transcribe_audio(file_path):
    print(f"[INFO] Loading Whisper model...")
    model = whisper.load_model("base")
    print(f"[INFO] Transcribing audio: {file_path}")
    result = model.transcribe(file_path)
    transcript = result["text"]
    print(f"[INFO] Transcription complete. Length: {len(transcript)} characters")
    return transcript


def summarize(transcript, model_name="llama2"):
    print(f"[INFO] Building summarization pipeline with model: {model_name}")

    prompt_template = """
    Summarize the following text in a clear and concise way:

    {{ transcript }}

    Summary:
    """

    prompt_builder = PromptBuilder(template=prompt_template)
    llm = OllamaGenerator(model=model_name, url="http://localhost:11434")

    pipeline = Pipeline()
    pipeline.add_component("prompt_builder", prompt_builder)
    pipeline.add_component("llm", llm)
    pipeline.connect("prompt_builder", "llm")

    print(f"[INFO] Running summarization...")
    output = pipeline.run({"prompt_builder": {"transcript": transcript}})
    summary = output["llm"]["replies"][0]
    print(f"[INFO] Summarization complete")
    return summary


def run(url):
    print(f"[INFO] Starting pipeline for URL: {url}")
    file_path = download_audio(url)
    transcript = transcribe_audio(file_path)
    summary = summarize(transcript)
    print(f"[INFO] Pipeline complete")
    return transcript, summary
