# render all animations for the named armature
# Clint Bellanger 2015

import bpy
from math import radians

angle = -45
axis = 2 # z-axis
armature_name = "FemaleArm"

# remember UI settings to restore at the end
original_path = bpy.data.scenes[0].render.filepath
original_frame_end = bpy.context.scene.frame_end

# RenderPlatform is an Empty object located at the origin
# and has the lights and cameras attached as children.
platform = bpy.data.objects["RenderPlatform"]
armature = bpy.data.objects[armature_name]

# Render all animations
for action in bpy.data.actions:

    # make this action the active one
    armature.animation_data.action = action    

    frame_begin, frame_end = [int(x) for x in action.frame_range]
    bpy.context.scene.frame_end = frame_end

    # Render in all 8 facing directions
    for i in range(0,8):

        # rotate the render platform and all children
        temp_rot = platform.rotation_euler
        temp_rot[axis] = temp_rot[axis] - radians(angle)
        platform.rotation_euler = temp_rot;

        # set the filename action and direction prefix
        bpy.data.scenes[0].render.filepath = original_path + action.name + str(i)

        # render animation for this direction
        bpy.ops.render.render(animation=True)

# restore UI settings
bpy.data.scenes[0].render.filepath = original_path
bpy.context.scene.frame_end = original_frame_end
