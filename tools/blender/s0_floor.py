import math, random
FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())
random.seed(23)

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles\floor_0.png"

sc = reset_scene()
floor_cam()

w = bpy.data.worlds.new('World'); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes['Background']
bg.inputs[0].default_value = (0.015, 0.012, 0.01, 1)
bg.inputs[1].default_value = 0.5

def parquet_mat():
    # dark oak with per-object grain offset + per-object tone tint (ObjectInfo.Random)
    m = bpy.data.materials.new('Parquet'); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord')
    oi = nt.nodes.new('ShaderNodeObjectInfo')
    m1 = nt.nodes.new('ShaderNodeMath'); m1.operation = 'MULTIPLY'; m1.inputs[1].default_value = 41.3
    m2 = nt.nodes.new('ShaderNodeMath'); m2.operation = 'MULTIPLY'; m2.inputs[1].default_value = 17.7
    cmb = nt.nodes.new('ShaderNodeCombineXYZ')
    nt.links.new(oi.outputs['Random'], m1.inputs[0])
    nt.links.new(oi.outputs['Random'], m2.inputs[0])
    nt.links.new(m1.outputs[0], cmb.inputs['X'])
    nt.links.new(m2.outputs[0], cmb.inputs['Y'])
    add = nt.nodes.new('ShaderNodeVectorMath'); add.operation = 'ADD'
    nt.links.new(tc.outputs['Object'], add.inputs[0])
    nt.links.new(cmb.outputs[0], add.inputs[1])
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (1.0, 7.0, 1.0)
    nt.links.new(add.outputs[0], mp.inputs['Vector'])
    wave = nt.nodes.new('ShaderNodeTexWave')
    wave.inputs['Scale'].default_value = 5.5
    wave.inputs['Distortion'].default_value = 7.0
    wave.inputs['Detail'].default_value = 3.0
    nt.links.new(mp.outputs[0], wave.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.048, 0.019, 0.007, 1)
    ramp.color_ramp.elements[1].color = (0.160, 0.076, 0.026, 1)
    nt.links.new(wave.outputs['Fac'], ramp.inputs['Fac'])
    tint = nt.nodes.new('ShaderNodeValToRGB')
    tint.color_ramp.elements[0].color = (0.52, 0.39, 0.28, 1)
    tint.color_ramp.elements[1].color = (1.0, 0.90, 0.74, 1)
    nt.links.new(oi.outputs['Random'], tint.inputs['Fac'])
    mul = nt.nodes.new('ShaderNodeVectorMath'); mul.operation = 'MULTIPLY'
    nt.links.new(ramp.outputs['Color'], mul.inputs[0])
    nt.links.new(tint.outputs['Color'], mul.inputs[1])
    nt.links.new(mul.outputs[0], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.35
    bmp = nt.nodes.new('ShaderNodeBump'); bmp.inputs['Strength'].default_value = 0.15
    nt.links.new(wave.outputs['Fac'], bmp.inputs['Height'])
    nt.links.new(bmp.outputs[0], b.inputs['Normal'])
    return m

# dark underlay showing through plank gaps as joint lines
um = bpy.data.materials.new('Under'); um.use_nodes = True
ub = um.node_tree.nodes['Principled BSDF']
ub.inputs['Base Color'].default_value = (0.015, 0.009, 0.005, 1)
ub.inputs['Roughness'].default_value = 0.9
plane((0, 0, -0.06), 5, um, name='Under')

pm = parquet_mat()
L, Wd = 0.42, 0.123
colW = L * math.cos(math.radians(45))      # column spacing
dy = 0.132 * math.sqrt(2)                  # in-column spacing
for c in range(-4, 5):
    ang = math.radians(45 if c % 2 == 0 else -45)
    for k in range(-9, 10):
        y = k*dy + (dy/2 if c % 2 else 0.0)
        x = c * colW
        if abs(x) > 1.35 or abs(y) > 1.40:
            continue
        cube((x, y, -0.013 - random.random()*0.004), (L, Wd, 0.024), pm,
             rot=(0, 0, ang + random.uniform(-0.008, 0.008)), name='Plank')
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

# warm key from upper-left, cool fill opposite (overhead for top-down cam)
area_light((-1.5, -1.2, 3.0), 300, 3.5, (1.0, 0.84, 0.60),
           rot=(math.radians(20), math.radians(-15), 0))
area_light((1.6, 1.4, 2.7), 55, 3.0, (0.72, 0.80, 1.0),
           rot=(math.radians(-16), math.radians(13), 0))

render_to(OUT, 192, 192, transparent=False, samples=160)
