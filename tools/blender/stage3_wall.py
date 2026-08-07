FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles\wall_3.png"

reset_scene()

# --- materials ---
cream   = marble_mat('CreamWall', base=(0.76, 0.62, 0.40), vein=(0.55, 0.42, 0.24), rough=0.35)
whitem  = marble_mat('WhiteMarble', base=(0.94, 0.92, 0.89), vein=(0.45, 0.45, 0.52), rough=0.18)
gold    = gold_mat()
mirror  = metal_mat('Mirror', tone=(0.9, 0.9, 0.95), rough=0.05, metallic=1.0)
velvet  = fabric_mat('Velvet', tone=(0.14, 0.015, 0.36), rough=0.85)
velvet.node_tree.nodes['Principled BSDF'].inputs['Sheen Weight'].default_value = 0.3
darkbar = metal_mat('DarkBar', tone=(0.04, 0.035, 0.03), rough=0.6, metallic=0.0)
sky     = emissive_mat('SkyGlow', color=(1.0, 0.72, 0.38), strength=1.6)

# --- wall backdrop (y=0.12) ---
plane((0, 0.12, 0), 4.5, cream, rot=(math.pi/2, 0, 0), name='Wall')

# gold cornice / baseboard
cube((0, 0.08, 0.97), (1.6, 0.05, 0.07), gold, name='Cornice')
cube((0, 0.08, -0.97), (1.6, 0.05, 0.07), gold, name='Baseboard')

# --- gilded frame (slightly bigger, behind mirror) ---
cube((0, 0.045, -0.235), (0.74, 0.04, 1.07), gold, name='FrameRect')
cyl((0, 0.04, 0.30), 0.37, 0.05, gold, rot=(math.pi/2, 0, 0), verts=64, name='FrameArch')

# --- arched mirror (arch sits slightly proud of rect to avoid coplanar z-fighting) ---
cube((0, 0.024, -0.235), (0.62, 0.02, 1.03), mirror, name='MirrorRect')
cyl((0, 0.016, 0.30), 0.31, 0.012, mirror, rot=(math.pi/2, 0, 0), verts=64, name='MirrorArch')

# crest ornament above arch
sphere((0, 0.04, 0.74), 0.07, gold, name='Crest')
sphere((-0.13, 0.05, 0.69), 0.045, gold, name='CrestL')
sphere((0.13, 0.05, 0.69), 0.045, gold, name='CrestR')

# --- white marble pilasters with gold capitals ---
for sx in (-0.55, 0.55):
    cube((sx, 0.07, 0.0), (0.16, 0.08, 1.8), whitem, name='Pilaster')
    cube((sx, 0.06, 0.87), (0.22, 0.09, 0.10), gold, name='Capital')
    cube((sx, 0.06, -0.87), (0.22, 0.09, 0.10), gold, name='PlinthG')

# --- purple velvet drape, left edge, in front ---
folds = [(-0.78, -0.10, 0.060), (-0.70, -0.17, 0.075), (-0.62, -0.11, 0.050)]
for fx, fy, fr in folds:
    cyl((fx, fy, 0.05), fr, 2.0, velvet, verts=24, name='Fold')
# diagonal swag fold at top
cyl((-0.60, -0.13, 0.92), 0.06, 0.55, velvet, rot=(0, math.radians(62), 0), verts=24, name='Swag')
# gold tie band
cube((-0.68, -0.20, -0.10), (0.26, 0.05, 0.07), gold, rot=(0, math.radians(-8), 0), name='Tie')

# --- backdrop behind camera: warm glow + window mullions -> seen only in mirror ---
plane((0, -9, 0), 14, sky, rot=(-math.pi/2, 0, 0), name='SkyPlane')
for bx in (-0.24, 0.04, 0.32):
    cube((bx, -8.5, 0), (0.09, 0.05, 8), darkbar, name='BarV')
for bz in (-0.35, 0.18):
    cube((0, -8.5, bz), (8, 0.05, 0.09), darkbar, name='BarH')

# --- lighting ---
warm_rig()
point_light((0.35, -1.4, 0.55), 60, (1, 0.8, 0.5))
point_light((-0.55, -1.1, 0.2), 45, (1, 0.75, 0.55))

wall_cam()
render_to(OUT, 288, 384, transparent=False, samples=160)
