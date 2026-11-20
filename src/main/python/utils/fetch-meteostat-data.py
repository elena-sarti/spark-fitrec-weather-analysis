import json
import csv
import gzip
import time
import urllib.request
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

t0 = time.time()

fitrec_cells = set()
with open("./datasets/fitrec_cells.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) >= 2:
            fitrec_cells.add((int(row[0]), int(row[1])))

print(f"Celle caricate da fitrec_cells.csv: {len(fitrec_cells)}", flush=True)

with open("./datasets/full.json", "r", encoding="utf-8") as f:
    all_stations = json.load(f)

stations_per_cell = {}
selected_stations = []

with open("./datasets/stations.csv", "w", newline="", encoding="utf-8") as f_st:
    st_writer = csv.writer(f_st)

    for st in all_stations:
        inv = (st.get("inventory") or {}).get("hourly") or {}
        start, end = inv.get("start"), inv.get("end")
        if not start or not end or start > "2015-12-31" or end < "2011-01-01":
            continue

        loc = st.get("location") or {}
        lat, lon = loc.get("latitude"), loc.get("longitude")
        if lat is None or lon is None:
            continue

        cell = (round(lat), round(lon))
        if cell in fitrec_cells and stations_per_cell.get(cell, 0) < 2:
            stations_per_cell[cell] = stations_per_cell.get(cell, 0) + 1
            st_id = st["id"]
            selected_stations.append(st_id)

            name_obj = st.get("name") or {}
            city = (name_obj.get("en") or next(iter(name_obj.values()), "Unknown")).replace(",", " ")

            st_writer.writerow([
                st_id,
                city,
                st.get("country", ""),
                lat,
                lon,
                loc.get("elevation", 0.0),
                start,
                end
            ])

print(f"stations.csv creato ({len(selected_stations)} stazioni selezionate).", flush=True)

def fetch_station(st_id):
    url = f"https://bulk.meteostat.net/v2/hourly/{st_id}.csv.gz"
    rows = []
    try:
        req = urllib.request.urlopen(url, timeout=15)
        with gzip.GzipFile(fileobj=req) as fin:
            for line in fin:
                cols = line.decode("utf-8").strip().split(",")
                if len(cols) >= 3:
                    date_str, hour_str, temp_str = cols[0], cols[1], cols[2]
                    if "2011-01-01" <= date_str <= "2015-12-31" and temp_str != "":
                        rows.append((st_id, date_str, hour_str, temp_str))
    except Exception:
        pass
    return rows

total_rows = 0
with open("./datasets/meteo_hourly.csv", "w", newline="", encoding="utf-8", buffering=8*1024*1024) as fout:
    writer = csv.writer(fout)
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures = {pool.submit(fetch_station, st_id): st_id for st_id in selected_stations}
        for idx, future in enumerate(as_completed(futures), 1):
            data = future.result()
            if data:
                writer.writerows(data)
                total_rows += len(data)
            if idx % 100 == 0 or idx == len(selected_stations):
                print(f"[{time.time() - t0:.1f}s] Scaricate {idx}/{len(selected_stations)} stazioni ({total_rows:,} righe meteo)...", flush=True)

print(f"Completato in {time.time() - t0:.1f}s! File generati: stations.csv e meteo_hourly.csv", flush=True)