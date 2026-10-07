#!/usr/bin/env python3
"""Package the generated 4x4 sheet as sixteen 64px RGB565 firmware frames."""
from pathlib import Path
import json
from PIL import Image

HERE = Path(__file__).resolve().parent
source = Image.open(HERE / "source.png").convert("RGB")
frames = []
for i in range(16):
    x, y = i % 4, i // 4
    box = (round(x * source.width / 4), round(y * source.height / 4),
           round((x + 1) * source.width / 4), round((y + 1) * source.height / 4))
    sprite = source.crop(box).resize((64, 64), Image.Resampling.LANCZOS)
    frames.append([((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
                   for r, g, b in sprite.getdata()])
with (HERE / "sprites.h").open("w") as out:
    out.write("/* Generated from source.png by pack_sprites.py. */\n")
    out.write("static const uint16_t tayne_sprites[16][4096] = {\n")
    for frame in frames:
        out.write("{\n")
        for j in range(0, len(frame), 32):
            out.write(",".join(f"0x{v:04x}" for v in frame[j:j+32]) + ",\n")
        out.write("},\n")
    out.write("};\n")
(HERE / "asset-info.json").write_text(json.dumps({
    "character": "Tayne", "reference": "https://www.youtube.com/watch?v=a8K6QUPmv8Q",
    "generator": "Built-in imagegen", "format": "RGB565", "frame_size": [64, 64],
    "frames": 16, "flash_bytes": 16*64*64*2,
    "prompt_summary": "Clothed Tayne, black fedora and sunglasses, gold patterned shirt, black trousers and boots; 4x4 consistent full-body retro digitized sprite sheet; eight dance poses, four hat-wobble poses, four conversational poses, black background. Costume reference: supplied Adult Swim video at 0:58."
}, indent=2) + "\n")
print("Packed 16 frames; 131072 bytes of read-only sprite data.")
