import math, random, sys, os
FW = r"C:\Users\Owner\Documents\once-upon-a-time\tools\blender\whimsy_framework.py"
exec(open(FW).read())
OUT = r"C:\Users\Owner\Documents\once-upon-a-time\assets\renders\whimsy\walls"

def bg_plane(top, bot):
    # sky/backdrop gradient behind the wall opening
    m = mat('Bg', top); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping')
    grad = nt.nodes.new('ShaderNodeTexGradient'); mp.inputs['Rotation'].default_value=(0,math.radians(-90),0)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs[0], grad.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color=(*bot,1); ramp.color_ramp.elements[1].color=(*top,1)
    nt.links.new(grad.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Emission Color'].default_value=(*top,1); b.inputs['Emission Strength'].default_value=0.35
    return m

def frame_rect(cx, cz, hw, hh, t, m, y=-0.02):
    cube((cx, y, cz+hh), (hw*2+t*2, 0.05, t), m)
    cube((cx, y, cz-hh), (hw*2+t*2, 0.05, t), m)
    cube((cx-hw-t/2, y, cz), (t, 0.05, hh*2), m)
    cube((cx+hw+t/2, y, cz), (t, 0.05, hh*2), m)

def w0_library():  # SUNLIT LIBRARY — honey shelves + sky window + sunbeam
    plane((0,0.12,0), 2.4, mat('WL', PAL['honey_dk'], rough=0.6), rot=(math.pi/2,0,0))
    wood = mat('Shelf', PAL['honey'], rough=0.5)
    for i in range(5):
        z=-0.85+i*0.42
        cube((0,0.02,z), (0.62,0.14,0.03), wood)
    spines=[PAL['rose'],PAL['sky'],PAL['leaf'],PAL['gold'],PAL['lav'],PAL['coral'],PAL['blossom']]
    random.seed(0)
    for row in range(4):
        z=-0.62+row*0.42; x=-0.56
        while x<0.56:
            bw=random.uniform(0.03,0.055); bh=random.uniform(0.24,0.32)
            cube((x+bw/2,-0.03,z+bh/2), (bw,0.05,bh), mat('bk',random.choice(spines),rough=0.6))
            x+=bw+0.006
    # arched sky window upper-right
    plane((0.42,0.09,0.72),1, bg_plane(PAL['skyhi'],PAL['sky']),rot=(math.pi/2,0,0)); bpy.context.active_object.scale=(0.28,0.34,1)
    frame_rect(0.42,0.72,0.28,0.34,0.03, mat('WF',PAL['cream'],rough=0.5))
    ball((0.5,-0.05,0.85),0.05, mat('sun',PAL['glow_yl'],emit=3.0)); point((0.5,-0.4,0.85),40,(1,0.95,0.7))
    # butterflies
    for (x,z) in [(-0.3,0.6),(0.15,0.3)]:
        for s in (-1,1): cube((x+s*0.04,-0.15,z),(0.03,0.005,0.05),mat('bf',PAL['rose'],emit=1.5),rot=(0,math.radians(30*s),0))
    sky_world(PAL['skyhi'],0.7); highkey()

def w1_rose():  # ROSE GARDEN — hedge + climbing roses + sky
    plane((0,0.14,0.4), 2.4, bg_plane(PAL['skyhi'],PAL['sky']), rot=(math.pi/2,0,0))  # sky top
    # hedge lower 2/3
    hedge=mat('Hedge',PAL['leaf_dk'],rough=0.85)
    cube((0,0.08,-0.5),(0.8,0.14,0.6), hedge)
    random.seed(1)
    for i in range(60):
        x=random.uniform(-0.72,0.72); z=random.uniform(-1.05,0.12)
        ball((x,-0.02,z), random.uniform(0.05,0.09), mat('lf',random.choice([PAL['leaf'],PAL['leaf_dk']]),rough=0.8))
    # roses climbing
    for i in range(22):
        x=random.uniform(-0.7,0.7); z=random.uniform(-0.9,0.15)
        ball((x,-0.12,z), random.uniform(0.03,0.055), mat('rs',random.choice([PAL['rose'],PAL['rose_dk'],PAL['blossom']]),rough=0.5))
    # white trellis arch
    tr=mat('Trellis',PAL['white'],rough=0.4)
    for x in (-0.62,0.62): cube((x,0.0,-0.2),(0.03,0.04,0.9),tr)
    torus((0,0.0,0.28),0.62,0.03, tr, rot=(math.pi/2,0,0))
    # doves
    for (x,z) in [(-0.2,0.5),(0.3,0.65)]:
        ball((x,-0.2,z),0.05,mat('dove',PAL['white'],rough=0.6))
    sky_world(PAL['skyhi'],0.85); highkey()

def w2_blossom():  # BLOSSOM PROMENADE — cherry canopy + red bridge + petals
    plane((0,0.14,0), 2.4, bg_plane(PAL['blossom'],PAL['pink']), rot=(math.pi/2,0,0))
    random.seed(2)
    # cherry canopy clusters upper
    for i in range(70):
        x=random.uniform(-0.75,0.75); z=random.uniform(0.05,1.0)
        ball((x,-0.05,z), random.uniform(0.06,0.12), mat('blo',random.choice([PAL['blossom'],PAL['pink'],PAL['rose']]),rough=0.6,sheen=0.5))
    # dark branch
    br=mat('Branch',PAL['honey_dk'],rough=0.7)
    cube((-0.1,0.02,0.5),(1.2,0.05,0.04),br,rot=(0,math.radians(8),0))
    # red bridge rail lower
    red=mat('Red',PAL['red'],rough=0.4)
    cube((0,-0.02,-0.72),(0.78,0.06,0.05),red)
    for x in [-0.5,-0.15,0.2,0.55]: cube((x,-0.02,-0.85),(0.04,0.06,0.22),red)
    # falling petals
    for i in range(18):
        x=random.uniform(-0.7,0.7); z=random.uniform(-0.6,0.4)
        cube((x,-0.2,z),(0.025,0.004,0.035),mat('pt',PAL['blossom'],emit=0.6),rot=(0,random.uniform(0,3),0))
    sky_world(PAL['blossom'],0.85); highkey()

def w3_ballroom():  # CRYSTAL BALLROOM — pink panels + gold mirror + chandelier
    plane((0,0.12,0), 2.4, mat('BR', PAL['pink'], rough=0.4, sheen=0.4), rot=(math.pi/2,0,0))
    gold=mat('Gold',PAL['goldmet'],rough=0.25,metal=1.0)
    # tall arched mirror
    mir=mat('Mirror',(0.86,0.88,0.92),rough=0.04,metal=1.0)
    plane((0,0.06,0.1),1,mir,rot=(math.pi/2,0,0)); bpy.context.active_object.scale=(0.34,0.6,1)
    ball((0,0.05,0.72),0.34,mir); bpy.context.active_object.scale=(1,0.3,0.5)  # arch top hint
    frame_rect(0,0.1,0.34,0.62,0.035,gold)
    # wall sconces
    for x in (-0.55,0.55):
        cube((x,-0.02,0.2),(0.05,0.06,0.28),mat('P',PAL['cream'],rough=0.5))
        ball((x,-0.1,0.42),0.06,mat('fl',PAL['glow_yl'],emit=3)); point((x,-0.3,0.42),18,(1,0.9,0.7))
    # panel molding
    for x in (-0.62,0.62): cube((x,0.04,0),(0.02,0.06,1.9),gold)
    # chandelier crystals top
    for i in range(9):
        a=i/9*6.28; ball((math.cos(a)*0.14,-0.05,0.88+math.sin(a)*0.04),0.03,mat('cr',(0.9,0.93,1),rough=0.03,emit=1))
    sky_world(PAL['pink'],0.6); highkey()

def w4_fountain():  # FOUNTAIN PLAZA — arch to sky + rainbow + ivy
    plane((0,0.14,0), 2.4, bg_plane(PAL['skyhi'],PAL['sky']), rot=(math.pi/2,0,0))
    stone=mat('Stone',PAL['marble'],rough=0.6)
    # arch opening framed in pale stone; stone on sides
    cube((-0.62,0.05,0),(0.28,0.1,1.9),stone); cube((0.62,0.05,0),(0.28,0.1,1.9),stone)
    cube((0,0.02,0.85),(0.96,0.09,0.24),stone)  # top spans between pillars, offset Y (no z-fight)
    torus((0,0.04,0.5),0.48,0.05, stone, rot=(math.pi/2,0,0))
    # rainbow arc in the sky opening
    cols=[(0.9,0.4,0.4),(0.95,0.7,0.4),(0.95,0.92,0.5),(0.5,0.85,0.5),(0.5,0.7,0.95),(0.7,0.5,0.9)]
    for i,c in enumerate(cols):
        torus((0,-0.08,-0.15),0.30+i*0.03,0.012, mat('rb',srgb(int(c[0]*255),int(c[1]*255),int(c[2]*255)),emit=1.2), rot=(math.pi/2,0,0))
    # clouds
    for (x,z,r) in [(-0.25,0.55,0.08),(0.3,0.4,0.07),(0.0,0.62,0.06)]:
        ball((x,-0.1,z),r,mat('cl',PAL['white'],emit=0.8))
    # ivy on stone
    random.seed(4)
    for i in range(24):
        s=random.choice([-1,1]); x=s*random.uniform(0.5,0.74); z=random.uniform(-1.0,0.7)
        ball((x,-0.06,z),random.uniform(0.03,0.06),mat('iv',PAL['leaf'],rough=0.8))
    sky_world(PAL['skyhi'],0.85); highkey()

def w5_conservatory():  # STARLIGHT CONSERVATORY — dusk glass + glow flowers + fireflies
    plane((0,0.14,0), 2.4, bg_plane(PAL['dusk'],PAL['dusk_dk']), rot=(math.pi/2,0,0))
    # glass mullions grid
    mul=mat('Mullion',PAL['dusk_dk'],rough=0.4,metal=0.6)
    for x in (-0.5,0,0.5): cube((x,0.02,0),(0.02,0.05,1.9),mul)
    for z in (-0.6,-0.1,0.4): cube((0,0.02,z),(1.5,0.05,0.02),mul)
    # glowing pastel flowers hanging
    random.seed(5)
    for i in range(14):
        x=random.uniform(-0.65,0.65); z=random.uniform(-0.3,0.85)
        c=random.choice([PAL['glow_pk'],PAL['glow_yl'],PAL['lav']])
        ball((x,-0.1,z),random.uniform(0.04,0.07),mat('gf',c,emit=2.2))
        point((x,-0.3,z),12,c,0.1)
    # fireflies
    for i in range(20):
        x=random.uniform(-0.7,0.7); z=random.uniform(-0.9,0.9)
        ball((x,-0.22,z),0.012,mat('ff',PAL['glow_yl'],emit=5))
    sky_world(PAL['dusk'],0.4); highkey(warm=(1,0.95,0.85), key=180, fill=90)

def w6_swan():  # SWAN LAKE TERRACE — balustrade + lake/sky + willow
    plane((0,0.14,0.35), 2.4, bg_plane(PAL['skyhi'],PAL['sky']), rot=(math.pi/2,0,0))
    # lake band
    cube((0,0.10,-0.35),(0.85,0.12,0.55), mat('Lake',PAL['water'],rough=0.12,metal=0.3))
    # pale balustrade
    bal=mat('Bal',PAL['marble'],rough=0.5)
    cube((0,-0.02,-0.78),(0.8,0.06,0.05),bal); cube((0,-0.02,-1.0),(0.8,0.06,0.05),bal)
    for x in [-0.6,-0.3,0,0.3,0.6]: cyl((x,-0.02,-0.89),0.03,0.2,bal,rot=(math.pi/2,0,0),v=12)
    # swans on the water
    for (x) in (-0.2,0.25):
        ball((x,-0.05,-0.32),0.06,mat('sw',PAL['white'],rough=0.5))
        cyl((x+0.05,-0.05,-0.24),0.015,0.12,mat('nk',PAL['white'],rough=0.5),rot=(math.radians(40),0,0),v=10)
    # willow fronds from top-left
    wl=mat('Willow',PAL['leaf'],rough=0.8)
    for i in range(10):
        x=-0.7+i*0.05; cyl((x,-0.08,0.55),0.006,random.uniform(0.4,0.7),wl,v=6)
    sky_world(PAL['skyhi'],0.85); highkey()

def w7_gallery():  # GALLERY OF DREAMS — lavender wall + gold painting + sun medallion
    plane((0,0.12,0), 2.4, mat('GW', PAL['lav'], rough=0.5), rot=(math.pi/2,0,0))
    gold=mat('Gold',PAL['goldmet'],rough=0.25,metal=1.0)
    # framed pastel painting (sunset landscape)
    cnv=bg_plane(PAL['sunset_hi'],PAL['pink'])
    plane((0,0.05,0.12),1,cnv,rot=(math.pi/2,0,0)); bpy.context.active_object.scale=(0.4,0.5,1)
    frame_rect(0,0.12,0.4,0.5,0.045,gold)
    # sun medallion above
    torus((0,0.04,0.78),0.12,0.02, gold, rot=(math.pi/2,0,0))
    ball((0,0.0,0.78),0.07,mat('sun',PAL['glow_yl'],emit=2.5))
    for i in range(12):
        a=i/12*6.28; cube((math.cos(a)*0.16,0.03,0.78+math.sin(a)*0.16),(0.015,0.03,0.05),gold,rot=(0,a,0))
    # wainscot
    cube((0,0.06,-0.82),(0.75,0.04,0.28),mat('WSC',PAL['cream'],rough=0.5))
    for x in (-0.62,0.62): cube((x,0.05,0),(0.02,0.05,1.9),gold)
    sky_world(PAL['lav'],0.6); highkey()

def w8_stage():  # SUNSET STAGE — sunset gradient + truss lights + string lights + confetti
    plane((0,0.14,0), 2.4, bg_plane(PAL['sunset_hi'],PAL['sunset']), rot=(math.pi/2,0,0))
    # sun low on horizon
    ball((0,-0.05,-0.2),0.22,mat('sun',PAL['glow_yl'],emit=3.0))
    # dark truss top
    tr=mat('Truss',srgb(60,52,70),rough=0.6,metal=0.4)
    cube((0,-0.05,0.9),(0.85,0.05,0.06),tr)
    # truss spotlights
    for x in [-0.6,-0.3,0,0.3,0.6]:
        cube((x,-0.1,0.82),(0.04,0.05,0.06),tr)
        ball((x,-0.16,0.74),0.035,mat('sl',PAL['glow_yl'],emit=3.5)); point((x,-0.4,0.7),14,(1,0.85,0.6))
    # string lights swag
    random.seed(8)
    for i in range(16):
        x=-0.7+i*0.093; z=0.55-abs(math.sin(i*0.5))*0.12
        ball((x,-0.14,z),0.02,mat('str',random.choice([PAL['glow_pk'],PAL['glow_yl'],PAL['sky']]),emit=3))
    # confetti
    for i in range(24):
        x=random.uniform(-0.72,0.72); z=random.uniform(-0.7,0.6)
        cube((x,-0.2,z),(0.02,0.004,0.03),mat('cf',random.choice([PAL['rose'],PAL['gold'],PAL['sky'],PAL['leaf']]),emit=1),rot=(0,random.uniform(0,3),0))
    # dark stage floor edge with crowd silhouette dots
    cube((0,-0.02,-0.9),(0.85,0.06,0.14),mat('crowd',srgb(50,40,60),rough=0.7))
    sky_world(PAL['sunset_hi'],0.7); highkey(warm=(1,0.85,0.6), cool=(1,0.7,0.6), key=380, fill=200)

BUILDERS=[w0_library,w1_rose,w2_blossom,w3_ballroom,w4_fountain,w5_conservatory,w6_swan,w7_gallery,w8_stage]
sel = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
idxs = [int(x) for x in sel] if sel else list(range(9))
for i in idxs:
    reset(); BUILDERS[i](); wall_cam()
    render_to(os.path.join(OUT, f'wall_{i}.png'), 288, 384, samples=128)
print('WHIMSY_WALLS_DONE')
