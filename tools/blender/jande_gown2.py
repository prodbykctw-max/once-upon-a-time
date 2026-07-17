import bpy, math, os, random
import numpy as np
from mathutils import Vector

# Replicate the RPG wedding-dress sprite exactly (observed, not guessed):
# - floor-length ivory gown (sRGB 204,186,173) + train pooling behind
# - corset bodice fit, high slit her-left, long bell sleeves
# - white thigh-high boots visible through slit, brown garter band
# - waist-length voluminous copper curls (sRGB 126,67,38), NO hat visible
# - small gold crown ornament
SAVE = r"C:\Users\Owner\Documents\once-upon-a-time\assets\jande_gown.blend"
OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul"

obj = bpy.data.objects['JandeModel']
sc = bpy.context.scene
for nm in ('ChkCam', 'ChkSun', 'Cube', 'Light', 'Camera', 'Lat'):
    o = bpy.data.objects.get(nm)
    if o: bpy.data.objects.remove(o, do_unlink=True)

me = obj.data
n = len(me.vertices)
V = np.empty(n * 3)
me.vertices.foreach_get('co', V)
V = V.reshape(n, 3)
X, Y, Z = V[:, 0], V[:, 1], V[:, 2]
FOOT_Z = float(Z.min())
crown_z = float(Z.max())
head = V[Z > crown_z - 0.16]
head_cx, head_cy = float(head[:, 0].mean()), float(head[:, 1].mean())

def srgb_lin(r, g, b):
    def f(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (f(r), f(g), f(b))

def mat(name, tone, rough=0.6, metal=0.0, sheen=0.0, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*tone, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if sheen: b.inputs['Sheen Weight'].default_value = sheen
    if coat: b.inputs['Coat Weight'].default_value = coat
    return m

# exact sprite colors converted to linear
IVORY = srgb_lin(204, 186, 173)
IVORY_DK = srgb_lin(180, 158, 142)
COPPER = srgb_lin(126, 67, 38)
COPPER_HI = srgb_lin(158, 92, 52)
ivory = mat('Ivory', IVORY, rough=0.5, sheen=0.9)
ivory_trim = mat('IvoryTrim', IVORY_DK, rough=0.4, sheen=0.6)
boot_w = mat('BootWhite', srgb_lin(226, 218, 208), rough=0.35, coat=0.3)
copper = mat('Copper', COPPER, rough=0.62, coat=0.2)
copper_hi = mat('CopperHi', COPPER_HI, rough=0.58, coat=0.2)
gold = mat('Gold', (0.78, 0.56, 0.14), rough=0.25, metal=1.0)
garter = mat('Garter', srgb_lin(115, 68, 38), rough=0.7)

def body_section(z0, dz=0.025, xlim=0.32):
    m = (Z > z0 - dz) & (Z < z0 + dz) & (np.abs(X) < xlim) & (np.abs(Y) < 0.32)
    if not m.any(): return 0.16, 0.12, 0.0
    sx = float(np.abs(X[m]).max())
    yc = float((Y[m].min() + Y[m].max()) / 2)
    sy = float((Y[m].max() - Y[m].min()) / 2)
    return sx, sy, yc

cands = [(-0.04 + i * 0.01) for i in range(13)]
waist_z = min(cands, key=lambda zz: body_section(zz)[0])
wx, wy, wyc = body_section(waist_z)
print(f'waist_z={waist_z:.3f} semi=({wx:.3f},{wy:.3f}) foot={FOOT_Z:.3f}')

# ══ GOWN: waist -> floor, direction-dependent hem + train pool ══
WAIST_Z = waist_z - 0.005
HEM_Z = FOOT_Z + 0.015
SEGS, RINGS = 48, 16
GAP_C = math.radians(55)
GAP_W = math.radians(40)
verts, faces = [], []
ring_rows = []
for ri in range(RINGS + 1):
    t = ri / RINGS
    z = WAIST_Z + (HEM_Z - WAIST_Z) * t
    bx, by, byc = body_section(max(z, -0.12))
    fit_x, fit_y = bx + 0.022, by + 0.022
    flare_t = max(0.0, (t - 0.20) / 0.80) ** 1.25
    row = []
    for si in range(SEGS + 1):
        a0 = GAP_C + GAP_W / 2
        a = a0 + (2 * math.pi - GAP_W) * si / SEGS
        dx = math.sin(a)
        dy = -math.cos(a)
        # hem radius: slimmer at front (0.24), fuller at back (0.38) = train side
        hem_r = 0.24 + 0.14 * max(0.0, dy)
        rx = fit_x + (hem_r - fit_x) * flare_t
        ry = fit_y + (hem_r - fit_y) * flare_t
        sway = 0.022 * math.sin(a * 4 + t * 5) * t * t
        row.append(len(verts))
        verts.append((dx * (rx + sway), dy * (ry + sway) + byc + 0.02 * t, z))
    ring_rows.append(row)
# train pool: 3 extra rings spreading along the floor toward the back
pool_spread = [0.06, 0.14, 0.22]
for pi_, spread in enumerate(pool_spread):
    prev = ring_rows[-1]
    row = []
    for si in range(SEGS + 1):
        a0 = GAP_C + GAP_W / 2
        a = a0 + (2 * math.pi - GAP_W) * si / SEGS
        dx = math.sin(a)
        dy = -math.cos(a)
        backness = max(0.0, dy)
        px, py, pz = verts[ring_rows[-1 if pi_ == 0 else -1][si]][0], 0, 0  # anchor from hem ring
        hem_v = verts[ring_rows[RINGS][si]]
        grow = spread * (0.15 + 0.85 * backness)          # mostly backward
        row.append(len(verts))
        verts.append((hem_v[0] * (1 + grow * 0.22), hem_v[1] + grow * dy if dy > 0 else hem_v[1] + grow * dy * 0.25,
                      HEM_Z - 0.006 * (pi_ + 1)))
    ring_rows.append(row)
for ri in range(len(ring_rows) - 1):
    for si in range(SEGS):
        a, b = ring_rows[ri][si], ring_rows[ri][si + 1]
        c, d = ring_rows[ri + 1][si + 1], ring_rows[ri + 1][si]
        faces.append((a, b, c, d))
gme = bpy.data.meshes.new('GownSkirt')
gme.from_pydata(verts, [], faces)
gme.update()
gown = bpy.data.objects.new('GownSkirt', gme)
sc.collection.objects.link(gown)
gown.data.materials.append(ivory)
gme.materials.append(ivory_trim)
for p in gme.polygons:
    zs = min(gme.vertices[v].co.z for v in p.vertices)
    if zs < HEM_Z + 0.03: p.material_index = 1
gme.update()
so = gown.modifiers.new('Sol', 'SOLIDIFY'); so.thickness = 0.010
ss = gown.modifiers.new('Sub', 'SUBSURF'); ss.levels = 2; ss.render_levels = 2

# thin champagne waist sash (not a chunky belt — sprite shows a seam)
bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.011, location=(0, wyc, waist_z))
sash = bpy.context.active_object
sash.name = 'WaistSash'
sash.scale = (wx + 0.024, wy + 0.024, 1.2)
sash.data.materials.append(gold)

# ══ LONG BELL SLEEVES along each MEASURED arm axis ══
def arm_axis(sgn):
    b1 = (np.abs(X) > 0.26) & (np.abs(X) < 0.31) & (np.sign(X) == sgn) & (Z > 0.05) & (Z < 0.60)
    b2 = (np.abs(X) > 0.37) & (np.abs(X) < 0.47) & (np.sign(X) == sgn) & (Z > -0.15) & (Z < 0.40)
    if not (b1.any() and b2.any()): return None, None
    return Vector(V[b1].mean(axis=0)), Vector(V[b2].mean(axis=0))

for sgn in (1, -1):
    A1, A2 = arm_axis(sgn)
    if A1 is None: continue
    d = A2 - A1
    S = A1 - d * 0.55          # back toward the shoulder
    H = A2 + d * 0.30          # out past the wrist
    d = H - S
    p1 = S + d * 0.30
    p2 = S + d * 1.04
    mid = (p1 + p2) / 2
    length = (p2 - p1).length
    bpy.ops.mesh.primitive_cone_add(radius1=0.048, radius2=0.085, depth=length, location=mid, vertices=24)
    cone = bpy.context.active_object
    cone.name = f'Sleeve{"L" if sgn > 0 else "R"}'
    cone.rotation_mode = 'QUATERNION'
    cone.rotation_quaternion = d.to_track_quat('Z', 'Y')   # +Z (radius2 bell end) points to the hand
    bpy.ops.object.shade_smooth()
    cone.data.materials.append(ivory)

# ══ THIGH-HIGH BOOTS: one smooth tapered cone per leg, ankle -> mid-thigh ══
def leg_slab(z0, sgn, dz=0.04):
    m2 = (Z > z0 - dz) & (Z < z0 + dz) & (np.sign(X) == sgn) & (np.abs(X) > 0.02) & (np.abs(X) < 0.3)
    if not m2.any(): return None
    cx = float(X[m2].mean()); cy = float(Y[m2].mean())
    rr = float(np.sqrt((X[m2] - cx) ** 2 + (Y[m2] - cy) ** 2).max())
    return cx, cy, rr

for sgn in (1, -1):
    ank = leg_slab(FOOT_Z + 0.10, sgn)
    thi = leg_slab(-0.33, sgn)
    if not (ank and thi): continue
    p1 = Vector((ank[0], ank[1], FOOT_Z + 0.08))
    p2 = Vector((thi[0], thi[1], -0.31))
    d2 = p2 - p1
    bpy.ops.mesh.primitive_cone_add(radius1=ank[2] + 0.009, radius2=thi[2] + 0.009,
                                    depth=d2.length, location=(p1 + p2) / 2, vertices=24)
    bc = bpy.context.active_object
    bc.name = f'Boot{"L" if sgn > 0 else "R"}'
    bc.rotation_mode = 'QUATERNION'
    bc.rotation_quaternion = d2.to_track_quat('Z', 'Y')
    bpy.ops.object.shade_smooth()
    bc.data.materials.append(boot_w)
    # gold boot cuff at the top edge
    bpy.ops.mesh.primitive_cylinder_add(radius=thi[2] + 0.012, depth=0.028, location=(thi[0], thi[1], -0.315), vertices=24)
    cf = bpy.context.active_object
    cf.data.materials.append(gold)
    # foot cover: heeled boot toe
    mf = (Z < FOOT_Z + 0.09) & (np.sign(X) == sgn) & (np.abs(X) > 0.02)
    if mf.any():
        fx = float(X[mf].mean())
        toe = float(Y[mf].min()) - 0.014
        heel = float(Y[mf].max()) + 0.010
        fcy = (toe + heel) / 2
        half_len = (heel - toe) / 2
        half_wid = float(np.abs(X[mf] - fx).max()) + 0.012
        bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(fx, fcy, FOOT_Z + 0.045), segments=18, ring_count=12)
        f = bpy.context.active_object
        f.scale = (half_wid, half_len, 0.075)
        bpy.ops.object.shade_smooth()
        f.data.materials.append(boot_w)
        # flat sole box: constant cross-section at ground level hides the sneaker sole
        bpy.ops.mesh.primitive_cube_add(size=1, location=(fx, fcy, FOOT_Z + 0.012))
        sole = bpy.context.active_object
        sole.scale = (half_wid * 2, half_len * 2, 0.032)
        sole.data.materials.append(boot_w)
# garter band on the slit leg (her left, +x), upper thigh
mg = (Z > -0.32) & (Z < -0.27) & (X > 0.02) & (X < 0.3)
if mg.any():
    gx = float(X[mg].mean()); gy = float(Y[mg].mean())
    gr = float(np.sqrt((X[mg] - gx) ** 2 + (Y[mg] - gy) ** 2).max()) + 0.006
    bpy.ops.mesh.primitive_cylinder_add(radius=gr, depth=0.035, location=(gx, gy, -0.295), vertices=18)
    g2 = bpy.context.active_object
    g2.name = 'GarterBand'
    g2.data.materials.append(garter)

# ══ WAIST-LENGTH COPPER CURLS covering the whole head (hat fully hidden) ══
random.seed(11)
skull_c = Vector((head_cx, head_cy, crown_z - 0.105))

def ringlet(x0, y0, z0, length, tube_r, turns, mat_pick, seed):
    cu = bpy.data.curves.new('CurlC', 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = tube_r
    cu.bevel_resolution = 3
    cu.use_fill_caps = True
    sp = cu.splines.new('NURBS')
    N = 18
    pts = []
    for i in range(N):
        t = i / (N - 1)
        ang = t * turns * 2 * math.pi + seed * 2.3
        rr = 0.030 * (1 - 0.2 * t)
        px = x0 + math.cos(ang) * rr + math.sin(seed * 3 + t * 5) * 0.008
        py = y0 + math.sin(ang) * rr * 0.6 + 0.02 * t
        pz = z0 - length * t
        pts.append((px, py, pz, 1))
    sp.points.add(N - 1)
    for i, p4 in enumerate(pts): sp.points[i].co = p4
    sp.use_endpoint_u = True
    ob = bpy.data.objects.new('CurlObj', cu)
    sc.collection.objects.link(ob)
    ob.data.materials.append(mat_pick)
    return ob

# waist-length back mass: long ringlets to z ~ -0.05
back_len = (crown_z - 0.10) - (-0.05)
for i in range(10):
    fx = (i / 9 - 0.5) * 0.21
    ln = back_len * random.uniform(0.88, 1.0)
    ringlet(head_cx + fx * 0.78, head_cy + 0.058, crown_z - 0.15, ln,
            0.024 + random.uniform(0, 0.006), 6 + random.uniform(-1, 1.5),
            copper if i % 2 == 0 else copper_hi, i)
for i in range(7):
    fx = (i / 6 - 0.5) * 0.16
    ln = back_len * random.uniform(0.55, 0.75)
    ringlet(head_cx + fx * 0.8, head_cy + 0.04, crown_z - 0.155, ln,
            0.021, 5 + random.uniform(-1, 1), copper_hi if i % 2 == 0 else copper, 10 + i)
# chest-length side curls framing the face
for sgn in (-1, 1):
    ringlet(head_cx + sgn * 0.105, head_cy + 0.01, crown_z - 0.14, 0.52, 0.018, 6.5, copper, 20 + sgn)
    ringlet(head_cx + sgn * 0.078, head_cy + 0.04, crown_z - 0.15, 0.58, 0.016, 6.0, copper_hi, 24 + sgn)

# ══ previews: side (sprite's angle), front, back ══
sc.render.engine = 'CYCLES'
sc.cycles.samples = 96
sc.cycles.use_denoising = True
sc.view_settings.view_transform = 'Filmic'
sc.render.film_transparent = True
sc.render.resolution_x = 480
sc.render.resolution_y = 640
sc.render.image_settings.file_format = 'PNG'
cam_data = bpy.data.cameras.new('PrevCam')
cam_data.type = 'ORTHO'
cam_data.ortho_scale = 2.3
cam = bpy.data.objects.new('PrevCam', cam_data)
sc.collection.objects.link(cam)
sc.camera = cam
def area(loc, e, size, col, rot):
    ld = bpy.data.lights.new('L', 'AREA'); ld.energy = e; ld.size = size; ld.color = col
    lo = bpy.data.objects.new('L', ld); sc.collection.objects.link(lo)
    lo.location = loc; lo.rotation_euler = rot
area((-1.8, -2.6, 1.6), 260, 2.6, (1, 0.93, 0.83), (math.radians(55), 0, math.radians(-35)))
area((2.0, -2.2, 0.6), 90, 2.2, (0.65, 0.72, 0.95), (math.radians(65), 0, math.radians(40)))
area((0, 2.8, 1.2), 160, 2.4, (1, 0.9, 0.8), (math.radians(-70), 0, 0))
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.3
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.5, 0.5, 0.6, 1)

cam.location = (3.2, 0, -0.02); cam.rotation_euler = (math.pi / 2, 0, math.pi / 2)
sc.render.filepath = os.path.join(OUT, 'gown2_side.png')
bpy.ops.render.render(write_still=True)
cam.location = (0, -3.2, -0.02); cam.rotation_euler = (math.pi / 2, 0, 0)
sc.render.filepath = os.path.join(OUT, 'gown2_front.png')
bpy.ops.render.render(write_still=True)
cam.location = (0, 3.2, -0.02); cam.rotation_euler = (math.pi / 2, 0, math.pi)
sc.render.filepath = os.path.join(OUT, 'gown2_back.png')
bpy.ops.render.render(write_still=True)

bpy.ops.wm.save_as_mainfile(filepath=SAVE)
print('GOWN2_DONE saved:', SAVE)
