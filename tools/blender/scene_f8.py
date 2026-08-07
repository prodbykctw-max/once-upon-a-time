FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())
import math, random

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles\floor_8.png"

reset_scene()
floor_cam()

# polished obsidian floor
obsidian = marble_mat('Obsidian', base=(0.05, 0.05, 0.08), vein=(0.15, 0.12, 0.20), rough=0.1)
gold = gold_mat()
plane((0, 0, 0), 3.0, obsidian, name='Floor')

# scattered gold coins, non-overlapping random layout
random.seed(88)
placed = []
tries = 0
while len(placed) < 9 and tries < 400:
    tries += 1
    x = random.uniform(-0.8, 0.8)
    y = random.uniform(-0.8, 0.8)
    if all((x-px)**2 + (y-py)**2 > 0.30**2 for px, py in placed):
        placed.append((x, y))

for i, (x, y) in enumerate(placed):
    r = random.uniform(0.09, 0.125)
    rot = (math.radians(random.uniform(-12, 12)),
           math.radians(random.uniform(-12, 12)),
           random.uniform(0, math.pi))
    cyl((x, y, 0.022), r, 0.02, gold, rot=rot, verts=28, name='Coin%d' % i)

# dim warm world so the gold coins have ambient reflections
w = bpy.data.worlds.new('W')
w.use_nodes = True
bg = w.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (1.0, 0.82, 0.6, 1)
bg.inputs['Strength'].default_value = 0.03
bpy.context.scene.world = w

# lighting: low side lights so the glossy floor does NOT mirror them into the top-down camera
area_light((-2.2, -2.2, 1.5), 260, 2.0, (1.0, 0.85, 0.6),
           rot=(math.radians(64), 0, math.radians(-45)))
area_light((2.2, 2.2, 1.4), 90, 2.5, (0.65, 0.75, 1.0),
           rot=(math.radians(65), 0, math.radians(135)))
area_light((0, 0, 3.0), 55, 5.0, (0.9, 0.9, 1.0))  # very soft dim overhead sheen
point_light((0.6, -0.8, 0.4), 45, (1.0, 0.78, 0.42), 0.15)

render_to(OUT, 192, 192, transparent=False, samples=160)
