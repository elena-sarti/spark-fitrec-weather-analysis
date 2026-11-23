import csv
from datetime import datetime, timezone

station_cell = {}
with open("./datasets/samples/sample_stations.csv", encoding="utf-8") as f:
    for r in csv.reader(f):
        if len(r) >= 5:
            station_cell[r[0]] = (round(float(r[3])), round(float(r[4])))

needed = set()
with open("./datasets/samples/sample_fitrec.csv", encoding="utf-8") as f:
    for r in csv.reader(f):
        d = datetime.fromtimestamp(int(r[4]), tz=timezone.utc)
        needed.add((round(float(r[8])), round(float(r[9])),
                    d.strftime("%Y-%m-%d"), d.hour))

sample_meteo = []
with open("./datasets/big/meteo_hourly.csv", encoding="utf-8") as f:
    for r in csv.reader(f):
        cell = station_cell.get(r[0])
        if cell and (cell[0], cell[1], r[1], int(r[2])) in needed:
            sample_meteo.append(r)

with open("./datasets/samples/sample_meteo_hourly.csv", "w", newline="", encoding="utf-8") as fout:
    csv.writer(fout).writerows(sample_meteo)

print("righe meteo nel nuovo campione:", len(sample_meteo))