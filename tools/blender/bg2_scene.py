FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())
import math

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\bgs\bg_2.png"

sc = reset_scene()
sc.cycles.transparent_max_bounces = 24

# dark night-ish world so nothing is pure black but no wash
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs[0].default_value = (0.004, 0.005, 0.010, 1)

def simple_mat(name, color, rough=0.4, metallic=0.0, coat=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metallic
    try:
        b.inputs['Coat Weight'].default_value = coat
    except Exception:
        pass
    return m

def haze_mat(name, color=(1, 0.5, 0.25), strength=0.5, density=0.12):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    mix = nt.nodes.new('ShaderNodeMixShader')
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    em = nt.nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = (*color, 1)
    em.inputs['Strength'].default_value = strength
    mix.inputs['Fac'].default_value = density
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs['Surface'])
    return m

# ---------- materials ----------
floor_m   = wood_mat('Floor',    tone=(0.085, 0.048, 0.026), grain_scale=10, rough=0.10)  # polished dark wood
darkwood  = wood_mat('DarkWood', tone=(0.060, 0.035, 0.020), grain_scale=5,  rough=0.50)
beamwood  = wood_mat('Beam',     tone=(0.050, 0.030, 0.018), grain_scale=4,  rough=0.55)
red_lac   = simple_mat('RedLacquer', (0.52, 0.035, 0.030), rough=0.12, coat=1.0)
gold      = gold_mat('Gold')
shoji_glow   = emissive_mat('ShojiGlow',   color=(1.0, 0.86, 0.62), strength=3.0)
lantern_glow = emissive_mat('LanternGlow', color=(1.0, 0.50, 0.18), strength=14)
far_glow     = emissive_mat('FarGlow',     color=(1.0, 0.45, 0.15), strength=5)

# ---------- geometry : corridor along +Y ----------
# floor (top at z=0), ceiling, trims
cube((0, 17, -0.05), (8, 62, 0.1), floor_m, name='Floor')
cube(( 2.82, 17, 0.07), (0.35, 62, 0.14), darkwood)
cube((-2.82, 17, 0.07), (0.35, 62, 0.14), darkwood)
cube((0, 17, 4.08), (8, 62, 0.16), darkwood)
cube(( 1.3, 17, 3.85), (0.28, 62, 0.30), beamwood)
cube((-1.3, 17, 3.85), (0.28, 62, 0.30), beamwood)
cube((0, 17, 3.90), (0.24, 62, 0.24), beamwood)

# shoji walls: glowing panel + dark lattice in front
for sx in (1, -1):
    cube((sx * 3.10, 17, 1.40), (0.06, 62, 2.4), shoji_glow)
    cube((sx * 3.12, 17, 3.35), (0.12, 62, 1.6), darkwood)   # wall above shoji
    cube((sx * 3.12, 17, 0.10), (0.12, 62, 0.3), darkwood)   # baseboard
    for z in (0.35, 0.95, 1.55, 2.15, 2.55):                 # horizontal bars
        cube((sx * 3.00, 17, z), (0.035, 62, 0.05), darkwood)
    y = -6.0
    while y <= 40.0:                                         # vertical bars
        cube((sx * 3.00, y, 1.40), (0.035, 0.05, 2.4), darkwood)
        y += 0.7
    y = -5.6
    while y <= 40.0:                                         # thicker panel posts
        cube((sx * 2.98, y, 1.40), (0.06, 0.10, 2.5), darkwood)
        y += 2.8

# red lacquer pillars every 4m + gold bands, red header beams every 8m
py = -4.0
while py <= 40.0:
    for sx in (1, -1):
        cyl((sx * 2.6, py, 2.00), 0.17, 4.2, red_lac)
        cyl((sx * 2.6, py, 0.16), 0.21, 0.32, gold)
        cyl((sx * 2.6, py, 3.60), 0.20, 0.25, gold)
    if (py + 4) % 8 == 0:
        cube((0, py, 3.55), (5.6, 0.30, 0.34), red_lac)
    py += 4.0

# hanging paper lanterns (outside the running lane x in [-1.5,1.5])
ly = -2.0
while ly <= 38.0:
    for sx in (1, -1):
        x = sx * 1.85
        cyl((x, ly, 2.62), 0.17, 0.40, lantern_glow, verts=24)
        cyl((x, ly, 2.38), 0.05, 0.10, darkwood)
        cyl((x, ly, 3.30), 0.012, 1.00, darkwood)
        if ly <= 30.0:
            point_light((x, ly, 2.62), 45, (1, 0.55, 0.22), 0.12)
    ly += 4.0

# strong warm glow at the vanishing point
cube((0, 41.5, 2), (7, 0.1, 4.4), far_glow)

# depth haze planes across the hall (thicker further away)
for hy, d in ((14, 0.10), (22, 0.14), (30, 0.20), (38, 0.30)):
    cube((0, hy, 2), (7, 0.02, 4.4), haze_mat('Haze%d' % hy, (1.0, 0.5, 0.22), 0.5, d))

# cool fill from behind camera + warm bounce near foreground
area_light((0, -5.8, 3.0), 220, 4.0, (0.65, 0.75, 1.0), (math.radians(75), 0, 0))
point_light((0, -3.5, 3.4), 120, (1, 0.7, 0.4), 0.3)

# ---------- camera : game one-point perspective ----------
cam = persp_cam((0, -6, 1.5), (math.radians(90), 0, 0), lens=24)
cam.data.shift_y = 0.09
cam.data.clip_end = 200

render_to(OUT, 960, 540, transparent=False, samples=160)
