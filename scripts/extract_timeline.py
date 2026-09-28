import cv2
import os
import numpy as np
from pathlib import Path

video_path = r"C:\Users\HP\Videos\2026-09-27 15-46-25.mp4"
output_dir = Path(r"C:\Users\HP\.gemini\antigravity-ide\brain\70803940-9743-43be-84f8-4c1d30842611\scratch\frames")
output_dir.mkdir(parents=True, exist_ok=True)

cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = total_frames / fps

print(f"Sampling video of {duration:.1f}s ({total_frames} frames)...")

# Sample every 3 seconds to capture all interactions and screens
sample_interval_sec = 3.0
step = int(fps * sample_interval_sec)

prev_thumb = None
saved_count = 0
timeline = []

for frame_idx in range(0, total_frames, step):
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    ret, frame = cap.read()
    if not ret:
        break
    
    sec = frame_idx / fps
    m = int(sec // 60)
    s = int(sec % 60)
    ts_str = f"{m:02d}_{s:02d}"
    
    # Create small thumbnail to detect major visual change
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    thumb = cv2.resize(gray, (160, 90))
    
    diff = 0.0
    if prev_thumb is not None:
        diff = np.mean(np.abs(thumb.astype(float) - prev_thumb.astype(float)))
    prev_thumb = thumb
    
    # Save frame image
    filename = f"frame_{saved_count:03d}_{ts_str}.jpg"
    filepath = output_dir / filename
    cv2.imwrite(str(filepath), frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    
    timeline.append({
        "index": saved_count,
        "frame_idx": frame_idx,
        "timestamp": f"{m:02d}:{s:02d}",
        "seconds": round(sec, 1),
        "diff": round(diff, 2),
        "file": filename
    })
    saved_count += 1

cap.release()
print(f"Extracted {saved_count} frames to {output_dir}")

import json
with open(output_dir / "timeline.json", "w") as f:
    json.dump(timeline, f, indent=2)

print("Timeline JSON saved.")
