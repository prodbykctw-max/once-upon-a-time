import bpy, math, os, sys
FRAMEWORK = r"C:\Users\Owner\Documents\once-upon-a-time\tools\blender\framework.py"
exec(open(FRAMEWORK).read())
ROOT = r"C:\Users\Owner\Documents\once-upon-a-time"
PBR = os.path.join(ROOT, 'assets', 'pbr')
OUT = os.path.join(ROOT, 'assets', 'renders', 'ground')
os.makedirs(OUT, exist_ok=True)

# Re-bake the nine stage grounds from real CC0 scans (Poly Haven) instead of
# procedural noise. Rendered flat-lit and top-down so the tile carries only
# surface detail — the GL world supplies the stage lighting and fog, and its
# shader mirror-tiles these, so no seam work is needed here.
#
# tone: multiplied over the albedo to keep each stage on its established
# palette (the whimsy day-cycle) without losing photographic detail.
SPECS = [
    ('library',   (1.00, 0.92, 0.80), 1.0),
    ('meadow',    (0.92, 1.06, 0.80), 1.6),
    ('blossom',   (1.02, 0.98, 0.94), 1.4),
    ('rose',      (0.88, 1.04, 0.78), 1.6),
    ('lake',      (1.02, 1.00, 0.95), 1.5),
    ('glade',     (0.80, 1.00, 0.82), 1.5),
    ('sunflower', (1.06, 0.98, 0.74), 1.5),
    ('clouds',    (1.00, 1.00, 1.02), 1.0),
    ('sunset',    (1.04, 0.94, 0.88), 1.3),
]


def load(short, tag):
    """Return an image datablock for a PBR map, or None if absent."""
    for ext in ('jpg', 'png'):
        p = os.path.join(PBR, short, f'{tag}.{ext}')
        if os.path.exists(p):
            return bpy.data.images.load(p)
    return None


def pbr_mat(short, tone, scale):
    m = bpy.data.materials.new(f'PBR_{short}')
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes['Principled BSDF']

    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (scale, scale, scale)
    nt.links.new(tc.outputs['UV'], mp.inputs['Vector'])

    def tex(tag, non_color=True):
        img = load(short, tag)
        if not img:
            return None
        n = nt.nodes.new('ShaderNodeTexImage')
        n.image = img
        if non_color:
            n.image.colorspace_settings.name = 'Non-Color'
        nt.links.new(mp.outputs['Vector'], n.inputs['Vector'])
        return n

    d = tex('diff', non_color=False)
    if d:
        # keep the scan's detail but pull it onto this stage's palette
        mix = nt.nodes.new('ShaderNodeMixRGB')
        mix.blend_type = 'MULTIPLY'
        mix.inputs['Fac'].default_value = 1.0
        mix.inputs['Color2'].default_value = (*tone, 1)
        nt.links.new(d.outputs['Color'], mix.inputs['Color1'])
        nt.links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])

    r = tex('rough')
    if r:
        nt.links.new(r.outputs['Color'], bsdf.inputs['Roughness'])
    else:
        bsdf.inputs['Roughness'].default_value = 0.85

    n = tex('nor')
    if n:
        nm = nt.nodes.new('ShaderNodeNormalMap')
        nm.inputs['Strength'].default_value = 1.0
        nt.links.new(n.outputs['Color'], nm.inputs['Color'])
        nt.links.new(nm.outputs['Normal'], bsdf.inputs['Normal'])

    # real displacement gives the tile self-shadowing relief rather than a
    # flat photo — this is what sells it at grazing camera angles in-game
    ds = tex('disp')
    if ds:
        dn = nt.nodes.new('ShaderNodeDisplacement')
        dn.inputs['Scale'].default_value = 0.035
        dn.inputs['Midlevel'].default_value = 0.5
        nt.links.new(ds.outputs['Color'], dn.inputs['Height'])
        nt.links.new(dn.outputs['Displacement'], nt.nodes['Material Output'].inputs['Displacement'])
        # moved off .cycles in Blender 4.x
        try:
            m.displacement_method = 'BOTH'
        except Exception:
            try:
                m.cycles.displacement_method = 'BOTH'
            except Exception:
                pass
    return m


only = None
for a in sys.argv:
    if a.startswith('--only='):
        only = a.split('=', 1)[1]

for i, (short, tone, scale) in enumerate(SPECS):
    if only and only != short:
        continue
    sc = reset_scene()
    pl = plane((0, 0, 0), 2.2, pbr_mat(short, tone, scale))
    # subdivide so displacement has geometry to push. MUST be SIMPLE —
    # Catmull-Clark rounds a flat quad into a disc.
    sub = pl.modifiers.new('Sub', 'SUBSURF')
    sub.subdivision_type = 'SIMPLE'
    sub.levels = 0
    sub.render_levels = 6
    # Exposure calibration: a lambertian surface renders at roughly
    # albedo * (P/(4*pi*d^2)/pi + world). At 460W/0.55 that came to ~1.9x and
    # blew the scans out to cream. 210W at 2.6m + 0.32 world lands near 1.0,
    # so the tile keeps the scan's true albedo. Slight off-axis offset lets the
    # normal/displacement relief shade itself without casting a gradient
    # across the tile — the GL world still supplies the real stage lighting.
    area_light((-0.9, -0.8, 2.6), 210, 3.2, (1, 0.99, 0.97),
               (math.radians(22), 0, math.radians(-48)))
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.32
    ortho_cam((0, 0, 3), (0, 0, 0), 2.0)
    sc.view_settings.view_transform = 'Standard'   # no Filmic: this is a texture
    render_to(os.path.join(OUT, f'g{i}_{short}.png'), 512, 512, samples=128)
    print(f'GPBR_{i}_{short}_DONE')
print('GROUND_PBR_DONE')
