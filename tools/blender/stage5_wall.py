FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())

reset_scene()

def flatten_rough(mat, lo, hi):
    # tame the noisy roughness ramp so metal reads brushed, not speckled paper
    for n in mat.node_tree.nodes:
        if n.type == 'VALTORGB':
            n.color_ramp.elements[0].color = (lo, lo, lo, 1)
            n.color_ramp.elements[1].color = (hi, hi, hi, 1)

# Materials
steel = metal_mat('Steel', tone=(0.10, 0.11, 0.16), rough=0.4)
flatten_rough(steel, 0.30, 0.46)
backing = metal_mat('Backing', tone=(0.02, 0.025, 0.04), rough=0.65)
bolt_m = metal_mat('Bolt', tone=(0.38, 0.40, 0.46), rough=0.28)
flatten_rough(bolt_m, 0.22, 0.34)
glow = emissive_mat('Conduit', color=(0.12, 0.5, 1.0), strength=4.0)

# Dark backing wall (seen through panel seams)
plane((0, 0.14, 0), 2.8, backing, rot=(math.pi/2, 0, 0), name='Backing')

# Brushed steel panels: 2 cols x 3 rows, seams between, hex bolts at corners
for cx in (-0.39, 0.39):
    for cz in (-0.68, 0.0, 0.68):
        cube((cx, 0.06, cz), (0.75, 0.04, 0.66), steel, name='Panel')
        for dx in (-0.315, 0.315):
            for dz in (-0.27, 0.27):
                cyl((cx + dx, 0.03, cz + dz), 0.024, 0.03, bolt_m,
                    rot=(math.pi/2, 0, 0), verts=6, name='Bolt')

# Two vertical glowing blue conduits with metal brackets
for x in (-0.55, 0.55):
    cube((x, 0.02, 0), (0.035, 0.02, 2.3), glow, name='Conduit')
    for z in (-0.66, 0.02, 0.70):
        cube((x, 0.012, z), (0.09, 0.026, 0.05), bolt_m, name='Bracket')
    # faint blue spill hugging the conduit line (close to wall, low energy)
    for z in (-0.7, 0.0, 0.7):
        point_light((x, -0.12, z), 8, (0.25, 0.55, 1.0), radius=0.3)

wall_cam()
# dim warm key upper-left, cool fill right, subtle blue frontal ambient
area_light((-2.2, -3.0, 2.4), 200, 3.5, (1.0, 0.88, 0.72),
           rot=(math.radians(60), 0, math.radians(-28)))
area_light((2.4, -2.6, 1.2), 80, 3.0, (0.6, 0.72, 1.0),
           rot=(math.radians(75), 0, math.radians(30)))
area_light((0, -3.2, 0.2), 55, 5.0, (0.35, 0.6, 1.0), rot=(math.pi/2, 0, 0))

render_to(r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles\wall_5.png",
          288, 384, transparent=False, samples=160)
