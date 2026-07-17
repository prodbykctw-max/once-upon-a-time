import bpy, os
import numpy as np

# Compose 25 x 512px frames into 1280x1280 sheets (5x5 grid of 256px cells).
# Grid row 0 = TOP (canvas convention); Blender pixels start bottom-left.
FRAMES = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\jande_frames"
OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul"

for anim in ('run', 'jump', 'slide'):
    sheet = np.zeros((1280, 1280, 4), dtype=np.float32)
    missing = []
    for i in range(25):
        p = os.path.join(FRAMES, f'{anim}_{i:02d}.png')
        if not os.path.exists(p):
            missing.append(i); continue
        img = bpy.data.images.load(p)
        img.scale(256, 256)
        px = np.empty(256 * 256 * 4, dtype=np.float32)
        img.pixels.foreach_get(px)
        px = px.reshape(256, 256, 4)
        col = i % 5
        row = i // 5
        y0 = (4 - row) * 256   # flip: grid row 0 at top of image
        x0 = col * 256
        sheet[y0:y0 + 256, x0:x0 + 256, :] = px
        bpy.data.images.remove(img)
    out_img = bpy.data.images.new(f'sheet_{anim}', 1280, 1280, alpha=True, float_buffer=False)
    out_img.pixels.foreach_set(sheet.reshape(-1))
    out_path = os.path.join(OUT, f'bk{anim}_sheet.webp')
    sc = bpy.context.scene
    sc.render.image_settings.file_format = 'WEBP'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.render.image_settings.quality = 85
    out_img.save_render(out_path, scene=sc)
    kb = os.path.getsize(out_path) // 1024
    print(f'SHEET {anim}: {kb} KB missing={missing}')
print('COMPOSE_DONE')
