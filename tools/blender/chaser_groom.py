import math, random, os
FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())
OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\chaser"

# THE GROOM'S SHADOW — spectral phantom groom, 4 animation frames.
# Camera frames 176x224 ratio; content plane XZ, camera looks +Y.

def build_groom(phase):
    """phase 0..3 — cape sway + bob + tail curl animation"""
    sc = reset_scene()
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.12
    w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.3, 0.2, 0.45, 1)

    def matte(name, tone, rough=0.8, coat=0.0):
        m = bpy.data.materials.new(name); m.use_nodes = True
        b = m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value = (*tone, 1)
        b.inputs['Roughness'].default_value = rough
        if coat: b.inputs['Coat Weight'].default_value = coat
        return m

    def glow(name, tone, strength):
        m = bpy.data.materials.new(name); m.use_nodes = True
        b = m.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value = (*tone, 1)
        b.inputs['Emission Color'].default_value = (*tone, 1)
        b.inputs['Emission Strength'].default_value = strength
        return m

    suit = matte('Suit', (0.015, 0.012, 0.025), rough=0.6, coat=0.6)
    shirt = matte('Shirt', (0.55, 0.55, 0.58), rough=0.5)
    tie = matte('Tie', (0.04, 0.02, 0.06), rough=0.4)
    skin = matte('Mask', (0.42, 0.4, 0.45), rough=0.55)   # pale spectral face
    eye = glow('Eye', (1.0, 0.04, 0.1), 7)
    wisp = matte('Wisp', (0.03, 0.02, 0.06), rough=0.9)
    gold = bpy.data.materials.new('Ring'); gold.use_nodes = True
    gb = gold.node_tree.nodes['Principled BSDF']
    gb.inputs['Base Color'].default_value = (0.75, 0.55, 0.15, 1)
    gb.inputs['Metallic'].default_value = 1.0
    gb.inputs['Roughness'].default_value = 0.25

    bob = math.sin(phase / 4 * math.pi * 2) * 0.06
    sway = math.sin(phase / 4 * math.pi * 2 + 1.2) * 1.0  # cape sway degrees base
    tilt = math.sin(phase / 4 * math.pi * 2) * 2.5

    zb = 1.1 + bob  # torso center height

    # wispy ghost tail (no legs): stacked shrinking spheres curving with phase
    curl = math.sin(phase / 4 * math.pi * 2) * 0.12
    for i in range(6):
        t = i / 5
        r = 0.30 - t * 0.2
        x = curl * t * t * 2.2
        z = zb - 0.45 - t * 0.62
        s = sphere((x, 0, z), r, wisp)
        s.scale = (1, 0.7, 1.15)
    # torso: tailcoat
    to = sphere((0, 0, zb), 0.32, suit); to.scale = (0.9, 0.58, 1.25)
    # shirt front V + bowtie
    sh = sphere((0, -0.17, zb + 0.16), 0.13, shirt); sh.scale = (0.55, 0.4, 0.95)
    bt = cube((0, -0.28, zb + 0.3), (0.14, 0.04, 0.05), tie)
    sphere((0, -0.29, zb + 0.3), 0.035, tie)
    # tailcoat lapels: two angled dark slabs over shirt edges
    for sgn in (-1, 1):
        lp = cube((sgn * 0.12, -0.24, zb + 0.14), (0.09, 0.03, 0.3), suit,
                  rot=(0, math.radians(-12 * sgn), math.radians(8 * sgn)))
    # arms reaching forward-down (grabbing pose), phase-alternating
    reach = math.sin(phase / 4 * math.pi * 2) * 0.08
    for sgn in (-1, 1):
        ax = sgn * 0.4
        arm = cyl((ax, -0.18, zb + 0.05 + sgn * reach * 0.5), 0.07, 0.62, suit,
                  rot=(math.radians(55), 0, math.radians(-18 * sgn)), verts=16)
        # skeletal hand: palm + 3 fingers
        hz = zb - 0.22 + sgn * reach * 0.5
        sphere((ax + sgn * 0.06, -0.44, hz), 0.055, skin)
        for f in range(3):
            fg = cyl((ax + sgn * 0.06 + (f - 1) * 0.035, -0.5, hz - 0.03), 0.012, 0.1, skin,
                     rot=(math.radians(70), 0, 0), verts=8)
    # cape: two big swaying panels behind
    for sgn in (-1, 1):
        cp = cube((sgn * 0.22, 0.24, zb - 0.25), (0.42, 0.05, 1.3), wisp,
                  rot=(math.radians(-6), math.radians((sway * 4 + 6) * sgn), math.radians(sway * 2 * sgn)))
    # collar
    cyl((0, 0.02, zb + 0.34), 0.15, 0.12, suit, verts=20)
    # head: pale gaunt face, slight tilt
    hd = sphere((0, -0.02, zb + 0.56), 0.21, skin)
    hd.scale = (0.85, 0.8, 1.1)
    hd.rotation_euler = (0, math.radians(tilt), 0)
    # hollow eye sockets + glowing eyes
    for sgn in (-1, 1):
        sphere((sgn * 0.08, -0.18, zb + 0.6), 0.045, tie)
        sphere((sgn * 0.08, -0.2, zb + 0.6), 0.028, eye)
    # grim mouth slit
    cube((0, -0.2, zb + 0.47), (0.09, 0.02, 0.012), tie)
    # top hat with gold band
    cyl((0, 0.0, zb + 0.78), 0.155, 0.06, suit, verts=24)          # brim
    cyl((0, 0.0, zb + 0.94), 0.115, 0.3, suit, verts=24)           # crown
    cyl((0, 0.0, zb + 0.84), 0.12, 0.05, gold, verts=24)           # band
    # wedding ring on one finger — the groom who lied
    cyl((0.46, -0.5, zb - 0.25), 0.02, 0.015, gold, rot=(math.radians(70), 0, 0), verts=12)

    # violet rim + cold key lighting
    area_light((-1.6, -2.4, 2.6), 170, 2.6, (0.7, 0.68, 0.95), (math.radians(52), 0, math.radians(-26)))
    area_light((1.8, -1.6, 1.6), 130, 2.0, (0.5, 0.2, 0.8), (math.radians(62), 0, math.radians(40)))
    point_light((0, -0.9, zb + 0.6), 12, (1, 0.15, 0.3), 0.15)  # eye glow spill
    # decor-style cam but 176x224 ratio: ortho spans 2.5 tall, 176/224*2.5=1.964 wide
    ortho_cam((0, -4, 1.15), (math.pi / 2, 0, 0), 2.5)

build_groom(0)
render_to(os.path.join(OUT, 'groom_0.png'), 352, 448, transparent=True, samples=160)
build_groom(1)
render_to(os.path.join(OUT, 'groom_1.png'), 352, 448, transparent=True, samples=160)
build_groom(2)
render_to(os.path.join(OUT, 'groom_2.png'), 352, 448, transparent=True, samples=160)
build_groom(3)
render_to(os.path.join(OUT, 'groom_3.png'), 352, 448, transparent=True, samples=160)
print('GROOM_DONE')
