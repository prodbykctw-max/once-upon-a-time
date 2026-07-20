import bpy, math, os, random
FRAMEWORK = r"C:\Users\Owner\Documents\once-upon-a-time\tools\blender\framework.py"
exec(open(FRAMEWORK).read())
OUT = r"C:\Users\Owner\Documents\once-upon-a-time\assets\renders\outprops"
os.makedirs(OUT, exist_ok=True)

# Library scenery for stage 0, appended to the shared outprops kit as 12..15.
# The Sunlit Library becomes a real GL world like every other stage: instead of
# corridor wall panels it is a grand hall whose aisles are built from these.
#   12 tall bookcase   13 globe + reading table   14 potted palm   15 armchair+lamp

# Book spines must survive being lit inside a shelf recess, so these are
# brighter than a literal binding colour — framework's mixing materials also
# wash out, so build the spine shader explicitly.
BOOKCOLS = [(0.72, 0.16, 0.18), (0.16, 0.34, 0.66), (0.62, 0.48, 0.16),
            (0.14, 0.46, 0.26), (0.52, 0.28, 0.52), (0.70, 0.50, 0.20),
            (0.30, 0.16, 0.44), (0.74, 0.36, 0.14)]

def spine_mat(name, col):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1)
    b.inputs['Roughness'].default_value = 0.55
    return m

def shelf_books(x0, x1, z, depth, n, seed):
    random.seed(seed)
    x = x0
    k = 0
    while x < x1 - 0.04:
        w = random.uniform(0.045, 0.085)
        h = random.uniform(0.26, 0.40)
        cube((x + w / 2, depth, z + h / 2), (w, 0.24, h),
             spine_mat(f'Bk{seed}{k}', random.choice(BOOKCOLS)),
             rot=(0, random.uniform(-0.05, 0.05), 0))
        x += w + random.uniform(0.004, 0.014)
        k += 1

def build(idx):
    sc = reset_scene()
    # glasshouse capture: real sun through a glazed roof, which is exactly the
    # light the Sunlit Library is meant to sit in.
    if not hdri_world('library', strength=1.4, rot_z=math.radians(-25)):
        w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
        w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.26
        w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.72, 0.64, 0.50, 1)
    random.seed(idx * 17 + 5)
    oak = wood_mat('Oak', (0.24, 0.13, 0.06), grain_scale=5, rough=0.5)
    warm = wood_mat('Warm', (0.32, 0.19, 0.09), grain_scale=7, rough=0.45)

    if idx == 12:      # tall bookcase — the aisle wall of the hall
        cube((0, 0, 1.30), (1.30, 0.34, 2.60), oak)          # carcass
        cube((0, -0.02, 2.66), (1.44, 0.40, 0.12), warm)      # cornice
        cube((0, -0.02, 2.76), (1.30, 0.34, 0.08), gold_mat('G'))
        cube((0, 0, 0.06), (1.40, 0.38, 0.12), warm)          # plinth
        for s in range(5):
            zz = 0.20 + s * 0.48
            cube((0, 0.02, zz), (1.20, 0.30, 0.04), warm)
            # spines sit proud of the case so the key light actually reaches them
            shelf_books(-0.58, 0.58, zz + 0.02, -0.11, 9, idx * 10 + s)
        for sx in (-0.62, 0.62):                              # side stiles
            cube((sx, -0.04, 1.30), (0.08, 0.36, 2.56), warm)
    elif idx == 13:    # globe on a reading table
        cube((0, 0, 0.78), (1.10, 0.62, 0.07), warm)          # table top
        cube((0, 0, 0.82), (1.16, 0.66, 0.02), gold_mat('Gt'))
        for (tx, ty) in ((-0.44, -0.22), (0.44, -0.22), (-0.44, 0.22), (0.44, 0.22)):
            cyl((tx, ty, 0.38), 0.045, 0.76, warm, verts=10)
        cyl((0, 0, 0.90), 0.13, 0.06, warm, verts=16)         # globe stand
        cyl((0, 0, 1.02), 0.028, 0.24, gold_mat('Gs'), verts=10)
        gl = bpy.data.materials.new('Globe'); gl.use_nodes = True
        gb = gl.node_tree.nodes['Principled BSDF']
        gb.inputs['Base Color'].default_value = (0.20, 0.42, 0.55, 1)
        gb.inputs['Roughness'].default_value = 0.35
        sphere((0, 0, 1.32), 0.26, gl)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.30, minor_radius=0.014, location=(0, 0, 1.32),
                                         rotation=(math.radians(70), 0, 0))
        bpy.context.active_object.data.materials.append(gold_mat('Ring'))
        for k in range(3):                                     # stacked books
            cube((0.34, 0.06 * k, 0.86 + k * 0.05), (0.34, 0.24, 0.05),
                 fabric_mat(f'Tb{k}', random.choice(BOOKCOLS), rough=0.55),
                 rot=(0, 0, random.uniform(-0.12, 0.12)))
    elif idx == 14:    # potted palm
        pot = stone_mat('Pot', (0.55, 0.34, 0.22), rough=0.6, scale=10, bump=0.25)
        cyl((0, 0, 0.26), 0.34, 0.52, pot, verts=22)
        cyl((0, 0, 0.53), 0.37, 0.07, pot, verts=22)
        soil = stone_mat('Soil', (0.16, 0.11, 0.07), rough=0.98, scale=24, bump=0.5)
        cyl((0, 0, 0.55), 0.30, 0.04, soil, verts=20)
        stm = fabric_mat('Stem', (0.20, 0.34, 0.12), rough=0.9)
        frond = fabric_mat('Frond', (0.17, 0.40, 0.14), rough=0.88)
        for k in range(9):
            a = k / 9 * 6.28 + random.uniform(-0.2, 0.2)
            tilt = random.uniform(0.5, 1.15)
            ln = random.uniform(0.55, 0.95)
            ex, ey = math.cos(a) * ln * tilt, math.sin(a) * ln * tilt * 0.6
            cyl((ex * 0.5, ey * 0.5, 0.60 + ln * 0.45), 0.022, ln, stm,
                rot=(math.radians(90) * tilt * 0.55 * math.sin(a + 1.57), 0,
                     math.radians(90) * tilt * 0.55 * math.cos(a)), verts=8)
            f = sphere((ex, ey, 0.62 + ln * 0.80), 0.30, frond)
            f.scale = (1.5, 0.7, 0.18)
            f.rotation_euler = (random.uniform(-0.4, 0.4), random.uniform(-0.5, 0.5), a)
    else:              # 15: armchair + floor lamp
        vel = fabric_mat('Velvet', (0.34, 0.09, 0.16), rough=0.85)
        cube((0, 0, 0.30), (0.86, 0.80, 0.20), vel)            # seat
        cube((0, 0.34, 0.72), (0.86, 0.16, 0.86), vel)         # back
        for sx in (-0.40, 0.40):
            cube((sx, -0.02, 0.50), (0.14, 0.76, 0.26), vel)   # arms
        for (tx, ty) in ((-0.34, -0.30), (0.34, -0.30), (-0.34, 0.30), (0.34, 0.30)):
            cyl((tx, ty, 0.11), 0.04, 0.22, oak, verts=8)
        cyl((0.78, 0.10, 0.03), 0.20, 0.06, gold_mat('Base'), verts=18)   # lamp
        cyl((0.78, 0.10, 0.82), 0.022, 1.60, gold_mat('Pole'), verts=10)
        sh = cyl((0.78, 0.10, 1.72), 0.26, 0.34, fabric_mat('Shade', (0.95, 0.86, 0.62), rough=0.9), verts=20)
        sh.scale = (1, 1, 1)
        sphere((0.78, 0.10, 1.66), 0.10, emissive_mat('Bulb', (1, 0.86, 0.55), 14.0))

    # warm window light raking from the left, cool fill, gentle top bounce
    area_light((-2.6, -2.2, 3.0), 110, 3.0, (1, 0.90, 0.68), (math.radians(52), 0, math.radians(-38)))
    area_light((2.2, -2.4, 1.2), 40, 2.4, (0.72, 0.80, 0.96), (math.radians(66), 0, math.radians(34)))
    area_light((0, 2.6, 2.4), 50, 2.6, (1, 0.92, 0.74), (math.radians(-60), 0, math.radians(180)))
    decor_cam()
    render_to(os.path.join(OUT, f'prop_{idx}.png'), 288, 480, transparent=True, samples=110)
    print(f'LIBPROP_{idx}_DONE')

for i in (12, 13, 14, 15):
    build(i)
print('LIBPROPS_DONE')
