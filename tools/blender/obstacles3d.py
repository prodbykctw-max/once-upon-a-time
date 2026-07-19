import bpy, math, os, random
FRAMEWORK = r"C:\Users\Owner\Documents\once-upon-a-time\tools\blender\framework.py"
exec(open(FRAMEWORK).read())
OUT = r"C:\Users\Owner\Documents\once-upon-a-time\assets\renders\obstacles"
os.makedirs(OUT, exist_ok=True)

# 3 obstacle types x 9 worlds, each 256x256 transparent, bottom-anchored.
#   low  = jump over        gate = slide under        wall = full blocker
# Rendered slightly above eye level so the player reads the top surface,
# matching the Temple View camera that looks a little down the track.

# Each type gets its own cell aspect + framing so the prop fills its sheet cell
# and its base lands on the bottom edge (the game anchors obstacles to the floor).
#            res_x res_y ortho
FRAME = {'low':  (256,  96, 2.32),
         'gate': (256, 192, 2.52),
         'wall': (256, 224, 2.42)}
TILT = 6.0      # degrees looking down — enough to read top surfaces
DIST = 5.0

def cam_rig(kind):
    rx, ry, osc = FRAME[kind]
    # aim at the cell centre so z=0 lands exactly on the bottom edge; a tilted
    # camera must be offset along its own view ray or the framing slides badly.
    span_v = osc * ry / rx
    th = math.radians(TILT)
    target_z = span_v / 2
    d = bpy.data.cameras.new('C'); d.type = 'ORTHO'; d.ortho_scale = osc
    c = bpy.data.objects.new('C', d); bpy.context.scene.collection.objects.link(c)
    c.location = (0, -DIST * math.cos(th), target_z + DIST * math.sin(th))
    c.rotation_euler = (math.radians(90 - TILT), 0, 0)
    bpy.context.scene.camera = c
    return rx, ry

# ── foliage helpers: leaves are flattened, randomly tilted discs, not bare
# spheres — that is what makes a hedge read as leafy instead of as a slab ──
def leafcluster(x, y, z, r, mat_, n=5, spread=0.5):
    for _ in range(n):
        s = sphere((x + random.uniform(-r, r) * spread,
                    y + random.uniform(-r, r) * spread * 0.6,
                    z + random.uniform(-r, r) * spread), r * random.uniform(0.55, 1.0), mat_)
        s.scale = (1.0, 0.34, 0.66)
        s.rotation_euler = (random.uniform(-0.5, 0.5), random.uniform(-0.6, 0.6), random.uniform(0, 3.14))

def leafy_box(w, d, h, tone, n=34, leaf_r=0.15, seed=0):
    """Dark recessed core fully clad in leaf clusters — the core must never
    read as a visible slab, so it is inset and the foliage laid on in a grid
    with jitter (random scatter alone leaves bald patches)."""
    random.seed(seed)
    core = stone_mat('Core', (tone[0] * 0.34, tone[1] * 0.34, tone[2] * 0.34), rough=0.96, scale=18, bump=0.5)
    cube((0, 0, h / 2), (w * 0.80, d * 0.62, h * 0.80), core)
    lm = [fabric_mat(f'Lf{k}', (tone[0] * f, tone[1] * f, tone[2] * f), rough=0.9)
          for k, f in enumerate((0.72, 1.0, 1.3))]
    cols = max(6, int(w / (leaf_r * 1.15)))
    rows = max(4, int(h / (leaf_r * 1.15)))
    for cx in range(cols + 1):                   # clad the front face
        for cz in range(rows + 1):
            u = -w / 2 + cx * w / cols + random.uniform(-0.4, 0.4) * leaf_r
            v = cz * h / rows + random.uniform(-0.4, 0.4) * leaf_r
            leafcluster(u, -d / 2 + leaf_r * 0.25, v, leaf_r * random.uniform(0.8, 1.1),
                        random.choice(lm), n=2, spread=0.35)
    for cz in range(rows + 1):                   # silhouette edges
        v = cz * h / rows
        for u in (-w / 2, w / 2):
            leafcluster(u, random.uniform(-d / 4, 0), v, leaf_r * 0.9, random.choice(lm), n=2, spread=0.4)
    for cx in range(cols + 1):                   # crown
        leafcluster(-w / 2 + cx * w / cols, random.uniform(-d / 3, 0), h,
                    leaf_r * 0.95, random.choice(lm), n=2, spread=0.4)

def rose(x, y, z, r=0.075, tone=(0.80, 0.10, 0.22)):
    cm = fabric_mat('Rc', tone, rough=0.68)
    pm = fabric_mat('Rp', (min(1, tone[0] * 1.25), tone[1] * 1.3 + 0.05, tone[2] * 1.2), rough=0.7)
    sphere((x, y, z), r * 0.6, cm)
    for k in range(5):
        a = k / 5 * 6.28 + random.uniform(-0.3, 0.3)
        p = sphere((x + math.cos(a) * r * 0.62, y - r * 0.18, z + math.sin(a) * r * 0.62), r * 0.60, pm)
        p.scale = (1, 0.42, 0.82)
        p.rotation_euler = (0, 0, a)

def lights(warm=(1, 0.94, 0.84), key=340):
    area_light((-2.2, -3.0, 3.0), key, 3.2, warm, (math.radians(48), 0, math.radians(-32)))
    area_light((2.4, -2.6, 1.6), 120, 2.6, (0.70, 0.78, 0.96), (math.radians(66), 0, math.radians(34)))
    area_light((0, 3.0, 2.2), 150, 3.0, warm, (math.radians(-58), 0, math.radians(180)))

def world_bg(strength=0.42, col=(0.72, 0.82, 0.92)):
    w = bpy.data.worlds.new('W'); bpy.context.scene.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = strength
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (*col, 1)

def leaf(x, y, z, r, m, flat=0.8):
    s = sphere((x, y, z), r, m); s.scale = (1, 0.75, flat); return s

# ── palettes ──
WOOD = lambda: wood_mat('W', (0.20, 0.12, 0.06), grain_scale=4, rough=0.72)
HEDGE = lambda t=(0.10, 0.26, 0.08): stone_mat('H', t, rough=0.95, scale=16, bump=0.55)
MARB = lambda: marble_mat('M', (0.80, 0.79, 0.76), (0.55, 0.55, 0.58), rough=0.26)

# ═══ LOW barriers (jump over) — under ~0.75 tall ═══
def low(i):
    if i == 0:      # library: stacked books on a plinth
        cube((0, 0, 0.10), (2.0, 0.5, 0.20), wood_mat('P', (0.26, 0.16, 0.08), rough=0.6))
        cols = [(0.55, 0.10, 0.12), (0.13, 0.25, 0.45), (0.35, 0.28, 0.10), (0.12, 0.32, 0.18)]
        for k in range(7):
            bx = -0.78 + k * 0.26
            for j in range(random.randint(1, 3)):
                cube((bx, random.uniform(-0.04, 0.04), 0.24 + j * 0.115),
                     (0.24, 0.34, 0.11), fabric_mat(f'B{k}{j}', random.choice(cols), rough=0.55),
                     rot=(0, 0, random.uniform(-0.09, 0.09)))
    elif i == 1:    # meadow: fallen mossy log
        lg = cyl((0, 0, 0.30), 0.30, 2.0, WOOD(), rot=(0, math.radians(90), 0), verts=18)
        mo = stone_mat('Mo', (0.16, 0.34, 0.12), rough=0.95, scale=22, bump=0.6)
        for k in range(9):
            leaf(random.uniform(-0.9, 0.9), random.uniform(-0.18, -0.02),
                 0.48 + random.uniform(-0.05, 0.05), random.uniform(0.10, 0.17), mo, 0.5)
    elif i == 2:    # blossom: planter box of pink blooms
        cube((0, 0, 0.22), (2.0, 0.56, 0.44), wood_mat('Pl', (0.42, 0.30, 0.20), rough=0.6))
        cube((0, 0, 0.45), (2.04, 0.60, 0.06), MARB())
        bm2 = fabric_mat('Bl', (0.97, 0.70, 0.81), rough=0.85)
        gm = fabric_mat('Lf', (0.22, 0.42, 0.16), rough=0.9)
        for k in range(16):
            x = random.uniform(-0.92, 0.92)
            leaf(x, random.uniform(-0.16, 0.16), 0.52 + random.uniform(0, 0.10), random.uniform(0.09, 0.15), gm, 0.7)
            leaf(x + random.uniform(-0.05, 0.05), random.uniform(-0.20, 0.10), 0.60 + random.uniform(0, 0.12), random.uniform(0.06, 0.10), bm2, 0.85)
    elif i == 3:    # rose garden: clipped rose hedge
        leafy_box(2.0, 0.62, 0.66, (0.13, 0.32, 0.10), n=30, leaf_r=0.10, seed=31)
        for k in range(11):
            rose(random.uniform(-0.92, 0.92), -0.30, 0.16 + random.uniform(0, 0.44))
    elif i == 4:    # swan lake: stone balustrade
        cube((0, 0, 0.06), (2.1, 0.44, 0.12), MARB())
        cube((0, 0, 0.66), (2.1, 0.40, 0.13), MARB())
        for k in range(7):
            bx = -0.84 + k * 0.28
            cyl((bx, 0, 0.36), 0.10, 0.50, MARB(), verts=14)
            sphere((bx, 0, 0.36), 0.135, MARB()).scale = (1, 1, 0.55)
    elif i == 5:    # fairy glade: mushroom cluster on moss
        mo = stone_mat('Mo', (0.14, 0.30, 0.13), rough=0.95, scale=20, bump=0.6)
        b = sphere((0, 0, 0.10), 0.95, mo); b.scale = (1.05, 0.42, 0.22)
        st = fabric_mat('S', (0.90, 0.87, 0.78), rough=0.8)
        cp = fabric_mat('C', (0.86, 0.22, 0.28), rough=0.55)
        dot = emissive_mat('D', (1, 0.97, 0.9), 1.4)
        for (mx, ms) in ((-0.62, 0.72), (-0.18, 1.0), (0.30, 0.85), (0.74, 0.62)):
            cyl((mx, 0, 0.20 * ms), 0.10 * ms, 0.40 * ms, st, verts=12)
            c = sphere((mx, 0, 0.44 * ms), 0.30 * ms, cp); c.scale = (1, 1, 0.52)
            for k in range(3):
                a = random.uniform(0, 6.28); rr = random.uniform(0.05, 0.19) * ms
                sphere((mx + math.cos(a) * rr, math.sin(a) * rr * 0.5 - 0.12, 0.50 * ms), 0.038 * ms, dot)
    elif i == 6:    # sunflower fields: hay bales
        hay = stone_mat('Hy', (0.66, 0.52, 0.20), rough=0.95, scale=30, bump=0.7)
        for (hx, hz) in ((-0.52, 0), (0.52, 0), (0, 0.60)):
            h = cyl((hx, 0, 0.30 + hz), 0.32, 0.86, hay, rot=(0, math.radians(90), 0), verts=16)
        tw = fabric_mat('Tw', (0.35, 0.26, 0.10), rough=0.9)
        for (hx, hz) in ((-0.52, 0), (0.52, 0), (0, 0.60)):
            for tx in (-0.16, 0.16):
                cyl((hx + tx, 0, 0.30 + hz), 0.325, 0.045, tw, rot=(0, math.radians(90), 0), verts=16)
    elif i == 7:    # cloud gardens: marble bench on a cloud
        cm = fabric_mat('Cl', (0.95, 0.96, 0.99), rough=1.0)
        for k in range(5):
            s = sphere((random.uniform(-0.85, 0.85), random.uniform(-0.12, 0.12), 0.13), random.uniform(0.24, 0.34), cm)
            s.scale = (1.25, 0.85, 0.55)
        cube((0, 0, 0.48), (1.75, 0.48, 0.11), MARB())
        for bx in (-0.62, 0.62):
            cyl((bx, 0, 0.26), 0.09, 0.44, MARB(), verts=12)
        g = gold_mat('G')
        for bx in (-0.62, 0.62):
            cyl((bx, 0, 0.50), 0.11, 0.05, g, verts=14)
    else:           # sunset stage: monitor wedges + riser
        blk = fabric_mat('Bk', (0.07, 0.07, 0.08), rough=0.7)
        cube((0, 0, 0.13), (2.0, 0.62, 0.26), fabric_mat('Rz', (0.14, 0.12, 0.15), rough=0.8))
        cube((0, 0, 0.27), (2.04, 0.66, 0.04), metal_mat('Ed', (0.72, 0.62, 0.35), rough=0.35))
        for mx in (-0.56, 0.56):
            w = cube((mx, 0, 0.44), (0.72, 0.52, 0.34), blk, rot=(math.radians(-22), 0, 0))
            cyl((mx, -0.18, 0.46), 0.16, 0.05, metal_mat('Gr', (0.35, 0.35, 0.38), rough=0.5),
                rot=(math.radians(68), 0, 0), verts=18)
        for mx in (-0.9, 0.9):
            sphere((mx, -0.1, 0.32), 0.07, emissive_mat('Lp', (1, 0.35, 0.5), 5.0))

# ═══ GATE (slide under) — header up high, legs at the sides, open below ═══
GAP = 0.78   # clear opening height she slides through
def gate(i):
    hz = GAP + 0.30                       # header centre height
    if i == 0:      # library: draped doorway
        for sx in (-0.94, 0.94):
            cube((sx, 0, 0.62), (0.22, 0.30, 1.24), wood_mat('Fr', (0.28, 0.17, 0.08), rough=0.6))
        cube((0, 0, hz), (2.1, 0.32, 0.44), wood_mat('Hd', (0.24, 0.14, 0.07), rough=0.6))
        cube((0, -0.02, hz + 0.26), (2.2, 0.28, 0.10), gold_mat('G'))
        dr = fabric_mat('Dr', (0.55, 0.10, 0.16), rough=0.85)
        for k in range(6):
            cube((-0.78 + k * 0.31, -0.16, hz - 0.30), (0.28, 0.05, 0.30), dr)
    elif i == 1:    # meadow: rustic trellis arch
        for sx in (-0.92, 0.92):
            cyl((sx, 0, 0.62), 0.10, 1.24, WOOD(), verts=12)
        cyl((0, 0, hz), 0.10, 2.0, WOOD(), rot=(0, math.radians(90), 0), verts=12)
        cyl((0, 0, hz + 0.26), 0.07, 1.7, WOOD(), rot=(0, math.radians(90), 0), verts=10)
        vm = fabric_mat('V', (0.20, 0.42, 0.14), rough=0.9)
        for k in range(14):
            leaf(random.uniform(-1.0, 1.0), random.uniform(-0.12, 0.12),
                 hz + random.uniform(-0.16, 0.34), random.uniform(0.08, 0.15), vm, 0.7)
    elif i == 2:    # blossom: cherry branch arch
        for sx in (-0.90, 0.90):
            cyl((sx, 0, 0.62), 0.11, 1.24, WOOD(), verts=12)
        cyl((0, 0, hz), 0.09, 1.9, WOOD(), rot=(0, math.radians(90), 0), verts=12)
        bl = fabric_mat('Bl', (0.98, 0.72, 0.83), rough=0.85)
        for k in range(20):
            leaf(random.uniform(-1.02, 1.02), random.uniform(-0.16, 0.16),
                 hz + random.uniform(-0.14, 0.40), random.uniform(0.09, 0.17), bl, 0.75)
    elif i == 3:    # rose garden: rose arbor
        for sx in (-0.92, 0.92):
            cyl((sx, 0, 0.62), 0.09, 1.24, wood_mat('Tr', (0.86, 0.85, 0.80), grain_scale=8, rough=0.5), verts=10)
        cyl((0, 0, hz), 0.09, 2.0, wood_mat('Tr2', (0.86, 0.85, 0.80), grain_scale=8, rough=0.5),
            rot=(0, math.radians(90), 0), verts=12)
        gm = fabric_mat('Lf', (0.14, 0.34, 0.10), rough=0.9)
        for k in range(18):
            x = random.uniform(-1.02, 1.02)
            leafcluster(x, random.uniform(-0.14, 0.14), hz + random.uniform(-0.18, 0.34), 0.12, gm, n=3)
            if k % 2 == 0:
                rose(x, -0.16, hz + random.uniform(-0.12, 0.30))
    elif i == 4:    # swan lake: marble arch
        for sx in (-0.92, 0.92):
            cube((sx, 0, 0.62), (0.26, 0.34, 1.24), MARB())
            cube((sx, 0, 1.26), (0.34, 0.40, 0.10), MARB())
        cube((0, 0, hz + 0.06), (2.1, 0.34, 0.46), MARB())
        cube((0, -0.02, hz + 0.33), (2.24, 0.30, 0.10), MARB())
        for k in range(5):
            cyl((-0.6 + k * 0.3, -0.04, hz + 0.06), 0.07, 0.30, gold_mat('G'), verts=12)
    elif i == 5:    # fairy glade: twisted branch arch with glow
        for sx in (-0.90, 0.90):
            cyl((sx, 0, 0.62), 0.12, 1.24, wood_mat('Tw', (0.16, 0.11, 0.07), grain_scale=3, rough=0.85), verts=10)
        cyl((0, 0, hz), 0.11, 1.95, wood_mat('Tw2', (0.16, 0.11, 0.07), grain_scale=3, rough=0.85),
            rot=(0, math.radians(90), 0), verts=12)
        mo = fabric_mat('Mo', (0.18, 0.36, 0.16), rough=0.95)
        gl = emissive_mat('Gl', (0.65, 0.95, 0.70), 3.4)
        for k in range(14):
            leaf(random.uniform(-1.0, 1.0), random.uniform(-0.12, 0.12), hz + random.uniform(-0.16, 0.30), random.uniform(0.08, 0.14), mo, 0.7)
        for k in range(9):
            sphere((random.uniform(-1.0, 1.0), -0.16, hz + random.uniform(-0.30, 0.34)), 0.045, gl)
    elif i == 6:    # sunflower fields: farm gate arch
        for sx in (-0.92, 0.92):
            cube((sx, 0, 0.62), (0.20, 0.24, 1.24), WOOD())
        cube((0, 0, hz), (2.1, 0.22, 0.26), WOOD())
        cube((0, 0, hz + 0.30), (1.8, 0.20, 0.16), WOOD())
        pm = emissive_mat('Pt', (0.96, 0.76, 0.14), 0.8)
        cm = fabric_mat('Cr', (0.26, 0.15, 0.05), rough=0.9)
        for sx in (-0.62, 0.62):
            c = sphere((sx, -0.14, hz + 0.30), 0.10, cm); c.scale = (1, 0.4, 1)
            for k in range(8):
                a = k / 8 * 6.28
                p = sphere((sx + math.cos(a) * 0.15, -0.13, hz + 0.30 + math.sin(a) * 0.15), 0.058, pm)
                p.scale = (1, 0.32, 0.6)
    elif i == 7:    # cloud gardens: golden arch on cloud piers
        cm = fabric_mat('Cl', (0.95, 0.96, 0.99), rough=1.0)
        for sx in (-0.92, 0.92):
            cyl((sx, 0, 0.62), 0.13, 1.24, MARB(), verts=16)
            for k in range(3):
                s = sphere((sx + random.uniform(-0.14, 0.14), random.uniform(-0.1, 0.1), 0.12), 0.22, cm)
                s.scale = (1.2, 0.9, 0.6)
        cube((0, 0, hz), (2.1, 0.28, 0.34), MARB())
        cube((0, -0.02, hz + 0.24), (2.24, 0.24, 0.10), gold_mat('G'))
        sphere((0, -0.06, hz + 0.40), 0.13, gold_mat('G2'))
    else:           # sunset stage: lighting truss
        mt = metal_mat('Tr', (0.62, 0.62, 0.66), rough=0.42)
        for sx in (-0.92, 0.92):
            for ox in (-0.08, 0.08):
                cyl((sx + ox, 0, 0.62), 0.045, 1.24, mt, verts=10)
            for k in range(5):
                cube((sx, 0, 0.18 + k * 0.26), (0.20, 0.05, 0.045), mt, rot=(0, math.radians(38), 0))
        for oz in (-0.10, 0.10):
            cyl((0, 0, hz + oz), 0.05, 2.05, mt, rot=(0, math.radians(90), 0), verts=10)
        for k in range(9):
            cube((-0.86 + k * 0.215, 0, hz), (0.05, 0.05, 0.22), mt, rot=(math.radians(0), math.radians(40), 0))
        for k in range(4):
            lx = -0.66 + k * 0.44
            cube((lx, -0.10, hz - 0.20), (0.17, 0.17, 0.20), fabric_mat('Ho', (0.06, 0.06, 0.07), rough=0.6))
            sphere((lx, -0.16, hz - 0.30), 0.075, emissive_mat(f'Lm{k}', (1, 0.62, 0.30), 9.0))

# ═══ WALL (full blocker, dodge to another lane) ═══
def wall(i):
    if i == 0:      # library: bookcase
        cube((0, 0, 0.90), (2.0, 0.40, 1.80), wood_mat('Bc', (0.24, 0.14, 0.07), rough=0.62))
        cols = [(0.5, 0.10, 0.12), (0.12, 0.24, 0.44), (0.32, 0.26, 0.10), (0.10, 0.30, 0.17), (0.36, 0.20, 0.34)]
        for sh in range(4):
            zz = 0.34 + sh * 0.44
            cube((0, -0.03, zz - 0.05), (1.86, 0.34, 0.05), wood_mat(f'Sh{sh}', (0.30, 0.18, 0.09), rough=0.6))
            for k in range(11):
                cube((-0.82 + k * 0.165, -0.06, zz + 0.16), (0.13, 0.26, 0.34),
                     fabric_mat(f'V{sh}{k}', random.choice(cols), rough=0.55),
                     rot=(0, 0, random.uniform(-0.06, 0.06)))
    elif i == 1:    # meadow: tall hedge
        leafy_box(2.0, 0.66, 1.84, (0.13, 0.31, 0.10), n=64, leaf_r=0.115, seed=11)
    elif i == 2:    # blossom: blossom hedge wall
        leafy_box(2.0, 0.60, 1.76, (0.15, 0.32, 0.12), n=52, leaf_r=0.11, seed=22)
        bl = fabric_mat('Bl', (0.97, 0.71, 0.82), rough=0.85)
        for k in range(26):
            leafcluster(random.uniform(-0.98, 0.98), -0.31, random.uniform(0.14, 1.74), 0.12, bl, n=3)
    elif i == 3:    # rose garden: rose trellis wall
        tm = wood_mat('Tr', (0.88, 0.87, 0.82), grain_scale=8, rough=0.5)
        for k in range(7):
            cube((-0.90 + k * 0.30, 0, 0.90), (0.06, 0.10, 1.80), tm)
        for k in range(6):
            cube((0, 0, 0.20 + k * 0.32), (2.0, 0.10, 0.06), tm)
        gm = fabric_mat('Lf', (0.13, 0.32, 0.10), rough=0.9)
        rm = fabric_mat('R', (0.82, 0.11, 0.23), rough=0.7)
        for k in range(24):
            x, z = random.uniform(-0.98, 0.98), random.uniform(0.10, 1.76)
            leafcluster(x, -0.12, z, 0.12, gm, n=3)
            if k % 2 == 0: rose(x, -0.22, z)
    elif i == 4:    # swan lake: stone terrace wall
        cube((0, 0, 0.86), (2.0, 0.44, 1.72), stone_mat('St', (0.62, 0.60, 0.56), rough=0.7, scale=9, bump=0.4))
        cube((0, 0, 1.76), (2.16, 0.52, 0.14), MARB())
        cube((0, 0, 0.08), (2.12, 0.50, 0.16), MARB())
        for k in range(5):
            cyl((-0.72 + k * 0.36, -0.24, 1.10), 0.10, 0.62, MARB(), verts=14)
    elif i == 5:    # fairy glade: mossy boulder wall
        bm2 = stone_mat('Bo', (0.34, 0.36, 0.32), rough=0.88, scale=7, bump=0.5)
        mo = stone_mat('Mo', (0.15, 0.32, 0.14), rough=0.95, scale=20, bump=0.6)
        random.seed(55)
        for k in range(9):
            b = sphere((random.uniform(-0.85, 0.85), random.uniform(-0.15, 0.15), random.uniform(0.25, 1.45)),
                       random.uniform(0.38, 0.56), bm2)
            b.scale = (1.15, 0.85, 0.95)
        for k in range(16):
            leaf(random.uniform(-0.9, 0.9), -0.30, random.uniform(0.20, 1.60), random.uniform(0.12, 0.22), mo, 0.6)
        for k in range(7):
            sphere((random.uniform(-0.9, 0.9), -0.34, random.uniform(0.3, 1.6)), 0.05, emissive_mat(f'G{k}', (0.7, 0.98, 0.72), 3.0))
    elif i == 6:    # sunflower fields: fence + sunflower bank
        for k in range(6):
            cube((-0.90 + k * 0.36, 0, 0.62), (0.12, 0.14, 1.24), WOOD())
        for zz in (0.52, 0.95):
            cube((0, 0, zz), (2.05, 0.10, 0.12), WOOD())
        stm = fabric_mat('Sm', (0.13, 0.31, 0.07), rough=0.9)
        pm = emissive_mat('Pt', (0.96, 0.77, 0.14), 0.7)
        cm = fabric_mat('Cr', (0.26, 0.15, 0.05), rough=0.9)
        for k in range(6):
            fx = -0.85 + k * 0.34
            fh = random.uniform(1.30, 1.75)
            cyl((fx, 0.08, fh / 2), 0.035, fh, stm, verts=8)
            c = sphere((fx, 0.0, fh), 0.15, cm); c.scale = (1, 0.4, 1)
            for j in range(9):
                a = j / 9 * 6.28
                p = sphere((fx + math.cos(a) * 0.21, 0.01, fh + math.sin(a) * 0.21), 0.078, pm)
                p.scale = (1, 0.3, 0.6)
    elif i == 7:    # cloud gardens: marble colonnade
        cube((0, 0, 0.10), (2.1, 0.60, 0.20), MARB())
        for k in range(4):
            cx = -0.72 + k * 0.48
            cyl((cx, 0, 0.92), 0.15, 1.48, MARB(), verts=20)
            cyl((cx, 0, 1.70), 0.20, 0.12, MARB(), verts=20)
        cube((0, 0, 1.82), (2.16, 0.56, 0.16), MARB())
        cube((0, -0.04, 1.92), (2.24, 0.48, 0.06), gold_mat('G'))
        cm = fabric_mat('Cl', (0.95, 0.96, 0.99), rough=1.0)
        for k in range(4):
            s = sphere((random.uniform(-0.9, 0.9), 0.22, random.uniform(0.4, 1.4)), 0.26, cm)
            s.scale = (1.3, 0.7, 0.6)
    else:           # sunset stage: stage flat with lights
        cube((0, 0, 0.90), (2.0, 0.34, 1.80), fabric_mat('Fl', (0.10, 0.08, 0.13), rough=0.85))
        mt = metal_mat('Tr', (0.58, 0.58, 0.62), rough=0.45)
        for sx in (-0.94, 0.94):
            cyl((sx, -0.10, 0.90), 0.06, 1.80, mt, verts=10)
        for k in range(5):
            cube((0, -0.10, 0.24 + k * 0.36), (1.9, 0.05, 0.05), mt)
        for k in range(5):
            lx = -0.78 + k * 0.39
            cube((lx, -0.20, 1.62), (0.16, 0.16, 0.18), fabric_mat('Ho', (0.06, 0.06, 0.07), rough=0.6))
            sphere((lx, -0.26, 1.52), 0.075, emissive_mat(f'Lm{k}', (1, 0.55, 0.28), 10.0))
        sphere((0, -0.24, 0.86), 0.30, emissive_mat('Neo', (1, 0.32, 0.52), 2.2)).scale = (2.4, 0.12, 0.5)

BUILDERS = {'low': low, 'gate': gate, 'wall': wall}
# per-world sun/ambient so each obstacle already sits in its world's light
LIGHT = [
    ((1.00, 0.90, 0.74), 330, (0.55, 0.45, 0.35)),   # 0 library warm
    ((1.00, 0.95, 0.86), 360, (0.70, 0.82, 0.94)),   # 1 meadow
    ((1.00, 0.94, 0.92), 340, (0.85, 0.80, 0.90)),   # 2 blossom
    ((1.00, 0.96, 0.90), 350, (0.72, 0.84, 0.95)),   # 3 rose
    ((0.94, 0.97, 1.00), 320, (0.66, 0.80, 0.94)),   # 4 lake
    ((0.80, 0.88, 0.95), 240, (0.30, 0.42, 0.55)),   # 5 glade (dusky)
    ((1.00, 0.95, 0.76), 380, (0.80, 0.82, 0.66)),   # 6 sunflower
    ((1.00, 0.98, 0.95), 360, (0.86, 0.90, 0.98)),   # 7 clouds
    ((1.00, 0.72, 0.48), 330, (0.55, 0.35, 0.38)),   # 8 sunset
]

import sys
only = None
for a in sys.argv:
    if a.startswith('--only='): only = a.split('=', 1)[1]

for kind in ('low', 'gate', 'wall'):
    for i in range(9):
        if only and only != f'{kind}{i}': continue
        random.seed(i * 31 + hash(kind) % 97)
        reset_scene()
        col, key, amb = LIGHT[i]
        world_bg(0.45, amb)
        lights(col, key)
        BUILDERS[kind](i)
        rx, ry = cam_rig(kind)
        render_to(os.path.join(OUT, f'{kind}_{i}.png'), rx, ry, transparent=True, samples=100)
        print(f'OB_{kind}_{i}_DONE')
print('OBSTACLES_DONE')
