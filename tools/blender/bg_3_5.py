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

# ═══ BG 3: ROYAL hall of mirrors ═══
sc = reset_scene()
random.seed(43)
marbf = marble_mat('MarbleFloor', (0.5, 0.49, 0.47), (0.28, 0.27, 0.29), rough=0.06)
plane((0, 16, 0), 52, marbf)
goldm = plain_metal('Gold', (0.72, 0.52, 0.14), 0.25)
# gold inlay lines
for s in (-1, 1):
    cube((s * 1.4, 16, 0.008), (0.08, 48, 0.012), goldm)
wallm = marble_mat('WallM', (0.42, 0.4, 0.37), (0.25, 0.24, 0.25), rough=0.4)
for s in (-1, 1):
    w = plane((s * 3.4, 16, 2.0), 52, wallm, rot=(0, math.pi/2 * s, 0))
    w.scale = (1, 1, 0.085)
mirror = plain_metal('Mirror', (0.85, 0.87, 0.92), 0.04)
drape = fabric_mat('Drape', (0.14, 0.03, 0.22), rough=0.9)
for s in (-1, 1):
    for i in range(12):
        y = -3 + i * 3.6
        # arched mirror: rect + circle top
        mplane = plane((s * 3.3, y, 1.6), 1, mirror, rot=(0, math.pi/2 * s, 0), name=f'Mir{s}{i}')
        mplane.scale = (1.5, 1.5, 1)  # 1.5 wide 1.5 tall wait scale xy
        mp2 = cyl((s * 3.3, y, 2.35), 0.75, 0.02, mirror, rot=(0, math.pi/2, 0), verts=32)
        # gold frame sides
        for dy in (-0.78, 0.78):
            cube((s * 3.28, y + dy, 1.55), (0.05, 0.09, 1.6), goldm)
        cube((s * 3.28, y, 0.72), (0.05, 1.62, 0.09), goldm)
        # purple drape between mirrors
        d = cube((s * 3.25, y + 1.8, 2.0), (0.12, 0.5, 3.6), drape)
# ceiling: pale with gold ribs
plane((0, 16, 4.0), 52, marble_mat('Ceil', (0.5, 0.48, 0.44), (0.35, 0.33, 0.32), rough=0.5), rot=(math.pi, 0, 0))
for i in range(12):
    y = -3 + i * 3.6
    cube((0, y, 3.92), (6.8, 0.14, 0.12), goldm)
# crystal chandeliers
for i in range(9):
    y = -1 + i * 4.4
    cyl((0, y, 3.7), 0.02, 0.55, goldm)
    core = sphere((0, y, 3.3), 0.2, emissive_mat(f'ChCore{i}', (1, 0.85, 0.6), 10))
    random.seed(100 + i)
    for k in range(10):
        a = k / 10 * math.pi * 2
        sphere((math.cos(a) * 0.3, y + math.sin(a) * 0.3, 3.22 + (k % 3) * 0.08), 0.045, plain_metal(f'Cr{i}{k}', (0.9, 0.93, 1), 0.03))
    point_light((0, y, 3.1), 380, (1, 0.83, 0.55), 0.3)
plane((0, 41, 2), 9, emissive_mat('FarGlow', (1, 0.85, 0.6), 2.8), rot=(math.pi/2, 0, 0))
corridor_cam()
render_to(os.path.join(OUT, 'bg_3.png'), 960, 540, samples=160)

# ═══ BG 4: MUSEUM gallery ═══
sc = reset_scene()
random.seed(54)
# checkerboard floor
darkt = marble_mat('DarkTile', (0.08, 0.08, 0.1), (0.16, 0.15, 0.18), rough=0.15)
lightt = marble_mat('LightTile', (0.45, 0.44, 0.42), (0.3, 0.29, 0.3), rough=0.15)
plane((0, 16, -0.005), 52, darkt)
for gx in range(-3, 4):
    for gy in range(-4, 30):
        if (gx + gy) % 2 == 0:
            cube((gx * 1.0, gy * 1.6, 0.004), (0.98, 1.58, 0.008), lightt)
wallm = stone_mat('Ashlar', (0.4, 0.38, 0.34), rough=0.7, scale=3, bump=0.15)
for s in (-1, 1):
    w = plane((s * 3.5, 16, 2.0), 52, wallm, rot=(0, math.pi/2 * s, 0))
    w.scale = (1, 1, 0.085)
# pilasters
pil = stone_mat('Pilaster', (0.48, 0.46, 0.42), rough=0.6, scale=2, bump=0.1)
for s in (-1, 1):
    for i in range(13):
        y = -4 + i * 3.4
        cube((s * 3.35, y, 1.9), (0.3, 0.5, 3.8), pil)
        cube((s * 3.3, y, 3.7), (0.42, 0.7, 0.2), pil)
# display cases along walls
glassf = plain_metal('CaseFrame', (0.1, 0.1, 0.12), 0.4)
for s in (-1, 1):
    for i in range(12):
        y = -2.5 + i * 3.4
        cube((s * 2.85, y, 0.5), (0.5, 0.7, 1.0), stone_mat(f'Ped{s}{i}', (0.09, 0.09, 0.11), rough=0.6, scale=2, bump=0.05))
        # artifact: small gold or terracotta piece
        if (i + (0 if s < 0 else 1)) % 2 == 0:
            sphere((s * 2.85, y, 1.18), 0.13, plain_metal(f'Art{s}{i}', (0.7, 0.5, 0.15), 0.3))
        else:
            a = sphere((s * 2.85, y, 1.2), 0.13, stone_mat(f'Amp{s}{i}', (0.3, 0.14, 0.08), rough=0.5, scale=3, bump=0.1))
            a.scale = (1, 1, 1.3)
        point_light((s * 2.85, y, 1.6), 40, (1, 0.9, 0.75), 0.1)
# skylight ceiling: emissive ribbon
plane((0, 16, 4.0), 52, stone_mat('Ceil4', (0.3, 0.29, 0.27), rough=0.8, scale=3, bump=0.1), rot=(math.pi, 0, 0))
sky = cube((0, 16, 3.96), (2.2, 48, 0.05), emissive_mat('Skylight', (0.9, 0.93, 1), 3.2))
plane((0, 41, 2), 9, emissive_mat('FarGlow4', (0.85, 0.9, 1), 2.2), rot=(math.pi/2, 0, 0))
corridor_cam()
render_to(os.path.join(OUT, 'bg_4.png'), 960, 540, samples=160)

# ═══ BG 5: TECH MANOR hall ═══
sc = reset_scene()
random.seed(65)
deck = plain_metal('Deck', (0.045, 0.05, 0.065), 0.45)
plane((0, 16, 0), 52, deck)
blue = emissive_mat('Blue', (0.15, 0.55, 1), 6)
# glowing floor seams
for s in (-1, 1):
    cube((s * 1.5, 16, 0.005), (0.05, 48, 0.01), blue)
    cube((s * 2.9, 16, 0.005), (0.04, 48, 0.01), blue)
for i in range(24):
    y = -4 + i * 1.9
    cube((0, y, 0.004), (5.8, 0.03, 0.008), plain_metal(f'Seam{i}', (0.09, 0.1, 0.13), 0.4))
wallm = plain_metal('SteelWall', (0.07, 0.075, 0.1), 0.5)
for s in (-1, 1):
    w = plane((s * 3.3, 16, 2.0), 52, wallm, rot=(0, math.pi/2 * s, 0))
    w.scale = (1, 1, 0.085)
# steel rib arches + wall LED strips
rib = plain_metal('Rib', (0.1, 0.11, 0.14), 0.35)
for i in range(13):
    y = -4 + i * 3.4
    cube((-3.2, y, 2.0), (0.25, 0.4, 4.0), rib)
    cube((3.2, y, 2.0), (0.25, 0.4, 4.0), rib)
    cube((0, y, 3.85), (6.6, 0.4, 0.3), rib)
    # blue ring light on each rib
    cube((-3.05, y, 2.0), (0.04, 0.12, 3.6), blue)
    cube((3.05, y, 2.0), (0.04, 0.12, 3.6), blue)
    point_light((0, y, 3.2), 130, (0.25, 0.55, 1), 0.3)
plane((0, 16, 4.1), 52, plain_metal('Ceil5', (0.04, 0.045, 0.06), 0.5), rot=(math.pi, 0, 0))
# far core glow
plane((0, 41, 2), 9, emissive_mat('FarGlow5', (0.2, 0.6, 1), 3.2), rot=(math.pi/2, 0, 0))
sphere((0, 39, 2), 0.8, emissive_mat('Core', (0.5, 0.8, 1), 8))
corridor_cam()
render_to(os.path.join(OUT, 'bg_5.png'), 960, 540, samples=160)
print('BG_3_5_DONE')
