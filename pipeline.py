#Now create the processing pipeline named pipeline.py.
import subprocess
from pathlib import Path
from sqlalchemy.orm import Session
from ..models import DubbingJob
from .transcriber import transcribe_audio
from .translator import translate_to_simple_telugu
from .tts_engine import synthesize_synced_audio

def run_dubbing_pipeline(job_id: str, db: Session, config):
    job = db.query(DubbingJob).filter(DubbingJob.id == job_id).first()
    try:
        work_dir = Path(config.TEMP_DIR) / job_id
        work_dir.mkdir(parents=True, exist_ok=True)
        extracted_wav = work_dir / "source_audio.wav"
        dubbed_wav = work_dir / "telugu_dubbed.wav"
        final_mp4 = Path(config.OUTPUT_DIR) / f"{job_id}_telugu.mp4"

        # 1. Isolate Audio
        job.status = "EXTRACTING"
        db.commit()
        subprocess.run([
            "ffmpeg", "-y", "-i", job.input_path,
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", str(extracted_wav)
        ], check=True)

        # 2. Speech-to-Text with timestamps
        job.status = "TRANSCRIBING"
        db.commit()
        segments = transcribe_audio(str(extracted_wav))

        # 3. Colloquial Telugu Translation
        job.status = "TRANSLATING"
        db.commit()
        telugu_segments = translate_to_simple_telugu(segments, config.GEMINI_API_KEY)

        # 4. Telugu TTS + Segment Time Alignment
        job.status = "SYNTHESIZING"
        db.commit()
        synthesize_synced_audio(telugu_segments, work_dir, str(dubbed_wav))

        # 5. Merge Dubbed Audio with Original Video Stream
        job.status = "MUXING"
        db.commit()
        subprocess.run([
            "ffmpeg", "-y",
            "-i", job.input_path,
            "-i", str(dubbed_wav),
            "-c:v", "copy",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-shortest",
            str(final_mp4)
        ], check=True)

        job.output_path = str(final_mp4)
        job.status = "COMPLETED"
        db.commit()
    except Exception as e:
        job.status = "FAILED"
        job.error_message = str(e)
        db.commit()
