# -*- coding: utf-8 -*-
"""v9 building footprints digitized on the FULL-campus z17 satellite image
(satellite_full_z17.jpg, 2816x1792). All coordinates are ORIGINAL image pixels.
Coordinate contract: CX,CY=1408,896; RES17=0.9809 m/px.

Buildings are grouped by real campus zones read from the imagery:
 - north red-tile dorm clusters (from auto-detection + manual)
 - west gray teaching/dorm blocks
 - core teaching zone (large diagonal enclosed complex + white square + blue roofs)
 - library (real position: central-south axis, white square with dark round core)
 - south new-build zone (symmetric grid-roof halls)
 - sports halls
Each entry: (id, name, kind, [(x1,y1)...], height, floors, desc, interior)
"""
import json, os

# Auto-detected red rooftops (north dorms + scattered), x1,y1,x2,y2 in full-image px
_RED = [
 (1276,144,1370,170),(1238,264,1332,286),(1664,356,1758,378),(1296,370,1394,390),
 (1130,388,1178,404),(1424,388,1512,406),(1166,430,1256,448),(1262,454,1354,472),
 (1488,456,1578,474),(1608,456,1684,476),(1172,862,1264,886),(954,864,1030,882),
 (1066,864,1142,882),(1010,1012,1100,1032),(1124,1012,1210,1032),
]
# North red dorm rows (manual, from fine_r0_c1 / fullgrid): several long bars per row
_NORTH_DORMS = [
 (1080,230,1200,250),(1220,235,1340,255),(1350,232,1460,252),(1480,238,1590,258),
 (1070,275,1190,295),(1215,280,1335,300),(1350,278,1470,298),(1485,284,1600,304),
 (1065,320,1185,340),(1210,325,1330,345),(1345,322,1465,342),(1480,328,1595,348),
 (1060,365,1180,385),(1205,370,1325,390),(1340,368,1460,388),(1475,374,1590,394),
 (1100,410,1220,430),(1240,415,1360,435),(1380,412,1500,432),
]

def rect(x1,y1,x2,y2):
    return [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]

BUILDINGS = []
def add(id,name,kind,pts,height,floors,desc,interior,roof='flat',inner=None):
    d=dict(id=id,name=name,kind=kind,pts_px=pts,height=height,floors=floors,
           desc=desc,interior=interior,roof=roof)
    if inner: d['inner_px']=inner
    BUILDINGS.append(d)

DORM=('学生公寓，多层长条式布局，房间配空调暖气与阳台，每层设公共卫生间。',
      '宿舍标准层：房间、卫生间、洗漱区与走廊。')
CLASS=('教学楼，灰白墙面配蓝灰玻璃窗，设多媒体教室与教研室。',
       '多媒体教室、办公室与教研室。')
OFFICE=('办公/行政用房，灰色石材立面平屋顶。','办公室、会议室与业务窗口。')

# ===== 图书馆：中轴南段，白色方形+中心圆顶（全图 x=1300-1340,y=1005-1080）=====
add('library','图书馆','library',rect(1298,1005,1342,1082),60,12,
    '校园中心地标与龙子湖高校园区标志性建筑，建筑面积4.76万平方米，地上12层、高60米。方正四望如一，顶部巨大方形挑檐如盖，银白竖向石材与蓝色玻璃幕墙相间，前方为博雅广场与中轴步道，明湖、鉴湖相依。立面纹理取自正面实景照片。',
    '一层服务大厅与检索区；中庭贯通多层；二至十二层为开架书库、阅览区、自习区与研讨间。',roof='ding')

# ===== 北部红瓦宿舍群（自动检测+人工，最密集区域）=====
for i,(x1,y1,x2,y2) in enumerate(_RED):
    add('ndorm_%02d'%i,'北区宿舍%d号'%(i+1),'dorm',rect(x1,y1,x2,y2),22,6,*DORM)
for i,(x1,y1,x2,y2) in enumerate(_NORTH_DORMS):
    add('ndormr_%02d'%i,'北区宿舍楼%d'%(i+1),'dorm',rect(x1,y1,x2,y2),22,6,*DORM)

# ===== 北部灰顶楼（fine_r0_c0: x=1150-1384,y=0-160）=====
for i,(x1,y1,x2,y2) in enumerate([
    (1150,5,1240,50),(1270,5,1380,55),(1150,60,1230,95),(1285,95,1380,160)]):
    add('nbldg_%d'%i,'北区综合楼%d'%(i+1),'classroom',rect(x1,y1,x2,y2),24,6,*CLASS)

# ===== 西区灰顶长条楼群（fine_r2_c0: x=1075-1180,y=540-810）=====
for i,(x1,y1,x2,y2) in enumerate([
    (1075,548,1180,582),(1075,602,1180,636),(1075,652,1160,682),
    (1075,812,1180,842),(1075,858,1210,890),(1130,908,1210,938),
    (1075,958,1210,990),(1075,1005,1180,1035)]):
    add('wbldg_%d'%i,'西区教学楼%d'%(i+1),'classroom',rect(x1,y1,x2,y2),24,6,*CLASS)

# ===== 核心区：西侧大斜向围合教学楼（fine_r2_c0 x=1220-1300,y=600-720）=====
add('core_enclose','核心教学组团','classroom',
    [(1218,600),(1300,618),(1290,718),(1208,700)],26,6,
    '核心区标志性斜向围合式教学楼群，中间为绿化内庭。',
    '多媒体教室、办公室与教研室。',
    inner=[(1240,625),(1282,636),(1276,692),(1232,682)])

# ===== 核心区：白色方形地标楼（fine_r2_c1 x=1420-1520,y=660-730）=====
add('core_square','核心综合楼','classroom',rect(1420,660,1520,730),26,6,*CLASS)

# ===== 核心区：蓝色屋顶体育馆群（x=1560-1660,y=660-750）=====
add('bluehall','体育馆','gym',rect(1560,660,1660,750),22,3,
    '蓝色屋顶场馆，承担室内球类与集会活动。','室内球场、看台与器材室。',roof='blue')

# ===== 核心区上方灰顶楼 + 东侧运动场配套 =====
for i,(x1,y1,x2,y2) in enumerate([
    (1580,555,1650,600),(1285,95,1380,160)]):
    add('core_aux%d'%i,'核心区配套楼%d'%(i+1),'office',rect(x1,y1,x2,y2),22,5,*OFFICE)

# ===== 中南区：大型围合庭院楼群（fine_r3_c1 x=1400-1570,y=860-970）=====
add('south_court1','南部庭院组团','classroom',
    [(1400,862),(1565,872),(1558,968),(1395,958)],24,6,
    '南部庭院式教学组团，围合出绿化内庭。','教室、会议室与中庭共享空间。',
    inner=[(1430,885),(1535,892),(1530,945),(1425,938)])
add('south_court2','南部弧线楼','office',
    [(1560,1000),(1680,1015),(1670,1075),(1555,1060)],24,6,*OFFICE)

# ===== 南部新区：中轴两侧对称网格顶楼（fine_r4_c0）=====
for i,(x1,y1,x2,y2) in enumerate([
    (1190,1150,1330,1182),(1210,1200,1300,1238),
    (1100,1300,1160,1350),(1290,1300,1345,1350)]):
    add('snew_%d'%i,'南部新建楼%d'%(i+1),'classroom',rect(x1,y1,x2,y2),24,6,*CLASS)

# ===== 运动场配套看台/训练馆（r2_c0 x=780-1000,y=1220-1300）=====
add('west_gym','西区体育馆','gym',rect(790,1220,980,1290),20,3,
    '西区体育场馆与看台。','室内球场、看台与器材室。',roof='blue')

# ===== 食堂（据卫星图零散小楼）=====
add('canteen1','第一食堂','canteen',rect(1080,640,1130,690),15,3,
    '学生食堂。','一层基本餐厅，二层风味小吃。')
add('canteen2','第二食堂','canteen',rect(1240,560,1290,600),15,3,
    '学生食堂。','多层就餐大厅与风味窗口。')

if __name__=='__main__':
    print('v9 buildings',len(BUILDINGS))
