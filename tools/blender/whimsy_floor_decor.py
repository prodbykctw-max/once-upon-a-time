import math, random, sys, os
FW = r"C:\Users\Owner\Documents\once-upon-a-time\tools\blender\whimsy_framework.py"
exec(open(FW).read())
OUTF = r"C:\Users\Owner\Documents\once-upon-a-time\assets\renders\whimsy\floors"
OUTD = r"C:\Users\Owner\Documents\once-upon-a-time\assets\renders\whimsy\decor"

def toplight():
    area((-1.4,-1.4,3.0), 55, 4.0, (1,0.97,0.9), (math.radians(20),0,math.radians(-22)))
    area((1.4,1.2,2.6), 28, 3.6, (0.85,0.9,1.0), (math.radians(-18),0,math.radians(20)))

# ─────────── FLOORS (top-down 96x96) ───────────
def plank_floor(tone, tone2, ang=0.0):
    random.seed(3)
    base=mat('U',tone2,rough=0.5)
    plane((0,0,-0.02),2.4,base)
    for i in range(-6,7):
        for j in range(-6,7):
            t=random.uniform(-0.05,0.06)
            cube((i*0.34*0.72+ (0.17*0.72 if j%2 else 0),j*0.17,0.01),(0.16,0.083,0.02),
                 mat('pk',(min(1,tone[0]+t),min(1,tone[1]+t),min(1,tone[2]+t)),rough=0.45),rot=(0,0,ang))

def tile_floor(a,b, gold=False):
    plane((0,0,-0.02),2.4,mat('grout',(0.9,0.88,0.86),rough=0.5))
    gm=mat('g',PAL['goldmet'],rough=0.25,metal=1) if gold else None
    for i in range(-3,4):
        for j in range(-3,4):
            c=a if (i+j)%2==0 else b
            cube((i*0.32,j*0.32,0.005),(0.15,0.15,0.02),mat('tl',c,rough=0.2))
    if gold:
        for i in range(-3,4):
            for j in range(-3,4):
                cube((i*0.32+0.16,j*0.32+0.16,0.01),(0.02,0.02,0.02),gm)

def f0(): plank_floor(PAL['honey'],PAL['honey_dk'])
def f1():  # grass with flowers
    plane((0,0,0),2.4,mat('grass',PAL['leaf'],rough=0.8)); random.seed(1)
    for i in range(40):
        ball((random.uniform(-1,1),random.uniform(-1,1),0.02),0.03,mat('fl',random.choice([PAL['rose'],PAL['gold'],PAL['white']]),emit=0.4))
def f2():  # pink stone + petals
    tile_floor(PAL['blossom'],PAL['pink']); random.seed(2)
    for i in range(24): cube((random.uniform(-1,1),random.uniform(-1,1),0.02),(0.03,0.045,0.004),mat('pt',PAL['rose'],emit=0.4),rot=(0,0,random.uniform(0,3)))
def f3(): tile_floor(PAL['pink'],PAL['white'],gold=True)
def f4():  # pale radial stone
    plane((0,0,0),2.4,mat('st',PAL['marble'],rough=0.4))
    for r in range(1,5): torus((0,0,0.01),r*0.22,0.012,mat('r',PAL['honey'],rough=0.4))
def f5():  # dusk tiles with sparkle
    tile_floor(PAL['dusk'],PAL['dusk_dk']); random.seed(5)
    for i in range(30): ball((random.uniform(-1,1),random.uniform(-1,1),0.02),0.012,mat('sp',PAL['glow_yl'],emit=4))
def f6():  # stone terrace edge to water
    plane((0,0,0),2.4,mat('st',PAL['marble'],rough=0.4))
    cube((0,0.7,0.01),(2.4,0.6,0.02),mat('w',PAL['water'],rough=0.1,metal=0.3))
def f7(): plank_floor(PAL['lav'],PAL['lav_dk'])
def f8():  # warm stage boards
    plane((0,0,0),2.4,mat('b',PAL['honey_dk'],rough=0.5))
    for j in range(-6,7): cube((0,j*0.17,0.01),(2.3,0.083,0.02),mat('pk',PAL['honey'],rough=0.4))
FLOORS=[f0,f1,f2,f3,f4,f5,f6,f7,f8]

# ─────────── DECOR PROPS (144x240 transparent, stand on z=0) ───────────
def d0():  # reading lamp + book stack
    gm=mat('g',PAL['goldmet'],rough=0.3,metal=1)
    cyl((0,0,0.05),0.22,0.1,mat('base',PAL['honey_dk'],rough=0.5),v=24)
    cyl((0,0,0.7),0.03,1.3,gm,v=12)
    cone((0.0,0,1.45),0.22,0.12,0.3,mat('shade',PAL['cream'],emit=1.2),v=24)
    point((0,-0.3,1.4),22,(1,0.92,0.7))
    for i,c in enumerate([PAL['rose'],PAL['sky'],PAL['leaf']]):
        cube((0.28,0,0.13+i*0.09),(0.34,0.24,0.08),mat('bk',c,rough=0.5),rot=(0,0,0.1*i))
def d1():  # rose topiary
    cyl((0,0,0.12),0.2,0.24,mat('pot',PAL['coral'],rough=0.5),v=24)
    for lvl,(z,r) in enumerate([(0.7,0.34),(1.2,0.28),(1.6,0.2)]):
        ball((0,0,z),r,mat('t',PAL['leaf_dk'],rough=0.8))
        random.seed(lvl)
        for i in range(14):
            a=i/14*6.28; ball((math.cos(a)*r*0.9,math.sin(a)*r*0.5,z+math.sin(a*2)*r*0.4),0.05,mat('rs',random.choice([PAL['rose'],PAL['rose_dk']]),rough=0.5))
def d2():  # cherry sapling in pot
    cyl((0,0,0.14),0.22,0.28,mat('pot',PAL['pink_dk'],rough=0.5),v=24)
    cyl((0,0,0.7),0.04,0.9,mat('tr',PAL['honey_dk'],rough=0.7),v=10)
    random.seed(2)
    for i in range(40):
        a=random.uniform(0,6.28); rr=random.uniform(0,0.4)
        ball((math.cos(a)*rr,math.sin(a)*rr*0.6,1.3+random.uniform(-0.2,0.3)),0.07,mat('bl',random.choice([PAL['blossom'],PAL['pink']]),rough=0.6,sheen=0.5))
def d3():  # gilded candelabra + flowers
    gm=mat('g',PAL['goldmet'],rough=0.25,metal=1)
    cone((0,0,0.1),0.24,0.1,0.2,gm,v=24); cyl((0,0,0.8),0.035,1.3,gm,v=12)
    for s in (-1,1):
        cyl((s*0.3,0,1.35),0.02,0.6,gm,rot=(0,math.radians(35*s),0),v=8)
        ball((s*0.32,0,1.62),0.05,mat('fl',PAL['glow_yl'],emit=3)); point((s*0.32,-0.3,1.62),12,(1,0.9,0.7))
    ball((0,0,1.55),0.055,mat('fl',PAL['glow_yl'],emit=3)); point((0,-0.3,1.55),12,(1,0.9,0.7))
def d4():  # TIERED FOUNTAIN (hero)
    st=mat('st',PAL['marble'],rough=0.4); wt=mat('w',PAL['water'],rough=0.1,metal=0.3,emit=0.2)
    cyl((0,0,0.12),0.66,0.24,st,v=40); cyl((0,0,0.26),0.6,0.05,wt,v=40)
    cyl((0,0,0.5),0.12,0.5,st,v=24)
    cyl((0,0,0.8),0.4,0.16,st,v=32); cyl((0,0,0.9),0.36,0.04,wt,v=32)
    cyl((0,0,1.05),0.08,0.35,st,v=20)
    cyl((0,0,1.3),0.22,0.12,st,v=24); cyl((0,0,1.38),0.19,0.03,wt,v=24)
    ball((0,0,1.5),0.09,mat('top',PAL['glow_yl'],emit=1.5))
    # water jets
    random.seed(4)
    for i in range(20):
        a=random.uniform(0,6.28); rr=random.uniform(0.05,0.3)
        ball((math.cos(a)*rr,math.sin(a)*rr,1.4+random.uniform(-0.3,0.2)),0.02,mat('j',(0.8,0.92,1),emit=1.2,alpha=0.8))
    point((0,-0.6,1.2),30,(0.8,0.95,1))
def d5():  # glowing potted flower
    cyl((0,0,0.14),0.22,0.28,mat('pot',PAL['lav_dk'],rough=0.5),v=24)
    cyl((0,0,0.6),0.03,0.7,mat('st',PAL['leaf_dk'],rough=0.8),v=8)
    for i in range(6):
        a=i/6*6.28; ball((math.cos(a)*0.12,math.sin(a)*0.08,1.05),0.08,mat('pt',PAL['glow_pk'],emit=3))
    ball((0,0,1.08),0.06,mat('c',PAL['glow_yl'],emit=4)); point((0,-0.4,1.1),20,PAL['glow_pk'])
def d6():  # swan statue
    st=mat('m',PAL['white'],rough=0.35)
    cyl((0,0,0.12),0.34,0.24,mat('ped',PAL['marble'],rough=0.5),v=24)
    b=ball((0,0.05,0.55),0.28,st); b.scale=(0.8,1.2,0.7)
    cyl((0,-0.15,0.85),0.05,0.5,st,rot=(math.radians(30),0,0),v=12)
    b2=ball((0,-0.32,1.12),0.09,st); b2.scale=(1,1.3,1)
    cone((0,-0.42,1.1),0.04,0.005,0.12,mat('bk',PAL['gold'],rough=0.4),rot=(math.radians(80),0,0),v=8)
    for s in (-1,1):
        w=ball((s*0.22,0.05,0.6),0.2,st); w.scale=(0.4,1.0,0.9)
def d7():  # marble STATUE on pedestal (hero)
    m=mat('m',PAL['marble'],rough=0.35)
    cyl((0,0,0.14),0.3,0.28,m,v=32); cube((0,0,0.32),(0.5,0.5,0.06),m)
    # figure
    b=ball((0,0,1.5),0.16,m); b.scale=(0.85,0.8,1.0)          # head
    cyl((0,0,1.28),0.09,0.2,m,v=16)                            # neck
    sh=ball((0,0,1.05),0.3,m); sh.scale=(1.0,0.6,0.7)          # shoulders/chest
    cone((0,0,0.62),0.34,0.16,0.7,m,v=24)                      # gown skirt
    for s in (-1,1): cyl((s*0.2,0,1.0),0.06,0.5,m,rot=(0,math.radians(20*s),0),v=10)  # arms
    point((0,-0.6,1.3),18,(1,0.96,0.9))
def d8():  # mic stand + speaker
    gm=mat('g',PAL['goldmet'],rough=0.3,metal=1); dk=mat('dk',srgb(50,44,60),rough=0.5)
    cyl((0,0,0.03),0.26,0.06,dk,v=24); cyl((0,0,0.8),0.025,1.5,gm,v=12)
    ball((0,-0.05,1.6),0.09,mat('mic',srgb(40,36,50),rough=0.4))
    # speaker
    cube((0.4,0,0.4),(0.4,0.34,0.8),dk); cyl((0.4,-0.18,0.55),0.14,0.04,mat('cone',PAL['honey'],rough=0.6),rot=(math.radians(90),0,0),v=24)
    cyl((0.4,-0.18,0.25),0.09,0.04,mat('cone2',PAL['honey'],rough=0.6),rot=(math.radians(90),0,0),v=20)
    # confetti
    random.seed(8)
    for i in range(16): cube((random.uniform(-0.4,0.6),-0.3,random.uniform(0.6,2.0)),(0.03,0.004,0.04),mat('cf',random.choice([PAL['rose'],PAL['gold'],PAL['sky'],PAL['leaf']]),emit=1),rot=(0,random.uniform(0,3),0))
DECOR=[d0,d1,d2,d3,d4,d5,d6,d7,d8]

mode = sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'both'
sel = sys.argv[sys.argv.index('--')+2:] if '--' in sys.argv and len(sys.argv)>sys.argv.index('--')+2 else []
idxs = [int(x) for x in sel] if sel else list(range(9))

if mode in ('floors','both'):
    for i in idxs:
        reset(); FLOORS[i](); sky_world(PAL['skyhi'],0.7); toplight(); floor_cam()
        render_to(os.path.join(OUTF, f'floor_{i}.png'), 192,192, samples=96)
if mode in ('decor','both'):
    for i in idxs:
        reset(); DECOR[i](); sky_world((0.6,0.64,0.72),0.5); highkey(); decor_cam()
        render_to(os.path.join(OUTD, f'decor_{i}.png'), 288,480, transparent=True, samples=128)
print('WHIMSY_FD_DONE')
