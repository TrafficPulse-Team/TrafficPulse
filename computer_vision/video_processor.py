from pathlib import Path
import uuid
import cv2
from backend.schemas.traffic import CVResult
from .tracker import UltralyticsTracker
from .vehicle_counter import LineCounter
from .speed_estimator import SpeedEstimator
from .utils import validate_video_path

class VideoProcessor:
    def __init__(self, model_name="yolo11n.pt", confidence=0.35, line_y_ratio=0.50):
        self.model_name = model_name
        self.confidence = confidence
        self.line_y_ratio = line_y_ratio

    def process(self, video_path, output_path=None, meters_per_pixel=None, max_frames=None):
        video_path = validate_video_path(video_path)
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError("OpenCV could not open the video.")

        fps = float(cap.get(cv2.CAP_PROP_FPS) or 0)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if width <= 0 or height <= 0:
            cap.release()
            raise ValueError("Invalid/corrupted video metadata.")

        if output_path is None:
            out_dir = Path("outputs")
            out_dir.mkdir(exist_ok=True)
            output_path = out_dir / f"{video_path.stem}_processed.mp4"
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        writer = cv2.VideoWriter(
            str(output_path), cv2.VideoWriter_fourcc(*"mp4v"),
            fps if fps > 0 else 25.0, (width, height)
        )
        tracker = UltralyticsTracker(self.model_name, self.confidence)
        counter = LineCounter(self.line_y_ratio)
        speed = SpeedEstimator(fps, meters_per_pixel)

        frame_count = 0
        pedestrian_ids = set()
        occupancy_samples = []
        track_summary = {}

        while True:
            ok, frame = cap.read()
            if not ok:
                break
            frame_count += 1
            tracks = tracker.track_frame(frame)
            counts = counter.update(tracks, height)
            speeds = speed.update(tracks)

            box_area = 0.0
            for t in tracks:
                x1,y1,x2,y2 = t["bbox"]
                box_area += max(0,x2-x1)*max(0,y2-y1)
                tid = t["track_id"]
                if t["class"] == "person" and tid is not None:
                    px1, py1, px2, py2 = t["bbox"]

                    is_rider = False

                    for other in tracks:
                        if other["class"] != "motorcycle":
                            continue

                        mx1, my1, mx2, my2 = other["bbox"]

                        person_center_x = (px1 + px2) / 2
                        person_bottom_y = py2

                        bike_width = mx2 - mx1
                        bike_height = my2 - my1

                        close_horizontally = (
                            mx1 - bike_width * 0.5
                            <= person_center_x
                            <= mx2 + bike_width * 0.5
                        )

                        close_vertically = (
                            my1 - bike_height * 1.5
                            <= person_bottom_y
                            <= my2 + bike_height * 0.5
                        )

                        if close_horizontally and close_vertically:
                            is_rider = True
                            break

                    if not is_rider:
                        pedestrian_ids.add(tid)
                if tid is not None:
                    track_summary[tid] = {"track_id":tid,"class":t["class"]}
                color = (0,255,0)
                cv2.rectangle(frame,(int(x1),int(y1)),(int(x2),int(y2)),color,2)
                tag = f'{t["class"]} #{tid if tid is not None else "?"} {t["confidence"]:.2f}'
                if tid in speeds:
                    tag += f" ~{speeds[tid]:.1f} km/h"
                cv2.putText(frame,tag,(int(x1),max(20,int(y1)-6)),
                            cv2.FONT_HERSHEY_SIMPLEX,0.5,color,2)

            line_y = int(height*self.line_y_ratio)
            cv2.line(frame,(0,line_y),(width,line_y),(255,255,0),2)
            occupancy_samples.append(min(1.0, box_area/(width*height)))
            writer.write(frame)
            if max_frames and frame_count >= max_frames:
                break

        cap.release()
        writer.release()
        if frame_count == 0:
            raise ValueError("Video contains no readable frames.")

        duration = frame_count/fps if fps > 0 else 0
        flow = counter.total/(duration/60) if duration > 0 else 0
        occupancy = sum(occupancy_samples)/len(occupancy_samples) if occupancy_samples else 0
        return CVResult(
            video_id=str(uuid.uuid4()),
            total_vehicles=counter.total,
            cars=counts["car"], buses=counts["bus"], trucks=counts["truck"],
            motorcycles=counts["motorcycle"], pedestrians=len(pedestrian_ids),
            average_speed=speed.average_speed(),
            vehicle_tracks=list(track_summary.values()),
            frame_count=frame_count, fps=fps,
            road_occupancy=occupancy, vehicle_flow=flow,
            stopped_vehicles=0,
            processed_video=str(output_path)
        )
