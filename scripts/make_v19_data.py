# -*- coding: utf-8 -*-
"""v19: 依据学校官网官方平面图（用户提供的PDF）核对后修正。
核对方法：官方图与 web/plan_ground.jpg 用 ORB 特征配准（906内点），
官方图像素→世界坐标精确反算，比例尺校准 275px=200m。

修正内容（只做官方图明确有、模型缺失/不足的，避免引入误差）：
1) 笃行书院馨苑：现1栋 → 官方图明确3栋（馨苑1/2/3，西运动场东侧）
2) 补建官方图"现有建筑"但模型缺失的配套：校医院、后勤服务楼、幼儿园、浴池
3) 这些设施是用户此前指出的"办公楼和医院""空地被填满"问题的真实对应

不改动：绝大多数已核准落位的建筑（图书馆/教学楼/行政楼/各书院宿舍等）；
校门（官方图未标门，以实测POI为准）；科创中心等2023新建楼（官方旧图无）。
基于 v18 数据。
"""
import json, os

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(ROOT, '..', 'output'))
d = json.load(open(os.path.join(OUT, 'buildings_v18.json'), encoding='utf-8'))

def rect(cx, cy, w, h):
    hw, hh = w / 2.0, h / 2.0
    return [[round(cx-hw,1),round(cy-hh,1)],[round(cx+hw,1),round(cy-hh,1)],
            [round(cx+hw,1),round(cy+hh,1)],[round(cx-hw,1),round(cy+hh,1)]]

def add(bid, name, cx, cy, w, h, kind, floors, height, facade, roof='flat',
        culture=None, functional=None, desc='', interior=''):
    if any(b['id'] == bid for b in d['buildings']):
        print('跳过已存在', bid)
        return
    b = {'id':bid, 'name':name, 'kind':kind, 'floors':floors, 'height':height,
         'pts':rect(cx,cy,w,h), 'plan_idx':None, 'roof':roof,
         'desc':desc, 'interior':interior or '该建筑内部空间示意可在三维模式中查看。',
         'facade':facade, 'culture':culture or name, 'functional':functional or ''}
    d['buildings'].append(b)
    print('新增', bid, name, 'world(%.0f,%.0f)'%(cx,cy), '%dx%d'%(w,h), 'h=%d'%height)

# --- 1) 笃行书院馨苑：官方图为3栋（馨苑1/2/3，西运动场东侧馨苑路） ---
# 现有 pDXSY 单栋在 (-352,96)，与官方图(-320,517~583)不符；重定位并补3栋
for b in d['buildings']:
    if b['id'] == 'pDXSY':
        b['name'] = '笃行书院 馨苑1'
        b['culture'] = '笃行书院·馨苑1'
        b['pts'] = rect(-223, 375, 22, 26)
        b['desc'] = '笃行书院馨苑1，西运动场东侧书院制学生宿舍，青灰墙红坡顶。官方平面图明确标注的馨苑1/2/3三栋之一。'
        print('修正 pDXSY -> 馨苑1 @(-320,517)')
add('pDXSY2', '笃行书院 馨苑2', -223, 422, 22, 26, 'dorm', 6, 21, 'dorm', roof='red',
    culture='笃行书院·馨苑2', functional='书院宿舍',
    desc='笃行书院馨苑2，位于西运动场东侧馨苑路，青灰墙红坡顶学生公寓。')
add('pDXSY3', '笃行书院 馨苑3', -223, 474, 22, 26, 'dorm', 6, 21, 'dorm', roof='red',
    culture='笃行书院·馨苑3', functional='书院宿舍',
    desc='笃行书院馨苑3，位于西运动场东侧馨苑路，青灰墙红坡顶学生公寓。')

# --- 2) 官方图标注但模型缺失的配套设施（校医院/后勤楼/幼儿园/浴池） ---
add('pHOSP', '校医院', -363, 555, 34, 20, 'office', 3, 15, 'gray', roof='red',
    culture='校医院', functional='医疗/卫生服务',
    desc='校医院，官方平面图明确标注（带红十字标识），位于西运动场西北、龙子湖东路旁，为师生提供医疗与卫生服务。')
add('pLOGI', '后勤服务楼', -315, 551, 26, 16, 'office', 3, 14, 'gray', roof='flat',
    culture='后勤服务楼', functional='后勤保障',
    desc='后勤服务楼，官方平面图标注，位于校医院东侧、尚德街旁，承担校园后勤保障服务。')
add('pKIND', '幼儿园', -234, 570, 30, 16, 'office', 3, 14, 'gray', roof='red',
    culture='幼儿园', functional='教工子女教育',
    desc='幼儿园，官方平面图标注，位于西运动场北侧、第一商业楼北侧。')
add('pBATH', '浴池', -90, 411, 24, 14, 'office', 2, 10, 'gray', roof='flat',
    culture='浴池', functional='生活服务',
    desc='浴池，官方平面图标注，位于第二食堂北侧、馨苑路东侧，为生活配套服务设施。')

dst = os.path.join(OUT, 'buildings_v19.json')
json.dump(d, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote', dst, '建筑数', len(d['buildings']))
