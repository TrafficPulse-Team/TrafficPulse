from collections import defaultdict, deque

class BaselineAnomalyDetector:
    """Tracking-feature baseline. It does NOT claim reliable accident detection."""
    def __init__(self, history=8, sudden_stop_ratio=0.25):
        self.positions = defaultdict(lambda: deque(maxlen=history))
        self.sudden_stop_ratio = sudden_stop_ratio

    def update(self, tracks):
        anomalies=[]
        for t in tracks:
            tid=t.get("track_id")
            if tid is None: continue
            self.positions[tid].append(tuple(t["center"]))
            pts=self.positions[tid]
            if len(pts) >= 4:
                d=[]
                for a,b in zip(list(pts)[:-1], list(pts)[1:]):
                    d.append(((b[0]-a[0])**2+(b[1]-a[1])**2)**0.5)
                earlier=max(sum(d[:-2])/max(1,len(d[:-2])), 1e-6)
                recent=sum(d[-2:])/2
                if earlier > 3 and recent/earlier < self.sudden_stop_ratio:
                    anomalies.append({"track_id":tid,"type":"sudden_stop","confidence":0.6})
        return anomalies
