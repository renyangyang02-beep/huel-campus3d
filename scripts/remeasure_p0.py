# -*- coding: utf-8 -*-
"""扩大区域重测 7 栋补建建筑精确中心（p0 基准图像素）。"""
import cv2, numpy as np, os
ROOT=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.abspath(os.path.join(ROOT,'..','output'))
img=cv2.imread(os.path.join(OUT,'ref_photos','campus_plan_p0.png'))
rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
REGIONS={
 '校医院':   (215,660,270,735),
 '后勤服务楼':(265,685,320,745),
 '幼儿园':   (385,675,475,725),
 '馨苑3':    (320,775,425,805),
 '馨苑2':    (320,818,425,850),
 '馨苑1':    (320,862,425,895),
 '浴池':     (480,818,560,860),
}
white=((rgb[:,:,0]>238)&(rgb[:,:,1]>238)&(rgb[:,:,2]>238)).astype(np.uint8)*255
for ksz in (9,15):
    k=cv2.getStructuringElement(cv2.MORPH_RECT,(ksz,ksz))
    wc=cv2.morphologyEx(white,cv2.MORPH_CLOSE,k)
    print('\n=== close kernel',ksz,'===')
    for name,(x0,y0,x1,y1) in REGIONS.items():
        sub=wc[y0:y1,x0:x1]
        cnts,_=cv2.findContours(sub,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cand=[]
        for c in cnts:
            a=cv2.contourArea(c)
            if a<100: continue
            bx,by,bw,bh=cv2.boundingRect(c)
            if bw<10 or bh<6: continue
            if a/(bw*bh)<0.35: continue
            M=cv2.moments(c)
            if M['m00']==0: continue
            cand.append((a,M['m10']/M['m00']+x0,M['m01']/M['m00']+y0,[bx+x0,by+y0,bw,bh]))
        cand.sort(key=lambda z:-z[0])
        print(name, ' | '.join('area=%d c=(%.1f,%.1f) box=%s'%(a,cx,cy,b) for a,cx,cy,b in cand[:3]))
