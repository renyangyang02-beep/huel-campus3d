# -*- coding: utf-8 -*-
"""把建模数据(buildings_vXX.json, pts世界坐标)转成网页所需格式:
补 x/y(建筑中心, y向北为正) 和 lat/lon(由campus原点反算)。
网页 index.html 大量依赖 b.x/b.y 做飞行定位/标签/小地图pin,
selectBuilding 还用 b.lat.toFixed(6)/b.lon.toFixed(6) —— 缺这些字段会抛异常导致点击速览无反应。
用法: python scripts/make_web_data.py [版本号, 默认v16]
"""
import json, os, sys, math

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(ROOT, '..', 'output'))
WEB = os.path.abspath(os.path.join(ROOT, '..', 'web'))
ver = sys.argv[1] if len(sys.argv) > 1 else 'v16'

src = os.path.join(OUT, 'buildings_%s.json' % ver)
d = json.load(open(src, encoding='utf-8'))
campus = d['campus']
lat0, lon0 = campus['lat0'], campus['lon0']

def to_latlon(x, y):
    # x: 东向米, y: 北向米 (相对原点)
    lat = lat0 + y / 111320.0
    lon = lon0 + x / (111320.0 * math.cos(math.radians(lat0)))
    return round(lat, 6), round(lon, 6)

for b in d['buildings']:
    pts = b['pts']
    cx = round(sum(p[0] for p in pts) / len(pts), 1)
    cy = round(sum(p[1] for p in pts) / len(pts), 1)
    b['x'] = cx
    b['y'] = cy
    lat, lon = to_latlon(cx, cy)
    b['lat'] = lat
    b['lon'] = lon

# culture/functional 兜底(个别老建筑缺)
for b in d['buildings']:
    b.setdefault('culture', b['name'])
    b.setdefault('functional', '')

for dst in [os.path.join(WEB, 'buildings.json'),
            os.path.abspath(os.path.join(ROOT, '..', 'publish', 'web', 'buildings.json'))]:
    json.dump(d, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('wrote', dst)

print('建筑数', len(d['buildings']))
for b in d['buildings'][:3]:
    print(' ', b['id'], b['name'], 'x=%.1f y=%.1f' % (b['x'], b['y']),
          'lat=%.6f lon=%.6f' % (b['lat'], b['lon']))
