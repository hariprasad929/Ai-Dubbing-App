#Now create the transcriber service named transcriber.py.
import whisper

def transcribe_audio(audio_path: str) -> list[dict]:
    model = whisper.load_model("base")
    result = model.transcribe(audio_path, word_timestamps=True)
    segments = []
    for segment in result["segments"]:
        segments.append({
            "start": segment["start"],
            "end": segment["end"],
            "text": segment["text"].strip()
        })
    return segments

