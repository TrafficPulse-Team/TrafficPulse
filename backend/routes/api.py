from pathlib import Path
import shutil, uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from database import crud
from computer_vision.utils import ALLOWED_EXTENSIONS
from computer_vision.video_processor import VideoProcessor
from machine_learning.traffic_classifier import TrafficClassifier

router=APIRouter()
UPLOAD_DIR=Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True,exist_ok=True)

@router.get("/health")
def health(): return {"status":"ok","service":"TrafficPulse AI"}

@router.post("/videos/upload")
def upload_video(file: UploadFile=File(...), db: Session=Depends(get_db)):
    suffix=Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(400,"Unsupported video format.")
    vid=str(uuid.uuid4())
    target=UPLOAD_DIR/f"{vid}{suffix}"
    with target.open("wb") as out: shutil.copyfileobj(file.file,out)
    if target.stat().st_size == 0:
        target.unlink(missing_ok=True); raise HTTPException(400,"Empty upload.")
    crud.create_video(db,vid,file.filename or target.name)
    return {"video_id":vid,"filename":file.filename,"stored_path":str(target)}

@router.post("/videos/{video_id}/analyze")
def analyze(video_id: str, db: Session=Depends(get_db)):
    video=crud.get_video(db,video_id)
    if not video: raise HTTPException(404,"Video not found.")
    matches=list(UPLOAD_DIR.glob(f"{video_id}.*"))
    if not matches: raise HTTPException(404,"Uploaded file is missing.")
    try:
        cv=VideoProcessor().process(matches[0])
        cv.video_id=video_id
        intel=TrafficClassifier().predict(cv)
        analysis=crud.create_analysis(db,video_id,cv,intel)
        video.processing_status="complete"; db.commit()
        return {"analysis_id":analysis.id,"cv":cv.model_dump(),"intelligence":intel.model_dump()}
    except Exception as e:
        video.processing_status="failed"; db.commit()
        raise HTTPException(500,f"Analysis failed: {e}")

@router.get("/videos")
def videos(db: Session=Depends(get_db)):
    return [{"id":v.id,"filename":v.filename,"status":v.processing_status} for v in crud.list_videos(db)]

@router.get("/videos/{video_id}")
def video(video_id: str, db: Session=Depends(get_db)):
    v=crud.get_video(db,video_id)
    if not v: raise HTTPException(404,"Video not found.")
    return {"id":v.id,"filename":v.filename,"status":v.processing_status}

@router.get("/analyses/{analysis_id}")
def analysis(analysis_id: int, db: Session=Depends(get_db)):
    a=crud.get_analysis(db,analysis_id)
    if not a: raise HTTPException(404,"Analysis not found.")
    return {c.name:getattr(a,c.name) for c in a.__table__.columns}

@router.get("/analyses/{analysis_id}/statistics")
def statistics(analysis_id: int, db: Session=Depends(get_db)):
    a=crud.get_analysis(db,analysis_id)
    if not a: raise HTTPException(404,"Analysis not found.")
    return {"total_vehicles":a.total_vehicles,"cars":a.cars,"motorcycles":a.motorcycles,
            "buses":a.buses,"trucks":a.trucks,"pedestrians":a.pedestrians,
            "average_speed":a.average_speed,"traffic_level":a.traffic_level,
            "congestion_score":a.congestion_score}

@router.get("/incidents")
def incidents(db: Session=Depends(get_db)):
    return [{"id":i.id,"video_id":i.video_id,"timestamp":i.timestamp,"type":i.type,
             "confidence":i.confidence,"description":i.description} for i in crud.list_incidents(db)]
