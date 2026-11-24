# -*- coding: utf-8 -*-
"""Generate build_campus_v9.py from v8:
 - full-campus satellite image as the single ground plane (2816x1792)
 - coordinate contract CX,CY=1408,896; RES17 unchanged
 - building definitions imported from buildings_v9_data.py
"""
import io, os
ROOT=os.path.dirname(os.path.abspath(__file__))
s=io.open(os.path.join(ROOT,'build_campus_v8.py'),encoding='utf-8').read()

s=s.replace('"""v8:','"""v9: 全校高清卫星图(2816x1792)重建，约60栋建筑，修正图书馆位置与楼间距。\n原v8:')

# coordinate center
s=s.replace('CX, CY = 1264 / 2, 625 / 2','CX, CY = 2816 / 2, 1792 / 2')

# ground planes: replace the two old planes with one full plane
old='''textured_plane('SITE_satellite_z16', os.path.join(OUT,'satellite_z16.jpg'),
               1264*RES16, 625*RES16, -0.3, site_col)
textured_plane('SITE_satellite_z17', os.path.join(OUT,'satellite_z17.jpg'),
               1264*RES17, 625*RES17, -0.15, site_col)'''
new='''textured_plane('SITE_full', os.path.join(OUT,'satellite_full_z17.jpg'),
               2816*RES17, 1792*RES17, -0.15, site_col)'''
assert old in s, 'ground plane block not found'
s=s.replace(old,new)

# Replace building definitions block
start=s.index('# ---------- building definitions (pixel coords on z17 image) ----------')
end=s.index('INTERIOR_IDS=',start)
newblock='''# ---------- building definitions (pixel coords on FULL satellite image) ----------
import importlib.util as _ilu
_spec=_ilu.spec_from_file_location('b9data', os.path.join(os.path.dirname(__file__),'buildings_v9_data.py'))
_b9=_ilu.module_from_spec(_spec); _spec.loader.exec_module(_b9)
BUILDINGS=[]
def P(*coords): return [px_to_xy(*p) for p in coords]
for _d in _b9.BUILDINGS:
    _b=dict(_d)
    _b['pts']=P(*_d['pts_px'])
    if 'inner_px' in _d: _b['inner']=P(*_d['inner_px'])
    BUILDINGS.append(_b)

'''
s=s[:start]+newblock+s[end:]

# INTERIOR_IDS: non-dorm + first of dorm rows (limit count for GLB size)
s=s.replace(
"INTERIOR_IDS=set(b['id'] for b in BUILDINGS if b['kind']!='dorm') | \\\n             set(b['id'] for b in BUILDINGS if b['kind']=='dorm' and b['id'].endswith('_0'))",
"INTERIOR_IDS=set(b['id'] for b in BUILDINGS if b['kind']!='dorm') | \\\n             set(b['id'] for b in BUILDINGS if b['kind']=='dorm' and b['id'] in ('ndorm_00','ndormr_00'))")

# core_west 'inner_px' no longer used; data uses 'inner' key already converted.
# The exterior builder checks 'inner_px' in b -> change to 'inner' with world pts
s=s.replace("    if 'inner_px' in b:\n        inner=P(*b['inner_px'])",
            "    if 'inner' in b:\n        inner=b['inner']")

# Landscape: the full satellite image already shows real lakes/roads/fields/greenery.
# Remove ALL procedural overlays (they used old-image coords and would be misplaced),
# keeping only the library plaza ring at the correct new-image position.
ls = s.index('# ---------- landscape: library plaza, lakes, central axis ----------')
# Cut landscape+facilities+trees but KEEP the interiors section (FloorBuilder + build_interior)
marker = s.index('# ---------- interiors (v5', ls)
new_land = '''# ---------- landscape: real satellite底图已含湖泊/道路/运动场/绿化，仅保留图书馆广场 ----------
site_parent=empty('GRP_landscape',site_col)
lx,ly=px_to_xy(1320,1042)
add_ring('SITE_lib_plaza_outer',lx,ly,46,74,0.35,M['plaza'],site_col,site_parent)
add_ring('SITE_lib_plaza_inner',lx,ly,40,46,0.4,M['trim'],site_col,site_parent)

'''
s = s[:ls] + new_land + s[marker:]

# description note
s=s.replace('建筑轮廓依据高德最新卫星影像数字化，辅以学校官网、官方平面图与微信公众号实景照片校准',
            '建筑轮廓依据覆盖全校的高清卫星影像逐区数字化，辅以学校官网、微信公众号实景照片与官方平面图校准')

io.open(os.path.join(ROOT,'build_campus_v9.py'),'w',encoding='utf-8').write(s)
print('written build_campus_v9.py')
