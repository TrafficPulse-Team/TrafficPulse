import argparse

from computer_vision.video_processor import VideoProcessor


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("video")
    parser.add_argument("--meters-per-pixel", type=float, default=None)
    parser.add_argument("--max-frames", type=int, default=None)

    args = parser.parse_args()

    result = VideoProcessor().process(
        args.video,
        meters_per_pixel=args.meters_per_pixel,
        max_frames=args.max_frames
    )

    tracks = result.vehicle_tracks

    vehicle_classes = {"car", "bus", "truck", "motorcycle"}

    vehicle_tracks = [
        track for track in tracks
        if track["class"] in vehicle_classes
    ]

    person_tracks = [
        track for track in tracks
        if track["class"] == "person"
    ]

    track_ids = [
        track["track_id"]
        for track in tracks
        if track["track_id"] is not None
    ]

    print("\n===== TrafficPulse AI Analysis =====")
    print(f"Frames processed: {result.frame_count}")
    print(f"FPS: {result.fps:.2f}")

    print("\n----- Tracked Objects -----")
    print(f"Tracked vehicles: {len(vehicle_tracks)}")
    print(f"Tracked pedestrians: {result.pedestrians}")
    print("---------------------------")

    print("\n----- Line-Crossing Counts -----")
    print(f"Total vehicle crossings: {result.total_vehicles}")
    print(f"Cars crossing: {result.cars}")
    print(f"Motorcycles crossing: {result.motorcycles}")
    print(f"Buses crossing: {result.buses}")
    print(f"Trucks crossing: {result.trucks}")
    print("--------------------------------")

    if result.average_speed is None:
        print("\nEstimated speed: Not available (calibration required)")
    else:
        print(f"\nEstimated speed: {result.average_speed:.2f} km/h")

    print(f"Road occupancy: {result.road_occupancy:.2%}")
    print(f"Vehicle flow: {result.vehicle_flow:.2f} vehicles/min")

    print("\n----- Tracking Diagnostics -----")
    print(f"Unique tracked objects: {len(tracks)}")
    print(f"Unique tracked vehicles: {len(vehicle_tracks)}")
    print(f"Unique person tracks: {len(person_tracks)}")

    if track_ids:
        print(f"Highest assigned track ID: {max(track_ids)}")

    print(f"Vehicles crossing counting line: {result.total_vehicles}")
    print("--------------------------------")

    print(f"\nProcessed video: {result.processed_video}")
    print("====================================")