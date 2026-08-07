import math, random, os
FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())
OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles"

def plain_metal(name, tone, rough):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*tone, 1)
    b.inputs['Metallic'].default_value = 1.0
    b.inputs['Roughness'].default_value = rough
    return m

# ═══ STAGE 8: TREASURE VAULT ═══

# ---- WALL: near-black stone + gold medallion + gems + gold edge light ----
sc = reset_scene()
random.seed(8)
dark = stone_mat('VaultStone', (0.035, 0.035, 0.05), rough=0.4, scale=5, bump=0.25)
plane((0, 0.12, 0), 3.2, dark, rot=(math.pi/2, 0, 0))
# block seams
seam = plain_metal('Seam', (0.02, 0.02, 0.03), 0.6)
for z in (-0.65, 0.0, 0.65):
    cube((0, 0.08, z), (1.6, 0.02, 0.015), seam)
for x in (-0.5, 0.5):
    cube((x, 0.08, 0.33), (0.015, 0.02, 0.63), seam)
    cube((-x, 0.08, -0.33), (0.015, 0.02, 0.63), seam)
# gold medallion: torus + disc + inner ring
gm = plain_metal('Gold', (0.8, 0.58, 0.16), 0.22)
t = bpy.ops.mesh.primitive_torus_add(major_radius=0.3, minor_radius=0.035, location=(0, 0.02, 0.15))
tor = bpy.context.active_object; tor.rotation_euler = (math.pi/2, 0, 0); tor.data.materials.append(gm)
cyl((0, 0.06, 0.15), 0.22, 0.03, gm, rot=(math.pi/2, 0, 0), verts=48)
t2 = bpy.ops.mesh.primitive_torus_add(major_radius=0.12, minor_radius=0.02, location=(0, 0.0, 0.15))
tor2 = bpy.context.active_object; tor2.rotation_euler = (math.pi/2, 0, 0); tor2.data.materials.append(gm)
sphere((0, -0.01, 0.15), 0.06, plain_metal('Ruby', (0.5, 0.02, 0.05), 0.1))
# scattered gems
gemcols = [(0.6, 0.05, 0.08), (0.05, 0.5, 0.15), (0.08, 0.15, 0.65), (0.55, 0.05, 0.5)]
for i in range(8):
    gx = random.uniform(-0.68, 0.68); gz = random.uniform(-1.0, 0.95)
    if abs(gx) < 0.42 and abs(gz - 0.15) < 0.42: continue
    col = gemcols[i % 4]
    g = bpy.data.materials.new(f'Gem{i}'); g.use_nodes = True
    gb = g.node_tree.nodes['Principled BSDF']
    gb.inputs['Base Color'].default_value = (*col, 1)
    gb.inputs['Roughness'].default_value = 0.05
    gb.inputs['Emission Color'].default_value = (*col, 1)
    gb.inputs['Emission Strength'].default_value = 2.2
    s = sphere((gx, 0.04, gz), random.uniform(0.025, 0.045), g)
# gold edge lighting from below + dim cool key
area_light((0, -1.4, -1.3), 120, 2.5, (1, 0.72, 0.25), (math.radians(-55), 0, 0))
area_light((-1.8, -2.6, 2.2), 90, 3.0, (0.5, 0.55, 0.75), (math.radians(58), 0, math.radians(-28)))
point_light((0, -0.5, 0.15), 40, (1, 0.8, 0.35), 0.15)
wall_cam()
render_to(os.path.join(OUT, 'wall_8.png'), 288, 384, samples=160)

# ---- FLOOR: polished obsidian + gold coins ----
sc = reset_scene()
random.seed(88)
obs = marble_mat('Obsidian', (0.03, 0.03, 0.05), (0.09, 0.07, 0.13), rough=0.08)
plane((0, 0, 0), 4.4, obs)
gm2 = plain_metal('Coin', (0.82, 0.6, 0.18), 0.28)
for i in range(11):
    cx = random.uniform(-0.9, 0.9); cy = random.uniform(-0.9, 0.9)
    c = cyl((cx, cy, 0.012), random.uniform(0.05, 0.075), 0.012, gm2, verts=24)
    c.rotation_euler = (random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1), 0)
# warm reflection strip (glossy only)
strip = plane((0, 0, 2.5), 2.0, emissive_mat('Strip', (1, 0.8, 0.4), 4))
strip.visible_camera = False
strip.visible_diffuse = False
area_light((-1.4, -1.4, 2.8), 130, 3.0, (1, 0.85, 0.5), (math.radians(18), 0, math.radians(-22)))
floor_cam()
render_to(os.path.join(OUT, 'floor_8.png'), 192, 192, samples=160)

# ---- DECOR: overflowing treasure chest (transparent) ----
sc = reset_scene()
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.3
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.5, 0.45, 0.35, 1)
wd = wood_mat('Chest', (0.14, 0.075, 0.04), grain_scale=5, rough=0.55)
gm3 = plain_metal('Gold3', (0.8, 0.58, 0.16), 0.25)
iron = plain_metal('Band', (0.12, 0.1, 0.09), 0.5)
# chest body
cube((0, 0, 0.35), (0.85, 0.55, 0.5), wd, name='ChestBody')
# iron bands
for x in (-0.28, 0.28):
    cube((x, 0, 0.35), (0.07, 0.57, 0.52), iron)
# open lid (tilted back)
lid = cube((0, 0.3, 0.78), (0.85, 0.5, 0.1), wd, name='Lid')
lid.rotation_euler = (math.radians(-58), 0, 0)
# coin heap inside + spilling
random.seed(888)
for i in range(46):
    hx = random.uniform(-0.36, 0.36)
    hy = random.uniform(-0.2, 0.2)
    hz = 0.62 + (0.25 - (hx * hx + hy * hy)) * random.uniform(0.5, 1.0)
    c = cyl((hx, hy, hz), random.uniform(0.045, 0.06), 0.014, gm3, verts=20)
    c.rotation_euler = (random.uniform(-0.6, 0.6), random.uniform(-0.6, 0.6), 0)
for i in range(10):  # spill front
    c = cyl((random.uniform(-0.5, 0.5), random.uniform(-0.5, -0.32), 0.02), random.uniform(0.045, 0.06), 0.013, gm3, verts=20)
    c.rotation_euler = (random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3), 0)
# goblets
gb1 = cyl((-0.55, -0.15, 0.75), 0.06, 0.2, gm3); sphere((-0.55, -0.15, 0.88), 0.075, gm3)
# glowing gems on the pile
for i, col in enumerate([(0.7, 0.05, 0.1), (0.05, 0.6, 0.2), (0.4, 0.05, 0.6)]):
    g = bpy.data.materials.new(f'BigGem{i}'); g.use_nodes = True
    b2 = g.node_tree.nodes['Principled BSDF']
    b2.inputs['Base Color'].default_value = (*col, 1)
    b2.inputs['Roughness'].default_value = 0.05
    b2.inputs['Emission Color'].default_value = (*col, 1)
    b2.inputs['Emission Strength'].default_value = 3.5
    sphere((-0.2 + i * 0.2, -0.05, 0.95 + (i % 2) * 0.06), 0.07, g)
point_light((0, -0.1, 0.95), 30, (1, 0.75, 0.3), 0.2)  # glow from inside
area_light((-1.6, -2.4, 2.4), 240, 2.8, (1, 0.9, 0.7), (math.radians(52), 0, math.radians(-26)))
area_light((1.8, -2.0, 1.0), 70, 2.2, (0.5, 0.55, 0.8), (math.radians(66), 0, math.radians(35)))
decor_cam()
render_to(os.path.join(OUT, 'decor_8.png'), 288, 480, transparent=True, samples=160)

# ═══ FIX: STAGE 7 WALL v2 — painting fills the frame ═══
sc = reset_scene()
burg = fabric_mat('Burgundy', (0.11, 0.012, 0.03), rough=0.85)
plane((0, 0.14, 0.15), 3.2, burg, rot=(math.pi/2, 0, 0))
wain = stone_mat('Wainscot', (0.35, 0.34, 0.32), rough=0.5, scale=2, bump=0.05)
cube((0, 0.1, -0.92), (1.6, 0.06, 0.28), wain)
cube((0, 0.07, -0.8), (1.6, 0.04, 0.03), plain_metal('WT', (0.75, 0.55, 0.15), 0.3))
# abstract sunset canvas fills frame opening
cnv = bpy.data.materials.new('Canvas'); cnv.use_nodes = True
nt = cnv.node_tree; b = nt.nodes['Principled BSDF']
b.inputs['Roughness'].default_value = 0.6
tc = nt.nodes.new('ShaderNodeTexCoord')
noise = nt.nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 1.6
noise.inputs['Detail'].default_value = 6.0
noise.inputs['Distortion'].default_value = 0.8
nt.links.new(tc.outputs['Object'], noise.inputs['Vector'])
ramp = nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = 0.3
ramp.color_ramp.elements[0].color = (0.4, 0.08, 0.02, 1)
e1 = ramp.color_ramp.elements.new(0.5); e1.color = (0.5, 0.28, 0.05, 1)
e2 = ramp.color_ramp.elements.new(0.62); e2.color = (0.1, 0.12, 0.3, 1)
ramp.color_ramp.elements[-1].color = (0.03, 0.04, 0.12, 1)
nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
pt = plane((0, 0.02, 0.22), 1.0, cnv, rot=(math.pi/2, 0, 0), name='Painting')
pt.scale = (0.5, 0.63, 1)
gmf = plain_metal('Frame', (0.75, 0.55, 0.15), 0.3)
fw, fh, ft = 0.5, 0.63, 0.055
cube((0, 0.0, 0.22 + fh + ft/2), (fw * 2 + ft * 2, 0.08, ft), gmf)
cube((0, 0.0, 0.22 - fh - ft/2), (fw * 2 + ft * 2, 0.08, ft), gmf)
cube((-fw - ft/2, 0.0, 0.22), (ft, 0.08, fh * 2), gmf)
cube((fw + ft/2, 0.0, 0.22), (ft, 0.08, fh * 2), gmf)
sphere((0, -0.03, 0.22 + fh + ft + 0.05), 0.05, gmf)
cyl((0, -0.12, 1.0), 0.02, 0.6, gmf, rot=(0, math.pi/2, 0))
point_light((0, -0.2, 0.92), 40, (1, 0.85, 0.6), 0.12)
area_light((-1.8, -2.8, 2.4), 200, 3.2, (0.98, 0.92, 0.85), (math.radians(56), 0, math.radians(-26)))
area_light((2.0, -2.4, 1.0), 60, 2.6, (0.7, 0.72, 0.85), (math.radians(70), 0, math.radians(30)))
wall_cam()
render_to(os.path.join(OUT, 'wall_7.png'), 288, 384, samples=160)

# ═══ FIX: STAGE 7 DECOR v2 — proper bust proportions ═══
sc = reset_scene()
w = bpy.data.worlds.new('W2'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.3
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.5, 0.52, 0.58, 1)
mb = marble_mat('Bust', (0.6, 0.59, 0.57), (0.42, 0.41, 0.42), rough=0.35)
ped = marble_mat('Ped', (0.32, 0.31, 0.3), (0.18, 0.17, 0.19), rough=0.5)
cube((0, 0, 0.07), (0.6, 0.6, 0.14), ped)
cyl((0, 0, 0.62), 0.19, 0.95, ped, verts=48)
for i in range(10):
    a = i / 10 * math.pi * 2
    cyl((math.cos(a) * 0.19, math.sin(a) * 0.19, 0.62), 0.03, 0.93, ped, verts=10)
cube((0, 0, 1.14), (0.52, 0.52, 0.1), ped)
# bust on its own small plinth
cube((0, 0, 1.24), (0.3, 0.3, 0.08), mb)
sh = sphere((0, 0.02, 1.5), 0.3, mb); sh.scale = (1.05, 0.55, 0.62)   # shoulders/chest
cyl((0, 0, 1.72), 0.1, 0.22, mb)                                      # neck
hd = sphere((0, 0, 1.98), 0.21, mb); hd.scale = (0.85, 0.95, 1.12)    # head
n = sphere((0, -0.17, 1.94), 0.05, mb); n.scale = (0.6, 1, 1.4)       # nose
hr = sphere((0, 0.05, 2.12), 0.2, mb); hr.scale = (0.9, 0.95, 0.6)    # hair cap
area_light((-1.6, -2.6, 2.8), 300, 2.8, (1, 0.96, 0.9), (math.radians(52), 0, math.radians(-26)))
area_light((2.0, -2.0, 1.4), 90, 2.4, (0.65, 0.7, 0.88), (math.radians(68), 0, math.radians(35)))
decor_cam()
render_to(os.path.join(OUT, 'decor_7.png'), 288, 480, transparent=True, samples=160)
print('STAGE8_AND_FIXES_DONE')
