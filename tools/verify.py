#!/usr/bin/env python3
"""Run the native character renderer under address/undefined-behavior sanitizers."""
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='celery-man-verify-') as tmp:
    binary = Path(tmp) / 'verify'
    subprocess.run([
        os.environ.get('CC', 'cc'), '-O1', '-g', '-Wall', '-Werror',
        '-fsanitize=address,undefined', '-fno-sanitize-recover=all',
        '-I', str(ROOT / 'sdk-headers'),
        str(ROOT / 'avatar/tayne/verify.c'), str(ROOT / 'avatar/muse_pixel.c'),
        '-lm', '-o', str(binary),
    ], check=True)
    subprocess.run([str(binary)], check=True)
