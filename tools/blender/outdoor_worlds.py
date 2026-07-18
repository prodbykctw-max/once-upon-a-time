import bpy, math, os, random, sys
FRAMEWORK = r"C:\Users\Owner\Documents\once-upon-a-time\tools\blender\framework.py"
exec(open(FRAMEWORK).read())
OUT = r"C:\Users\Owner\Documents\once-upon-a-time\assets\renders\bgs"
os.makedirs(OUT, exist_ok=True)
ONLY = None
for a in sys.argv:
    if a.startswith('--only='): ONLY = [int(x) for x in a.split('=')[1].split(',')]

# ══ REAL OUTDOOR WORLDS — no walls, open sky, scenery recedes to horizon ══
# Camera matches the game projection (VP ~34% from top, center lane open).

def corridor_cam():
    cam = persp_cam((0, -6, 1.5), (math.radians(90), 0, 0), lens=24)
    cam.data.shift_y = 0.09
    return cam

def sky_world(top, horizon, strength=1.0):
    w = bpy.data.worlds.new('W'); bpy.context.scene.world = w; w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes['Background']
    bg.inputs['Strength'].default_value = strength
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    nt.links.new(tc.outputs['Window'], mp.inputs[0])
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(mp.outputs[0], sep.inputs[0])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.30
    ramp.color_ramp.elements[0].color = (*horizon, 1)
    ramp.color_ramp.elements[1].position = 0.9
    ramp.color_ramp.elements[1].color = (*top, 1)
    nt.links.new(sep.outputs['Y'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])

def sun(rot=(50, 0, -30), energy=4.0, color=(1, 0.95, 0.85), angle=2.0):
    ld = bpy.data.lights.new('Sun', 'SUN')
    ld.energy = energy; ld.color = color; ld.angle = math.radians(angle)
    lo = bpy.data.objects.new('Sun', ld)
    bpy.context.scene.collection.objects.link(lo)
    lo.rotation_euler = tuple(math.radians(v) for v in rot)

def ground(mat, size=220):
    g = plane((0, 60, 0), size, mat)
    return g

def path(mat, width=2.8):
    p = cube((0, 60, 0.012), (width, 200, 0.02), mat)
    return p

def grass_mat(tone=(0.13, 0.30, 0.08)):
    return stone_mat('Grass', tone, rough=0.9, scale=18, bump=0.25)

def sparkles(n=26, area_x=8, y0=-2, y1=40, z0=0.3, z1=3.4, color=(1, 0.95, 0.6), strength=5, seed=1):
    random.seed(seed)
    m = emissive_mat('Sparkle', color, strength)
    for i in range(n):
        sphere((random.uniform(-area_x, area_x), random.uniform(y0, y1),
                random.uniform(z0, z1)), random.uniform(0.015, 0.04), m)

def birds(n=6, seed=2, color=(0.12, 0.1, 0.12)):
    random.seed(seed)
    m = fabric_mat('Bird', color, rough=0.9)
    for i in range(n):
        bx = random.uniform(-7, 7); by = random.uniform(6, 34); bz = random.uniform(2.6, 4.4)
        for sgn in (-1, 1):
            wq = cube((bx + sgn * 0.10, by, bz), (0.2, 0.02, 0.035), m,
                      rot=(0, math.radians(25 * sgn * random.choice([1, 1.4])), 0))

def fountain(x, y, scale=1.0):
    marble = marble_mat('FMarble', (0.72, 0.71, 0.68), (0.5, 0.5, 0.52), rough=0.3)
    water = bpy.data.materials.new('Water'); water.use_nodes = True
    wb = water.node_tree.nodes['Principled BSDF']
    wb.inputs['Base Color'].default_value = (0.45, 0.75, 0.9, 1)
    wb.inputs['Roughness'].default_value = 0.05
    wb.inputs['Transmission Weight'].default_value = 0.7
    cyl((x, y, 0.22 * scale), 1.05 * scale, 0.42 * scale, marble, verts=28)
    cyl((x, y, 0.44 * scale), 0.92 * scale, 0.06 * scale, water, verts=28)
    cyl((x, y, 0.7 * scale), 0.14 * scale, 0.9 * scale, marble, verts=16)
    cyl((x, y, 1.18 * scale), 0.5 * scale, 0.09 * scale, marble, verts=24)
    cyl((x, y, 1.24 * scale), 0.42 * scale, 0.05 * scale, water, verts=24)
    cyl((x, y, 1.45 * scale), 0.09 * scale, 0.45 * scale, marble, verts=12)
    sphere((x, y, 1.72 * scale), 0.16 * scale, water)
    # spray sparkle
    sm = emissive_mat('Spray', (0.8, 0.95, 1), 2.5)
    random.seed(int(x * 10 + y))
    for i in range(7):
        sphere((x + random.uniform(-0.3, 0.3) * scale, y + random.uniform(-0.3, 0.3) * scale,
                (1.5 + random.uniform(0, 0.5)) * scale), 0.03 * scale, sm)

def statue(x, y, scale=1.0):
    marble = marble_mat('SMarble', (0.68, 0.67, 0.64), (0.48, 0.48, 0.5), rough=0.35)
    cube((x, y, 0.35 * scale), (0.6 * scale, 0.6 * scale, 0.7 * scale), marble)
    cyl((x, y, 1.0 * scale), 0.16 * scale, 0.6 * scale, marble, verts=14)
    s = sphere((x, y, 1.5 * scale), 0.3 * scale, marble); s.scale = (0.75, 0.5, 1.1)
    sphere((x, y, 1.95 * scale), 0.14 * scale, marble)
    for sgn in (-1, 1):  # raised wings/arms
        wr = cube((x + sgn * 0.34 * scale, y, 1.65 * scale), (0.5 * scale, 0.06 * scale, 0.16 * scale), marble,
                  rot=(0, math.radians(-35 * sgn), 0))

def blossom_tree(x, y, scale=1.0, bloom=(0.98, 0.72, 0.82)):
    trunk = wood_mat('Trunk', (0.16, 0.09, 0.05), grain_scale=3, rough=0.8)
    cyl((x, y, 0.9 * scale), 0.13 * scale, 1.8 * scale, trunk, verts=10)
    bm = fabric_mat('Bloom', bloom, rough=0.85)
    random.seed(int(x * 7 + y))
    for i in range(7):
        sphere((x + random.uniform(-0.55, 0.55) * scale, y + random.uniform(-0.4, 0.4) * scale,
                (1.9 + random.uniform(0, 0.75)) * scale), random.uniform(0.4, 0.62) * scale, bm)

def leafy_tree(x, y, scale=1.0, leaf=(0.16, 0.36, 0.10)):
    blossom_tree(x, y, scale, bloom=leaf)

def hedge(x, y, w, d, h=0.7):
    m = stone_mat('Hedge', (0.10, 0.24, 0.07), rough=0.95, scale=14, bump=0.5)
    cube((x, y, h / 2), (w, d, h), m)

def sunflower(x, y, scale=1.0):
    st = fabric_mat('Stem', (0.12, 0.3, 0.06), rough=0.9)
    cyl((x, y, 0.55 * scale), 0.025 * scale, 1.1 * scale, st, verts=8)
    petal = emissive_mat('Petal', (0.95, 0.75, 0.12), 0.6)
    core = fabric_mat('Core', (0.25, 0.14, 0.04), rough=0.9)
    c = sphere((x, y - 0.03, 1.12 * scale), 0.13 * scale, core); c.scale = (1, 0.4, 1)
    for k in range(8):
        a = k / 8 * math.pi * 2
        p = sphere((x + math.cos(a) * 0.17 * scale, y - 0.02, 1.12 * scale + math.sin(a) * 0.17 * scale),
                   0.07 * scale, petal)
        p.scale = (1, 0.3, 0.55)

def mushroom(x, y, scale=1.0, cap=(0.85, 0.25, 0.3)):
    st = fabric_mat('MStem', (0.8, 0.76, 0.68), rough=0.8)
    cyl((x, y, 0.5 * scale), 0.16 * scale, 1.0 * scale, st, verts=12)
    cm = fabric_mat('MCap', cap, rough=0.6)
    c = sphere((x, y, 1.05 * scale), 0.55 * scale, cm); c.scale = (1, 1, 0.55)
    dm = fabric_mat('MDot', (0.95, 0.93, 0.88), rough=0.7)
    random.seed(int(x * 5 + y))
    for i in range(4):
        a = random.uniform(0, math.pi * 2); rr = random.uniform(0.1, 0.4) * scale
        sphere((x + math.cos(a) * rr, y + math.sin(a) * rr - 0.15, (1.2 + random.uniform(0, 0.1)) * scale), 0.07 * scale, dm)

def cloudpuff(x, y, z, scale=1.0):
    cm = fabric_mat('Cloud', (0.92, 0.93, 0.97), rough=1.0)
    random.seed(int(x * 3 + y))
    for i in range(5):
        s = sphere((x + random.uniform(-0.7, 0.7) * scale, y + random.uniform(-0.4, 0.4) * scale,
                    z + random.uniform(-0.15, 0.2) * scale), random.uniform(0.35, 0.6) * scale, cm)
        s.scale = (1.3, 1, 0.6)

def far_castle(y=46):
    m = stone_mat('Castle', (0.62, 0.60, 0.70), rough=0.7, scale=3, bump=0.1)
    roof = fabric_mat('Roof', (0.35, 0.5, 0.75), rough=0.6)
    for (cx2, w, h) in ((-3, 2.2, 5.5), (0, 3.2, 7.5), (3, 2.2, 5.5)):
        cube((cx2, y, h / 2), (w, 2, h), m)
        # cone roof
        bpy.ops.mesh.primitive_cone_add(radius1=w * 0.62, radius2=0.03, depth=2.4, location=(cx2, y, h + 1.2), vertices=12)
        r = bpy.context.active_object; r.data.materials.append(roof)

def render_world(i, path_out):
    bpy.context.scene.render.resolution_x = 960
    bpy.context.scene.render.resolution_y = 540
    bpy.context.scene.render.film_transparent = False
    render_to(path_out, 960, 540, transparent=False, samples=140)

def build(i):
    sc = reset_scene()
    random.seed(100 + i)
    if i == 0:
        # GRAND LIBRARY — the single interior: bright, sunny windows
        sky_world((0.55, 0.45, 0.35), (0.75, 0.65, 0.5), 0.6)
        wd = wood_mat('Floor0', (0.32, 0.2, 0.1), grain_scale=10, rough=0.35)
        plane((0, 60, 0), 220, wd)
        carpet = fabric_mat('Carpet', (0.55, 0.15, 0.25), rough=0.9)
        cube((0, 60, 0.012), (2.6, 200, 0.02), carpet)
        wood = wood_mat('Shelf', (0.26, 0.15, 0.075), grain_scale=4, rough=0.5)
        cols = [(0.75, 0.2, 0.18), (0.2, 0.4, 0.65), (0.75, 0.6, 0.15), (0.2, 0.55, 0.3), (0.6, 0.3, 0.6)]
        for s in (-1, 1):
            for b in range(12):
                y = -3 + b * 3.6
                cube((s * 3.1, y, 1.9), (0.4, 3.2, 3.8), wood)
                random.seed(b * 3 + s)
                for row in range(4):
                    z = 0.6 + row * 0.8
                    yy = y - 1.4
                    while yy < y + 1.4:
                        bw = random.uniform(0.14, 0.26)
                        col = cols[random.randint(0, 4)]
                        cube((s * 2.85, yy + bw / 2, z + 0.3), (0.2, bw - 0.02, 0.6),
                             fabric_mat(f'B{b}{row}{int(yy*9)}', col, rough=0.7))
                        yy += bw
        # sunbeam windows high on shelves + warm lamps
        for b in range(6):
            y = 1 + b * 7
            plane((0, y, 4.6), 2.2, emissive_mat(f'Sky0{b}', (1, 0.93, 0.8), 4), rot=(math.pi, 0, 0))
        sun((38, 0, 15), 2.2, (1, 0.9, 0.75))
        sparkles(18, 5, 0, 30, 0.5, 4, (1, 0.85, 0.5), 3, seed=5)
    elif i == 1:
        # SUNRISE MEADOW
        sky_world((0.45, 0.62, 0.95), (0.99, 0.75, 0.55), 1.1)
        ground(grass_mat((0.14, 0.32, 0.09)))
        path(stone_mat('Dirt', (0.42, 0.3, 0.17), rough=0.85, scale=8, bump=0.2))
        for s in (-1, 1):
            for k in range(10):
                y = -2 + k * 4.5
                leafy_tree(s * random.uniform(4.5, 8), y, random.uniform(0.8, 1.4))
        # wildflowers
        random.seed(11)
        for k in range(60):
            fx = random.uniform(-8, 8)
            if abs(fx) < 1.6: continue
            col = random.choice([(0.9, 0.4, 0.55), (0.95, 0.8, 0.2), (0.6, 0.5, 0.9), (0.95, 0.95, 0.9)])
            sphere((fx, random.uniform(-3, 35), 0.1), 0.07, emissive_mat(f'Fl{k}', col, 0.9))
        birds(7)
        sun((28, 0, 40), 4.5, (1, 0.85, 0.7))
        far_castle()
    elif i == 2:
        # CHERRY BLOSSOM LANE
        sky_world((0.55, 0.7, 0.95), (0.98, 0.85, 0.88), 1.05)
        ground(grass_mat((0.18, 0.34, 0.12)))
        path(stone_mat('Cobble', (0.6, 0.55, 0.52), rough=0.7, scale=14, bump=0.35))
        for s in (-1, 1):
            for k in range(9):
                blossom_tree(s * random.uniform(3.2, 5.5), -2 + k * 5, random.uniform(0.9, 1.3))
        # drifting petals
        random.seed(22)
        pm = fabric_mat('Petal2', (0.98, 0.75, 0.83), rough=0.8)
        for k in range(50):
            p = sphere((random.uniform(-6, 6), random.uniform(-3, 34), random.uniform(0.2, 3.6)), 0.045, pm)
            p.scale = (1, 0.5, 0.25)
        sun((45, 0, -20), 3.8, (1, 0.92, 0.85))
        sparkles(14, 6, 0, 30, 0.4, 3, (1, 0.85, 0.9), 2.5, seed=9)
    elif i == 3:
        # ROYAL ROSE GARDEN
        sky_world((0.4, 0.65, 0.98), (0.85, 0.92, 0.99), 1.1)
        ground(grass_mat((0.12, 0.3, 0.08)))
        path(stone_mat('White', (0.7, 0.68, 0.62), rough=0.6, scale=10, bump=0.2))
        for s in (-1, 1):
            hedge(s * 3.4, 60, 1.2, 200, 0.8)
            for k in range(7):
                y = 1 + k * 6
                fountain(s * 6.2, y, 0.85) if k % 2 == 0 else statue(s * 6.0, y, 0.9)
                # rose dots on hedge
                random.seed(k * 9 + s)
                rm = emissive_mat(f'Rose{s}{k}', (0.85, 0.12, 0.25), 1.2)
                for r in range(8):
                    sphere((s * random.uniform(2.9, 3.9), y + random.uniform(-2.5, 2.5), random.uniform(0.3, 0.85)), 0.07, rm)
        fountain(0, 42, 2.2)   # grand center fountain far ahead (lane splits around visually)
        birds(5)
        sun((40, 0, 10), 4.6)
    elif i == 4:
        # CRYSTAL LAKESIDE
        sky_world((0.42, 0.68, 0.95), (0.8, 0.92, 0.98), 1.05)
        ground(grass_mat((0.15, 0.33, 0.11)))
        path(stone_mat('Sand', (0.75, 0.66, 0.5), rough=0.8, scale=12, bump=0.15))
        water = bpy.data.materials.new('Lake'); water.use_nodes = True
        wb = water.node_tree.nodes['Principled BSDF']
        wb.inputs['Base Color'].default_value = (0.3, 0.6, 0.8, 1)
        wb.inputs['Roughness'].default_value = 0.04
        wb.inputs['Metallic'].default_value = 0.4
        plane((-14, 60, 0.02), 24, water)
        plane((14, 60, 0.02), 24, water)
        for k in range(8):
            leafy_tree(random.choice([-1, 1]) * random.uniform(3.4, 6.5), k * 5, random.uniform(0.9, 1.4), leaf=(0.2, 0.42, 0.18))
        # swans: white blobs with necks
        sw = fabric_mat('Swan', (0.95, 0.95, 0.92), rough=0.7)
        for k in range(4):
            sx = random.choice([-1, 1]) * random.uniform(9, 13); sy = random.uniform(6, 28)
            b = sphere((sx, sy, 0.14), 0.24, sw); b.scale = (1, 1.5, 0.8)
            cyl((sx, sy - 0.3, 0.4), 0.05, 0.5, sw, rot=(math.radians(15), 0, 0))
            sphere((sx, sy - 0.42, 0.62), 0.09, sw)
        sparkles(24, 12, 2, 34, 0.06, 0.5, (0.9, 1, 1), 3, seed=44)   # water glints
        birds(5)
        sun((36, 0, -25), 4.4)
        far_castle(48)
    elif i == 5:
        # FAIRY GLADE
        sky_world((0.2, 0.3, 0.55), (0.5, 0.65, 0.75), 0.85)
        ground(grass_mat((0.08, 0.24, 0.1)))
        path(stone_mat('Moss', (0.25, 0.35, 0.2), rough=0.9, scale=10, bump=0.3))
        for s in (-1, 1):
            for k in range(8):
                mushroom(s * random.uniform(3, 6), -1 + k * 5.2, random.uniform(0.7, 1.6),
                         cap=random.choice([(0.85, 0.25, 0.3), (0.6, 0.3, 0.75), (0.9, 0.6, 0.2)]))
            for k in range(5):
                leafy_tree(s * random.uniform(6, 9), 2 + k * 8, 1.6, leaf=(0.1, 0.28, 0.14))
        # fairies: bright glowing motes with tiny wings
        random.seed(55)
        for k in range(16):
            fx = random.uniform(-5, 5); fy = random.uniform(0, 30); fz = random.uniform(0.8, 3.2)
            col = random.choice([(1, 0.85, 0.4), (0.6, 0.9, 1), (1, 0.6, 0.9)])
            sphere((fx, fy, fz), 0.05, emissive_mat(f'Fairy{k}', col, 9))
            wm = fabric_mat(f'FW{k}', (0.9, 0.95, 1), rough=0.3)
            for sgn in (-1, 1):
                wq = cube((fx + sgn * 0.07, fy, fz), (0.09, 0.01, 0.05), wm, rot=(0, math.radians(30 * sgn), 0))
        sparkles(40, 6, 0, 32, 0.2, 3.6, (0.8, 1, 0.9), 4, seed=56)
        sun((55, 0, 30), 1.6, (0.7, 0.85, 1))
    elif i == 6:
        # SUNFLOWER FIELDS
        sky_world((0.35, 0.6, 0.97), (0.95, 0.93, 0.75), 1.15)
        ground(grass_mat((0.2, 0.36, 0.1)))
        path(stone_mat('Dirt6', (0.5, 0.38, 0.2), rough=0.85, scale=8, bump=0.2))
        for s in (-1, 1):
            for k in range(26):
                sunflower(s * random.uniform(2.4, 8.5), -2 + k * 1.6, random.uniform(0.8, 1.35))
        birds(8)
        # big visible sun disc low ahead
        plane((3, 55, 7), 6, emissive_mat('SunDisc', (1, 0.9, 0.55), 30), rot=(math.pi / 2, 0, 0))
        sun((30, 0, 5), 5.5, (1, 0.93, 0.7))
    elif i == 7:
        # CLOUD GARDENS
        sky_world((0.35, 0.55, 0.95), (0.85, 0.9, 1.0), 1.2)
        # marble sky-path over clouds
        marble = marble_mat('SkyPath', (0.8, 0.8, 0.82), (0.6, 0.62, 0.7), rough=0.25)
        cube((0, 60, -0.05), (4.2, 200, 0.1), marble)
        gold_r = gold_mat('Rail')
        for s in (-1, 1):
            cube((s * 2.0, 60, 0.5), (0.06, 200, 0.06), gold_r)
            for k in range(24):
                cyl((s * 2.0, k * 2.2, 0.25), 0.03, 0.5, gold_r, verts=8)
        for k in range(14):
            cloudpuff(random.choice([-1, 1]) * random.uniform(3.5, 9), k * 3.2, random.uniform(-0.6, 0.4), random.uniform(1, 2.2))
        for k in range(5):
            statue(random.choice([-1, 1]) * random.uniform(2.8, 3.4), 4 + k * 7, 0.8)
        # doves
        birds(7, seed=77, color=(0.95, 0.95, 0.98))
        sun((42, 0, -15), 4.8)
        sparkles(20, 6, 0, 34, 0.5, 3.5, (1, 1, 0.85), 3, seed=78)
    else:
        # SUNSET PALACE COURTYARD — the finale
        sky_world((0.45, 0.3, 0.55), (0.99, 0.55, 0.3), 1.15)
        marble = marble_mat('Court', (0.6, 0.5, 0.48), (0.4, 0.32, 0.34), rough=0.3)
        plane((0, 60, 0), 220, marble)
        path(gold_mat('GoldPath'), width=2.9)
        for s in (-1, 1):
            for k in range(6):
                y = 1 + k * 6.5
                if k % 2 == 0: fountain(s * 5.5, y, 1.0)
                else: statue(s * 5.2, y, 1.05)
            # rose columns
            for k in range(7):
                cyl((s * 3.3, k * 5.5, 1.3), 0.16, 2.6, marble, verts=14)
                sphere((s * 3.3, k * 5.5, 2.8), 0.3, emissive_mat(f'RoseTop{s}{k}', (0.9, 0.2, 0.3), 1.4))
        # palace ahead with warm windows
        far_castle(44)
        wm2 = emissive_mat('Win', (1, 0.75, 0.35), 6)
        random.seed(88)
        for k in range(10):
            cube((random.uniform(-3.5, 3.5), 43.6, random.uniform(1.5, 6)), (0.3, 0.05, 0.5), wm2)
        # sunset sun disc
        plane((0, 58, 5.5), 8, emissive_mat('Sunset', (1, 0.6, 0.3), 22), rot=(math.pi / 2, 0, 0))
        sun((18, 0, 0), 3.8, (1, 0.6, 0.4))
        sparkles(26, 7, 0, 32, 0.3, 3.5, (1, 0.8, 0.5), 4, seed=89)
        birds(4, seed=90)
    corridor_cam()
    render_world(i, os.path.join(OUT, f'bg_{i}.png'))
    print(f'WORLD_{i}_DONE')

todo = ONLY if ONLY else list(range(9))
for i in todo:
    build(i)
print('OUTDOOR_WORLDS_DONE')
