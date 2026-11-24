# -*- coding: utf-8 -*-
"""生成带像素坐标网格的官方平面图，便于人工精确读数。"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(ROOT, '..', 'output'))
REF = os.path.join(OUT, 'ref_photos', 'official_plan_from_pdf.png')
im = Image.open(REF).convert('RGB')
dr = ImageDraw.Draw(im, 'RGBA')
try:
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 20)
except Exception:
    font = ImageFont.load_default()

W, H = im.size
STEP = 100
for x in range(0, W, STEP):
    dr.line((x, 0, x, H), fill=(255, 0, 0, 90), width=1)
    for y in range(0, H, STEP):
        dr.text((x+3, y+3), '%d' % x, fill=(255, 0, 0, 220), font=font)
for y in range(0, H, STEP):
    dr.line((0, y, W, y), fill=(0, 0, 255, 90), width=1)
    dr.text((3, y+3), '%d' % y, fill=(0, 0, 255, 220), font=font)
im.save(os.path.join(OUT, 'ref_photos', '_official_grid.png'))
# 分区：西北（校医院/后勤/幼儿园/馨苑）
im.crop((250, 1000, 1100, 2100)).resize((1275, 1650)).save(
    os.path.join(OUT, 'ref_photos', '_official_grid_nw.png'))
# 全校缩略带网格
im.resize((int(W*0.45), int(H*0.45))).save(os.path.join(OUT, 'ref_photos', '_official_grid_small.png'))
print('ok', W, H)
