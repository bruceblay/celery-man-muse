#!/usr/bin/env python3
"""Package Tayne's original poses and new dance sheet as 64px RGB565 frames."""
from pathlib import Path
import json
from PIL import Image

HERE = Path(__file__).resolve().parent
frames = []
for filename in ("source.png", "dance.png"):
    source = Image.open(HERE / filename).convert("RGB")
    for i in range(16):
        x, y = i % 4, i // 4
        box = (round(x * source.width / 4), round(y * source.height / 4),
               round((x + 1) * source.width / 4), round((y + 1) * source.height / 4))
        sprite = source.crop(box).resize((64, 64), Image.Resampling.LANCZOS)
        frames.append([((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
                       for r, g, b in sprite.getdata()])
with (HERE / "sprites.h").open("w") as out:
    out.write("/* Generated from source.png and dance.png by pack_sprites.py. */\n")
    out.write("static const uint16_t tayne_sprites[32][4096] = {\n")
    for frame in frames:
        out.write("{\n")
        for j in range(0, len(frame), 32):
            out.write(",".join(f"0x{v:04x}" for v in frame[j:j+32]) + ",\n")
        out.write("},\n")
    out.write("};\n")
(HERE / "asset-info.json").write_text(json.dumps({
    "character": "Tayne", "reference": "https://www.youtube.com/watch?v=a8K6QUPmv8Q",
    "generator": "Built-in imagegen", "format": "RGB565", "frame_size": [64, 64],
    "frames": 32, "flash_bytes": 32*64*64*2,
    "prompt_summary": "Original sixteen poses plus sixteen new shuffle and turn poses. Clothed Tayne, black fedora and sunglasses, gold patterned shirt, black trousers and boots; two 4x4 full-body sprite sheets on black. Exact prompts: imagegen-prompt.txt and dance-prompt.txt."
}, indent=2) + "\n")
print("Packed 32 frames; 262144 bytes of read-only sprite data.")
