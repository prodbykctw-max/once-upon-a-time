import bpy, math, os
FRAMEWORK = r"C:\Users\Owner\Documents\once-upon-a-time\tools\blender\framework.py"
exec(open(FRAMEWORK).read())
OUT = r"C:\Users\Owner\Documents\once-upon-a-time\assets\renders\ground"
os.makedirs(OUT, exist_ok=True)

# 9 ground textures for the GL terrain, one per stage. Rendered 512x512
# top-down; the GL shader uses mirrored tiling so seams never show.
SPECS = [
    ('library',  'wood',   (0.36, 0.23, 0.11)),
    ('meadow',   'grass',  (0.30, 0.52, 0.20)),
    ('blossom',  'petals', (0.42, 0.56, 0.30)),
    ('rose',     'lawn',   (0.24, 0.46, 0.18)),
    ('lake',     'sand',   (0.66, 0.58, 0.42)),
    ('glade',    'moss',   (0.16, 0.34, 0.16)),
    ('sunflower','field',  (0.45, 0.50, 0.20)),
    ('clouds',   'marble', (0.78, 0.79, 0.84)),
    ('sunset',   'stone',  (0.62, 0.48, 0.42)),
]

def build(i, name, kind, tone):
    sc = reset_scene()
    if kind == 'wood':
        m = wood_mat('G', tone, grain_scale=14, rough=0.4)
    elif kind == 'marble':
        m = marble_mat('G', tone, (tone[0]*0.75, tone[1]*0.75, tone[2]*0.8), rough=0.25)
    elif kind == 'sand':
        m = stone_mat('G', tone, rough=0.85, scale=26, bump=0.15)
    elif kind == 'stone':
        m = marble_mat('G', tone, (tone[0]*0.7, tone[1]*0.66, tone[2]*0.66), rough=0.5)
    else:  # grass / petals / lawn / moss / field
        m = stone_mat('G', tone, rough=0.92, scale=34, bump=0.3)
    plane((0, 0, 0), 2.2, m)
    # scatter accents: petals on blossom, flowers on meadow, glow dots on glade
    import random
    random.seed(i * 13 + 5)
    if kind == 'petals':
        pm = fabric_mat('P', (0.97, 0.74, 0.82), rough=0.85)
        for k in range(50):
            p = sphere((random.uniform(-1, 1), random.uniform(-1, 1), 0.004), 0.02, pm)
            p.scale = (1, 0.55, 0.12)
            p.rotation_euler = (0, 0, random.uniform(0, 3.14))
    elif kind == 'grass':
        for k in range(24):
            col = random.choice([(0.9, 0.5, 0.6), (0.95, 0.85, 0.3), (0.85, 0.85, 0.9)])
            f = sphere((random.uniform(-1, 1), random.uniform(-1, 1), 0.004), 0.014, emissive_mat(f'F{k}', col, 0.8))
            f.scale = (1, 1, 0.2)
    elif kind == 'moss':
        for k in range(16):
            f = sphere((random.uniform(-1, 1), random.uniform(-1, 1), 0.004), 0.012, emissive_mat(f'M{k}', (0.7, 0.95, 0.6), 2.0))
            f.scale = (1, 1, 0.2)
    elif kind == 'field':
        pm2 = fabric_mat('St', (0.55, 0.42, 0.15), rough=0.9)
        for k in range(30):
            s2 = sphere((random.uniform(-1, 1), random.uniform(-1, 1), 0.003), 0.015, pm2)
            s2.scale = (1, 0.35, 0.1)
            s2.rotation_euler = (0, 0, random.uniform(0, 3.14))
    # flat even light (texture must be shadeless-ish; GL adds its own light)
    area_light((0, 0, 3), 480, 4.0, (1, 1, 1), (0, 0, 0))
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.5
    ortho_cam((0, 0, 3), (0, 0, 0), 2.0)
    render_to(os.path.join(OUT, f'g{i}_{name}.png'), 512, 512, samples=96)
    print(f'GROUND_{i}_DONE')

for i, (name, kind, tone) in enumerate(SPECS):
    build(i, name, kind, tone)
print('GROUND_TILES_DONE')
