# -*- coding: utf-8 -*-
"""Generate build_campus_v8.py from v7 by replacing the building-definition block
with a full digitization of the latest Gaode satellite imagery."""
import io, os

ROOT = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(ROOT, 'build_campus_v7.py')
dst = os.path.join(ROOT, 'build_campus_v8.py')
s = io.open(src, encoding='utf-8').read()

# update header docstring
s = s.replace(
'''"""v7: 基于最新高德卫星影像 + 多渠道实景照片（官网/微信公众号/贴吧素材）复原郑东校区。''',
'''"""v8: 按高德最新卫星影像逐栋数字化全部建筑轮廓（约38栋），修正宿舍区/核心教学区
的真实排布，图书馆立面提亮。基于多渠道实景照片（官网/微信公众号）校准配色。
（原v7说明：）''')

s = s.replace(
"- 图书馆立面改用真实正面照片裁切的银白竖柱+蓝玻璃纹理。",
"- v8: 建筑由24栋扩到38栋，宿舍区按卫星图5-6排逐栋重建，核心区改斜向围合+田字楼群，图书馆纹理提亮。")

start = s.index('# ---------- building definitions (pixel coords on z17 image) ----------')
end = s.index('INTERIOR_IDS=', start)

new_block = '''# ---------- building definitions (pixel coords on z17 image) ----------
def P(*coords): return [px_to_xy(*p) for p in coords]

BUILDINGS=[]
def add_b(id,name,kind,pts_px,height,floors,desc,interior,roof='flat',inner_px=None):
    pts=P(*pts_px)
    d=dict(id=id,name=name,kind=kind,pts=pts,height=height,floors=floors,
           desc=desc,interior=interior,roof=roof)
    if inner_px: d['inner_px']=inner_px
    BUILDINGS.append(d)

DORM_DESC='学生公寓，六层长条式布局，四人间/六人间，每层设公共卫生间与浴室，配空调、暖气与阳台。'
DORM_INT='学生宿舍标准层：房间、公共卫生间、洗漱区与走廊。'
CLASS_DESC='多层教学楼，灰色墙面配蓝灰玻璃窗，设多媒体教室与教研室。'
CLASS_INT='多媒体教室、办公室与教研室。'
OFFICE_DESC='行政/办公用房，灰色石材立面，平屋顶。'
OFFICE_INT='办公室、会议室与业务窗口。'
CANTEEN_DESC='学生食堂，多层就餐大厅与风味窗口。'
CANTEEN_INT='一层基本餐厅，二层风味小吃与休闲就餐区。'

# ===== 一、北部核心教学区（卫星图：西侧斜向围合庭院 + 东侧田字四栋 + 蓝顶体育馆）=====
add_b('core_west','至善楼','classroom',
      [(548,95),(655,80),(668,160),(560,175)],26,6,
      '核心教学组团西侧，斜向围合庭院式布局，中间为绿化内庭，灰白墙面配蓝灰玻璃。',
      CLASS_INT, inner_px=[(578,108),(632,99),(640,146),(586,156)])
for i,(x1,y1,x2,y2) in enumerate([(675,60,725,100),(730,60,780,100),
                                  (675,107,725,147),(730,107,780,147)]):
    add_b('core_e%d'%i,['文韬楼','文锦楼','博文楼','明理楼'][i],'classroom',
          [(x1,y1),(x2,y1),(x2,y2),(x1,y2)],26,6,CLASS_DESC,CLASS_INT)
add_b('bluehall','体育馆','gym',
      [(800,95),(840,95),(840,175),(800,175)],22,3,
      '东运动场西侧的蓝色屋顶场馆，承担室内球类与集会活动。',
      '室内球场、看台与器材室。',roof='blue')

# ===== 二、学生公寓区（卫星图：静苑/雅苑，6排共15栋长条楼）=====
dorm_rows=[
    (190,[(155,250),(275,370),(400,490)]),
    (235,[(155,255),(275,375),(415,490)]),
    (285,[(155,255),(275,375),(415,490)]),
    (320,[(200,345),(360,490)]),
    (375,[(200,345),(360,490)]),
    (410,[(200,345),(360,490)]),
]
for r,(y,spans) in enumerate(dorm_rows):
    for c,(x1,x2) in enumerate(spans):
        add_b('dorm_%d_%d'%(r,c),'%s苑%d号楼'%('静雅'[c%2],r+1),'dorm',
              [(x1,y),(x2,y),(x2,y+20),(x1,y+20)],22,6,DORM_DESC,DORM_INT)

# ===== 三、图书馆（中心地标，坐标经卫星图核对）=====
add_b('library','图书馆','library',
      [(533,417),(607,417),(607,492),(533,492)],60,12,
      '校园中心地标，建筑面积4.76万平方米，地上12层、高60米。方正四望如一，顶部巨大方形挑檐如盖，银白竖向石材线条与蓝色玻璃幕墙相间，前为博雅广场，明湖、鉴湖相依。立面纹理取自正面实景照片。',
      '一层服务大厅与检索区；中庭贯通多层；二至十二层为开架书库、阅览区、自习区与研讨间。',roof='ding')

# ===== 四、东部庭院组团（卫星图：知行/博文实验楼群 + 东侧庭院楼）=====
add_b('eastgrid_w','知行楼','lab',
      [(680,290),(735,290),(735,370),(680,370)],25,6,
      '综合实验教学楼，实景为橙红格栅配灰砖立面。','计算机实验室、专业实验室与教研室。')
add_b('eastgrid_e','博文楼','lab',
      [(740,290),(790,290),(790,370),(740,370)],25,6,
      '综合实验教学楼，与知行楼相邻。','专业实验室、研讨室与教研室。')
add_b('eastcourt1','崇法楼','classroom',
      [(950,300),(980,300),(980,370),(950,370)],24,6,
      '法学部综合楼，位于校园东部庭院组团。','法学专业教室、模拟法庭与报告厅。')
add_b('eastcourt2','鼎新楼','office',
      [(780,400),(830,400),(830,485),(780,485)],24,6,
      '大学生科创中心，庭院式布局。','创新工坊、项目工作室与展示空间。')
add_b('eastcourt3','建树楼','office',
      [(835,400),(880,400),(880,485),(835,485)],24,6,
      '校友捐建楼宇，与鼎新楼构成庭院组团。','办公室、会议室与陈列室。')
add_b('training_hall','训练馆','gym',
      [(900,300),(950,300),(950,370),(900,370)],18,3,
      '东运动场西侧的室内训练馆。','室内训练场、器械区与更衣室。')

# ===== 五、南部中轴礼仪区（卫星图：广场两侧对称建筑）=====
add_b('teaching1','第一教学楼','classroom',
      [(430,560),(545,560),(545,605),(430,605)],24,6,
      '南门内侧中轴西侧教学楼。','多媒体教室、阶梯教室与教研室。')
add_b('admin_building','行政办公楼','office',
      [(585,560),(700,560),(700,605),(585,605)],24,6,
      '南门内侧中轴东侧的行政管理核心，楼前为礼仪广场。',
      '行政办公室、会议室、报告厅与教务服务窗口。')

# ===== 六、食堂与生活配套 =====
add_b('canteen1','第一食堂','canteen',
      [(470,465),(520,465),(520,510),(470,510)],15,3,
      '位于教学楼与图书馆之间的食堂。',CANTEEN_INT)
add_b('canteen2','第二食堂','canteen',
      [(420,330),(465,330),(465,370),(420,370)],15,3,
      '位于学生公寓附近的食堂。',CANTEEN_INT)
add_b('canteen3','第三食堂','canteen',
      [(900,195),(950,195),(950,235),(900,235)],15,3,
      '位于综合运动场附近的食堂。',CANTEEN_INT)

# ===== 七、北部运动场周边教学楼 =====
add_b('north_1','北区教学楼A','classroom',
      [(300,25),(360,25),(360,65),(300,65)],24,6,
      '北部运动场南侧教学楼。',CLASS_INT)
add_b('north_2','北区教学楼B','classroom',
      [(370,25),(430,25),(430,65),(370,65)],24,6,
      '北部运动场南侧教学楼。',CLASS_INT)
add_b('north_3','北区综合楼','office',
      [(300,75),(360,75),(360,115),(300,115)],24,6,
      '北部教学组团综合办公与实验用房。',OFFICE_INT)

# ===== 八、西部生活配套 =====
add_b('west_1','西区综合楼','office',
      [(30,200),(100,200),(100,240),(30,240)],22,5,
      '校区西侧综合服务楼。',OFFICE_INT)
add_b('west_2','西区服务中心','canteen',
      [(30,260),(100,260),(100,300),(30,300)],15,3,
      '校区西侧生活服务中心。',CANTEEN_INT)

'''
s = s[:start] + new_block + s[end:]

# Keep interiors for all non-dorm buildings + first dorm of each row (keeps GLB reasonable)
s = s.replace(
"INTERIOR_IDS=set(b['id'] for b in BUILDINGS)  # v5: 每栋楼都有内部示意",
"""INTERIOR_IDS=set(b['id'] for b in BUILDINGS if b['kind']!='dorm') | \\
             set(b['id'] for b in BUILDINGS if b['kind']=='dorm' and b['id'].endswith('_0'))""")

# brighten library photo texture at load via a brighter material
s = s.replace(
" 'library':texmat('fac_library_photo',os.path.join(TEXDIR,'facade_library_photo.jpg')),",
" 'library':texmat('fac_library_photo',os.path.join(TEXDIR,'facade_library_photo_v8.jpg')),")

io.open(dst,'w',encoding='utf-8').write(s)
print('written',dst,'buildings block',len(new_block))
