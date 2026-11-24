# -*- coding: utf-8 -*-
"""v13: derive build_campus_v13.py from v12 — only switch data source to buildings_v13.json."""
import io, os
ROOT = os.path.dirname(os.path.abspath(__file__))
s = io.open(os.path.join(ROOT, 'build_campus_v12.py'), encoding='utf-8').read()
s = s.replace('v12: plan-based campus + photo-faithful teaching buildings (fins/glass/eaves/canopy)',
              'v13: +建树楼 corrected (idx12), +综合实验楼(知行楼), official cultural names')
s = s.replace('buildings_v12.json', 'buildings_v13.json')
s = s.replace('建筑位置、轮廓与名称依据学校官方《郑东校区平面图》矢量化复原（真实格局），地面采用该官方平面图；教学楼立面按实景重绘（浅灰竖格栅/深灰砖墙+蓝玻璃、挑檐与入口雨棚），高度为常见层数示意，非测绘成果。',
              '建筑位置/轮廓依据学校官方《郑东校区平面图》矢量化（建树楼按官方标注补正）；楼名含学校官方文化名；教学楼立面按实景重绘；高度为常见层数示意，非测绘成果。')
dst = os.path.join(ROOT, 'build_campus_v13.py')
io.open(dst, 'w', encoding='utf-8').write(s)
print('wrote', dst, len(s))
