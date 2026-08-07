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

# ═══ BG 0: GRAND LIBRARY hall ═══
sc = reset_scene()
random.seed(10)
floor_m = wood_mat('Parquet', (0.16, 0.09, 0.045), grain_scale=10, rough=0.35)
plane((0, 16, 0), 52, floor_m)
carpet = fabric_mat('Carpet', (0.28, 0.03, 0.05), rough=0.9)
c = cube((0, 16, 0.012), (2.4, 48, 0.02), carpet)
gold_trim = plain_metal('CTrim', (0.6, 0.44, 0.12), 0.35)
for s in (-1, 1):
    cube((s * 1.25, 16, 0.015), (0.1, 48, 0.02), gold_trim)
# bookshelf walls: repeated bays
wood = wood_mat('Shelf', (0.17, 0.1, 0.05), grain_scale=4, rough=0.5)
random.seed(11)
book_cols = [(0.35, 0.06, 0.05), (0.06, 0.16, 0.3), (0.3, 0.24, 0.05), (0.05, 0.24, 0.1), (0.26, 0.08, 0.24), (0.3, 0.18, 0.06)]
for s in (-1, 1):
    for bay in range(14):
        y = -4 + bay * 3.2
        # shelf frame
        cube((s * 3.0, y, 1.9), (0.35, 3.0, 3.8), wood, name=f'Bay{s}{bay}')
        # shelf rows of books (front face toward lane)
        for row in range(5):
            z = 0.5 + row * 0.72
            x = s * 2.78
            yy = y - 1.3
            while yy < y + 1.3:
                bw = random.uniform(0.12, 0.24)
                bh = random.uniform(0.42, 0.58)
                col = book_cols[random.randint(0, 5)]
                br = random.uniform(0.75, 1.3)
                mat = fabric_mat(f'Bk{s}{bay}{row}{int(yy*10)}', tuple(min(1, cc * br) for cc in col), rough=0.7)
                cube((x, yy + bw/2, z + bh/2), (0.18, bw - 0.02, bh), mat)
                yy += bw + 0.01
# ceiling: dark wood with beams
ceil = wood_mat('Ceil', (0.1, 0.06, 0.03), grain_scale=3, rough=0.6)
plane((0, 16, 4.0), 52, ceil, rot=(math.pi, 0, 0))
for bay in range(14):
    y = -4 + bay * 3.2
    cube((0, y, 3.9), (6.4, 0.3, 0.25), wood)
# hanging brass lamps + warm light
for bay in range(12):
    y = -2 + bay * 3.4
    cyl((0, y, 3.6), 0.02, 0.6, gold_trim)
    sphere((0, y, 3.25), 0.16, emissive_mat(f'Lamp{bay}', (1, 0.75, 0.4), 14))
    point_light((0, y, 3.0), 320, (1, 0.72, 0.4), 0.25)
# far glow
plane((0, 41, 2), 9, emissive_mat('FarGlow', (1, 0.8, 0.5), 2.4), rot=(math.pi/2, 0, 0))
corridor_cam()
render_to(os.path.join(OUT, 'bg_0.png'), 960, 540, samples=160)

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
    sh = cube((0.8, y, 2.0), (1.0, 0.5, 3.9), emissive_mat(f'Shaft{i}', (1, 0.85, 0.55), 0.55))
    sh.rotation_euler = (0, math.radians(8), 0)
# far glow
plane((0, 41, 2), 9, emissive_mat('FarGlow2', (1, 0.75, 0.35), 2.6), rot=(math.pi/2, 0, 0))
point_light((0, -4, 3), 180, (1, 0.8, 0.5), 0.4)
corridor_cam()
render_to(os.path.join(OUT, 'bg_1.png'), 960, 540, samples=160)

# ═══ BG 2: SAMURAI temple corridor ═══
sc = reset_scene()
random.seed(32)
dkwood = wood_mat('DarkFloor', (0.08, 0.045, 0.025), grain_scale=12, rough=0.18)
plane((0, 16, 0), 52, dkwood)
beam = wood_mat('Beam', (0.09, 0.05, 0.028), grain_scale=4, rough=0.55)
lacq = fabric_mat('Lacquer', (0.3, 0.02, 0.02), rough=0.25)
shoji_glow = emissive_mat('Shoji', (1, 0.92, 0.75), 1.7)
frame_dark = wood_mat('Frame', (0.06, 0.035, 0.02), grain_scale=3, rough=0.6)
for s in (-1, 1):
    for i in range(13):
        y = -4 + i * 3.4
        # glowing shoji panel with lattice
        p = plane((s * 3.1, y, 1.7), 1, shoji_glow, rot=(0, math.pi/2 * s, 0), name=f'Sh{s}{i}')
        p.scale = (2.6, 2.6, 1)
        for k in range(4):
            cube((s * 3.05, y - 1.3 + k * 0.87, 1.7), (0.04, 0.06, 2.6), frame_dark)
        for k in range(4):
            cube((s * 3.05, y, 0.45 + k * 0.85), (0.04, 2.6, 0.06), frame_dark)
        # red lacquer pillar between panels
        cyl((s * 2.95, y + 1.7, 1.9), 0.16, 3.8, lacq, verts=20)
# floor reflections come free from rough 0.18
# ceiling beams
plane((0, 16, 3.9), 52, frame_dark, rot=(math.pi, 0, 0))
for i in range(13):
    y = -4 + i * 3.4
    cube((0, y, 3.75), (6.4, 0.35, 0.3), beam)
# paper lanterns down the center
for i in range(11):
    y = -2 + i * 3.8
    cyl((0, y, 3.4), 0.02, 0.5, frame_dark)
    lt = sphere((0, y, 3.0), 0.22, emissive_mat(f'Lant{i}', (1, 0.65, 0.3), 9))
    lt.scale = (1, 1, 1.25)
    point_light((0, y, 2.8), 260, (1, 0.6, 0.3), 0.3)
plane((0, 41, 2), 9, emissive_mat('FarGlow3', (1, 0.5, 0.25), 2.2), rot=(math.pi/2, 0, 0))
corridor_cam()
render_to(os.path.join(OUT, 'bg_2.png'), 960, 540, samples=160)
print('BG_0_2_DONE')
