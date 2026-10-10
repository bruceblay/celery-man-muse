#!/usr/bin/env python3
"""Render animated README display mockups from the current native C renderer."""
import argparse
import ctypes as C
import json
import math
from pathlib import Path
import subprocess
import tempfile
from PIL import Image, ImageDraw, ImageFont
from boards import BOARDS

ROOT = Path(__file__).resolve().parents[1]
NAMES = ['Tayne', 'Celery Man', 'Oyster']
ACCENTS = ['#f3c971', '#b6d9e9', '#f17d79']
# Exact 15 fps sequences; Oyster's thinking sequence includes the held smile.
TIMELINE = [(0, 1, 'Idle', 24), (1, 1, 'Idle', 24),
            (2, 1, 'Idle', 16), (2, 3, 'Thinking / printout', 37)]
CARD = (360, 408)

class Pose(C.Structure):
    _fields_ = [('mode', C.c_int), ('t', C.c_float), ('mode_t', C.c_float),
                ('level', C.c_float), ('happy', C.c_float)]

def font(size):
    try:
        return ImageFont.truetype('DejaVuSans.ttf', size)
    except OSError:
        return ImageFont.load_default(size=size)

def centered(draw, text, y, size, color):
    draw.text((CARD[0]//2, y), text, font=font(size), fill=color, anchor='mt')

def avatar_top(board):
    # Normal avatar position from the pinned SDK's muse_ui.c. Caption/control
    # drawing is illustrative; this is not an LVGL screenshot or a case model.
    if board.width < 200:
        return (board.height-board.avatar)//2
    ring_in = min(board.width, board.height)//2-10
    cap_bottom = int(math.sqrt(ring_in*ring_in-256*256//4))-3 if board.round else 179
    meter_y = cap_bottom-34-6-9//2
    art_bottom = meter_y-9//2-4
    offset = art_bottom-(board.avatar//2-3*(board.avatar//64))
    return board.height//2-board.avatar//2+offset

def draw_card(board, avatar, character, mode, label, progress):
    panel = Image.new('RGB', (board.width, board.height))
    panel.paste(avatar, ((board.width-board.avatar)//2, avatar_top(board)))
    draw = ImageDraw.Draw(panel)
    accent = '#c2a1ff' if mode == 3 else ACCENTS[character]
    if board.width >= 200:
        diameter = min(board.width,board.height)-8
        x,y=(board.width-diameter)//2,(board.height-diameter)//2
        draw.ellipse((x,y,x+diameter-1,y+diameter-1),outline='#140f22',width=6)
    if board.height >= 200:
        y = 22 if board.width < 200 else 40+(0 if board.round else (board.height-466)//2)
        draw.text((board.width//2,y),'THINKING' if mode==3 else 'READY',
                  font=font(8 if board.width<200 else 16),fill=accent,anchor='mt')
    scale = min(264/board.width,264/board.height)
    pw,ph=round(board.width*scale),round(board.height*scale)
    panel=panel.resize((pw,ph),Image.Resampling.NEAREST)
    card=Image.new('RGB',CARD,'#0d1117');draw=ImageDraw.Draw(card)
    centered(draw,board.name,17,17,'#f0f6fc')
    centered(draw,f'{board.width} x {board.height}  /  '+('round' if board.round else 'rectangular'),43,12,'#8b949e')
    px,py=(CARD[0]-pw)//2,73+(264-ph)//2
    bounds=(px-12,py-12,px+pw+11,py+ph+11)
    if board.round:
        draw.ellipse(bounds,fill='#252b34',outline='#48515e',width=2)
        mask=Image.new('L',panel.size);ImageDraw.Draw(mask).ellipse((0,0,pw-1,ph-1),fill=255)
    else:
        draw.rounded_rectangle(bounds,radius=18,fill='#252b34',outline='#48515e',width=2)
        mask=Image.new('L',panel.size);ImageDraw.Draw(mask).rounded_rectangle((0,0,pw-1,ph-1),radius=4,fill=255)
    card.paste(panel,(px,py),mask)
    centered(draw,NAMES[character]+'  /  '+label,357,15,accent)
    centered(draw,'Display mockup',382,11,'#8b949e')
    draw.rectangle((36,401,324,403),fill='#252b34')
    draw.rectangle((36,401,36+round(288*progress),403),fill=accent)
    return card

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk',type=Path,default=ROOT.parent/'muse-gadget-sdk')
    parser.add_argument('--output',type=Path,default=ROOT/'docs/devices')
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    report={}
    with tempfile.TemporaryDirectory(prefix='muse-device-previews-') as tmp:
        binary=Path(tmp)/'renderer.so'
        subprocess.run(['cc','-O2','-shared','-fPIC','-I',str(ROOT/'sdk-headers'),
                        f'-DMUSE_DEFAULT_SOURCE="{(args.sdk/"esp32/avatar/muse_pixel.c").resolve()}"',
                        str(ROOT/'avatar/muse_pixel.c'),str(ROOT/'avatar/muse_default.c'),
                        '-lm','-o',str(binary)],check=True)
        lib=C.CDLL(str(binary));lib.muse_pixel_render.argtypes=[C.POINTER(Pose)]
        for key,board in BOARDS.items():
            frames=[];pixels=(C.c_uint16*(board.avatar*board.avatar))()
            for character,mode,label,count in TIMELINE:
                lib.muse_character_select(character);lib.muse_pixel_set_size(board.avatar)
                for tick in range(count):
                    t=tick/15
                    pose=Pose(mode,10+t,t,0,0);lib.muse_pixel_render(C.byref(pose))
                    lib.muse_pixel_scale(pixels,board.avatar,0,board.avatar-1,0,board.avatar-1)
                    raw=bytes(v for p in pixels for v in (((p>>11)&31)*255//31,((p>>5)&63)*255//63,(p&31)*255//31))
                    avatar=Image.frombytes('RGB',(board.avatar,board.avatar),raw)
                    frames.append(draw_card(board,avatar,character,mode,label,tick/max(1,count-1)))
            # One palette avoids per-frame color shifts in hands, clothing and text.
            samples=Image.new('RGB',(180*len(frames),204))
            for i,frame in enumerate(frames):samples.paste(frame.resize((180,204)),(180*i,0))
            palette=samples.quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
            indexed=[f.quantize(palette=palette,dither=Image.Dither.NONE) for f in frames]
            durations=[(round((i+1)/15*100)-round(i/15*100))*10 for i in range(len(frames))]
            path=args.output/f'{key}.gif'
            indexed[0].save(path,save_all=True,append_images=indexed[1:],duration=durations,
                            loop=0,optimize=True,disposal=1)
            frames[0].save(args.output/f'{key}.png')
            report[key]={'panel':[board.width,board.height],'avatar':board.avatar,
                         'frames':len(frames),'duration_ms':sum(durations),'bytes':path.stat().st_size}
            print(key,report[key])
    (args.output/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
