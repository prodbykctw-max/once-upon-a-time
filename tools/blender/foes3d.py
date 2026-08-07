import bpy, math, os, random
FRAMEWORK = r"C:\Users\Owner\Documents\once-upon-a-time\tools\blender\framework.py"
exec(open(FRAMEWORK).read())
OUT = r"C:\Users\Owner\Documents\once-upon-a-time\assets\renders\foes"
os.makedirs(OUT, exist_ok=True)

# Fairy-tale villains, 3 frames each, 272x304 -> composed to 136x152 cells.
#   0 THORN GOBLIN   bramble creature that stalks along the ground
#   1 CURSED RAVEN   the stepmother's spy, dives at her
#   2 NIGHTSHADE SPRITE  dark fairy that drifts and darts
# These read at ~52px against bright pastel worlds, so they are built for
# SILHOUETTE and contrast: near-black bodies, one saturated accent, burning
# eyes, and a coloured rim so they never merge into the background.
# NOTE: framework's wood_mat/stone_mat mix toward a lighter base — they wash
# out at this scale. Everything here uses an explicit Principled instead.

def mat(name, col, rough=0.7, spec=0.5):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1)
    b.inputs['Roughness'].default_value = rough
    try: b.inputs['Specular IOR Level'].default_value = spec
    except Exception: pass
    return m

def glow(name, col, s):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = (*col, 1); e.inputs['Strength'].default_value = s
    nt.links.new(e.outputs['Emission'], nt.nodes['Material Output'].inputs['Surface'])
    return m

def eyes(x, y, z, r, col=(1.0, 0.34, 0.06), s=26.0):
    m = glow('Eye', col, s)
    for sx in (-1, 1):
        sphere((x + sx * r * 1.6, y, z), r, m)

def thorn_goblin(f):
    bark = mat('Bark', (0.055, 0.038, 0.022), rough=0.92)
    knot = mat('Knot', (0.10, 0.072, 0.040), rough=0.9)
    moss = mat('Moss', (0.10, 0.26, 0.07), rough=0.95)
    lean = (-0.20, 0.0, 0.20)[f]
    swing = (0.55, 0.0, -0.55)[f]
    body = sphere((0, 0, 0.60), 0.40, bark)
    body.scale = (1.0, 0.82, 1.18); body.rotation_euler = (lean, 0, 0)
    h = sphere((0, -0.12, 1.08), 0.27, bark); h.rotation_euler = (lean, 0, 0)
    # brow sits above the eye line; eyes must clear the head sphere (r=0.27
    # about y=-0.12) or they get buried inside it and stop reading as eyes
    cube((0, -0.28, 1.22), (0.44, 0.13, 0.08), knot, rot=(0.25, 0, 0))
    eyes(0, -0.40, 1.07, 0.055)
    random.seed(f * 7 + 1)
    for k in range(13):          # bramble crown
        a = random.uniform(0, 6.28); rr = random.uniform(0.16, 0.32)
        cyl((math.cos(a) * rr, math.sin(a) * rr * 0.7, 1.24 + random.uniform(0, 0.26)),
            0.021, random.uniform(0.16, 0.34), knot,
            rot=(random.uniform(-0.9, 0.9), random.uniform(-0.9, 0.9), 0), verts=6)
    for sx in (-1, 1):           # shoulder thorns
        for k in range(4):
            cyl((sx * 0.36, -0.08, 0.60 + k * 0.15), 0.017, 0.19, knot,
                rot=(0, math.radians(sx * 58), 0), verts=6)
    for sx in (-1, 1):           # arms + legs
        cyl((sx * 0.36, -0.06 + swing * sx * 0.12, 0.64), 0.058, 0.54, bark,
            rot=(swing * sx * 0.75, math.radians(sx * 14), 0), verts=8)
        sphere((sx * 0.41, -0.12 + swing * sx * 0.24, 0.38), 0.085, knot)
        cyl((sx * 0.17, -swing * sx * 0.17, 0.19), 0.068, 0.40, bark,
            rot=(-swing * sx * 0.85, 0, 0), verts=8)
    for k in range(8):
        sphere((random.uniform(-0.34, 0.34), random.uniform(-0.32, 0.06),
                random.uniform(0.32, 0.94)), random.uniform(0.05, 0.095), moss)

def cursed_raven(f):
    feather = mat('Feather', (0.022, 0.020, 0.034), rough=0.38, spec=0.75)
    sheen = mat('Sheen', (0.10, 0.055, 0.16), rough=0.30, spec=0.85)
    beak = mat('Beak', (0.30, 0.24, 0.10), rough=0.42)
    b = sphere((0, 0, 0.72), 0.30, feather); b.scale = (0.82, 1.28, 0.78)
    sphere((0, -0.34, 0.94), 0.17, feather)
    bpy.ops.mesh.primitive_cone_add(radius1=0.078, radius2=0.005, depth=0.30,
                                    location=(0, -0.56, 0.92), rotation=(math.radians(-96), 0, 0), vertices=10)
    bpy.context.active_object.data.materials.append(beak)
    eyes(0, -0.45, 1.00, 0.040, (1.0, 0.18, 0.42), 30.0)
    # wing beat: up / spread / down — separate primaries read as feathers
    tilt = (math.radians(64), math.radians(4), math.radians(-54))[f]
    span = (0.60, 1.08, 0.80)[f]
    for sx in (-1, 1):
        for k in range(6):
            L = span * (1.0 - k * 0.11)
            sw = math.radians(14 + k * 7)          # swept back
            # anchor the inner end at the shoulder — offset by the full span
            # leaves a visible gap and the wings read as detached plates
            wq = sphere((sx * (0.10 + L * 0.30), 0.04 + k * 0.10, 0.80 + math.sin(tilt) * L * 0.52),
                        0.19, feather if k % 2 == 0 else sheen)
            wq.scale = (L * 1.60, 0.055, 0.14)
            wq.rotation_euler = (0, -sx * tilt, sx * sw)
    for k in range(5):                              # fanned tail
        t = sphere((0, 0.44 + k * 0.05, 0.66 - k * 0.02), 0.16, feather)
        t.scale = (0.26, 1.55, 0.075)
        t.rotation_euler = (math.radians(-14), 0, math.radians((k - 2) * 10))
    for sx in (-1, 1):
        cyl((sx * 0.09, 0.12, 0.47), 0.021, 0.20, beak, rot=(math.radians(30), 0, 0), verts=6)

def nightshade_sprite(f):
    skin = mat('Skin', (0.30, 0.20, 0.34), rough=0.62)
    gown = mat('Gown', (0.055, 0.020, 0.095), rough=0.9)
    trim = mat('Trim', (0.34, 0.10, 0.46), rough=0.6)
    spark = glow('Spark', (0.85, 0.35, 1.0), 16.0)
    bob = (0.06, 0.0, -0.06)[f]
    body = sphere((0, 0, 0.92 + bob), 0.20, gown); body.scale = (0.78, 0.68, 1.18)
    sphere((0, -0.06, 1.24 + bob), 0.155, skin)
    eyes(0, -0.21, 1.25 + bob, 0.042, (1.0, 0.30, 0.92), 34.0)
    for k in range(9):           # dark hair
        a = k / 9 * 6.28
        hq = sphere((math.cos(a) * 0.12, math.sin(a) * 0.10 - 0.03, 1.34 + bob), 0.115, gown)
        hq.scale = (1, 0.8, 1.35)
    for k in range(10):          # tattered gown
        a = k / 10 * 6.28
        s = sphere((math.cos(a) * 0.19, math.sin(a) * 0.15, 0.60 + bob - abs(math.sin(a * 2)) * 0.13),
                   0.16, gown if k % 3 else trim)
        s.scale = (0.9, 0.72, 1.7)
    for sx in (-1, 1):
        cyl((sx * 0.21, -0.05, 0.92 + bob), 0.034, 0.34, skin,
            rot=(0, math.radians(sx * 40), 0), verts=8)
    wt = (math.radians(30), math.radians(-4), math.radians(-32))[f]
    pane = bpy.data.materials.new('Pane'); pane.use_nodes = True
    pb = pane.node_tree.nodes['Principled BSDF']
    pb.inputs['Base Color'].default_value = (0.50, 0.22, 0.92, 1)
    pb.inputs['Roughness'].default_value = 0.10
    try: pb.inputs['Emission Color'].default_value = (0.42, 0.16, 0.85, 1)
    except Exception: pass
    try: pb.inputs['Emission Strength'].default_value = 1.5
    except Exception: pass
    for sx in (-1, 1):
        for (dz, ln) in ((0.30, 0.64), (0.05, 0.48)):
            wq = sphere((sx * 0.34, 0.17, 1.00 + dz + bob), 0.30, pane)
            wq.scale = (ln * 1.35, 0.045, 0.56)
            wq.rotation_euler = (0, -sx * wt, sx * math.radians(22))
    random.seed(f * 13 + 3)
    for k in range(10):
        sphere((random.uniform(-0.40, 0.40), random.uniform(-0.12, 0.28),
                random.uniform(0.22, 1.38) + bob), random.uniform(0.020, 0.036), spark)

BUILD = {0: thorn_goblin, 1: cursed_raven, 2: nightshade_sprite}
# key / rim / ambient tuned per villain: low ambient keeps them dark, a strong
# coloured RIM from behind cuts the silhouette out of the pastel background.
LIGHT = {0: ((1.00, 0.86, 0.62), 150, (1.0, 0.52, 0.22), 320, (0.10, 0.11, 0.10)),
         1: ((0.88, 0.90, 1.00), 130, (0.85, 0.35, 1.00), 340, (0.09, 0.09, 0.13)),
         2: ((0.80, 0.68, 1.00), 120, (0.95, 0.40, 1.00), 360, (0.08, 0.05, 0.13))}

import sys
only = None
for a in sys.argv:
    if a.startswith('--only='): only = a.split('=', 1)[1]

for tp in (0, 1, 2):
    for f in range(3):
        if only and only != f'{tp}{f}': continue
        sc = reset_scene()
        kcol, kE, rcol, rE, amb = LIGHT[tp]
        w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
        w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.30
        w.node_tree.nodes['Background'].inputs['Color'].default_value = (*amb, 1)
        BUILD[tp](f)
        area_light((-2.0, -2.4, 2.4), kE, 2.4, kcol, (math.radians(52), 0, math.radians(-34)))
        area_light((2.2, -1.8, 1.0), 55, 2.0, (0.55, 0.62, 0.90), (math.radians(68), 0, math.radians(38)))
        area_light((0, 2.6, 1.9), rE, 2.2, rcol, (math.radians(-62), 0, math.radians(180)))
        d = bpy.data.cameras.new('C'); d.type = 'ORTHO'; d.ortho_scale = 2.05
        c = bpy.data.objects.new('C', d); sc.collection.objects.link(c)
        th = math.radians(6)
        c.location = (0, -5.0 * math.cos(th), 2.05 * 304 / 272 / 2 + 5.0 * math.sin(th))
        c.rotation_euler = (math.radians(84), 0, 0)
        sc.camera = c
        render_to(os.path.join(OUT, f'foe_{tp}_{f}.png'), 272, 304, transparent=True, samples=110)
        print(f'FOE_{tp}_{f}_DONE')
print('FOES_DONE')
