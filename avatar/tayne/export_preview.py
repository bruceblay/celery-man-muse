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
args = ap.parse_args()
names = ['tayne', 'celery-man', 'oyster']
dest = HERE.parent / args.character

class Pose(C.Structure):
    _fields_ = [("mode", C.c_int), ("t", C.c_float), ("mode_t", C.c_float),
                ("level", C.c_float), ("happy", C.c_float)]

with tempfile.TemporaryDirectory() as td:
    libpath = Path(td) / "tayne.dylib"
    subprocess.run(["cc", "-O2", "-shared", "-fPIC", "-I", str(ROOT / "sdk-headers"),
                    str(HERE.parent / "muse_pixel.c"), "-lm", "-o", str(libpath)], check=True)
    lib = C.CDLL(str(libpath))
    lib.muse_character_select(names.index(args.character))
    lib.muse_pixel_render.argtypes = [C.POINTER(Pose)]
    lib.muse_pixel_set_size(64)
    buf = (C.c_uint16 * 4096)()
    modes = {"idle":1, "listening":2, "thinking":3, "speaking":4, "happy":1, "boot":0, "off":6, "error":5}
    data = {}
    for name, mode in modes.items():
        frames = []
        n = 40 if name == "happy" else [25,30,20][names.index(args.character)] if name == "idle" else 30
        for i in range(n):
            t = i * 0.08
            level = max(0, abs(math.sin(t*6.3)) * (0.55+0.45*math.sin(t*1.7+1)))
            happy = max(0, min(1, (2.0-t)/0.4)) if name == "happy" and t >= 0.4 else 0
            pose = Pose(mode, 10+t, t, level if name in ("speaking", "listening") else 0, happy)
            lib.muse_pixel_render(C.byref(pose))
            lib.muse_pixel_scale(buf, 64, 0, 63, 0, 63)
            raw = bytes(v for c in buf for v in (((c>>11)&31)*255//31, ((c>>5)&63)*255//63, (c&31)*255//31))
            frames.append(Image.frombytes("RGB", (64,64), raw))
        atlas = Image.new("RGB", (640, 64*math.ceil(n/10)))
        for i, f in enumerate(frames):
            atlas.paste(f, ((i%10)*64, (i//10)*64))
        encoded = io.BytesIO()
        atlas.save(encoded, format="PNG", optimize=True)
        data[name] = {"frames": n, "src": "data:image/png;base64,"+base64.b64encode(encoded.getvalue()).decode()}
        if name in ('idle', 'happy'):
            enlarged=[f.resize((320,320),Image.Resampling.NEAREST) for f in frames]
            enlarged[0].save(dest/(name+'.gif'),save_all=True,append_images=enlarged[1:],duration=80,loop=0)
    (dest / "preview-data.json").write_text(json.dumps(data, separators=(",", ":")))
    print("Exported eight states from the native C renderer.")
