# -*- coding: utf-8 -*-
"""Clean Tencent satellite screenshots for use as georeferenced ground textures."""
from PIL import Image
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, '..', 'output')

SRC16 = os.path.join(OUT, 'satellite_clean2_z16.png')
SRC17 = os.path.join(OUT, 'satellite_clean_z17.png')

def clean(src, dst):
    im = Image.open(src).convert('RGB')
    w, h = im.size
    px = im.load()
    # top-right compass: replace with patch shifted left
    for y in range(0, 80):
        for x in range(w-90, w):
            px[x, y] = px[x-100, y]
    # bottom-left watermark: replace with patch shifted up
    for y in range(h-45, h):
        for x in range(0, 180):
            px[x, y] = px[x, y-60]
    im.save(dst, quality=88)
    print(dst, im.size)

clean(SRC16, os.path.join(OUT, 'satellite_z16.jpg'))
clean(SRC17, os.path.join(OUT, 'satellite_z17.jpg'))
