#!/usr/bin/env python3
"""Extract Celery Man review loops without removing the white shirt."""
from pathlib import Path
import argparse
import json,subprocess,tempfile
from PIL import Image,ImageDraw,ImageFilter
HERE=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('video',type=Path)
parser.add_argument('--source-start',type=float,default=0,help='Source timestamp at the start of a trimmed video')
parser.add_argument('--output',type=Path,default=HERE)
args=parser.parse_args()
DEST=args.output
DEST.mkdir(parents=True,exist_ok=True)
spec=json.loads((HERE/'source-clips.json').read_text())
clips=spec['clips']
mattes=json.loads((Path(__file__).parent/'torso-mattes.json').read_text())
details=json.loads((HERE/'foreground-mattes.json').read_text())
for clip in clips:
 x,y,w,h=clip['crop'];frames=[]
 with tempfile.TemporaryDirectory() as tmp:
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(clip['start']-args.source_start),'-i',str(args.video),'-vf',f"fps=15,crop={w}:{h}:{x}:{y},{clip['key']},format=rgba",'-frames:v',str(clip['frames']),str(Path(tmp)/'%03d.png')],check=True)
  for i in range(clip['frames']):
   rgba=Image.open(Path(tmp)/f'{i+1:03}.png').convert('RGBA');alpha=rgba.getchannel('A')
   outside=alpha.point(lambda a:0 if a<255 else 255)
   for bx,by in [(bx,by) for bx in range(w) for by in (0,h-1)]+[(bx,by) for by in range(h) for bx in (0,w-1)]:
    if outside.getpixel((bx,by))==0:ImageDraw.floodfill(outside,(bx,by),128)
   matte=Image.composite(alpha,Image.new('L',(w,h),255),outside.point(lambda v:255 if v==128 else 0))
   # Keep the accepted hip-sway matte. The other two clips use a narrower
   # background key so bright skin and fabric survive without broad masks.
   if clip.get('torso_protection', True):
    anchors={int(k):v for k,v in mattes[clip['name']].items()}
    lo=max(k for k in anchors if k<=i);hi=min((k for k in anchors if k>i),default=lo)
    t=(i-lo)/(hi-lo) if hi>lo else 0
    poly=[(round((a[0]*(1-t)+b[0]*t)*2),round((a[1]*(1-t)+b[1]*t)*2)) for a,b in zip(anchors[lo],anchors[hi])]
    ImageDraw.Draw(matte).polygon(poly,fill=255)
   # Exact-frame patches preserve the shirt where it matches the background.
   # These restore source pixels; they do not paint or interpolate the image.
   for poly in details.get(clip['name'], {}).get(str(i), []):
    ImageDraw.Draw(matte).polygon([(x*2,y*2) for x,y in poly],fill=255)
   if clip.get('edge_inset',0):
    matte=matte.filter(ImageFilter.MinFilter(clip['edge_inset']*2+1))
   rgb=Image.new('RGB',(w,h));rgb.paste(rgba,mask=matte)
   tile=Image.new('RGB',(64,64));tile.paste(rgb.resize(clip['size'],Image.Resampling.LANCZOS),tuple(clip['pos']))
   # Match the firmware's RGB565 precision before enlarging for review.
   channels=tile.split();tile=Image.merge('RGB',(channels[0].point(lambda v:(v>>3)*255//31),channels[1].point(lambda v:(v>>2)*255//63),channels[2].point(lambda v:(v>>3)*255//31)))
   frames.append(tile)
  sheet=Image.new('RGB',(64*8,64*3))
  for i,frame in enumerate(frames):sheet.paste(frame,(i%8*64,i//8*64))
  sheet.save(DEST/('video-'+clip['name']+'.png'))
  palette=sheet.quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
  big=[f.quantize(palette=palette,dither=Image.Dither.NONE).resize((256,256),Image.Resampling.NEAREST) for f in frames]
  durations=[(round((i+1)/15*100)-round(i/15*100))*10 for i in range(len(big))]
  big[0].save(DEST/(clip['name']+'.gif'),save_all=True,append_images=big[1:],duration=durations,loop=0,optimize=False,disposal=2)
  print(clip['name'],len(frames),'frames')
