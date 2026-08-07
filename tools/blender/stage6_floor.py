FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())
import random
random.seed(61)

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles\floor_6.png"

sc = reset_scene()

w = bpy.data.worlds.new('W'); w.use_nodes = True
bg = w.node_tree.nodes['Background']
bg.inputs[0].default_value = (0.35, 0.38, 0.42, 1)
bg.inputs[1].default_value = 0.10
sc.world = w

# dark mossy grout base (green stays subtle, raised so light reaches it)
moss = stone_mat('Moss', tone=(0.05, 0.085, 0.038), rough=0.95, scale=14.0, bump=0.5)
plane((0, 0, -0.05), 3.2, moss, name='Grout')

tones = [(0.21, 0.21, 0.24), (0.17, 0.18, 0.20), (0.24, 0.21, 0.17),
         (0.16, 0.19, 0.18), (0.20, 0.20, 0.19)]
mats = []
for i, t in enumerate(tones):
    m = stone_mat('Slab%d' % i, tone=t, rough=0.9, scale=8.0, bump=0.85)
    for n in m.node_tree.nodes:
        if n.type == 'VALTORGB':
            n.color_ramp.elements[0].color = (t[0]*0.35, t[1]*0.35, t[2]*0.35, 1)
            n.color_ramp.elements[1].color = (t[0]*1.4, t[1]*1.4, t[2]*1.4, 1)
    mats.append(m)

# irregular flagstone layout: (cx, cy, sx, sy)
slabs = [
    (-0.62,  0.78, 0.84, 0.52),
    ( 0.28,  0.78, 0.84, 0.52),
    ( 0.90,  0.78, 0.36, 0.52),
    (-0.35,  0.12, 1.37, 0.66),
    ( 0.70,  0.12, 0.70, 0.66),
    (-0.70, -0.66, 0.70, 0.82),
    ( 0.10, -0.66, 0.82, 0.82),
    ( 0.82, -0.66, 0.54, 0.82),
]
for i, (cx, cy, sx, sy) in enumerate(slabs):
    o = cube((cx + random.uniform(-0.008, 0.008), cy + random.uniform(-0.008, 0.008),
              -0.06 + random.uniform(-0.012, 0.012)),
             (sx, sy, 0.12),
             mats[i % len(mats)],
             rot=(0, 0, random.uniform(-0.025, 0.025)), name='Slab%d' % i)
    m = o.modifiers.new('bv', 'BEVEL'); m.width = 0.022; m.segments = 2

# raking warm key (accentuates bump + slab edges) + weak cool fill
area_light((-2.4, -2.0, 1.5), 170, 3.0, (1, 0.88, 0.72), (math.radians(52), 0, math.radians(-50)))
area_light((2.0, 1.8, 2.4), 55, 3.0, (0.7, 0.78, 1.0), (math.radians(-35), 0, math.radians(-45)))

floor_cam()
render_to(OUT, 192, 192, transparent=False, samples=160)
