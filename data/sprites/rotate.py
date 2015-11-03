import bpy

import os

import math

from time import sleep

tx = 10.0
ty = -10.0
tz = 10.0

rx = 60.0
ry = 0.0
rz = 45.0

fov = 50.0

pi = 3.14159265

scene = bpy.data.scenes["Scene"]
obj_scene = bpy.context.scene

# Set render resolution
scene.render.resolution_x = 64
scene.render.resolution_y = 64

# Set camera fov in degrees
scene.camera.data.angle = fov*(pi/180.0)

# Set camera rotation in euler angles
scene.camera.rotation_mode = 'XYZ'
scene.camera.rotation_euler[0] = rx*(pi/180.0)
scene.camera.rotation_euler[1] = ry*(pi/180.0)
scene.camera.rotation_euler[2] = rz*(pi/180.0)

# Set camera translation
scene.camera.location.x = tx
scene.camera.location.y = ty
scene.camera.location.z = tz

bpy.ops.object.select_by_type(type="MESH")
bpy.ops.object.select_by_type(type="ARMATURE")
bpy.ops.object.select_by_type(type="EMPTY")

output_path = bpy.context.scene.render.filepath

for i in range(4):
    
    bpy.context.scene.objects.active.rotation_euler[2] = math.radians(i*90)
    
    bpy.context.scene.render.filepath = os.path.join(output_path, str(i) + "-")
    
    bpy.ops.render.render(animation=True)


bpy.context.scene.render.filepath = output_path

bpy.ops.render.spritify()