FRAMEWORK = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\framework.py"
exec(open(FRAMEWORK).read())

OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\tiles\floor_2.png"

reset_scene()

# ---------- materials ----------
def tatami_mat(name, tone=(0.55, 0.5, 0.3), direction='X', light_mult=1.0):
    # fine woven ridges: wave bands + noise variation + bump
    m, nt, b = _new_mat(name)
    mp = _tex_coord_chain(nt, (1, 1, 1))
    wave = nt.nodes.new('ShaderNodeTexWave')
    wave.wave_type = 'BANDS'
    wave.bands_direction = direction
    wave.inputs['Scale'].default_value = 22.0
    wave.inputs['Distortion'].default_value = 1.2
    wave.inputs['Detail'].default_value = 2.0
    nt.links.new(mp.outputs[0], wave.inputs['Vector'])
    noise = nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 14.0
    noise.inputs['Detail'].default_value = 6.0
    nt.links.new(mp.outputs[0], noise.inputs['Vector'])
    mixfac = nt.nodes.new('ShaderNodeMix')
    mixfac.data_type = 'FLOAT'
    mixfac.inputs['Factor'].default_value = 0.25
    nt.links.new(wave.outputs['Fac'], mixfac.inputs['A'])
    nt.links.new(noise.outputs['Fac'], mixfac.inputs['B'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    d = 0.48
    lm = 1.30 * light_mult
    ramp.color_ramp.elements[0].color = (tone[0]*d, tone[1]*d, tone[2]*d, 1)
    ramp.color_ramp.elements[1].color = (min(1, tone[0]*lm), min(1, tone[1]*lm), min(1, tone[2]*lm), 1)
    nt.links.new(mixfac.outputs['Result'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.75
    b.inputs['Sheen Weight'].default_value = 0.35
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.5
    nt.links.new(wave.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs[0], b.inputs['Normal'])
    return m

tatami_a = tatami_mat('TatamiA', tone=(0.46, 0.43, 0.20), direction='X', light_mult=1.0)
tatami_b = tatami_mat('TatamiB', tone=(0.48, 0.44, 0.19), direction='Y', light_mult=1.06)
border_wood = wood_mat('BorderWood', tone=(0.085, 0.05, 0.028), grain_scale=10.0, rough=0.45)

# ---------- geometry (top-down frame: x,y in [-1,1]) ----------
# two tatami mats, weave directions crossed
cube((-0.5, 0, 0.0), (0.96, 1.96, 0.06), tatami_a, name='MatA')
cube((0.5, 0, 0.0), (0.96, 1.96, 0.06), tatami_b, name='MatB')

# dark wood border strips: center + edges (edges tile seamlessly)
cube((0, 0, 0.008), (0.10, 2.1, 0.075), border_wood, name='StripC')
cube((-1.0, 0, 0.008), (0.10, 2.1, 0.075), border_wood, name='StripL')
cube((1.0, 0, 0.008), (0.10, 2.1, 0.075), border_wood, name='StripR')
cube((0, -1.0, 0.008), (2.1, 0.10, 0.075), border_wood, name='StripB')
cube((0, 1.0, 0.008), (2.1, 0.10, 0.075), border_wood, name='StripT')

# ---------- lighting: warm key above-left, cool fill, low warm rake for weave ----------
area_light((-1.8, -1.2, 3.0), 300, 3.5, (1, 0.92, 0.75), (math.radians(22), 0, math.radians(-25)))
area_light((1.8, 1.5, 2.6), 90, 3.0, (0.72, 0.80, 1.0), (math.radians(-16), 0, math.radians(20)))
point_light((0.2, -1.6, 0.5), 50, (1, 0.75, 0.45), 0.3)

floor_cam()
render_to(OUT, 192, 192, transparent=False, samples=160)
