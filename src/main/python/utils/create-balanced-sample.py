import csv
import os

MAX_FITREC_BYTES = 6_500_000   
MAX_WORKOUTS_PER_USER = 3      

selected_rows = []
sample_cells = set()
user_workout_counts = {}
seen_workouts = {}

gender_bytes = {"male": 0, "female": 0}
target_per_gender = MAX_FITREC_BYTES // 2

with open("./datasets/fitrec_flat.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) < 10:
            continue
        user_id, workout_id, sport, gender = row[0], row[1], row[2], row[3].lower()
        if gender not in ("male", "female"):
            continue

        if gender_bytes[gender] >= target_per_gender:
            if all(b >= target_per_gender for b in gender_bytes.values()):
                break
            continue

        if workout_id not in seen_workouts:
            if user_workout_counts.get(user_id, 0) >= MAX_WORKOUTS_PER_USER:
                continue
            seen_workouts[workout_id] = gender
            user_workout_counts[user_id] = user_workout_counts.get(user_id, 0) + 1

        if seen_workouts.get(workout_id) == gender:
            selected_rows.append(row)
            gender_bytes[gender] += sum(len(c) + 1 for c in row)
            lat, lon = float(row[8]), float(row[9])
            sample_cells.add((round(lat), round(lon)))

with open("./datasets/sample_fitrec.csv", "w", newline="", encoding="utf-8") as fout:
    csv.writer(fout).writerows(selected_rows)

sample_station_ids = set()
sample_stations = []
with open("./datasets/stations.csv", "r", encoding="utf-8") as fst:
    for row in csv.reader(fst):
        if len(row) >= 5:
            cell = (round(float(row[3])), round(float(row[4])))
            if cell in sample_cells:
                sample_station_ids.add(row[0])
                sample_stations.append(row)

with open("./datasets/sample_stations.csv", "w", newline="", encoding="utf-8") as fout:
    csv.writer(fout).writerows(sample_stations)

meteo_bytes = 0
MAX_METEO_BYTES = 2_500_000
sample_meteo = []
with open("./datasets/meteo_hourly.csv", "r", encoding="utf-8") as fm:
    for row in csv.reader(fm):
        if row and row[0] in sample_station_ids:
            sample_meteo.append(row)
            meteo_bytes += sum(len(c) + 1 for c in row)
            if meteo_bytes >= MAX_METEO_BYTES:
                break

with open("./datasets/sample_meteo_hourly.csv", "w", newline="", encoding="utf-8") as fout:
    csv.writer(fout).writerows(sample_meteo)
