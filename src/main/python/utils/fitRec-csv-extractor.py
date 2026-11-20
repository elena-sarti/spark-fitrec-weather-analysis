import ast
import csv
import math
import time

def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    return 2.0 * r * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

t0 = time.time()
fitrec_cells = set()

with open("./datasets/endomondoHR.json", "r", encoding="utf-8") as fin, \
     open("./datasets/fitrec_flat.csv", "w", newline="", encoding="utf-8") as fout:

    writer = csv.writer(fout)
    # Schema: user_id, workout_id, sport, gender, timestamp, speed_kmh, heart_rate, altitude, latitude, longitude

    for line_num, line in enumerate(fin, 1):
        try:
            row = ast.literal_eval(line)
        except Exception:
            continue

        if not all(k in row for k in ("timestamp", "latitude", "longitude")):
            continue

        user_id = row.get("userId", "")
        workout_id = row.get("id", "")
        sport = row.get("sport", "unknown")
        gender = row.get("gender", "unknown")

        ts_list = row["timestamp"]
        lat_list = row["latitude"]
        lon_list = row["longitude"]
        sp_list = row.get("speed")
        hr_list = row.get("heart_rate")
        alt_list = row.get("altitude")

        n = min(len(ts_list), len(lat_list), len(lon_list))

        for i in range(n):
            lat, lon, ts = lat_list[i], lon_list[i], ts_list[i]

            # speed se presente e valido, altrimenti calcolato dai punti GPS consecutivi
            sp = None
            if sp_list is not None and i < len(sp_list) and sp_list[i] is not None:
                sp = float(sp_list[i])
            elif i > 0:
                dt_hours = (ts - ts_list[i - 1]) / 3600.0
                if dt_hours > 0:
                    dist_km = haversine_km(lat_list[i - 1], lon_list[i - 1], lat, lon)
                    sp = dist_km / dt_hours

            # Scartati i punti senza velocità valida o outlier (> 60 km/h)
            if sp is None or sp <= 0.5 or sp > 60.0:
                continue

            hr = hr_list[i] if (hr_list is not None and i < len(hr_list) and hr_list[i] is not None) else ""
            alt = alt_list[i] if (alt_list is not None and i < len(alt_list) and alt_list[i] is not None) else ""

            writer.writerow([user_id, workout_id, sport, gender, ts, round(sp, 3), hr, alt, lat, lon])
            fitrec_cells.add((round(lat), round(lon)))

        if line_num % 25000 == 0:
            print(f"[{time.time() - t0:.1f}s] Processati {line_num}/253020 workout...", flush=True)

with open("fitrec_cells.csv", "w", newline="", encoding="utf-8") as fcells:
    cwriter = csv.writer(fcells)
    for lat_c, lon_c in sorted(fitrec_cells):
        cwriter.writerow([lat_c, lon_c])

print(f"Completato in {time.time() - t0:.1f}s! Celle uniche: {len(fitrec_cells)}", flush=True)