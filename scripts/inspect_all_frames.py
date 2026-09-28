import cv2
import json
import numpy as np
from pathlib import Path

frames_dir = Path(r"C:\Users\HP\.gemini\antigravity-ide\brain\70803940-9743-43be-84f8-4c1d30842611\scratch\frames")
with open(frames_dir / "timeline.json") as f:
    timeline = json.load(f)

# Sidebar items in order:
# Overview, Dataset Ingestion, Transactions, Entities_Wallets, Link Analysis,
# Behavioral Anomalies, Ranked Alerts, Investigations, Evidence Chain,
# Model Evaluation, Reports_Exports, System_Settings

# Let's write a function to detect which sidebar item is highlighted.
# The blue accent bar is at x roughly 10..18.
# Let's inspect the exact Y positions of the blue bar.

analysis = []

for item in timeline:
    frame_path = frames_dir / item["file"]
    img = cv2.imread(str(frame_path))
    if img is None:
        continue
    
    sec = item["seconds"]
    ts = item["timestamp"]
    
    # Check if OBS is showing (e.g. at 00:00)
    # OBS has red rectangle in center or black theme with specific controls
    is_obs = False
    if sec < 3:
        # Check if OBS text / controls visible
        is_obs = True
    
    # Check theme: brightness
    mean_val = np.mean(img)
    theme = "Light" if mean_val > 130 else "Dark"
    
    # Check Header dataset tag:
    # Tag is located around y: 40..70, x: 330..480
    tag_area = img[35:75, 330:490]
    # Check if empty (dark blue/black) or has text/badge
    has_dataset = False
    # If dataset loaded, the tag has text like "Imported Dataset (569 records)"
    # We can detect if Overview has KPI cards (KPI cards start around y: 90, x: 230)
    # Check pixel variance or presence of KPI boxes
    
    # Sidebar blue bar detection:
    # Sidebar runs x: 8 to 20, y: 160 to 600
    sidebar_col = img[160:600, 10:20]
    b, g, r = cv2.split(sidebar_col)
    blue_mask = (b > 180) & (g > 130) & (r < 100)
    y_matches = np.where(blue_mask)[0]
    
    active_nav = "Unknown"
    active_y = -1
    if len(y_matches) > 10:
        active_y = int(np.median(y_matches)) + 160
        # Button Y ranges (approx 35-40px each starting around 160-180):
        # Let's map approx Y:
        # 160-205: Overview
        # 205-245: Dataset Ingestion
        # 245-285: Transactions
        # 285-325: Entities & Wallets
        # 325-365: Link Analysis
        # 365-405: Behavioral Anomalies
        # 405-445: Ranked Alerts
        # 445-485: Investigations
        # 485-525: Evidence Chain
        # 525-565: Model Evaluation
        # 565-605: Reports & Exports
        # 605-645: System & Settings
        pass
    
    analysis.append({
        "index": item["index"],
        "seconds": sec,
        "timestamp": ts,
        "file": item["file"],
        "is_obs": is_obs,
        "theme": theme,
        "active_y": active_y,
        "diff": item["diff"]
    })

with open(frames_dir / "frame_analysis.json", "w") as f:
    json.dump(analysis, f, indent=2)

print("Frame analysis complete.")
