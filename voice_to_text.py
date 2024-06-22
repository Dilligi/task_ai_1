from pathlib import Path
import whisper

def voice_to_text(file_path: str) -> str:
    model = whisper.load_model("base")
    result = model.transcribe(file_path, fp16=False)
    return result["text"]
