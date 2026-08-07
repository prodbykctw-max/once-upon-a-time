import math, random, os
FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())
OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\bgs"

def plain_metal(name, tone, rough):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*tone, 1)
    b.inputs['Metallic'].default_value = 1.0
    b.inputs['Roughness'].default_value = rough
    return m

def corridor_cam():
    cam = persp_cam((0, -6, 1.5), (math.radians(90), 0, 0), lens=24)
    cam.data.shift_y = 0.09
    return cam

# ═══ BG 1: EGYPTIAN hypostyle ═══
sc = reset_scene()
random.seed(21)
sand = stone_mat('SandFloor', (0.3, 0.22, 0.12), rough=0.8, scale=6, bump=0.3)
plane((0, 16, 0), 52, sand)
path = stone_mat('Path', (0.38, 0.3, 0.18), rough=0.5, scale=3, bump=0.1)
cube((0, 16, 0.01), (2.6, 48, 0.02), path)
wallm = stone_mat('SandWall', (0.34, 0.25, 0.13), rough=0.85, scale=4, bump=0.4)
for s in (-1, 1):
    w = plane((s * 3.6, 16, 2.0), 52, wallm, rot=(0, math.pi/2 * s, 0))
    w.scale = (1, 1, 0.09)
# columns with papyrus capitals
colm = stone_mat('Col', (0.4, 0.3, 0.16), rough=0.8, scale=5, bump=0.35)
goldb = plain_metal('GoldBand', (0.7, 0.5, 0.14), 0.3)
for s in (-1, 1):
    for i in range(13):
        y = -4 + i * 3.4
        cyl((s * 2.9, y, 1.7), 0.42, 3.4, colm, verts=24)
        cp = cyl((s * 2.9, y, 3.55), 0.62, 0.45, colm, verts=24)
        cp.scale = (1, 1, 1)
        cyl((s * 2.9, y, 3.25), 0.45, 0.14, goldb, verts=24)
# ceiling
plane((0, 16, 4.0), 52, stone_mat('Ceil2', (0.22, 0.16, 0.09), rough=0.9, scale=4, bump=0.3), rot=(math.pi, 0, 0))
# light shafts: warm sun beams via spot-like area lights from ceiling gaps
for i in range(6):
    y = 0 + i * 6.5
    area_light((0.8, y, 3.9), 550, 1.4, (1, 0.8, 0.45), (math.radians(12), 0, 0))
# far glow
plane((0, 41, 2), 9, emissive_mat('FarGlow2', (1, 0.75, 0.35), 1.9), rot=(math.pi/2, 0, 0))
point_light((0, -4, 3), 180, (1, 0.8, 0.5), 0.4)
corridor_cam()
render_to(os.path.join(OUT, 'bg_1.png'), 960, 540, samples=160)

print('BG1_V2_DONE')
