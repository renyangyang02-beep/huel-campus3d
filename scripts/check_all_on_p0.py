# -*- coding: utf-8 -*-
"""全部建筑投影到 p0 基准图，检查 x/y 中心是否落在官方图建筑轮廓内。"""
import json, os
from PIL import Image, ImageDraw, ImageFont
ROOT=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.abspath(os.path.join(ROOT,'..','output'))
d=json.load(open(os.path.join(OUT,'buildings_v19.json'),encoding='utf-8'))
S=d['campus']['scale_m_per_px']; OX,OY=d['campus']['origin_plan_px']
im=Image.open(os.path.join(OUT,'ref_photos','campus_plan_p0.png')).convert('RGB')
dr=ImageDraw.Draw(im,'RGBA')
try: f=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',10)
except: f=ImageFont.load_default()
for i,b in enumerate(d['buildings']):
    p=b['pts']; cx=sum(q[0] for q in p)/len(p); cy=sum(q[1] for q in p)/len(p)
    px=cx/S+OX; py=OY-cy/S
    # 轮廓
    poly=[(q[0]/S+OX, OY-q[1]/S) for q in p]
    dr.line(poly+[poly[0]], fill=(255,140,0,150), width=1)
    dr.ellipse((px-2,py-2,px+2,py+2),fill=(255,0,0,220))
    dr.text((px+2,py-4),b['id'],fill=(200,0,0,235),font=f)
im.save(os.path.join(OUT,'ref_photos','_p0_all_buildings.png'))
print('saved',len(d['buildings']))
