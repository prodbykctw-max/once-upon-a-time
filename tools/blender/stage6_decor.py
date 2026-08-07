FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())
import random
random.seed(6)

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles\decor_6.png"

sc = reset_scene()

w = bpy.data.worlds.new('W'); w.use_nodes = True
bg = w.node_tree.nodes['Background']
bg.inputs[0].default_value = (0.45, 0.5, 0.6, 1)
bg.inputs[1].default_value = 0.35
sc.world = w

def tighten_metal(m, lo, hi):
    for n in m.node_tree.nodes:
        if n.type == 'VALTORGB':
            n.color_ramp.elements[0].color = (lo, lo, lo, 1)
            n.color_ramp.elements[1].color = (hi, hi, hi, 1)

armor = metal_mat('Armor', tone=(0.60, 0.62, 0.70), rough=0.3)
tighten_metal(armor, 0.24, 0.36)
dark_iron = metal_mat('DarkIron', tone=(0.08, 0.08, 0.10), rough=0.6)
black = metal_mat('BlackStand', tone=(0.03, 0.03, 0.035), rough=0.5, metallic=0.2)
shaft_wood = wood_mat('Shaft', tone=(0.10, 0.05, 0.025), grain_scale=3.0, rough=0.6)
blade_steel = metal_mat('BladeSteel', tone=(0.38, 0.40, 0.46), rough=0.38)
tighten_metal(blade_steel, 0.28, 0.42)
slit_black = fabric_mat('SlitBlack', tone=(0.01, 0.01, 0.012), rough=0.9)

def bev(o, wdt=0.02):
    m = o.modifiers.new('bv', 'BEVEL'); m.width = wdt; m.segments = 2
    return o

# ---- black display stand ----
bev(cube((0, 0.02, 0.05), (0.78, 0.5, 0.10), black, name='Base1'))
bev(cube((0, 0.02, 0.13), (0.56, 0.38, 0.06), black, name='Base2'), 0.015)
cyl((0, 0.16, 1.05), 0.035, 1.9, black, name='Pole')

# ---- legs ----
for s in (1, -1):
    x = 0.14 * s
    bev(cube((x, -0.06, 0.20), (0.13, 0.28, 0.10), armor, name='Foot'), 0.015)
    cyl((x, 0, 0.47), 0.060, 0.52, armor, name='Shin')
    sphere((x, 0, 0.74), 0.080, armor, name='Knee')
    cyl((x, 0, 0.96), 0.078, 0.50, armor, name='Thigh')

# ---- torso ----
bev(cube((0, 0, 1.28), (0.40, 0.26, 0.20), armor, name='Faulds'), 0.03)
bev(cube((0, 0, 1.55), (0.44, 0.28, 0.42), armor, name='Cuirass'), 0.05)
cyl((0, 0, 1.36), 0.23, 0.05, dark_iron, name='Belt')
cyl((0, 0, 1.80), 0.09, 0.10, armor, name='Gorget')

# ---- arms + pauldrons ----
for s in (1, -1):
    sphere((0.29 * s, 0, 1.74), 0.13, armor, name='Pauldron')
    cyl((0.30 * s, 0, 1.58), 0.060, 0.30, armor, name='UpperArm')
sphere((-0.30, 0, 1.42), 0.065, armor, name='ElbowL')
cyl((-0.31, 0, 1.27), 0.055, 0.32, armor, name='ForearmL')
sphere((-0.31, 0, 1.09), 0.07, armor, name='GauntletL')
# right forearm angles out and DOWN to grip the poleaxe (131 deg: +x, -z direction)
sphere((0.30, 0, 1.40), 0.065, armor, name='ElbowR')
cyl((0.375, 0, 1.34), 0.055, 0.24, armor, rot=(0, math.radians(131), 0), name='ForearmR')
sphere((0.45, 0, 1.27), 0.07, armor, name='GauntletR')

# ---- helmet ----
sphere((0, 0, 1.94), 0.155, armor, name='Helmet')
bev(cube((0, -0.150, 1.955), (0.22, 0.05, 0.035), slit_black, name='VisorSlit'), 0.005)
cyl((0, 0, 1.815), 0.145, 0.04, dark_iron, name='NeckRing')

# ---- vertical poleaxe in right gauntlet ----
cyl((0.45, 0, 1.16), 0.024, 2.28, shaft_wood, name='Haft')
bev(cube((0.545, 0, 2.00), (0.13, 0.035, 0.30), blade_steel, name='AxeBlade'), 0.02)
bev(cube((0.37, 0, 2.06), (0.10, 0.03, 0.10), blade_steel, name='BackSpike'), 0.012)
cyl((0.45, 0, 2.26), 0.013, 0.14, blade_steel, name='TopSpike')
cyl((0.45, 0, 1.90), 0.030, 0.09, dark_iron, name='HaftCollar')

# custom rig: warm key upper-left-front, cool fill right, weak frontal fill
area_light((-2.2, -2.8, 2.6), 240, 3.5, (1, 0.88, 0.72), (math.radians(55), 0, math.radians(-35)))
area_light((2.4, -2.2, 1.2), 110, 3.0, (0.7, 0.78, 1.0), (math.radians(70), 0, math.radians(35)))
area_light((0, -3.2, 1.2), 50, 5.0, (0.85, 0.9, 1.0), (math.pi/2, 0, 0))

decor_cam()
render_to(OUT, 288, 480, transparent=True, samples=160)
