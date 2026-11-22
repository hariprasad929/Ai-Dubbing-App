#Next, create the speech synthesis engine named tts_engine.py.
import os
from google.cloud import texttospeech
import ffmpeg

def synthesize_synced_audio(segments: list, work_dir: str, output_wav: str):
    client = texttospeech.TextToSpeechClient()
    voice = texttospeech.VoiceSelectionParams(
        language_code="te-IN",
        name="te-IN-Standard-A"
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16
    )

    segment_files = []
    for i, seg in enumerate(segments):
        synthesis_input = texttospeech.SynthesisInput(text=seg.telugu_text)
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        temp_segment = os.path.join(work_dir, f"seg_{i}.wav")
        with open(temp_segment, "wb") as out:
            out.write(response.audio_content)
        
        target_duration = seg.end - seg.start
        stretched_segment = os.path.join(work_dir, f"stretched_{i}.wav")
        
        try:
            probe = ffmpeg.probe(temp_segment)
            duration = float(probe['format']['duration'])
            if duration > 0:
                tempo = duration / target_duration
                tempo = max(0.5, min(2.0, tempo))
                ffmpeg.input(temp_segment).filter('atempo', tempo).output(
                    stretched_segment, loglevel="quiet"
                ).run(overwrite_output=True)
                segment_files.append(stretched_segment)
            else:
                segment_files.append(temp_segment)
        except Exception:
            segment_files.append(temp_segment)

    inputs = [ffmpeg.input(f) for f in segment_files]
    merged = ffmpeg.concat(*inputs, v=0, a=1).node
    ffmpeg.output(merged.audio, output_wav, loglevel="quiet").run(overwrite_output=True)

