import cv2
import numpy as np
from pathlib import Path

frames_dir = Path(r"C:\Users\HP\.gemini\antigravity-ide\brain\70803940-9743-43be-84f8-4c1d30842611\scratch\frames")
img = cv2.imread(str(frames_dir / "crop_sidebar_0.jpg"))

# Let's inspect where text and buttons are located in the sidebar
# In 1364x768, sidebar width is roughly 220px
# Let's save slices of the sidebar buttons
print("Sidebar image shape:", img.shape)

# Let's also look at breadcrumb in header: x in [240, 550], y in [10, 50]
header = cv2.imread(str(frames_dir / "crop_header_0.jpg"))
print("Header image shape:", header.shape)

# Let's save a crop of the breadcrumb area from frame 0, frame 5, frame 10, frame 20, etc.
sample_frames = [0, 5, 10, 15, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130]
for idx in sample_frames:
    fpath = frames_dir / f"frame_{idx:03d}_{idx*3//60:02d}_{idx*3%60:02d}.jpg"
    if fpath.exists():
        im = cv2.imread(str(fpath))
        # Crop header breadcrumb
        crop_bc = im[10:55, 230:520]
        cv2.imwrite(str(frames_dir / f"breadcrumb_{idx:03d}.jpg"), crop_bc)
        # Crop top status / KPIs or title
        crop_title = im[60:120, 240:800]
        cv2.imwrite(str(frames_dir / f"title_{idx:03d}.jpg"), crop_title)

print("Saved sample crops.")
