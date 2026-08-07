import math, random, sys, os
FW = r"C:\Users\Owner\Documents\once-upon-a-time\tools\blender\whimsy_framework.py"
exec(open(FW).read())
OUT = r"C:\Users\Owner\Documents\once-upon-a-time\assets\renders\whimsy\corridors"

# per-stage: (sky_top, sky_bot, wall, floor, accent, prop) ; prop in {'column','hedge','tree','arch','fountainrow','glass','rail','frame','truss'}
SPECS = [
 (PAL['skyhi'], PAL['sky'],     PAL['honey'],  PAL['honey_dk'], PAL['gold'],  'frame'),   # 0 library
 (PAL['skyhi'], PAL['sky'],     PAL['leaf'],   PAL['leaf_dk'],  PAL['rose'],  'hedge'),   # 1 rose garden
 (PAL['blossom'],PAL['pink'],   PAL['pink'],   PAL['pink_dk'],  PAL['red'],   'tree'),    # 2 blossom
 (PAL['pink'],  PAL['blossom'], PAL['pink'],   PAL['white'],    PAL['gold'],  'column'),  # 3 ballroom
 (PAL['skyhi'], PAL['sky'],     PAL['marble'], PAL['marble'],   PAL['gold'],  'fountainrow'), # 4 fountain
 (PAL['dusk'],  PAL['dusk_dk'], PAL['dusk'],   PAL['dusk_dk'],  PAL['glow_pk'],'glass'),  # 5 conservatory
 (PAL['skyhi'], PAL['sky'],     PAL['marble'], PAL['water'],    PAL['white'], 'rail'),    # 6 swan lake
 (PAL['lav'],   PAL['lav_dk'],  PAL['lav'],    PAL['lav_dk'],   PAL['gold'],  'frame'),   # 7 gallery
 (PAL['sunset_hi'],PAL['sunset'],PAL['coral'], PAL['honey_dk'], PAL['glow_yl'],'truss'),  # 8 sunset stage
]

def bggrad(top, bot, loc, size):
    m = mat('Sky', top); nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc=nt.nodes.new('ShaderNodeTexCoord'); mp=nt.nodes.new('ShaderNodeMapping'); gr=nt.nodes.new('ShaderNodeTexGradient')
    mp.inputs['Rotation'].default_value=(0,math.radians(-90),0)
    nt.links.new(tc.outputs['Object'],mp.inputs['Vector']); nt.links.new(mp.outputs[0],gr.inputs['Vector'])
    rp=nt.nodes.new('ShaderNodeValToRGB'); rp.color_ramp.elements[0].color=(*bot,1); rp.color_ramp.elements[1].color=(*top,1)
    nt.links.new(gr.outputs['Fac'],rp.inputs['Fac']); nt.links.new(rp.outputs['Color'],b.inputs['Base Color'])
    b.inputs['Emission Color'].default_value=(*top,1); b.inputs['Emission Strength'].default_value=0.5
    p=plane(loc,size,m,rot=(math.pi/2,0,0)); return p

def build(i):
    sky_t,sky_b,wall,floor,acc,prop = SPECS[i]
    reset()
    wm=mat('Wall',wall,rough=0.55); fm=mat('Floor',floor,rough=0.4); am=mat('Acc',acc,rough=0.35,metal=0.3)
    gm=mat('Gold',PAL['goldmet'],rough=0.25,metal=1)
    # floor along +Y
    plane((0,18,0),52,fm)
    # sky backdrop far
    bggrad(sky_t,sky_b,(0,44,3),60)
    # side walls (unless open-air themes use low rails)
    openair = prop in ('hedge','rail','fountainrow')
    if not openair:
        for s in (-1,1):
            w=plane((s*3.2,18,2.2),52,wm,rot=(0,math.radians(90)*s,0)); w.scale=(1,1,0.085)
        plane((0,18,4.2),52,mat('Ceil',sky_t,rough=0.6),rot=(math.pi,0,0))
    # carpet/path runner
    cube((0,18,0.02),(2.2,48,0.03),am)
    random.seed(i)
    # repeating themed props down the hall
    for k in range(14):
        y=-3+k*3.4
        if prop=='column':
            for s in (-1,1):
                cyl((s*2.6,y,1.7),0.28,3.4,mat('col',PAL['white'],rough=0.4),v=20)
                cyl((s*2.6,y,3.45),0.34,0.2,gm,v=20); cyl((s*2.6,y,-0.05),0.34,0.2,gm,v=20)
        elif prop=='hedge':
            for s in (-1,1):
                cube((s*3.0,y,0.6),(0.5,1.2,1.2),mat('hg',PAL['leaf_dk'],rough=0.85))
                for r in range(5): ball((s*3.0+random.uniform(-0.3,0.3),y+random.uniform(-0.5,0.5),1.0+random.uniform(0,0.4)),0.14,mat('rs',PAL['rose'],rough=0.5))
        elif prop=='tree':
            for s in (-1,1):
                cyl((s*2.9,y,1.0),0.12,2.0,mat('tr',PAL['honey_dk'],rough=0.7),v=8)
                for r in range(10): ball((s*2.9+random.uniform(-0.6,0.6),y+random.uniform(-0.6,0.6),2.4+random.uniform(-0.3,0.4)),0.3,mat('bl',random.choice([PAL['blossom'],PAL['pink']]),rough=0.6))
        elif prop=='fountainrow':
            if k%2==0:
                for s in (-1,1):
                    cyl((s*2.4,y,0.3),0.5,0.6,mat('fst',PAL['marble'],rough=0.4),v=24)
                    ball((s*2.4,y,1.0),0.14,mat('fw',PAL['water'],rough=0.1,metal=0.3,emit=0.5))
        elif prop=='glass':
            for s in (-1,1):
                for r in range(4): ball((s*3.0,y+random.uniform(-1,1),0.5+r*0.7),0.12,mat('gf',random.choice([PAL['glow_pk'],PAL['glow_yl']]),emit=2.5))
        elif prop=='rail':
            for s in (-1,1):
                cube((s*2.6,y,0.5),(0.1,3.4,0.06),mat('rl',PAL['marble'],rough=0.4))
                for c in range(3): cyl((s*2.6,y-1.1+c*1.1,0.3),0.05,0.4,mat('rl2',PAL['marble'],rough=0.4),v=8)
            if k%3==0:
                for s in (-1,1): ball((s*2.0,y,0.15),0.18,mat('sw',PAL['white'],rough=0.5))  # swans
        elif prop=='frame':
            for s in (-1,1):
                cube((s*3.05,y,1.8),(0.04,0.9,1.1),gm)
                cube((s*3.02,y,1.8),(0.02,0.7,0.9),mat('art',random.choice([PAL['rose'],PAL['sky'],PAL['leaf'],PAL['sunset']]),rough=0.5))
        elif prop=='truss':
            cube((0,y,4.0),(6.4,0.3,0.25),mat('tr',srgb(60,52,70),rough=0.6,metal=0.4))
            for s in (-1,1): ball((s*1.5,y,3.7),0.1,mat('sl',PAL['glow_yl'],emit=3));
    # hanging lights down the center for most themes
    if prop in ('column','frame','tree'):
        for k in range(11):
            y=-2+k*3.6
            ball((0,y,3.6),0.16,mat('lamp',PAL['glow_yl'],emit=2.5)); point((0,y,3.2),120,(1,0.9,0.6),0.3)
    # far bright glow at vanishing point
    plane((0,43,2),9,mat('Far',sky_t,emit=2.2),rot=(math.pi/2,0,0))
    # lighting
    sky_world(sky_t, 0.9 if i!=5 and i!=8 else 0.5)
    area((-2.5,-2,3.5),140,4,(1,0.96,0.88),(math.radians(35),0,math.radians(-20)))
    area((2.5,2,3),90,4,(0.85,0.9,1),(math.radians(-30),0,math.radians(20)))
    cam=persp_cam((0,-6,1.5),(math.radians(90),0,0),lens=24,shift_y=0.09)
    render_to(os.path.join(OUT,f'bg_{i}.png'),960,540,transparent=False,samples=110)

sel = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
for i in ([int(x) for x in sel] if sel else range(9)): build(i)
print('WHIMSY_CORR_DONE')
