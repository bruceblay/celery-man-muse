#!/usr/bin/env python3
"""Export preview atlases from the actual firmware renderer, without hardware."""
from pathlib import Path
import base64
import argparse
import ctypes as C
import io
import json
import math
import subprocess
import tempfile
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('--character', choices=['tayne', 'celery-man', 'oyster'], default='tayne')
ap.add_argument('--sdk', type=Path, default=ROOT.parent/'muse-gadget-sdk')
ap.add_argument('--size', type=int, default=320, help='GIF width and height, from 1 to 512 pixels')
ap.add_argument('--output', type=Path, help='Output directory; defaults to the character directory')
args = ap.parse_args()
if not 1 <= args.size <= 512:
    ap.error('--size must be between 1 and 512')
names = ['tayne', 'celery-man', 'oyster']
dest = args.output or HERE.parent / args.character
dest.mkdir(parents=True, exist_ok=True)

class Pose(C.Structure):
    _fields_ = [("mode", C.c_int), ("t", C.c_float), ("mode_t", C.c_float),
                ("level", C.c_float), ("happy", C.c_float)]

with tempfile.TemporaryDirectory() as td:
    libpath = Path(td) / "tayne.dylib"
    subprocess.run(["cc", "-O2", "-shared", "-fPIC", "-I", str(ROOT / "sdk-headers"),
                    f'-DMUSE_DEFAULT_SOURCE="{(args.sdk / "esp32/avatar/muse_pixel.c").resolve()}"',
                    str(HERE.parent / "muse_pixel.c"), str(HERE.parent / "muse_default.c"),
                    "-lm", "-o", str(libpath)], check=True)
    lib = C.CDLL(str(libpath))
    lib.muse_character_select(names.index(args.character))
    lib.muse_pixel_render.argtypes = [C.POINTER(Pose)]
    buf = (C.c_uint16 * 4096)()
    display_buf = (C.c_uint16 * (args.size*args.size))()
    def rgb_image(pixels, size):
        raw = bytes(v for c in pixels for v in (((c>>11)&31)*255//31, ((c>>5)&63)*255//63, (c&31)*255//31))
        return Image.frombytes('RGB', (size, size), raw)
    modes = {"idle":1, "listening":2, "thinking":3, "speaking":4, "happy":1, "boot":0, "off":6, "error":5}
    data = {}
    for name, mode in modes.items():
        frames = []
        display_frames = []
        video_dance = args.character == 'tayne' and name in ('idle', 'happy')
        interval = 1/15 if video_dance else 0.08
        n = 24 if video_dance else 40 if name == "happy" else [20,30,20][names.index(args.character)] if name == "idle" else 30
        for i in range(n):
            t = i * interval
            level = max(0, abs(math.sin(t*6.3)) * (0.55+0.45*math.sin(t*1.7+1)))
            happy = max(0, min(1, (2.0-t)/0.4)) if name == "happy" and t >= 0.4 else 0
            if video_dance and name == 'happy':
                happy = 1  # Show the complete source sequence without idle lead-in/recovery.
            pose = Pose(mode, 10+t, t, level if name in ("speaking", "listening") else 0, happy)
            lib.muse_pixel_render(C.byref(pose))
            lib.muse_pixel_set_size(64)
            lib.muse_pixel_scale(buf, 64, 0, 63, 0, 63)
            frames.append(rgb_image(buf, 64))
            if name in ('idle', 'happy'):
                lib.muse_pixel_set_size(args.size)
                lib.muse_pixel_scale(display_buf, args.size, 0, args.size-1, 0, args.size-1)
                display_frames.append(rgb_image(display_buf, args.size))
        atlas = Image.new("RGB", (640, 64*math.ceil(n/10)))
        for i, f in enumerate(frames):
            atlas.paste(f, ((i%10)*64, (i//10)*64))
        encoded = io.BytesIO()
        atlas.save(encoded, format="PNG", optimize=True)
        data[name] = {"frames": n, "frame_ms": interval*1000, "src": "data:image/png;base64,"+base64.b64encode(encoded.getvalue()).decode()}
        if name in ('idle', 'happy'):
            # GIF durations are multiples of 10 ms; distribute rounding error.
            durations = [(round((i+1)*interval*100)-round(i*interval*100))*10 for i in range(n)]
            display_frames[0].save(dest/(name+'.gif'),save_all=True,append_images=display_frames[1:],duration=durations,loop=0)
    (dest / "preview-data.json").write_text(json.dumps(data, separators=(",", ":")))
    print("Exported eight states from the native C renderer.")
