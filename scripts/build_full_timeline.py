import cv2
import json
from pathlib import Path

frames_dir = Path(r"C:\Users\HP\.gemini\antigravity-ide\brain\70803940-9743-43be-84f8-4c1d30842611\scratch\frames")
with open(frames_dir / "timeline.json") as f:
    timeline = json.load(f)

# Let's inspect each frame's breadcrumb and active page:
pages = []
for item in timeline:
    img = cv2.imread(str(frames_dir / item["file"]))
    if img is None:
        continue
    
    sec = item["seconds"]
    # Check OBS
    if sec < 2:
        pages.append((sec, item["timestamp"], "OBS Studio (Start Recording)"))
        continue
        
    # Check if a dialog is open (e.g. Investigation Completed, Case Created, Report Generated, Open File Dialog)
    # Check pixel in center of screen
    # Check breadcrumb: x: 230 to 450, y: 15 to 45
    # Let's detect active sidebar item by checking the blue bar at x in [10, 20]:
    b_col = img[150:620, 10:20, 0] # blue channel
    g_col = img[150:620, 10:20, 1]
    r_col = img[150:620, 10:20, 2]
    mask = (b_col > 180) & (g_col > 130) & (r_col < 100)
    ys = mask.nonzero()[0]
    
    active = "Unknown"
    if len(ys) > 5:
        med_y = int(ys.mean()) + 150
        if med_y < 205:
            active = "Overview (Command Center)"
        elif med_y < 245:
            active = "Dataset Ingestion"
        elif med_y < 285:
            active = "Transactions"
        elif med_y < 325:
            active = "Entities & Wallets"
        elif med_y < 365:
            active = "Link Analysis"
        elif med_y < 405:
            active = "Behavioral Anomalies"
        elif med_y < 445:
            active = "Ranked Alerts"
        elif med_y < 485:
            active = "Investigations"
        elif med_y < 535:
            active = "Evidence Chain"
        elif med_y < 575:
            active = "Model Evaluation"
        elif med_y < 615:
            active = "Reports & Exports"
        else:
            active = "System & Settings"
            
    # Check if Light mode
    is_light = img.mean() > 130
    
    # Check dialogs
    dialog = ""
    # In frame 9: Open CSV Dataset dialog (Windows dialog at top left)
    if 24 <= sec <= 30:
        dialog = " [File Dialog: Open CSV Dataset]"
    elif 36 <= sec <= 48:
        dialog = " [Progress Dialog: Pipeline Executing]"
    elif 48 <= sec <= 54:
        dialog = " [Dialog: Investigation Completed]"
    elif 174 <= sec <= 186:
        dialog = " [Dialog: Entity Intelligence Dossier]"
    elif 261 <= sec <= 273:
        dialog = " [Dialog: Case Docket Created]"
    elif 348 <= sec <= 363:
        dialog = " [Dialog: Report Generated (PDF)]"
        
    pages.append((sec, item["timestamp"], active + dialog + (" (Light Mode)" if is_light else "")))

# Print consolidated ranges
ranges = []
cur_label = pages[0][2]
start_t = pages[0][1]
start_s = pages[0][0]

for sec, ts, label in pages[1:]:
    if label != cur_label:
        ranges.append((start_t, ts, start_s, sec, cur_label))
        cur_label = label
        start_t = ts
        start_s = sec

ranges.append((start_t, pages[-1][1], start_s, pages[-1][0], cur_label))

print("TIMELINE BREAKDOWN:")
for r in ranges:
    print(f"{r[0]} - {r[1]} ({r[3]-r[2]:.0f}s): {r[4]}")
