# Stage 7 ART GALLERY - FLOOR tile: light oak herringbone parquet
FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())
import bpy, math

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles\floor_7.png"

reset_scene()

# ---------- light oak material with per-plank variation ----------
oak = wood_mat('Oak', tone=(0.45, 0.30, 0.15), grain_scale=2.5, rough=0.30)
nt = oak.node_tree
mapping = next(n for n in nt.nodes if n.type == 'MAPPING')
wave    = next(n for n in nt.nodes if n.type == 'TEX_WAVE')
noise   = next(n for n in nt.nodes if n.type == 'TEX_NOISE')
ramp    = next(n for n in nt.nodes if n.type == 'VALTORGB')
bsdf    = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')

# grain runs along plank length (local X): bands vary along Y
wave.bands_direction = 'Y'
wave.inputs['Distortion'].default_value = 4.5
wave.inputs['Detail'].default_value = 3.0

# per-object random offset so each plank gets unique grain
oi = nt.nodes.new('ShaderNodeObjectInfo')
m1 = nt.nodes.new('ShaderNodeMath'); m1.operation = 'MULTIPLY'
m1.inputs[1].default_value = 37.0
nt.links.new(oi.outputs['Random'], m1.inputs[0])
m2 = nt.nodes.new('ShaderNodeMath'); m2.operation = 'MULTIPLY'
m2.inputs[1].default_value = 11.0
nt.links.new(oi.outputs['Random'], m2.inputs[0])
comb = nt.nodes.new('ShaderNodeCombineXYZ')
nt.links.new(m1.outputs[0], comb.inputs['X'])
nt.links.new(m2.outputs[0], comb.inputs['Y'])
vadd = nt.nodes.new('ShaderNodeVectorMath')  # default ADD
nt.links.new(mapping.outputs[0], vadd.inputs[0])
nt.links.new(comb.outputs[0], vadd.inputs[1])
nt.links.new(vadd.outputs[0], wave.inputs['Vector'])
nt.links.new(vadd.outputs[0], noise.inputs['Vector'])

# per-plank brightness variation
hsv = nt.nodes.new('ShaderNodeHueSaturation')
nt.links.new(ramp.outputs['Color'], hsv.inputs['Color'])
mr = nt.nodes.new('ShaderNodeMapRange')
mr.inputs['From Min'].default_value = 0.0
mr.inputs['From Max'].default_value = 1.0
mr.inputs['To Min'].default_value = 0.82
mr.inputs['To Max'].default_value = 1.14
nt.links.new(oi.outputs['Random'], mr.inputs['Value'])
nt.links.new(mr.outputs[0], hsv.inputs['Value'])
nt.links.new(hsv.outputs['Color'], bsdf.inputs['Base Color'])

# dark seam underlay
dark = bpy.data.materials.new('Seam')
dark.use_nodes = True
db = dark.node_tree.nodes['Principled BSDF']
db.inputs['Base Color'].default_value = (0.07, 0.045, 0.02, 1)
db.inputs['Roughness'].default_value = 0.8
plane((0, 0, -0.045), 4, dark, name='Underlay')

# ---------- herringbone lattice ----------
# plank L x W, columns along y; column i at x=i*L/sqrt2, orientation +-45,
# odd columns shifted by half the y-period (verified herringbone lattice).
L = 0.47140
W = 0.11785
sx = L / math.sqrt(2)          # 0.33335 column spacing (3 periods per 2 units)
sy = W * math.sqrt(2)          # 0.16667 y period
half = W / math.sqrt(2)        # 0.08334 odd-column offset
for i in range(-4, 5):
    ang = math.radians(45 if i % 2 == 0 else -45)
    yoff = (i % 2) * half
    for j in range(-9, 10):
        cube((i * sx, j * sy + yoff, -0.021),
             (L * 0.97, W * 0.93, 0.04),
             oak, rot=(0, 0, ang), name=f'P{i}_{j}')

# ---------- lights / camera ----------
warm_rig()
area_light((0, 0, 3), 260, 5.0, (1, 0.95, 0.88))

floor_cam()
render_to(OUT, 192, 192, transparent=False, samples=160)
