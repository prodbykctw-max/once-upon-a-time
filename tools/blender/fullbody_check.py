import bpy, math, os
OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul"
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 96
sc.cycles.use_denoising = True
sc.view_settings.view_transform = 'Filmic'
sc.render.film_transparent = True
sc.render.resolution_x = 480
sc.render.resolution_y = 640
cam = bpy.data.objects['PrevCam']
sc.camera = cam
cam.data.type = 'ORTHO'
cam.data.ortho_scale = 2.3
cam.location = (0, -3.2, -0.02); cam.rotation_euler = (math.pi/2, 0, 0)
sc.render.filepath = os.path.join(OUT, 'final_front.png')
bpy.ops.render.render(write_still=True)
cam.location = (0, 3.2, -0.02); cam.rotation_euler = (math.pi/2, 0, math.pi)
sc.render.filepath = os.path.join(OUT, 'final_back.png')
bpy.ops.render.render(write_still=True)
print('FULLBODY_DONE')
