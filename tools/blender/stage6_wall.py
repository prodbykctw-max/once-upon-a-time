FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())
import random
random.seed(66)

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles\wall_6.png"

sc = reset_scene()

w = bpy.data.worlds.new('W'); w.use_nodes = True
bg = w.node_tree.nodes['Background']
bg.inputs[0].default_value = (0.35, 0.38, 0.45, 1)
bg.inputs[1].default_value = 0.10
sc.world = w

def tighten_metal(m, lo, hi):
    for n in m.node_tree.nodes:
        if n.type == 'VALTORGB':
            n.color_ramp.elements[0].color = (lo, lo, lo, 1)
            n.color_ramp.elements[1].color = (hi, hi, hi, 1)

# ---- granite block wall ----
mortar = stone_mat('Mortar', tone=(0.13, 0.12, 0.105), rough=0.95, scale=9.0, bump=0.3)
plane((0, 0.28, 0), 4, mortar, rot=(math.pi/2, 0, 0), name='Backing')

granites = [stone_mat('G%d' % i, tone=t, rough=0.85, scale=7.5, bump=0.7)
            for i, t in enumerate([(0.22, 0.23, 0.27), (0.19, 0.21, 0.24),
                                   (0.26, 0.24, 0.21), (0.20, 0.23, 0.23)])]
# push granite mottle contrast beyond stone_mat default
for g, t in zip(granites, [(0.22, 0.23, 0.27), (0.19, 0.21, 0.24),
                           (0.26, 0.24, 0.21), (0.20, 0.23, 0.23)]):
    for n in g.node_tree.nodes:
        if n.type == 'VALTORGB':
            n.color_ramp.elements[0].color = (t[0]*0.38, t[1]*0.38, t[2]*0.38, 1)
            n.color_ramp.elements[1].color = (t[0]*1.35, t[1]*1.35, t[2]*1.35, 1)

pitch_x, pitch_z = 0.46, 0.335
bw, bh = 0.445, 0.315
for row in range(8):
    z = -1.15 + row * pitch_z
    off = (pitch_x / 2) if row % 2 else 0.0
    x = -1.15 + off
    while x < 1.2:
        b = cube((x + random.uniform(-0.006, 0.006),
                  0.13 + random.uniform(-0.02, 0.01), z),
                 (bw * random.uniform(0.96, 1.02), 0.14, bh * random.uniform(0.96, 1.02)),
                 random.choice(granites), rot=(0, random.uniform(-0.012, 0.012), 0), name='Blk')
        mod = b.modifiers.new('bv', 'BEVEL'); mod.width = 0.013; mod.segments = 2
        x += pitch_x

# ---- prop materials ----
sword_steel = metal_mat('SwordSteel', tone=(0.42, 0.44, 0.50), rough=0.38)
tighten_metal(sword_steel, 0.28, 0.42)
shield_steel = metal_mat('ShieldSteel', tone=(0.50, 0.53, 0.60), rough=0.30)
tighten_metal(shield_steel, 0.22, 0.34)
dark_iron = metal_mat('DarkIron', tone=(0.08, 0.08, 0.09), rough=0.7)
gold = gold_mat()
leather = fabric_mat('Leather', tone=(0.16, 0.07, 0.03), rough=0.85)

# ---- crossed swords behind shield (+-35 deg) ----
for s in (1, -1):
    a = math.radians(35 * s)
    d = (math.sin(a), 0, math.cos(a))
    cz = 0.10
    bl = cube((0, 0.05, cz), (0.062, 0.024, 1.34), sword_steel, rot=(0, a, 0), name='Blade')
    m = bl.modifiers.new('bv', 'BEVEL'); m.width = 0.010; m.segments = 2
    t = -0.50
    cube((t * d[0], 0.05, cz + t * d[2]), (0.26, 0.05, 0.055), dark_iron, rot=(0, a, 0), name='Guard')
    t = -0.585
    cyl((t * d[0], 0.05, cz + t * d[2]), 0.028, 0.16, leather, rot=(0, a, 0), name='Grip')
    t = -0.675
    sphere((t * d[0], 0.05, cz + t * d[2]), 0.045, gold, name='Pommel')

# ---- round steel shield with gold rim + embossed boss ----
cyl((0, 0.00, 0.10), 0.37, 0.05, gold, rot=(math.pi/2, 0, 0), verts=64, name='Rim')
cyl((0, -0.035, 0.10), 0.335, 0.06, shield_steel, rot=(math.pi/2, 0, 0), verts=64, name='Face')
cyl((0, -0.075, 0.10), 0.135, 0.05, gold, rot=(math.pi/2, 0, 0), verts=48, name='BossRing')
bd = sphere((0, -0.075, 0.10), 0.10, shield_steel, name='Boss')
bd.scale = (1, 0.55, 1)
for ang in (45, 135, 225, 315):
    r = math.radians(ang)
    sphere((0.26 * math.cos(r), -0.07, 0.10 + 0.26 * math.sin(r)), 0.028, gold, name='Rivet')

# ---- iron torch sconce at right edge ----
cube((0.60, 0.04, 0.36), (0.05, 0.24, 0.05), dark_iron, rot=(math.radians(40), 0, 0), name='Bracket')
cyl((0.60, -0.07, 0.47), 0.062, 0.17, dark_iron, name='Cup')
cyl((0.60, -0.07, 0.54), 0.070, 0.035, dark_iron, name='CupBand')
f = sphere((0.60, -0.07, 0.645), 0.058, emissive_mat('Flame', (1.0, 0.32, 0.05), 8), name='FlameOuter')
f.scale = (1, 1, 1.8)
f2 = sphere((0.60, -0.07, 0.615), 0.026, emissive_mat('FlameCore', (1.0, 0.6, 0.15), 16), name='FlameCore')
f2.scale = (1, 1, 1.5)
point_light((0.60, -0.30, 0.66), 45, (1, 0.5, 0.18), 0.1)

# custom rig: warm key upper-left, cool fill right (lower energy than warm_rig)
area_light((-2.2, -3.0, 2.4), 200, 3.5, (1, 0.88, 0.72), (math.radians(60), 0, math.radians(-28)))
area_light((2.4, -2.6, 1.2), 90, 3.0, (0.7, 0.78, 1.0), (math.radians(75), 0, math.radians(30)))

wall_cam()
render_to(OUT, 288, 384, transparent=False, samples=160)
