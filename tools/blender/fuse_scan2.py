import bpy, math, os
import numpy as np

# FUSE v2: solidify the open shells FIRST (closed slabs), then voxel remesh
# (real volumes fuse properly), smooth, UV, bake + inpaint. One pass.
SAVE = r"C:\Users\Owner\Documents\once-upon-a-time\assets\jande_fused.blend"
OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul"
TEXPATH = r"C:\Users\Owner\Documents\once-upon-a-time\assets\jande_fused_diffuse.png"

sc = bpy.context.scene
orig = bpy.data.objects['JandeModel']
for nm in ('ChkCam', 'ChkSun', 'Cube', 'Light', 'Camera', 'Lat'):
    o = bpy.data.objects.get(nm)
    if o: bpy.data.objects.remove(o, do_unlink=True)

# ── 1. copy -> solidify -> voxel remesh -> relax ──
fused = orig.copy()
fused.data = orig.data.copy()
fused.name = 'JandeFused'
sc.collection.objects.link(fused)
bpy.ops.object.select_all(action='DESELECT')
fused.select_set(True)
bpy.context.view_layer.objects.active = fused
sol = fused.modifiers.new('Sol', 'SOLIDIFY')
sol.thickness = 0.014
sol.offset = 0.0
bpy.ops.object.modifier_apply(modifier='Sol')
fused.data.remesh_voxel_size = 0.006
fused.data.remesh_voxel_adaptivity = 0.0
bpy.ops.object.voxel_remesh()
smo = fused.modifiers.new('Smo', 'SMOOTH')
smo.factor = 0.6
smo.iterations = 6
bpy.ops.object.modifier_apply(modifier='Smo')
bpy.ops.object.shade_smooth()
print(f'fused: {len(fused.data.vertices)} verts, {len(fused.data.polygons)} faces')

# ── 2. smart UV ──
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.003)
bpy.ops.object.mode_set(mode='OBJECT')
print('UV done')

# ── 3. bake original texture onto fused (magenta prefill + inpaint) ──
bake_img = bpy.data.images.new('JandeBaked', 2048, 2048, alpha=False)
W = 2048
px = np.empty(W * W * 4, dtype=np.float32)
px[0::4] = 1.0; px[1::4] = 0.0; px[2::4] = 1.0; px[3::4] = 1.0
bake_img.pixels.foreach_set(px)
mat = bpy.data.materials.new('JandeFusedMat')
mat.use_nodes = True
nt = mat.node_tree
bsdf = nt.nodes['Principled BSDF']
texn = nt.nodes.new('ShaderNodeTexImage')
texn.image = bake_img
texn.location = (-400, 200)
nt.links.new(texn.outputs['Color'], bsdf.inputs['Base Color'])
bsdf.inputs['Roughness'].default_value = 0.55
fused.data.materials.clear()
fused.data.materials.append(mat)
nt.nodes.active = texn

sc.render.engine = 'CYCLES'
sc.cycles.samples = 16
sc.render.bake.use_pass_direct = False
sc.render.bake.use_pass_indirect = False
sc.render.bake.use_selected_to_active = True
sc.render.bake.cage_extrusion = 0.035
sc.render.bake.max_ray_distance = 0.10
sc.render.bake.use_clear = False
sc.render.bake.margin = 8
bpy.ops.object.select_all(action='DESELECT')
orig.select_set(True)
fused.select_set(True)
bpy.context.view_layer.objects.active = fused
bpy.ops.object.bake(type='DIFFUSE')
print('bake done')

buf = np.empty(W * W * 4, dtype=np.float32)
bake_img.pixels.foreach_get(buf)
rgba = buf.reshape(W, W, 4)
rgb = rgba[:, :, :3]
hole = (rgba[:, :, 0] > 0.95) & (rgba[:, :, 1] < 0.05) & (rgba[:, :, 2] > 0.95)
print(f'holes: {int(hole.sum())}')
filled = rgb.copy()
mask = ~hole
for it in range(64):
    if hole.sum() == 0: break
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
bake_img.pixels.foreach_set(rgba.reshape(-1))
bake_img.filepath_raw = TEXPATH
bake_img.file_format = 'PNG'
bake_img.save()
bake_img.pack()
print('inpaint done')

# ── 4. fused becomes THE JandeModel ──
bpy.data.objects.remove(orig, do_unlink=True)
fused.name = 'JandeModel'

# ── 5. verification renders ──
sc.cycles.samples = 96
sc.cycles.use_denoising = True
sc.view_settings.view_transform = 'Filmic'
sc.render.film_transparent = True
sc.render.image_settings.file_format = 'PNG'
cd = bpy.data.cameras.new('PrevCam'); cd.type = 'ORTHO'
cam = bpy.data.objects.new('PrevCam', cd)
sc.collection.objects.link(cam)
sc.camera = cam
def area(loc, e, size, col, rot):
    ld = bpy.data.lights.new('L', 'AREA'); ld.energy = e; ld.size = size; ld.color = col
    lo = bpy.data.objects.new('L', ld); sc.collection.objects.link(lo)
    lo.location = loc; lo.rotation_euler = rot
area((-1.8, -2.6, 1.6), 260, 2.6, (1, 0.93, 0.83), (math.radians(55), 0, math.radians(-35)))
area((2.0, -2.2, 0.6), 90, 2.2, (0.65, 0.72, 0.95), (math.radians(65), 0, math.radians(40)))
area((0, 2.8, 1.2), 160, 2.4, (1, 0.9, 0.8), (math.radians(-70), 0, 0))
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.3

sc.render.resolution_x = 480; sc.render.resolution_y = 640
cd.ortho_scale = 2.3
cam.location = (0, -3.2, -0.02); cam.rotation_euler = (math.pi/2, 0, 0)
sc.render.filepath = os.path.join(OUT, 'fused_front.png')
bpy.ops.render.render(write_still=True)
cam.location = (0, 3.2, -0.02); cam.rotation_euler = (math.pi/2, 0, math.pi)
sc.render.filepath = os.path.join(OUT, 'fused_back.png')
bpy.ops.render.render(write_still=True)
sc.render.resolution_x = 480; sc.render.resolution_y = 580
cd.ortho_scale = 0.42
cam.location = (0, -1.6, 0.72); cam.rotation_euler = (math.pi/2, 0, 0)
sc.render.filepath = os.path.join(OUT, 'fused_face.png')
bpy.ops.render.render(write_still=True)

bpy.ops.wm.save_as_mainfile(filepath=SAVE)
print('FUSE2_DONE saved:', SAVE)
