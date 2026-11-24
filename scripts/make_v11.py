# -*- coding: utf-8 -*-
"""Derive build_campus_v11.py from v9: real plan-based footprints, plan as ground."""
import io, os
ROOT=os.path.dirname(os.path.abspath(__file__))
s=io.open(os.path.join(ROOT,'build_campus_v9.py'),encoding='utf-8').read()

# 1) Header note
s=s.replace('Rebuild HUEL Zhengdong campus from real satellite imagery',
            'v11: rebuild HUEL Zhengdong campus from OFFICIAL CAMPUS PLAN (authoritative layout)')

# 2) Reference point: use actual campus center from map provider
s=s.replace("LAT0, LON0 = 34.7826, 113.8200", "LAT0, LON0 = 34.7837, 113.8206")

# 3) Ground: official plan instead of satellite. Plan ground is 1100x1220 px at S=1.09 m/px
s=s.replace(
"textured_plane('SITE_full', os.path.join(OUT,'satellite_full_z17.jpg'),\n               2816*RES17, 1792*RES17, -0.15, site_col)",
"# Ground = official campus plan (roads/lakes/sports/greenery faithful to official layout)\nPLAN_S=1.09; PLAN_CROP_L, PLAN_CROP_T = 85, 440; LIB_PX, LIB_PY = 562, 1214\n_gnd=textured_plane('SITE_full', os.path.join(WEB,'plan_ground.jpg'),\n               1100*PLAN_S, 1220*PLAN_S, -0.15, site_col)\n# align ground center with world coords (plan crop center relative to library origin)\n_gnd.location.x=(PLAN_CROP_L+550-LIB_PX)*PLAN_S\n_gnd.location.y=(LIB_PY-(PLAN_CROP_T+610))*PLAN_S")

# 4) Buildings source: v11 data (already world-space pts), drop px_to_xy conversion
old_block="""BUILDINGS=[]
def P(*coords): return [px_to_xy(*p) for p in coords]
for _d in _b9.BUILDINGS:
    _b=dict(_d)
    _b['pts']=P(*_d['pts_px'])
    if 'inner_px' in _d: _b['inner']=P(*_d['inner_px'])
    BUILDINGS.append(_b)

INTERIOR_IDS=set(b['id'] for b in BUILDINGS if b['kind']!='dorm') | \\
             set(b['id'] for b in BUILDINGS if b['kind']=='dorm' and b['id'] in ('ndorm_00','ndormr_00'))"""
new_block="""BUILDINGS=[]
_v11=json.load(open(os.path.join(OUT,'buildings_v11.json'),encoding='utf-8'))
for _d in _v11['buildings']:
    _b=dict(_d)
    # x,y = centroid of real footprint polygon
    _b['x']=round(sum(p[0] for p in _b['pts'])/len(_b['pts']),2)
    _b['y']=round(sum(p[1] for p in _b['pts'])/len(_b['pts']),2)
    BUILDINGS.append(_b)

INTERIOR_IDS=set(b['id'] for b in BUILDINGS if b['kind']!='dorm') | \\
             set(b['id'] for b in BUILDINGS if b['kind']=='dorm' and b['id'] in ('p00','p11'))"""
assert old_block in s, 'building block not found'
s=s.replace(old_block,new_block)

# 5) Remove import of v9 data (no longer needed) but keep harmless if present
s=s.replace("import build_campus_v9_data as _b9", "# v11 uses official plan data (loaded below)")

# 6) Library plaza overlay coords: v11 library centroid; keep simple ring at 0,0 (library near origin)
s=s.replace("lx,ly=px_to_xy(1320,1042)", "lx,ly=0,0")

# 7) meta note
s=s.replace('建筑轮廓依据覆盖全校的高清卫星影像逐区数字化，辅以学校官网、微信公众号实景照片与官方平面图校准；建筑高度与室内依据公开资料示意，非测绘成果。',
 '建筑位置、轮廓与名称依据学校官方《郑东校区平面图》矢量化复原（真实格局），地面采用该官方平面图；建筑高度按类型示意，非测绘成果。')

dst=os.path.join(ROOT,'build_campus_v11.py')
io.open(dst,'w',encoding='utf-8').write(s)
print('wrote',dst,len(s))
