#!/usr/bin/env python3
"""Rebuild the two dance sheets from a local copy of the referenced video."""
import argparse
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('video', type=Path, help='1920x1080 source video')
parser.add_argument('--source-start', type=float, default=0,
                    help='Original timestamp at the beginning of a trimmed input')
parser.add_argument('--output', type=Path, default=HERE)
args = parser.parse_args()
spec = json.loads((HERE/'video-clips.json').read_text())
probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                   '-show_entries', 'stream=width,height:format=duration', '-of', 'json', str(args.video)]))
stream = probe['streams'][0]
if [stream['width'], stream['height']] != spec['source_resolution']:
    parser.error('The recorded crops require a 1920x1080 source')
duration = float(probe['format']['duration'])
for clip in spec['clips']:
    end = clip['start_seconds'] - args.source_start + spec['frames_per_clip']/spec['fps']
    if end > duration:
        parser.error('Input ends before the requested dance sequence finishes')
args.output.mkdir(parents=True, exist_ok=True)
for clip in spec['clips']:
    start = clip['start_seconds'] - args.source_start
    if start < 0:
        parser.error('Input starts after the requested dance sequence')
    x, y, w, h = clip['crop_xywh']
    fw, fh = spec['foreground_size']
    px, py = spec['foreground_position']
    sw, sh = spec['frame_size']
    cols, rows = spec['grid']
    fps = spec['fps']
    filters = (f"[0:v]fps={fps},crop={w}:{h}:{x}:{y},"
               f"colorkey={spec['background_key']}[pet];"
               f"[1:v][pet]overlay=0:0:shortest=1,scale={fw}:{fh}:flags=lanczos,"
               f"pad={sw}:{sh}:{px}:{py}:black,format=rgb24,tile={cols}x{rows}")
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-ss', str(start),
                    '-i', str(args.video), '-f', 'lavfi', '-i', f'color=black:s={w}x{h}:r={fps}',
                    '-filter_complex', filters, '-frames:v', '1', '-y',
                    str(args.output/clip['file'])], check=True)
    print(f"Extracted {clip['name']} from {clip['start_seconds']:.2f}s at {fps} fps")
