import math, os
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

sc = reset_scene()
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.15
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.6, 0.55, 0.5, 1)

lacq = bpy.data.materials.new('BlackLacquer'); lacq.use_nodes = True
lb = lacq.node_tree.nodes['Principled BSDF']
lb.inputs['Base Color'].default_value = (0.015, 0.013, 0.015, 1)
lb.inputs['Roughness'].default_value = 0.12
lb.inputs['Coat Weight'].default_value = 1.0
redsilk = fabric_mat('RedSilk', (0.32, 0.02, 0.04), rough=0.7)
goldm = plain_metal('GoldFit', (0.72, 0.52, 0.15), 0.28)
saya1 = bpy.data.materials.new('Saya1'); saya1.use_nodes = True
s1b = saya1.node_tree.nodes['Principled BSDF']
s1b.inputs['Base Color'].default_value = (0.28, 0.015, 0.03, 1)
s1b.inputs['Roughness'].default_value = 0.18
s1b.inputs['Coat Weight'].default_value = 1.0
saya2 = bpy.data.materials.new('Saya2'); saya2.use_nodes = True
s2b = saya2.node_tree.nodes['Principled BSDF']
s2b.inputs['Base Color'].default_value = (0.015, 0.04, 0.13, 1)
s2b.inputs['Roughness'].default_value = 0.18
s2b.inputs['Coat Weight'].default_value = 1.0
wrap = fabric_mat('Wrap', (0.05, 0.05, 0.06), rough=0.85)

# stepped base
cube((0, 0, 0.07), (0.95, 0.42, 0.14), lacq)
cube((0, 0, 0.16), (0.75, 0.32, 0.06), lacq)
cube((0, 0, 0.2), (0.6, 0.26, 0.03), redsilk)
# two posts, forks facing camera
for s in (-1, 1):
    cyl((s * 0.3, 0.05, 0.85), 0.05, 1.35, lacq, verts=20)
    for hz in (0.95, 1.35):
        for d in (-1, 1):
            f = cyl((s * 0.3, -0.04 + d * 0.05, hz), 0.02, 0.17, lacq, verts=10)
            f.rotation_euler = (math.radians(30 * d), 0, 0)
# sword 1 (upper, red saya): total span 1.16, centered
cyl((0.06, -0.06, 1.42), 0.036, 0.92, saya1, rot=(0, math.pi/2, 0), verts=18)
cyl((-0.52, -0.06, 1.42), 0.042, 0.26, wrap, rot=(0, math.pi/2, 0), verts=14)  # tsuka
cyl((-0.38, -0.06, 1.42), 0.06, 0.022, goldm, rot=(0, math.pi/2, 0), verts=18)  # tsuba
cyl((0.53, -0.06, 1.42), 0.037, 0.03, goldm, rot=(0, math.pi/2, 0), verts=18)   # kojiri cap
# sword 2 (lower, navy saya)
cyl((-0.06, -0.06, 1.02), 0.036, 0.92, saya2, rot=(0, math.pi/2, 0), verts=18)
cyl((0.52, -0.06, 1.02), 0.042, 0.26, wrap, rot=(0, math.pi/2, 0), verts=14)
cyl((0.38, -0.06, 1.02), 0.06, 0.022, goldm, rot=(0, math.pi/2, 0), verts=18)
cyl((-0.53, -0.06, 1.02), 0.037, 0.03, goldm, rot=(0, math.pi/2, 0), verts=18)
# red tassel hanging from upper-left fork
cyl((-0.3, -0.1, 0.62), 0.012, 0.3, redsilk)
sphere((-0.3, -0.1, 0.44), 0.04, redsilk)
# lighting: warm key, gold rim
area_light((-1.6, -2.5, 2.7), 300, 2.6, (1, 0.92, 0.8), (math.radians(52), 0, math.radians(-25)))
area_light((1.9, -1.9, 1.3), 110, 2.0, (0.75, 0.6, 0.45), (math.radians(64), 0, math.radians(38)))
point_light((0, -1.4, 1.8), 35, (1, 0.8, 0.5), 0.15)
decor_cam()
render_to(os.path.join(OUT, 'decor_2.png'), 288, 480, transparent=True, samples=160)
print('DECOR2_V3_DONE')
