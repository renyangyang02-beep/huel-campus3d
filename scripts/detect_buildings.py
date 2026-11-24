# -*- coding: utf-8 -*-
"""Auto-detect building rooftops on the full-campus satellite image.
Buildings = bright/low-saturation rectangular blobs (gray roofs, red tile roofs,
blue roofs), excluding green vegetation, dark water and narrow roads.
Outputs candidate rectangles to JSON + an overlay image for manual review.
"""
import os, json
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(ROOT, '..', 'output'))
IMG = os.path.join(OUT, 'satellite_full_z17.jpg')

try:
    import cv2
    HAS_CV = True
except ImportError:
    HAS_CV = False
    print('cv2 unavailable; using numpy-only fallback')

im = np.asarray(Image.open(IMG).convert('RGB'))
H, W = im.shape[:2]
R, G, B = im[:,:,0].astype(int), im[:,:,1].astype(int), im[:,:,2].astype(int)
mx = im.max(axis=2).astype(int); mn = im.min(axis=2).astype(int)
bright = (R+G+B)/3.0
sat = mx - mn

# Building rooftops:
#  - gray/white roofs: bright, low saturation
#  - red tile roofs: R clearly > G,B
#  - blue roofs: B slightly > R, medium sat
gray = (bright > 95) & (sat < 42)
red  = (R > G + 18) & (R > B + 18) & (bright > 70) & (sat < 90)
blue = (B > R + 12) & (B > G + 2) & (bright > 80) & (sat < 70)
mask = (gray | red | blue).astype(np.uint8) * 255

if HAS_CV:
    k = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5,5), np.uint8))
    n, labels, stats, cents = cv2.connectedComponentsWithStats(mask, 8)
    boxes = []
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        if not (180 <= area <= 30000): continue
        if w < 12 or h < 8: continue
        ar = w / float(h)
        if ar < 0.45 or ar > 9: continue
        fill = area / float(w*h)
        if fill < 0.55: continue
        boxes.append(dict(x1=int(x),y1=int(y),x2=int(x+w),y2=int(y+h),
                          area=int(area),fill=round(fill,2)))
else:
    # numpy-only connected components via simple flood fill (slow but ok for ~5M px)
    from collections import deque
    boxes = []
    seen = np.zeros((H,W), bool)
    m = mask > 0
    ys, xs = np.where(m)
    print('candidate pixels', len(xs))
    # downsample to speed up
    step = 2
    small = m[::step,::step]
    sh, sw = small.shape
    seen = np.zeros((sh,sw), bool)
    for sy in range(sh):
        for sx in range(sw):
            if not small[sy,sx] or seen[sy,sx]: continue
            q=deque([(sy,sx)]); seen[sy,sx]=True
            minx=maxx=sx; miny=maxy=sy; cnt=0
            while q:
                cy,cx=q.popleft(); cnt+=1
                if cx<minx:minx=cx
                if cx>maxx:maxx=cx
                if cy<miny:miny=cy
                if cy>maxy:maxy=cy
                for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    ny,nx=cy+dy,cx+dx
                    if 0<=ny<sh and 0<=nx<sw and small[ny,nx] and not seen[ny,nx]:
                        seen[ny,nx]=True; q.append((ny,nx))
            w=(maxx-minx+1)*step; h=(maxy-miny+1)*step
            area=cnt*step*step
            if not (180<=area<=30000) or w<12 or h<8: continue
            ar=w/float(h)
            if ar<0.45 or ar>9 or area/float(w*h)<0.55: continue
            boxes.append(dict(x1=minx*step,y1=miny*step,x2=(maxx+1)*step,y2=(maxy+1)*step,
                              area=int(area)))

# Focus on campus body: drop outskirts farmland/roads by lat/lon band
# campus roughly x 500-2100, y 0-1550 in full image
boxes=[b for b in boxes if 480<b['x1']<2100 and 0<b['y1']<1560]
json.dump(boxes, open(os.path.join(OUT,'detected_boxes.json'),'w'), ensure_ascii=False, indent=1)

# overlay
ov = Image.open(IMG).convert('RGB')
d = ImageDraw.Draw(ov)
try: font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
except: font=ImageFont.load_default()
for i,b in enumerate(boxes):
    d.rectangle((b['x1'],b['y1'],b['x2'],b['y2']),outline=(255,60,60),width=2)
ov.save(os.path.join(OUT,'detected_overlay.jpg'),quality=88)
# downscaled preview
pv = ov.resize((1408,896), Image.LANCZOS)
pv.save(os.path.join(OUT,'ref_photos','detected_preview.png'))
print('DETECTED', len(boxes), 'buildings; cv2=',HAS_CV)
