import bpy, math, os
cap = bpy.data.objects['HairCap']
cap.scale = (1.16, 1.10, 1.12)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.samples = 96; sc.cycles.use_denoising = True
sc.render.film_transparent = True
sc.render.resolution_x = 480; sc.render.resolution_y = 580
cam = bpy.data.objects.get('PrevCam')
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 0.42
cam.location = (1.6, 0, 0.72); cam.rotation_euler = (math.pi/2, 0, math.pi/2)
sc.camera = cam
sc.render.filepath = r"OUTDIR\nohat_side.png".replace('OUTDIR', r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul")
bpy.ops.render.render(write_still=True)
cam.location = (0, -1.6, 0.72); cam.rotation_euler = (math.pi/2, 0, 0)
sc.render.filepath = r"OUTDIR\nohat_front.png".replace('OUTDIR', r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul")
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_mainfile()
print('CAP_WIDENED')
