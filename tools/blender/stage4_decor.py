FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())
import math

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles\decor_4.png"

sc = reset_scene()

w = bpy.data.worlds.new('W'); w.use_nodes = True
bg = w.node_tree.nodes['Background']
bg.inputs[0].default_value = (0.85, 0.72, 0.52, 1)
bg.inputs[1].default_value = 0.15
sc.world = w

# ---------- materials ----------
ped_m   = marble_mat('Pedestal', base=(0.026, 0.026, 0.036), vein=(0.062, 0.062, 0.078), rough=0.20)
frame_m = metal_mat('CaseFrame', tone=(0.07, 0.06, 0.05), rough=0.38)
velvet  = fabric_mat('Velvet', tone=(0.05, 0.008, 0.015), rough=0.95)
gold    = gold_mat('MaskGold')
lapis   = metal_mat('Lapis', tone=(0.014, 0.038, 0.17), rough=0.28, metallic=0.0)
lapis_d = metal_mat('LapisDark', tone=(0.006, 0.010, 0.04), rough=0.25, metallic=0.0)
glow    = emissive_mat('CaseLight', color=(1.0, 0.85, 0.55), strength=8.0)

# ---------- dark pedestal (z 0 .. 0.78) ----------
cube((0, 0, 0.05), (1.05, 0.60, 0.10), ped_m, name='PedBase')
cube((0, 0, 0.41), (0.80, 0.55, 0.62), ped_m, name='PedCol')
cube((0, 0, 0.75), (0.95, 0.62, 0.06), ped_m, name='PedTop')

# ---------- display case: thin dark metal frame (z 0.78 .. 1.97) ----------
for px in (-0.40, 0.40):
    for py in (-0.26, 0.26):
        cube((px, py, 1.35), (0.028, 0.028, 1.14), frame_m, name='Post')
for zz in (0.805, 1.895):
    for py in (-0.26, 0.26):
        cube((0, py, zz), (0.835, 0.028, 0.028), frame_m, name='RailX')
    for px in (-0.40, 0.40):
        cube((px, 0, zz), (0.028, 0.555, 0.028), frame_m, name='RailY')
cube((0, 0, 1.945), (0.90, 0.60, 0.05), frame_m, name='CaseCap')
# warm light strip under the cap (museum case lighting)
cube((0, 0, 1.87), (0.36, 0.20, 0.012), glow, name='Strip')

# ---------- interior: velvet plinth + gold funerary mask ----------
cube((0, 0, 0.87), (0.36, 0.30, 0.18), velvet, name='Plinth')
cyl((0, 0.02, 1.06), 0.028, 0.20, frame_m, name='StandRod')

f = sphere((0, 0.02, 1.34), 0.19, gold, name='Face')
f.scale = (0.80, 0.50, 1.08)
# nemes headdress side flaps
cube((-0.19, 0.04, 1.30), (0.075, 0.11, 0.38), gold, rot=(0, math.radians(7), 0), name='FlapL')
cube(( 0.19, 0.04, 1.30), (0.075, 0.11, 0.38), gold, rot=(0, math.radians(-7), 0), name='FlapR')
# lapis brow band + low crown disc
cube((0, 0.02, 1.535), (0.32, 0.16, 0.055), lapis, name='Band')
cyl((0, 0.02, 1.578), 0.052, 0.045, gold, name='Crown')
# ceremonial beard
cyl((0, -0.01, 1.10), 0.036, 0.16, gold, name='Beard')
# subtle dark eyes
sphere((-0.055, -0.062, 1.375), 0.016, lapis_d, name='EyeL')
sphere(( 0.055, -0.062, 1.375), 0.016, lapis_d, name='EyeR')

# ---------- lights: lit from above (dimmer than warm_rig) ----------
area_light((-2.2, -3.0, 2.6), 300, 3.5, (1.0, 0.89, 0.72), rot=(math.radians(60), 0, math.radians(-28)))
area_light(( 2.4, -2.6, 1.4), 90, 3.0, (0.70, 0.79, 1.0), rot=(math.radians(75), 0, math.radians(30)))
point_light((0, -0.32, 2.50), energy=130, color=(1.0, 0.85, 0.55), radius=0.12)
point_light((0, -0.15, 1.82), energy=15, color=(1.0, 0.80, 0.45), radius=0.05)

decor_cam()
render_to(OUT, 288, 480, transparent=True, samples=160)
