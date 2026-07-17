import bpy, math
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.samples = 128; sc.cycles.use_denoising = True
sc.render.film_transparent = True
sc.render.resolution_x = 480; sc.render.resolution_y = 640
cam = bpy.data.objects.get('PrevCam')
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 2.3
for nm, loc, rot in (('final_front', (0, -3.2, -0.02), (math.pi/2, 0, 0)),
                     ('final_side', (3.2, 0, -0.02), (math.pi/2, 0, math.pi/2)),
                     ('final_back', (0, 3.2, -0.02), (math.pi/2, 0, math.pi))):
    cam.location = loc; cam.rotation_euler = rot
    sc.camera = cam
    sc.render.filepath = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul" + "\\" + nm + ".png"
    bpy.ops.render.render(write_still=True)
print('FINALS_DONE')
