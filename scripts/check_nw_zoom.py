# -*- coding: utf-8 -*-
"""放大西北片区核对补建建筑 + 周边原有建筑。"""
import json, os
from PIL import Image, ImageDraw, ImageFont
ROOT=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.abspath(os.path.join(ROOT,'..','output'))
d=json.load(open(os.path.join(OUT,'buildings_v19.json'),encoding='utf-8'))
S=d['campus']['scale_m_per_px']; OX,OY=d['campus']['origin_plan_px']
im=Image.open(os.path.join(OUT,'ref_photos','campus_plan_p0.png')).convert('RGB')
dr=ImageDraw.Draw(im,'RGBA')
try: f=ImageFont.truetype('C:/Windows/Fonts/simsun.ttc',11)
except: f=ImageFont.load_default()
for b in d['buildings']:
    p=b['pts']; cx=sum(q[0] for q in p)/len(p); cy=sum(q[1] for q in p)/len(p)
    px=cx/S+OX; py=OY-cy/S
    if not (120<px<620 and 560<py<980): continue
    poly=[(q[0]/S+OX, OY-q[1]/S) for q in p]
    dr.line(poly+[poly[0]], fill=(255,140,0,180), width=1)
    dr.ellipse((px-3,py-3,px+3,py+3),fill=(255,0,0,255))
    dr.text((px+4,py-5),b['id'],fill=(200,0,0,255),font=f,stroke_width=1,stroke_fill=(255,255,255,255))
sub=im.crop((120,560,620,980)).resize((1500,1260))
sub.save(os.path.join(OUT,'ref_photos','_p0_nw_zoom.png'))
print('saved')
