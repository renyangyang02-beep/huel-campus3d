# -*- coding: utf-8 -*-
"""v18: 按用户反馈补齐近年新建建筑（都需立体化）：
1) 大学生科创中心/鼎新楼 A+B 座（文创中心所在，图书馆北侧，33775m2 大楼）——A/B 双塔
2) 笃行书院（馨苑片区）+ 新苑宿舍——西运动场东侧宿舍群
3) 第二商业街（北区宿舍旁的商铺带）
4) 教职工活动中心（躬行楼，内环西路近西门）
5) 北部综合楼 p30 改标为体育训练馆（用户：北部综合楼是体育训练楼）
坐标来源：腾讯地图 POI 实测经纬度 + 官方平面图配准；换算同 make_web_data.py。
基于 v16 数据（构建脚本会自动再取 pts 质心）。
"""
import json, os, math

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(ROOT, '..', 'output'))
d = json.load(open(os.path.join(OUT, 'buildings_v16.json'), encoding='utf-8'))

lat0, lon0 = 34.7837, 113.8206
def ll2xy(lat, lon):
    return ((lon - lon0) * 111320 * math.cos(math.radians(lat0)),
            (lat - lat0) * 111320)

def rect(cx, cy, w, h):
    hw, hh = w / 2.0, h / 2.0
    return [[round(cx-hw,1),round(cy-hh,1)],[round(cx+hw,1),round(cy-hh,1)],
            [round(cx+hw,1),round(cy+hh,1)],[round(cx-hw,1),round(cy+hh,1)]]

def add(bid, name, cx, cy, w, h, kind, floors, height, facade, roof='flat',
        culture=None, functional=None, desc='', interior='', inner=None):
    b = {'id':bid, 'name':name, 'kind':kind, 'floors':floors, 'height':height,
         'pts':rect(cx,cy,w,h), 'plan_idx':None, 'roof':roof,
         'desc':desc, 'interior':interior or '该建筑内部空间示意可在三维模式中查看。',
         'facade':facade, 'culture':culture or name, 'functional':functional or ''}
    if inner: b['inner'] = inner
    d['buildings'].append(b)
    print('新增', bid, name, 'world(%.0f,%.0f)'%(cx,cy), '%dx%d'%(w,h), 'h=%d'%height)

# ---------- 1) 大学生科创中心（鼎新楼 A/B 座）——图书馆北侧，双塔立体 ----------
# 鼎新楼A座 财菁印象 POI 34.784796,113.820758 ; B座 34.784375,113.819766
ax, ay = ll2xy(34.784796, 113.820758)   # (14, 122)
bx, by = ll2xy(34.784375, 113.819766)   # (-76, 75)
# 为避免压图书馆(0,0)与博文楼，A座略北移，B座保持
add('pDX_A', '鼎新楼A座（大学生科创中心）', ax+26, ay+34, 74, 46,
    'innovation', 13, 62, 'glass',
    culture='鼎新楼A座', functional='大学生科创中心/文创中心',
    desc='鼎新楼A座，大学生科创中心（取“革故鼎新”之意）。2023年建成，总建筑面积约3.38万平方米，'
         '内含学校文创中心、财菁印象等创新创业与文创空间，是郑东校区新建的地标性综合体。',
    )
add('pDX_B', '鼎新楼B座（大学生科创中心）', bx-30, by+18, 66, 42,
    'innovation', 11, 52, 'glass',
    culture='鼎新楼B座', functional='大学生科创中心',
    desc='鼎新楼B座，与A座共同构成大学生科创中心，汇聚创新创业教育、学科交叉与实训空间。',
    )

# ---------- 2) 笃行书院（馨苑片区）与 新苑宿舍 ----------
# 笃行书院 POI 34.784981,113.817321 -> (-300,143)，位于雅苑群。
# 放在雅苑群西南侧空地，避免压 pYA 楼（最近43m），青灰墙+红顶。
add('pDXSY', '笃行书院（馨苑）', -352, 96, 58, 26, 'dorm', 6, 21, 'dorm', roof='red',
    culture='笃行书院·馨苑', functional='书院宿舍',
    desc='笃行书院（馨苑），取“笃学笃行”之意。郑东校区四大书院之一，位于西运动场东侧学生公寓区。')
add('pXINY', '新苑', -352, 58, 58, 26, 'dorm', 6, 21, 'dorm', roof='red',
    culture='新苑', functional='书院宿舍',
    desc='新苑学生公寓，青灰墙、红坡顶，位于西运动场东侧生活区。')

# ---------- 3) 第二商业街（北区宿舍旁，沿街低层商铺带） ----------
# 移动营业厅 POI 第二商业街2-102 34.788354,113.816799 -> (-347,518)
add('pSHOP2', '第二商业街', -398, 500, 78, 24, 'commercial', 2, 11, 'shop',
    culture='第二商业街', functional='商业街',
    desc='第二商业街，涵盖生活超市、药店、文体店、图文店、眼镜店、理发店、冷饮及水果店等生活服务。')
add('pSHOP1', '第一商业街（第一食堂旁）', -300, -118, 66, 22, 'commercial', 2, 11, 'shop',
    culture='第一商业街', functional='商业街',
    desc='第一商业街，位于第一食堂、教学楼附近的生活服务街区。')

# ---------- 4) 教职工活动中心（躬行楼，内环西路近西门） ----------
# 城市吧：内环西路，靠近秋实街和龙子湖东路（校园西北侧）。放在雅苑群西侧空地。
add('pGX', '教职工活动中心（躬行楼）', -430, 250, 60, 32, 'activity', 4, 19, 'office',
    culture='躬行楼', functional='教职工活动中心',
    desc='教职工活动中心（躬行楼），位于内环西路，靠近秋实街，设离退休职工工作处等活动空间。',
    )

# ---------- 5) 北部综合楼 -> 体育训练馆 ----------
for b in d['buildings']:
    if b['id'] == 'p30':
        b['name'] = '体育训练馆（北部综合楼）'
        b['culture'] = '北部综合楼'
        b['functional'] = '体育训练'
        b['kind'] = 'gym'
        b['floors'] = 3
        b['height'] = 20
        b['roof'] = 'blue'
        b['facade'] = 'gray'
        b['desc'] = '北部综合楼，实际为体育训练馆，承担体育教学与训练功能，位于东运动场北侧。'
        b['interior'] = '训练馆内部为体育馆空间示意，可在三维模式中查看。'

# ---------- 6) 四个校门（作为可点击点位的建筑标记，用 gate 类型小型门楼） ----------
# 经纬度实测：北门34.78703,113.81594; 南门34.777849,113.819558; 东门34.781451,113.824056
# 北1门34.787437,113.824479(作东门辅助)。西门按官方平面图取校园西边界。
gates = [
    ('pGateN', '北门', 34.78703, 113.81594),
    ('pGateS', '南门', 34.777849, 113.819558),
    ('pGateE', '东门', 34.781451, 113.824056),
    ('pGateW', '西门', 34.78360, 113.81630),
]
for gid, gname, la, lo in gates:
    gx, gy = ll2xy(la, lo)
    add(gid, gname, gx, gy, 20, 10, 'gate', 1, 9, 'gate', roof='flat',
        culture=gname, functional='校门',
        desc='%s，河南财经政法大学郑东校区校门。校园东南西北四个方向均设大门，为师生主要出入口。'%gname,
        interior='校门为入口门楼，不设内部空间。')

dst = os.path.join(OUT, 'buildings_v18.json')
json.dump(d, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote', dst, '建筑数', len(d['buildings']))
