from pathlib import Path

TARGET_CLASSES = {"person", "car", "motorcycle", "bus", "truck"}

class VehicleDetector:
    def __init__(self, model_name: str = "yolo11n.pt", confidence: float = 0.35):
        self.model_name = model_name
        self.confidence = confidence
        self._model = None

    def load(self):
        if self._model is None:
            from ultralytics import YOLO
            self._model = YOLO(self.model_name)
        return self._model

    def detect(self, frame):
        model = self.load()
        result = model.predict(frame, conf=self.confidence, verbose=False)[0]
        detections = []
        names = result.names
        for box in result.boxes:
            cls_id = int(box.cls.item())
            label = names[cls_id]
            if label not in TARGET_CLASSES:
                continue
            x1, y1, x2, y2 = [float(v) for v in box.xyxy[0].tolist()]
            detections.append({
                "class": label,
                "confidence": float(box.conf.item()),
                "bbox": [x1, y1, x2, y2],
            })
        return detections
