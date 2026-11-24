# -*- coding: utf-8 -*-
"""快速试验：把 blend 地面贴图换成真实卫星图并渲染，验证视觉效果。"""
import bpy, os, math
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(ROOT, '..', 'output'))
WEB = os.path.abspath(os.path.join(ROOT, '..', 'web'))
BLEND = os.path.join(OUT, 'HUEL_Zhengdong_Campus.blend')
IMG = os.path.join(OUT, 'test_sat_ground.png')
SAT = os.path.join(WEB, 'sat_ground.jpg')

bpy.ops.wm.open_mainfile(filepath=BLEND)
scene = bpy.context.scene
for col in bpy.data.collections:
    col.hide_render = False
    col.hide_viewport = False

# 找到地面对象并替换贴图
targets = [o for o in bpy.data.objects if o.name.startswith('SITE_full')]
print('GROUND OBJS', [o.name for o in targets])
for o in targets:
    for mat in o.data.materials:
        if not mat or not mat.use_nodes:
            continue
        for n in mat.node_tree.nodes:
            if n.type == 'TEX_IMAGE':
                img = bpy.data.images.load(SAT, check_existing=True)
                n.image = img
                print('REPLACED', o.name, mat.name, '->', img.filepath)

# 相机：斜俯视图书馆+湖
cam_data = bpy.data.cameras.new('TestCam')
cam = bpy.data.objects.new('TestCam', cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam.location = (-120, -440, 180)
target = Vector((-20, -80, 10))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
cam_data.type = 'PERSP'
cam_data.lens = 42

# 光照
world = scene.world or bpy.data.worlds.new('W')
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value = (0.78, 0.85, 0.95, 1)
bg.inputs['Strength'].default_value = 1.0
sun_data = bpy.data.lights.new('Sun', 'SUN')
sun = bpy.data.objects.new('Sun', sun_data)
scene.collection.objects.link(sun)
sun.location = (200, -300, 600)
sun.rotation_euler = (math.radians(35), math.radians(-20), math.radians(-25))
sun_data.energy = 2.0
sun_data.angle = math.radians(8)

scene.render.engine = ('BLENDER_EEVEE_NEXT' if hasattr(scene.render, 'bl_rna')
    and 'BLENDER_EEVEE_NEXT' in scene.render.bl_rna.properties['engine'].enum_items.keys()
    else 'BLENDER_EEVEE')
scene.render.resolution_x = 1400
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = IMG
try:
    scene.view_settings.view_transform = 'AgX'
except Exception:
    pass

bpy.ops.render.render(write_still=True)
print('RENDERED', IMG, os.path.getsize(IMG))
