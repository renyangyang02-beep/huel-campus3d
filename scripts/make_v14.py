# -*- coding: utf-8 -*-
"""v14: 地面由官方规划示意图换成真实卫星影像（湖/草坪/道路/树木皆实景），
保留 v13 全部建筑成果（建树楼/综合实验楼/官方文化名）。去掉突兀的白色圆盘广场环。"""
import io, os
ROOT = os.path.dirname(os.path.abspath(__file__))
s = io.open(os.path.join(ROOT, 'build_campus_v13.py'), encoding='utf-8').read()

old = ("'v13: +建树楼 corrected (idx12), +综合实验楼(知行楼), official cultural names'")
new = ("'v14: REAL satellite ground (real lake/lawn/roads) + all v13 buildings'")
s = s.replace(old, new)

# 地面贴图：规划示意图 -> 真实卫星图
s = s.replace("'plan_ground.jpg'", "'sat_ground.jpg'")

# 地面说明注释
s = s.replace('# Ground = official campus plan (roads/lakes/sports/greenery faithful to official layout)',
              '# Ground = REAL satellite imagery (real lake/lawn/roads/trees, georeferenced to building coords)')

# 去掉白色圆盘广场环（卫星图已含真实广场与绿地）
s = s.replace("add_ring('SITE_lib_plaza_outer',lx,ly,46,74,0.35,M['plaza'],site_col,site_parent)\n"
              "add_ring('SITE_lib_plaza_inner',lx,ly,40,46,0.4,M['trim'],site_col,site_parent)",
              "# v14: 白色圆盘广场环移除——卫星图地面已含真实图书馆广场与绿地\n"
              "# add_ring('SITE_lib_plaza_outer',lx,ly,46,74,0.35,M['plaza'],site_col,site_parent)\n"
              "# add_ring('SITE_lib_plaza_inner',lx,ly,40,46,0.4,M['trim'],site_col,site_parent)")

# 更新导出说明文字
s = s.replace('建筑位置/轮廓依据学校官方《郑东校区平面图》矢量化（建树楼按官方标注补正）；楼名含学校官方文化名；教学楼立面按实景重绘；高度为常见层数示意，非测绘成果。',
              '地面采用真实卫星影像（明湖、草坪、道路、树木等均为实景）；建筑位置/轮廓依据官方平面图矢量化（建树楼按官方标注补正）；楼名含学校官方文化名；教学楼立面按实景重绘；高度为常见层数示意，非测绘成果。')

dst = os.path.join(ROOT, 'build_campus_v14.py')
io.open(dst, 'w', encoding='utf-8').write(s)
print('wrote', dst, len(s))
print('check sat_ground.jpg:', "'sat_ground.jpg'" in s)
print('check ring removed:', 'add_ring(\'SITE_lib_plaza_outer\',lx,ly,46,74' not in s)
