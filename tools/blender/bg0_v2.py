import math, random, os
FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())
OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\bgs"

def plain_metal(name, tone, rough):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*tone, 1)
    b.inputs['Metallic'].default_value = 1.0
    b.inputs['Roughness'].default_value = rough
    return m

def corridor_cam():
    cam = persp_cam((0, -6, 1.5), (math.radians(90), 0, 0), lens=24)
    cam.data.shift_y = 0.09
    return cam

# ═══ BG 0: GRAND LIBRARY hall ═══
sc = reset_scene()
random.seed(10)
floor_m = wood_mat('Parquet', (0.085, 0.048, 0.024), grain_scale=10, rough=0.35)
plane((0, 16, 0), 52, floor_m)
carpet = fabric_mat('Carpet', (0.19, 0.018, 0.032), rough=0.9)
c = cube((0, 16, 0.012), (2.4, 48, 0.02), carpet)
gold_trim = plain_metal('CTrim', (0.5, 0.36, 0.1), 0.35)
for s in (-1, 1):
    cube((s * 1.25, 16, 0.015), (0.1, 48, 0.02), gold_trim)
# bookshelf walls: repeated bays
wood = wood_mat('Shelf', (0.095, 0.055, 0.027), grain_scale=4, rough=0.5)
random.seed(11)
book_cols = [(0.35, 0.06, 0.05), (0.06, 0.16, 0.3), (0.3, 0.24, 0.05), (0.05, 0.24, 0.1), (0.26, 0.08, 0.24), (0.3, 0.18, 0.06)]
for s in (-1, 1):
    for bay in range(14):
        y = -4 + bay * 3.2
        # shelf frame
        cube((s * 3.0, y, 1.9), (0.35, 3.0, 3.8), wood, name=f'Bay{s}{bay}')
        # shelf rows of books (front face toward lane)
        for row in range(5):
            z = 0.5 + row * 0.72
            x = s * 2.78
            yy = y - 1.3
            while yy < y + 1.3:
                bw = random.uniform(0.12, 0.24)
                bh = random.uniform(0.42, 0.58)
                col = book_cols[random.randint(0, 5)]
                br = random.uniform(0.5, 0.95)
                mat = fabric_mat(f'Bk{s}{bay}{row}{int(yy*10)}', tuple(min(1, cc * br) for cc in col), rough=0.7)
                cube((x, yy + bw/2, z + bh/2), (0.18, bw - 0.02, bh), mat)
                yy += bw + 0.01
# ceiling: dark wood with beams
ceil = wood_mat('Ceil', (0.055, 0.032, 0.016), grain_scale=3, rough=0.6)
plane((0, 16, 4.0), 52, ceil, rot=(math.pi, 0, 0))
for bay in range(14):
    y = -4 + bay * 3.2
    cube((0, y, 3.9), (6.4, 0.3, 0.25), wood)
# hanging brass lamps + warm light
for bay in range(12):
    y = -2 + bay * 3.4
    cyl((0, y, 3.6), 0.02, 0.6, gold_trim)
    sphere((0, y, 3.25), 0.16, emissive_mat(f'Lamp{bay}', (1, 0.72, 0.38), 8))
    point_light((0, y, 3.0), 130, (1, 0.72, 0.4), 0.25)
# far glow
plane((0, 41, 2), 9, emissive_mat('FarGlow', (1, 0.75, 0.42), 1.7), rot=(math.pi/2, 0, 0))
corridor_cam()
render_to(os.path.join(OUT, 'bg_0.png'), 960, 540, samples=160)

print('BG0_V2_DONE')
