FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles\decor_2.png"

reset_scene()

# dim world so glossy metal/lacquer has something to reflect;
# film_transparent hides it from camera rays, alpha stays clean
world = bpy.data.worlds.new('W')
world.use_nodes = True
wbg = world.node_tree.nodes['Background']
wbg.inputs['Color'].default_value = (0.45, 0.55, 0.68, 1)
wbg.inputs['Strength'].default_value = 0.35
bpy.context.scene.world = world

# ---------- materials ----------
def lacquer_mat(name='Lacquer', tone=(0.018, 0.016, 0.018), rough=0.28):
    m, nt, b = _new_mat(name)
    b.inputs['Base Color'].default_value = (*tone, 1)
    b.inputs['Roughness'].default_value = rough
    if 'Coat Weight' in b.inputs:
        b.inputs['Coat Weight'].default_value = 1.0
    return m

lacquer = lacquer_mat()
blade_steel = metal_mat('Blade', tone=(0.80, 0.83, 0.88), rough=0.18)
handle_wood = wood_mat('Handle', tone=(0.08, 0.045, 0.03), grain_scale=8.0, rough=0.5)
gold = gold_mat('Gold')
red_silk = fabric_mat('RedSilk', tone=(0.34, 0.020, 0.040), rough=0.55)
red_silk.node_tree.nodes['Principled BSDF'].inputs['Sheen Weight'].default_value = 0.5

# ---------- stand (frame: x [-0.75,0.75], z [-0.15,2.35], ground z=0) ----------
# base slab
cube((0, 0, 0.07), (1.15, 0.34, 0.14), lacquer, name='Base')
# vertical posts
for x in (-0.38, 0.38):
    cube((x, 0, 1.12), (0.10, 0.09, 2.0), lacquer, name='Post')
    # gold cap
    cyl((x, 0, 2.14), 0.06, 0.04, gold, name='Cap')
# top crossbar
cube((0, 0, 2.05), (0.86, 0.07, 0.07), lacquer, name='CrossBar')

# cradle arms + front stubs (two sword rests per side)
for z_arm, z_stub in ((1.56, 1.60), (1.09, 1.13)):
    for x in (-0.38, 0.38):
        cube((x, -0.05, z_arm), (0.08, 0.20, 0.05), lacquer, name='Arm')
        cube((x, -0.14, z_stub), (0.055, 0.035, 0.10), lacquer, name='Stub')

# ---------- swords (horizontal, y=-0.10, slight upward rake at tip) ----------
def sword(zc, handle_len, handle_r, guard_r, blade_len, blade_h, hx0):
    # handle
    hxc = hx0 + handle_len / 2
    cyl((hxc, -0.10, zc), handle_r, handle_len, handle_wood, rot=(0, math.pi/2, 0), name='Tsuka')
    # pommel + guard (gold)
    cyl((hx0 - 0.008, -0.10, zc), handle_r + 0.004, 0.022, gold, rot=(0, math.pi/2, 0), name='Kashira')
    gx = hx0 + handle_len + 0.012
    cyl((gx, -0.10, zc), guard_r, 0.022, gold, rot=(0, math.pi/2, 0), name='Tsuba')
    # blade
    bxc = gx + 0.015 + blade_len / 2
    cube((bxc, -0.10, zc), (blade_len, 0.022, blade_h), blade_steel,
         rot=(0, math.radians(-1.5), 0), name='Blade')

# katana (upper) and wakizashi (lower)
sword(1.62, 0.26, 0.038, 0.068, 1.05, 0.055, -0.68)
sword(1.15, 0.22, 0.036, 0.060, 0.86, 0.048, -0.61)

# ---------- red silk cloth draped on base ----------
cube((0.08, -0.02, 0.17), (0.55, 0.26, 0.07), red_silk, rot=(0, 0, math.radians(7)), name='Silk1')
cube((-0.18, -0.06, 0.21), (0.30, 0.20, 0.06), red_silk, rot=(0, 0, math.radians(-14)), name='Silk2')
cube((0.16, -0.175, 0.06), (0.30, 0.035, 0.16), red_silk, rot=(math.radians(6), 0, math.radians(-4)), name='SilkDrape')

# ---------- lighting (custom, cooler + dimmer than v1 which washed out) ----------
area_light((-2.2, -3.0, 2.4), 280, 3.5, (1, 0.88, 0.72), (math.radians(60), 0, math.radians(-28)))
area_light((2.4, -2.6, 1.2), 85, 3.0, (0.72, 0.80, 1.0), (math.radians(75), 0, math.radians(30)))
# cool rim from behind so black lacquer separates from any dark backdrop
area_light((0, 2.5, 2.2), 120, 3.0, (0.78, 0.84, 1.0), (math.radians(-100), 0, 0))
# (front point light removed: it produced a glow smear over the base in v1-v3)

decor_cam()
render_to(OUT, 288, 480, transparent=True, samples=160)
