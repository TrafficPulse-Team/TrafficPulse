import csv, random
from pathlib import Path

random.seed(42)
out=Path("data/sample/traffic_features.csv")
out.parent.mkdir(parents=True,exist_ok=True)
rows=[]
for _ in range(240):
    count=random.randint(2,90); occupancy=random.random()*.8
    speed=max(5,75-occupancy*65+random.gauss(0,7))
    stopped=max(0,int(occupancy*12+random.gauss(0,2)))
    flow=max(1,count*random.uniform(.5,1.5))
    score=.45*occupancy+.25*min(flow/90,1)+.2*min(stopped/12,1)+.1*(1-min(speed/80,1))
    level="LOW" if score<.25 else "MODERATE" if score<.45 else "HIGH" if score<.65 else "SEVERE"
    rows.append([count,occupancy,speed,stopped,flow,level])
with out.open("w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["total_vehicles","road_occupancy","average_speed","stopped_vehicles","vehicle_flow","traffic_level"]); w.writerows(rows)
print(out)
