import cv2
import json
import numpy as np
from pathlib import Path

frames_dir = Path(r"C:\Users\HP\.gemini\antigravity-ide\brain\70803940-9743-43be-84f8-4c1d30842611\scratch\frames")
with open(frames_dir / "timeline.json") as f:
    timeline = json.load(f)

# Inspect frame 0 to find coordinates of sidebar and header
img0 = cv2.imread(str(frames_dir / "frame_000_00_00.jpg"))
h, w, _ = img0.shape
print(f"Frame resolution: {w}x{h}")

# Let's save a cropped strip of the sidebar from frame 0 and frame 10 to see button Y positions
cv2.imwrite(str(frames_dir / "crop_sidebar_0.jpg"), img0[:, :220])
cv2.imwrite(str(frames_dir / "crop_header_0.jpg"), img0[:70, 220:])

# Check where the blue accent strip (#38BDF8 or similar blue: BGR ~ [248, 189, 56] in RGB -> BGR [248, 189, 56]) appears in x in [10, 25]
# Let's scan along x in [10, 30], y in [100, 650]
results = []
for item in timeline:
    img = cv2.imread(str(frames_dir / item["file"]))
    if img is None:
        continue
    
    # Check top breadcrumb text area (x: 230 to 550, y: 15 to 55)
    # Check theme: check pixel at (w//2, h//2)
    center_val = img[h//2, w//2].tolist()
    is_dark = np.mean(center_val) < 100
    
    # Check for modals: look for a centered high-contrast rectangle or semi-transparent overlay
    # Detect dialog by checking if center area has a dialog border/header
    
    # Detect active sidebar button by looking for cyan/blue accent strip
    # Accent color in BGR: B > 180, G > 150, R < 100
    sidebar_strip = img[100:650, 10:25]
    # Mask blue/cyan pixels
    b, g, r = cv2.split(sidebar_strip)
    cyan_mask = (b > 180) & (g > 140) & (r < 100)
    y_coords = np.where(cyan_mask)[0]
    
    active_y = None
    if len(y_coords) > 0:
        active_y = int(np.median(y_coords)) + 100
        
    results.append({
        "time": item["timestamp"],
        "seconds": item["seconds"],
        "file": item["file"],
        "is_dark": is_dark,
        "active_y": active_y
    })

print("Sample results (first 20):")
for r in results[:20]:
    print(r)

with open(frames_dir / "screen_scan.json", "w") as f:
    json.dump(results, f, indent=2)
