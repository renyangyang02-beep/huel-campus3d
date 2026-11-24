# -*- coding: utf-8 -*-
"""生成基准图 campus_plan_p0.png 的带网格版本，便于精确读数。"""
import os
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(ROOT, '..', 'output'))
REF = os.path.join(OUT, 'ref_photos', 'campus_plan_p0.png')
im = Image.open(REF).convert('RGB')
dr = ImageDraw.Draw(im, 'RGBA')
try:
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 16)
    fontb = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 19)
except Exception:
    font = ImageFont.load_default(); fontb = font
W, H = im.size
for x in range(0, W, 50):
    dr.line((x, 0, x, H), fill=(255,0,0,70), width=1)
    if x % 100 == 0:
        dr.text((x+2, 2), str(x), fill=(255,0,0,235), font=fontb, stroke_width=1, stroke_fill=(255,255,255,220))
for y in range(0, H, 50):
    dr.line((0, y, W, y), fill=(0,0,255,70), width=1)
    if y % 100 == 0:
        dr.text((2, y+2), str(y), fill=(0,0,255,235), font=fontb, stroke_width=1, stroke_fill=(255,255,255,220))
im.save(os.path.join(OUT, 'ref_photos', '_p0_grid.png'))
# 西北片区放大：p0 图上校医院/后勤/幼儿园/馨苑/浴池
im.crop((80, 180, 700, 1000)).resize((1240, 1640)).save(os.path.join(OUT, 'ref_photos', '_p0_grid_nw.png'))
print('saved', W, H)
