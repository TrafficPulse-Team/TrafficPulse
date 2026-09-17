class LineCounter:
    def __init__(self, y_ratio: float = 0.60):
        if not 0 < y_ratio < 1:
            raise ValueError("y_ratio must be between 0 and 1")
        self.y_ratio = y_ratio
        self.last_side = {}
        self.counted = set()
        self.class_counts = {"car":0,"motorcycle":0,"bus":0,"truck":0}

    def update(self, tracks, frame_height: int):
        line_y = frame_height * self.y_ratio
        for t in tracks:
            tid = t.get("track_id")
            label = t.get("class")
            if tid is None or label not in self.class_counts:
                continue
            cy = t["center"][1]
            side = cy >= line_y
            if tid in self.last_side and self.last_side[tid] != side and tid not in self.counted:
                self.counted.add(tid)
                self.class_counts[label] += 1
            self.last_side[tid] = side
        return dict(self.class_counts)

    @property
    def total(self):
        return sum(self.class_counts.values())
