import bpy, math, os, random
FRAMEWORK = r"C:\Users\Owner\Documents\once-upon-a-time\tools\blender\framework.py"
exec(open(FRAMEWORK).read())
OUT = r"C:\Users\Owner\Documents\once-upon-a-time\assets\renders\outprops"
os.makedirs(OUT, exist_ok=True)

# 12 outdoor scenery sprites, 288x480 transparent, used as parallax billboards.
# 0 oak  1 birch  2 cherry  3 willow  4 rosebush  5 fountain  6 statue
# 7 mushroom  8 sunflowers  9 cloudcolumn  10 swan  11 bunny

def leafball(x, y, z, r, mat_):
    s = sphere((x, y, z), r, mat_)
    return s

def build(idx):
    sc = reset_scene()
    # These props are shared by all nine stages, so they get one neutral bright
    # daylight capture; the GL world re-tints and fogs them per stage.
    if not hdri_world('blossom', strength=1.0, rot_z=math.radians(-30)):
        w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
        w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.35
        w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.7, 0.8, 0.9, 1)
    random.seed(idx * 7 + 3)
    trunk = wood_mat('Trunk', (0.17, 0.10, 0.05), grain_scale=3, rough=0.8)
    leafG = fabric_mat('LeafG', (0.16, 0.36, 0.10), rough=0.9)
    if idx == 0:      # oak
        cyl((0, 0, 0.7), 0.16, 1.4, trunk, verts=12)
        for i in range(6):
            leafball(random.uniform(-0.5, 0.5), random.uniform(-0.3, 0.3), 1.6 + random.uniform(0, 0.6), random.uniform(0.38, 0.58), leafG)
    elif idx == 1:    # birch
        bark = fabric_mat('Bark', (0.82, 0.8, 0.75), rough=0.7)
        cyl((0, 0, 0.85), 0.09, 1.7, bark, verts=10)
        dm = fabric_mat('Dash', (0.15, 0.14, 0.12), rough=0.8)
        for i in range(5):
            cube((random.uniform(-0.07, 0.07), -0.08, 0.3 + i * 0.3), (0.06, 0.02, 0.05), dm)
        leafL = fabric_mat('LeafL', (0.35, 0.52, 0.2), rough=0.9)
        for i in range(5):
            leafball(random.uniform(-0.35, 0.35), random.uniform(-0.2, 0.2), 1.8 + random.uniform(0, 0.5), random.uniform(0.28, 0.42), leafL)
    elif idx == 2:    # cherry
        cyl((0, 0, 0.75), 0.13, 1.5, trunk, verts=10)
        bloom = fabric_mat('Bloom', (0.97, 0.72, 0.82), rough=0.85)
        for i in range(6):
            leafball(random.uniform(-0.5, 0.5), random.uniform(-0.25, 0.25), 1.7 + random.uniform(0, 0.55), random.uniform(0.34, 0.52), bloom)
    elif idx == 3:    # willow
        cyl((0, 0, 0.8), 0.14, 1.6, trunk, verts=10)
        wl = fabric_mat('Willow', (0.3, 0.48, 0.22), rough=0.9)
        leafball(0, 0, 1.95, 0.55, wl)
        for i in range(8):
            a = i / 8 * math.pi * 2
            dr = cyl((math.cos(a) * 0.5, math.sin(a) * 0.25, 1.35), 0.05, 1.0, wl, verts=8)
    elif idx == 4:    # rosebush
        hb = stone_mat('Hedge', (0.10, 0.26, 0.08), rough=0.95, scale=14, bump=0.5)
        b = sphere((0, 0, 0.55), 0.62, hb); b.scale = (1.1, 0.8, 0.85)
        rm = emissive_mat('Rose', (0.85, 0.12, 0.25), 1.3)
        for i in range(9):
            a = random.uniform(0, math.pi * 2); rr = random.uniform(0.2, 0.55)
            sphere((math.cos(a) * rr, -0.35 - random.uniform(0, 0.15), 0.45 + random.uniform(0, 0.5)), 0.07, rm)
    elif idx == 5:    # fountain
        marble = marble_mat('FM', (0.72, 0.71, 0.68), (0.5, 0.5, 0.52), rough=0.3)
        water = bpy.data.materials.new('Wat'); water.use_nodes = True
        wb = water.node_tree.nodes['Principled BSDF']
        wb.inputs['Base Color'].default_value = (0.45, 0.75, 0.9, 1)
        wb.inputs['Roughness'].default_value = 0.05
        cyl((0, 0, 0.22), 0.85, 0.44, marble, verts=28)
        cyl((0, 0, 0.45), 0.74, 0.05, water, verts=28)
        cyl((0, 0, 0.7), 0.12, 0.8, marble, verts=14)
        cyl((0, 0, 1.1), 0.4, 0.08, marble, verts=22)
        cyl((0, 0, 1.15), 0.33, 0.04, water, verts=22)
        sphere((0, 0, 1.45), 0.13, water)
        sm = emissive_mat('Spray', (0.8, 0.95, 1), 2.5)
        for i in range(6):
            sphere((random.uniform(-0.25, 0.25), random.uniform(-0.25, 0.25), 1.3 + random.uniform(0, 0.4)), 0.028, sm)
    elif idx == 6:    # statue (angel)
        marble = marble_mat('SM', (0.68, 0.67, 0.64), (0.48, 0.48, 0.5), rough=0.35)
        cube((0, 0, 0.3), (0.55, 0.55, 0.6), marble)
        cyl((0, 0, 0.85), 0.14, 0.5, marble, verts=12)
        s = sphere((0, 0, 1.35), 0.27, marble); s.scale = (0.75, 0.5, 1.1)
        sphere((0, 0, 1.76), 0.13, marble)
        for sgn in (-1, 1):
            cube((sgn * 0.32, 0.02, 1.5), (0.45, 0.06, 0.14), marble, rot=(0, math.radians(-38 * sgn), 0))
        t = bpy.ops.mesh.primitive_torus_add(major_radius=0.16, minor_radius=0.02, location=(0, 0, 1.98))
        tor = bpy.context.active_object; tor.data.materials.append(gold_mat('Halo'))
    elif idx == 7:    # mushroom
        st = fabric_mat('MS', (0.8, 0.76, 0.68), rough=0.8)
        cyl((0, 0, 0.55), 0.17, 1.1, st, verts=12)
        cm = fabric_mat('MC', (0.85, 0.25, 0.3), rough=0.6)
        c = sphere((0, 0, 1.15), 0.6, cm); c.scale = (1, 1, 0.55)
        dm2 = fabric_mat('MD', (0.95, 0.93, 0.88), rough=0.7)
        for i in range(5):
            a = random.uniform(0, math.pi * 2); rr = random.uniform(0.1, 0.45)
            sphere((math.cos(a) * rr, math.sin(a) * rr - 0.18, 1.3 + random.uniform(0, 0.12)), 0.075, dm2)
    elif idx == 8:    # sunflower clump
        stm = fabric_mat('Stem', (0.12, 0.3, 0.06), rough=0.9)
        petal = emissive_mat('Pet', (0.95, 0.75, 0.12), 0.7)
        core = fabric_mat('Core', (0.25, 0.14, 0.04), rough=0.9)
        for (fx, fs) in ((-0.28, 0.9), (0.05, 1.15), (0.34, 0.8)):
            cyl((fx, 0, 0.55 * fs), 0.03, 1.1 * fs, stm, verts=8)
            cc = sphere((fx, -0.04, 1.14 * fs), 0.14 * fs, core); cc.scale = (1, 0.4, 1)
            for k in range(8):
                a = k / 8 * math.pi * 2
                p = sphere((fx + math.cos(a) * 0.19 * fs, -0.03, 1.14 * fs + math.sin(a) * 0.19 * fs), 0.075 * fs, petal)
                p.scale = (1, 0.3, 0.55)
    elif idx == 9:    # cloud column (gold pillar on a puff)
        cm2 = fabric_mat('Cl', (0.93, 0.94, 0.98), rough=1.0)
        for i in range(4):
            s = sphere((random.uniform(-0.4, 0.4), random.uniform(-0.2, 0.2), 0.3 + random.uniform(0, 0.15)), random.uniform(0.3, 0.45), cm2)
            s.scale = (1.3, 1, 0.6)
        cyl((0, 0, 1.15), 0.13, 1.4, marble_mat('P', (0.8, 0.8, 0.82), (0.6, 0.62, 0.7), rough=0.25), verts=14)
        sphere((0, 0, 1.95), 0.17, gold_mat('Orb'))
    elif idx == 10:   # swan
        sw = fabric_mat('Swan', (0.95, 0.95, 0.92), rough=0.7)
        b = sphere((0, 0, 0.35), 0.4, sw); b.scale = (0.8, 1.3, 0.7)
        wq = sphere((0.18, 0.1, 0.5), 0.28, sw); wq.scale = (0.5, 1, 0.7)
        cyl((0, -0.42, 0.7), 0.07, 0.7, sw, rot=(math.radians(18), 0, 0), verts=10)
        hd = sphere((0, -0.55, 1.05), 0.12, sw)
        bpy.ops.mesh.primitive_cone_add(radius1=0.05, radius2=0.005, depth=0.16, location=(0, -0.68, 1.03), rotation=(math.radians(95), 0, 0), vertices=8)
        bk = bpy.context.active_object; bk.data.materials.append(fabric_mat('Beak', (0.85, 0.5, 0.1), rough=0.6))
    else:             # bunny
        fur = fabric_mat('Fur', (0.75, 0.68, 0.6), rough=0.95)
        b = sphere((0, 0, 0.32), 0.32, fur); b.scale = (0.85, 1.1, 0.9)
        hd = sphere((0, -0.28, 0.62), 0.2, fur)
        for sgn in (-1, 1):
            e = sphere((sgn * 0.09, -0.3, 0.92), 0.07, fur); e.scale = (0.55, 0.4, 1.9)
        tl = sphere((0, 0.32, 0.35), 0.1, fabric_mat('Tail', (0.92, 0.9, 0.86), rough=0.95))
        em = fabric_mat('Eye', (0.08, 0.05, 0.04), rough=0.4)
        for sgn in (-1, 1):
            sphere((sgn * 0.08, -0.45, 0.66), 0.028, em)
    # soft shaping key only — the HDRI supplies ambient, sun colour, reflections
    area_light((-1.8, -2.6, 2.6), 90, 3.0, (1, 0.95, 0.86), (math.radians(52), 0, math.radians(-30)))
    area_light((2.0, -2.2, 1.2), 35, 2.5, (0.7, 0.78, 0.95), (math.radians(65), 0, math.radians(35)))
    decor_cam()
    render_to(os.path.join(OUT, f'prop_{idx}.png'), 288, 480, transparent=True, samples=110)
    print(f'PROP_{idx}_DONE')

for i in range(12):
    build(i)
print('OUTPROPS_DONE')
