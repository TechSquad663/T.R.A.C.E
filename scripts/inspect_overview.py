import cv2
from pathlib import Path

frames_dir = Path(r"C:\Users\HP\.gemini\antigravity-ide\brain\70803940-9743-43be-84f8-4c1d30842611\scratch\frames")

# Save detailed crops or inspect frames
for i in [20, 24, 28, 32, 35]:
    sec = i * 3
    fname = f"frame_{i:03d}_{sec//60:02d}_{sec%60:02d}.jpg"
    img = cv2.imread(str(frames_dir / fname))
    if img is not None:
        # Check if scrolled down (lower section of Overview: Top Ranked Leads table & Detected Behavioral Patterns)
        # Check lower area y: 400..740
        print(f"Frame {fname} (t={sec}s): mean={img.mean():.1f}")
