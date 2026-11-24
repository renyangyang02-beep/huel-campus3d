# -*- coding: utf-8 -*-
"""v20: 基于 p0 官方平面图基准图，逐栋重测并修正 7 栋补建建筑坐标。
核对方法：
  - 配准链官方PDF(1871x2772) -> p0(1263x1871) 用 _H_off2base.npy，图书馆锚点往返误差=0。
  - 世界坐标定义: world_x=(px-562)*1.09, world_y=(1214-py)*1.09, px/py为p0图像素。
  - 7 栋补建建筑用 p0 图白色轮廓自动分割(闭运算+moments)+超高倍人工复核取中心。
修正前误差(米): 校医院+29.5 后勤+27.2 幼儿园+89.0 浴池+22.4 馨苑3+13.7 馨苑2+10.4 馨苑1+5.0
同时按官方图轮廓长宽比修正建筑尺寸(原设定普遍偏小、方向偏竖)。
基于 v19 数据。
"""
import json, os
ROOT=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.abspath(os.path.join(ROOT,'..','output'))
d=json.load(open(os.path.join(OUT,'buildings_v19.json'),encoding='utf-8'))
S=1.09; OX=562; OY=1214

def rect(cx,cy,w,h):
    hw,hh=w/2.0,h/2.0
    return [[round(cx-hw,1),round(cy-hh,1)],[round(cx+hw,1),round(cy-hh,1)],
            [round(cx+hw,1),round(cy+hh,1)],[round(cx-hw,1),round(cy+hh,1)]]

# p0 图像素中心 -> 世界坐标
def w(xpx,ypx):
    return round((xpx-OX)*S,1), round((OY-ypx)*S,1)

FIX={
 'pHOSP': (w(256,706), 40, 22, '校医院'),
 'pLOGI': (w(298,715), 44, 30, '后勤服务楼'),
 'pKIND': (w(429,694), 80, 26, '幼儿园'),
 'pDXSY3':(w(370,791), 82, 24, '笃行书院 馨苑3'),
 'pDXSY2':(w(367,834), 82, 24, '笃行书院 馨苑2'),
 'pDXSY': (w(362,876), 82, 24, '笃行书院 馨苑1'),
 'pBATH': (w(500,840), 38, 28, '浴池'),
}
for b in d['buildings']:
    if b['id'] in FIX:
        (cx,cy),ww,hh,name=FIX[b['id']]
        old_x=round(sum(p[0] for p in b['pts'])/len(b['pts']),1)
        old_y=round(sum(p[1] for p in b['pts'])/len(b['pts']),1)
        b['pts']=rect(cx,cy,ww,hh)
        b['x'],b['y']=cx,cy
        print('%-8s %-14s (%7.1f,%7.1f)->(%7.1f,%7.1f) dx=%+.1f dy=%+.1f size %dx%d'%(
            b['id'],name[:12],old_x,old_y,cx,cy,cx-old_x,cy-old_y,ww,hh))

# 更新校医院 desc 中的方位描述，坐标已按官方图核准
for b in d['buildings']:
    if b['id']=='pHOSP':
        b['desc']='校医院，官方平面图明确标注（带红十字标识），位于西运动场西北、尚德街与东 River 路之间，为师生提供医疗与卫生服务。位置已按官方平面图逐像素核准。'
        b['desc']=b['desc'].replace('东 River 路','东侧道路')

dst=os.path.join(OUT,'buildings_v20.json')
json.dump(d,open(dst,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('wrote',dst,'建筑数',len(d['buildings']))
