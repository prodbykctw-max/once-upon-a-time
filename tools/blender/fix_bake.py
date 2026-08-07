import bpy, math, os
import numpy as np

# Fill the bake holes: re-bake onto magenta with use_clear=False, then
# inpaint unhit texels from their neighbors (the gaps between the original
# scan fragments produce ray misses).
OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul"
TEXPATH = r"C:\Users\Owner\Documents\once-upon-a-time\assets\jande_fused_diffuse.png"
RODIN = r"C:\Users\Owner\Documents\once-upon-a-time\assets\jande_rodin.blend"

sc = bpy.context.scene
fused = bpy.data.objects['JandeModel']

# bring the ORIGINAL fragmented scan back in as bake source
with bpy.data.libraries.load(RODIN) as (src, dst):
    dst.objects = ['JandeModel']
orig = [o for o in dst.objects if o is not None][0]
orig.name = 'RodinSource'
sc.collection.objects.link(orig)

img = bpy.data.images['JandeBaked']
W = img.size[0]
px = np.empty(W * W * 4, dtype=np.float32)
px[0::4] = 1.0; px[1::4] = 0.0; px[2::4] = 1.0; px[3::4] = 1.0   # magenta
img.pixels.foreach_set(px)

mat = fused.data.materials[0]
nt = mat.node_tree
texn = next(nd for nd in nt.nodes if nd.type == 'TEX_IMAGE' and nd.image and nd.image.name == 'JandeBaked')
nt.nodes.active = texn

sc.render.engine = 'CYCLES'
sc.cycles.samples = 16
sc.render.bake.use_pass_direct = False
sc.render.bake.use_pass_indirect = False
sc.render.bake.use_selected_to_active = True
sc.render.bake.cage_extrusion = 0.03
sc.render.bake.max_ray_distance = 0.09
sc.render.bake.use_clear = False
sc.render.bake.margin = 8
bpy.ops.object.select_all(action='DESELECT')
orig.select_set(True)
fused.select_set(True)
bpy.context.view_layer.objects.active = fused
bpy.ops.object.bake(type='DIFFUSE')
print('rebake done')

# ── numpy inpaint: replace remaining magenta with neighbor average ──
buf = np.empty(W * W * 4, dtype=np.float32)
img.pixels.foreach_get(buf)
rgba = buf.reshape(W, W, 4)
rgb = rgba[:, :, :3]
hole = (rgba[:, :, 0] > 0.95) & (rgba[:, :, 1] < 0.05) & (rgba[:, :, 2] > 0.95)
print(f'holes: {int(hole.sum())} texels of {W*W}')
filled = rgb.copy()
mask = ~hole
for it in range(64):
    if hole.sum() == 0: break
    # neighbor sums via shifts
    acc = np.zeros_like(filled)
    cnt = np.zeros((W, W), dtype=np.float32)
    for dy, dx in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
        sm = np.roll(mask, (dy, dx), axis=(0, 1))
        sv = np.roll(filled, (dy, dx), axis=(0, 1))
        acc += sv * sm[:, :, None]
        cnt += sm
    can = hole & (cnt > 0)
    filled[can] = acc[can] / cnt[can][:, None]
    mask = mask | can
    hole = hole & ~can
rgba[:, :, :3] = filled
img.pixels.foreach_set(rgba.reshape(-1))
img.filepath_raw = TEXPATH
img.file_format = 'PNG'
img.save()
img.pack()
print('inpaint done')

# remove the source again and save
bpy.data.objects.remove(orig, do_unlink=True)

# verification renders
sc.cycles.samples = 96
sc.cycles.use_denoising = True
sc.render.film_transparent = True
cam = bpy.data.objects['PrevCam']
sc.camera = cam
sc.render.resolution_x = 480; sc.render.resolution_y = 640
cam.data.ortho_scale = 2.3
cam.location = (0, -3.2, -0.02); cam.rotation_euler = (math.pi/2, 0, 0)
sc.render.filepath = os.path.join(OUT, 'fused_front.png')
bpy.ops.render.render(write_still=True)
sc.render.resolution_x = 480; sc.render.resolution_y = 580
cam.data.ortho_scale = 0.42
cam.location = (0, -1.6, 0.72); cam.rotation_euler = (math.pi/2, 0, 0)
sc.render.filepath = os.path.join(OUT, 'fused_face.png')
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_mainfile()
print('FIX_BAKE_DONE')
