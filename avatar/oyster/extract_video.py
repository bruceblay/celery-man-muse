#!/usr/bin/env python3
"""Export source-video Oyster drafts for review before firmware integration."""
import argparse,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('video',type=Path)
p.add_argument('--source-start',type=float,default=0)
p.add_argument('--output',type=Path,default=HERE)
p.add_argument('--qa',type=Path)
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
spec=json.loads((HERE/'source-clips.json').read_text())
for clip in spec['clips']:
 x,y,w,h=clip['crop'];frames=[]
 with tempfile.TemporaryDirectory() as tmp:
  subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(clip['start']-a.source_start),'-i',str(a.video),'-vf',f"fps=15,crop={w}:{h}:{x}:{y}",'-frames:v',str(clip['frames']),str(Path(tmp)/'%03d.png')],check=True)
  for i in range(clip['frames']):
   rgb=Image.open(Path(tmp)/f'{i+1:03d}.png').convert('RGB');v=np.asarray(rgb).astype(np.float32);r,g,b=v[:,:,0],v[:,:,1],v[:,:,2]
   if clip['background']=='pastel':
    background=np.minimum(np.clip((g-200)/15,0,1),np.clip((np.maximum(r,g)-210)/12,0,1))
   else:
    background=np.minimum.reduce([np.clip((b-115)/20,0,1),np.clip((b-g-25)/20,0,1),np.clip((75-(r-b))/20,0,1)])
   alpha=Image.fromarray(np.uint8((1-background)*255))
   if clip['background']=='pastel':
    outside=alpha.point(lambda v:0 if v<255 else 255)
    for bx,by in [(x,y) for x in range(w) for y in (0,h-1)]+[(x,y) for y in range(h) for x in (0,w-1)]:
     if outside.getpixel((bx,by))==0:ImageDraw.floodfill(outside,(bx,by),128)
    # Restore small enclosed highlights, but leave larger background gaps
    # between his hands/legs transparent.
    while True:
     holes=np.asarray(outside)==0
     if not holes.any():break
     hy,hx=np.argwhere(holes)[0];ImageDraw.floodfill(outside,(int(hx),int(hy)),64)
     region=np.asarray(outside)==64
     if np.count_nonzero(region)<=700:
      alpha.paste(255,mask=Image.fromarray(np.uint8(region)*255))
     outside.paste(128,mask=Image.fromarray(np.uint8(region)*255))
   alpha=alpha.filter(ImageFilter.MinFilter(3))
   fg=Image.new('RGB',(w,h));fg.paste(rgb,mask=alpha)
   if a.qa:
    d=a.qa/clip['name'];d.mkdir(parents=True,exist_ok=True);fg.save(d/f'{i:02d}.png')
   tile=Image.new('RGB',(64,64));tile.paste(fg.resize(clip['size'],Image.Resampling.LANCZOS),tuple(clip['pos']))
   ch=tile.split();tile=Image.merge('RGB',(ch[0].point(lambda v:(v>>3)*255//31),ch[1].point(lambda v:(v>>2)*255//63),ch[2].point(lambda v:(v>>3)*255//31)));frames.append(tile)
 sheet=Image.new('RGB',(64*8,64*((len(frames)+7)//8)))
 for i,f in enumerate(frames):sheet.paste(f,(i%8*64,i//8*64))
 sheet.save(a.output/('video-'+clip['name']+'.png'))
 palette=sheet.quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
 big=[f.quantize(palette=palette,dither=Image.Dither.NONE).resize((256,256),Image.Resampling.NEAREST) for f in frames]
 durations=[(round((i+1)/15*100)-round(i/15*100))*10 for i in range(len(big))]
 big[0].save(a.output/(clip['name']+'.gif'),save_all=True,append_images=big[1:],duration=durations,loop=0,optimize=False,disposal=2)
 print(clip['name'],len(frames),'frames')
