#!/usr/bin/env python3
"""Run the native character renderer under address/undefined-behavior sanitizers."""
import os
from pathlib import Path
import subprocess
import tempfile
import argparse

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--sdk', type=Path, default=ROOT.parent/'muse-gadget-sdk')
args = parser.parse_args()
default_source = (args.sdk/'esp32/avatar/muse_pixel.c').resolve()
if not default_source.is_file():
    parser.error('Clone the pinned Muse SDK first, then pass --sdk /path/to/muse-gadget-sdk')
with tempfile.TemporaryDirectory(prefix='celery-man-verify-') as tmp:
    binary = Path(tmp) / 'verify'
    subprocess.run([
        os.environ.get('CC', 'cc'), '-O1', '-g', '-Wall', '-Werror',
        '-fsanitize=address,undefined', '-fno-sanitize-recover=all',
        '-I', str(ROOT / 'sdk-headers'),
        f'-DMUSE_DEFAULT_SOURCE="{default_source}"',
        str(ROOT / 'avatar/tayne/verify.c'), str(ROOT / 'avatar/muse_pixel.c'),
        str(ROOT / 'avatar/muse_default.c'),
        '-lm', '-o', str(binary),
    ], check=True)
    subprocess.run([str(binary)], check=True)
