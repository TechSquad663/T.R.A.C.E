import cv2
import os
import sys
from pathlib import Path

video_path = r"C:\Users\HP\Videos\2026-09-27 15-46-25.mp4"
output_dir = Path(r"C:\Users\HP\.gemini\antigravity-ide\brain\70803940-9743-43be-84f8-4c1d30842611\scratch\frames")
output_dir.mkdir(parents=True, exist_ok=True)

cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"Error opening video {video_path}")
    sys.exit(1)

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
duration_sec = total_frames / fps if fps > 0 else 0

print(f"VIDEO_PATH: {video_path}")
print(f"TOTAL_FRAMES: {total_frames}")
print(f"FPS: {fps}")
print(f"WIDTH: {width}")
print(f"HEIGHT: {height}")
print(f"DURATION_SEC: {duration_sec:.2f} ({int(duration_sec // 60)}m {int(duration_sec % 60)}s)")

# Check for audio track by scanning mp4 atoms
def check_audio_track(filepath):
    try:
        with open(filepath, "rb") as f:
            data = f.read(10000000) # first 10MB
            has_soun = b"soun" in data
            has_vide = b"vide" in data
            return has_soun
    except Exception as e:
        return None

has_audio = check_audio_track(video_path)
print(f"HAS_AUDIO_TRACK_MARKER: {has_audio}")

cap.release()
