# -*- coding: utf-8 -*-
"""v21: 整体位置修整（用户反馈鼎新楼在湖里、建树楼太靠东门）。
最高依据：学校官方《郑东校区平面图》上的建筑标注与轮廓（用户最初指定的基准）。
改动：
1) 鼎新楼A/B(大学生科创中心,2023新建)：原在湖里/宿舍区路上(严重错误)。官方旧图无标注，
   移到教学科研楼东北的"待建建筑"(黄色)区——旧图待建、现已建成的合理落位，避开湖面、
   避开风雅广场、不压现有楼。
2) 综合实验楼：原略偏东，微调贴合官方图综合实验楼白色L形建筑中心。
3) 建树楼：官方图明确标注在东北内环路旁白楼(约px866,687)，原位置(427,113)基本吻合，
   仅微调贴合轮廓中心。注：腾讯POI(34.781985,113.824051)落在南侧待建区，与官方图标注
   冲突，本版以官方图标注为准（官方图为用户指定基准）。
基于 v20 数据。
"""
import json, os
ROOT=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.abspath(os.path.join(ROOT,'..','output'))
d=json.load(open(os.path.join(OUT,'buildings_v20.json'),encoding='utf-8'))
S=1.09

def rect(cx,cy,w,h):
    hw,hh=w/2.0,h/2.0
    return [[round(cx-hw,1),round(cy-hh,1)],[round(cx+hw,1),round(cy-hh,1)],
            [round(cx+hw,1),round(cy+hh,1)],[round(cx-hw,1),round(cy+hh,1)]]
def p2w(px,py): return (round((px-477)*S,1),round((774-py)*S,1))
def setpos(b,cx,cy,w,h,desc):
    p=b['pts']; ox=sum(q[0] for q in p)/len(p); oy=sum(q[1] for q in p)/len(p)
    b['pts']=rect(cx,cy,w,h); b['x'],b['y']=cx,cy; b['desc']=desc
    print('%-8s %-16s (%.0f,%.0f)->(%.0f,%.0f) dx=%.0f dy=%.0f'%(b['id'],b['name'][:14],ox,oy,cx,cy,cx-ox,cy-oy))
byid={b['id']:b for b in d['buildings']}

# 1) 鼎新楼A/B -> 官方图待建区黄楼群（px~690,600/628），避开湖与广场
ax,ay=p2w(690,603); bx,by=p2w(692,640)
setpos(byid['pDX_A'],ax,ay,64,26,
 '鼎新楼A座，大学生科创中心，2023年建成，总建筑面积约3.38万㎡，含大报告厅、创新创业与文创空间。官方平面图（旧版）未标此楼，按图中"待建建筑"区合理落位于教学科研楼东北，方位为推断，非测绘成果。')
setpos(byid['pDX_B'],bx,by,64,26,
 '鼎新楼B座，与A座共同构成大学生科创中心，汇聚创新创业教育、学科交叉与实训空间。按官方平面图待建区合理落位，方位为推断。')

# 2) 综合实验楼 -> 贴合官方图白楼中心 px~697,840
cx,cy=p2w(697,840)
setpos(byid['pZX'],cx,cy,88,52,
 '综合实验楼（知行楼），上机课与实践课场所，橙红格栅+灰砖立面。位置按官方平面图综合实验楼建筑轮廓落位。')

# 3) 建树楼 -> 贴合官方图标注白楼中心 px~866,687（保持东北方位，官方图为准）
jx,jy=p2w(866,687)
setpos(byid['p12'],jx,jy,60,26,
 '建树楼，校友王建树捐建、2014年落成的教学楼（房地产/金融/国贸学院使用）。位置依据学校官方平面图"建树楼"标注落位，位于内环路西侧、弘德路北。')

d['campus']['source']=('建筑位置依据学校官方《郑东校区平面图》建筑标注与轮廓矢量化；'
 '鼎新楼（大学生科创中心）2023新建，官方旧图未标，按待建区合理落位（方位为推断）；'
 '楼名含官方文化名；高度为常见层数示意，非测绘成果。')

dst=os.path.join(OUT,'buildings_v21.json')
json.dump(d,open(dst,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('wrote',dst,'建筑数',len(d['buildings']))
