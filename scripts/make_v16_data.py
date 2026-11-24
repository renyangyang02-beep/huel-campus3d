# -*- coding: utf-8 -*-
"""v16: 按用户反馈+官方坐标修正两处餐厅名称/类型；
删除压在空绿地上的错位"教学配套"p18。基于 v15 数据。
- p19 第三教学楼 -> 第三食堂(三餐厅)  world(271,440), 官方第三食堂(285,391)
- p17 教学配套   -> 第二食堂(二餐厅)  world(-114,353), 官方第二食堂(-113,340)
  笃行书院(馨苑)东面即第二食堂, 官方介绍佐证
- p18 教学配套   -> 删除(卫星影像上是空绿地, 建筑错位)
"""
import json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(ROOT, '..', 'output'))
d = json.load(open(os.path.join(OUT, 'buildings_v15.json'), encoding='utf-8'))

CANTEEN = {
    'p19': ('第三餐厅', '第三食堂', 4, 16),   # 三餐厅(综合运动场/怡苑附近)
    'p17': ('第二餐厅', '第二食堂', 3, 13),   # 二餐厅(笃行书院馨苑东面)
}
for b in d['buildings']:
    if b['id'] in CANTEEN:
        name, culture, floors, h = CANTEEN[b['id']]
        b['name'] = name
        b['culture'] = culture
        b['functional'] = '食堂'
        b['kind'] = 'canteen'
        b['floors'] = floors
        b['height'] = h
        b['roof'] = 'flat'
        b['facade'] = 'canteen'
        b['desc'] = '按学校官方资料与真实卫星位置复原的食堂建筑。%s。' % (
            '位于综合运动场、怡苑附近，一层区域特色美食，二层自选餐厅' if b['id']=='p19'
            else '位于笃行书院（馨苑）东侧、学生公寓区，一层基本伙，二/三层风味与民族餐厅')
        b['interior'] = '食堂内部为多层餐厅空间示意，可在三维模式查看。'

# 删除压在空绿地上的错位建筑 p18
before = len(d['buildings'])
d['buildings'] = [b for b in d['buildings'] if b['id'] != 'p18']
print('删除错位建筑 p18:', before, '->', len(d['buildings']))

dst = os.path.join(OUT, 'buildings_v16.json')
json.dump(d, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote', dst, '建筑数', len(d['buildings']))
for b in d['buildings']:
    if b['kind'] == 'canteen':
        print(' 食堂', b['id'], b['name'], b['culture'], b['height'])
