#!/usr/bin/env python3
"""Crop Oyster's actual printout reveal, retaining the paper and printer lip."""
import argparse,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('video',type=Path);p.add_argument('--source-start',type=float,default=0);p.add_argument('--output',type=Path,default=HERE);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
spec={'source':'https://www.youtube.com/watch?v=a8K6QUPmv8Q','start':44.55,'frames':28,'fps':15,'crop':[470,80,1040,1000],'size':[60,58],'pos':[2,3],'processing':'Consecutive original frames. Track the upper paper edge to remove the rear tray and room; retain the original paper, portrait, and printer lip. RGB565 with one shared GIF palette. Original timing, no generated poses.'}
frames=[]
with tempfile.TemporaryDirectory() as tmp:
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(spec['start']-a.source_start),'-i',str(a.video),'-vf','fps=15','-frames:v',str(spec['frames']),str(Path(tmp)/'%03d.png')],check=True)
 for i in range(spec['frames']):
  im=Image.open(Path(tmp)/f'{i+1:03d}.png').convert('RGB');v=np.asarray(im);points=[]
  for x in [400,650,900,1150,1400,1650]:
   col=np.median(v[70:950,x-3:x+4],axis=1);white=(col[:,0]>200)&(col[:,1]>200)&(col[:,2]>210)
   hit=np.flatnonzero(np.convolve(white.astype(int),np.ones(8,dtype=int),'valid')==8)
   if not len(hit):raise ValueError(f'Paper edge missing: frame {i}, x={x}')
   points.append((x,int(hit[0])+74))
  edge=[(220,points[0][1])]+points+[(1780,points[-1][1])]
  mask=Image.new('L',im.size);ImageDraw.Draw(mask).polygon(edge+[(1780,1079),(220,1079)],fill=255)
  cut=Image.new('RGB',im.size);cut.paste(im,mask=mask);cut=cut.crop((470,80,1510,1080))
  tile=Image.new('RGB',(64,64));tile.paste(cut.resize((60,58),Image.Resampling.LANCZOS),(2,3));ch=tile.split();tile=Image.merge('RGB',(ch[0].point(lambda v:(v>>3)*255//31),ch[1].point(lambda v:(v>>2)*255//63),ch[2].point(lambda v:(v>>3)*255//31)));frames.append(tile)
 sheet=Image.new('RGB',(64*7,64*4))
 for i,im in enumerate(frames):sheet.paste(im,(i%7*64,i//7*64))
 sheet.save(a.output/'video-printout.png');palette=sheet.quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
 big=[f.quantize(palette=palette,dither=Image.Dither.NONE).resize((256,256),Image.Resampling.NEAREST) for f in frames];dur=[(round((i+1)/15*100)-round(i/15*100))*10 for i in range(len(frames))]
 big[0].save(a.output/'printout.gif',save_all=True,append_images=big[1:],duration=dur,loop=0,optimize=False,disposal=2)
 frames[-1].resize((256,256),Image.Resampling.NEAREST).save(a.output/'printed-smile.png')
 (a.output/'printout-source.json').write_text(json.dumps(spec,indent=2)+'\n')
 print('Exported',len(frames),'source frames')
