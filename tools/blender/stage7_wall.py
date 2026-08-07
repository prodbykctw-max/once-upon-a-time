# Stage 7 ART GALLERY - WALL tile (Louvre Grande Galerie)
FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())
import bpy, math

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles\wall_7.png"

reset_scene()

# ---------- materials ----------
burg = fabric_mat('Burgundy', tone=(0.35, 0.06, 0.10), rough=0.9)
# enrich the fabric: subtle vertical damask stripes + fine weave bump
bnt = burg.node_tree
bb = bnt.nodes['Principled BSDF']
btc = bnt.nodes.new('ShaderNodeTexCoord')
bwave = bnt.nodes.new('ShaderNodeTexWave')
bwave.inputs['Scale'].default_value = 3.0
bwave.inputs['Distortion'].default_value = 0.0
bnt.links.new(btc.outputs['Object'], bwave.inputs['Vector'])
bmix = bnt.nodes.new('ShaderNodeMix')
bmix.data_type = 'RGBA'
bmix.inputs[6].default_value = (0.32, 0.045, 0.085, 1)   # A dark stripe
bmix.inputs[7].default_value = (0.42, 0.075, 0.13, 1)    # B lighter stripe
bnt.links.new(bwave.outputs['Fac'], bmix.inputs[0])
bnt.links.new(bmix.outputs[2], bb.inputs['Base Color'])
bnoise = bnt.nodes.new('ShaderNodeTexNoise')
bnoise.inputs['Scale'].default_value = 90.0
bnoise.inputs['Detail'].default_value = 2.0
bnt.links.new(btc.outputs['Object'], bnoise.inputs['Vector'])
bbump = bnt.nodes.new('ShaderNodeBump')
bbump.inputs['Strength'].default_value = 0.08
bnt.links.new(bnoise.outputs['Fac'], bbump.inputs['Height'])
bnt.links.new(bbump.outputs[0], bb.inputs['Normal'])

gold = gold_mat('FrameGold')

white = bpy.data.materials.new('WainscotPaint')
white.use_nodes = True
wb = white.node_tree.nodes['Principled BSDF']
wb.inputs['Base Color'].default_value = (0.92, 0.90, 0.85, 1)
wb.inputs['Roughness'].default_value = 0.45

# ---------- canvas: procedural sunset landscape ----------
canvas = bpy.data.materials.new('SunsetCanvas')
canvas.use_nodes = True
cnt = canvas.node_tree
cb = cnt.nodes['Principled BSDF']
cb.inputs['Roughness'].default_value = 0.5

ctc = cnt.nodes.new('ShaderNodeTexCoord')
sep = cnt.nodes.new('ShaderNodeSeparateXYZ')
cnt.links.new(ctc.outputs['Object'], sep.inputs[0])
# vertical factor t = local y + 0.5  (0 bottom .. 1 top of canvas)
tadd = cnt.nodes.new('ShaderNodeMath')
tadd.operation = 'ADD'
tadd.inputs[1].default_value = 0.5
cnt.links.new(sep.outputs['Y'], tadd.inputs[0])

# sky gradient ramp: orange -> pink -> deep blue
sky = cnt.nodes.new('ShaderNodeValToRGB')
sky.color_ramp.elements[0].position = 0.0
sky.color_ramp.elements[0].color = (1.0, 0.30, 0.03, 1)
sky.color_ramp.elements[1].position = 1.0
sky.color_ramp.elements[1].color = (0.03, 0.09, 0.42, 1)
e = sky.color_ramp.elements.new(0.30)
e.color = (1.0, 0.55, 0.10, 1)
e = sky.color_ramp.elements.new(0.55)
e.color = (0.80, 0.28, 0.38, 1)
cnt.links.new(tadd.outputs[0], sky.inputs['Fac'])

# sun glow disc
sundist = cnt.nodes.new('ShaderNodeVectorMath')
sundist.operation = 'DISTANCE'
sundist.inputs[1].default_value = (0.14, -0.13, 0.0)
cnt.links.new(ctc.outputs['Object'], sundist.inputs[0])
sunmask = cnt.nodes.new('ShaderNodeMapRange')
sunmask.inputs['From Min'].default_value = 0.05
sunmask.inputs['From Max'].default_value = 0.22
sunmask.inputs['To Min'].default_value = 1.0
sunmask.inputs['To Max'].default_value = 0.0
cnt.links.new(sundist.outputs['Value'], sunmask.inputs['Value'])
sunmix = cnt.nodes.new('ShaderNodeMix')
sunmix.data_type = 'RGBA'
cnt.links.new(sky.outputs['Color'], sunmix.inputs[6])       # A = sky
sunmix.inputs[7].default_value = (1.0, 0.88, 0.55, 1)       # B = sun
cnt.links.new(sunmask.outputs[0], sunmix.inputs[0])

# dark noise hills band across the bottom
hmap = cnt.nodes.new('ShaderNodeMapping')
hmap.inputs['Scale'].default_value = (3.0, 0.4, 1.0)
cnt.links.new(ctc.outputs['Object'], hmap.inputs['Vector'])
hnoise = cnt.nodes.new('ShaderNodeTexNoise')
hnoise.inputs['Scale'].default_value = 2.0
hnoise.inputs['Detail'].default_value = 5.0
cnt.links.new(hmap.outputs[0], hnoise.inputs['Vector'])
hn1 = cnt.nodes.new('ShaderNodeMath'); hn1.operation = 'SUBTRACT'
hn1.inputs[1].default_value = 0.5
cnt.links.new(hnoise.outputs['Fac'], hn1.inputs[0])
hn2 = cnt.nodes.new('ShaderNodeMath'); hn2.operation = 'MULTIPLY'
hn2.inputs[1].default_value = 0.22
cnt.links.new(hn1.outputs[0], hn2.inputs[0])
hn3 = cnt.nodes.new('ShaderNodeMath'); hn3.operation = 'ADD'
cnt.links.new(tadd.outputs[0], hn3.inputs[0])
cnt.links.new(hn2.outputs[0], hn3.inputs[1])
hillmask = cnt.nodes.new('ShaderNodeValToRGB')
hillmask.color_ramp.interpolation = 'CONSTANT'
hillmask.color_ramp.elements[0].position = 0.0
hillmask.color_ramp.elements[0].color = (0, 0, 0, 1)
hillmask.color_ramp.elements[1].position = 0.27
hillmask.color_ramp.elements[1].color = (1, 1, 1, 1)
cnt.links.new(hn3.outputs[0], hillmask.inputs['Fac'])
hillmix = cnt.nodes.new('ShaderNodeMix')
hillmix.data_type = 'RGBA'
hillmix.inputs[6].default_value = (0.045, 0.025, 0.06, 1)   # A = dark hills
cnt.links.new(sunmix.outputs[2], hillmix.inputs[7])         # B = sky+sun
cnt.links.new(hillmask.outputs['Color'], hillmix.inputs[0])

cnt.links.new(hillmix.outputs[2], cb.inputs['Base Color'])
cnt.links.new(hillmix.outputs[2], cb.inputs['Emission Color'])
cb.inputs['Emission Strength'].default_value = 0.8

# ---------- geometry ----------
plane((0, 0.1, 0), 4, burg, rot=(math.pi/2, 0, 0), name='Wall')

# wainscot (white panel zone below z=-0.45)
cube((0, 0.06, -0.72), (1.6, 0.05, 0.52), white, name='Field')
cube((0, 0.035, -0.96), (1.6, 0.07, 0.10), white, name='Baseboard')
cube((0, 0.02, -0.46), (1.6, 0.07, 0.06), white, name='Rail')
cube((-0.37, 0.028, -0.71), (0.56, 0.03, 0.30), white, name='PanelL')
cube(( 0.37, 0.028, -0.71), (0.56, 0.03, 0.30), white, name='PanelR')

# ornate gold frame, center z=0.22, outer 1.0 x 1.1
cube((0, 0.03,  0.73), (1.00, 0.09, 0.08), gold, name='FrTop')
cube((0, 0.03, -0.29), (1.00, 0.09, 0.08), gold, name='FrBot')
cube((-0.46, 0.03, 0.22), (0.08, 0.09, 1.10), gold, name='FrL')
cube(( 0.46, 0.03, 0.22), (0.08, 0.09, 1.10), gold, name='FrR')
# inner lip
cube((0, 0.005,  0.633), (0.80, 0.045, 0.034), gold, name='LipTop')
cube((0, 0.005, -0.193), (0.80, 0.045, 0.034), gold, name='LipBot')
cube((-0.383, 0.005, 0.22), (0.034, 0.045, 0.86), gold, name='LipL')
cube(( 0.383, 0.005, 0.22), (0.034, 0.045, 0.86), gold, name='LipR')
# corner rosettes
for sx in (-0.46, 0.46):
    for sz in (-0.29, 0.73):
        sphere((sx, 0.0, sz), 0.06, gold)

# canvas
cv = plane((0, 0.055, 0.22), 1, canvas, rot=(math.pi/2, 0, 0), name='Canvas')
cv.scale = (0.88, 0.94, 1)

# brass picture light above frame
cyl((0, -0.04, 0.88), 0.035, 0.60, gold, rot=(0, math.pi/2, 0), name='LampTube')
cube((-0.20, 0.03, 0.90), (0.03, 0.14, 0.03), gold, name='ArmL')
cube(( 0.20, 0.03, 0.90), (0.03, 0.14, 0.03), gold, name='ArmR')

# ---------- lights / camera ----------
warm_rig()
area_light((0, -2.6, 0.2), 220, 3.0, (1, 0.93, 0.82), rot=(math.radians(90), 0, 0))
point_light((0, -0.18, 0.80), 18, (1, 0.72, 0.35), 0.05)

wall_cam()
render_to(OUT, 288, 384, transparent=False, samples=160)
