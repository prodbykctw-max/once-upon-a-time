FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())
import math, random

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles\decor_8.png"

reset_scene()
decor_cam()

wood = wood_mat('ChestWood', tone=(0.10, 0.05, 0.024), grain_scale=6.0, rough=0.45)
gold = gold_mat()

# ---- chest body ----
cube((0, 0, 0.36), (1.12, 0.68, 0.72), wood, name='Body')
# gold straps + lock on the front face
cube((-0.38, -0.352, 0.36), (0.09, 0.03, 0.74), gold, name='StrapL')
cube((0.38, -0.352, 0.36), (0.09, 0.03, 0.74), gold, name='StrapR')
cube((0, -0.355, 0.52), (0.17, 0.035, 0.17), gold, name='Lock')
cube((0, -0.35, 0.705), (1.14, 0.035, 0.05), gold, name='RimTrim')

# ---- tilted open lid, hinged at back top edge, opened ~105deg (mostly upright) ----
lid_rot = math.radians(-105)
cube((0, 0.478, 1.004), (1.16, 0.62, 0.12), wood, rot=(lid_rot, 0, 0), name='Lid')
cube((0, 0.478, 1.004), (1.18, 0.10, 0.135), gold, rot=(lid_rot, 0, 0), name='LidBand')

# ---- gold coin pile heaped over the rim ----
random.seed(42)
for i in range(30):
    x = random.uniform(-0.48, 0.48)
    y = random.uniform(-0.25, 0.12)
    mound = 0.30 * max(0.0, 1.0 - (x / 0.58) ** 2) * random.uniform(0.5, 1.0)
    z = 0.74 + mound
    rot = (math.radians(random.uniform(-45, 45)),
           math.radians(random.uniform(-25, 25)),
           random.uniform(0, math.pi))
    cyl((x, y, z), random.uniform(0.06, 0.085), 0.02, gold, rot=rot, verts=24, name='PCoin%d' % i)
for i in range(6):
    x = random.uniform(-0.4, 0.4)
    y = random.uniform(-0.2, 0.1)
    z = 0.76 + 0.22 * max(0.0, 1.0 - (x / 0.55) ** 2) * random.uniform(0.4, 0.9)
    sphere((x, y, z), random.uniform(0.05, 0.075), gold, name='PSph%d' % i)

# coins tipping over the front rim
for i, (x, tz) in enumerate([(-0.25, 0.76), (0.05, 0.78), (0.3, 0.75)]):
    cyl((x, -0.36, tz), 0.07, 0.02, gold,
        rot=(math.radians(70), 0, random.uniform(0, math.pi)), verts=24, name='TipCoin%d' % i)

# spilled coins on the ground in front (tilted so they read from the side view)
for i in range(8):
    x = random.uniform(-0.5, 0.5)
    y = random.uniform(-0.58, -0.40)
    rot = (math.radians(random.uniform(55, 80)), math.radians(random.uniform(-20, 20)),
           random.uniform(0, math.pi))
    cyl((x, y, 0.05), random.uniform(0.06, 0.08), 0.02, gold, rot=rot, verts=24, name='SCoin%d' % i)

# ---- two gold goblets ----
# standing goblet, left of chest
gx = -0.56
cyl((gx, -0.22, 0.015), 0.095, 0.03, gold, verts=32, name='Gob1Base')
cyl((gx, -0.22, 0.11), 0.03, 0.16, gold, verts=24, name='Gob1Stem')
cyl((gx, -0.22, 0.275), 0.09, 0.17, gold, verts=32, name='Gob1Cup')
# tipped-over goblet, right of chest (axis along X)
cyl((0.42, -0.30, 0.09), 0.09, 0.17, gold, rot=(0, math.pi / 2, 0), verts=32, name='Gob2Cup')
cyl((0.55, -0.30, 0.09), 0.03, 0.12, gold, rot=(0, math.pi / 2, 0), verts=24, name='Gob2Stem')
cyl((0.625, -0.30, 0.09), 0.095, 0.03, gold, rot=(0, math.pi / 2, 0), verts=32, name='Gob2Base')

# ---- three glowing gems ----
gem_r = emissive_mat('GemR', (1.0, 0.06, 0.08), 3.5)
gem_g = emissive_mat('GemG', (0.08, 1.0, 0.25), 3.5)
gem_p = emissive_mat('GemP', (0.75, 0.15, 1.0), 3.5)
sphere((-0.28, -0.18, 1.03), 0.065, gem_r, name='GemRs')
sphere((0.24, -0.12, 0.99), 0.06, gem_g, name='GemGs')
sphere((0.16, -0.50, 0.09), 0.06, gem_p, name='GemPs')

# dim warm world so gold reads as coherent metal, not black/white zebra
w = bpy.data.worlds.new('W')
w.use_nodes = True
bg = w.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (1.0, 0.8, 0.55, 1)
bg.inputs['Strength'].default_value = 0.12
bpy.context.scene.world = w

# ---- lighting: warm key, cool fill, warm glow inside chest, low front kicker ----
area_light((-2.2, -3.0, 2.2), 300, 3.0, (1.0, 0.88, 0.7),
           rot=(math.radians(55), 0, math.radians(-30)))
area_light((2.4, -2.4, 1.0), 80, 3.0, (0.7, 0.8, 1.0),
           rot=(math.radians(70), 0, math.radians(35)))
point_light((0, 0.05, 1.05), 70, (1.0, 0.70, 0.35), 0.12)
point_light((0, -1.5, 0.35), 40, (1.0, 0.75, 0.4), 0.2)

render_to(OUT, 288, 480, transparent=True, samples=160)
