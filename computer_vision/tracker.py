class UltralyticsTracker:
    """Thin wrapper around Ultralytics tracking (ByteTrack by default)."""
    def __init__(self, model_name: str = "yolo11n.pt", confidence: float = 0.35):
        from ultralytics import YOLO
        self.model = YOLO(model_name)
        self.confidence = confidence

    def track_frame(self, frame):
        result = self.model.track(
            frame, persist=True, tracker="config/bytetrack_traffic.yaml",
            conf=self.confidence, verbose=False
        )[0]
        tracks = []
        if result.boxes is None:
            return tracks
        for box in result.boxes:
            cls_id = int(box.cls.item())
            label = result.names[cls_id]
            if label not in {"person","car","motorcycle","bus","truck"}:
                continue
            track_id = int(box.id.item()) if box.id is not None else None
            x1, y1, x2, y2 = [float(v) for v in box.xyxy[0].tolist()]
            tracks.append({
                "track_id": track_id,
                "class": label,
                "confidence": float(box.conf.item()),
                "bbox": [x1, y1, x2, y2],
                "center": [(x1+x2)/2, (y1+y2)/2],
            })
        return tracks
