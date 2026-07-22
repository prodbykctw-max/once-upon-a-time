import bpy, math, os, random, sys
FRAMEWORK = r"C:\Users\Owner\Documents\once-upon-a-time\tools\blender\framework.py"
exec(open(FRAMEWORK).read())
OUT = r"C:\Users\Owner\Documents\once-upon-a-time\assets\renders\outprops_hq"
os.makedirs(OUT, exist_ok=True)

# ── Premium Runner décor per BLENDER_PROPS_BRIEF.md (Fable handoff) ──────────
# Same 16 cells / meanings / silhouettes / 0.45 aspect — a FIDELITY upgrade, not
# a redesign. Rendered 216x480 transparent, front-ortho, bottom-anchored.
# NEUTRAL mid-key colour: the engine now adds per-prop warm/cool tint (aTint),
# so we bake FORM + DETAIL, not hue variants. Lit by a soft HDRI + gentle key.
#
# Quality technique: canopies are subdivided icospheres pushed around by noise
# (organic lumpy silhouette, not a ball) CLAD in ~120 small leaf cards for
# surface detail; trunks get procedural bark with real bump. That reads as
# authored foliage at small size + through fog, where blob-spheres read as clay.
CW, CH = 216, 480          # 2x the 108x240 cell; atlas becomes 3456x480

# ── materials ───────────────────────────────────────────────────────────────
def pmat(name, col, rough=0.8, spec=0.4):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1)
    b.inputs['Roughness'].default_value = rough
    try: b.inputs['Specular IOR Level'].default_value = spec
    except Exception: pass
    return m

def bark_mat(name, base=(0.20, 0.12, 0.06)):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; bsdf = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord')
    # vertical wave = bark ridges, modulated by noise for irregularity
    wav = nt.nodes.new('ShaderNodeTexWave'); wav.inputs['Scale'].default_value = 3.0
    wav.inputs['Distortion'].default_value = 8.0; wav.wave_profile = 'SAW'
    nt.links.new(tc.outputs['Object'], wav.inputs['Vector'])
    noi = nt.nodes.new('ShaderNodeTexNoise'); noi.inputs['Scale'].default_value = 14.0
    nt.links.new(tc.outputs['Object'], noi.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (base[0]*0.5, base[1]*0.5, base[2]*0.5, 1)
    ramp.color_ramp.elements[1].color = (*base, 1)
    nt.links.new(wav.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.85
    bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.5
    nt.links.new(wav.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    return m

def leaf_mat(name, col, rough=0.75):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; bsdf = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord')
    noi = nt.nodes.new('ShaderNodeTexNoise'); noi.inputs['Scale'].default_value = 6.0
    nt.links.new(tc.outputs['Generated'], noi.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (col[0]*0.7, col[1]*0.72, col[2]*0.6, 1)
    ramp.color_ramp.elements[1].color = (min(1,col[0]*1.2), min(1,col[1]*1.2), col[2], 1)
    nt.links.new(noi.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = rough
    try: bsdf.inputs['Subsurface Weight'].default_value = 0.12
    except Exception: pass
    return m

def marble_hq(name, base=(0.86, 0.85, 0.83)):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; bsdf = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord')
    noi = nt.nodes.new('ShaderNodeTexNoise'); noi.inputs['Scale'].default_value = 2.5
    noi.inputs['Detail'].default_value = 6.0
    nt.links.new(tc.outputs['Object'], noi.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*base, 1)
    ramp.color_ramp.elements[1].color = (base[0]*0.72, base[1]*0.72, base[2]*0.76, 1)
    ramp.color_ramp.elements[0].position = 0.35; ramp.color_ramp.elements[1].position = 0.55
    nt.links.new(noi.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.22
    return m

# ── foliage builder: organic canopy + clad leaf cards ───────────────────────
def canopy(cx, cy, cz, rx, ry, rz, tone, seed, density=120, leaf_r=0.11):
    random.seed(seed)
    # base lumpy mass: subdivided icosphere with displacement-ish jitter
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1.0, location=(cx, cy, cz))
    o = bpy.context.active_object
    o.scale = (rx, ry, rz)
    me = o.data
    for v in me.vertices:                         # push verts by pseudo-noise
        n = math.sin(v.co.x*4+seed)*math.cos(v.co.y*4)*math.sin(v.co.z*4+seed*2)
        f = 1.0 + n*0.16
        v.co = (v.co[0]*f, v.co[1]*f, v.co[2]*f)
    core = leaf_mat(f'CanCore{seed}', (tone[0]*0.7, tone[1]*0.72, tone[2]*0.62))
    o.data.materials.append(core)
    for p in o.data.polygons: p.use_smooth = True
    # clad with small leaf cards over the front hemisphere for surface texture
    lm = [leaf_mat(f'Lf{seed}_{i}', c) for i, c in enumerate([
        (tone[0]*0.82, tone[1]*0.85, tone[2]*0.7),
        tone,
        (min(1,tone[0]*1.18), min(1,tone[1]*1.15), tone[2]*0.9)])]
    for _ in range(density):
        u = random.uniform(0, 6.283); v = random.uniform(-0.35, 1.0)
        rr = math.sqrt(1 - min(0.99, v*v))
        px = cx + math.cos(u)*rr*rx*0.98
        py = cy + (-abs(math.sin(u))*ry*0.98)*0.6 - ry*0.15   # bias to front
        pz = cz + v*rz*0.98
        s = sphere((px, py, pz), leaf_r*random.uniform(0.7, 1.2), random.choice(lm))
        s.scale = (1, 0.45, 0.8)
        s.rotation_euler = (random.uniform(0, 3.14), random.uniform(0, 3.14), random.uniform(0, 3.14))
        for pl in s.data.polygons: pl.use_smooth = True
    return o

def trunk(cx, r_bot, r_top, h, mat, flare=True):
    bpy.ops.mesh.primitive_cone_add(radius1=r_bot, radius2=r_top, depth=h,
                                    location=(cx, 0, h/2), vertices=16)
    o = bpy.context.active_object; o.data.materials.append(mat)
    for p in o.data.polygons: p.use_smooth = True
    if flare:
        for k in range(5):                        # root flares
            a = k/5*6.283
            rt = cyl((cx+math.cos(a)*r_bot*0.8, math.sin(a)*r_bot*0.8, 0.04),
                     r_bot*0.32, 0.14, mat, rot=(0.5, 0, a), verts=6)
    return o

def rose(x, y, z, r=0.09, tone=(0.85, 0.16, 0.30)):
    cm = pmat('Rc', tone, 0.6); pm = pmat('Rp', (min(1,tone[0]*1.15), tone[1]*1.3+0.06, tone[2]*1.15), 0.62)
    sphere((x, y, z), r*0.55, cm)
    for ring, cnt, rr in ((0, 5, 0.6), (1, 7, 0.95)):
        for k in range(cnt):
            a = k/cnt*6.283 + ring*0.4
            p = sphere((x+math.cos(a)*r*rr, y-r*0.15, z+math.sin(a)*r*rr*0.6), r*0.5, pm)
            p.scale = (1, 0.4, 0.85); p.rotation_euler = (0, 0, a)
            for pl in p.data.polygons: pl.use_smooth = True

# ── the 16 cells (neutral, premium) ─────────────────────────────────────────
def build(idx):
    random.seed(idx*17+5)
    bark = bark_mat('Bark', (0.22, 0.13, 0.07))
    birch = bark_mat('Birch', (0.80, 0.78, 0.72))
    G1 = (0.30, 0.46, 0.20)     # neutral leaf green (engine tints)

    if idx == 0:      # round bushy tree
        trunk(0, 0.20, 0.13, 1.5, bark)
        canopy(0, 0, 2.15, 0.95, 0.85, 0.95, G1, 10, density=150)
    elif idx == 1:    # tall slim tree (birch)
        trunk(0, 0.11, 0.08, 2.2, birch, flare=False)
        dm = pmat('Dash', (0.14, 0.13, 0.11), 0.8)
        for i in range(6):
            cube((random.uniform(-0.08, 0.08), -0.10, 0.4+i*0.32), (0.07, 0.02, 0.05), dm)
        canopy(0, 0, 2.65, 0.6, 0.55, 0.7, (0.34, 0.5, 0.24), 11, density=90, leaf_r=0.09)
    elif idx == 2:    # blossom tree (neutral pale — engine adds pink warmth)
        trunk(0, 0.16, 0.10, 1.6, bark)
        canopy(0, 0, 2.2, 0.9, 0.82, 0.85, (0.86, 0.80, 0.82), 12, density=160, leaf_r=0.10)
        pm = pmat('Petal', (0.95, 0.82, 0.86), 0.7)   # neutral blush
        for _ in range(40):
            a = random.uniform(0, 6.283); rr = random.uniform(0.4, 0.95)
            sphere((math.cos(a)*rr, -0.3, 2.0+math.sin(a)*rr*0.7), 0.05, pm)
    elif idx == 3:    # willow
        trunk(0, 0.15, 0.10, 1.7, bark)
        canopy(0, 0, 2.15, 0.85, 0.78, 0.6, (0.34, 0.46, 0.24), 13, density=90)
        wl = leaf_mat('Willow', (0.32, 0.44, 0.22))
        for i in range(14):                       # trailing fronds
            a = i/14*6.283
            cyl((math.cos(a)*0.6, math.sin(a)*0.4-0.15, 1.5), 0.03, 1.3, wl,
                rot=(0.12, 0, a), verts=6)
    elif idx == 4:    # round green tree (fuller)
        trunk(0, 0.18, 0.12, 1.4, bark)
        canopy(0, 0, 2.1, 1.0, 0.9, 1.0, (0.28, 0.44, 0.20), 14, density=170)
    elif idx == 5:    # rose bush — taller, dense, prominent blooms
        canopy(0, 0, 0.7, 0.8, 0.62, 0.72, (0.20, 0.36, 0.15), 15, density=150, leaf_r=0.09)
        for _ in range(16):
            a = random.uniform(0, 6.283); rr = random.uniform(0.2, 0.62)
            rose(math.cos(a)*rr, -0.24-random.uniform(0, 0.12), 0.55+random.uniform(0, 0.75), r=0.14)
    elif idx == 6:    # marble fountain
        M = marble_hq('FM', (0.84, 0.83, 0.80))
        cyl((0, 0, 0.22), 0.85, 0.44, M, verts=40)
        cyl((0, 0, 0.7), 0.12, 0.9, M, verts=20)
        cyl((0, 0, 1.15), 0.42, 0.10, M, verts=32)
        water = bpy.data.materials.new('Wat'); water.use_nodes = True
        wb = water.node_tree.nodes['Principled BSDF']
        wb.inputs['Base Color'].default_value = (0.6, 0.8, 0.92, 1)
        wb.inputs['Roughness'].default_value = 0.04
        try: wb.inputs['Transmission Weight'].default_value = 0.6
        except Exception: pass
        cyl((0, 0, 0.46), 0.74, 0.04, water, verts=40)
        cyl((0, 0, 1.2), 0.34, 0.03, water, verts=32)
        sphere((0, 0, 1.5), 0.14, water)
        sm = pmat('Spray', (0.85, 0.93, 1.0), 0.1)
        for _ in range(10):
            sphere((random.uniform(-0.28, 0.28), random.uniform(-0.28, 0.28),
                    1.3+random.uniform(0, 0.35)), 0.03, sm)
    elif idx == 7:    # angel statue
        M = marble_hq('SM', (0.82, 0.81, 0.79))
        cube((0, 0, 0.3), (0.6, 0.6, 0.6), M)                 # plinth
        cyl((0, 0, 0.9), 0.16, 0.7, M, verts=18)              # body
        b = sphere((0, 0, 1.35), 0.2, M); b.scale = (0.7, 0.5, 1.0)   # torso
        sphere((0, -0.02, 1.72), 0.14, M)                     # head
        for sgn in (-1, 1):                                   # smooth swept wings
            for k in range(6):
                fr = k/5.0
                w = sphere((sgn*(0.22+fr*0.5), 0.05, 1.62+fr*0.28), 0.16, M)
                w.scale = (0.34-fr*0.05, 0.09, 0.5-fr*0.28)
                w.rotation_euler = (0, 0, sgn*math.radians(24+fr*20))
                for pl in w.data.polygons: pl.use_smooth = True
        for sgn in (-1, 1):                                   # arms out
            a = cyl((sgn*0.24, -0.05, 1.26), 0.05, 0.42, M, rot=(0, math.radians(sgn*72), 0), verts=12)
            for pl in a.data.polygons: pl.use_smooth = True
        bpy.ops.mesh.primitive_torus_add(major_radius=0.17, minor_radius=0.02, location=(0, 0, 1.95))
        bpy.context.active_object.data.materials.append(gold_mat('Halo'))
    elif idx == 8:    # glow-flower / lamp (neutral warm-white emissive)
        stm = leaf_mat('Stem', (0.24, 0.4, 0.16))
        cyl((0, 0, 0.6), 0.16, 1.2, stm, verts=12)
        cap = sphere((0, 0, 1.35), 0.5, pmat('Cap', (0.9, 0.82, 0.85), 0.5)); cap.scale = (1, 1, 0.6)
        gl = emissive_mat('Glow', (1, 0.9, 0.8), 3.0)
        for _ in range(6):
            sphere((random.uniform(-0.2, 0.2), -0.2, 1.3+random.uniform(0, 0.15)), 0.06, gl)
    elif idx == 9:    # golden daisies (neutral gold)
        stm = leaf_mat('DStem', (0.22, 0.4, 0.14))
        petal = pmat('Pet', (0.92, 0.82, 0.4), 0.55)
        core = pmat('Core', (0.4, 0.28, 0.1), 0.7)
        for (fx, fs) in ((-0.35, 0.85), (-0.05, 1.1), (0.28, 0.8), (0.5, 0.7)):
            cyl((fx, 0, 0.55*fs), 0.03, 1.1*fs, stm, verts=8)
            cc = sphere((fx, -0.04, 1.12*fs), 0.11*fs, core); cc.scale = (1, 0.5, 1)
            for k in range(10):
                a = k/10*6.283
                p = sphere((fx+math.cos(a)*0.16*fs, -0.03, 1.12*fs+math.sin(a)*0.16*fs), 0.06*fs, petal)
                p.scale = (1, 0.3, 0.55); p.rotation_euler = (0, 0, a)
    elif idx == 10:   # swan statue (marble + gold orb)
        M = marble_hq('SwM', (0.85, 0.84, 0.82))
        b = sphere((0, 0, 0.5), 0.42, M); b.scale = (0.8, 1.3, 0.7)
        cyl((0, -0.45, 0.9), 0.09, 0.9, M, rot=(0.3, 0, 0), verts=12)
        sphere((0, -0.7, 1.35), 0.14, M)
        wq = sphere((0.2, 0.05, 0.7), 0.3, M); wq.scale = (0.4, 1, 0.8)
        wq2 = sphere((-0.2, 0.05, 0.7), 0.3, M); wq2.scale = (0.4, 1, 0.8)
        sphere((0, 0, 1.75), 0.18, gold_mat('Orb'))
    elif idx == 11:   # live swan
        sw = pmat('Swan', (0.96, 0.96, 0.94), 0.6)
        b = sphere((0, 0, 0.42), 0.42, sw); b.scale = (0.85, 1.35, 0.72)
        for pl in b.data.polygons: pl.use_smooth = True
        # layered wing feathers (bigger, arched over the back)
        for sgn in (-1, 1):
            for k in range(6):
                fr = k/5.0
                f = sphere((sgn*(0.26+fr*0.12), 0.05+fr*0.2, 0.58+fr*0.18), 0.3, sw)
                f.scale = (0.42, 1.05, 0.16); f.rotation_euler = (math.radians(fr*18), 0, sgn*math.radians(14+fr*10))
                for pl in f.data.polygons: pl.use_smooth = True
        cyl((0, -0.5, 0.85), 0.08, 0.95, sw, rot=(math.radians(20), 0, 0), verts=12)
        hd = sphere((0, -0.62, 1.3), 0.13, sw)
        bpy.ops.mesh.primitive_cone_add(radius1=0.05, radius2=0.005, depth=0.16,
                                        location=(0, -0.76, 1.28), rotation=(math.radians(95), 0, 0), vertices=8)
        bpy.context.active_object.data.materials.append(pmat('Beak', (0.9, 0.5, 0.12), 0.5))
    elif idx == 12:   # globe on stand (indoor)
        warm = bark_mat('W', (0.34, 0.2, 0.1))
        cyl((0, 0, 0.5), 0.06, 1.0, warm, verts=12)
        cyl((0, 0, 0.05), 0.22, 0.1, warm, verts=16)
        gl = pmat('Globe', (0.24, 0.44, 0.56), 0.35)
        sphere((0, 0, 1.2), 0.32, gl)
        bpy.ops.mesh.primitive_torus_add(major_radius=0.37, minor_radius=0.015, location=(0, 0, 1.2), rotation=(math.radians(70), 0, 0))
        bpy.context.active_object.data.materials.append(gold_mat('Ring'))
    elif idx == 13:   # topiary (indoor)
        pot = pmat('Pot', (0.5, 0.32, 0.2), 0.6)
        cyl((0, 0, 0.25), 0.28, 0.5, pot, verts=20)
        canopy(0, 0, 0.95, 0.42, 0.4, 0.5, (0.26, 0.42, 0.18), 33, density=80, leaf_r=0.07)
        canopy(0, 0, 1.5, 0.34, 0.32, 0.4, (0.28, 0.44, 0.2), 34, density=60, leaf_r=0.06)
    else:             # 14,15: bunny critter
        fur = pmat('Fur', (0.92, 0.9, 0.86), 0.9)
        b = sphere((0, 0, 0.32), 0.32, fur); b.scale = (0.85, 1.1, 0.9)
        for pl in b.data.polygons: pl.use_smooth = True
        hd = sphere((0, -0.28, 0.62), 0.2, fur)
        for pl in hd.data.polygons: pl.use_smooth = True
        for sgn in (-1, 1):
            e = sphere((sgn*0.09, -0.3, 0.92), 0.07, fur); e.scale = (0.55, 0.4, 1.9)
        sphere((0, 0.32, 0.35), 0.1, pmat('Tail', (0.98, 0.97, 0.95), 0.95))
        em = pmat('Eye', (0.08, 0.05, 0.04), 0.4)
        for sgn in (-1, 1):
            sphere((sgn*0.08, -0.45, 0.66), 0.028, em)

# ── render ──────────────────────────────────────────────────────────────────
only = None
for a in sys.argv:
    if a.startswith('--only='): only = a.split('=', 1)[1]

CELLS = range(16) if not only else [int(x) for x in only.split(',')]
for idx in CELLS:
    sc = reset_scene()
    if not hdri_world('blossom', strength=1.15, rot_z=math.radians(-25)):
        w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
        w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.4
    build(idx)
    # soft shaping key + cool rim so silhouettes pop; HDRI carries ambient
    area_light((-1.6, -2.6, 2.8), 80, 2.6, (1, 0.96, 0.88), (math.radians(50), 0, math.radians(-28)))
    area_light((2.0, -1.4, 1.4), 40, 2.2, (0.8, 0.86, 1.0), (math.radians(64), 0, math.radians(40)))
    # ONE consistent front-ortho frame for ALL props: bottom edge = z=0 (props
    # plant on the ground), top = ~z FRAME_H. Same frame for every prop keeps
    # RELATIVE heights (a tree fills it; a bush sits in the lower third) and
    # makes bottom-anchoring automatic. Cell aspect 0.45 (216:480).
    FRAME_H = 3.35
    d = bpy.data.cameras.new('C'); d.type = 'ORTHO'; d.ortho_scale = FRAME_H
    d.sensor_fit = 'VERTICAL'                          # ortho_scale = vertical extent
    c = bpy.data.objects.new('C', d); sc.collection.objects.link(c)
    c.location = (0, -6.0, FRAME_H/2 - 0.06); c.rotation_euler = (math.radians(90), 0, 0)
    sc.camera = c
    sc.view_settings.view_transform = 'Filmic'
    # render 2x the cell (432x960) for AA; the atlas composer downscales.
    render_to(os.path.join(OUT, f'prop_{idx}.png'), CW*2, CH*2, transparent=True, samples=140)
    print(f'HQPROP_{idx}_DONE')
print('HQPROPS_DONE')
