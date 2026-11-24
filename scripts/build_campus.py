# -*- coding: utf-8 -*-
"""Generate a Blender 3D scene for Henan University of Economics and Law, Zhengdong Campus.
Uses public coordinates / public building descriptions. Footprints are schematic, not survey data.
Run: python build_campus.py
"""
import bpy
import json
import math
import os
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "..", "output")
WEB = os.path.join(ROOT, "..", "web")
os.makedirs(OUT, exist_ok=True)
os.makedirs(WEB, exist_ok=True)

LAT0 = 34.7826
LON0 = 113.8200
MX = 111320.0 * math.cos(math.radians(LAT0))
MY = 110570.0

def to_xy(lat, lon):
    return ((lon - LON0) * MX, (lat - LAT0) * MY)

# ---------- scene reset ----------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name != 'Collection':
        bpy.data.collections.remove(c)
base_col = bpy.data.collections.get('Collection')
if base_col:
    base_col.name = 'SITE'

site_col = base_col
building_col = bpy.data.collections.new('BUILDINGS')
interior_col = bpy.data.collections.new('INTERIORS')
bpy.context.scene.collection.children.link(building_col)
bpy.context.scene.collection.children.link(interior_col)

scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0

# ---------- materials ----------
def mat(name, color, rough=0.85, metal=0.0, emissive=None):
    m = bpy.data.materials.new(name=name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (*color, 1.0)
        bsdf.inputs['Roughness'].default_value = rough
        bsdf.inputs['Metallic'].default_value = metal
        if emissive:
            bsdf.inputs['Emission Color'].default_value = (*emissive, 1.0)
            bsdf.inputs['Emission Strength'].default_value = 0.8
    return m

M = {
    'grass': mat('grass', (0.29, 0.48, 0.28)),
    'road': mat('road', (0.28, 0.30, 0.33)),
    'path': mat('path', (0.72, 0.69, 0.60)),
    'water': mat('water', (0.16, 0.45, 0.62), rough=0.25, metal=0.15),
    'track': mat('track', (0.62, 0.20, 0.16)),
    'field': mat('field', (0.24, 0.52, 0.27)),
    'wall': mat('wall', (0.80, 0.77, 0.70)),
    'wall_warm': mat('wall_warm', (0.72, 0.61, 0.49)),
    'wall_brick': mat('wall_brick', (0.60, 0.40, 0.33)),
    'roof': mat('roof', (0.32, 0.36, 0.42)),
    'roof_red': mat('roof_red', (0.48, 0.23, 0.20)),
    'glass': mat('glass', (0.16, 0.30, 0.42), rough=0.18, metal=0.35),
    'glass_warm': mat('glass_warm', (0.36, 0.42, 0.44), rough=0.2, metal=0.2),
    'stone': mat('stone', (0.68, 0.67, 0.62)),
    'tree': mat('tree', (0.18, 0.40, 0.22)),
    'tree2': mat('tree2', (0.30, 0.50, 0.25)),
    'trunk': mat('trunk', (0.36, 0.26, 0.18)),
    'wood': mat('wood', (0.52, 0.36, 0.22)),
    'floor': mat('floor', (0.86, 0.84, 0.78)),
    'partition': mat('partition', (0.90, 0.89, 0.84)),
    'desk': mat('desk', (0.62, 0.45, 0.30)),
    'chair': mat('chair', (0.25, 0.30, 0.38)),
    'shelf': mat('shelf', (0.42, 0.30, 0.20)),
    'book': mat('book', (0.65, 0.25, 0.22)),
    'light': mat('light', (1.0, 0.94, 0.72), emissive=(1.0, 0.9, 0.6)),
    'bed': mat('bed', (0.82, 0.82, 0.86)),
    'court': mat('court', (0.30, 0.46, 0.34)),
    'counter': mat('counter', (0.55, 0.58, 0.60)),
}

# ---------- helpers ----------
def empty(name, col):
    e = bpy.data.objects.new(name, None)
    col.objects.link(e)
    return e

def add_box(name, loc, dims, material, col, parent=None, rot=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=(0, 0, rot))
    o = bpy.context.object
    o.name = name
    o.scale = dims
    o.data.materials.append(material)
    for c in list(o.users_collection):
        c.objects.unlink(o)
    col.objects.link(o)
    if parent:
        o.parent = parent
    return o

def add_cyl(name, loc, radius, depth, material, col, vertices=16, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    for c in list(o.users_collection):
        c.objects.unlink(o)
    col.objects.link(o)
    if parent:
        o.parent = parent
    return o

def add_cone(name, loc, radius, depth, material, col, vertices=7, parent=None):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=radius, radius2=0, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    for c in list(o.users_collection):
        c.objects.unlink(o)
    col.objects.link(o)
    if parent:
        o.parent = parent
    return o

def add_plane(name, loc, dims, material, col, rot=0.0):
    return add_box(name, loc, (dims[0], dims[1], 0.12), material, col, rot=rot)

def add_frustum(name, loc, bx, by, tx, ty, z0, z1, material, col):
    verts = [(-bx, -by, z0), (bx, -by, z0), (bx, by, z0), (-bx, by, z0),
             (-tx, -ty, z1), (tx, -ty, z1), (tx, ty, z1), (-tx, ty, z1)]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5),
             (2, 3, 7, 6), (3, 0, 4, 7)]
    mesh = bpy.data.meshes.new(name + '_mesh')
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    col.objects.link(o)
    o.data.materials.append(material)
    o.location = loc
    return o

# ---------- site ----------
add_box('SITE_ground', (0, 0, -0.6), (1100, 1300, 1.0), M['grass'], site_col)

# perimeter + internal roads
add_plane('SITE_road_ns', (5, -10, 0.08), (26, 1080), M['road'], site_col)
add_plane('SITE_road_ew', (10, -125, 0.09), (820, 22), M['road'], site_col)
add_plane('SITE_road_ring_w', (-320, 0, 0.08), (14, 900), M['road'], site_col)
add_plane('SITE_road_ring_e', (330, 0, 0.08), (14, 900), M['road'], site_col)
add_plane('SITE_road_ring_n', (5, 440, 0.08), (660, 14), M['road'], site_col)
add_plane('SITE_road_ring_s', (5, -440, 0.08), (660, 14), M['road'], site_col)
add_plane('SITE_road_lib', (-50, -180, 0.09), (180, 14), M['path'], site_col)
add_plane('SITE_axis_north', (0, 300, 0.09), (18, 300), M['path'], site_col)

# lakes
add_cyl('SITE_lake_ming', (-185, -115, 0.16), 78, 0.25, M['water'], site_col, vertices=24)
add_cyl('SITE_lake_jian', (105, -175, 0.16), 62, 0.25, M['water'], site_col, vertices=20)
add_plane('SITE_stream', (-45, -145, 0.14), (140, 10), M['water'], site_col)

# sports field
add_plane('SITE_track', (295, -355, 0.14), (190, 120), M['track'], site_col)
add_plane('SITE_field', (295, -355, 0.20), (150, 82), M['field'], site_col)

#弘毅山
add_cone('SITE_hongyi_hill', (300, 300, 12), 62, 24, M['stone'], site_col, vertices=12)
add_cone('SITE_hongyi_hill2', (255, 270, 8), 38, 16, M['stone'], site_col, vertices=10)

# plaza
add_cyl('SITE_plaza', (35, 95, 0.15), 95, 0.2, M['stone'], site_col, vertices=8)
add_cyl('SITE_flag_base', (35, 150, 0.3), 12, 0.5, M['stone'], site_col, vertices=8)
add_box('SITE_flag_pole', (35, 150, 14), (0.8, 0.8, 28), M['roof'], site_col)

# trees (shared meshes via linked objects)
def make_tree_mesh(name, radius, depth, material):
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=radius, radius2=0, depth=depth)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    mesh = o.data
    bpy.data.objects.remove(o, do_unlink=True)
    return mesh

crown_mesh = make_tree_mesh('tree_crown_mesh', 5.0, 12, M['tree'])
crown_mesh2 = make_tree_mesh('tree_crown_mesh2', 4.2, 10, M['tree2'])
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.9, depth=4)
trunk_obj = bpy.context.object
trunk_mesh = trunk_obj.data
trunk_mesh.materials.append(M['trunk'])
bpy.data.objects.remove(trunk_obj, do_unlink=True)

tree_seed = 20261121
import random
random.seed(tree_seed)
tree_positions = []
for i in range(120):
    x = random.uniform(-500, 510)
    y = random.uniform(-590, 590)
    # avoid roads, lakes, sports field, plaza
    if abs(x) < 20 and -540 < y < 540:
        continue
    if abs(y + 125) < 22 and abs(x) < 410:
        continue
    if (x + 185) ** 2 + (y + 115) ** 2 < 90 ** 2:
        continue
    if (x - 105) ** 2 + (y + 175) ** 2 < 75 ** 2:
        continue
    if 180 < x < 410 and -430 < y < -280:
        continue
    if (x - 35) ** 2 + (y - 95) ** 2 < 105 ** 2:
        continue
    tree_positions.append((x, y))

for i, (x, y) in enumerate(tree_positions):
    s = random.uniform(0.8, 1.35)
    c = bpy.data.objects.new('SITE_tree_%03d' % i, crown_mesh if i % 3 else crown_mesh2)
    site_col.objects.link(c)
    c.location = (x, y, 4 * s + 4)
    c.scale = (s, s, s)
    t = bpy.data.objects.new('SITE_trunk_%03d' % i, trunk_mesh)
    site_col.objects.link(t)
    t.location = (x, y, 2 * s)
    t.scale = (s, s, s)

# ---------- buildings ----------
BUILDINGS = [
    dict(id='library', name='图书馆', cn='图书馆', kind='library', lat=34.781433, lon=113.819460,
         w=92, d=74, h=40, rot=0, floors=5, wall='wall', roof='roof',
         desc='校园中心地标，外观呈矩形、四望如一，倒梯形方形屋顶状如宝鼎，寓意鼎立中原。',
         interior='一层为服务大厅与检索区；二至五层为开架书库、阅览区与自习区，设有研讨间和电子阅览室。'),
    dict(id='zhishan', name='至善楼（综合办公楼）', kind='office', lat=34.783743, lon=113.820591,
         w=74, d=46, h=33, rot=0, floors=7, wall='wall', roof='roof',
         desc='取“大学之道，在明明德，在亲民，在止于至善”之意。学校行政管理核心，位于校园中轴线重要位置。',
         interior='内设职能部门办公室、会议室、报告厅与档案室，中部为通高共享大厅。'),
    dict(id='wentao', name='文韬楼（第一教学楼）', kind='classroom', lat=34.78480, lon=113.81900,
         w=84, d=42, h=25, rot=0, floors=6, wall='wall_warm', roof='roof',
         desc='第一教学楼，日常授课主阵地，教室配备多媒体设备。与文锦楼之间植有成排桂花。',
         interior='标准多媒体教室、阶梯教室与教师休息室，每层设中部走廊与两侧教室。'),
    dict(id='wenjin', name='文锦楼（第二教学楼）', kind='classroom', lat=34.78450, lon=113.82140,
         w=84, d=42, h=25, rot=0, floors=6, wall='wall_warm', roof='roof',
         desc='第二教学楼，与文韬楼并肩承担大量日常教学任务，南侧道路两旁夏日木槿盛开。',
         interior='普通教室、多媒体教室与研讨室，走廊连接东西两侧教学单元。'),
    dict(id='zhixing', name='知行楼（综合实验楼）', kind='lab', lat=34.78260, lon=113.82200,
         w=72, d=46, h=29, rot=0, floors=6, wall='wall', roof='roof',
         desc='取“知行合一”之意，承担上机课、实践课等实验教学任务。',
         interior='计算机实验室、专业实验室、实训室与准备间，配置实验台与设备机柜。'),
    dict(id='bowen', name='博文楼（教学科研楼）', kind='office', lat=34.78540, lon=113.82240,
         w=68, d=42, h=27, rot=0, floors=6, wall='wall', roof='roof',
         desc='取“君子博学于文，约之以礼”之意，承担部分教学任务，也是多个院系办公室所在地。',
         interior='院系办公室、教研室、小型报告室与科研工作室。'),
    dict(id='chongfa', name='崇法楼（法学部综合楼）', kind='classroom', lat=34.78620, lon=113.82330,
         w=62, d=40, h=27, rot=0, floors=6, wall='wall_brick', roof='roof_red',
         desc='取“尚法，则国富民强”之意，法学部核心阵地，常年举办法学学术讲座。',
         interior='法学专业教室、模拟法庭、学术报告厅与教研办公室。'),
    dict(id='dingxin_a', name='鼎新楼A座（大学生科创中心）', kind='lab', lat=34.78060, lon=113.82300,
         w=52, d=38, h=23, rot=0, floors=5, wall='wall', roof='roof',
         desc='取“革故鼎新”之意，大学生科创中心A座，功能多元复合。',
         interior='创新工坊、创客空间、项目工作室与成果展示区。'),
    dict(id='dingxin_b', name='鼎新楼B座（大学生科创中心）', kind='lab', lat=34.78010, lon=113.82320,
         w=52, d=38, h=23, rot=0, floors=5, wall='wall', roof='roof',
         desc='大学生科创中心B座，与A座共同构成学生创新创业实践平台。',
         interior='竞赛训练室、路演厅、开放式工位与设备间。'),
    dict(id='jianshu', name='建树楼', kind='office', lat=34.77950, lon=113.82180,
         w=62, d=40, h=26, rot=0, floors=6, wall='wall_warm', roof='roof',
         desc='取“建功立业、有所作为”之意，寄托学有所成、业有所立的期许。',
         interior='行政与服务中心办公室、会议室及校友交流空间。'),
    dict(id='canteen1', name='第一食堂', kind='canteen', lat=34.78400, lon=113.81960,
         w=58, d=38, h=15, rot=0, floors=3, wall='wall_warm', roof='roof_red',
         desc='位于教学楼附近。一楼为基本伙食，二楼汇聚各地特色风味小吃并设钢琴与中央屏幕。',
         interior='一层为基本餐厅与备餐区，二层为风味小吃区与休闲就餐区。'),
    dict(id='canteen2', name='第二食堂（知味轩餐厅）', kind='canteen', lat=34.78000, lon=113.81750,
         w=64, d=40, h=16, rot=0, floors=3, wall='wall_warm', roof='roof_red',
         desc='位于学生公寓附近，一楼品类丰富，二楼为时尚餐厅，三楼为民族餐厅和教工餐厅。',
         interior='多层就餐大厅、风味窗口、民族餐厅与教工餐厅。'),
    dict(id='canteen3', name='第三食堂', kind='canteen', lat=34.77880, lon=113.82280,
         w=56, d=36, h=15, rot=0, floors=3, wall='wall_warm', roof='roof_red',
         desc='位于综合运动场附近。一楼为区域特色美食，二楼为自选餐厅和特色美食。',
         interior='自选餐厅、特色风味档口与公共就餐区。'),
    dict(id='museum', name='博物馆', kind='museum', lat=34.78430, lon=113.81820,
         w=48, d=36, h=19, rot=0, floors=2, wall='stone', roof='roof',
         desc='校史与文物展示空间，位于教学区西侧。',
         interior='序厅、校史展厅、专题展厅与文物库房，设置展柜与图文展板。'),
    dict(id='student_center', name='大学生活动中心', kind='activity', lat=34.77900, lon=113.82000,
         w=58, d=44, h=21, rot=0, floors=3, wall='wall_warm', roof='roof_red',
         desc='学生社团活动、演出与竞赛交流场所。',
         interior='多功能厅、排练室、社团活动室与公共服务空间。'),
    dict(id='gym', name='体育馆', kind='gym', lat=34.77850, lon=113.82400,
         w=86, d=58, h=24, rot=0, floors=2, wall='wall', roof='roof',
         desc='综合运动场旁的室内体育场馆，承担球类与大型活动。',
         interior='室内篮球场、排球场、看台与器材室。'),
    dict(id='admin_annex', name='行政楼东配楼', kind='office', lat=34.78360, lon=113.82130,
         w=46, d=32, h=25, rot=0, floors=6, wall='wall', roof='roof',
         desc='综合办公楼东侧配楼，设报告厅与会议空间。',
         interior='报告厅、会议室与行政办公室。'),
]

# dorm clusters
DORMS = [
    ('jing', '静苑', 34.78580, 113.81720, 4),
    ('ya', '雅苑', 34.78650, 113.82200, 4),
    ('xin', '馨苑', 34.77900, 113.81680, 4),
    ('yi', '怡苑', 34.77950, 113.82350, 4),
]
for key, name, lat, lon, n in DORMS:
    bx, by = to_xy(lat, lon)
    for i in range(n):
        ox = bx + (i - (n - 1) / 2) * 34
        oy = by + (8 if i % 2 else -8)
        # convert offset back to lat/lon for metadata
        la = LAT0 + oy / MY
        lo = LON0 + ox / MX
        BUILDINGS.append(dict(
            id='%s%d' % (key, i + 1), name='%s%d号楼' % (name, i + 1), kind='dorm',
            lat=la, lon=lo, w=28, d=18, h=24, rot=0, floors=6,
            wall='wall_warm', roof='roof_red',
            desc='%s学生公寓，四人间/六人间，每层设公共卫生间与浴室，配备空调、暖气、阳台与电脑桌。' % name,
            interior='学生宿舍标准层：房间、公共卫生间、洗漱区与走廊。怡苑设独立卫浴，馨苑每层设洗澡隔间。'
        ))

INTERIOR_IDS = {'library', 'zhishan', 'wentao', 'zhixing', 'canteen1', 'canteen2',
                'museum', 'gym', 'student_center', 'jing1'}

def build_exterior(b):
    x, y = to_xy(b['lat'], b['lon'])
    name = b['id']
    parent = empty('GRP_' + name, building_col)
    wall_m = M[b['wall']]
    roof_m = M[b['roof']]
    add_box('B_%s_body' % name, (x, y, b['h'] / 2), (b['w'], b['d'], b['h']), wall_m, building_col, parent)
    if name == 'library':
        add_frustum('B_%s_roof' % name, (x, y, 0), b['w'] * 0.44, b['d'] * 0.44,
                    b['w'] * 0.60, b['d'] * 0.60, b['h'] - 2, b['h'] + 9,
                    M['roof'], building_col)
    else:
        add_box('B_%s_roof' % name, (x, y, b['h'] + 1.2), (b['w'] + 3, b['d'] + 3, 2.4),
                roof_m, building_col, parent)
    # window bands
    fh = b['h'] / b['floors']
    for f in range(b['floors']):
        z = f * fh + fh * 0.62
        for side in range(4):
            if side == 0:
                loc = (x, y - b['d'] / 2 - 0.15, z)
                dim = (b['w'] * 0.86, 0.5, fh * 0.42)
            elif side == 1:
                loc = (x, y + b['d'] / 2 + 0.15, z)
                dim = (b['w'] * 0.86, 0.5, fh * 0.42)
            elif side == 2:
                loc = (x - b['w'] / 2 - 0.15, y, z)
                dim = (0.5, b['d'] * 0.86, fh * 0.42)
            else:
                loc = (x + b['w'] / 2 + 0.15, y, z)
                dim = (0.5, b['d'] * 0.86, fh * 0.42)
            add_box('B_%s_win_%d_%d' % (name, f, side), loc, dim,
                    M['glass'] if f % 2 == 0 else M['glass_warm'], building_col, parent)
    # entrance canopy
    add_box('B_%s_entrance' % name, (x, y - b['d'] / 2 - 2.5, 3.2),
            (min(20, b['w'] * 0.28), 5, 6.4), M['stone'], building_col, parent)


def build_interior(b):
    name = b['id']
    x, y = to_xy(b['lat'], b['lon'])
    root = empty('INT_' + name, interior_col)
    w = b['w'] * 0.84
    d = b['d'] * 0.84
    fh = min(4.2, b['h'] / b['floors'])
    levels = min(b['floors'], 3)
    kind = b['kind']
    for lv in range(levels):
        z = 0.8 + lv * fh
        add_box('IN_%s_floor_%d' % (name, lv), (x, y, z), (w, d, 0.35), M['floor'], interior_col, root)
        add_box('IN_%s_wallN_%d' % (name, lv), (x, y + d / 2, z + fh / 2), (w, 0.4, fh - 0.6), M['partition'], interior_col, root)
        add_box('IN_%s_wallS_%d' % (name, lv), (x, y - d / 2, z + fh / 2), (w, 0.4, fh - 0.6), M['partition'], interior_col, root)
        add_box('IN_%s_wallW_%d' % (name, lv), (x - w / 2, y, z + fh / 2), (0.4, d, fh - 0.6), M['partition'], interior_col, root)
        add_box('IN_%s_wallE_%d' % (name, lv), (x + w / 2, y, z + fh / 2), (0.4, d, fh - 0.6), M['partition'], interior_col, root)
        add_box('IN_%s_corridor_%d' % (name, lv), (x, y, z + 0.22), (w * 0.9, 3.0, 0.05), M['path'], interior_col, root)
        # room dividers
        for k in range(1, 4):
            add_box('IN_%s_div_%d_%d' % (name, lv, k),
                    (x - w / 2 + w * k / 4, y + d * 0.22, z + fh / 2),
                    (0.35, d * 0.5, fh - 0.8), M['partition'], interior_col, root)

        zt = z + 0.9
        if kind in ('classroom', 'office', 'lab'):
            for r in range(3):
                for c in range(4):
                    dx = x - w * 0.30 + c * (w * 0.20)
                    dy = y - d * 0.26 + r * (d * 0.20)
                    add_box('IN_%s_desk_%d_%d_%d' % (name, lv, r, c), (dx, dy, zt + 0.9),
                            (3.2, 1.8, 0.18), M['desk'], interior_col, root)
                    add_box('IN_%s_chair_%d_%d_%d' % (name, lv, r, c), (dx, dy - 1.6, zt + 0.6),
                            (1.4, 1.2, 1.2), M['chair'], interior_col, root)
            add_box('IN_%s_podium_%d' % (name, lv), (x, y + d * 0.36, zt + 1.1),
                    (6, 2, 2.2), M['wood'], interior_col, root)
        elif kind == 'library':
            for r in range(4):
                for c in range(3):
                    dx = x - w * 0.30 + c * (w * 0.28)
                    dy = y - d * 0.28 + r * (d * 0.20)
                    add_box('IN_%s_shelf_%d_%d_%d' % (name, lv, r, c), (dx, dy, zt + 1.6),
                            (0.7, 7.0, 3.2), M['shelf'], interior_col, root)
                    add_box('IN_%s_books_%d_%d_%d' % (name, lv, r, c), (dx + 0.42, dy, zt + 1.6),
                            (0.18, 6.6, 2.8), M['book'], interior_col, root)
            for r in range(2):
                add_box('IN_%s_readtable_%d_%d' % (name, lv, r), (x, y - d * 0.2 + r * d * 0.35, zt + 0.9),
                        (w * 0.45, 2.2, 0.2), M['wood'], interior_col, root)
        elif kind == 'canteen':
            add_box('IN_%s_counter_%d' % (name, lv), (x, y + d * 0.34, zt + 1.2),
                    (w * 0.72, 2.2, 2.4), M['counter'], interior_col, root)
            for r in range(3):
                for c in range(4):
                    dx = x - w * 0.30 + c * (w * 0.20)
                    dy = y - d * 0.22 + r * (d * 0.22)
                    add_cyl('IN_%s_table_%d_%d_%d' % (name, lv, r, c), (dx, dy, zt + 0.9),
                            1.9, 0.18, M['wood'], interior_col, vertices=10, parent=root)
        elif kind == 'dorm':
            for r in range(2):
                for c in range(3):
                    dx = x - w * 0.28 + c * (w * 0.27)
                    dy = y - d * 0.22 + r * (d * 0.3)
                    add_box('IN_%s_bed_%d_%d_%d' % (name, lv, r, c), (dx, dy, zt + 0.7),
                            (3.6, 2.0, 1.0), M['bed'], interior_col, root)
                    add_box('IN_%s_desk2_%d_%d_%d' % (name, lv, r, c), (dx, dy + 2.6, zt + 0.9),
                            (3.0, 1.2, 0.16), M['desk'], interior_col, root)
            add_box('IN_%s_wet_%d' % (name, lv), (x + w * 0.38, y + d * 0.3, zt + 1.2),
                    (4, 5, 2.4), M['counter'], interior_col, root)
        elif kind == 'gym':
            add_box('IN_%s_court_%d' % (name, lv), (x, y, z + 0.25), (w * 0.7, d * 0.6, 0.1), M['court'], interior_col, root)
            for s in (-1, 1):
                add_box('IN_%s_stand_%d_%d' % (name, lv, s), (x, y + s * d * 0.38, z + 1.0),
                        (w * 0.7, 5, 2.0), M['chair'], interior_col, root)
        elif kind == 'museum':
            for r in range(3):
                for c in range(4):
                    dx = x - w * 0.30 + c * (w * 0.20)
                    dy = y - d * 0.25 + r * (d * 0.24)
                    add_box('IN_%s_case_%d_%d_%d' % (name, lv, r, c), (dx, dy, zt + 1.0),
                            (2.6, 1.8, 2.0), M['glass_warm'], interior_col, root)
        elif kind == 'activity':
            add_box('IN_%s_stage_%d' % (name, lv), (x, y + d * 0.34, z + 0.8),
                    (w * 0.5, 5, 1.5), M['wood'], interior_col, root)
            for r in range(3):
                for c in range(5):
                    dx = x - w * 0.32 + c * (w * 0.16)
                    dy = y - d * 0.25 + r * (d * 0.20)
                    add_box('IN_%s_seat_%d_%d_%d' % (name, lv, r, c), (dx, dy, zt + 0.6),
                            (1.6, 1.4, 1.2), M['chair'], interior_col, root)
        # ceiling lights
        for k in range(3):
            add_box('IN_%s_light_%d_%d' % (name, lv, k),
                    (x - w * 0.25 + k * w * 0.25, y, z + fh - 0.5),
                    (3.0, 1.0, 0.15), M['light'], interior_col, root)

for b in BUILDINGS:
    build_exterior(b)
    if b['id'] in INTERIOR_IDS:
        build_interior(b)

# ---------- camera / world ----------
bpy.ops.object.camera_add(location=(-520, -620, 520), rotation=(math.radians(55), 0, math.radians(-35)))
cam = bpy.context.object
cam.name = 'OverviewCamera'
scene.camera = cam
world = bpy.data.worlds.new('CampusWorld')
scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.68, 0.78, 0.90, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.8

# ---------- save .blend ----------
blend_path = os.path.abspath(os.path.join(OUT, 'HUEL_Zhengdong_Campus.blend'))
bpy.ops.wm.save_as_mainfile(filepath=blend_path)

# ---------- export glb ----------
def export_selection(filepath):
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.context.scene.objects:
        if o.name.startswith('B_') or o.name.startswith('SITE_') or o.name.startswith('GRP_'):
            if '_INT_' not in o.name:
                o.select_set(True)
    bpy.context.view_layer.objects.active = None
    bpy.ops.export_scene.gltf(filepath=filepath, export_format='GLB', use_selection=True,
                              export_apply=False, export_yup=True,
                              export_materials='EXPORT', export_extras=True,
                              export_cameras=False, export_lights=False,
                              export_normals=True, export_texcoords=False)

def export_interiors(filepath):
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.context.scene.objects:
        if o.name.startswith('INT_') or o.name.startswith('IN_'):
            o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=filepath, export_format='GLB', use_selection=True,
                              export_apply=False, export_yup=True,
                              export_materials='EXPORT', export_extras=True,
                              export_cameras=False, export_lights=False,
                              export_normals=True, export_texcoords=False)

ext_path = os.path.abspath(os.path.join(OUT, 'campus_exterior.glb'))
int_path = os.path.abspath(os.path.join(OUT, 'campus_interiors.glb'))
export_selection(ext_path)
export_interiors(int_path)

# ---------- metadata ----------
meta = []
for b in BUILDINGS:
    x, y = to_xy(b['lat'], b['lon'])
    meta.append(dict(
        id=b['id'], name=b['name'], kind=b['kind'], lat=b['lat'], lon=b['lon'],
        x=round(x, 2), y=round(y, 2), z=round(b['h'] / 2, 2),
        height=b['h'], floors=b['floors'],
        desc=b['desc'], interior=b['interior'],
        hasInterior=b['id'] in INTERIOR_IDS
    ))
with open(os.path.join(WEB, 'buildings.json'), 'w', encoding='utf-8') as f:
    json.dump(dict(
        campus=dict(name='河南财经政法大学（郑东校区）', lat0=LAT0, lon0=LON0,
                    address='河南省郑州市金水东路180号',
                    note='建筑坐标依据公开地图与公开资料复原，建筑轮廓为三维示意，非测绘画成果。'),
        buildings=meta
    ), f, ensure_ascii=False, indent=2)

print('DONE')
print('blend:', blend_path)
print('exterior:', ext_path, os.path.getsize(ext_path))
print('interiors:', int_path, os.path.getsize(int_path))
print('buildings:', len(BUILDINGS))
