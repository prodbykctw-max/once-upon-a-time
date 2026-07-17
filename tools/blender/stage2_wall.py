FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles\wall_2.png"

reset_scene()

# ---------- materials ----------
dark_wood = wood_mat('DarkWood', tone=(0.055, 0.030, 0.017), grain_scale=6.0, rough=0.4)
lattice_wood = wood_mat('LatticeWood', tone=(0.045, 0.026, 0.016), grain_scale=8.0, rough=0.5)
red_lacquer = fabric_mat('RedLacquer', tone=(0.38, 0.020, 0.020), rough=0.3)

# shoji paper: warm white, rough, faint warm emission = backlit translucency
def shoji_mat():
    m, nt, b = _new_mat('Shoji')
    b.inputs['Base Color'].default_value = (0.88, 0.84, 0.72, 1)
    b.inputs['Roughness'].default_value = 0.9
    b.inputs['Emission Color'].default_value = (1.0, 0.90, 0.70, 1)
    b.inputs['Emission Strength'].default_value = 0.12
    mp = _tex_coord_chain(nt, (1, 1, 1))
    noise = nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 60.0
    nt.links.new(mp.outputs[0], noise.inputs['Vector'])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.05
    nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs[0], b.inputs['Normal'])
    return m

shoji = shoji_mat()

# ---------- geometry (frame: x [-0.75,0.75], z [-1,1], wall at y~0.1) ----------
# full shoji backing
p = plane((0, 0.12, 0), 1, shoji, rot=(math.pi/2, 0, 0), name='ShojiBack')
p.scale = (1.6, 2.2, 1)

# vertical posts (edges + center) - tile seamlessly at x=+/-0.75
for x in (-0.75, 0.0, 0.75):
    cube((x, 0.0, 0), (0.16, 0.10, 2.2), dark_wood, name='Post')

# horizontal beams
cube((0, 0.01, -0.90), (1.6, 0.08, 0.22), dark_wood, name='BottomRail')
cube((0, 0.01, 0.94), (1.6, 0.08, 0.18), dark_wood, name='TopBeam')
cube((0, 0.01, 0.505), (1.6, 0.08, 0.08), dark_wood, name='MidRail')
# red lacquer accent beam, slightly proud of the wall
cube((0, -0.005, 0.78), (1.6, 0.10, 0.10), red_lacquer, name='RedBeam')

# ---------- lattice grid over main shoji panels ----------
main_z0, main_z1 = -0.79, 0.465
mh = main_z1 - main_z0
mzc = (main_z0 + main_z1) / 2
panels = [(-0.67, -0.08), (0.08, 0.67)]
for (x0, x1) in panels:
    pw = x1 - x0
    pxc = (x0 + x1) / 2
    # vertical strips
    for i in range(1, 4):
        x = x0 + pw * i / 4
        cube((x, 0.095, mzc), (0.02, 0.03, mh), lattice_wood, name='LatV')
    # horizontal strips
    for j in range(1, 6):
        z = main_z0 + mh * j / 6
        cube((pxc, 0.095, z), (pw, 0.03, 0.02), lattice_wood, name='LatH')

# transom band (ranma) lattice: dense verticals between mid rail and red beam
tz0, tz1 = 0.545, 0.72
tzc = (tz0 + tz1) / 2
th = tz1 - tz0
x = -0.63
while x <= 0.631:
    if abs(x) > 0.11:
        cube((x, 0.095, tzc), (0.018, 0.03, th), lattice_wood, name='TranV')
    x += 0.09

# ---------- lighting (custom, ~40% of v1 energy: v1 was blown out) ----------
area_light((-2.2, -3.0, 2.4), 240, 3.5, (1, 0.88, 0.70), (math.radians(60), 0, math.radians(-28)))
area_light((2.4, -2.6, 1.2), 75, 3.0, (0.72, 0.80, 1.0), (math.radians(75), 0, math.radians(30)))
# gentle frontal fill so nothing crushes to black
area_light((0, -3.5, 0.1), 85, 4.0, (1, 0.96, 0.88), (math.pi/2, 0, 0))
# warm lantern accent low right
point_light((0.5, -1.4, -0.35), 55, (1, 0.70, 0.38), 0.2)

wall_cam()
render_to(OUT, 288, 384, transparent=False, samples=160)
