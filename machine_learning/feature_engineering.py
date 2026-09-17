FEATURE_COLUMNS = [
    "total_vehicles","road_occupancy","average_speed",
    "stopped_vehicles","vehicle_flow"
]

def cv_result_to_features(cv):
    return {
        "total_vehicles": cv.total_vehicles,
        "road_occupancy": cv.road_occupancy,
        "average_speed": cv.average_speed or 0.0,
        "stopped_vehicles": cv.stopped_vehicles,
        "vehicle_flow": cv.vehicle_flow,
    }
