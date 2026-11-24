# -*- coding: utf-8 -*-
"""Extract building footprints from the official campus plan (white filled, dark outline)."""
import cv2, numpy as np, json, os
ROOT=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.abspath(os.path.join(ROOT,'..','output')); REF=os.path.join(OUT,'ref_photos')
im=cv2.imread(os.path.join(REF,'campus_plan_p0.png'))
rgb=cv2.cvtColor(im,cv2.COLOR_BGR2RGB)

# campus area bbox in plan coords (from grid): x~90-1180, y~440-1660
x0,y0,x1,y1=90,440,1180,1660
sub=rgb[y0:y1,x0:x1]
h,w=sub.shape[:2]

# White-ish building fill: R,G,B all high and near-equal (paper/building), but paper excluded by enclosure
# 1) detect dark outlines (strokes)
gray=cv2.cvtColor(sub,cv2.COLOR_RGB2GRAY)
# white regions
white=((sub[:,:,0]>235)&(sub[:,:,1]>235)&(sub[:,:,2]>235)).astype(np.uint8)*255
# dark outline mask (dark gray/black strokes)
dark=(gray<110).astype(np.uint8)*255
# dilate dark strokes slightly to ensure closed boundaries
dark_d=cv2.dilate(dark,cv2.getStructuringElement(cv2.MORPH_RECT,(3,3)),iterations=1)
# holes = white regions fully enclosed by dark -> flood fill from border on (255-dark_d)
free=cv2.bitwise_not(dark_d)
ff=free.copy()
mask=np.zeros((h+2,w+2),np.uint8)
cv2.floodFill(ff,mask,(0,0),1)   # outside becomes 1
# enclosed white = white & not-outer
outer=(ff==1)
enclosed=(white>0)&(~outer)
enclosed=(enclosed.astype(np.uint8)*255)
enclosed=cv2.morphologyEx(enclosed,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_RECT,(3,3)))

contours,_=cv2.findContours(enclosed,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
bldgs=[]
for c in contours:
    area=cv2.contourArea(c)
    if area<120: continue
    bx,by,bw_,bh_=cv2.boundingRect(c)
    if bw_<12 or bh_<8: continue
    fill=area/(bw_*bh_)
    if fill<0.35: continue
    peri=cv2.arcLength(c,True)
    approx=cv2.approxPolyDP(c,0.05*peri,True)
    if len(approx)<4 or len(approx)>14: continue
    pts=(approx[:,0,:]+np.array([x0,y0])).tolist()
    bldgs.append({'px':pts,'area':round(area),'box':[bx+x0,by+y0,bw_,bh_]})

print('extracted buildings:',len(bldgs))
json.dump(bldgs,open(os.path.join(OUT,'plan_buildings.json'),'w'),ensure_ascii=False)

vis=rgb.copy()
for b in bldgs:
    p=np.array(b['px'],np.int32)
    cv2.polylines(vis,[p],True,(255,0,0),2)
cv2.imwrite(os.path.join(REF,'plan_extracted.jpg'),cv2.cvtColor(vis,cv2.COLOR_RGB2BGR))
print('saved plan_extracted.jpg')
for b in sorted(bldgs,key=lambda z:-z['area'])[:12]: print(b['box'],'area',b['area'],'pts',len(b['px']))
