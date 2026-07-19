import bpy, math, os, random, sys
import mathutils
FRAMEWORK = r"C:\Users\Owner\Documents\once-upon-a-time\tools\blender\framework.py"
exec(open(FRAMEWORK).read())
REN = r"C:\Users\Owner\Documents\once-upon-a-time\assets\renders"
os.makedirs(os.path.join(REN, 'hall'), exist_ok=True)
os.makedirs(os.path.join(REN, 'prince'), exist_ok=True)

def flat(name, col, rough=0.7):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1)
    b.inputs['Roughness'].default_value = rough
    return m

def limb(p0, p1, r, m, verts=12):
    """Cylinder spanning p0->p1, oriented along the bone."""
    v = mathutils.Vector(p1) - mathutils.Vector(p0)
    mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, (p0[2] + p1[2]) / 2)
    o = cyl(mid, r, max(0.02, v.length), m, verts=verts)
    o.rotation_euler = v.to_track_quat('Z', 'Y').to_euler()
    return o

def glowm(name, col, s):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = (*col, 1); e.inputs['Strength'].default_value = s
    nt.links.new(e.outputs['Emission'], nt.nodes['Material Output'].inputs['Surface'])
    return m

# ═══════════════════════════════════════════════════════════════════
#  1. HALL TEXTURES — the library must be an enclosed room, not props
#     standing in a field. These tile along the length of the hall.
#     Pilasters sit on both edges so the repeat reads as architecture.
# ═══════════════════════════════════════════════════════════════════
BOOKCOLS = [(0.72, 0.16, 0.18), (0.16, 0.34, 0.66), (0.62, 0.48, 0.16),
            (0.14, 0.46, 0.26), (0.52, 0.28, 0.52), (0.70, 0.50, 0.20),
            (0.30, 0.16, 0.44), (0.74, 0.36, 0.14)]

def wall_tex():
    sc = reset_scene()
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.55
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.80, 0.70, 0.54, 1)
    oak = flat('Oak', (0.30, 0.17, 0.08), 0.55)
    warm = flat('Warm', (0.40, 0.24, 0.11), 0.5)
    back = flat('Back', (0.20, 0.12, 0.06), 0.8)
    cube((0, 0.30, 0), (2.0, 0.10, 2.0), back)              # carcass back
    random.seed(7)
    for s in range(5):                                       # 5 shelves of books
        zz = -0.86 + s * 0.44
        cube((0, 0.22, zz - 0.20), (2.0, 0.34, 0.05), warm)  # shelf board
        x = -0.94
        k = 0
        while x < 0.92:
            bw = random.uniform(0.048, 0.086)
            bh = random.uniform(0.24, 0.36)
            cube((x + bw / 2, 0.05, zz - 0.175 + bh / 2), (bw, 0.24, bh),
                 flat(f'B{s}{k}', random.choice(BOOKCOLS), 0.55),
                 rot=(random.uniform(-0.05, 0.05), 0, 0))
            x += bw + random.uniform(0.004, 0.012)
            k += 1
    for sx in (-1.0, 1.0):                                   # edge pilasters -> seamless repeat
        cube((sx, 0.10, 0), (0.14, 0.42, 2.0), warm)
        cube((sx, -0.06, 0), (0.06, 0.14, 2.0), oak)
    cube((0, 0.12, 0.98), (2.0, 0.44, 0.10), warm)           # cornice
    cube((0, 0.12, -0.97), (2.0, 0.44, 0.12), warm)          # base
    area_light((0, -3.0, 0), 520, 5.0, (1, 0.95, 0.86), (math.radians(90), 0, 0))
    area_light((-2.0, -2.0, 1.6), 140, 2.4, (1, 0.90, 0.70), (math.radians(60), 0, math.radians(-30)))
    d = bpy.data.cameras.new('C'); d.type = 'ORTHO'; d.ortho_scale = 2.0
    c = bpy.data.objects.new('C', d); sc.collection.objects.link(c)
    c.location = (0, -5.0, 0); c.rotation_euler = (math.radians(90), 0, 0)
    sc.camera = c
    render_to(os.path.join(REN, 'hall', 'wall.png'), 512, 512, samples=110)
    print('HALL_WALL_DONE')

def ceil_tex():
    sc = reset_scene()
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.5
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.78, 0.70, 0.56, 1)
    beam = flat('Beam', (0.34, 0.20, 0.10), 0.6)
    panel = flat('Panel', (0.62, 0.50, 0.34), 0.7)
    cube((0, 0.20, 0), (2.0, 0.10, 2.0), panel)
    for sx in (-1.0, 0.0, 1.0):                              # cross beams
        cube((sx, 0.02, 0), (0.20, 0.30, 2.0), beam)
    for sz in (-1.0, 0.0, 1.0):
        cube((0, 0.02, sz), (2.0, 0.30, 0.20), beam)
    for (px, pz) in ((-0.5, -0.5), (0.5, -0.5), (-0.5, 0.5), (0.5, 0.5)):
        cube((px, 0.06, pz), (0.62, 0.20, 0.62), flat('In', (0.70, 0.58, 0.40), 0.7))
        sphere((px, -0.10, pz), 0.10, glowm('Lamp', (1, 0.86, 0.58), 6.0))
    area_light((0, -3.0, 0), 700, 5.0, (1, 0.94, 0.82), (math.radians(90), 0, 0))
    d = bpy.data.cameras.new('C'); d.type = 'ORTHO'; d.ortho_scale = 2.0
    c = bpy.data.objects.new('C', d); sc.collection.objects.link(c)
    c.location = (0, -5.0, 0); c.rotation_euler = (math.radians(90), 0, 0)
    sc.camera = c
    render_to(os.path.join(REN, 'hall', 'ceil.png'), 512, 512, samples=100)
    print('HALL_CEIL_DONE')

# ═══════════════════════════════════════════════════════════════════
#  2. THE PRINCE — waiting at the end of the last stage. Seen from the
#     front (she runs toward him), so he needs a warm, open silhouette:
#     arms opening wider across the 3 frames as she closes the distance.
# ═══════════════════════════════════════════════════════════════════
def prince(f):
    skin = flat('Skin', (0.52, 0.34, 0.22), 0.62)
    hair = flat('Hair', (0.09, 0.06, 0.05), 0.75)
    coat = flat('Coat', (0.10, 0.20, 0.46), 0.62)
    cuff = flat('Cuff', (0.86, 0.72, 0.32), 0.42)
    trou = flat('Trou', (0.14, 0.13, 0.20), 0.7)
    boot = flat('Boot', (0.16, 0.11, 0.08), 0.5)
    sash = flat('Sash', (0.66, 0.12, 0.22), 0.7)
    gold = gold_mat('G')
    op = (0.22, 0.48, 0.75)[f]        # how far his arms have opened
    # legs
    for sx in (-1, 1):
        cyl((sx * 0.13, 0, 0.36), 0.085, 0.72, trou, verts=12)
        cube((sx * 0.13, -0.04, 0.05), (0.20, 0.30, 0.11), boot)
    # torso: tailored coat, tapered
    t = sphere((0, 0, 1.02), 0.30, coat); t.scale = (0.92, 0.62, 1.30)
    cube((0, 0, 0.74), (0.50, 0.34, 0.30), coat)
    # coat tails
    for sx in (-1, 1):
        ct = cube((sx * 0.16, 0.14, 0.58), (0.26, 0.14, 0.42), coat, rot=(0.12, 0, 0))
    # sash across the chest
    s2 = cube((0, -0.17, 1.02), (0.62, 0.06, 0.16), sash, rot=(0, math.radians(32), 0))
    for sx in (-1, 1):                # gold trim down the front
        cube((sx * 0.07, -0.19, 1.00), (0.035, 0.04, 0.52), cuff)
    # arms opening toward her — built as a joint chain. Placing rotated
    # cylinders by their centre detaches them from the shoulder, so span each
    # bone between its two joint positions instead.
    for sx in (-1, 1):
        shoulder = (sx * 0.28, -0.02, 1.22)
        elbow = (shoulder[0] + sx * (0.16 + 0.18 * op), shoulder[1] - 0.08 - 0.10 * op,
                 shoulder[2] - 0.34 + 0.08 * op)
        hand = (elbow[0] + sx * (0.13 + 0.20 * op), elbow[1] - 0.13 - 0.14 * op,
                elbow[2] - 0.22 + 0.18 * op)
        limb(shoulder, elbow, 0.072, coat)
        limb(elbow, hand, 0.061, coat)
        sphere(shoulder, 0.085, coat)          # deltoid caps the joint
        sphere(elbow, 0.062, coat)
        cyl(((elbow[0] + hand[0] * 3) / 4, (elbow[1] + hand[1] * 3) / 4,
             (elbow[2] + hand[2] * 3) / 4), 0.070, 0.06, cuff, verts=12)
        sphere(hand, 0.072, skin)
    # head
    h = sphere((0, -0.04, 1.46), 0.165, skin); h.scale = (0.94, 1.0, 1.14)
    for k in range(7):                # hair sweep
        a = k / 7 * 3.14
        hq = sphere((math.cos(a) * 0.13, -0.02 + math.sin(a) * 0.05, 1.58), 0.115, hair)
        hq.scale = (1, 0.95, 0.85)
    sphere((0, -0.14, 1.60), 0.155, hair).scale = (1.05, 0.75, 0.72)
    for sx in (-1, 1):                # eyes + warm smile line
        sphere((sx * 0.068, -0.20, 1.47), 0.022, flat('Eye', (0.06, 0.05, 0.05), 0.35))
    cube((0, -0.19, 1.385), (0.062, 0.03, 0.013), flat('Mouth', (0.34, 0.16, 0.14), 0.6))
    # circlet
    bpy.ops.mesh.primitive_torus_add(major_radius=0.185, minor_radius=0.018, location=(0, -0.03, 1.58))
    bpy.context.active_object.data.materials.append(gold)
    sphere((0, -0.21, 1.60), 0.035, gold)
    # a single rose held out on the last frame
    if f == 2:
        cyl((0.52, -0.34, 0.72), 0.012, 0.26, flat('Stem', (0.14, 0.30, 0.10), 0.85),
            rot=(math.radians(28), 0, 0), verts=6)
        sphere((0.545, -0.40, 0.85), 0.055, flat('Rose', (0.80, 0.10, 0.22), 0.65))

def render_prince():
    for f in range(3):
        sc = reset_scene()
        w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
        w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.40
        w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.62, 0.52, 0.44, 1)
        prince(f)
        # warm key from her side, golden rim behind him (he stands in the light)
        area_light((-2.0, -2.6, 2.4), 320, 2.8, (1, 0.92, 0.78), (math.radians(52), 0, math.radians(-32)))
        area_light((2.2, -2.0, 1.2), 110, 2.2, (0.70, 0.78, 0.96), (math.radians(66), 0, math.radians(34)))
        area_light((0, 2.8, 1.8), 420, 2.6, (1, 0.78, 0.46), (math.radians(-60), 0, math.radians(180)))
        # ortho_scale maps to the LARGER render dimension (here: height), so the
        # vertical span IS ortho_scale — aim at half of it to sit him on the
        # bottom edge. Frame is widened to 384 so his open arms do not clip.
        RX, RY, OSC = 384, 480, 2.15
        d = bpy.data.cameras.new('C'); d.type = 'ORTHO'; d.ortho_scale = OSC
        c = bpy.data.objects.new('C', d); sc.collection.objects.link(c)
        th = math.radians(5)
        c.location = (0, -5.0 * math.cos(th), OSC / 2 + 5.0 * math.sin(th))
        c.rotation_euler = (math.radians(85), 0, 0)
        sc.camera = c
        render_to(os.path.join(REN, 'prince', f'prince_{f}.png'), RX, RY, transparent=True, samples=120)
        print(f'PRINCE_{f}_DONE')

only = None
for a in sys.argv:
    if a.startswith('--only='): only = a.split('=', 1)[1]
if only in (None, 'hall'):
    wall_tex(); ceil_tex()
if only in (None, 'prince'):
    render_prince()
print('HALL_PRINCE_DONE')
