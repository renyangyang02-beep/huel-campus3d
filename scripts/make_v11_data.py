# -*- coding: utf-8 -*-
"""Build v11 building dataset from the official campus PLAN (authoritative layout).
Plan pixel -> world: scale 1.09 m/px, origin at library center (562,1214), north up.
Each building keeps its REAL footprint polygon extracted from the plan and a real name.
"""
import json, os
ROOT=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.abspath(os.path.join(ROOT,'..','output'))
S=1.09; OX,OY=562,1214

plan=json.load(open(os.path.join(OUT,'plan_buildings_numbered.json'),encoding='utf-8'))

def name_for(i,cx,cy,area):
    # 精确命名的地标
    exact={
      7:('图书馆','library',12,48),
      1:('第二教学楼','classroom',5,22),
      2:('第一教学楼','classroom',5,22),
      0:('行政办公楼','office',6,26),
      13:('教学科研楼','office',7,30),
      12:('综合实验楼','lab',6,26),
      19:('第三教学楼','classroom',5,22),
      30:('第三教学楼','classroom',5,22),
      4:('第一食堂','canteen',3,14),
    }
    if i in exact: return exact[i]
    if i in (3,10,21): return None  # 广场/运动场，非建筑
    # 书院宿舍区（西部 x<480, y 1000-1220）：博治静 / 通达静
    if 1000<cy<1230 and cx<480:
        if cx<340: return ('博治书院 %d'%((1230-cy)//60+1),'dorm',4,15)
        return ('通达书院 %d'%((1230-cy)//60+1),'dorm',4,15)
    # 书院西区（x 280-460, y 1000-1100 上部）：明理雅
    if 950<cy<1080 and 380<cx<500: return ('明理书院','dorm',4,15)
    # 北部宿舍区（y<760）
    if cy<760:
        if cx<520: return ('弘毅书院 / 致远书院','dorm',6,21)
        return ('经世书院','dorm',6,21)
    # 经世书院怡 / 明理书院怡（y 720-800）
    if 700<cy<820:
        if cx<560: return ('经世书院','dorm',4,15)
        return ('明理书院','dorm',4,15)
    return ('教学配套','office',4,16)

def to_world(px):
    return [(round((x-OX)*S,1), round((OY-y)*S,1)) for x,y in px]

buildings=[]
for o in plan:
    i=o['idx']; info=name_for(i,o['cx'],o['cy'],o['area'])
    if not info: continue
    name,kind,floors,h=info
    pts=to_world(o['px'])
    # 去重同名（如两个第三教学楼）
    bid='p%02d'%i
    roof='ding' if kind=='library' else 'flat'
    buildings.append({
      'id':bid,'name':name,'kind':kind,'floors':floors,'height':h,
      'pts':pts,'plan_idx':i,'roof':roof,
      'desc':'位于郑东校区，按学校官方平面图真实位置与轮廓复原。',
      'interior':'该建筑内部空间示意可在三维模式中查看。'
    })

meta={
 'name':'河南财经政法大学（郑东校区）',
 'lat0':34.7837,'lon0':113.8206,
 'address':'河南省郑州市金水东路180号',
 'source':'建筑位置、轮廓、名称依据学校官方《郑东校区平面图》矢量化；高度按建筑类型与常见层数示意，非测绘成果。',
 'scale_m_per_px':S,'origin_plan_px':[OX,OY]
}
json.dump({'campus':meta,'buildings':buildings},open(os.path.join(OUT,'buildings_v11.json'),'w'),ensure_ascii=False,indent=1)
print('v11 buildings',len(buildings))
from collections import Counter
print('kinds',Counter(b['kind'] for b in buildings))
print('names sample')
for b in buildings[:12]: print(' ',b['id'],b['name'],b['kind'],b['floors'],'层')
