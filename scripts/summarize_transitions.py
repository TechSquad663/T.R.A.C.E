import json

data = json.load(open(r"C:\Users\HP\.gemini\antigravity-ide\brain\70803940-9743-43be-84f8-4c1d30842611\scratch\frames\frame_analysis.json"))
cur_y = None
cur_th = None
for d in data:
    y = d["active_y"]
    th = d["theme"]
    if y != cur_y or th != cur_th:
        print(f"{d['timestamp']} (t={d['seconds']}s) -> Y={y}, Theme={th}, File={d['file']}")
        cur_y = y
        cur_th = th
