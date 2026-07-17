import math, os
FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())
OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles"

# STAGE 6 DECOR v2 — knightly plate armor, clean materials
sc = reset_scene()
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.4
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.5, 0.55, 0.65, 1)

def plain_metal(name, tone, rough):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*tone, 1)
    b.inputs['Metallic'].default_value = 1.0
    b.inputs['Roughness'].default_value = rough
    return m

plate = plain_metal('Plate', (0.42, 0.43, 0.48), 0.3)
dark = plain_metal('DarkIron', (0.06, 0.06, 0.07), 0.55)
goldm = plain_metal('Gold', (0.75, 0.55, 0.15), 0.25)
red = fabric_mat('Plume', (0.35, 0.03, 0.05), rough=0.85)

# base plinth
cyl((0, 0, 0.05), 0.32, 0.1, dark, verts=40)
# legs: greaves taper
for s in (-1, 1):
    g = cyl((s * 0.11, 0, 0.5), 0.062, 0.78, plate, verts=24)
    g.scale = (1, 1, 1)
    sphere((s * 0.11, 0, 0.92), 0.075, plate)  # poleyn (knee)
    sphere((s * 0.11, 0, 0.14), 0.07, plate)   # sabaton
# faulds (skirt) — tapered stacked rings
for i, r in enumerate((0.24, 0.21, 0.185)):
    c = cyl((0, 0, 1.02 + i * 0.07), r, 0.07, plate, verts=32)
# breastplate: rounded (scaled sphere over core)
bp = sphere((0, 0.02, 1.42), 0.26, plate); bp.scale = (0.95, 0.62, 0.78)
cube((0, 0, 1.17), (0.36, 0.2, 0.07), goldm, name='Belt')
# pauldrons + arms
for s in (-1, 1):
    p = sphere((s * 0.28, 0, 1.6), 0.125, plate)
    cyl((s * 0.31, 0, 1.32), 0.058, 0.42, plate, verts=20)
    sphere((s * 0.31, 0, 1.28), 0.062, plate)  # elbow couter
    cyl((s * 0.32, 0, 1.06), 0.05, 0.3, plate, verts=20)
    s2 = sphere((s * 0.33, 0, 0.9), 0.065, plate); s2.scale = (1, 1.25, 1)  # gauntlet
# gorget + helmet
cyl((0, 0, 1.66), 0.1, 0.1, plate, verts=24)
h = sphere((0, 0, 1.86), 0.15, plate); h.scale = (0.92, 1.02, 1.15)
# visor: dark horizontal slit + ridged snout
cube((0, -0.125, 1.86), (0.22, 0.05, 0.022), dark, name='VisorSlit')
v = sphere((0, -0.1, 1.8), 0.09, plate); v.scale = (0.8, 0.9, 0.7)
# red plume
pl = sphere((0, 0.06, 2.1), 0.06, red); pl.scale = (0.5, 1.1, 1.8)
pl.rotation_euler = (math.radians(-25), 0, 0)
# poleaxe: connected, held at gauntlet
haft = cyl((0.35, 0, 1.2), 0.02, 2.25, wood_mat('Haft', (0.13, 0.08, 0.045)))
cube((0.35 + 0.09, 0, 2.2), (0.18, 0.018, 0.16), plain_metal('Axe', (0.5, 0.51, 0.55), 0.22), name='AxeBlade')
cyl((0.35, 0, 2.36), 0.018, 0.14, plain_metal('Spike', (0.5, 0.51, 0.55), 0.22))
# lights: warm key, cool rim
area_light((-1.8, -2.6, 2.6), 280, 2.8, (1, 0.94, 0.85), (math.radians(54), 0, math.radians(-26)))
area_light((2.0, -2.0, 1.4), 100, 2.2, (0.55, 0.65, 0.9), (math.radians(66), 0, math.radians(38)))
point_light((0, -1.2, 0.3), 25, (1, 0.7, 0.4), 0.2)  # uplight for drama
decor_cam()
render_to(os.path.join(OUT, 'decor_6.png'), 288, 480, transparent=True, samples=160)
print('S6D_V2_DONE')
