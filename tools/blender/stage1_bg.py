import math, random
FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\bgs\bg_1.png"

random.seed(7)
sc = reset_scene()
sc.cycles.transparent_max_bounces = 32

# --- world ambient (never pitch black) ---
w = bpy.data.worlds.new('W')
w.use_nodes = True
bgn = w.node_tree.nodes['Background']
bgn.inputs[0].default_value = (0.05, 0.035, 0.02, 1)
bgn.inputs[1].default_value = 1.0
sc.world = w

def apply_scale(o):
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.select_set(False)

# --- materials ---
sand_wall = stone_mat('SandWall', tone=(0.66, 0.44, 0.20), rough=0.9, scale=5.0, bump=0.4)
sand_col  = stone_mat('SandCol',  tone=(0.80, 0.54, 0.24), rough=0.8, scale=7.0, bump=0.3)
floor_m   = stone_mat('Floor',    tone=(0.52, 0.39, 0.22), rough=0.95, scale=6.0, bump=0.45)
path_m    = marble_mat('Path',    base=(0.82, 0.66, 0.42), vein=(0.50, 0.36, 0.20), rough=0.22)
ceil_m    = stone_mat('CeilBlue', tone=(0.14, 0.14, 0.30), rough=0.9, scale=4.0, bump=0.3)
gold = gold_mat()

def hiero_mat(name='Hiero'):
    m, nt, b = _new_mat(name)
    mp = _tex_coord_chain(nt, (1.0, 1.2, 3.0))
    brick = nt.nodes.new('ShaderNodeTexBrick')
    brick.inputs['Scale'].default_value = 1.6
    brick.inputs['Mortar Size'].default_value = 0.06
    brick.inputs['Color1'].default_value = (0.78, 0.52, 0.22, 1)
    brick.inputs['Color2'].default_value = (0.64, 0.38, 0.14, 1)
    brick.inputs['Mortar'].default_value = (0.22, 0.12, 0.04, 1)
    nt.links.new(mp.outputs[0], brick.inputs['Vector'])
    nt.links.new(brick.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.75
    inv = nt.nodes.new('ShaderNodeInvert')
    nt.links.new(brick.outputs['Fac'], inv.inputs['Color'])
    bn = nt.nodes.new('ShaderNodeBump')
    bn.inputs['Strength'].default_value = 0.7
    nt.links.new(inv.outputs[0], bn.inputs['Height'])
    nt.links.new(bn.outputs[0], b.inputs['Normal'])
    return m
hiero = hiero_mat()

def glowfade_mat(name, color, strength, fac):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    mix = nt.nodes.new('ShaderNodeMixShader')
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    em = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = (*color, 1)
    em.inputs['Strength'].default_value = strength
    mix.inputs['Fac'].default_value = fac
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs['Surface'])
    return m

# --- floor + central smooth path ---
o = cube((0, 17, -0.1), (16, 60, 0.2), floor_m, name='Floor'); apply_scale(o)
o = cube((0, 17, 0.005), (3.0, 60, 0.05), path_m, name='Path'); apply_scale(o)
# gold lane trims
for sx in (-1, 1):
    o = cube((1.55*sx, 17, 0.035), (0.08, 60, 0.05), gold, name='Trim'); apply_scale(o)

# --- walls + hieroglyph relief bands + gold trims ---
for sx in (-1, 1):
    o = cube((3.15*sx, 17, 2.0), (0.3, 52, 4.2), sand_wall, name='Wall'); apply_scale(o)
    o = cube((2.94*sx, 17, 1.9), (0.12, 52, 1.5), hiero, name='HieroBand'); apply_scale(o)
    for zt in (1.12, 2.68):
        o = cube((2.90*sx, 17, zt), (0.06, 52, 0.09), gold, name='GoldTrim'); apply_scale(o)

# --- columns with papyrus-bud capitals, 13 pairs ---
ys = [-1.5 + 3.5*i for i in range(13)]
for y in ys:
    for sx in (-1, 1):
        x = 2.35 * sx
        cyl((x, y, 0.14), 0.66, 0.28, sand_col, name='Base')
        cyl((x, y, 1.5), 0.46, 2.75, sand_col, name='Shaft')
        s = sphere((x, y, 3.05), 0.62, sand_col, name='Bud')
        s.scale = (1, 1, 0.75)
        cube((x, y, 3.7), (1.0, 1.0, 0.55), sand_col, name='Abacus')
        for (zr, mr, nr) in ((2.62, 0.47, 0.045), (2.80, 0.49, 0.04)):
            bpy.ops.mesh.primitive_torus_add(location=(x, y, zr), major_radius=mr, minor_radius=nr)
            t = bpy.context.active_object
            t.data.materials.append(gold)

# --- architraves over columns ---
for sx in (-1, 1):
    o = cube((2.35*sx, 17, 4.05), (1.1, 52, 0.35), sand_col, name='Architrave'); apply_scale(o)

# --- ceiling beams (deep blue) with lit slots between them ---
slot_glow = emissive_mat('SlotGlow', color=(1.0, 0.88, 0.62), strength=12.0)
for y in ys:
    o = cube((0, y, 4.3), (8, 2.6, 0.6), ceil_m, name='Beam'); apply_scale(o)
gaps = [y + 1.75 for y in ys[:-1]]
for gy in gaps:
    o = cube((0, gy, 4.55), (7, 0.7, 0.1), slot_glow, name='Slot'); apply_scale(o)
    area_light((0, gy, 3.95), energy=550, size=1.4, color=(1.0, 0.85, 0.58))

# --- visible god-ray shafts (transparent emissive planes) ---
shaft_m = glowfade_mat('Shaft', (1.0, 0.85, 0.55), 2.2, 0.10)
for gy in (0.25, 7.25, 14.25, 21.25, 28.25):
    p = plane((0.35, gy, 2.0), 4, shaft_m, rot=(math.pi/2, math.radians(10), 0), name='GodRay')
    p.scale = (0.38, 1.0, 1.1)
    p.visible_shadow = False

# --- depth haze layers ---
haze_m = glowfade_mat('Haze', (1.0, 0.80, 0.55), 0.7, 0.06)
for hy in (12, 20, 28, 36):
    p = plane((0, hy, 2.0), 12, haze_m, rot=(math.pi/2, 0, 0), name='Haze')
    p.visible_shadow = False

# --- far vanishing-point glow ---
plane((0, 39.4, 2.2), 11, emissive_mat('FarGlow', color=(1.0, 0.72, 0.35), strength=3.5), rot=(math.pi/2, 0, 0), name='FarGlow')
point_light((0, 36, 2.4), energy=1800, color=(1.0, 0.70, 0.35), radius=0.5)

# --- torch glow between columns ---
for ty in (1, 8, 15, 22, 29, 36):
    for sx in (-1, 1):
        point_light((2.05*sx, ty, 2.3), energy=90, color=(1.0, 0.52, 0.18), radius=0.08)

# --- near key + cool fill ---
area_light((0, -5.8, 3.4), energy=420, size=4.0, color=(1.0, 0.88, 0.70), rot=(math.radians(70), 0, 0))
area_light((0, -6.2, 1.2), energy=130, size=3.0, color=(0.70, 0.80, 1.0), rot=(math.radians(85), 0, 0))

# --- camera (game projection) ---
cam = persp_cam((0, -6, 1.5), (math.radians(90), 0, 0), lens=24)
cam.data.shift_y = 0.09
cam.data.clip_end = 200

render_to(OUT, 960, 540, transparent=False, samples=160)
