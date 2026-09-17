from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

def now(): return datetime.now(timezone.utc)

class Video(Base):
    __tablename__="videos"
    id: Mapped[str]=mapped_column(String,primary_key=True)
    filename: Mapped[str]=mapped_column(String)
    upload_time: Mapped[datetime]=mapped_column(DateTime,default=now)
    duration: Mapped[float]=mapped_column(Float,default=0)
    processing_status: Mapped[str]=mapped_column(String,default="uploaded")

class Analysis(Base):
    __tablename__="analyses"
    id: Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    video_id: Mapped[str]=mapped_column(ForeignKey("videos.id"))
    total_vehicles: Mapped[int]=mapped_column(Integer,default=0)
    cars: Mapped[int]=mapped_column(Integer,default=0)
    motorcycles: Mapped[int]=mapped_column(Integer,default=0)
    buses: Mapped[int]=mapped_column(Integer,default=0)
    trucks: Mapped[int]=mapped_column(Integer,default=0)
    pedestrians: Mapped[int]=mapped_column(Integer,default=0)
    average_speed: Mapped[float | None]=mapped_column(Float,nullable=True)
    traffic_level: Mapped[str]=mapped_column(String)
    congestion_score: Mapped[float]=mapped_column(Float)
    anomaly_detected: Mapped[bool]=mapped_column(Boolean,default=False)
    created_at: Mapped[datetime]=mapped_column(DateTime,default=now)

class Incident(Base):
    __tablename__="incidents"
    id: Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    video_id: Mapped[str]=mapped_column(ForeignKey("videos.id"))
    timestamp: Mapped[float]=mapped_column(Float,default=0)
    type: Mapped[str]=mapped_column(String)
    confidence: Mapped[float]=mapped_column(Float,default=0)
    description: Mapped[str]=mapped_column(String,default="")
