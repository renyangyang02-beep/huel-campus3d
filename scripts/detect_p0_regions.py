# -*- coding: utf-8 -*-
"""在 p0 基准图指定区域内自动检测白色建筑轮廓，输出精确中心与 bbox。"""
import cv2, numpy as np, os
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(ROOT, '..', 'output'))
img = cv2.imread(os.path.join(OUT, 'ref_photos', 'campus_plan_p0.png'))
rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# 区域: name -> (x0,y0,x1,y1)
REGIONS = {
    '校医院':   (205, 655, 265, 735),
    '后勤服务楼': (255, 675, 320, 740),
    '幼儿园':   (380, 660, 490, 730),
    '馨苑3':    (295, 760, 430, 810),
    '馨苑2':    (295, 805, 430, 855),
    '馨苑1':    (295, 850, 430, 900),
    '浴池':     (470, 770, 560, 840),
    '第二食堂':  (430, 830, 560, 940),
    '图书馆':   (420, 1180, 560, 1280),
}
white = ((rgb[:,:,0]>238)&(rgb[:,:,1]>238)&(rgb[:,:,2]>238)).astype(np.uint8)*255
# 闭运算填补文字孔洞
k = cv2.getStructuringElement(cv2.MORPH_RECT,(9,9))
wc = cv2.morphologyEx(white, cv2.MORPH_CLOSE, k)
vis = img.copy()
for name,(x0,y0,x1,y1) in REGIONS.items():
    sub = wc[y0:y1, x0:x1]
    cnts,_ = cv2.findContours(sub, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cand=[]
    for c in cnts:
        a=cv2.contourArea(c)
        if a<80: continue
        bx,by,bw,bh=cv2.boundingRect(c)
        if bw<8 or bh<6: continue
        if a/(bw*bh)<0.4: continue
        M=cv2.moments(c)
        if M['m00']==0: continue
        cx=M['m10']/M['m00']+x0; cy=M['m01']/M['m00']+y0
        cand.append((a,round(cx,1),round(cy,1),[bx+x0,by+y0,bw,bh]))
    cand.sort(key=lambda z:-z[0])
    print('\n%s  region=(%d,%d,%d,%d)'%(name,x0,y0,x1,y1))
    for a,cx,cy,box in cand[:6]:
        print('  area=%6d center=(%6.1f,%6.1f) box=%s'%(a,cx,cy,box))
        cv2.rectangle(vis,(box[0],box[1]),(box[0]+box[2],box[1]+box[3]),(0,0,255),1)
        cv2.putText(vis,'%.0f,%.0f'%(cx,cy),(box[0],box[1]-2),cv2.FONT_HERSHEY_SIMPLEX,0.3,(255,0,0),1)
        cv2.drawMarker(vis,(int(cx),int(cy)),(0,255,255),cv2.MARKER_CROSS,8,1)
cv2.imwrite(os.path.join(OUT,'ref_photos','_p0_detect_regions.png'),vis)
print('\nsaved _p0_detect_regions.png')
