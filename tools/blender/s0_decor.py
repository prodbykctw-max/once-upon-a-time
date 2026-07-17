import math, random
FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())
random.seed(5)

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles\decor_0.png"

sc = reset_scene()
decor_cam()

# dim warm world so brass has something to reflect (film is transparent anyway)
w = bpy.data.worlds.new('World'); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes['Background']
bg.inputs[0].default_value = (0.04, 0.03, 0.02, 1)
bg.inputs[1].default_value = 0.8

brass = metal_mat('Brass', tone=(0.90, 0.60, 0.22), rough=0.24)
brassd = metal_mat('BrassDark', tone=(0.70, 0.44, 0.15), rough=0.34)

wax = bpy.data.materials.new('Wax'); wax.use_nodes = True
wb = wax.node_tree.nodes['Principled BSDF']
wb.inputs['Base Color'].default_value = (0.93, 0.90, 0.84, 1)
wb.inputs['Roughness'].default_value = 0.32
try:
    wb.inputs['Subsurface Weight'].default_value = 0.4
    wb.inputs['Subsurface Radius'].default_value = (0.05, 0.04, 0.02)
    wb.inputs['Subsurface Scale'].default_value = 0.05
except Exception:
    pass

flame = emissive_mat('Flame', color=(1.0, 0.42, 0.06), strength=9)
flame_core = emissive_mat('FlameCore', color=(1.0, 0.78, 0.38), strength=22)
wick = bpy.data.materials.new('Wick'); wick.use_nodes = True
wick.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.03, 0.02, 0.01, 1)

# ---- ornate circular base ----
cyl((0, 0, 0.035), 0.30, 0.07, brassd, name='Base1')
cyl((0, 0, 0.10), 0.22, 0.06, brass, name='Base2')
cyl((0, 0, 0.17), 0.13, 0.08, brassd, name='Base3')
sphere((0, 0, 0.26), 0.09, brass, name='BaseKnop')
for i in range(14):
    a = i * (2*math.pi/14)
    sphere((0.26*math.sin(a), 0.26*math.cos(a), 0.082), 0.028, brass, name='Bead')

# ---- central column with knops ----
cyl((0, 0, 0.875), 0.038, 1.15, brass, name='Column')
sphere((0, 0, 0.58), 0.078, brassd, name='Knop1')
sphere((0, 0, 0.95), 0.062, brass, name='Knop2')
cyl((0, 0, 1.22), 0.062, 0.05, brassd, name='Collar')
sphere((0, 0, 1.46), 0.072, brass, name='Capital')

# ---- 3 arms: center riser + two S-curved side arms (sphere chains) ----
def bez(p0, p1, p2, t):
    u = 1 - t
    return (u*u*p0[0] + 2*u*t*p1[0] + t*t*p2[0],
            u*u*p0[1] + 2*u*t*p1[1] + t*t*p2[1])

for sgn in (-1, 1):
    p0, p1, p2 = (0, 1.38), (sgn*0.36, 1.16), (sgn*0.48, 1.50)
    for i in range(13):
        t = i / 12.0
        px, pz = bez(p0, p1, p2, t)
        sphere((px, 0, pz), 0.033, brass, name='Arm')
    ex, ez = bez(p0, p1, p2, 0.5)
    sphere((ex, 0, ez - 0.02), 0.048, brassd, name='Elbow')
    sphere((ex, 0, ez - 0.085), 0.026, brass, name='Pendant')

# ---- drip pans + cups ----
for px, pz in ((-0.48, 1.53), (0.48, 1.53), (0.0, 1.52)):
    cyl((px, 0, pz), 0.10, 0.02, brass, name='Pan')
    cyl((px, 0, pz + 0.037), 0.055, 0.05, brassd, name='Cup')

# ---- candles, wicks, flames ----
candles = [(-0.48, 1.585, 0.30), (0.48, 1.585, 0.26), (0.0, 1.575, 0.36)]
for px, zb, h in candles:
    cyl((px, 0, zb + h/2), 0.036, h, wax, name='Candle')
    top = zb + h
    cyl((px, 0, top + 0.012), 0.004, 0.028, wick, name='Wick')
    fl = sphere((px, 0, top + 0.075), 0.031, flame, name='Flame')
    fl.scale = (1, 1, 2.2)
    fc = sphere((px, 0, top + 0.055), 0.014, flame_core, name='FlameCore')
    fc.scale = (1, 1, 1.8)
    point_light((px, -0.09, top + 0.07), 22, (1, 0.52, 0.18), 0.05)

# lighting: warm key / cool fill + soft front fill for brass reflections
warm_rig()
area_light((0, -5, 1.3), 150, 6.0, (1, 0.85, 0.65), rot=(math.radians(90), 0, 0))

render_to(OUT, 288, 480, transparent=True, samples=160)
