FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())
import math

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles\wall_8.png"

reset_scene()
wall_cam()

# near-black polished stone wall
stone = stone_mat('DarkPolish', tone=(0.06, 0.06, 0.09), rough=0.3, scale=5.0, bump=0.15)
gold = gold_mat()
plane((0, 0.1, 0), 3.4, stone, rot=(math.pi/2, 0, 0), name='Wall')

# ---- circular gold medallion ----
bpy.ops.mesh.primitive_torus_add(major_radius=0.40, minor_radius=0.075,
                                 location=(0, 0.02, 0.15), rotation=(math.pi/2, 0, 0))
t = bpy.context.active_object
bpy.ops.object.shade_smooth()
t.data.materials.append(gold)

bpy.ops.mesh.primitive_torus_add(major_radius=0.26, minor_radius=0.04,
                                 location=(0, 0.0, 0.15), rotation=(math.pi/2, 0, 0))
t2 = bpy.context.active_object
bpy.ops.object.shade_smooth()
t2.data.materials.append(gold)

cyl((0, 0.03, 0.15), 0.19, 0.06, gold, rot=(math.pi/2, 0, 0), verts=48, name='Disc')

# ---- gems: emissive strength 2, red/green/blue ----
gem_r = emissive_mat('GemR', (1.0, 0.05, 0.08), 2.0)
gem_g = emissive_mat('GemG', (0.08, 1.0, 0.25), 2.0)
gem_b = emissive_mat('GemB', (0.15, 0.35, 1.0), 2.0)

# center gem in the medallion disc
sphere((0, -0.035, 0.15), 0.075, gem_r, name='GemCenter')

# scattered small gems on the wall
spots = [(-0.55, 0.72, gem_g), (0.52, 0.78, gem_b), (-0.62, -0.30, gem_b),
         (0.58, -0.42, gem_r), (-0.30, -0.78, gem_g), (0.34, -0.72, gem_r),
         (0.60, 0.32, gem_g), (-0.58, 0.26, gem_b)]
for i, (x, z, gm) in enumerate(spots):
    sphere((x, 0.055, z), 0.04, gm, name='Gem%d' % i)
    # tiny gold bezel ring behind each gem
    cyl((x, 0.075, z), 0.055, 0.02, gold, rot=(math.pi/2, 0, 0), verts=24, name='Bez%d' % i)

# dim warm world so gold has something to reflect
w = bpy.data.worlds.new('W')
w.use_nodes = True
bg = w.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (1.0, 0.8, 0.55, 1)
bg.inputs['Strength'].default_value = 0.04
bpy.context.scene.world = w

# ---- lighting: dramatic gold edge light grazing up from below + faint cool graze from top ----
area_light((0, -0.9, -1.5), 200, 1.6, (1.0, 0.68, 0.24), rot=(math.radians(140), 0, 0))
area_light((0, -0.7, 1.7), 45, 2.5, (0.60, 0.72, 1.0), rot=(math.radians(30), 0, 0))
point_light((0.5, -0.9, 0.3), 25, (1.0, 0.8, 0.5), 0.2)

render_to(OUT, 288, 384, transparent=False, samples=160)
