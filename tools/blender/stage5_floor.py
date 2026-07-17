FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())

reset_scene()

def flatten_rough(mat, lo, hi):
    for n in mat.node_tree.nodes:
        if n.type == 'VALTORGB':
            n.color_ramp.elements[0].color = (lo, lo, lo, 1)
            n.color_ramp.elements[1].color = (hi, hi, hi, 1)

deck = metal_mat('Deck', tone=(0.06, 0.07, 0.10), rough=0.45)
flatten_rough(deck, 0.34, 0.50)
tread = metal_mat('Tread', tone=(0.13, 0.14, 0.19), rough=0.32)
flatten_rough(tread, 0.24, 0.38)
under = metal_mat('Under', tone=(0.015, 0.02, 0.035), rough=0.7)
glow = emissive_mat('Seam', color=(0.12, 0.5, 1.0), strength=8.0)

# Sub-floor (bottom of grooves)
plane((0, 0, -0.035), 2.8, under, name='Under')

# 2x2 large deck plates with grooves between (top surface z=0.025)
for px in (-0.5, 0.5):
    for py in (-0.5, 0.5):
        cube((px, py, 0), (0.94, 0.94, 0.05), deck, name='Plate')

# Glowing blue seam grid in the grooves (center cross + edges for tiling)
for c in (-1.0, 0.0, 1.0):
    cube((c, 0, -0.006), (0.048, 2.7, 0.02), glow, name='SeamV')
    cube((0, c, -0.006), (2.7, 0.048, 0.02), glow, name='SeamH')

# Raised tread rectangles, staggered orientation (diamond-plate feel)
for px in (-0.5, 0.5):
    for py in (-0.5, 0.5):
        for ix, ox in enumerate((-0.28, 0.0, 0.28)):
            for iy, oy in enumerate((-0.28, 0.0, 0.28)):
                rz = 0.0 if (ix + iy) % 2 == 0 else math.pi / 2
                cube((px + ox, py + oy, 0.033), (0.20, 0.07, 0.016),
                     tread, rot=(0, 0, rz), name='Tread')

floor_cam()
# much dimmer: warm key upper-left, cool fill lower-right
area_light((-1.2, 1.2, 2.6), 90, 4.0, (1.0, 0.9, 0.72),
           rot=(math.radians(-18), math.radians(-18), 0))
area_light((1.4, -1.4, 2.2), 42, 4.0, (0.6, 0.72, 1.0),
           rot=(math.radians(18), math.radians(18), 0))

render_to(r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles\floor_5.png",
          192, 192, transparent=False, samples=160)
