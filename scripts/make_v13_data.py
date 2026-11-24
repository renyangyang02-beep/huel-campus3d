# -*- coding: utf-8 -*-
"""v13 data: fix the '建树楼' error found by user.
Facts verified from official sources:
 - 财子微青春官方推文: 至善楼/文韬楼/文锦楼/知行楼/博文楼/崇法楼/鼎新楼/建树楼 文化名.
 - 官方平面图: 建树楼位于东侧弘德路北侧，是带天井的白色方楼 (plan idx=12) —— 之前被错标成"综合实验楼".
 - 综合实验楼(知行楼)实际在明湖东南，更靠南 —— 之前漏建.
 - 建树楼: 校友王建树2014年捐建教学楼, 占地3090㎡, 使用面积15508㎡, 约5层, -coordinate经纬度(34.781985,113.824051).
这里: 把 p12 名字由"综合实验楼"改为"建树楼"(保留其真实轮廓), 在明湖东南补建真正的"综合实验楼",
并给核心楼宇加上官方文化名(主名功能名+括注文化名, 两套名字都能对上).
"""
import json, os
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(ROOT, '..', 'output'))
d = json.load(open(os.path.join(OUT, 'buildings_v12.json'), encoding='utf-8'))
by_id = {b['id']: b for b in d['buildings']}

# 1) 官方文化名 (主名沿用功能名+括注文化名, 保证平面图/推文两套都对得上)
CULTURE = {
    'p00': ('行政办公楼', '至善楼'),
    'p02': ('第一教学楼', '文韬楼'),
    'p01': ('第二教学楼', '文锦楼'),
    'p19': ('第三教学楼', None),
    'p13': ('教学科研楼', '博文楼'),
    'p12': ('建树楼', None),          # 下面专门处理
    'p07': ('图书馆', None),
}
for bid, (func, cult) in CULTURE.items():
    if bid == 'p12':
        continue
    b = by_id.get(bid)
    if b and cult:
        b['name'] = '%s（%s）' % (func, cult)
        b['culture'] = cult
        b['functional'] = func

# 2) p12 = 建树楼 (真实轮廓保留, 由 lab 改回 classroom/office 属性)
js = by_id['p12']
js['name'] = '建树楼'
js['culture'] = '建树楼'
js['functional'] = '建树楼(捐资教学楼)'
js['kind'] = 'classroom'
js['facade'] = 'axis'          # 与同区教学楼一致的实景立面
js['floors'] = 5
js['height'] = 22
js['desc'] = ('建树楼——校友王建树先生2014年捐资3800万元兴建的教学楼，占地约3090㎡、'
              '使用面积约15508㎡，供国际经济与贸易、金融、房地产等学院教学科研办公使用；'
              '位于校园东侧弘德路北，学校官方平面图在此明确标注“建树楼”。')
js['interior'] = '建树楼内部空间（教室/办公室/研讨室）示意可在三维模式中查看。'

# 3) 补建真正的综合实验楼（知行楼）在明湖东南 (世界坐标约 270,-70)
new = {
    'id': 'pZX',
    'name': '综合实验楼（知行楼）',
    'culture': '知行楼',
    'functional': '综合实验楼',
    'kind': 'lab',
    'facade': 'gray',
    'floors': 6,
    'height': 26,
    'pts': [[236, -42], [306, -42], [306, -118], [236, -118]],
    'plan_idx': None,
    'roof': 'flat',
    'desc': ('综合实验楼（知行楼）——上机课、实践课与实验教学的场所，位于明湖东南、'
             '校园东侧环路以西；据学校官方平面图该楼在明湖东南侧，之前版本误将建树楼位置当作此楼。'),
    'interior': '综合实验楼内部（实验室/机房）示意可在三维模式中查看。'
}
if not any(b['id'] == 'pZX' for b in d['buildings']):
    d['buildings'].append(new)

# 4) 更新来源说明
d['campus']['source'] = ('建筑位置/轮廓依据学校官方《郑东校区平面图》矢量化（东侧黄色待建区中的建树楼2014年已建成，'
                         '本版据官方标注补正）；楼名含学校官方文化名；建树楼按校友捐建教学楼史料复原；'
                         '高度为常见层数示意，非测绘成果。')

json.dump(d, open(os.path.join(OUT, 'buildings_v13.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('v13 buildings', len(d['buildings']))
for bid in ('p00','p02','p01','p13','p12','pZX','p07'):
    b = by_id.get(bid) or next(x for x in d['buildings'] if x['id']==bid)
    print(' ', bid, b['name'], b['kind'])
