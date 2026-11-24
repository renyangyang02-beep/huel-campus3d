# -*- coding: utf-8 -*-
"""p0 基准图关键片区高倍放大 + 当前 v19 点位叠加。"""
import json, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(ROOT, '..', 'output'))
REF = os.path.join(OUT, 'ref_photos', 'campus_plan_p0.png')
d = json.load(open(os.path.join(OUT, 'buildings_v19.json'), encoding='utf-8'))
S = d['campus']['scale_m_per_px']; OX, OY = d['campus']['origin_plan_px']

im0 = Image.open(REF).convert('RGB')
dr = ImageDraw.Draw(im0, 'RGBA')
try:
    fontb = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 14)
    fontcn = ImageFont.truetype('C:/Windows/Fonts/simsun.ttc', 13)
except Exception:
    fontb = ImageFont.load_default(); fontcn = fontb
KEY = {'pHOSP','pLOGI','pKIND','pBATH','pDXSY','pDXSY2','pDXSY3'}
for b in d['buildings']:
    p=b['pts']; cx=sum(q[0] for q in p)/len(p); cy=sum(q[1] for q in p)/len(p)
    px=cx/S+OX; py=OY-cy/S
    col=(255,0,0,255) if b['id'] in KEY else (255,140,0,200)
    r=5 if b['id'] in KEY else 2
    dr.ellipse((px-r,py-r,px+r,py+r), fill=col, outline=(255,255,255,255), width=1)
    if b['id'] in KEY:
        dr.text((px+6,py-6), b['id'], fill=(200,0,0,255), font=fontcn, stroke_width=1, stroke_fill=(255,255,255,255))

# 网格（在放大后的图上按原图每50px画线）
def crop_zoom(box, scale, name):
    x0,y0,x1,y1=box
    sub=im0.crop(box).resize((int((x1-x0)*scale), int((y1-y0)*scale)))
    dd=ImageDraw.Draw(sub,'RGBA')
    for x in range(((x0+49)//50)*50, x1, 50):
        X=(x-x0)*scale
        dd.line((X,0,X,sub.height), fill=(255,0,0,80), width=1)
        if x%100==0: dd.text((X+2,2),str(x),fill=(255,0,0,240),font=fontb,stroke_width=1,stroke_fill=(255,255,255,220))
    for y in range(((y0+49)//50)*50, y1, 50):
        Y=(y-y0)*scale
        dd.line((0,Y,sub.width,Y), fill=(0,0,255,80), width=1)
        if y%100==0: dd.text((2,Y+2),str(y),fill=(0,0,255,240),font=fontb,stroke_width=1,stroke_fill=(255,255,255,220))
    sub.save(os.path.join(OUT,'ref_photos',name))
    print(name, sub.size)

crop_zoom((60,580,520,1000), 3, '_p0_zoom_hospital.png')   # 校医院/后勤/幼儿园
crop_zoom((180,740,560,1000), 4, '_p0_zoom_xinyuan.png')    # 馨苑1/2/3/浴池/第二食堂
crop_zoom((380,1120,700,1300), 4, '_p0_zoom_library.png')   # 图书馆锚点
