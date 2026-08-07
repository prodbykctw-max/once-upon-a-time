import bpy, math
sc = bpy.context.scene
copper = bpy.data.materials['Copper']
copper_hi = bpy.data.materials['CopperHi']
# hairline roll: tilted elliptical ring tracing the cut line (front 0.795 -> sides 0.74)
bpy.ops.mesh.primitive_torus_add(major_radius=0.112, minor_radius=0.036, location=(0, 0.02, 0.772))
roll = bpy.context.active_object
roll.name = 'HairlineRoll'
roll.scale = (1.02, 1.08, 1.0)
roll.rotation_euler = (math.radians(-11), 0, 0)
bpy.ops.object.shade_smooth()
roll.data.materials.append(copper)
# deeper temple coverage over the dark ear-flap slivers
for sgn in (-1, 1):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.052, location=(sgn * 0.103, -0.045, 0.718), segments=14, ring_count=10)
    t = bpy.context.active_object
    t.scale = (0.6, 1.0, 1.35)
    bpy.ops.object.shade_smooth()
    t.data.materials.append(copper_hi)
# renders
sc.render.engine = 'CYCLES'; sc.cycles.samples = 96; sc.cycles.use_denoising = True
sc.render.film_transparent = True
sc.render.resolution_x = 480; sc.render.resolution_y = 580
cam = bpy.data.objects.get('PrevCam')
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 0.42
cam.location = (0, -1.6, 0.72); cam.rotation_euler = (math.pi/2, 0, 0)
sc.camera = cam
sc.render.filepath = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\nohat_front.png"
bpy.ops.render.render(write_still=True)
cam.location = (1.6, 0, 0.72); cam.rotation_euler = (math.pi/2, 0, math.pi/2)
sc.render.filepath = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\nohat_side.png"
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_mainfile()
print('HAIRLINE_DONE')
