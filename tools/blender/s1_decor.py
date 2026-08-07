FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles\decor_1.png"

sc = reset_scene()

# warm world for gold reflections (hidden from camera by film_transparent)
w = bpy.data.worlds.new('W')
w.use_nodes = True
bg = w.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.55, 0.35, 0.15, 1)
bg.inputs['Strength'].default_value = 0.45
sc.world = w

sand      = stone_mat('Sand',     tone=(0.50, 0.29, 0.11), rough=0.86, scale=7.0, bump=0.50)
sand_dark = stone_mat('SandDark', tone=(0.24, 0.13, 0.05), rough=0.90, scale=8.0, bump=0.3)
gold      = gold_mat('Gold')

def smooth(o):
    try:
        bpy.ops.object.shade_auto_smooth(angle=math.radians(40))
    except Exception:
        try:
            bpy.ops.object.shade_smooth()
        except Exception:
            pass
    return o

# --- stepped sandstone pedestal (3 steps), stands on z=0 ---
cube((0, 0, 0.09),  (1.05, 0.60, 0.18), sand, name='Step1')
cube((0, 0, 0.25),  (0.82, 0.48, 0.14), sand, name='Step2')
cube((0, 0, 0.375), (0.60, 0.38, 0.11), sand, name='Step3')

# small carved accents on the front of the middle step
cube((-0.16, -0.245, 0.25), (0.09, 0.03, 0.030), sand_dark)
cyl((0.0, -0.245, 0.25), 0.035, 0.04, sand_dark, rot=(math.pi/2, 0, 0))
cube((0.16, -0.245, 0.25), (0.09, 0.03, 0.030), sand_dark)

# gold base plate on top of pedestal
smooth(cyl((0, 0, 0.445), 0.24, 0.035, gold, verts=64, name='BasePlate'))

# --- gold ankh ---
# vertical shaft
smooth(cyl((0, 0, 0.95), 0.065, 1.05, gold, verts=64, name='Shaft'))
# horizontal cross bar (axis along X) with rounded end caps
smooth(cyl((0, 0, 1.33), 0.060, 0.86, gold, rot=(0, math.pi/2, 0), verts=64, name='CrossBar'))
sphere(( 0.43, 0, 1.33), 0.062, gold)
sphere((-0.43, 0, 1.33), 0.062, gold)
# collar where loop meets the cross
smooth(cyl((0, 0, 1.435), 0.095, 0.09, gold, verts=64, name='Collar'))
# loop: torus standing in XZ plane
bpy.ops.mesh.primitive_torus_add(location=(0, 0, 1.76), rotation=(math.pi/2, 0, 0),
                                 major_radius=0.27, minor_radius=0.075,
                                 major_segments=64, minor_segments=24)
loop = bpy.context.active_object
loop.name = 'Loop'
loop.data.materials.append(gold)
smooth(loop)

decor_cam()

# --- lighting: warm amber key + faint cool fill + strong warm rim from behind-right ---
area_light((-2.2, -3.0, 2.6), 260, 3.5, (1, 0.78, 0.50), (math.radians(60), 0, math.radians(-28)))
area_light((2.4, -2.6, 1.4), 80, 3.0, (0.65, 0.75, 1.0), (math.radians(75), 0, math.radians(30)))
area_light((1.2, 1.6, 1.9), 380, 2.0, (1, 0.72, 0.40),
           rot=(math.radians(-65), 0, math.radians(-30)))
point_light((0.35, -1.5, 1.7), 70, (1, 0.85, 0.55), 0.1)

render_to(OUT, 288, 480, transparent=True, samples=160)
