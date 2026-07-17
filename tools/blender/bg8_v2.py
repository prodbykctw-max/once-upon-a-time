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

sc = reset_scene()
random.seed(98)
obs = marble_mat('Obsidian', (0.03, 0.03, 0.05), (0.08, 0.06, 0.12), rough=0.07)
plane((0, 16, 0), 52, obs)
darkw = stone_mat('VaultWall', (0.04, 0.04, 0.06), rough=0.5, scale=4, bump=0.3)
for s in (-1, 1):
    w = plane((s * 3.3, 16, 2.0), 52, darkw, rot=(0, math.pi/2 * s, 0))
    w.scale = (1, 1, 0.085)
plane((0, 16, 4.0), 52, darkw, rot=(math.pi, 0, 0))
gold = plain_metal('Gold8', (0.75, 0.53, 0.14), 0.3)
colm = stone_mat('Col8', (0.05, 0.05, 0.075), rough=0.45, scale=4, bump=0.25)
for s in (-1, 1):
    for i in range(13):
        y = -4 + i * 3.4
        cyl((s * 2.9, y, 2.0), 0.3, 4.0, colm, verts=24)
        for z in (0.7, 2.0, 3.3):
            cyl((s * 2.9, y, z), 0.33, 0.12, gold, verts=24)
        py = y + 1.7
        random.seed(i * 7 + (0 if s < 0 else 50))
        for k in range(14):
            a = random.uniform(0, math.pi * 2); r = random.uniform(0, 0.45)
            gx = s * 2.75 + math.cos(a) * r * 0.4
            gy = py + math.sin(a) * r
            gz = 0.03 + (0.45 - r) * 0.4
            c = cyl((gx, gy, gz), random.uniform(0.05, 0.08), 0.02, gold, verts=14)
            c.rotation_euler = (random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5), 0)
        sphere((s * 2.7, py, 0.32), 0.12, gold)
        col = [(0.7, 0.05, 0.1), (0.05, 0.55, 0.2), (0.35, 0.05, 0.6)][i % 3]
        g = bpy.data.materials.new(f'Gm{s}{i}'); g.use_nodes = True
        gb = g.node_tree.nodes['Principled BSDF']
        gb.inputs['Base Color'].default_value = (*col, 1)
        gb.inputs['Emission Color'].default_value = (*col, 1)
        gb.inputs['Emission Strength'].default_value = 4
        sphere((s * 2.6, py + 0.2, 0.5), 0.06, g)
# god-ray LIGHTS only (no emissive geometry)
for i in range(6):
    y = 1 + i * 6.4
    area_light((-0.6, y, 3.9), 500, 1.2, (1, 0.78, 0.35), (math.radians(10), 0, 0))
# warm ambient fill so hall isn't pitch black
area_light((0, 4, 3.6), 200, 5.0, (1, 0.8, 0.45), (0, 0, 0))
plane((0, 41, 2), 9, emissive_mat('FarGlow8', (1, 0.75, 0.3), 2.2), rot=(math.pi/2, 0, 0))
corr = persp_cam((0, -6, 1.5), (math.radians(90), 0, 0), lens=24)
corr.data.shift_y = 0.09
render_to(os.path.join(OUT, 'bg_8.png'), 960, 540, samples=160)
print('BG8_V2_DONE')
