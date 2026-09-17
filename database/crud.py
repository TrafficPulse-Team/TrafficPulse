from sqlalchemy.orm import Session
from .models import Video, Analysis, Incident

def create_video(db: Session, video_id: str, filename: str):
    obj=Video(id=video_id,filename=filename)
    db.add(obj); db.commit(); db.refresh(obj); return obj

def get_video(db: Session, video_id: str):
    return db.get(Video, video_id)

def list_videos(db: Session):
    return db.query(Video).order_by(Video.upload_time.desc()).all()

def create_analysis(db: Session, video_id: str, cv, intel):
    obj=Analysis(video_id=video_id,total_vehicles=cv.total_vehicles,cars=cv.cars,
        motorcycles=cv.motorcycles,buses=cv.buses,trucks=cv.trucks,pedestrians=cv.pedestrians,
        average_speed=cv.average_speed,traffic_level=intel.traffic_level,
        congestion_score=intel.congestion_score,anomaly_detected=intel.anomaly_detected)
    db.add(obj); db.commit(); db.refresh(obj); return obj

def get_analysis(db: Session, analysis_id: int):
    return db.get(Analysis,analysis_id)

def list_incidents(db: Session):
    return db.query(Incident).order_by(Incident.id.desc()).all()
