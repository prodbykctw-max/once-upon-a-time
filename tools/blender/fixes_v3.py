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

# ═══ WALL 7 v3: painting truly fills frame ═══
sc = reset_scene()
burg = fabric_mat('Burgundy', (0.11, 0.012, 0.03), rough=0.85)
plane((0, 0.14, 0.15), 3.2, burg, rot=(math.pi/2, 0, 0))
wain = stone_mat('Wainscot', (0.35, 0.34, 0.32), rough=0.5, scale=2, bump=0.05)
cube((0, 0.1, -0.92), (1.6, 0.06, 0.28), wain)
gmf = plain_metal('Frame', (0.7, 0.5, 0.13), 0.3)
cube((0, 0.07, -0.8), (1.6, 0.04, 0.03), gmf)
cnv = bpy.data.materials.new('Canvas'); cnv.use_nodes = True
nt = cnv.node_tree; b = nt.nodes['Principled BSDF']
b.inputs['Roughness'].default_value = 0.6
tc = nt.nodes.new('ShaderNodeTexCoord')
noise = nt.nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 2.2
noise.inputs['Detail'].default_value = 8.0
noise.inputs['Distortion'].default_value = 1.1
nt.links.new(tc.outputs['Object'], noise.inputs['Vector'])
ramp = nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = 0.28
ramp.color_ramp.elements[0].color = (0.35, 0.06, 0.015, 1)
e1 = ramp.color_ramp.elements.new(0.48); e1.color = (0.5, 0.25, 0.04, 1)
e2 = ramp.color_ramp.elements.new(0.6); e2.color = (0.14, 0.14, 0.32, 1)
ramp.color_ramp.elements[-1].color = (0.03, 0.035, 0.1, 1)
nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
pt = plane((0, 0.02, 0.22), 1.0, cnv, rot=(math.pi/2, 0, 0), name='Painting')
pt.scale = (1.02, 1.28, 1)   # fills 1.0 x 1.26 opening
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

# ═══ DECOR 7 v3: bust seated on pedestal ═══
sc = reset_scene()
w = bpy.data.worlds.new('W2'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.3
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.5, 0.52, 0.58, 1)
mb = marble_mat('Bust', (0.6, 0.59, 0.57), (0.45, 0.44, 0.45), rough=0.35)
ped = marble_mat('Ped', (0.3, 0.29, 0.28), (0.16, 0.15, 0.17), rough=0.5)
cube((0, 0, 0.07), (0.6, 0.6, 0.14), ped)
cyl((0, 0, 0.62), 0.19, 0.95, ped, verts=48)
for i in range(10):
    a = i / 10 * math.pi * 2
    cyl((math.cos(a) * 0.19, math.sin(a) * 0.19, 0.62), 0.03, 0.93, ped, verts=10)
cube((0, 0, 1.14), (0.52, 0.52, 0.1), ped)
cube((0, 0, 1.25), (0.34, 0.34, 0.12), mb)      # bust plinth
sh = sphere((0, 0.02, 1.5), 0.3, mb); sh.scale = (1.05, 0.55, 0.68)   # chest bottom ~1.30 sits on plinth top 1.31
cyl((0, 0, 1.74), 0.1, 0.24, mb)
hd = sphere((0, 0, 2.0), 0.21, mb); hd.scale = (0.85, 0.95, 1.12)
n = sphere((0, -0.17, 1.96), 0.05, mb); n.scale = (0.6, 1, 1.4)
hr = sphere((0, 0.05, 2.14), 0.2, mb); hr.scale = (0.9, 0.95, 0.6)
area_light((-1.6, -2.6, 2.8), 300, 2.8, (1, 0.96, 0.9), (math.radians(52), 0, math.radians(-26)))
area_light((2.0, -2.0, 1.4), 90, 2.4, (0.65, 0.7, 0.88), (math.radians(68), 0, math.radians(35)))
decor_cam()
render_to(os.path.join(OUT, 'decor_7.png'), 288, 480, transparent=True, samples=160)

# ═══ WALL 8 v2: medallion as metal, not glow ═══
sc = reset_scene()
random.seed(8)
dark = stone_mat('VaultStone', (0.035, 0.035, 0.05), rough=0.4, scale=5, bump=0.25)
plane((0, 0.12, 0), 3.2, dark, rot=(math.pi/2, 0, 0))
seam = plain_metal('Seam', (0.02, 0.02, 0.03), 0.6)
for z in (-0.65, 0.0, 0.65):
    cube((0, 0.08, z), (1.6, 0.02, 0.015), seam)
for x in (-0.5, 0.5):
    cube((x, 0.08, 0.33), (0.015, 0.02, 0.63), seam)
    cube((-x, 0.08, -0.33), (0.015, 0.02, 0.63), seam)
gm = plain_metal('Gold', (0.62, 0.44, 0.12), 0.32)
bpy.ops.mesh.primitive_torus_add(major_radius=0.3, minor_radius=0.035, location=(0, 0.02, 0.15))
tor = bpy.context.active_object; tor.rotation_euler = (math.pi/2, 0, 0); tor.data.materials.append(gm)
cyl((0, 0.06, 0.15), 0.22, 0.03, gm, rot=(math.pi/2, 0, 0), verts=48)
bpy.ops.mesh.primitive_torus_add(major_radius=0.12, minor_radius=0.02, location=(0, 0.0, 0.15))
tor2 = bpy.context.active_object; tor2.rotation_euler = (math.pi/2, 0, 0); tor2.data.materials.append(gm)
ruby = bpy.data.materials.new('Ruby'); ruby.use_nodes = True
rb = ruby.node_tree.nodes['Principled BSDF']
rb.inputs['Base Color'].default_value = (0.4, 0.01, 0.04, 1)
rb.inputs['Roughness'].default_value = 0.08
rb.inputs['Emission Color'].default_value = (0.8, 0.05, 0.1, 1)
rb.inputs['Emission Strength'].default_value = 1.2
sphere((0, -0.01, 0.15), 0.06, ruby)
gemcols = [(0.6, 0.05, 0.08), (0.05, 0.5, 0.15), (0.08, 0.15, 0.65), (0.55, 0.05, 0.5)]
random.seed(8)
for i in range(8):
    gx = random.uniform(-0.68, 0.68); gz = random.uniform(-1.0, 0.95)
    if abs(gx) < 0.42 and abs(gz - 0.15) < 0.42: continue
    col = gemcols[i % 4]
    g = bpy.data.materials.new(f'Gem{i}'); g.use_nodes = True
    gb = g.node_tree.nodes['Principled BSDF']
    gb.inputs['Base Color'].default_value = (*col, 1)
    gb.inputs['Roughness'].default_value = 0.05
    gb.inputs['Emission Color'].default_value = (*col, 1)
    gb.inputs['Emission Strength'].default_value = 1.6
    sphere((gx, 0.04, gz), random.uniform(0.025, 0.045), g)
area_light((0, -1.6, -1.4), 90, 2.5, (1, 0.72, 0.25), (math.radians(-55), 0, 0))
area_light((-1.8, -2.6, 2.2), 80, 3.0, (0.5, 0.55, 0.75), (math.radians(58), 0, math.radians(-28)))
point_light((0.9, -1.1, 1.1), 25, (1, 0.8, 0.4), 0.25)
wall_cam()
render_to(os.path.join(OUT, 'wall_8.png'), 288, 384, samples=160)

# ═══ DECOR 8 v2: readable open chest ═══
sc = reset_scene()
w = bpy.data.worlds.new('W3'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.3
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.5, 0.45, 0.35, 1)
wd = wood_mat('Chest', (0.12, 0.06, 0.03), grain_scale=7, rough=0.55)
wdin = wood_mat('ChestIn', (0.08, 0.04, 0.02), grain_scale=7, rough=0.6)
gm3 = plain_metal('Gold3', (0.75, 0.53, 0.14), 0.28)
iron = plain_metal('Band', (0.1, 0.09, 0.08), 0.5)
# body: 5 panels so it has an open interior
cube((0, 0, 0.14), (0.9, 0.6, 0.06), wdin, name='Bottom')
cube((0, 0.29, 0.4), (0.9, 0.06, 0.55), wd, name='Back')
cube((0, -0.29, 0.4), (0.9, 0.06, 0.55), wd, name='Front')
cube((-0.44, 0, 0.4), (0.06, 0.6, 0.55), wd, name='L')
cube((0.44, 0, 0.4), (0.06, 0.6, 0.55), wd, name='R')
for x in (-0.3, 0.3):
    cube((x, -0.3, 0.4), (0.08, 0.05, 0.57), iron)
cube((0, -0.32, 0.42), (0.1, 0.03, 0.12), gm3)  # clasp
# lid: thin, opened back ~65deg
lid = cube((0, 0.42, 0.82), (0.9, 0.5, 0.06), wd, name='Lid')
lid.rotation_euler = (math.radians(-65), 0, 0)
# coin heap: dome above rim
random.seed(888)
for i in range(60):
    a = random.uniform(0, math.pi * 2); r = random.uniform(0, 0.36) * random.uniform(0.5, 1)
    hx = math.cos(a) * r; hy = math.sin(a) * r * 0.6
    hz = 0.68 + (0.4 - r) * 0.55 + random.uniform(-0.02, 0.02)
    c = cyl((hx, hy, hz), random.uniform(0.05, 0.068), 0.016, gm3, verts=18)
    c.rotation_euler = (random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5), 0)
for i in range(9):
    c = cyl((random.uniform(-0.55, 0.55), random.uniform(-0.52, -0.38), 0.02), random.uniform(0.05, 0.065), 0.014, gm3, verts=18)
    c.rotation_euler = (random.uniform(-0.25, 0.25), random.uniform(-0.25, 0.25), 0)
# goblet leaning on chest
cyl((-0.62, -0.3, 0.1), 0.055, 0.2, gm3)
sphere((-0.62, -0.3, 0.24), 0.07, gm3)
# gems nested IN the heap
for i, col in enumerate([(0.7, 0.05, 0.1), (0.05, 0.6, 0.2), (0.4, 0.05, 0.6)]):
    g = bpy.data.materials.new(f'BigGem{i}'); g.use_nodes = True
    b2 = g.node_tree.nodes['Principled BSDF']
    b2.inputs['Base Color'].default_value = (*col, 1)
    b2.inputs['Roughness'].default_value = 0.05
    b2.inputs['Emission Color'].default_value = (*col, 1)
    b2.inputs['Emission Strength'].default_value = 2.5
    sphere((-0.18 + i * 0.18, -0.12, 0.86 + (i % 2) * 0.05), 0.065, g)
point_light((0, -0.15, 1.0), 22, (1, 0.75, 0.3), 0.2)
area_light((-1.6, -2.4, 2.4), 260, 2.8, (1, 0.9, 0.7), (math.radians(52), 0, math.radians(-26)))
area_light((1.8, -2.0, 1.0), 80, 2.2, (0.5, 0.55, 0.8), (math.radians(66), 0, math.radians(35)))
decor_cam()
render_to(os.path.join(OUT, 'decor_8.png'), 288, 480, transparent=True, samples=160)
print('FIXES_V3_DONE')
