# -*- coding: utf-8 -*-
"""v9: 全校高清卫星图(2816x1792)重建，约60栋建筑，修正图书馆位置与楼间距。
原v8: 按高德最新卫星影像逐栋数字化全部建筑轮廓（约38栋），修正宿舍区/核心教学区
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

LAT0, LON0 = 34.7837, 113.8206
MX = 111320.0 * math.cos(math.radians(LAT0))
MY = 110570.0
RES17 = 156543.03392 * math.cos(math.radians(LAT0)) / (2 ** 17)
RES16 = 156543.03392 * math.cos(math.radians(LAT0)) / (2 ** 16)
CX, CY = 2816 / 2, 1792 / 2

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
 'classroom':texmat('fac_classroom_v12',os.path.join(TEXDIR,'facade_teach_axis.jpg')),
 'office':texmat('fac_office',os.path.join(TEXDIR,'facade_office.jpg')),
 'dorm':texmat('fac_dorm',os.path.join(TEXDIR,'facade_dorm_photo.jpg')),
 'library':texmat('fac_library_photo',os.path.join(TEXDIR,'facade_library_photo_v8.jpg')),
 'canteen':texmat('fac_canteen',os.path.join(TEXDIR,'facade_canteen.jpg')),
 'gym':texmat('fac_office_gym',os.path.join(TEXDIR,'facade_office.jpg')),
}
# 知行楼/综合实验楼：实景照片中的橙红格栅 + 灰砖（若照片纹理存在则用）
_lab_tex=os.path.join(TEXDIR,'facade_teach_gray.jpg')
T['lab']=texmat('fac_lab_gray',_lab_tex) if os.path.exists(_lab_tex) else T['classroom']
T['teach_axis']=texmat('fac_teach_axis',os.path.join(TEXDIR,'facade_teach_axis.jpg'))
T['teach_gray']=texmat('fac_teach_gray',os.path.join(TEXDIR,'facade_teach_gray.jpg'))
M['roof_red']=texmat('roof_red_tiles',os.path.join(TEXDIR,'roof_red.jpg'))
# v18: 新建建筑材质
M['glass_tower']=mat('glass_tower',(0.30,0.45,0.58),rough=.18,metal=.45)
M['glass_stripe']=mat('glass_stripe',(0.16,0.26,0.38),rough=.22,metal=.35)
M['shop_warm']=mat('shop_warm',(0.86,0.72,0.52),rough=.8)
M['gate_stone']=mat('gate_stone',(0.82,0.80,0.74),rough=.85)
T['innovation']=M['glass_tower']
T['commercial']=M['shop_warm']
T['activity']=texmat('fac_activity',os.path.join(TEXDIR,'facade_office.jpg'))
T['gate']=M['gate_stone']
T['gym']=texmat('fac_gym',os.path.join(TEXDIR,'facade_office.jpg'))

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

# Ground = bright official plan (v13 look) — clean 3D sandbox, matches aerial-tone
PLAN_S=1.09; PLAN_CROP_L, PLAN_CROP_T = 85, 440; LIB_PX, LIB_PY = 562, 1214
_gnd=textured_plane('SITE_full', os.path.join(WEB,'plan_ground.jpg'),
               1100*PLAN_S, 1220*PLAN_S, -0.15, site_col)
# align ground center with world coords (plan crop center relative to library origin)
_gnd.location.x=(PLAN_CROP_L+550-LIB_PX)*PLAN_S
_gnd.location.y=(LIB_PY-(PLAN_CROP_T+610))*PLAN_S

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

# ---------- building definitions (pixel coords on FULL satellite image) ----------
import importlib.util as _ilu
_spec=_ilu.spec_from_file_location('b9data', os.path.join(os.path.dirname(__file__),'buildings_v9_data.py'))
_b9=_ilu.module_from_spec(_spec); _spec.loader.exec_module(_b9)
BUILDINGS=[]
_v11=json.load(open(os.path.join(OUT,'buildings_v18.json'),encoding='utf-8'))
for _d in _v11['buildings']:
    _b=dict(_d)
    # x,y = centroid of real footprint polygon
    _b['x']=round(sum(p[0] for p in _b['pts'])/len(_b['pts']),2)
    _b['y']=round(sum(p[1] for p in _b['pts'])/len(_b['pts']),2)
    BUILDINGS.append(_b)

INTERIOR_IDS=set(b['id'] for b in BUILDINGS if b['kind'] not in ('dorm','gate')) | \
             set(b['id'] for b in BUILDINGS if b['kind']=='dorm' and b['id'] in ('p00','p11'))

# ---------- build exteriors ----------
for b in BUILDINGS:
    name=b['id']; pts=b['pts']
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    cx,cy=sum(xs)/len(xs),sum(ys)/len(ys)
    b['x'],b['y']=cx,cy
    parent=empty('GRP_'+name,build_col)
    fmat=T.get(b['kind'],T['classroom'])
    if b.get('facade')=='axis': fmat=T['teach_axis']
    elif b.get('facade')=='gray': fmat=T['teach_gray']
    elif b.get('facade')=='glass': fmat=T['innovation']
    elif b.get('facade')=='shop': fmat=T['commercial']
    if 'inner' in b:
        inner=b['inner']
        body=add_prism_ring('B_%s_body'%name,pts,inner,b['height'],fmat,build_col)
        roof=add_prism_ring('B_%s_roof'%name,pts,inner,1.6,M['roof'],build_col,z0=b['height'])
        body.parent=parent; roof.parent=parent
        add_facade_edges(name,pts,b['height'],build_col,parent,b['floors'])
        add_facade_edges(name,inner,b['height'],build_col,parent,b['floors'])
        add_roof_details(name,pts,b,build_col,parent)
    elif b['kind']=='library':
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
        # v12: 教学楼真实特征——大挑檐 + 檐下玻璃带 + 南向入口雨棚 + 立面竖鳍
        if b['kind'] in ('classroom','lab') or b.get('facade') in ('axis','gray'):
            bx,by=(max(xs)-min(xs))/2,(max(ys)-min(ys))/2
            # 宽大挑檐（略外扩），如教学楼顶部出挑屋盖
            e=1.06
            eave=[(cx+(x-cx)*e, cy+(y-cy)*e) for x,y in pts]
            add_prism('B_%s_teave'%name,eave,2.2,M['trim'],build_col,z0=b['height']-0.6).parent=parent
            add_prism('B_%s_tglass'%name,pts,1.4,M['glass2'],build_col,z0=b['height']-2.4).parent=parent
            # 入口雨棚（朝南，位于轮廓最南边）
            ey=min(ys)
            add_box('B_%s_canopy'%name,(cx,ey-3.4,6.0),(bx*0.34,6.5,0.9),M['trim'],build_col,parent)
            for k in (-1,1):
                add_cyl('B_%s_col_%d'%(name,k),(cx+k*bx*0.14,ey-5.6,3.0),0.5,6,M['trim'],build_col,parent=parent)
        # ===== v18: 新建建筑立体化特征 =====
        if b['kind']=='innovation':
            # 大学生科创中心(鼎新楼)：玻璃幕墙塔楼 + 竖向深色格栅 + 顶部退台塔冠 + 入口大堂
            bx,by=(max(xs)-min(xs))/2,(max(ys)-min(ys))/2
            # 竖向玻璃条（沿四边密肋，突出高层挺拔感）
            for i in range(len(pts)):
                x1,y1=pts[i]; x2,y2=pts[(i+1)%len(pts)]
                seg=9
                for k in range(1,seg):
                    t=k/seg; fx=x1+(x2-x1)*t; fy=y1+(y2-y1)*t
                    add_box('B_%s_vfin_%d_%d'%(name,i,k),(fx,fy,b['height']/2),(1.5,1.5,b['height']-2),M['glass_stripe'],build_col,parent)
            # 顶部退台塔冠
            crown=[(cx+(x-cx)*0.74, cy+(y-cy)*0.74) for x,y in pts]
            add_prism('B_%s_crown'%name,crown,7.5,M['glass_stripe'],build_col,z0=b['height']).parent=parent
            add_prism('B_%s_crowncap'%name,crown,1.2,M['trim'],build_col,z0=b['height']+7.5).parent=parent
            # 玻璃大堂（南侧）
            ey=min(ys)
            add_box('B_%s_lobby'%name,(cx,ey-4,8),(bx*0.6,7,13),M['glass2'],build_col,parent)
            add_prism('B_%s_lobbytop'%name,pts,1.0,M['trim'],build_col,z0=b['height']*0.32).parent=parent
        elif b['kind']=='gate':
            # 校门：两侧门柱 + 横梁门楼 + 顶檐（东南西北四门可辨识）
            bx,by=(max(xs)-min(xs))/2,(max(ys)-min(ys))/2
            for s in (-1,1):
                add_box('B_%s_pier_%d'%(name,s),(cx+s*bx*0.62,cy,5.5),(4.5,5.0,11),M['gate_stone'],build_col,parent)
            add_box('B_%s_beam'%name,(cx,cy,10.5),(bx*1.45,4.0,2.2),M['gate_stone'],build_col,parent)
            add_box('B_%s_cap'%name,(cx,cy,12.2),(bx*1.6,5.2,1.1),M['roof_blue'],build_col,parent)
        elif b['kind']=='commercial':
            # 商业街：低层商铺 + 连续骑楼雨棚 + 招牌色带
            ey=min(ys); bx=(max(xs)-min(xs))/2
            add_box('B_%s_arcade'%name,(cx,ey-3.0,4.2),(bx*1.9,5.0,0.7),M['trim'],build_col,parent)
            for k in range(-3,4):
                add_cyl('B_%s_col_%d'%(name,k),(cx+k*bx*0.28,ey-5.0,2.1),0.35,4.2,M['trim'],build_col,parent=parent)
            add_prism('B_%s_sign'%name,pts,1.4,M['shop_warm'],build_col,z0=b['height']-1.4).parent=parent
        elif b['kind']=='gym':
            # 体育训练馆：大跨度拱形屋顶（蓝色）
            bx,by=(max(xs)-min(xs))/2,(max(ys)-min(ys))/2
            add_frustum('B_%s_gymroof'%name,cx,cy,bx,by,bx*0.9,by*0.78,
                        b['height'],b['height']+5.0,M['roof_blue'],build_col).parent=parent
        add_roof_details(name,pts,b,build_col,parent)

# ---------- landscape: real satellite底图已含湖泊/道路/运动场/绿化，仅保留图书馆广场 ----------
site_parent=empty('GRP_landscape',site_col)
lx,ly=0,0
# v14: 白色圆盘广场环移除——卫星图地面已含真实图书馆广场与绿地
# add_ring('SITE_lib_plaza_outer',lx,ly,46,74,0.35,M['plaza'],site_col,site_parent)
# add_ring('SITE_lib_plaza_inner',lx,ly,40,46,0.4,M['trim'],site_col,site_parent)

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
        floorH=4.0, pts=[[round(p[0],1),round(p[1],1)] for p in b['pts']],
        desc=b['desc'],interior=b['interior'],hasInterior=b['id'] in INTERIOR_IDS))
with open(os.path.join(WEB,'buildings.json'),'w',encoding='utf-8') as f:
    json.dump(dict(campus=dict(name='河南财经政法大学（郑东校区）',lat0=LAT0,lon0=LON0,
        address='河南省郑州市金水东路180号',
        note='地面采用真实卫星影像（明湖、草坪、道路、树木等均为实景）；建筑位置/轮廓依据官方平面图矢量化（建树楼按官方标注补正）；楼名含学校官方文化名；教学楼立面按实景重绘；高度为常见层数示意，非测绘成果。'),
        buildings=meta),f,ensure_ascii=False,indent=2)
print('DONE',len(BUILDINGS),'RES',RES17,RES16)
