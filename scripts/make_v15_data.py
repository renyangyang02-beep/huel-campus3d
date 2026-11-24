# -*- coding: utf-8 -*-
"""v15: 补齐西运动场北侧缺失的8栋书院宿舍(弘毅雅1-3/致远雅4-6/明理雅7-8)，
修正已有宿舍楼重复/错误的名称，采用青灰墙+红坡顶。基于 v13 数据。"""
import json, os, math, io

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(ROOT, '..', 'output'))
d = json.load(open(os.path.join(OUT, 'buildings_v13.json'), encoding='utf-8'))

# ---- 1) 修正已有宿舍楼名称（按规划图真实书院名）----
# 静字楼（西南，已建但名字错乱）
rename = {
    'p05': '通达书院 静4',
    'p06': '博治书院 静1',
    'p08': '通达书院 静5',
    'p09': '博治书院 静2',
    'p11': '通达书院 静6',
    'p14': '博治书院 静3',
}
for b in d['buildings']:
    if b['id'] in rename:
        b['name'] = rename[b['id']]
        b['culture'] = rename[b['id']]
        b['kind'] = 'dorm'
        b['roof'] = 'red'
        b['height'] = 20
        b['floors'] = 6

# p27/p25 等在北侧的经世书院等保持，但去掉重复的"弘毅书院/致远书院"错误名
# 这些实际是北区的楼，改按经世/明理系列命名
north_rename = {
    'p27': '经世书院 北1', 'p25': '经世书院 北2',
    'p38': '经世书院 北3', 'p37': '经世书院 北4',
    'p43': '经世书院 北5', 'p44': '经世书院 北6',
    'p41': '经世书院 北7', 'p42': '经世书院 北8',
    'p28': '经世书院 北9',
}
for b in d['buildings']:
    if b['id'] in north_rename:
        b['name'] = north_rename[b['id']]
        b['culture'] = north_rename[b['id']]
        b['roof'] = 'red'

# ---- 2) 补齐8栋缺失的雅字宿舍楼 ----
ya = json.load(open(os.path.join(OUT, 'ya_dorms_manual.json'), encoding='utf-8'))
for i, y in enumerate(ya):
    cx, cy, w, h = y['cx'], y['cy'], y['w'], y['h']
    hw, hh = w/2, h/2
    pts = [[round(cx-hw,1),round(cy-hh,1)],[round(cx+hw,1),round(cy-hh,1)],
           [round(cx+hw,1),round(cy+hh,1)],[round(cx-hw,1),round(cy+hh,1)]]
    name = y['name'].replace('-HY','').replace('-ZY','').replace('-ML','')
    if 'HY' in y['name']: fullname='弘毅书院 '+name
    elif 'ZY' in y['name']: fullname='致远书院 '+name
    else: fullname='明理书院 '+name
    bid = 'pYA%d'%(i+1)
    nb = {
        'id':bid, 'name':fullname, 'kind':'dorm', 'floors':6, 'height':21,
        'pts':pts, 'plan_idx':None, 'roof':'red',
        'desc':'依据官方平面图名称与真实卫星影像位置复原的书院宿舍楼。',
        'interior':'书院宿舍内部空间示意可在三维模式中查看。',
        'facade':'dorm', 'culture':fullname, 'functional':'书院宿舍',
    }
    d['buildings'].append(nb)

# ---- 3) 所有宿舍统一青灰墙+红顶标记 ----
for b in d['buildings']:
    if b['kind']=='dorm':
        b['roof']='red'
        b['facade']='dorm'

dst = os.path.join(OUT, 'buildings_v15.json')
json.dump(d, open(dst,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote',dst,'建筑数',len(d['buildings']))
print('新增雅楼',sum(1 for b in d['buildings'] if b['id'].startswith('pYA')))
