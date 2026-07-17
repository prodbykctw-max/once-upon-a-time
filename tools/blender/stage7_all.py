import math, random, os
FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())
OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles"

# ═══ STAGE 7: ART GALLERY — Louvre Grande Galerie ═══

# ---- WALL: burgundy fabric + ornate gold-framed painting + wainscot + picture light ----
sc = reset_scene()
burg = fabric_mat('Burgundy', (0.17, 0.025, 0.05), rough=0.85)
plane((0, 0.14, 0.15), 3.2, burg, rot=(math.pi/2, 0, 0))
# white wainscot lower
wain = stone_mat('Wainscot', (0.4, 0.39, 0.37), rough=0.5, scale=2, bump=0.05)
cube((0, 0.1, -0.92), (1.6, 0.06, 0.28), wain)
cube((0, 0.07, -0.8), (1.6, 0.04, 0.03), gold_mat('WainTrim'))
# painting: procedural sunset landscape canvas
cnv = bpy.data.materials.new('Canvas'); cnv.use_nodes = True
nt = cnv.node_tree; b = nt.nodes['Principled BSDF']
b.inputs['Roughness'].default_value = 0.6
tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping')
nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
grad = nt.nodes.new('ShaderNodeTexGradient')
mp.inputs['Rotation'].default_value = (0, math.radians(-90), 0)
nt.links.new(mp.outputs[0], grad.inputs['Vector'])
ramp = nt.nodes.new('ShaderNodeValToRGB')
ramp.color_ramp.elements[0].position = 0.0
ramp.color_ramp.elements[0].color = (0.45, 0.12, 0.03, 1)   # sunset orange horizon
e1 = ramp.color_ramp.elements.new(0.45); e1.color = (0.35, 0.2, 0.08, 1)
e2 = ramp.color_ramp.elements.new(0.75); e2.color = (0.08, 0.1, 0.22, 1)  # dusk blue sky
ramp.color_ramp.elements[-1].color = (0.04, 0.05, 0.14, 1)
nt.links.new(grad.outputs['Fac'], ramp.inputs['Fac'])
# dark hills band via noise mixed over
noise = nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 4
nt.links.new(mp.outputs[0], noise.inputs['Vector'])
hills = nt.nodes.new('ShaderNodeValToRGB')
hills.color_ramp.elements[0].position = 0.48; hills.color_ramp.elements[0].color = (0, 0, 0, 1)
hills.color_ramp.elements[1].position = 0.52; hills.color_ramp.elements[1].color = (1, 1, 1, 1)
nt.links.new(noise.outputs['Fac'], hills.inputs['Fac'])
mixn = nt.nodes.new('ShaderNodeMix'); mixn.data_type = 'RGBA'; mixn.blend_type = 'MULTIPLY'
mixn.inputs[0].default_value = 0.35
nt.links.new(ramp.outputs['Color'], mixn.inputs['A'])
nt.links.new(hills.outputs['Color'], mixn.inputs['B'])
nt.links.new(mixn.outputs['Result'], b.inputs['Base Color'])
plane((0, 0.02, 0.22), 1.0, cnv, rot=(math.pi/2, 0, 0), name='Painting')
bpy.context.active_object.scale = (0.42, 0.55, 1)
# ornate gold frame (non-overlapping bars)
gm = gold_mat('Frame')
fw, fh, ft = 0.5, 0.63, 0.05
cube((0, 0.0, 0.22 + fh), (fw * 2 + ft * 2, 0.08, ft), gm)   # top
cube((0, 0.0, 0.22 - fh), (fw * 2 + ft * 2, 0.08, ft), gm)   # bottom
cube((-fw - ft/2, 0.0, 0.22), (ft, 0.08, fh * 2 - ft), gm)   # left
cube((fw + ft/2, 0.0, 0.22), (ft, 0.08, fh * 2 - ft), gm)    # right
sphere((0, -0.03, 0.22 + fh + 0.06), 0.05, gm)               # crest
# picture light
cyl((0, -0.12, 0.95), 0.02, 0.55, gm, rot=(0, math.pi/2, 0))
point_light((0, -0.18, 0.88), 45, (1, 0.85, 0.6), 0.12)
# lighting
area_light((-1.8, -2.8, 2.4), 240, 3.2, (0.98, 0.92, 0.85), (math.radians(56), 0, math.radians(-26)))
area_light((2.0, -2.4, 1.0), 70, 2.6, (0.7, 0.72, 0.85), (math.radians(70), 0, math.radians(30)))
wall_cam()
render_to(os.path.join(OUT, 'wall_7.png'), 288, 384, samples=160)

# ---- FLOOR: light oak herringbone parquet ----
sc = reset_scene()
random.seed(7)
plane((0, 0, -0.02), 4.4, stone_mat('Under', (0.06, 0.04, 0.03), rough=0.9, scale=4, bump=0.1))
pl, pw = 0.5, 0.125
for row in range(-6, 7):
    for col in range(-6, 7):
        x0 = col * pl * 0.72
        y0 = row * pl * 0.72
        ang = math.radians(45 if (row + col) % 2 == 0 else -45)
        tone = 0.24 + random.uniform(-0.05, 0.06)
        m = wood_mat(f'P{row}{col}', (tone, tone * 0.65, tone * 0.35), grain_scale=8, rough=0.3)
        cube((x0, y0, 0.01), (pl, pw, 0.02), m, rot=(0, 0, ang))
area_light((-1.4, -1.6, 3.0), 260, 3.5, (1, 0.93, 0.82), (math.radians(18), 0, math.radians(-22)))
area_light((1.6, 1.4, 2.6), 70, 3.0, (0.7, 0.75, 0.9), (math.radians(-16), 0, math.radians(18)))
floor_cam()
render_to(os.path.join(OUT, 'floor_7.png'), 192, 192, samples=160)

# ---- DECOR: marble bust on fluted pedestal (transparent) ----
sc = reset_scene()
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.3
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.5, 0.52, 0.58, 1)
mb = marble_mat('Bust', (0.55, 0.54, 0.52), (0.3, 0.29, 0.3), rough=0.35)
ped = marble_mat('Pedestal', (0.42, 0.41, 0.4), (0.22, 0.21, 0.23), rough=0.5)
# pedestal: base, fluted column, cap
cube((0, 0, 0.07), (0.56, 0.56, 0.14), ped)
col = cyl((0, 0, 0.75), 0.2, 1.2, ped, verts=48)
# flutes: vertical groove strips
for i in range(12):
    a = i / 12 * math.pi * 2
    cyl((math.cos(a) * 0.2, math.sin(a) * 0.2, 0.75), 0.028, 1.18, ped, verts=12)
cube((0, 0, 1.42), (0.5, 0.5, 0.1), ped)
# bust: shoulders, neck, head
sh = cube((0, 0, 1.62), (0.44, 0.24, 0.22), mb, name='Shoulders')
sh.rotation_euler = (0, 0, 0)
cyl((0, 0, 1.8), 0.09, 0.18, mb)
hd = sphere((0, 0, 2.0), 0.155, mb)
hd.scale = (0.9, 1.0, 1.18)
# subtle nose/brow suggestion
n = sphere((0, -0.13, 1.98), 0.045, mb); n.scale = (0.7, 1, 1.3)
area_light((-1.6, -2.6, 2.8), 260, 2.8, (1, 0.96, 0.9), (math.radians(52), 0, math.radians(-26)))
area_light((2.0, -2.0, 1.4), 80, 2.4, (0.65, 0.7, 0.88), (math.radians(68), 0, math.radians(35)))
decor_cam()
render_to(os.path.join(OUT, 'decor_7.png'), 288, 480, transparent=True, samples=160)
print('STAGE7_DONE')
