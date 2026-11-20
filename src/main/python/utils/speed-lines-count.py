import ast

tot, has_speed, has_gps = 0, 0, 0
with open("./datasets/endomondoHR.json", "r", encoding="utf-8") as f:
    for line in f:
        tot += 1
        if "'speed':" in line or '"speed":' in line:
            has_speed += 1
        if "'latitude':" in line or '"latitude":' in line:
            has_gps += 1

print(f"Totale workout: {tot} | Con GPS (lat/lon): {has_gps} | Con campo 'speed': {has_speed}")