# -*- coding: utf-8 -*-
"""把 v19 建筑投影到 web/plan_ground.jpg 底图上，验证坐标链一致性。"""
import json, os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(ROOT, '..', 'output'))
BASE = os.path.join(ROOT, '..', 'web', 'plan_ground.jpg')
d = json.load(open(os.path.join(OUT, 'buildings_v19.json'), encoding='utf-8'))
im = Image.open(BASE).convert('RGB')
dr = ImageDraw.Draw(im, 'RGBA')
try:
    font = ImageFont.truetype('C:/Windows/Fonts/simsun.ttc', 13)
except Exception:
    font = ImageFont.load_default()
S = d['campus']['scale_m_per_px']
OX, OY = d['campus']['origin_plan_px']
KEY = {'pHOSP','pLOGI','pKIND','pBATH','pDXSY','pDXSY2','pDXSY3'}
for b in d['buildings']:
    p = b['pts']
    cx = sum(q[0] for q in p)/len(p); cy = sum(q[1] for q in p)/len(p)
    bx = cx/S + OX; by = OY - cy/S
    col = (255,0,0,255) if b['id'] in KEY else (0,80,255,220)
    r = 7 if b['id'] in KEY else 3
    dr.ellipse((bx-r,by-r,bx+r,by+r), fill=col, outline=(255,255,255,255), width=1)
    if b['id'] in KEY:
        dr.text((bx+8,by-6), b['id']+' '+b['name'], fill=(200,0,0,255), font=font, stroke_width=1, stroke_fill=(255,255,255,255))
im.save(os.path.join(OUT, 'ref_photos', '_verify_v19_on_base.png'))
print('saved', im.size, 'origin', OX, OY, 'scale', S)
