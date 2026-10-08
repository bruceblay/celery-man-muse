#!/usr/bin/env python3
"""Package original conversation poses and sampled video dances as RGB565."""
from pathlib import Path
import json
from PIL import Image

HERE = Path(__file__).resolve().parent
frames = []
for filename, columns, rows in (("source.png", 4, 4), ("video-idle.png", 8, 3), ("video-happy.png", 8, 3)):
    source = Image.open(HERE / filename).convert("RGB")
    for i in range(columns * rows):
        x, y = i % columns, i // columns
        box = (round(x * source.width / columns), round(y * source.height / rows),
               round((x + 1) * source.width / columns), round((y + 1) * source.height / rows))
        sprite = source.crop(box).resize((64, 64), Image.Resampling.LANCZOS)
        frames.append([((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
                       for r, g, b in sprite.getdata()])
with (HERE / "sprites.h").open("w") as out:
    out.write("/* Packed from source.png, video-idle.png and video-happy.png. See ART.md for provenance. */\n")
    out.write("static const uint16_t tayne_sprites[64][4096] = {\n")
    for frame in frames:
        out.write("{\n")
        for j in range(0, len(frame), 32):
            out.write(",".join(f"0x{v:04x}" for v in frame[j:j+32]) + ",\n")
        out.write("},\n")
    out.write("};\n")
(HERE / "asset-info.json").write_text(json.dumps({
    "character": "Tayne", "reference": "https://www.youtube.com/watch?v=a8K6QUPmv8Q",
    "generator": "Original poses: imagegen; dances: source-video frames via FFmpeg", "format": "RGB565", "frame_size": [64, 64],
    "frames": 64, "flash_bytes": 64*64*64*2,
    "provenance": "video-clips.json; original conversation art: imagegen-prompt.txt"
}, indent=2) + "\n")
print("Packed 64 frames; 524288 bytes of read-only sprite data.")
