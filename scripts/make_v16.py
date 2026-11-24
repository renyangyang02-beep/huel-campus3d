# -*- coding: utf-8 -*-
"""v16: 基于v14(真实卫星地面) + v16数据(补齐8栋雅字宿舍+修正书院名)。
宿舍立面换青灰实景纹理 facade_dorm_photo.jpg，屋顶红瓦。"""
import io, os
ROOT = os.path.dirname(os.path.abspath(__file__))
s = io.open(os.path.join(ROOT, 'build_campus_v14.py'), encoding='utf-8').read()

s = s.replace('v14: REAL satellite ground (real lake/lawn/roads) + all v13 buildings',
              'v16: +8 missing 雅字 dorms + fixed academy names + cyan-grey facade')

# 换数据源
s = s.replace('buildings_v13.json', 'buildings_v16.json')

# 宿舍立面: 程序纹理 -> 青灰实景纹理
s = s.replace("'dorm':texmat('fac_dorm',os.path.join(TEXDIR,'facade_dorm.jpg')),",
              "'dorm':texmat('fac_dorm',os.path.join(TEXDIR,'facade_dorm_photo.jpg')),")

dst = os.path.join(ROOT, 'build_campus_v16.py')
io.open(dst, 'w', encoding='utf-8').write(s)
print('wrote', dst, len(s))
print('v16 data:', 'buildings_v16.json' in s)
print('cyan facade:', 'facade_dorm_photo.jpg' in s)
print('sat ground:', 'sat_ground.jpg' in s)
