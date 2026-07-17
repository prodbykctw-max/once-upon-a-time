FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())

reset_scene()

def flatten_rough(mat, lo, hi):
    for n in mat.node_tree.nodes:
        if n.type == 'VALTORGB':
            n.color_ramp.elements[0].color = (lo, lo, lo, 1)
            n.color_ramp.elements[1].color = (hi, hi, hi, 1)

body_m = metal_mat('Obelisk', tone=(0.04, 0.045, 0.07), rough=0.28)
flatten_rough(body_m, 0.20, 0.30)          # smooth dark metal, no granite speckle
trim_m = metal_mat('Trim', tone=(0.14, 0.15, 0.19), rough=0.35)
flatten_rough(trim_m, 0.26, 0.38)
vent_m = metal_mat('Vent', tone=(0.02, 0.02, 0.03), rough=0.6)
ring_glow = emissive_mat('Ring', color=(0.12, 0.5, 1.0), strength=3.2)
panel_glow = emissive_mat('Panel', color=(0.25, 0.6, 1.0), strength=2.2)

# Server obelisk: plinth, monolith body, cap, beacon
cube((0, 0, 0.05), (0.86, 0.56, 0.10), trim_m, name='Plinth')       # z 0.00-0.10
cube((0, 0, 1.10), (0.68, 0.42, 2.04), body_m, name='Body')         # z 0.08-2.12
cube((0, 0, 2.15), (0.56, 0.36, 0.08), trim_m, name='Cap')          # z 2.11-2.19
cube((0, 0, 2.22), (0.10, 0.10, 0.05), ring_glow, name='Beacon')

# 4 glowing blue rings wrapped around the monolith
for z in (0.45, 0.95, 1.45, 1.95):
    cube((0, 0, z), (0.74, 0.48, 0.05), ring_glow, name='Ring')

# Front details: vent slits near base, small status panel up high
for z in (0.20, 0.25, 0.30):
    cube((0, -0.215, z), (0.42, 0.02, 0.022), vent_m, name='VentSlit')
cube((0, -0.215, 1.70), (0.20, 0.02, 0.12), panel_glow, name='Status')

decor_cam()
# key (slightly warm) upper-left front, cool fill right, very faint blue point
area_light((-2.0, -2.5, 2.6), 380, 3.0, (1.0, 0.92, 0.8),
           rot=(math.radians(55), 0, math.radians(-30)))
area_light((2.2, -2.0, 1.2), 150, 3.0, (0.5, 0.65, 1.0),
           rot=(math.radians(70), 0, math.radians(35)))
point_light((0, -1.4, 0.8), 14, (0.3, 0.6, 1.0), radius=0.35)
point_light((0, -1.2, 1.95), 10, (0.3, 0.6, 1.0), radius=0.35)  # lift the dark top

render_to(r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles\decor_5.png",
          288, 480, transparent=True, samples=160)
