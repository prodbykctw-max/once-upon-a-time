FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())
import math

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles\floor_4.png"

sc = reset_scene()

w = bpy.data.worlds.new('W'); w.use_nodes = True
bg = w.node_tree.nodes['Background']
bg.inputs[0].default_value = (0.55, 0.56, 0.62, 1)
bg.inputs[1].default_value = 0.05
sc.world = w

# ---------- materials ----------
grout = stone_mat('Grout', tone=(0.04, 0.04, 0.045), rough=0.85, scale=12.0, bump=0.12)
light_marble = marble_mat('LightM', base=(0.85, 0.81, 0.72), vein=(0.38, 0.36, 0.35), rough=0.15)
dark_marble  = marble_mat('DarkM',  base=(0.028, 0.033, 0.055), vein=(0.085, 0.095, 0.125), rough=0.15)

plane((0, 0, -0.035), 3.2, grout, name='Grout')

# ---------- 4x4 polished checkerboard ----------
for i in range(4):
    for j in range(4):
        x = -0.75 + i * 0.5
        y = -0.75 + j * 0.5
        m = light_marble if (i + j) % 2 == 0 else dark_marble
        cube((x, y, -0.012), (0.488, 0.488, 0.024), m, name='Tile%d%d' % (i, j))

# ---------- lights ----------
area_light((-1.6, -1.6, 3.0), 320, 3.2, (1.0, 0.89, 0.72), rot=(math.radians(28), math.radians(-28), 0))
area_light(( 1.8,  1.8, 2.6), 85, 2.8, (0.68, 0.77, 1.0), rot=(math.radians(-30), math.radians(30), 0))
area_light((0, 0, 3.4), 45, 3.5, (0.98, 0.96, 0.92))

floor_cam()
render_to(OUT, 192, 192, transparent=False, samples=160)
