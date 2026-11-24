# -*- coding: utf-8 -*-
"""Rebuild HUEL Zhengdong campus from real satellite imagery (v2)."""
import bpy, json, math, os

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
}

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

def add_prism(name, pts, height, material, col, z0=0):
    n=len(pts)
    verts=[(x,y,z0) for x,y in pts]+[(x,y,z0+height) for x,y in pts]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
    for i in range(n):
        j=(i+1)%n
        faces.append((i,j,j+n,i+n))
    mesh=bpy.data.meshes.new(name+'_mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new(name,mesh); col.objects.link(o); o.data.materials.append(material)
    return o

def add_prism_ring(name, outer, inner, height, material, col, z0=0):
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
    o=bpy.data.objects.new(name,mesh); col.objects.link(o); o.data.materials.append(material)
    return o

def add_frustum(name,cx,cy,bx,by,tx,ty,z0,z1,material,col):
    verts=[(cx-bx,cy-by,z0),(cx+bx,cy-by,z0),(cx+bx,cy+by,z0),(cx-bx,cy+by,z0),
           (cx-tx,cy-ty,z1),(cx+tx,cy-ty,z1),(cx+tx,cy+ty,z1),(cx-tx,cy+ty,z1)]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    mesh=bpy.data.meshes.new(name+'_mesh'); mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new(name,mesh); col.objects.link(o); o.data.materials.append(material)
    return o

def add_facade_edges(name, pts, height, col, parent, floors=6):
    step = height/max(1,floors)
    for i in range(len(pts)):
        x1,y1=pts[i]; x2,y2=pts[(i+1)%len(pts)]
        cx,cy=(x1+x2)/2,(y1+y2)/2
        L=math.hypot(x2-x1,y2-y1)
        ang=math.atan2(y2-y1,x2-x1)
        dx,dy=-math.sin(ang)*0.8, math.cos(ang)*0.8
        for f in range(1,floors):
            z=f*step
            add_box('B_%s_band_%d_%d'%(name,i,f),(cx,cy,z),(L,1.5,0.9),M['band'],col,parent,ang)
            add_box('B_%s_glass_%d_%d'%(name,i,f),(cx+dx,cy+dy,z+step*0.42),(L*0.94,0.5,step*0.5),M['glass'],col,parent,ang)

# ---------- building definitions (pixel coords on z17 image) ----------
def P(*coords): return [px_to_xy(*p) for p in coords]

BUILDINGS=[]
def add_b(id,name,kind,pts_px,height,floors,desc,interior,roof='flat'):
    pts=P(*pts_px)
    BUILDINGS.append(dict(id=id,name=name,kind=kind,pts=pts,height=height,floors=floors,
                          desc=desc,interior=interior,roof=roof))

add_b('central','至善楼 · 文韬楼 · 文锦楼建筑群','classroom',
      [(555,60),(780,60),(800,110),(760,180),(610,180),(540,110)],
      26,6,
      '校园核心建筑群，呈半围合布局，中部为庭院；综合办公与主要教学功能集中于此。',
      '环形走廊连接各教学单元，内设多媒体教室、办公室、会议室与中庭共享空间。')
BUILDINGS[-1]['inner_px']=[(600,90),(740,90),(755,120),(725,150),(625,150),(585,120)]

add_b('library','图书馆','library',
      [(533,417),(607,417),(607,492),(533,492)],60,12,
      '校园中心地标与河南省高校自建体量最大的图书馆，建筑面积 4.76 万平方米，地上 12 层、高 60 米。外观矩形四望如一，倒梯形方形屋顶大悬挑如宝鼎，寓意鼎立中原；外墙为干挂花岗岩、铝板与玻璃幕墙，内设多层中空大厅与开敞学习空间。前方为圆形广场与中轴步道，明湖、鉴湖如双璧相依。',
      '一层为服务大厅与检索区；中庭贯通多层；二至十二层为开架书库、阅览区、自习区与研讨间，六层大厅为标志性中庭空间。',roof='ding')

add_b('bluehall','体育馆','gym',
      [(760,100),(815,105),(820,160),(765,165)],22,3,
      '位于东运动场西侧的蓝色屋顶场馆，承担室内球类与集会活动。',
      '室内球场、看台与器材室。',roof='blue')

add_b('eastgrid','知行楼 · 博文楼','lab',
      [(680,290),(790,295),(790,370),(680,365)],25,6,
      '综合实验与教学科研楼群，位于图书馆东侧。',
      '计算机实验室、专业实验室、教研室与研讨室。')

add_b('eastcourt1','崇法楼','classroom',
      [(880,290),(960,295),(960,370),(880,365)],24,6,
      '法学部综合楼，位于校园东部庭院式建筑组团。',
      '法学专业教室、模拟法庭与学术报告厅。')

add_b('eastcourt2','鼎新楼 · 建树楼','office',
      [(780,400),(880,405),(880,485),(780,480)],24,6,
      '大学生科创中心与校友捐建楼宇，庭院式布局。',
      '创新工坊、项目工作室、办公室与展示交流空间。')

add_b('southblock','南部教学与生活组团','classroom',
      [(520,545),(660,545),(660,612),(520,612)],22,5,
      '校区南部教学楼与配套组团。',
      '教室、实验室与学生服务空间。')

# dorm rows (visible long bars west of the axis)
for row,y in enumerate([205,245,285,325,365]):
    for seg,(x1,x2) in enumerate([(160,300),(310,460)]):
        add_b('dorm_%d_%d'%(row,seg),'%s苑%d号楼'%('静雅'[seg],row+1),'dorm',
              [(x1,y),(x2,y),(x2,y+17),(x1,y+17)],22,6,
              '学生公寓，四人间/六人间，每层设公共卫生间与浴室，配备空调、暖气、阳台与电脑桌。',
              '学生宿舍标准层：房间、公共卫生间、洗漱区与走廊。')

# small service buildings visible near library / dorms
add_b('canteen1','第一食堂','canteen',
      [(470,465),(520,465),(520,510),(470,510)],15,3,
      '位于教学楼与图书馆之间的食堂。',
      '一层基本餐厅，二层风味小吃与休闲就餐区。')
add_b('canteen2','第二食堂','canteen',
      [(420,330),(465,330),(465,370),(420,370)],15,3,
      '位于学生公寓附近的食堂。',
      '多层就餐大厅与风味窗口。')
add_b('canteen3','第三食堂','canteen',
      [(900,195),(950,195),(950,235),(900,235)],15,3,
      '位于综合运动场附近的食堂。',
      '自选餐厅与特色风味档口。')

INTERIOR_IDS={'central','library','eastgrid','dorm_0_0','bluehall','canteen1'}

# ---------- build exteriors ----------
for b in BUILDINGS:
    name=b['id']; pts=b['pts']
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    cx,cy=sum(xs)/len(xs),sum(ys)/len(ys)
    b['x'],b['y']=cx,cy
    parent=empty('GRP_'+name,build_col)
    if 'inner_px' in b:
        inner=P(*b['inner_px'])
        body=add_prism_ring('B_%s_body'%name,pts,inner,b['height'],M['wall'],build_col)
        roof=add_prism_ring('B_%s_roof'%name,pts,inner,1.6,M['roof'],build_col,z0=b['height'])
        body.parent=parent; roof.parent=parent
    elif name=='library':
        # 主体：12 层矩形体量，干挂花岗岩墙面 + 玻璃幕墙带
        body=add_prism('B_library_body',pts,b['height'],M['wall'],build_col)
        body.parent=parent
        # 倒梯形方形大悬挑屋顶（宝鼎造型）：下小上大
        bx,by=(max(xs)-min(xs))/2,(max(ys)-min(ys))/2
        add_frustum('B_library_ding',cx,cy,bx*0.92,by*0.92,bx*1.22,by*1.22,
                    b['height']-6,b['height']+6,M['trim'],build_col).parent=parent
        # 顶部檐口压边
        add_prism('B_library_crown',pts,1.4,M['roof'],build_col,z0=b['height']+6).parent=parent
        # 中心蓝色天窗（卫星影像中可见的蓝色方形采光顶）
        sw=10
        add_prism('B_library_skylight',[(cx-sw,cy-sw),(cx+sw,cy-sw),(cx+sw,cy+sw),(cx-sw,cy+sw)],
                  1.8,M['glass2'],build_col,z0=b['height']+7.2).parent=parent
        # 玻璃幕墙竖向分区（每层一圈，模拟干挂石材+玻璃带）
        add_facade_edges(name,pts,b['height'],build_col,parent,b['floors'])
        # 主入口门廊（南侧）
        ey=min(ys)
        add_box('B_library_portico',(cx,ey-3,6),(bx*0.9,6,12),M['trim'],build_col,parent)
        for k in (-1,0,1):
            add_cyl('B_library_col_%d'%k,(cx+k*bx*0.3,ey-5.5,6.5),0.7,13,M['trim'],build_col,parent=parent)
    else:
        body=add_prism('B_%s_body'%name,pts,b['height'],M['wall'],build_col)
        if b['roof']=='ding':
            bx,by=(max(xs)-min(xs))/2,(max(ys)-min(ys))/2
            add_frustum('B_%s_roof'%name,cx,cy,bx*.88,by*.88,bx*1.14,by*1.14,
                        b['height']-3,b['height']+8,M['roof'],build_col)
        elif b['roof']=='blue':
            add_prism('B_%s_roof'%name,pts,2.2,M['roof_blue'],build_col,z0=b['height'])
        else:
            add_prism('B_%s_roof'%name,pts,1.6,M['roof'],build_col,z0=b['height'])
    if name!='library':
        body.parent=parent
        add_facade_edges(name,pts,b['height'],build_col,parent,b['floors'])
    if 'inner_px' in b:
        add_facade_edges(name,inner,b['height'],build_col,parent,b['floors'])

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
for i in range(46):
    px=random.choice([530,585])+random.uniform(-18,18)
    py=random.uniform(200,540)
    x,y=px_to_xy(px,py)
    c=bpy.data.objects.new('SITE_tree_%02d'%i,crown_mesh); site_col.objects.link(c)
    c.location=(x,y,7); c.scale=(1,1,1)
    t=bpy.data.objects.new('SITE_trunk_%02d'%i,trunk_mesh); site_col.objects.link(t)
    t.location=(x,y,1.5)

# ---------- interiors ----------
def build_interior(b):
    name=b['id']; pts=b['pts']
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    cx,cy=b['x'],b['y']
    w=(max(xs)-min(xs))*.82; d=(max(ys)-min(ys))*.82
    root=empty('INT_'+name,interior_col)
    fh=4.2; levels=min(b['floors'],6 if name=='library' else 3)
    for lv in range(levels):
        z=.8+lv*fh
        if name=='library':
            # 图书馆：环形楼板 + 贯通中庭（中空大厅）
            outer=[(cx-w/2,cy-d/2),(cx+w/2,cy-d/2),(cx+w/2,cy+d/2),(cx-w/2,cy+d/2)]
            inner=[(cx-w*0.22,cy-d*0.22),(cx+w*0.22,cy-d*0.22),(cx+w*0.22,cy+d*0.22),(cx-w*0.22,cy+d*0.22)]
            add_prism_ring('IN_library_floor_%d'%lv,outer,inner,.35,M['floor'],interior_col,z0=z).parent=root
            add_box('IN_library_rail_%d'%lv,(cx,cy,z+0.55),(w*0.44,0.5,1.1),M['trim'],interior_col,root)
        else:
            add_box('IN_%s_floor_%d'%(name,lv),(cx,cy,z),(w,d,.35),M['floor'],interior_col,root)
        for s,dy in [('N',d/2),('S',-d/2)]:
            add_box('IN_%s_wall%s_%d'%(name,s,lv),(cx,cy+dy,z+fh/2),(w,.4,fh-.6),M['partition'],interior_col,root)
        for s,dx in [('W',-w/2),('E',w/2)]:
            add_box('IN_%s_wall%s_%d'%(name,s,lv),(cx+dx,cy,z+fh/2),(.4,d,fh-.6),M['partition'],interior_col,root)
        add_box('IN_%s_corridor_%d'%(name,lv),(cx,cy,z+.22),(w*.9,3,.05),M['stone'],interior_col,root)
        zt=z+.9; kind=b['kind']
        if kind=='library':
            for r in range(3):
                for c in range(4):
                    dx=cx-w*.32+c*w*.21; dy=cy-d*.28+r*d*.25
                    add_box('IN_%s_shelf_%d_%d_%d'%(name,lv,r,c),(dx,dy,zt+1.6),(.7,7,3.2),M['shelf'],interior_col,root)
                    add_box('IN_%s_book_%d_%d_%d'%(name,lv,r,c),(dx+.42,dy,zt+1.6),(.18,6.6,2.8),M['book'],interior_col,root)
        elif kind=='gym':
            add_box('IN_%s_court_%d'%(name,lv),(cx,cy,z+.3),(w*.7,d*.6,.1),M['court'],interior_col,root)
            for s in (-1,1):
                add_box('IN_%s_stand_%d_%d'%(name,lv,s),(cx,cy+s*d*.38,z+1),(w*.7,5,2),M['chair'],interior_col,root)
        elif kind=='canteen':
            add_box('IN_%s_counter_%d'%(name,lv),(cx,cy+d*.32,zt+1.1),(w*.7,2,2.2),M['counter'],interior_col,root)
            for r in range(2):
                for c in range(3):
                    add_cyl('IN_%s_table_%d_%d_%d'%(name,lv,r,c),(cx-w*.25+c*w*.25,cy-d*.2+r*d*.3,zt+.9),1.8,.18,M['wood'],interior_col,vertices=10,parent=root)
        else:
            for r in range(3):
                for c in range(4):
                    dx=cx-w*.3+c*w*.2; dy=cy-d*.25+r*d*.2
                    if kind=='dorm':
                        add_box('IN_%s_bed_%d_%d_%d'%(name,lv,r,c),(dx,dy,zt+.7),(3.4,2,1),M['bed'],interior_col,root)
                    else:
                        add_box('IN_%s_desk_%d_%d_%d'%(name,lv,r,c),(dx,dy,zt+.9),(3.2,1.8,.18),M['desk'],interior_col,root)
                        add_box('IN_%s_chair_%d_%d_%d'%(name,lv,r,c),(dx,dy-1.5,zt+.6),(1.4,1.2,1.2),M['chair'],interior_col,root)
        for k in range(3):
            add_box('IN_%s_light_%d_%d'%(name,lv,k),(cx-w*.25+k*w*.25,cy,z+fh-.5),(3,1,.15),M['light'],interior_col,root)

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
           lambda n: n.startswith(('INT_','IN_')))

# ---------- metadata ----------
meta=[]
for b in BUILDINGS:
    lat,lon=xy_to_ll(b['x'],b['y'])
    meta.append(dict(id=b['id'],name=b['name'],kind=b['kind'],
        lat=round(lat,6),lon=round(lon,6),x=round(b['x'],2),y=round(b['y'],2),
        z=round(b['height']/2,2),height=b['height'],floors=b['floors'],
        desc=b['desc'],interior=b['interior'],hasInterior=b['id'] in INTERIOR_IDS))
with open(os.path.join(WEB,'buildings.json'),'w',encoding='utf-8') as f:
    json.dump(dict(campus=dict(name='河南财经政法大学（郑东校区）',lat0=LAT0,lon0=LON0,
        address='河南省郑州市金水东路180号',
        note='建筑轮廓依据腾讯地图卫星影像数字化，建筑高度与外观依据公开资料示意，非测绘成果。'),
        buildings=meta),f,ensure_ascii=False,indent=2)
print('DONE',len(BUILDINGS),'RES',RES17,RES16)
