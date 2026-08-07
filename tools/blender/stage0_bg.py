# Stage 0 background: GRAND LIBRARY corridor (Trinity Long Room vibe)
FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())

import random
random.seed(7)

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\bgs\bg_0.png"

sc = reset_scene()

# ---- world: very dim warm ambient so nothing is pitch black
w = bpy.data.worlds.new('W')
w.use_nodes = True
bgn = w.node_tree.nodes['Background']
bgn.inputs[0].default_value = (0.02, 0.012, 0.007, 1)
bgn.inputs[1].default_value = 1.0
sc.world = w

# ---- materials
oak_dark  = wood_mat('OakDark',  tone=(0.10, 0.050, 0.022), grain_scale=8,  rough=0.5)
oak_shelf = wood_mat('OakShelf', tone=(0.15, 0.075, 0.032), grain_scale=10, rough=0.45)
parquet   = wood_mat('Parquet',  tone=(0.17, 0.090, 0.040), grain_scale=14, rough=0.26)
carpet    = fabric_mat('Carpet', tone=(0.50, 0.030, 0.045), rough=0.85)
brass     = metal_mat('Brass', tone=(0.88, 0.62, 0.25), rough=0.28)
trim_gold = gold_mat('TrimGold')

def solid_mat(name, col, rough=0.55):
    m, nt, b = _new_mat(name)
    b.inputs['Base Color'].default_value = (*col, 1)
    b.inputs['Roughness'].default_value = rough
    return m

BOOK_COLS = [
    (0.55, 0.05, 0.06), (0.42, 0.02, 0.10), (0.05, 0.30, 0.08),
    (0.02, 0.24, 0.16), (0.04, 0.08, 0.42), (0.02, 0.16, 0.46),
    (0.02, 0.30, 0.30), (0.62, 0.40, 0.05), (0.56, 0.20, 0.03),
    (0.26, 0.05, 0.36), (0.30, 0.12, 0.05), (0.70, 0.60, 0.42),
]

# template book meshes (one per colour) -> cheap data-API instancing
book_meshes = []
for i, col in enumerate(BOOK_COLS):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, -60, -20 - i))
    o = bpy.context.active_object
    o.name = 'BookTpl%d' % i
    o.data.materials.append(solid_mat('Book%d' % i, col))
    book_meshes.append(o.data)

def add_book(mesh, loc, scale):
    o = bpy.data.objects.new('bk', mesh)
    o.location = loc
    o.scale = scale
    bpy.context.scene.collection.objects.link(o)

def haze_mat(name, fac, strength=1.1, col=(1.0, 0.55, 0.25)):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    mix = nt.nodes.new('ShaderNodeMixShader')
    tr  = nt.nodes.new('ShaderNodeBsdfTransparent')
    em  = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = (*col, 1)
    em.inputs['Strength'].default_value = strength
    mix.inputs['Fac'].default_value = fac
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs['Surface'])
    return m

# ---- floor: dark parquet + red runner + gold trim
plane((0, 17, 0), 100, parquet, name='Floor')
cube((0, 17, 0.02), (2.3, 50, 0.04), carpet, name='Runner')
cube((-1.2, 17, 0.025), (0.09, 50, 0.05), trim_gold, name='TrimL')
cube(( 1.2, 17, 0.025), (0.09, 50, 0.05), trim_gold, name='TrimR')

# ---- bookshelf walls both sides
BOARD_Z = [0.15, 0.82, 1.49, 2.16, 2.83, 3.50]
for side in (-1, 1):
    sx = side
    cube((sx * 3.05, 17, 2.1), (0.10, 50, 4.4), oak_dark, name='BackWall')      # back wall
    cube((sx * 2.80, 17, 0.06), (0.42, 50, 0.12), oak_dark, name='Plinth')      # plinth
    cube((sx * 2.80, 17, 3.62), (0.52, 50, 0.18), oak_dark, name='Cornice')     # cornice
    cyl((sx * 2.52, 17, 3.44), 0.03, 46, trim_gold, rot=(math.radians(90), 0, 0), name='Rail')
    for zb in BOARD_Z:
        cube((sx * 2.85, 17, zb), (0.34, 46, 0.06), oak_shelf, name='Board')
    for k in range(16):
        yk = -6 + 3 * k
        cube((sx * 2.78, yk, 1.82), (0.24, 0.18, 3.64), oak_dark, name='Col')

# ---- BOOKS packed on every shelf
n_books = 0
ROW_BASE = [zb + 0.03 for zb in BOARD_Z[:-1]]
for side in (-1, 1):
    for zbase in ROW_BASE:
        y = -5.88
        while y < 39.4:
            wdt = random.uniform(0.09, 0.20) if y < 18 else random.uniform(0.18, 0.34)
            rem = (y + 6.0) % 3.0
            if rem < 0.12:
                y += 0.12 - rem
                continue
            if rem + wdt > 2.88:
                y += (3.0 - rem) + 0.12
                continue
            h = random.uniform(0.40, 0.58)
            mesh = random.choice(book_meshes)
            jx = random.uniform(-0.025, 0.02)
            add_book(mesh, (side * (2.84 + jx), y + wdt / 2, zbase + h / 2),
                     (0.26, wdt * 0.94, h))
            n_books += 1
            y += wdt + random.uniform(0.002, 0.015)
print('BOOKS:', n_books)

# ---- arched wooden ceiling: barrel vault + ribs + ridge beam
cyl((0, 17, -0.4), 5.0, 50, oak_dark, rot=(math.radians(90), 0, 0), verts=48, name='Vault')
for k in range(16):
    yk = -6 + 3 * k
    bpy.ops.mesh.primitive_torus_add(major_radius=5.0, minor_radius=0.09,
                                     location=(0, yk, -0.4),
                                     rotation=(math.radians(90), 0, 0),
                                     major_segments=64, minor_segments=8)
    rib = bpy.context.active_object
    rib.name = 'Rib%d' % k
    rib.data.materials.append(oak_shelf)
cube((0, 17, 4.52), (0.16, 50, 0.12), oak_shelf, name='Ridge')

# ---- hanging brass lamps receding down the hall
bulb_mat = emissive_mat('Bulb', color=(1.0, 0.72, 0.35), strength=20)
ly = 1.5
lamp_ys = []
while ly < 38:
    lamp_ys.append(ly)
    ly += 4.0
for yk in lamp_ys:
    cyl((0, yk, 3.95), 0.015, 1.3, brass, name='Chain')
    cyl((0, yk, 3.32), 0.16, 0.10, brass, name='Shade')
    sphere((0, yk, 3.18), 0.10, bulb_mat, name='Bulb')
    point_light((0, yk, 2.96), energy=70, color=(1, 0.72, 0.38), radius=0.12)

# ---- far end: warm glowing vanishing point
cube((0, 41.8, 2.3), (6.4, 0.3, 5.2), oak_dark, name='FarWall')
fw = plane((0, 41.5, 2.4), 1, emissive_mat('FarGlow', color=(1.0, 0.62, 0.28), strength=4.5),
           rot=(math.radians(90), 0, 0), name='FarWindow')
fw.scale = (2.2, 1.9, 1)
area_light((0, 38.0, 2.4), 2000, 5.0, (1.0, 0.62, 0.30), rot=(math.radians(-90), 0, 0))

# ---- depth haze cards (increasing warm fog toward far end)
for i, (yc, fac) in enumerate([(12, 0.05), (18, 0.07), (24, 0.10), (30, 0.13), (36, 0.17)]):
    hp = plane((0, yc, 2.0), 1, haze_mat('Haze%d' % i, fac), rot=(math.radians(90), 0, 0),
               name='Haze%d' % i)
    hp.scale = (4.5, 2.9, 1)

# ---- key + fill
area_light((0, -5.0, 4.0), 350, 3.0, (1.0, 0.88, 0.70), rot=(0, 0, 0))                      # warm key over foreground
area_light((0, -7.6, 2.0), 130, 4.0, (0.68, 0.78, 1.0), rot=(math.radians(90), 0, 0))       # cool fill down the hall

# ---- camera: one-point perspective matching game projection
cam = persp_cam((0, -6, 1.5), (math.radians(90), 0, 0), lens=24)
cam.data.shift_y = 0.09
cam.data.clip_end = 300

sc.cycles.transparent_max_bounces = 24

render_to(OUT, 960, 540, transparent=False, samples=160)
