import bpy, math, os
import numpy as np

# Project the real face photo (face_crop.png) onto the scan's smeared face.
# Anchored at the mesh nose tip; window scaled from photo landmark fractions:
# crop 480x580: brow 0.22, eyes 0.31, nose 0.47, lips 0.60, chin 0.80 (from top),
# face centerline u = 0.44.
BLEND = r"C:\Users\Owner\Documents\once-upon-a-time\assets\jande_gown.blend"
CROP = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\face_crop.png"
OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul"

# tunables (iterated by render comparison)
S = 0.31           # mesh height covered by the full crop
U_ANCHOR = 0.44    # face centerline in crop u
NOSE_FRAC = 0.47   # nose fraction from crop top
MASK_RX, MASK_RZ = 0.075, 0.13
MASK_CZ_OFF = 0.045  # ellipse center offset from nose z

obj = bpy.data.objects['JandeModel']
me = obj.data
n = len(me.vertices)
V = np.empty(n * 3)
me.vertices.foreach_get('co', V)
V = V.reshape(n, 3)
X, Y, Z = V[:, 0], V[:, 1], V[:, 2]
crown_z = float(Z.max())

# nose tip: front-most vertex in the face band
mh = (Z > crown_z - 0.30) & (Z < crown_z - 0.05) & (np.abs(X) < 0.12)
idx = np.argmin(Y[mh])
nx = float(X[mh][idx]); ny = float(Y[mh][idx]); nz = float(Z[mh][idx])
print(f'nose tip: ({nx:.3f}, {ny:.3f}, {nz:.3f}) crown={crown_z:.3f}')

z_top = nz + 0.012 + NOSE_FRAC * S
z_bot = z_top - S
w = S * (480.0 / 580.0)
x0 = nx - U_ANCHOR * w
x1 = x0 + w

mtl = obj.data.materials[0]
nt = mtl.node_tree
bsdf = next(nd for nd in nt.nodes if nd.type == 'BSDF_PRINCIPLED')
base_in = bsdf.inputs['Base Color']

# remove any previous projection nodes FIRST (idempotent re-runs)
for nd in [nd for nd in nt.nodes if nd.get('face_proj')]:
    nt.nodes.remove(nd)

# original color source: surviving Base Color link, else the scan's own
# image texture node (never one of ours — those are gone already)
if base_in.links:
    orig_sock = base_in.links[0].from_socket
else:
    scan_tex = next((nd for nd in nt.nodes if nd.type == 'TEX_IMAGE'
                     and nd.image and 'face_crop' not in nd.image.name), None)
    orig_sock = scan_tex.outputs['Color'] if scan_tex else None
    if scan_tex: print('recovered original texture:', scan_tex.image.name)

def node(tp, x, y, **props):
    nd = nt.nodes.new(tp)
    nd.location = (x, y)
    nd['face_proj'] = True
    for k, v in props.items():
        setattr(nd, k, v)
    return nd

tc = node('ShaderNodeTexCoord', -1200, 300)
sep = node('ShaderNodeSeparateXYZ', -1000, 300)
nt.links.new(tc.outputs['Object'], sep.inputs[0])
mu = node('ShaderNodeMapRange', -800, 420)
mu.inputs['From Min'].default_value = x0
mu.inputs['From Max'].default_value = x1
nt.links.new(sep.outputs['X'], mu.inputs['Value'])
mv = node('ShaderNodeMapRange', -800, 180)
mv.inputs['From Min'].default_value = z_bot
mv.inputs['From Max'].default_value = z_top
nt.links.new(sep.outputs['Z'], mv.inputs['Value'])
comb = node('ShaderNodeCombineXYZ', -600, 300)
nt.links.new(mu.outputs[0], comb.inputs['X'])
nt.links.new(mv.outputs[0], comb.inputs['Y'])
img = bpy.data.images.load(CROP, check_existing=True)
tex = node('ShaderNodeTexImage', -430, 300)
tex.image = img
tex.extension = 'EXTEND'
nt.links.new(comb.outputs[0], tex.inputs['Vector'])
hsv = node('ShaderNodeHueSaturation', -260, 300)
hsv.inputs['Value'].default_value = 0.78
hsv.inputs['Saturation'].default_value = 1.06
nt.links.new(tex.outputs['Color'], hsv.inputs['Color'])

# ellipse mask around the face
sub_x = node('ShaderNodeMath', -800, -60, operation='SUBTRACT')
nt.links.new(sep.outputs['X'], sub_x.inputs[0]); sub_x.inputs[1].default_value = nx
div_x = node('ShaderNodeMath', -650, -60, operation='DIVIDE')
nt.links.new(sub_x.outputs[0], div_x.inputs[0]); div_x.inputs[1].default_value = MASK_RX
sq_x = node('ShaderNodeMath', -500, -60, operation='MULTIPLY')
nt.links.new(div_x.outputs[0], sq_x.inputs[0]); nt.links.new(div_x.outputs[0], sq_x.inputs[1])
sub_z = node('ShaderNodeMath', -800, -220, operation='SUBTRACT')
nt.links.new(sep.outputs['Z'], sub_z.inputs[0]); sub_z.inputs[1].default_value = nz + MASK_CZ_OFF
div_z = node('ShaderNodeMath', -650, -220, operation='DIVIDE')
nt.links.new(sub_z.outputs[0], div_z.inputs[0]); div_z.inputs[1].default_value = MASK_RZ
sq_z = node('ShaderNodeMath', -500, -220, operation='MULTIPLY')
nt.links.new(div_z.outputs[0], sq_z.inputs[0]); nt.links.new(div_z.outputs[0], sq_z.inputs[1])
add_e = node('ShaderNodeMath', -350, -140, operation='ADD')
nt.links.new(sq_x.outputs[0], add_e.inputs[0]); nt.links.new(sq_z.outputs[0], add_e.inputs[1])
efall = node('ShaderNodeMapRange', -200, -140)
efall.interpolation_type = 'SMOOTHSTEP'
efall.inputs['From Min'].default_value = 1.0
efall.inputs['From Max'].default_value = 0.62
nt.links.new(add_e.outputs[0], efall.inputs['Value'])

# front-facing mask
geo = node('ShaderNodeNewGeometry', -800, -400)
dotf = node('ShaderNodeVectorMath', -650, -400, operation='DOT_PRODUCT')
nt.links.new(geo.outputs['Normal'], dotf.inputs[0])
dotf.inputs[1].default_value = (0, -1, 0)
ffall = node('ShaderNodeMapRange', -450, -400)
ffall.interpolation_type = 'SMOOTHSTEP'
ffall.inputs['From Min'].default_value = 0.25
ffall.inputs['From Max'].default_value = 0.6
nt.links.new(dotf.outputs['Value'], ffall.inputs['Value'])

mask = node('ShaderNodeMath', -60, -140, operation='MULTIPLY')
nt.links.new(efall.outputs[0], mask.inputs[0])
nt.links.new(ffall.outputs[0], mask.inputs[1])

mix = node('ShaderNodeMix', 140, 260)
mix.data_type = 'RGBA'
if orig_sock is not None:
    nt.links.new(orig_sock, mix.inputs['A'])
else:
    mix.inputs['A'].default_value = (*base_in.default_value[:3], 1)
nt.links.new(hsv.outputs['Color'], mix.inputs['B'])
nt.links.new(mask.outputs[0], mix.inputs['Factor'])
nt.links.new(mix.outputs['Result'], base_in)

# ── verification render: face close-up front ──
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.samples = 96
sc.cycles.use_denoising = True
sc.render.film_transparent = True
sc.render.resolution_x = 480
sc.render.resolution_y = 580
cam = bpy.data.objects.get('PrevCam')
if cam is None:
    cd = bpy.data.cameras.new('PrevCam'); cd.type = 'ORTHO'
    cam = bpy.data.objects.new('PrevCam', cd)
    sc.collection.objects.link(cam)
cam.data.type = 'ORTHO'
cam.data.ortho_scale = S * 1.35
cam.location = (nx, ny - 1.6, nz + 0.02)
cam.rotation_euler = (math.pi / 2, 0, 0)
sc.camera = cam
sc.render.filepath = os.path.join(OUT, 'face_check.png')
bpy.ops.render.render(write_still=True)

bpy.ops.wm.save_mainfile()
print('FACE_PROJ_DONE')
