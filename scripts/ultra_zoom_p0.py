# -*- coding: utf-8 -*-
"""超高倍局部图：10x，10px网格，叠加模型当前红点，人工精读。"""
import json, os
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(ROOT, '..', 'output'))
d = json.load(open(os.path.join(OUT, 'buildings_v19.json'), encoding='utf-8'))
S=d['campus']['scale_m_per_px']; OX,OY=d['campus']['origin_plan_px']
im0=Image.open(os.path.join(OUT,'ref_photos','campus_plan_p0.png')).convert('RGB')
dr=ImageDraw.Draw(im0,'RGBA')
KEY={'pHOSP','pLOGI','pKIND','pBATH','pDXSY','pDXSY2','pDXSY3'}
pts={}
for b in d['buildings']:
    if b['id'] in KEY:
        p=b['pts']; cx=sum(q[0] for q in p)/len(p); cy=sum(q[1] for q in p)/len(p)
        px=cx/S+OX; py=OY-cy/S
        pts[b['id']]=(px,py)
        dr.ellipse((px-3,py-3,px+3,py+3),fill=(255,0,0,255),outline=(255,255,255,255),width=1)
try: f=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',11)
except: f=ImageFont.load_default()
def zoom(box, scale, name):
    x0,y0,x1,y1=box
    sub=im0.crop(box).resize(((x1-x0)*scale,(y1-y0)*scale))
    dd=ImageDraw.Draw(sub,'RGBA')
    for x in range(((x0+9)//10)*10,x1,10):
        X=(x-x0)*scale
        dd.line((X,0,X,sub.height),fill=(255,0,0,55),width=1)
        if x%20==0: dd.text((X+1,1),str(x),fill=(255,0,0,235),font=f,stroke_width=1,stroke_fill=(255,255,255,220))
    for y in range(((y0+9)//10)*10,y1,10):
        Y=(y-y0)*scale
        dd.line((0,Y,sub.width,Y),fill=(0,0,255,55),width=1)
        if y%20==0: dd.text((1,Y+1),str(y),fill=(0,0,255,235),font=f,stroke_width=1,stroke_fill=(255,255,255,220))
    sub.save(os.path.join(OUT,'ref_photos',name))
    print(name,sub.size,'model pts:',{k:(round(v[0],1),round(v[1],1)) for k,v in pts.items() if x0<=v[0]<=x1 and y0<=v[1]<=y1})
zoom((215,660,275,735),10,'_p0_10x_hospital.png')
zoom((275,675,325,740),10,'_p0_10x_logi.png')
zoom((395,675,470,720),10,'_p0_10x_kind.png')
zoom((320,775,430,900),7,'_p0_10x_xinyuan.png')
zoom((470,780,560,850),10,'_p0_10x_bath.png')
