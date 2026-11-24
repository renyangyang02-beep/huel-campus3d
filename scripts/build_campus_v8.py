# -*- coding: utf-8 -*-
"""v8: 按高德最新卫星影像逐栋数字化全部建筑轮廓（约38栋），修正宿舍区/核心教学区
的真实排布，图书馆立面提亮。基于多渠道实景照片（官网/微信公众号）校准配色。
（原v7说明：）
- 卫星底图替换为高德最新无注记影像（与模型坐标系配准一致）。
- v8: 建筑由24栋扩到38栋，宿舍区按卫星图5-6排逐栋重建，核心区改斜向围合+田字楼群，图书馆纹理提亮。
- 依据学校官方平面图补充行政办公楼、第二教学楼、训练馆。
- 知行楼/综合实验楼采用实景照片中的橙红格栅+灰砖配色。"""
import bpy, json, math, os, random

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(ROOT, '..', 'output'))
WEB = os.path.abspath(os.path.join(ROOT, '..', 'web'))
os.makedirs(WEB, exist_ok=True)

LAT0, LON0 = 34.7826, 113.8200
MX = 111320.0 * math.cos(math.radians(LAT0))
MY = 110570.0
RES17 = 156543.03392 * math.cos(math.radians(LAT0)) / (2 ** 17)
RES16 = 156543.03392 * math.cos(math.radians(LAT0)) / (2 ** 16)
CX, CY = 1264 / 2, 625 / 2

def px_to_xy(px, py):
    return ((px - CX) * RES17, (CY - py) * RES17)

def xy_to_ll(x, y):
    return (LAT0 + y / MY, LON0 + x / MX)

# ---------- reset ----------
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name != 'Collection': bpy.data.collections.remove(c)
site_col = bpy.data.collections.get('Collection'); site_col.name = 'SITE'
build_col = bpy.data.collections.new('BUILDINGS')
interior_col = bpy.data.collections.new('INTERIORS')
bpy.context.scene.collection.children.link(build_col)
bpy.context.scene.collection.children.link(interior_col)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'

# ---------- materials ----------
def mat(name, color, rough=.85, metal=0, emissive=None):
    m = bpy.data.materials.new(name); m.diffuse_color=(*color,1)
    m.use_nodes=True
    b=m.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value=(*color,1)
        b.inputs['Roughness'].default_value=rough
        b.inputs['Metallic'].default_value=metal
        if emissive:
            b.inputs['Emission Color'].default_value=(*emissive,1)
            b.inputs['Emission Strength'].default_value=.8
    return m

def texmat(name, img, rough=.85):
    m=bpy.data.materials.new(name); m.use_nodes=True
    nt=m.node_tree; bs=nt.nodes.get('Principled BSDF')
    tex=nt.nodes.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(img, check_existing=True)
    nt.links.new(tex.outputs['Color'], bs.inputs['Base Color'])
    bs.inputs['Roughness'].default_value=rough
    return m

M = {
 'wall':mat('wall_light_gray',(0.73,0.75,0.77)),
 'band':mat('band_dusty_pink',(0.67,0.51,0.51)),
 'glass':mat('glass_blue',(0.17,0.29,0.44),rough=.2,metal=.3),
 'roof':mat('roof_light',(0.80,0.82,0.83)),
 'roof_blue':mat('roof_blue',(0.22,0.40,0.62)),
 'stone':mat('stone',(0.72,0.71,0.67)),
 'wood':mat('wood',(0.55,0.38,0.24)),
 'floor':mat('floor',(0.88,0.86,0.80)),
 'partition':mat('partition',(0.92,0.91,0.86)),
 'desk':mat('desk',(0.62,0.45,0.30)),
 'chair':mat('chair',(0.25,0.30,0.38)),
 'shelf':mat('shelf',(0.42,0.30,0.20)),
 'book':mat('book',(0.65,0.25,0.22)),
 'light':mat('light',(1,.94,.72),emissive=(1,.9,.6)),
 'bed':mat('bed',(.82,.82,.86)),
 'counter':mat('counter',(.55,.58,.60)),
 'court':mat('court',(.30,.46,.34)),
 'tree':mat('tree',(.20,.43,.24)),
 'trunk':mat('trunk',(.36,.26,.18)),
 'water':mat('water_blue',(.13,.36,.48),rough=.25,metal=.15),
 'plaza':mat('plaza_stone',(.78,.77,.73)),
 'glass2':mat('glass_blue_light',(.30,.52,.72),rough=.18,metal=.35),
 'trim':mat('trim_white',(.90,.90,.88)),
 'green':mat('roof_green',(.42,.52,.38)),
 # v5 interior detail materials
 'ceiling':mat('ceiling',(.95,.95,.93)),
 'wallin':mat('wallin',(.86,.87,.84)),
 'door':mat('door',(.45,.30,.20)),
 'doorframe':mat('doorframe',(.75,.72,.68)),
 'glasswall':mat('glasswall',(.55,.72,.82),rough=.15,metal=.2),
 'teacherdesk':mat('teacherdesk',(.50,.36,.24)),
 'blackboard':mat('blackboard',(.15,.22,.19)),
 'computer':mat('computer',(.20,.24,.30)),
 'labbench':mat('labbench',(.78,.80,.78)),
 'wardrobe':mat('wardrobe',(.62,.52,.40)),
 'toilet':mat('toilet',(.92,.92,.94)),
 'plant':mat('plant',(.28,.48,.26)),
 'stair':mat('stair',(.70,.68,.62)),
 'rail':mat('rail',(.60,.62,.65),metal=.5,rough=.4),
 'courtline':mat('courtline',(.92,.92,.90)),
 'track':mat('track',(.62,.28,.24)),
 'seat':mat('seat',(.32,.40,.58)),
 'flag':mat('flag',(.78,.15,.16)),
 'lamp':mat('lamp',(.30,.32,.34)),
 'car':mat('car',(.35,.40,.48),rough=.4,metal=.3),
 'road':mat('road',(.30,.31,.32)),
}
TEXDIR=os.path.join(OUT,'tex')
# v7: 图书馆用真实正面照片裁切的纹理；其余沿用程序纹理
T = {
 'classroom':texmat('fac_classroom',os.path.join(TEXDIR,'facade_classroom.jpg')),
 'office':texmat('fac_office',os.path.join(TEXDIR,'facade_office.jpg')),
 'dorm':texmat('fac_dorm',os.path.join(TEXDIR,'facade_dorm.jpg')),
 'library':texmat('fac_library_photo',os.path.join(TEXDIR,'facade_library_photo_v8.jpg')),
 'canteen':texmat('fac_canteen',os.path.join(TEXDIR,'facade_canteen.jpg')),
 'gym':texmat('fac_office_gym',os.path.join(TEXDIR,'facade_office.jpg')),
}
# 知行楼/综合实验楼：实景照片中的橙红格栅 + 灰砖（若照片纹理存在则用）
_lab_tex=os.path.join(TEXDIR,'facade_lab_red.jpg')
T['lab']=texmat('fac_lab_red',_lab_tex) if os.path.exists(_lab_tex) else T['classroom']
M['roof_red']=texmat('roof_red_tiles',os.path.join(TEXDIR,'roof_red.jpg'))

# ---------- textured ground ----------
def textured_plane(name, img_path, w, h, z, col):
    img = bpy.data.images.load(img_path, check_existing=True)
    m = bpy.data.materials.new(name+'_mat'); m.use_nodes=True
    nt=m.node_tree; bs=nt.nodes.get('Principled BSDF')
    tex=nt.nodes.new('ShaderNodeTexImage'); tex.image=img
    nt.links.new(tex.outputs['Color'], bs.inputs['Base Color'])
    mesh=bpy.data.meshes.new(name+'_mesh')
    mesh.from_pydata([(-w/2,-h/2,0),(w/2,-h/2,0),(w/2,h/2,0),(-w/2,h/2,0)],[],[(0,1,2,3)])
    mesh.update()
    uv=mesh.uv_layers.new(name='UVMap')
    for i,co in enumerate([(0,0),(1,0),(1,1),(0,1)]): uv.data[i].uv=co
    o=bpy.data.objects.new(name,mesh); col.objects.link(o)
    o.data.materials.append(m); o.location.z=z
    return o

textured_plane('SITE_satellite_z16', os.path.join(OUT,'satellite_z16.jpg'),
               1264*RES16, 625*RES16, -0.3, site_col)
textured_plane('SITE_satellite_z17', os.path.join(OUT,'satellite_z17.jpg'),
               1264*RES17, 625*RES17, -0.15, site_col)

# ---------- helpers ----------
def empty(name,col):
    e=bpy.data.objects.new(name,None); col.objects.link(e); return e

def add_box(name,loc,dims,material,col,parent=None,rot=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc,rotation=(0,0,rot))
    o=bpy.context.object; o.name=name; o.scale=dims; o.data.materials.append(material)
    for c in list(o.users_collection): c.objects.unlink(o)
    col.objects.link(o)
    if parent: o.parent=parent
    return o

def add_cyl(name,loc,r,d,material,col,vertices=12,parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=d,location=loc)
    o=bpy.context.object; o.name=name; o.data.materials.append(material)
    for c in list(o.users_collection): c.objects.unlink(o)
    col.objects.link(o)
    if parent: o.parent=parent
    return o

def add_cone(name,loc,r,d,material,col,vertices=6,parent=None):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=r,radius2=0,depth=d,location=loc)
    o=bpy.context.object; o.name=name; o.data.materials.append(material)
    for c in list(o.users_collection): c.objects.unlink(o)
    col.objects.link(o)
    if parent: o.parent=parent
    return o

def add_ring(name,cx,cy,r_in,r_out,z,material,col,parent=None,segments=48):
    verts=[]
    for i in range(segments):
        a=2*math.pi*i/segments
        verts.append((cx+r_in*math.cos(a),cy+r_in*math.sin(a),z))
        verts.append((cx+r_out*math.cos(a),cy+r_out*math.sin(a),z))
    faces=[]
    for i in range(segments):
        j=(i+1)%segments
        faces.append((2*i,2*i+1,2*j+1,2*j))
    mesh=bpy.data.meshes.new(name+'_mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new(name,mesh); col.objects.link(o); o.data.materials.append(material)
    if parent: o.parent=parent
    return o

def add_circ(name,cx,cy,r,z,material,col,parent=None,segments=48):
    verts=[(cx+r*math.cos(2*math.pi*i/segments),cy+r*math.sin(2*math.pi*i/segments),z) for i in range(segments)]
    mesh=bpy.data.meshes.new(name+'_mesh'); mesh.from_pydata(verts,[],[tuple(range(segments))]); mesh.update()
    o=bpy.data.objects.new(name,mesh); col.objects.link(o); o.data.materials.append(material)
    if parent: o.parent=parent
    return o

def add_polygon(name,pts,z,material,col,parent=None):
    n=len(pts)
    verts=[(x,y,z) for x,y in pts]
    mesh=bpy.data.meshes.new(name+'_mesh'); mesh.from_pydata(verts,[],[(tuple(range(n)))]); mesh.update()
    o=bpy.data.objects.new(name,mesh); col.objects.link(o); o.data.materials.append(material)
    if parent: o.parent=parent
    return o

def add_prism(name, pts, height, material, col, z0=0, uv_scale=24.0, v_repeat=None):
    """Prism with per-face UVs so facade textures tile correctly on each wall.
    Each facade texture image holds 2 floors, so v_repeat should be floors/2."""
    n=len(pts)
    if v_repeat is None: v_repeat=max(1,height/12)
    verts=[(x,y,z0) for x,y in pts]+[(x,y,z0+height) for x,y in pts]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    for i in range(n):
        j=(i+1)%n
        faces.append((i,j,j+n,i+n))
    mesh=bpy.data.meshes.new(name+'_mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    # UV: two caps (0..1) + side faces tiled by real-world size
    uv=mesh.uv_layers.new(name='UVMap')
    for poly in mesh.polygons:
        if poly.index<2:
            for li in poly.loop_indices:
                v=mesh.vertices[mesh.loops[li].vertex_index].co
                uv.data[li].uv=((v.x/uv_scale)%1,(v.y/uv_scale)%1)
        else:
            i=poly.index-2
            x1,y1=pts[i]; x2,y2=pts[(i+1)%n]
            edge=math.hypot(x2-x1,y2-y1)
            u0=0; u1=edge/uv_scale
            for li in poly.loop_indices:
                v=mesh.vertices[mesh.loops[li].vertex_index].co
                along=math.hypot(v.x-x1,v.y-y1)
                vv=(v.z-z0)/height*v_repeat
                uv.data[li].uv=(u0 if along<1e-4 else u1, vv)
    o=bpy.data.objects.new(name,mesh); col.objects.link(o); o.data.materials.append(material)
    return o

def add_prism_ring(name, outer, inner, height, material, col, z0=0, v_repeat=3):
    n=len(outer)
    verts=[(x,y,z0) for x,y in outer]+[(x,y,z0+height) for x,y in outer]+\
          [(x,y,z0) for x,y in inner]+[(x,y,z0+height) for x,y in inner]
    faces=[]
    for i in range(n):
        j=(i+1)%n
        faces.append((n+i,n+j,3*n+j,3*n+i))       # top ring
        faces.append((i,2*n+i,2*n+j,j))           # bottom ring
        faces.append((i,j,n+j,n+i))               # outer wall
        faces.append((2*n+j,2*n+i,3*n+i,3*n+j))   # inner wall
    mesh=bpy.data.meshes.new(name+'_mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    uv=mesh.uv_layers.new(name='UVMap')
    for poly in mesh.polygons:
        i=poly.index//4; j=(i+1)%n; typ=poly.index%4
        ring=outer if typ==2 else inner
        x1,y1=ring[i]; x2,y2=ring[j]
        edge=math.hypot(x2-x1,y2-y1)
        for li in poly.loop_indices:
            v=mesh.vertices[mesh.loops[li].vertex_index].co
            if typ in (0,1):
                uv.data[li].uv=((v.x/24)%1,(v.y/24)%1)
            else:
                along=math.hypot(v.x-x1,v.y-y1)
                uv.data[li].uv=((along/24), (v.z-z0)/height*v_repeat)
    o=bpy.data.objects.new(name,mesh); col.objects.link(o); o.data.materials.append(material)
    return o

def add_frustum(name,cx,cy,bx,by,tx,ty,z0,z1,material,col):
    verts=[(cx-bx,cy-by,z0),(cx+bx,cy-by,z0),(cx+bx,cy+by,z0),(cx-bx,cy+by,z0),
           (cx-tx,cy-ty,z1),(cx+tx,cy-ty,z1),(cx+tx,cy+ty,z1),(cx-tx,cy+ty,z1)]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    mesh=bpy.data.meshes.new(name+'_mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new(name,mesh); col.objects.link(o); o.data.materials.append(material)
    return o

def add_roof_details(name, pts, b, col, parent):
    """女儿墙 + 屋顶机房/设备，让平顶建筑不再像光滑盒子。"""
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    cx,cy=sum(xs)/len(xs),sum(ys)/len(ys)
    bx,by=(max(xs)-min(xs))/2,(max(ys)-min(ys))/2
    hz=b['height']
    # 女儿墙（沿屋顶边缘一圈矮墙）
    for i in range(len(pts)):
        x1,y1=pts[i]; x2,y2=pts[(i+1)%len(pts)]
        mx,my=(x1+x2)/2,(y1+y2)/2
        L=math.hypot(x2-x1,y2-y1); ang=math.atan2(y2-y1,x2-x1)
        add_box('B_%s_parapet_%d'%(name,i),(mx,my,hz+1.2),(L,0.7,2.4),M['trim'],col,parent,ang)
    # 屋顶机房 / 楼梯间（random but deterministic by id）
    h=sum(ord(c) for c in name)*17
    if b['kind']!='dorm':
        mx=cx+(h%7-3)*bx*0.18; my=cy+((h//7)%5-2)*by*0.18
        add_box('B_%s_mpf'%name,(mx,my,hz+3.2),(min(bx*0.5,14),min(by*0.4,12),6.4),M['wall'],col,parent)
        add_prism('B_%s_mpf_roof'%name,
                  [(mx-8,my-7),(mx+8,my-7),(mx+8,my+7),(mx-8,my+7)],
                  0.8,M['roof'],col,z0=hz+6.4).parent=parent
        # 空调外机 / 设备块
        for k in range(3):
            ax=cx-bx*0.6+k*bx*0.5; ay=cy+by*0.55
            add_box('B_%s_hvac_%d'%(name,k),(ax,ay,hz+1.6),(3.4,2.6,2.2),M['counter'],col,parent)

def add_facade_edges(name, pts, height, col, parent, floors=6):
    """仅保留细的水平层间线脚（窗户由立面纹理提供）。"""
    step=height/max(1,floors)
    for i in range(len(pts)):
        x1,y1=pts[i]; x2,y2=pts[(i+1)%len(pts)]
        cx,cy=(x1+x2)/2,(y1+y2)/2
        L=math.hypot(x2-x1,y2-y1); ang=math.atan2(y2-y1,x2-x1)
        for f in range(1,floors):
            add_box('B_%s_slab_%d_%d'%(name,i,f),(cx,cy,f*step),(L,0.35,0.28),M['trim'],col,parent,ang)

# ---------- building definitions (pixel coords on z17 image) ----------
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

INTERIOR_IDS=set(b['id'] for b in BUILDINGS if b['kind']!='dorm') | \
             set(b['id'] for b in BUILDINGS if b['kind']=='dorm' and b['id'].endswith('_0'))

# ---------- build exteriors ----------
for b in BUILDINGS:
    name=b['id']; pts=b['pts']
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    cx,cy=sum(xs)/len(xs),sum(ys)/len(ys)
    b['x'],b['y']=cx,cy
    parent=empty('GRP_'+name,build_col)
    fmat=T.get(b['kind'],T['classroom'])
    if 'inner_px' in b:
        inner=P(*b['inner_px'])
        body=add_prism_ring('B_%s_body'%name,pts,inner,b['height'],fmat,build_col)
        roof=add_prism_ring('B_%s_roof'%name,pts,inner,1.6,M['roof'],build_col,z0=b['height'])
        body.parent=parent; roof.parent=parent
        add_facade_edges(name,pts,b['height'],build_col,parent,b['floors'])
        add_facade_edges(name,inner,b['height'],build_col,parent,b['floors'])
        add_roof_details(name,pts,b,build_col,parent)
    elif name=='library':
        # 图书馆真实形态（据官网航拍）：矩形塔楼 + 顶部巨大方形挑檐平顶
        body=add_prism('B_library_body',pts,b['height'],T['library'],build_col,
                       v_repeat=b['floors']/2)
        body.parent=parent
        bx,by=(max(xs)-min(xs))/2,(max(ys)-min(ys))/2
        # 顶部大挑檐：四周外扩的矩形板，如同一个大屋盖扣在塔楼上
        e=1.20  # 挑檐外扩系数（真实照片外扩明显）
        eave=[(cx+(x-cx)*e, cy+(y-cy)*e) for x,y in pts]
        add_prism('B_library_eaves',eave,3.2,M['trim'],build_col,z0=b['height']-1).parent=parent
        # 挑檐下方一圈深灰玻璃带（真实照片中挑檐下有深色格栅层）
        eave2=[(cx+(x-cx)*(e-0.02), cy+(y-cy)*(e-0.02)) for x,y in pts]
        add_prism('B_library_eaveglass',eave2,2.4,M['glass2'],build_col,z0=b['height']-4.2).parent=parent
        # 挑檐边缘的格栅竖线（真实照片中屋盖边缘的密肋）
        for i in range(len(eave)):
            x1,y1=eave[i]; x2,y2=eave[(i+1)%len(eave)]
            for k in range(1,7):
                t=k/7.0
                gx=x1+(x2-x1)*t; gy=y1+(y2-y1)*t
                add_box('B_library_eavefin_%d_%d'%(i,k),(gx,gy,b['height']-0.2),(1.2,1.2,3.4),M['trim'],build_col,parent)
        # 平屋顶面 + 屋顶设备
        add_prism('B_library_roof',pts,1.2,M['roof'],build_col,z0=b['height']+2.2).parent=parent
        # 主入口门廊（南侧）
        ey=min(ys)
        add_box('B_library_portico',(cx,ey-3,6),(bx*0.55,6,11),M['trim'],build_col,parent)
        for k in (-1,0,1):
            add_cyl('B_library_col_%d'%k,(cx+k*bx*0.18,ey-5.5,6.5),0.6,11,M['trim'],build_col,parent=parent)
        add_roof_details(name,pts,b,build_col,parent)
    else:
        body=add_prism('B_%s_body'%name,pts,b['height'],fmat,build_col,
                       v_repeat=b['floors']/2)
        body.parent=parent
        if b['roof']=='blue':
            add_prism('B_%s_roof'%name,pts,2.2,M['roof_blue'],build_col,z0=b['height']).parent=parent
        elif b['kind']=='dorm':
            # 宿舍坡屋顶（红瓦）——卫星影像中宿舍区明显红顶
            bx,by=(max(xs)-min(xs))/2,(max(ys)-min(ys))/2
            add_frustum('B_%s_roof'%name,cx,cy,bx,by,bx*0.82,by*0.8,
                        b['height'],b['height']+3.5,M['roof_red'],build_col).parent=parent
        else:
            add_prism('B_%s_roof'%name,pts,1.6,M['roof'],build_col,z0=b['height']).parent=parent
        add_roof_details(name,pts,b,build_col,parent)

# ---------- landscape: library plaza, lakes, central axis ----------
site_parent=empty('GRP_landscape',site_col)
lx,ly=px_to_xy(570,455)
# 环形广场（卫星影像中图书馆四周浅色铺装）
add_ring('SITE_lib_plaza_outer',lx,ly,52,84,0.35,M['plaza'],site_col,site_parent)
add_ring('SITE_lib_plaza_inner',lx,ly,45,52,0.4,M['trim'],site_col,site_parent)
# 南侧中轴步道：从广场向南延伸
ax0=px_to_xy(566,492); ax1=px_to_xy(566,610)
add_box('SITE_axis_walk',((ax0[0]+ax1[0])/2,(ax0[1]+ax1[1])/2,0.32),
        (10,abs(ax0[1]-ax1[1]),0.12),M['plaza'],site_col,site_parent)
# 北侧中轴 connections
axn=px_to_xy(566,300)
add_box('SITE_axis_north',((ax0[0]+axn[0])/2,(ax0[1]+axn[1])/2,0.3),
        (8,abs(ax0[1]-axn[1]),0.1),M['plaza'],site_col,site_parent)
# 明湖（图书馆西侧水面）与鉴湖（东侧水面）
lakes=[
 ('minghu',[(520,412),(536,404),(548,412),(545,470),(532,486),(518,470)]),
 ('jianhu',[(615,414),(665,410),(690,436),(682,485),(650,498),(622,478)]),
]
for lname,pp in lakes:
    pts=P(*pp)
    add_polygon('SITE_lake_'+lname,pts,0.22,M['water'],site_col,site_parent)
# 湖岸绿化带
add_ring('SITE_lake_bank',lx,ly,84,90,0.2,M['green'],site_col,site_parent)

# ---------- v5: sports fields, roads, street lights, cars ----------
site2=empty('GRP_facilities',site_col)
def P2(px,py): return px_to_xy(px,py)
# 西运动场（卫星图左侧红色跑道椭圆）+ 东运动场（右上）
def sports_field(name, px, py, rw, rh, rot=0):
    fx,fy=P2(px,py)
    par=empty('GRP_'+name,site_col); par.parent=site2
    # running track as a ring, green infield
    add_ring(name+'_track',fx,fy,rh*0.86,rh,0.25,M['track'],site_col,par,segments=40)
    add_circ(name+'_field',fx,fy,rh*0.84,0.28,M['court'],site_col,par,segments=40)
    # football pitch marking
    add_box(name+'_pitch',(fx,fy,0.3),(rw*0.55,rh*1.3,0.05),M['court'],site_col,par)
    add_box(name+'_midline',(fx,fy,0.34),(rw*0.55,0.3,0.03),M['courtline'],site_col,par)
# (west field near x≈120,y≈150; east field near x≈900,y≈120)
sports_field('field_west',135,160,26,44)
sports_field('field_east',955,120,24,40)

# 校园主要道路（连接中轴与东西）—— 卫星影像中的浅色路网
road_segments=[
 (566,300,566,545),   # central axis already walkway, widen as road
 (160,320,566,320),   # mid west-east
 (566,200,960,200),   # north east-west
 (300,320,300,560),   # west vertical
 (760,200,760,520),   # east vertical
]
for i,(x1,y1,x2,y2) in enumerate(road_segments):
    a=P2(x1,y1); b=P2(x2,y2)
    L=math.hypot(b[0]-a[0],b[1]-a[1]); ang=math.atan2(b[1]-a[1],b[0]-a[0])
    add_box('SITE_road_%d'%i,((a[0]+b[0])/2,(a[1]+b[1])/2,0.18),(L,9,0.1),M['road'],site_col,site2,ang)
    # center dashed line
    for k in range(int(L/24)):
        t=(k+0.5)/max(1,int(L/24))
        px=a[0]+(b[0]-a[0])*t; py=a[1]+(b[1]-a[1])*t
        add_box('SITE_roadline_%d_%d'%(i,k),(px,py,0.24),(4,0.4,0.05),M['courtline'],site_col,site2,ang)

# 路灯（沿中轴与主要道路）
for i in range(10):
    py=300+i*26
    lx,ly=P2(566,py)
    add_cyl('SITE_lamp_pole_%d'%i,(lx+7,ly,3.2),0.18,6.4,M['lamp'],site_col,vertices=8,parent=site2)
    add_box('SITE_lamp_head_%d'%i,(lx+7,ly,6.4),(1.6,0.6,0.3),M['light'],site_col,site2)

# 旗杆与旗台（图书馆南侧广场）
fx,fy=P2(566,505)
add_cyl('SITE_flagbase',(fx,fy,0.6),3,1.2,M['stone'],site_col,vertices=16,parent=site2)
add_cyl('SITE_flagpole',(fx,fy,9),0.16,18,M['rail'],site_col,vertices=10,parent=site2)
add_box('SITE_flag',(fx+1.6,fy,16),(3.2,0.1,2.0),M['flag'],site_col,site2)

# 少量车辆点缀在停车场（卫星图图书馆西南有停车场）
random.seed(21)
for i in range(8):
    px=random.uniform(430,500); py=random.uniform(500,560)
    vx,vy=P2(px,py)
    r=random.uniform(0,math.pi)
    add_box('SITE_car_%d'%i,(vx,vy,0.7),(4.4,2.0,1.5),M['car'],site_col,site2,r)
    add_box('SITE_car_top_%d'%i,(vx,vy,1.6),(2.4,1.8,0.7),M['glass'],site_col,site2,r)

# gazebo by the lake (from real campus photo: blue roof, white columns)
gx,gy=px_to_xy(600,300)
gparent=empty('GRP_gazebo',build_col)
add_cyl('B_gazebo_floor',(gx,gy,0.4),8,0.8,M['stone'],build_col,vertices=8,parent=gparent)
for i in range(8):
    a=2*math.pi*i/8
    add_cyl('B_gazebo_col_%d'%i,(gx+6*math.cos(a),gy+6*math.sin(a),3.2),0.45,5.6,
            M['roof'],build_col,vertices=8,parent=gparent)
add_cone('B_gazebo_roof',(gx,gy,8.0),11,3.2,M['roof_blue'],build_col,vertices=8,parent=gparent)

# a few trees along the central axis (satellite already contains vegetation)
import random
random.seed(88)
crown_mesh=None
bpy.ops.mesh.primitive_cone_add(vertices=6,radius1=4,radius2=0,depth=9)
tmp=bpy.context.object; crown_mesh=tmp.data; crown_mesh.materials.append(M['tree'])
bpy.data.objects.remove(tmp,do_unlink=True)
bpy.ops.mesh.primitive_cylinder_add(vertices=6,radius=.7,depth=3)
tmp=bpy.context.object; trunk_mesh=tmp.data; trunk_mesh.materials.append(M['trunk'])
bpy.data.objects.remove(tmp,do_unlink=True)
# 大规模绿化：沿中轴、湖岸、宿舍区、建筑周边成片种植（真实校园绿树成荫）
tree_spots=[]
def scatter(cx,cy,n,rx,ry):
    for _ in range(n):
        tree_spots.append((cx+random.uniform(-rx,rx), cy+random.uniform(-ry,ry)))
# 中轴两侧行道树
for py in range(150,560,14):
    for px in (515,525,590,600):
        tree_spots.append((px+random.uniform(-5,5), py+random.uniform(-5,5)))
# 图书馆周边与湖岸
scatter(430,470,55,80,60); scatter(700,470,40,60,50)
scatter(380,300,50,90,80); scatter(560,300,40,70,50)
scatter(700,220,45,90,70); scatter(300,180,40,80,60)
# 宿舍区之间
for ry in [195,235,275,315,355]:
    for px in range(150,470,12):
        if 295<px<315: continue
        tree_spots.append((px+random.uniform(-3,3), ry+random.uniform(-4,9)))
# 东侧与南部零散绿化
for _ in range(90):
    tree_spots.append((random.uniform(650,960), random.uniform(180,560)))
for i,(px,py) in enumerate(tree_spots[:600]):
    x,y=px_to_xy(px,py)
    sc=random.uniform(.75,1.25)
    c=bpy.data.objects.new('SITE_tree_%03d'%i,crown_mesh); site_col.objects.link(c)
    c.location=(x,y,6.5*sc); c.scale=(sc,sc,sc)
    t=bpy.data.objects.new('SITE_trunk_%03d'%i,trunk_mesh); site_col.objects.link(t)
    t.location=(x,y,1.4*sc); t.scale=(sc,sc,sc)
print('trees planted:',len(tree_spots[:600]))

# ---------- interiors (v5: full, room-divided, furnished, per-floor) ----------
class FloorBuilder:
    """Accumulate box/cylinder geometry into ONE mesh per floor with material slots.
    Avoids thousands of slow bpy.ops calls."""
    def __init__(self):
        self.verts=[]
        self.faces=[]      # (vertex_index_tuple, material_index)
        self.slots=[]
        self.slotmap={}
    def _slot(self, mat):
        k=mat.name
        if k not in self.slotmap:
            self.slotmap[k]=len(self.slots); self.slots.append(mat)
        return self.slotmap[k]
    def box(self, loc, dims, mat, rot=0):
        cx,cy,cz=loc; sx,sy,sz=dims
        hx,hy,hz=sx/2,sy/2,sz/2
        ca,sa=math.cos(rot),math.sin(rot)
        base=len(self.verts)
        for x,y,z in [(-hx,-hy,-hz),(hx,-hy,-hz),(hx,hy,-hz),(-hx,hy,-hz),
                      (-hx,-hy,hz),(hx,-hy,hz),(hx,hy,hz),(-hx,hy,hz)]:
            self.verts.append((cx+x*ca-y*sa, cy+x*sa+y*ca, cz+z))
        s=self._slot(mat)
        for f in [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]:
            self.faces.append((tuple(base+i for i in f), s))
    def cyl(self, loc, r, h, mat, verts=10):
        cx,cy,cz=loc; base=len(self.verts); n=verts
        for dz in (-h/2,h/2):
            for i in range(n):
                a=2*math.pi*i/n
                self.verts.append((cx+r*math.cos(a), cy+r*math.sin(a), cz+dz))
        s=self._slot(mat)
        for i in range(n):
            j=(i+1)%n
            self.faces.append(((base+i,base+j,base+n+j,base+n+i), s))
        self.faces.append((tuple(base+i for i in range(n-1,-1,-1)), s))
        self.faces.append((tuple(base+n+i for i in range(n)), s))
    def commit(self, name, col, parent):
        if not self.verts: return None
        mesh=bpy.data.meshes.new(name+'_m')
        mesh.from_pydata(self.verts, [], [f for f,_ in self.faces])
        mesh.update()
        for m in self.slots: mesh.materials.append(m)
        for poly,(f,mi) in zip(mesh.polygons,self.faces):
            poly.material_index=mi
        o=bpy.data.objects.new(name, mesh); col.objects.link(o); o.parent=parent
        return o

def build_interior(b):
    name=b['id']; pts=b['pts']; kind=b['kind']
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    cx,cy=b['x'],b['y']
    w=(max(xs)-min(xs))*0.86; d=(max(ys)-min(ys))*0.86
    floors=b['floors']; fh=4.0
    root=empty('INT_'+name, interior_col)
    for lv in range(floors):
        z=lv*fh
        fl = empty('FL_%s_%d'%(name,lv), interior_col); fl.parent=root
        fb=FloorBuilder()
        def B(n,loc,dims,m,parent=None): fb.box(loc,dims,m)
        def C(n,loc,r,dep,m,verts=10,parent=None): fb.cyl(loc,r,dep,m,verts)

        # floor slab only (NO ceiling - so furniture below is visible from above in cutaway)
        B('slab',(cx,cy,z),(w,d,0.3),M['floor'])
        # low cutaway walls (1.3m) so interior is visible from a 3/4 view
        for s,dy in [('N',d/2),('S',-d/2)]:
            B('wall%s'%s,(cx,cy+dy,z+0.65),(w,0.35,1.3),M['wallin'])
        for s,dx in [('W',-w/2),('E',w/2)]:
            B('wall%s'%s,(cx+dx,cy,z+0.65),(0.35,d,1.3),M['wallin'])
        # stairs + service core (east side)
        sx=cx+w*0.40
        B('stair',(sx,cy,z+1.0),(5,d*0.30,2.0),M['stair'])
        for st in range(5):
            B('stairstep_%d'%st,(sx-2+st,cy-d*0.08+st*0.1,z+0.3+st*0.35),(1,d*0.28,0.3),M['trim'])
        B('core',(cx+w*0.40,cy+d*0.32,z+fh/2),(5,4,fh-0.4),M['wallin'])

        if kind=='library':
            if lv==0:
                B('infodesk',(cx,cy+d*0.30,z+1.3),(w*0.30,2.2,2.6),M['wood'])
                for k in range(3):
                    C('lamp%d'%k,(cx-w*0.2+k*w*0.2,cy,z+2.2),0.5,0.25,M['light'])
            for r in range(2):
                for c in range(3):
                    bx=cx-w*0.34+c*w*0.20; by=cy-d*0.30+r*d*0.34
                    B('shelf_%d_%d'%(r,c),(bx,by,z+1.7),(0.9,d*0.22,3.4),M['shelf'])
                    B('books_%d_%d'%(r,c),(bx+0.5,by,z+1.7),(0.25,d*0.20,3.0),M['book'])
            for t in range(3):
                tx=cx-w*0.28+t*w*0.26; ty=cy+d*0.12
                B('rtable_%d'%t,(tx,ty,z+0.9),(6,2.2,0.18),M['desk'])
                for q in (-1,1):
                    B('rchair_%d_%d'%(t,q),(tx,ty+q*1.6,z+0.55),(1.4,1.2,1.1),M['chair'])
            B('atrium_rail',(cx,cy,z+0.75),(w*0.30,0.25,1.5),M['rail'])
        elif kind=='gym':
            B('court',(cx,cy,z+0.25),(w*0.72,d*0.62,0.1),M['court'])
            for kx in range(3):
                B('courtline_x%d'%kx,(cx-w*0.36+kx*w*0.24,cy,z+0.32),(0.25,d*0.62,0.05),M['courtline'])
            B('courtline_mid',(cx,cy,z+0.32),(w*0.72,0.25,0.05),M['courtline'])
            for s in (-1,1):
                B('bleacher_%d'%s,(cx,cy+s*d*0.36,z+0.9),(w*0.72,3.2,1.8),M['seat'])
                for r in range(3):
                    B('bleachstep_%d_%d'%(s,r),(cx,cy+s*d*0.34+s*r*0.6,z+0.5+r*0.5),(w*0.72,0.6,0.5),M['stair'])
            for k in range(4):
                C('hoopole_%d'%k,(cx-w*0.2+k*w*0.13,cy-d*0.28,z+1.6),0.12,3.2,M['rail'])
        elif kind=='canteen':
            for c in range(3):
                B('counter_%d'%c,(cx-w*0.28+c*w*0.28,cy-d*0.32,z+1.1),(w*0.22,1.8,2.2),M['counter'])
                B('food_%d'%c,(cx-w*0.28+c*w*0.28,cy-d*0.32,z+2.3),(w*0.20,1.6,0.3),M['wood'])
            for r in range(2):
                for c in range(4):
                    tx=cx-w*0.32+c*w*0.21; ty=cy-d*0.05+r*d*0.28
                    C('dtable_%d_%d'%(r,c),(tx,ty,z+0.9),1.7,0.16,M['wood'],verts=10)
                    for q in (-1,1):
                        B('dstool_%d_%d_%d'%(r,c,q),(tx+q*2.2,ty,z+0.55),(1.1,1.1,1.1),M['chair'])
        elif kind=='dorm':
            nrooms=4
            for rm in range(nrooms):
                rx=cx-w*0.36+rm*w*0.24
                B('rpart_%d'%rm,(rx+w*0.12,cy,z+fh/2),(0.25,d*0.85,fh-0.4),M['wallin'])
                for bb in range(2):
                    B('bed_%d_%d'%(rm,bb),(rx,cy-d*0.18+bb*d*0.30,z+0.7+bb*0.9),(3.6,2.0,0.9),M['bed'])
                B('desk_%d'%rm,(rx,cy+d*0.28,z+0.9),(3.4,1.5,0.18),M['desk'])
                B('chair_%d'%rm,(rx,cy+d*0.20,z+0.55),(1.2,1.2,1.1),M['chair'])
                B('wardrobe_%d'%rm,(rx+w*0.08,cy+d*0.34,z+1.2),(1.2,1.0,2.4),M['wardrobe'])
            B('bathroom',(cx+w*0.40,cy-d*0.28,z+fh/2),(4,d*0.22,fh-0.5),M['toilet'])
            for k in range(2):
                C('wash_%d'%k,(cx+w*0.40-1+k*2,cy+d*0.30,z+0.7),0.5,1.4,M['toilet'])
        elif kind=='office':
            for rm in range(3):
                rx=cx-w*0.30+rm*w*0.26
                B('opart_%d'%rm,(rx+w*0.13,cy,z+fh/2),(0.25,d*0.80,fh-0.4),M['glasswall'])
                for dk in range(2):
                    B('odesk_%d_%d'%(rm,dk),(rx,cy-d*0.15+dk*d*0.32,z+0.85),(3.2,1.6,0.16),M['desk'])
                    B('monitor_%d_%d'%(rm,dk),(rx,cy-d*0.15+dk*d*0.32,z+1.3),(1.4,0.12,0.9),M['computer'])
                    B('ochair_%d_%d'%(rm,dk),(rx,cy-d*0.15+dk*d*0.32+1.2,z+0.55),(1.2,1.2,1.0),M['chair'])
            B('meeting',(cx+w*0.32,cy,z+0.9),(w*0.18,d*0.30,0.18),M['desk'])
        else:  # classroom / lab
            is_lab=(kind=='lab')
            B('blackboard',(cx,cy-d*0.42,z+1.8),(w*0.55,0.15,2.6),M['blackboard'])
            B('teacher',(cx,cy-d*0.32,z+0.9),(w*0.20,1.4,0.18),M['teacherdesk'])
            for r in range(3):
                for c in range(5):
                    dx=cx-w*0.36+c*w*0.18; dy=cy-d*0.10+r*d*0.20
                    if is_lab:
                        B('labbench_%d_%d'%(r,c),(dx,dy,z+0.95),(3.0,1.4,0.20),M['labbench'])
                        B('sink_%d_%d'%(r,c),(dx,dy-0.4,z+1.08),(0.8,0.5,0.1),M['counter'])
                    else:
                        B('desk_%d_%d'%(r,c),(dx,dy,z+0.85),(2.6,1.3,0.16),M['desk'])
                        B('chair_%d_%d'%(r,c),(dx,dy+1.0,z+0.5),(1.1,1.0,1.0),M['chair'])
            for k in range(3):
                B('light_%d'%k,(cx-w*0.25+k*w*0.25,cy,z+fh-0.35),(3.2,0.8,0.12),M['light'])

        fb.commit('IN_%s_L%d_all'%(name,lv), interior_col, fl)
    return root

for b in BUILDINGS:
    if b['id'] in INTERIOR_IDS: build_interior(b)

# ---------- camera / save / export ----------
bpy.ops.object.camera_add(location=(-500,-650,520),rotation=(math.radians(55),0,math.radians(-38)))
scene.camera=bpy.context.object
world=bpy.data.worlds.new('W'); scene.world=world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.7,.8,.9,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.8
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'HUEL_Zhengdong_Campus.blend'))

def export_sel(path,pred):
    bpy.ops.object.select_all(action='DESELECT')
    for o in scene.objects:
        if pred(o.name): o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=path,export_format='GLB',use_selection=True,
        export_apply=False,export_yup=True,export_materials='EXPORT',export_extras=True,
        export_cameras=False,export_lights=False,export_normals=True,export_texcoords=True)

export_sel(os.path.join(OUT,'campus_exterior.glb'),
           lambda n: n.startswith(('B_','SITE_','GRP_')))
export_sel(os.path.join(OUT,'campus_interiors.glb'),
           lambda n: n.startswith(('INT_','FL_','IN_')))

# ---------- metadata ----------
meta=[]
for b in BUILDINGS:
    lat,lon=xy_to_ll(b['x'],b['y'])
    meta.append(dict(id=b['id'],name=b['name'],kind=b['kind'],
        lat=round(lat,6),lon=round(lon,6),x=round(b['x'],2),y=round(b['y'],2),
        z=round(b['height']/2,2),height=b['height'],floors=b['floors'],
        floorH=4.0,
        desc=b['desc'],interior=b['interior'],hasInterior=b['id'] in INTERIOR_IDS))
with open(os.path.join(WEB,'buildings.json'),'w',encoding='utf-8') as f:
    json.dump(dict(campus=dict(name='河南财经政法大学（郑东校区）',lat0=LAT0,lon0=LON0,
        address='河南省郑州市金水东路180号',
        note='建筑轮廓依据高德最新卫星影像数字化，辅以学校官网、官方平面图与微信公众号实景照片校准；建筑高度与室内依据公开资料示意，非测绘成果。'),
        buildings=meta),f,ensure_ascii=False,indent=2)
print('DONE',len(BUILDINGS),'RES',RES17,RES16)
