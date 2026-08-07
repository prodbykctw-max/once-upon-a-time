import math, random, os
FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())
OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles"

def plain_metal(name, tone, rough):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*tone, 1)
    b.inputs['Metallic'].default_value = 1.0
    b.inputs['Roughness'].default_value = rough
    return m

# ═══ FLOOR 6 v2: full-coverage worn flagstones ═══
sc = reset_scene()
random.seed(66)
grout = stone_mat('Grout', (0.05, 0.05, 0.045), rough=0.95, scale=8, bump=0.2)
plane((0, 0, -0.02), 4.6, grout)
# grid of slabs with slight size/rotation jitter, overlapping coverage
for gx in range(-2, 3):
    for gy in range(-2, 3):
        x = gx * 0.52 + random.uniform(-0.02, 0.02)
        y = gy * 0.52 + random.uniform(-0.02, 0.02)
        tone = 0.14 + random.uniform(-0.035, 0.05)
        moss = random.uniform(0, 0.018)
        m = stone_mat(f'Slab{gx}{gy}', (tone, tone + moss, tone * 0.95), rough=0.85, scale=5, bump=0.45)
        cube((x, y, 0.015), (0.5, 0.5, 0.04), m, rot=(0, 0, random.uniform(-0.02, 0.02)))
area_light((-1.5, -1.5, 3.0), 300, 3.5, (0.9, 0.88, 0.92), (math.radians(20), 0, math.radians(-25)))
area_light((1.5, 1.2, 2.5), 80, 3.0, (0.6, 0.65, 0.85), (math.radians(-18), 0, math.radians(20)))
floor_cam()
render_to(os.path.join(OUT, 'floor_6.png'), 192, 192, samples=160)

# ═══ DECOR 2 v2: proper katana display stand ═══
sc = reset_scene()
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.4
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.55, 0.5, 0.45, 1)
lacq = fabric_mat('BlackLacquer', (0.02, 0.02, 0.025), rough=0.15)
redsilk = fabric_mat('RedSilk', (0.3, 0.02, 0.04), rough=0.7)
goldm = plain_metal('GoldFit', (0.7, 0.5, 0.14), 0.3)
blade = plain_metal('Blade', (0.62, 0.64, 0.7), 0.12)
saya1 = fabric_mat('Saya1', (0.25, 0.02, 0.03), rough=0.25)   # red scabbard
saya2 = fabric_mat('Saya2', (0.02, 0.05, 0.15), rough=0.25)   # navy scabbard
wrap = fabric_mat('Wrap', (0.04, 0.04, 0.05), rough=0.85)
# base
cube((0, 0, 0.08), (0.9, 0.4, 0.16), lacq)
cube((0, 0, 0.18), (0.7, 0.3, 0.05), redsilk)
# two upright posts with Y-forks
for s in (-1, 1):
    cyl((s * 0.32, 0, 0.75), 0.045, 1.3, lacq, verts=16)
    # fork prongs (two angled stubs at two heights)
    for hz in (0.85, 1.25):
        for d in (-1, 1):
            f = cyl((s * 0.32, d * 0.06, hz + 0.05), 0.022, 0.16, lacq, verts=10)
            f.rotation_euler = (math.radians(28 * d), 0, 0)
# katana 1 (upper): scabbarded, red saya
k1 = cyl((0, 0, 1.32), 0.035, 1.15, saya1, rot=(0, math.pi/2, 0), verts=16)
k1.scale = (1, 0.8, 1)
h1 = cyl((-0.68, 0, 1.32), 0.04, 0.28, wrap, rot=(0, math.pi/2, 0), verts=14)
cyl((-0.53, 0, 1.32), 0.055, 0.02, goldm, rot=(0, math.pi/2, 0), verts=16)  # tsuba
# katana 2 (lower): bare curved blade suggestion — slight arc via 3 segments
for i, (dx, dz, ang) in enumerate([(-0.3, 0.0, 4), (0.05, 0.02, 0), (0.4, 0.0, -4)]):
    b2 = cube((dx, 0, 0.92 + dz), (0.38, 0.015, 0.035), blade, rot=(0, math.radians(ang), 0))
h2 = cyl((-0.62, 0, 0.9), 0.04, 0.26, wrap, rot=(0, math.pi/2, 0), verts=14)
cyl((-0.48, 0, 0.9), 0.055, 0.02, goldm, rot=(0, math.pi/2, 0), verts=16)
# red silk knot on base
sphere((0.25, -0.12, 0.22), 0.05, redsilk)
area_light((-1.7, -2.5, 2.6), 280, 2.8, (1, 0.93, 0.85), (math.radians(54), 0, math.radians(-26)))
area_light((1.9, -2.1, 1.2), 90, 2.2, (0.6, 0.65, 0.85), (math.radians(66), 0, math.radians(35)))
decor_cam()
render_to(os.path.join(OUT, 'decor_2.png'), 288, 480, transparent=True, samples=160)
print('FIXES_V4_DONE')
