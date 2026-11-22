#Now create the router for video upload and status checks, named video_router.py.
import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import get_current_user
from ..models import User, DubbingJob
from ..services.pipeline import run_dubbing_pipeline
from ..config import settings

router = APIRouter(prefix="/api/videos", tags=["videos"])

@router.post("/upload")
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Invalid video format")
    job_id = str(uuid.uuid4())
    input_path = Path(settings.UPLOAD_DIR) / f"{job_id}_{file.filename}"
    with input_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    job = DubbingJob(id=job_id, user_id=current_user.id, input_path=str(input_path))
    db.add(job)
    db.commit()

    background_tasks.add_task(run_dubbing_pipeline, job_id, db, settings)
    return {"job_id": job_id, "status": job.status}

@router.get("/status/{job_id}")
def get_job_status(job_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    job = db.query(DubbingJob).filter(DubbingJob.id == job_id, DubbingJob.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job.id, "status": job.status, "error": job.error_message}

@router.get("/download/{job_id}")
def download_dubbed_video(job_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    job = db.query(DubbingJob).filter(DubbingJob.id == job_id, DubbingJob.user_id == current_user.id).first()
    if not job or job.status != "COMPLETED":
        raise HTTPException(status_code=400, detail="Video not ready")
    return FileResponse(job.output_path, media_type="video/mp4", filename=f"telugu_{job_id}.mp4")
``` videos with AI-driven dubbing in your requested language.
