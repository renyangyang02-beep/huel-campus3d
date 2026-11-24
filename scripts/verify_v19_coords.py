# -*- coding: utf-8 -*-
"""把 v19 模型坐标反投影回官方平面图，生成逐栋核对叠加图。"""
import json, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(ROOT, '..', 'output'))
REF = os.path.join(OUT, 'ref_photos', 'official_plan_from_pdf.png')

d = json.load(open(os.path.join(OUT, 'buildings_v19.json'), encoding='utf-8'))
H = np.load(os.path.join(OUT, '_H_off2base.npy'))
Hinv = np.linalg.inv(H)
im = Image.open(REF).convert('RGB')
dr = ImageDraw.Draw(im)
try:
    font = ImageFont.truetype('C:/Windows/Fonts/simsun.ttc', 22)
    font_s = ImageFont.truetype('C:/Windows/Fonts/simsun.ttc', 17)
except Exception:
    font = ImageFont.load_default(); font_s = font

S = d['campus']['scale_m_per_px']
OX, OY = d['campus']['origin_plan_px']

def world2off(x, y):
    bx = x / S + OX
    by = OY - y / S
    v = Hinv @ np.array([bx, by, 1.0])
    return v[0] / v[2], v[1] / v[2]

KEY = {'pHOSP','pLOGI','pKIND','pBATH','pDXSY','pDXSY2','pDXSY3'}
print('id name world -> official px')
for b in d['buildings']:
    pts = b['pts']
    cx = sum(p[0] for p in pts)/len(pts)
    cy = sum(p[1] for p in pts)/len(pts)
    ox, oy = world2off(cx, cy)
    b['_off'] = (ox, oy)
    if b['id'] in KEY:
        print('%-8s %-16s (%7.1f,%7.1f) -> (%7.1f,%7.1f)' % (b['id'], b['name'], cx, cy, ox, oy))
    col = (255, 0, 0) if b['id'] in KEY else (0, 100, 255)
    r = 11 if b['id'] in KEY else 6
    dr.ellipse((ox-r, oy-r, ox+r, oy+r), fill=col, outline=(255,255,255), width=2)
    if b['id'] in KEY:
        dr.text((ox+14, oy-12), '%s %s' % (b['id'], b['name']), fill=(200,0,0), font=font, stroke_width=2, stroke_fill=(255,255,255))

im.save(os.path.join(OUT, 'ref_photos', '_verify_all_official.png'))
# 西北片区放大
crop = im.crop((250, 1350, 900, 2050)).resize((1300, 1400))
crop.save(os.path.join(OUT, 'ref_photos', '_verify_nw_official.png'))
print('saved overlays')
