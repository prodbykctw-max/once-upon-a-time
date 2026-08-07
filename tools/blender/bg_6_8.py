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

# ═══ BG 6: ARMORY hall ═══
sc = reset_scene()
random.seed(76)
flag = stone_mat('Flagstone', (0.13, 0.135, 0.14), rough=0.8, scale=5, bump=0.4)
plane((0, 16, 0), 52, flag)
wallm = stone_mat('Granite', (0.15, 0.155, 0.17), rough=0.85, scale=4, bump=0.5)
for s in (-1, 1):
    w = plane((s * 3.3, 16, 2.0), 52, wallm, rot=(0, math.pi/2 * s, 0))
    w.scale = (1, 1, 0.085)
plane((0, 16, 4.0), 52, wood_mat('CeilBeams', (0.07, 0.045, 0.025), grain_scale=3, rough=0.7), rot=(math.pi, 0, 0))
beam = wood_mat('Beam', (0.09, 0.05, 0.03), grain_scale=3, rough=0.6)
plate = plain_metal('Plate', (0.4, 0.41, 0.46), 0.3)
dark = plain_metal('DarkIron', (0.05, 0.05, 0.06), 0.55)
red = fabric_mat('Banner', (0.3, 0.03, 0.05), rough=0.9)
goldb = plain_metal('GoldB', (0.6, 0.42, 0.12), 0.35)
for i in range(13):
    y = -4 + i * 3.4
    cube((0, y, 3.85), (6.6, 0.35, 0.3), beam)
for s in (-1, 1):
    for i in range(12):
        y = -2.5 + i * 3.4
        # armor suits on plinths
        cyl((s * 2.8, y, 0.15), 0.3, 0.3, dark, verts=24)
        for ss in (-1, 1):
            cyl((s * 2.8 + ss * 0.1, y, 0.7), 0.06, 0.7, plate, verts=14)
        sphere((s * 2.8, y, 1.25), 0.23, plate)  # torso
        for ss in (-1, 1):
            sphere((s * 2.8 + ss * 0.26, y, 1.42), 0.1, plate)
        h = sphere((s * 2.8, y, 1.66), 0.13, plate); h.scale = (0.9, 1, 1.15)
        # torch between suits
        ty = y + 1.7
        cyl((s * 3.15, ty, 2.2), 0.02, 0.4, dark, rot=(0, math.radians(-18) * s, 0))
        fl = sphere((s * 3.05, ty, 2.45), 0.09, emissive_mat(f'Fl{s}{i}', (1, 0.5, 0.14), 11))
        fl.scale = (1, 1, 1.5)
        point_light((s * 2.95, ty, 2.45), 210, (1, 0.55, 0.2), 0.2)
# banners overhead
for i in range(6):
    y = 0 + i * 6.5
    b = cube((0, y, 3.3), (0.9, 0.06, 1.1), red)
    cube((0, y, 3.9), (1.0, 0.08, 0.08), goldb)
plane((0, 41, 2), 9, emissive_mat('FarGlow6', (1, 0.6, 0.3), 1.9), rot=(math.pi/2, 0, 0))
corridor_cam()
render_to(os.path.join(OUT, 'bg_6.png'), 960, 540, samples=160)

# ═══ BG 7: ART GALLERY grande galerie ═══
sc = reset_scene()
random.seed(87)
pq = wood_mat('Parquet', (0.3, 0.19, 0.09), grain_scale=10, rough=0.3)
plane((0, 16, 0), 52, pq)
burg = fabric_mat('BurgWall', (0.13, 0.015, 0.035), rough=0.85)
for s in (-1, 1):
    w = plane((s * 3.4, 16, 2.0), 52, burg, rot=(0, math.pi/2 * s, 0))
    w.scale = (1, 1, 0.085)
goldf = plain_metal('GoldF', (0.65, 0.47, 0.12), 0.3)
random.seed(78)
palettes = [((0.35, 0.06, 0.02), (0.5, 0.28, 0.05), (0.1, 0.12, 0.3)),
            ((0.05, 0.15, 0.3), (0.3, 0.35, 0.4), (0.5, 0.4, 0.2)),
            ((0.1, 0.25, 0.08), (0.35, 0.3, 0.1), (0.06, 0.1, 0.2)),
            ((0.3, 0.1, 0.2), (0.45, 0.3, 0.15), (0.1, 0.05, 0.15))]
for s in (-1, 1):
    for i in range(12):
        y = -3 + i * 3.5
        pw, ph = (1.1, 0.85) if (i % 2 == 0) else (0.8, 1.05)
        # canvas with per-painting palette
        cv = bpy.data.materials.new(f'Cv{s}{i}'); cv.use_nodes = True
        cb = cv.node_tree.nodes['Principled BSDF']; cb.inputs['Roughness'].default_value = 0.6
        ntc = cv.node_tree
        tcn = ntc.nodes.new('ShaderNodeTexCoord')
        nn = ntc.nodes.new('ShaderNodeTexNoise')
        nn.inputs['Scale'].default_value = random.uniform(1.5, 3.5)
        nn.inputs['Detail'].default_value = 7
        ntc.links.new(tcn.outputs['Object'], nn.inputs['Vector'])
        rmp = ntc.nodes.new('ShaderNodeValToRGB')
        p = palettes[random.randint(0, 3)]
        rmp.color_ramp.elements[0].position = 0.3; rmp.color_ramp.elements[0].color = (*p[0], 1)
        em = rmp.color_ramp.elements.new(0.5); em.color = (*p[1], 1)
        rmp.color_ramp.elements[-1].color = (*p[2], 1)
        ntc.links.new(nn.outputs['Fac'], rmp.inputs['Fac'])
        ntc.links.new(rmp.outputs['Color'], cb.inputs['Base Color'])
        cp = plane((s * 3.36, y, 1.9), 1, cv, rot=(0, math.pi/2 * s, 0), name=f'P{s}{i}')
        cp.scale = (pw * 2, ph * 2, 1)
        # gold frame bars
        for dz in (-ph - 0.05, ph + 0.05):
            cube((s * 3.34, y, 1.9 + dz), (0.05, pw * 2 + 0.2, 0.1), goldf)
        for dy in (-pw - 0.05, pw + 0.05):
            cube((s * 3.34, y + dy, 1.9), (0.05, 0.1, ph * 2), goldf)
        point_light((s * 2.9, y, 2.9), 60, (1, 0.9, 0.7), 0.15)
# skylight ribbon ceiling
plane((0, 16, 4.05), 52, stone_mat('Ceil7', (0.28, 0.26, 0.23), rough=0.7, scale=3, bump=0.1), rot=(math.pi, 0, 0))
cube((0, 16, 4.0), (2.4, 48, 0.06), emissive_mat('Sky7', (1, 0.95, 0.85), 3.0))
plane((0, 41, 2), 9, emissive_mat('FarGlow7', (1, 0.9, 0.7), 2.4), rot=(math.pi/2, 0, 0))
corridor_cam()
render_to(os.path.join(OUT, 'bg_7.png'), 960, 540, samples=160)

# ═══ BG 8: TREASURE VAULT hall ═══
sc = reset_scene()
random.seed(98)
obs = marble_mat('Obsidian', (0.03, 0.03, 0.05), (0.08, 0.06, 0.12), rough=0.07)
plane((0, 16, 0), 52, obs)
darkw = stone_mat('VaultWall', (0.04, 0.04, 0.06), rough=0.5, scale=4, bump=0.3)
for s in (-1, 1):
    w = plane((s * 3.3, 16, 2.0), 52, darkw, rot=(0, math.pi/2 * s, 0))
    w.scale = (1, 1, 0.085)
plane((0, 16, 4.0), 52, darkw, rot=(math.pi, 0, 0))
gold = plain_metal('Gold8', (0.75, 0.53, 0.14), 0.3)
colm = stone_mat('Col8', (0.05, 0.05, 0.075), rough=0.45, scale=4, bump=0.25)
for s in (-1, 1):
    for i in range(13):
        y = -4 + i * 3.4
        cyl((s * 2.9, y, 2.0), 0.3, 4.0, colm, verts=24)
        for z in (0.7, 2.0, 3.3):
            cyl((s * 2.9, y, z), 0.33, 0.12, gold, verts=24)
        # gold piles between columns
        py = y + 1.7
        random.seed(i * 7 + (0 if s < 0 else 50))
        for k in range(14):
            a = random.uniform(0, math.pi * 2); r = random.uniform(0, 0.45)
            gx = s * 2.75 + math.cos(a) * r * 0.4
            gy = py + math.sin(a) * r
            gz = 0.03 + (0.45 - r) * 0.4
            c = cyl((gx, gy, gz), random.uniform(0.05, 0.08), 0.02, gold, verts=14)
            c.rotation_euler = (random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5), 0)
        sphere((s * 2.7, py, 0.32), 0.12, gold)
        # glowing gem accents
        col = [(0.7, 0.05, 0.1), (0.05, 0.55, 0.2), (0.35, 0.05, 0.6)][i % 3]
        g = bpy.data.materials.new(f'Gm{s}{i}'); g.use_nodes = True
        gb = g.node_tree.nodes['Principled BSDF']
        gb.inputs['Base Color'].default_value = (*col, 1)
        gb.inputs['Emission Color'].default_value = (*col, 1)
        gb.inputs['Emission Strength'].default_value = 4
        sphere((s * 2.6, py + 0.2, 0.5), 0.06, g)
# god rays: emissive shafts + warm lights from ceiling gaps
for i in range(6):
    y = 1 + i * 6.4
    sh = cube((-0.6, y, 2.2), (0.7, 0.4, 3.6), emissive_mat(f'Ray{i}', (1, 0.8, 0.4), 0.5))
    sh.rotation_euler = (0, math.radians(-7), 0)
    area_light((-0.6, y, 3.9), 420, 1.2, (1, 0.78, 0.35), (math.radians(10), 0, 0))
plane((0, 41, 2), 9, emissive_mat('FarGlow8', (1, 0.75, 0.3), 2.6), rot=(math.pi/2, 0, 0))
corridor_cam()
render_to(os.path.join(OUT, 'bg_8.png'), 960, 540, samples=160)
print('BG_6_8_DONE')
