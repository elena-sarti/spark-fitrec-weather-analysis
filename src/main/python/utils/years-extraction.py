import json, ast
from datetime import datetime, timezone

years, cells = {}, {}
n = errors = 0
STEP = 50

with open("./datasets/endomondoHR.json") as f:
    for line in f:
        n += 1
        if n % STEP:
            continue
        try:
            try:
                w = json.loads(line)
            except Exception:
                w = ast.literal_eval(line)
            y = datetime.fromtimestamp(w["timestamp"][0], tz=timezone.utc).year
            cell = (round(w["latitude"][0]), round(w["longitude"][0]))
        except Exception:
            errors += 1
            continue
        years[y] = years.get(y, 0) + 1
        cells[cell] = cells.get(cell, 0) + 1

print("righe totali:", n, "| non parsate:", errors)
print("workout per anno:", dict(sorted(years.items())))
print("celle (lat, lon) più frequenti:",
      sorted(cells.items(), key=lambda x: -x[1])[:15])