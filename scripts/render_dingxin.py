# -*- coding: utf-8 -*-
"""渲染鼎新楼(大学生科创中心)A/B座 3D 效果图，作为网页展示图（用户选择用渲染图代替实景照）。
基于最新 v21 blend，从东南方向俯视拍摄A/B两座+周边。
"""
import bpy, math, os
from mathutils import Vector
ROOT=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.abspath(os.path.join(ROOT,'..','output'))
WEB=os.path.abspath(os.path.join(ROOT,'..','web'))
bpy.ops.wm.open_mainfile(filepath=os.path.join(OUT,'HUEL_Zhengdong_Campus.blend'))
scene=bpy.context.scene
# 省内存：隐藏室内集合（不参与外观渲染）
for col in bpy.data.collections:
    if col.name in ('INTERIORS',):
        col.hide_render=True
    else:
        col.hide_render=False

# 鼎新楼A/B新位置 world ~ (232,180) 和 (243,159)，中心取 (238,170)
center=Vector((238,170,16))
cam_data=bpy.data.cameras.new('DXCam')
cam=bpy.data.objects.new('DXCam',cam_data); scene.collection.objects.link(cam)
scene.camera=cam
# 从东面偏南看（x+方向），能同时看到南北排列的A/B两座，略俯视
cam.location=(center.x+145, center.y-55, 72)
cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
cam_data.type='PERSP'; cam_data.lens=42

world=scene.world or bpy.data.worlds.new('W'); scene.world=world
world.use_nodes=True
bg=world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value=(0.72,0.82,0.94,1)
bg.inputs['Strength'].default_value=0.85
sun_data=bpy.data.lights.new('Sun','SUN'); sun=bpy.data.objects.new('Sun',sun_data)
scene.collection.objects.link(sun)
sun.location=(center.x+200,center.y-300,500)
sun.rotation_euler=(math.radians(38),math.radians(-15),math.radians(-30))
sun_data.energy=2.4; sun_data.angle=math.radians(9)

eng='BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in scene.render.bl_rna.properties['engine'].enum_items.keys() else 'BLENDER_EEVEE'
scene.render.engine=eng
scene.render.resolution_x=760; scene.render.resolution_y=520
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.filepath=os.path.join(WEB,'realphotos','dingxin_3d.png')
scene.render.film_transparent=False
try: scene.view_settings.view_transform='AgX'
except: pass
bpy.ops.render.render(write_still=True)
print('SAVED',scene.render.filepath)
