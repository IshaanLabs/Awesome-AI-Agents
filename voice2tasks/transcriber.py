import whisper
import tempfile
import os

model = whisper.load_model("base")
print("Whisper model loaded.")


def transcribe(audio_file):
    """Transcribe an uploaded audio file using local Whisper."""
    print(f"Transcribing audio: {audio_file.name}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_file.read())
        tmp_path = tmp.name

    result = model.transcribe(tmp_path)
    os.unlink(tmp_path)

    text = result["text"]
    print(f"Transcription complete: {text[:100]}...")
    return text
