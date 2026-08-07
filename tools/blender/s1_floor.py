FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles\floor_1.png"

sc = reset_scene()

w = bpy.data.worlds.new('W')
w.use_nodes = True
bg = w.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.45, 0.32, 0.18, 1)
bg.inputs['Strength'].default_value = 0.25
sc.world = w

# dark grout base under the slabs
grout = stone_mat('Grout', tone=(0.13, 0.08, 0.04), rough=0.95, scale=9.0, bump=0.25)
plane((0, 0, -0.04), 3.0, grout, name='GroutBase')

# 2x2 sandstone slabs, slight tone/scale variation per slab
slab_specs = [
    ((-0.5, -0.5), (0.50, 0.35, 0.16), 6.5,  0.4),
    (( 0.5, -0.5), (0.45, 0.30, 0.13), 7.6, -0.3),
    ((-0.5,  0.5), (0.52, 0.34, 0.15), 8.2,  0.2),
    (( 0.5,  0.5), (0.43, 0.31, 0.14), 7.0, -0.5),
]
for i, ((sx, sy), tone, nscale, rdeg) in enumerate(slab_specs):
    m = stone_mat('Slab%d' % i, tone=tone, rough=0.85, scale=nscale, bump=0.75)
    cube((sx, sy, 0.0), (0.955, 0.955, 0.07), m,
         rot=(0, 0, math.radians(rdeg)), name='Slab%d' % i)

floor_cam()

# lighting: grazing warm key for bump relief + faint cool fill + dim warm overhead
area_light((-2.6, -2.6, 1.8), 340, 3.0, (1, 0.76, 0.48), (math.radians(55), 0, math.radians(-45)))
area_light((2.4, 2.2, 2.0), 60, 3.0, (0.65, 0.75, 1.0), (math.radians(-50), 0, math.radians(-45)))
area_light((0, 0, 3.0), 85, 5.0, (1, 0.85, 0.62))

render_to(OUT, 192, 192, transparent=False, samples=160)
