import csv
from datetime import datetime, timezone

st_cell = {}
with open("./datasets/big/stations.csv", encoding="utf-8") as f:
    for r in csv.reader(f):
        st_cell[r[0]] = (round(float(r[3])), round(float(r[4])))

need = {}
tot = 0
with open("./datasets/samples/sample_fitrec.csv", encoding="utf-8") as f:
    for r in csv.reader(f):
        d = datetime.fromtimestamp(int(r[4]), tz=timezone.utc)
        k = (round(float(r[8])), round(float(r[9])), d.strftime("%Y-%m-%d"), d.hour)
        need[k] = need.get(k, 0) + 1
        tot += 1

found = set()
with open("./datasets/samples/sample_meteo_hourly.csv", encoding="utf-8") as f:
    for r in csv.reader(f):
        c = st_cell.get(r[0])
        if c:
            k = (c[0], c[1], r[1], int(r[2]))
            if k in need:
                found.add(k)

hit = sum(need[k] for k in found)
print(hit, tot, hit / tot)