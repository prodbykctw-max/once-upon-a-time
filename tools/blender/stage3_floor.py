FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles\floor_3.png"

reset_scene()

white = marble_mat('WhitePolished', base=(0.95, 0.94, 0.91), vein=(0.58, 0.58, 0.65), rough=0.05)
seam  = marble_mat('Seam', base=(0.16, 0.15, 0.17), vein=(0.10, 0.10, 0.12), rough=0.3)
gold  = metal_mat('InlayGold', tone=(0.92, 0.60, 0.10), rough=0.3, metallic=1.0)

plane((0, 0, 0), 5, white, name='Floor')

# tile seams: 1.0 spacing grid (tileable across the 2x2 frame)
for c in (-1.0, 0.0, 1.0):
    cube((c, 0, 0.002), (0.022, 4.4, 0.004), seam, name='SeamV')
    cube((0, c, 0.002), (4.4, 0.022, 0.004), seam, name='SeamH')

# gold diamonds at tile intersections
for gx in (-1.0, 0.0, 1.0):
    for gy in (-1.0, 0.0, 1.0):
        cube((gx, gy, 0.006), (0.20, 0.20, 0.006), gold, rot=(0, 0, math.pi/4), name='Dia')

# small gold accent diamonds at tile centers
for gx in (-0.5, 0.5):
    for gy in (-0.5, 0.5):
        cube((gx, gy, 0.005), (0.085, 0.085, 0.005), gold, rot=(0, 0, math.pi/4), name='DiaS')

# --- overhead emissive strips (hidden from camera, reflected by glossy marble) ---
# glossy-only: streak shows in the polished marble without washing the diffuse
strip1 = cube((0.35, 0.35, 2.6), (0.7, 5.5, 0.02), emissive_mat('WarmStrip', (1.0, 0.72, 0.32), 40.0),
              rot=(0, 0, math.radians(35)), name='Strip1')
strip1.visible_camera = False
strip1.visible_diffuse = False
strip2 = cube((-0.55, -0.45, 2.9), (0.45, 5.5, 0.02), emissive_mat('CoolStrip', (0.65, 0.78, 1.0), 9.0),
              rot=(0, 0, math.radians(-40)), name='Strip2')
strip2.visible_camera = False
strip2.visible_diffuse = False

# general lights, offset outside frame so they don't blow the ortho reflection
area_light((-2.2, 2.0, 2.8), 520, 4.0, (1, 0.9, 0.72), rot=(math.radians(-30), math.radians(-25), 0))
area_light((2.2, -1.8, 2.4), 180, 3.5, (0.75, 0.82, 1.0), rot=(math.radians(28), math.radians(28), 0))

floor_cam()
render_to(OUT, 192, 192, transparent=False, samples=160)
