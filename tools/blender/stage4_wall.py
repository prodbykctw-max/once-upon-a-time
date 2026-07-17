FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())
import math, random

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles\wall_4.png"

sc = reset_scene()

w = bpy.data.worlds.new('W'); w.use_nodes = True
bg = w.node_tree.nodes['Background']
bg.inputs[0].default_value = (0.75, 0.68, 0.55, 1)
bg.inputs[1].default_value = 0.07
sc.world = w

random.seed(41)

# ---------- materials ----------
mortar = stone_mat('Mortar', tone=(0.22, 0.20, 0.17), rough=0.92, scale=9.0, bump=0.2)
ashlars = [
    stone_mat('AshA', tone=(0.64, 0.58, 0.47), rough=0.82, scale=4.0, bump=0.16),
    stone_mat('AshB', tone=(0.68, 0.61, 0.49), rough=0.80, scale=6.0, bump=0.14),
    stone_mat('AshC', tone=(0.60, 0.55, 0.45), rough=0.85, scale=5.0, bump=0.18),
    stone_mat('AshD', tone=(0.67, 0.62, 0.52), rough=0.80, scale=7.0, bump=0.15),
]
slate     = stone_mat('Slate', tone=(0.075, 0.085, 0.115), rough=0.40, scale=6.0, bump=0.12)
slate_pan = stone_mat('SlatePanel', tone=(0.105, 0.115, 0.15), rough=0.36, scale=7.0, bump=0.10)
rail_m    = marble_mat('Rail', base=(0.26, 0.27, 0.30), vein=(0.10, 0.11, 0.13), rough=0.26)
niche_dark = stone_mat('NicheDark', tone=(0.035, 0.03, 0.028), rough=0.9, scale=6.0, bump=0.1)
frame_m   = marble_mat('Frame', base=(0.44, 0.35, 0.23), vein=(0.24, 0.18, 0.11), rough=0.34)
terra     = stone_mat('Terracotta', tone=(0.40, 0.155, 0.075), rough=0.62, scale=9.0, bump=0.08)

# ---------- wall base ----------
plane((0, 0.09, 0), 4.5, mortar, rot=(math.radians(90), 0, 0), name='WallBase')

# ---------- ashlar courses, clipped around the niche ----------
NX0, NX1 = -0.415, 0.415
NZ0, NZ1 = -0.175, 0.775
bw, bh, gap = 0.44, 0.28, 0.012

def add_block(x0, x1, z):
    wdt = x1 - x0
    if wdt < 0.05:
        return
    cube(((x0 + x1) / 2, 0.055, z), (wdt, 0.05, bh), random.choice(ashlars), name='Blk')

zrow = -0.35 + bh / 2
row = 0
while zrow < 1.15:
    xoff = 0.0 if row % 2 == 0 else (bw + gap) / 2
    x = -0.95 + xoff
    while x < 1.05:
        x0, x1 = x - bw / 2, x + bw / 2
        z0, z1 = zrow - bh / 2, zrow + bh / 2
        if x1 > NX0 and x0 < NX1 and z1 > NZ0 and z0 < NZ1:
            add_block(x0, min(x1, NX0), zrow)   # left sliver
            add_block(max(x0, NX1), x1, zrow)   # right sliver
        else:
            add_block(x0, x1, zrow)
        x += bw + gap
    zrow += bh + gap
    row += 1

# ---------- dark slate wainscot ----------
cube((0, 0.02, -0.70), (2.0, 0.10, 0.76), slate, name='Wainscot')
for px in (-0.585, -0.195, 0.195, 0.585):
    cube((px, -0.005, -0.68), (0.30, 0.10, 0.42), slate_pan, name='Panel')
cube((0, -0.02, -0.325), (2.0, 0.13, 0.055), rail_m, name='Rail')

# ---------- central framed niche (no overlapping frame pieces) ----------
cube((0, 0.075, 0.30), (0.64, 0.02, 0.76), niche_dark, name='NicheBack')
# jambs full height, bars only between them
cube((-0.35, -0.03, 0.30), (0.10, 0.14, 0.92), frame_m, name='FrameL')
cube(( 0.35, -0.03, 0.30), (0.10, 0.14, 0.92), frame_m, name='FrameR')
cube((0, -0.03, 0.71), (0.60, 0.14, 0.10), frame_m, name='FrameT')
cube((0, -0.04, -0.11), (0.60, 0.17, 0.10), frame_m, name='FrameSill')
# projecting lintel above and sill base below (cover the clip margins)
cube((0, -0.045, 0.795), (0.92, 0.15, 0.075), frame_m, name='Lintel')
cube((0, -0.035, -0.245), (0.92, 0.14, 0.17), frame_m, name='SillBase')

# ---------- terracotta amphora ----------
ay = 0.02
cyl((0, ay, -0.035), 0.065, 0.05, terra, name='AmpFoot')
b = sphere((0, ay, 0.10), 0.15, terra, name='AmpBody'); b.scale = (1.0, 1.0, 1.06)
sphere((0, ay, 0.305), 0.10, terra, name='AmpShoulder')
cyl((0, ay, 0.445), 0.042, 0.18, terra, name='AmpNeck')
cyl((0, ay, 0.545), 0.066, 0.035, terra, name='AmpRim')
cyl((-0.115, ay, 0.40), 0.016, 0.19, terra, rot=(0, math.radians(18), 0), name='AmpHandL')
cyl(( 0.115, ay, 0.40), 0.016, 0.19, terra, rot=(0, math.radians(-18), 0), name='AmpHandR')

# ---------- lights (custom, dimmer than warm_rig to keep stone from washing out) ----------
area_light((-2.2, -3.0, 2.4), 330, 3.5, (1.0, 0.87, 0.68), rot=(math.radians(60), 0, math.radians(-28)))
area_light(( 2.4, -2.6, 1.2), 110, 3.0, (0.68, 0.77, 1.0), rot=(math.radians(75), 0, math.radians(30)))
# warm museum spot pooled on the amphora
point_light((0, -0.25, 0.58), energy=4.5, color=(1.0, 0.66, 0.30), radius=0.05)

wall_cam()
render_to(OUT, 288, 384, transparent=False, samples=160)
