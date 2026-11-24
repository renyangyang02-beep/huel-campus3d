# -*- coding: utf-8 -*-
"""Render an offline preview of the v12 campus model (bypasses browser WebGL issues).
Loads the blend saved by build_campus_v12.py, sets a top-down oblique camera,
enables EEVEE with soft lighting, renders output/v12_render.png.
"""
import bpy, math, os
from mathutils import Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(ROOT, '..', 'output'))
BLEND = os.path.join(OUT, 'HUEL_Zhengdong_Campus.blend')
IMG = os.path.join(OUT, 'v14_render_clean.png')

bpy.ops.wm.open_mainfile(filepath=BLEND)
scene = bpy.context.scene

# Ensure collections visible
for col in bpy.data.collections:
    col.hide_render = False
    col.hide_viewport = False
# 隐藏室内集合，避免室内楼板与地面共面 z-fighting 黑条
for col in bpy.data.collections:
    if any(k in col.name.lower() for k in ('interior','fl_','in_')):
        col.hide_render = True

# Camera: top-down oblique looking at campus center (library ~ origin)
cam_data = bpy.data.cameras.new('PreviewCam')
cam = bpy.data.objects.new('PreviewCam', cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam.location = (-120, -440, 150)
target = Vector((-20, -100, 15))
direction = target - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
cam_data.type = 'PERSP'
cam_data.lens = 40

# Lighting: world ambient + sun
world = bpy.data.worlds.new('PreviewWorld') if not scene.world else scene.world
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value = (0.78, 0.85, 0.95, 1)
bg.inputs['Strength'].default_value = 0.9

sun_data = bpy.data.lights.new('Sun', 'SUN')
sun = bpy.data.objects.new('Sun', sun_data)
scene.collection.objects.link(sun)
sun.location = (200, -300, 600)
sun.rotation_euler = (math.radians(35), math.radians(-20), math.radians(-25))
sun_data.energy = 2.2
sun_data.angle = math.radians(8)

# Render settings
scene.render.engine = 'CYCLES' if False else 'BLENDER_EEVEE_NEXT' if hasattr(scene.render, 'bl_rna') and 'BLENDER_EEVEE_NEXT' in scene.render.bl_rna.properties['engine'].enum_items.keys() else 'BLENDER_EEVEE'
scene.render.resolution_x = 1400
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = IMG
scene.render.film_transparent = False
try:
    scene.view_settings.view_transform = 'AgX'
except Exception:
    pass

bpy.ops.render.render(write_still=True)
print('RENDERED', IMG, os.path.getsize(IMG))
