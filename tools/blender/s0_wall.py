import math, random
FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())
random.seed(11)

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles\wall_0.png"

sc = reset_scene()
wall_cam()

# faint warm ambient world
w = bpy.data.worlds.new('World'); sc.world = w; w.use_nodes = True
bg = w.node_tree.nodes['Background']
bg.inputs[0].default_value = (0.03, 0.02, 0.012, 1)
bg.inputs[1].default_value = 0.6

dark_oak = wood_mat('DarkOak', tone=(0.048, 0.024, 0.010), grain_scale=7, rough=0.42)
rail_oak = wood_mat('RailOak', tone=(0.080, 0.040, 0.016), grain_scale=5, rough=0.38)
gold = gold_mat()

def leather_mat(name, tone, rough):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*tone, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Sheen Weight'].default_value = 0.15
    return m

# back panel (wall plane at y ~ 0.1+)
cube((0, 0.16, 0), (1.7, 0.08, 2.4), dark_oak, name='Back')

# shelf boards (5 boards -> 4 book rows)
for zb in (-1.0, -0.5, 0.0, 0.5, 1.0):
    cube((0, -0.02, zb), (1.52, 0.34, 0.05), rail_oak, name='Shelf')
    cube((0, -0.196, zb), (1.52, 0.012, 0.013), gold, name='ShelfTrim')

# carved side rails
for sx in (-0.71, 0.71):
    cube((sx, -0.05, 0), (0.10, 0.36, 2.4), rail_oak, name='Rail')
    cube((sx, -0.238, 0), (0.055, 0.024, 2.4), dark_oak, name='RailFace')
    cube((sx, -0.252, 0), (0.013, 0.008, 2.4), gold, name='RailGold')

# leather palette: DEEP saturated reds, greens, blues, browns
palette = [
    (0.28, 0.012, 0.018), (0.20, 0.008, 0.030), (0.34, 0.030, 0.012),
    (0.014, 0.115, 0.025), (0.008, 0.075, 0.040),
    (0.014, 0.035, 0.22), (0.008, 0.020, 0.13),
    (0.16, 0.062, 0.020), (0.095, 0.036, 0.013), (0.21, 0.10, 0.028),
]
leathers = []
for i, c in enumerate(palette):
    for k in range(2):
        f = random.uniform(0.8, 1.25)
        m = leather_mat('L%d_%d' % (i, k),
                        tone=(min(1, c[0]*f), min(1, c[1]*f), min(1, c[2]*f)),
                        rough=random.uniform(0.40, 0.55))
        leathers.append(m)

# books packed edge to edge, 4 rows
for zb in (-1.0, -0.5, 0.0, 0.5):
    zbase = zb + 0.025
    x = -0.645
    last = -1
    while True:
        bw = random.uniform(0.04, 0.09)
        if x + bw > 0.650:
            bw = 0.650 - x
            if bw < 0.035:
                break
        bh = random.uniform(0.28, 0.40)
        bd = random.uniform(0.16, 0.22)
        tilt = 0.0
        if random.random() < 0.16:
            tilt = random.uniform(-0.07, 0.07)
        mi = random.randrange(len(leathers))
        while mi == last:
            mi = random.randrange(len(leathers))
        last = mi
        cx = x + bw/2
        cz = zbase + bh/2 + abs(tilt)*bw*0.5
        cy = -0.035
        cube((cx, cy, cz), (bw*0.93, bd, bh), leathers[mi], rot=(0, tilt, 0), name='Book')
        # thin gold spine bands
        ct, st = math.cos(tilt), math.sin(tilt)
        by = cy - bd/2 - 0.004
        nb = random.choice((2, 2, 3))
        offs = [bh*0.36, bh*0.26]
        if nb == 3:
            offs.append(-bh*0.38)
        for dz in offs:
            cube((cx + dz*st, by, cz + dz*ct), (bw*0.88, 0.014, 0.012), gold,
                 rot=(0, tilt, 0), name='Band')
        x += bw + 0.004

# lighting: dimmer moody warm key / cool fill + candle glow from the left
area_light((-2.2, -3.0, 2.4), 220, 3.5, (1, 0.88, 0.72), (math.radians(60), 0, math.radians(-28)))
area_light((2.4, -2.6, 1.2), 65, 3.0, (0.70, 0.78, 1.0), (math.radians(75), 0, math.radians(30)))
point_light((-0.60, -0.50, 0.62), 42, (1, 0.55, 0.22), 0.06)
point_light((-0.62, -0.42, -0.35), 28, (1, 0.50, 0.20), 0.05)

render_to(OUT, 288, 384, transparent=False, samples=160)
