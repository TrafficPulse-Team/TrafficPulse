from typing import Any
from pydantic import BaseModel, Field

class CVResult(BaseModel):
    video_id: str
    total_vehicles: int = 0
    cars: int = 0
    buses: int = 0
    trucks: int = 0
    motorcycles: int = 0
    pedestrians: int = 0
    average_speed: float | None = None
    vehicle_tracks: list[dict[str, Any]] = Field(default_factory=list)
    frame_count: int = 0
    fps: float = 0.0
    road_occupancy: float = 0.0
    vehicle_flow: float = 0.0
    stopped_vehicles: int = 0
    processed_video: str | None = None

class IntelligenceResult(BaseModel):
    traffic_level: str
    congestion_score: float = Field(ge=0.0, le=1.0)
    anomaly_detected: bool = False
    anomaly_type: str | None = None

class AnalysisResult(BaseModel):
    cv: CVResult
    intelligence: IntelligenceResult
