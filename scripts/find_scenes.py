import cv2
import json
import numpy as np
from pathlib import Path

frames_dir = Path(r"C:\Users\HP\.gemini\antigravity-ide\brain\70803940-9743-43be-84f8-4c1d30842611\scratch\frames")
with open(frames_dir / "timeline.json") as f:
    timeline = json.load(f)

print(f"Total frames: {len(timeline)}")

# Detect brightness and major transitions
scenes = []
prev_scene = None

for item in timeline:
    frame_path = frames_dir / item["file"]
    img = cv2.imread(str(frame_path))
    if img is None:
        continue
    
    # Measure average brightness
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    brightness = np.mean(hsv[:, :, 2])
    is_light_theme = brightness > 120
    
    # Check top header text area (breadcrumb)
    # Header is roughly y: 35 to 80, x: 250 to 500
    # Sidebar is roughly x: 0 to 220
    # Main area is x: 220 to 1364, y: 80 to 740
    
    item["brightness"] = round(float(brightness), 1)
    item["theme"] = "Light" if is_light_theme else "Dark"

# Group frames into scenes based on diff threshold or time
current_scene = {
    "start_time": timeline[0]["timestamp"],
    "start_sec": timeline[0]["seconds"],
    "end_time": timeline[0]["timestamp"],
    "end_sec": timeline[0]["seconds"],
    "start_file": timeline[0]["file"],
    "theme": timeline[0]["theme"],
    "frames": [timeline[0]]
}

grouped_scenes = []

for item in timeline[1:]:
    diff = item["diff"]
    theme_changed = item["theme"] != current_scene["theme"]
    
    # Major transition if diff > 35 or theme changed
    if diff > 35.0 or theme_changed:
        current_scene["end_time"] = current_scene["frames"][-1]["timestamp"]
        current_scene["end_sec"] = current_scene["frames"][-1]["seconds"]
        grouped_scenes.append(current_scene)
        current_scene = {
            "start_time": item["timestamp"],
            "start_sec": item["seconds"],
            "end_time": item["timestamp"],
            "end_sec": item["seconds"],
            "start_file": item["file"],
            "theme": item["theme"],
            "frames": [item]
        }
    else:
        current_scene["frames"].append(item)
        current_scene["end_time"] = item["timestamp"]
        current_scene["end_sec"] = item["seconds"]

if current_scene["frames"]:
    grouped_scenes.append(current_scene)

print(f"Detected {len(grouped_scenes)} major scene clusters:")
for i, sc in enumerate(grouped_scenes):
    print(f"Scene {i+1:02d}: {sc['start_time']} - {sc['end_time']} (duration: {sc['end_sec'] - sc['start_sec'] + 3:.1f}s) | Theme: {sc['theme']} | Start: {sc['start_file']}")

with open(frames_dir / "grouped_scenes.json", "w") as f:
    json.dump([{k: v for k, v in sc.items() if k != "frames"} for sc in grouped_scenes], f, indent=2)
