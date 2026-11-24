# -*- coding: utf-8 -*-
"""Detect building rooftops from the full-campus satellite image using OpenCV.
Buildings = low-saturation bright grey/white or reddish tiles, with regular
rectangular edges. Vegetation/water/roads are excluded by color + morphology.
"""
import cv2, numpy as np, json, os
ROOT=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.abspath(os.path.join(ROOT,'..','output'))
REF=os.path.join(OUT,'ref_photos')

im=cv2.imread(os.path.join(OUT,'satellite_full_z17.jpg'))
hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
H,S,V=cv2.split(hsv)
h,w=im.shape[:2]

# --- Roof candidate mask ---
# Buildings: low/medium saturation, medium-high value (grey/white roofs)
mask_grey=((S<70)&(V>95)).astype(np.uint8)*255
# Red tile roofs: hue red-ish, medium sat
mask_red=(((H<15)|(H>170))&(S>35)&(S<130)&(V>80)).astype(np.uint8)*255
mask=cv2.bitwise_or(mask_grey,mask_red)

# Restrict to campus polygon-ish bounding region (visual guess), exclude outer farmland/roads
roi=np.zeros((h,w),np.uint8)
# campus roughly x 700-2050, y 50-1450 (from full preview * 2.56)
cv2.rectangle(roi,(760,120),(2050,1480),255,-1)
mask=cv2.bitwise_and(mask,roi)

# Morphology: close small gaps, remove tiny specks
k=cv2.getStructuringElement(cv2.MORPH_RECT,(7,7))
mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,k)
mask=cv2.morphologyEx(mask,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_RECT,(3,3)))

contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
boxes=[]
for c in contours:
    area=cv2.contourArea(c)
    if area<180 or area>60000: continue
    x,y,bw,bh=cv2.boundingRect(c)
    ar=bw/bh if bh else 0
    fill=area/(bw*bh) if bw*bh else 0
    if bw<16 or bh<12: continue
    if fill<0.45: continue          # need fairly solid blob (roof, not road line)
    if ar>8 or ar<0.12: continue    # building-ish aspect ratio
    peri=cv2.arcLength(c,True)
    approx=cv2.approxPolyDP(c,0.06*peri,True)
    if len(approx)<4 or len(approx)>12: continue
    boxes.append({'x':x,'y':y,'w':bw,'h':bh,'area':round(area),'fill':round(fill,2),'n':len(approx)})

print('detected',len(boxes))
json.dump(boxes,open(os.path.join(OUT,'detected_roofs.json'),'w'),ensure_ascii=False)

# visualization
vis=im.copy()
for b in boxes:
    cv2.rectangle(vis,(b['x'],b['y']),(b['x']+b['w'],b['y']+b['h']),(0,0,255),2)
cv2.imwrite(os.path.join(REF,'roofs_detected.jpg'),vis[::2,::2])
print('saved roofs_detected.jpg')
# sort sample
for b in sorted(boxes,key=lambda z:-z['area'])[:15]: print(b)
