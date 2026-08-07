FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles\wall_1.png"

sc = reset_scene()

# warm ambient world so shadows are not pure black
w = bpy.data.worlds.new('W')
w.use_nodes = True
bg = w.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.45, 0.30, 0.15, 1)
bg.inputs['Strength'].default_value = 0.25
sc.world = w

# --- materials ---
sand      = stone_mat('Sand',     tone=(0.52, 0.30, 0.11), rough=0.85, scale=7.0, bump=0.55)
sand_band = stone_mat('SandBand', tone=(0.47, 0.27, 0.10), rough=0.88, scale=8.0, bump=0.35)
sand_dark = stone_mat('SandDark', tone=(0.29, 0.16, 0.06), rough=0.90, scale=9.0, bump=0.30)
groove    = stone_mat('Groove',   tone=(0.07, 0.04, 0.02), rough=0.95, scale=10.0, bump=0.2)
gold      = gold_mat('Gold')

# --- wall base plane (XZ, facing camera at -Y) ---
plane((0, 0.1, 0), 3.0, sand, rot=(math.pi/2, 0, 0), name='Wall')

# --- horizontal block seams (thin dark inset grooves, barely proud) ---
for z in (-0.72, -0.22, 0.28, 0.78, 0.965):
    cube((0, 0.092, z), (1.6, 0.03, 0.016), groove, name='HSeam')

# --- staggered vertical seams (running bond, calmer layout) ---
# rows A and C: center joint + outer joints; rows B and D: outer joints offset
cube((0.0,  0.092, 0.53), (0.024, 0.03, 0.50), groove)
cube((0.66, 0.092, 0.53), (0.024, 0.03, 0.50), groove)
cube((-0.66,0.092, 0.53), (0.024, 0.03, 0.50), groove)
cube((0.0,  0.092, -0.47), (0.024, 0.03, 0.50), groove)
cube((0.66, 0.092, -0.47), (0.024, 0.03, 0.50), groove)
cube((-0.66,0.092, -0.47), (0.024, 0.03, 0.50), groove)
cube((0.70, 0.092, 0.03), (0.024, 0.03, 0.50), groove)
cube((-0.70,0.092, 0.03), (0.024, 0.03, 0.50), groove)
cube((0.70, 0.092, -0.86), (0.024, 0.03, 0.30), groove)
cube((-0.70,0.092, -0.86), (0.024, 0.03, 0.30), groove)

# --- two raised hieroglyph panels (full height) ---
for px in (-0.42, 0.42):
    cube((px, 0.075, 0), (0.30, 0.05, 2.2), sand_band, name='Panel')
    # incised borders flanking each panel
    cube((px-0.165, 0.070, 0), (0.020, 0.045, 2.2), groove)
    cube((px+0.165, 0.070, 0), (0.020, 0.045, 2.2), groove)

# --- gold band near top (in front of everything) ---
cube((0, 0.055, 0.88), (1.6, 0.06, 0.13), gold, name='GoldBand')

# --- hieroglyph relief glyphs on the panels ---
def glyph(kind, x, z):
    y = 0.045
    if kind == 'circle':
        cyl((x, y, z), 0.055, 0.06, sand_dark, rot=(math.pi/2, 0, 0))
    elif kind == 'disk_gold':
        cyl((x, y, z), 0.050, 0.06, gold, rot=(math.pi/2, 0, 0))
    elif kind == 'bar':
        cube((x, y, z), (0.17, 0.05, 0.035), sand_dark)
    elif kind == 'bar2':
        cube((x, y, z+0.030), (0.16, 0.05, 0.026), sand_dark)
        cube((x, y, z-0.030), (0.16, 0.05, 0.026), sand_dark)
    elif kind == 'tri':
        bpy.ops.mesh.primitive_cone_add(radius1=0.075, radius2=0, depth=0.11,
                                        location=(x, y, z), rotation=(0, 0, 0))
        o = bpy.context.active_object
        o.data.materials.append(sand_dark)
    elif kind == 'eye':
        s = sphere((x, y, z), 0.055, sand_dark)
        s.scale = (1.5, 0.6, 0.75)
    elif kind == 'zig':
        for i, dx in enumerate((-0.058, 0.0, 0.058)):
            cube((x+dx, y, z + (0.02 if i % 2 else -0.02)),
                 (0.055, 0.045, 0.028), sand_dark,
                 rot=(0, math.radians(-20 if i % 2 else 20), 0))

rows = [0.58, 0.40, 0.22, 0.04, -0.14, -0.32, -0.50, -0.68, -0.86]
left_seq  = ['circle', 'bar2', 'tri', 'eye', 'bar', 'disk_gold', 'zig', 'tri', 'bar2']
right_seq = ['tri', 'disk_gold', 'bar', 'zig', 'circle', 'bar2', 'eye', 'bar', 'tri']
for z, k in zip(rows, left_seq):
    glyph(k, -0.42, z)
for z, k in zip(rows, right_seq):
    glyph(k, 0.42, z)

wall_cam()

# --- lighting: warm amber key, faint cool fill, strong torch glow ---
area_light((-2.2, -3.0, 2.4), 250, 3.5, (1, 0.76, 0.48), (math.radians(60), 0, math.radians(-28)))
area_light((2.4, -2.6, 1.2), 70, 3.0, (0.65, 0.75, 1.0), (math.radians(75), 0, math.radians(30)))
point_light((-0.45, -0.70, 0.15), 105, (1, 0.48, 0.13), 0.10)
point_light((0.50, -0.75, -0.55), 75, (1, 0.42, 0.11), 0.10)

render_to(OUT, 288, 384, transparent=False, samples=160)
