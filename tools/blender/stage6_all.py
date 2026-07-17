import math, random, os
FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())
OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles"

# ═══ STAGE 6: ARMORY — Tower of London ═══

# ---- WALL: granite blocks + mounted shield with crossed swords + torch sconce ----
sc = reset_scene()
random.seed(6)
granite = stone_mat('Granite', (0.17, 0.175, 0.19), rough=0.88, scale=6.0, bump=0.5)
# staggered granite blocks
bw, bh = 0.5, 0.33
for row in range(8):
    z = -1.1 + row * bh
    off = (row % 2) * bw / 2
    for col in range(-2, 3):
        x = col * bw + off
        g = stone_mat(f'G{row}{col}', (0.155 + random.uniform(-0.03, 0.04),) * 2 + (0.18 + random.uniform(-0.03, 0.03),), rough=0.9, scale=7.0, bump=0.5)
        cube((x, 0.12, z), (bw - 0.02, 0.16, bh - 0.02), g, name=f'B{row}{col}')
# crossed swords behind shield
steel = metal_mat('Steel', (0.55, 0.56, 0.6), rough=0.32)
darksteel = metal_mat('DarkSteel', (0.25, 0.26, 0.3), rough=0.45)
for ang in (35, -35):
    r = math.radians(ang)
    cube((0, -0.06, 0.25), (0.045, 0.012, 1.0), steel, rot=(0, r, 0), name=f'Blade{ang}')
    cube((math.sin(r) * -0.42, -0.06, 0.25 - math.cos(r) * 0.42), (0.16, 0.03, 0.035), darksteel, rot=(0, r, 0), name=f'Guard{ang}')
# round shield
shield = cyl((0, -0.12, 0.25), 0.3, 0.05, metal_mat('Shield', (0.4, 0.41, 0.46), rough=0.38), rot=(math.pi/2, 0, 0), verts=48)
boss = sphere((0, -0.16, 0.25), 0.09, gold_mat('Boss'))
rim = cyl((0, -0.125, 0.25), 0.31, 0.03, gold_mat('Rim'), rot=(math.pi/2, 0, 0), verts=48)
# torch sconce right edge
iron = metal_mat('Iron', (0.1, 0.1, 0.11), rough=0.7)
cyl((0.62, -0.1, -0.45), 0.025, 0.35, iron, rot=(math.radians(20), 0, 0))
cyl((0.62, -0.16, -0.24), 0.05, 0.1, iron)
flame = sphere((0.62, -0.16, -0.14), 0.055, emissive_mat('Flame', (1, 0.45, 0.12), 10))
flame.scale = (1, 1, 1.6)
point_light((0.62, -0.3, -0.05), 60, (1, 0.55, 0.2), 0.1)
# moody lighting
area_light((-2.0, -2.8, 2.2), 260, 3.0, (0.85, 0.85, 0.95), (math.radians(58), 0, math.radians(-30)))
area_light((2.2, -2.4, 0.8), 70, 2.5, (0.55, 0.62, 0.8), (math.radians(72), 0, math.radians(32)))
wall_cam()
render_to(os.path.join(OUT, 'wall_6.png'), 288, 384, samples=160)

# ---- FLOOR: worn flagstones ----
sc = reset_scene()
random.seed(66)
grout = stone_mat('Grout', (0.05, 0.05, 0.045), rough=0.95, scale=8, bump=0.2)
plane((0, 0, -0.02), 4.4, grout)
slabs = [(-0.52, -0.5, 0.85, 0.9), (0.45, -0.55, 0.95, 0.8), (-0.45, 0.42, 0.95, 0.85), (0.5, 0.45, 0.85, 0.95), (0.02, -0.02, 0.0, 0.0)]
for i, (x, y, w, h) in enumerate(slabs):
    if w == 0: continue
    tone = 0.14 + random.uniform(-0.03, 0.05)
    moss = random.uniform(0, 0.02)
    m = stone_mat(f'Slab{i}', (tone, tone + moss, tone * 0.95), rough=0.85, scale=5, bump=0.45)
    cube((x, y, 0.02), (w, h, 0.05), m, rot=(0, 0, random.uniform(-0.03, 0.03)))
# center stone
m = stone_mat('SlabC', (0.16, 0.165, 0.155), rough=0.85, scale=5, bump=0.45)
cube((0.0, -0.02, 0.02), (0.8, 0.75, 0.05), m, rot=(0, 0, 0.015))
area_light((-1.5, -1.5, 3.0), 300, 3.5, (0.9, 0.88, 0.92), (math.radians(20), 0, math.radians(-25)))
area_light((1.5, 1.2, 2.5), 80, 3.0, (0.6, 0.65, 0.85), (math.radians(-18), 0, math.radians(20)))
floor_cam()
render_to(os.path.join(OUT, 'floor_6.png'), 192, 192, samples=160)

# ---- DECOR: suit of plate armor on stand (transparent) ----
sc = reset_scene()
# dim world for metal reflections (film_transparent keeps alpha clean)
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.35
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.45, 0.5, 0.6, 1)
plate = metal_mat('Plate', (0.5, 0.51, 0.56), rough=0.28)
dark = metal_mat('DarkIron', (0.08, 0.08, 0.09), rough=0.6)
goldm = gold_mat('GoldTrim')
# stand base
cyl((0, 0, 0.04), 0.34, 0.08, dark, verts=32)
# legs
for s in (-1, 1):
    cyl((s * 0.12, 0, 0.55), 0.07, 0.85, plate)
    sphere((s * 0.12, 0, 1.0), 0.085, plate)  # knee-ish joint at top
# cuirass
c = cube((0, 0, 1.35), (0.46, 0.3, 0.55), plate, name='Cuirass')
c.rotation_euler = (0, 0, 0)
cube((0, -0.14, 1.5), (0.4, 0.08, 0.3), plate, name='ChestPlate')
cube((0, 0, 1.06), (0.4, 0.26, 0.1), goldm, name='Belt')
# pauldrons
for s in (-1, 1):
    sphere((s * 0.3, 0, 1.58), 0.14, plate)
    cyl((s * 0.33, 0, 1.25), 0.075, 0.5, plate)  # arms
    sphere((s * 0.36, 0, 0.98), 0.075, plate)  # gauntlet
# helmet
h = sphere((0, 0, 1.85), 0.17, plate)
h.scale = (1, 1.05, 1.2)
cube((0, -0.15, 1.83), (0.28, 0.06, 0.025), dark, name='VisorSlit')
cyl((0, 0, 2.02), 0.05, 0.12, goldm)  # plume holder
# poleaxe
cyl((0.52, 0, 1.15), 0.022, 2.3, wood_mat('Haft', (0.15, 0.09, 0.05)))
cube((0.52, 0, 2.32), (0.16, 0.02, 0.22), steel_mat if False else metal_mat('AxeHead', (0.6, 0.61, 0.65), 0.25), name='AxeHead')
# lighting
area_light((-1.8, -2.6, 2.6), 300, 3.0, (0.95, 0.93, 0.9), (math.radians(55), 0, math.radians(-28)))
area_light((2.0, -2.2, 1.2), 90, 2.5, (0.6, 0.68, 0.9), (math.radians(70), 0, math.radians(35)))
decor_cam()
render_to(os.path.join(OUT, 'decor_6.png'), 288, 480, transparent=True, samples=160)
print('STAGE6_DONE')
