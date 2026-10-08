#!/usr/bin/env python3
"""Rebuild Tayne's source-video sheets; Pillow is needed for recorded mattes."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('video', type=Path, help='1920x1080 source video')
parser.add_argument('--source-start', type=float, default=0,
                    help='Original timestamp at the beginning of a trimmed input')
parser.add_argument('--output', type=Path, default=HERE)
parser.add_argument('--clip', action='append', help='Extract only the named clip(s)')
args = parser.parse_args()
spec = json.loads((HERE/'video-clips.json').read_text())
clips = [clip for clip in spec['clips'] if not args.clip or clip['name'] in args.clip]
if not clips or (args.clip and set(args.clip)-{clip['name'] for clip in clips}):
    parser.error('Unknown clip name')
probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                   '-show_entries', 'stream=width,height:format=duration', '-of', 'json', str(args.video)]))
stream = probe['streams'][0]
if [stream['width'], stream['height']] != spec['source_resolution']:
    parser.error('The recorded crops require a 1920x1080 source')
duration = float(probe['format']['duration'])
for clip in clips:
    end = clip['start_seconds'] - args.source_start + clip.get('frames', spec['frames_per_clip'])/spec['fps']
    if end > duration:
        parser.error('Input ends before the requested dance sequence finishes')
args.output.mkdir(parents=True, exist_ok=True)
for clip in clips:
    start = clip['start_seconds'] - args.source_start
    if start < 0:
        parser.error('Input starts after the requested dance sequence')
    x, y, w, h = clip['crop_xywh']
    fw, fh = clip.get('foreground_size', spec['foreground_size'])
    px, py = clip.get('foreground_position', spec['foreground_position'])
    sw, sh = spec['frame_size']
    cols, rows = clip.get('grid', spec['grid'])
    fps = spec['fps']
    key = clip.get('key_filter', f"colorkey={spec['background_key']}")
    if clip.get('preserve_highlights') or 'window_matte' in clip or 'floor_matte' in clip:
        from PIL import Image, ImageDraw
        with tempfile.TemporaryDirectory(prefix='tayne-matte-') as tmp:
            pattern = str(Path(tmp)/'%03d.png')
            count = clip.get('frames', spec['frames_per_clip'])
            subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-ss', str(start),
                            '-i', str(args.video), '-vf', f'fps={fps},crop={w}:{h}:{x}:{y},{key},format=rgba',
                            '-frames:v', str(count), pattern], check=True)
            sheet = Image.new('RGB', (sw*cols, sh*rows))
            for i in range(count):
                rgba = Image.open(Path(tmp)/f'{i+1:03d}.png').convert('RGBA')
                alpha = rgba.getchannel('A')
                matte = alpha.copy()
                if clip.get('preserve_highlights'):
                    # Keep enclosed white reflections in the portrait's sunglasses.
                    outside = alpha.point(lambda a: 0 if a < 255 else 255)
                    boundary = [(bx, by) for bx in range(w) for by in (0, h-1)]
                    boundary += [(bx, by) for by in range(h) for bx in (0, w-1)]
                    for bx, by in boundary:
                        if outside.getpixel((bx, by)) == 0:
                            ImageDraw.floodfill(outside, (bx, by), 128)
                    matte = Image.composite(alpha, Image.new('L', (w,h), 255),
                                            outside.point(lambda v: 255 if v==128 else 0))
                if 'window_matte' in clip:
                    m = clip['window_matte']
                    aw, ah = m['annotation_size']
                    allowed = Image.new('L', (w,h))
                    draw = ImageDraw.Draw(allowed)
                    draw.rectangle((0, 20, m['edge_x']*w/aw, m['foot_y'][i]*h/ah), fill=255)
                    poly = m['arm_polygons'][i]
                    if poly:
                        draw.polygon([(round(a*w/aw), round(b*h/ah)) for a,b in poly], fill=255)
                    matte = Image.composite(matte, Image.new('L', (w,h)), allowed)
                    # His extended hand crosses the orange window behind him.
                    for by in range(h):
                        for bx in range(round(m['edge_x']*w/aw), w):
                            r,g,b,_ = rgba.getpixel((bx,by))
                            if r > 215 and g > 85 and b < 110:
                                matte.putpixel((bx,by), 0)
                if 'floor_matte' in clip:
                    m = clip['floor_matte']
                    aw, ah = m['annotation_size']
                    allowed = Image.new('L', (w,h))
                    draw = ImageDraw.Draw(allowed)
                    draw.rectangle((0, 0, w, m['edge_y']*h/ah), fill=255)
                    draw.polygon([(round(a*w/aw), round(b*h/ah)) for a,b in m['foot_polygons'][i]], fill=255)
                    matte = Image.composite(matte, Image.new('L', (w,h)), allowed)
                    # Below the desktop, the source boots cross a pale title bar.
                    # Preserve dark boot pixels while removing that strip.
                    for by in range(round(m['edge_y']*h/ah), h):
                        for bx in range(w):
                            r,g,b,_ = rgba.getpixel((bx,by))
                            if min(r,g,b) > 80:
                                matte.putpixel((bx,by), 0)
                rgb = Image.new('RGB', (w,h))
                rgb.paste(rgba, mask=matte)
                # Composite before scaling to prevent background-colored fringes.
                rgb = rgb.resize((fw,fh), Image.Resampling.LANCZOS)
                sheet.paste(rgb, ((i%cols)*sw+px, (i//cols)*sh+py))
            sheet.save(args.output/clip['file'])
        print(f"Extracted {clip['name']} with matte from {clip['start_seconds']:.2f}s")
        continue
    filters = (f"[0:v]fps={fps},crop={w}:{h}:{x}:{y},"
               f"colorkey={spec['background_key']}[pet];"
               f"[1:v][pet]overlay=0:0:shortest=1,scale={fw}:{fh}:flags=lanczos,"
               f"pad={sw}:{sh}:{px}:{py}:black,format=rgb24,tile={cols}x{rows}")
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-ss', str(start),
                    '-i', str(args.video), '-f', 'lavfi', '-i', f'color=black:s={w}x{h}:r={fps}',
                    '-filter_complex', filters, '-frames:v', '1', '-y',
                    str(args.output/clip['file'])], check=True)
    print(f"Extracted {clip['name']} from {clip['start_seconds']:.2f}s at {fps} fps")
