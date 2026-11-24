# -*- coding: utf-8 -*-
"""把建模数据(buildings_v18.json)里的建筑轮廓点 pts 同步到网页数据 buildings.json。

网页小地图的矢量覆盖层需要 pts(世界坐标, 米)来绘制锐利的建筑轮廓/标注。
build_campus_v18.py 生成的 web/buildings.json 是精简 meta, 默认不带 pts,
本脚本补齐它, 同时写入 web/ 与 publish/web/ 两份。

用法: python scripts/sync_web_pts.py [版本号, 默认v18]
"""
import json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(ROOT, '..'))
OUT = os.path.join(PROJ, 'output')
ver = sys.argv[1] if len(sys.argv) > 1 else 'v18'

src = json.load(open(os.path.join(OUT, 'buildings_%s.json' % ver), encoding='utf-8'))
pts_map = {b['id']: b['pts'] for b in src['buildings'] if b.get('pts')}

dsts = [os.path.join(PROJ, 'web', 'buildings.json'),
        os.path.join(PROJ, 'publish', 'web', 'buildings.json')]
for dst in dsts:
    d = json.load(open(dst, encoding='utf-8'))
    added = 0
    for b in d['buildings']:
        if b['id'] in pts_map:
            if b.get('pts') != pts_map[b['id']]:
                added += 1
            b['pts'] = pts_map[b['id']]
    json.dump(d, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('wrote', dst, '| pts', added, '/', len(d['buildings']))
