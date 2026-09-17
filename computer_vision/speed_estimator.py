from collections import defaultdict
from math import hypot

class SpeedEstimator:
    """Estimated speed using pixel motion and optional meters-per-pixel calibration."""
    def __init__(self, fps: float, meters_per_pixel: float | None = None):
        self.fps = fps
        self.meters_per_pixel = meters_per_pixel
        self.previous = {}
        self.speeds = defaultdict(list)

    def update(self, tracks):
        if not self.meters_per_pixel or self.fps <= 0:
            return {}
        current = {}
        output = {}
        for t in tracks:
            tid = t.get("track_id")
            if tid is None:
                continue
            center = tuple(t["center"])
            current[tid] = center
            if tid in self.previous:
                dx = center[0] - self.previous[tid][0]
                dy = center[1] - self.previous[tid][1]
                meters = hypot(dx, dy) * self.meters_per_pixel
                kmh = meters * self.fps * 3.6
                self.speeds[tid].append(kmh)
                output[tid] = kmh
        self.previous.update(current)
        return output

    def average_speed(self):
        vals = [v for speeds in self.speeds.values() for v in speeds]
        return sum(vals)/len(vals) if vals else None
