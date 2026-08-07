import bpy, bmesh, math, os
import numpy as np

# Dress the Rodin scan in her signature look: white gown with high slit,
# gold belt + hem, auburn curls down the back. Saves as jande_gown.blend.
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

# body landmarks from the mesh itself
crown_z = Z.max()
head = V[Z > crown_z - 0.16]
head_cx, head_cy = head[:, 0].mean(), head[:, 1].mean()
hip = V[(Z > -0.10) & (Z < -0.02) & (np.abs(X) < 0.25)]
hip_cy = hip[:, 1].mean() if len(hip) else 0.0
print(f'crown={crown_z:.3f} head=({head_cx:.3f},{head_cy:.3f}) hip_cy={hip_cy:.3f}')

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

white = mat('GownWhite', (0.82, 0.80, 0.76), rough=0.42, sheen=0.8)
gold = mat('GownGold', (0.78, 0.56, 0.14), rough=0.25, metal=1.0)
auburn = mat('Auburn', (0.085, 0.028, 0.012), rough=0.65, coat=0.25)
auburn2 = mat('Auburn2', (0.125, 0.045, 0.02), rough=0.6, coat=0.25)

# ── BODY-FITTED GOWN: sample the real cross-section so waist/belt sit ON her ──
def body_section(z0, dz=0.025):
    m = (Z > z0 - dz) & (Z < z0 + dz) & (np.abs(X) < 0.32) & (np.abs(Y) < 0.32)
    if not m.any(): return 0.16, 0.12, 0.0
    sx = np.abs(X[m]).max()
    yc = (Y[m].min() + Y[m].max()) / 2
    sy = (Y[m].max() - Y[m].min()) / 2
    return sx, sy, yc

# natural waist = narrowest slab between hips and ribs
cands = [(-0.04 + i * 0.01) for i in range(13)]
waist_z = min(cands, key=lambda zz: body_section(zz)[0])
wx, wy, wyc = body_section(waist_z)
print(f'waist_z={waist_z:.3f} semi=({wx:.3f},{wy:.3f}) yc={wyc:.3f}')

WAIST_Z, HEM_Z = waist_z - 0.01, -0.62
SEGS, RINGS = 48, 12
GAP_C = math.radians(55)
GAP_W = math.radians(42)
HEM_R = 0.30
verts, faces = [], []
ring_rows = []
for ri in range(RINGS + 1):
    t = ri / RINGS
    z = WAIST_Z + (HEM_Z - WAIST_Z) * t
    # hug the real body contour from waist over the hips, then flare to the hem
    bx, by, byc = body_section(max(z, -0.12))
    fit_x, fit_y = bx + 0.022, by + 0.022
    flare_t = max(0.0, (t - 0.22) / 0.78) ** 1.2
    rx = fit_x + (HEM_R - fit_x) * flare_t
    ry = fit_y + (HEM_R - fit_y) * flare_t
    yc_r = byc + 0.03 * t
    row = []
    for si in range(SEGS + 1):
        a0 = GAP_C + GAP_W / 2
        a = a0 + (2 * math.pi - GAP_W) * si / SEGS
        dx = math.sin(a)
        dy = -math.cos(a)
        train = 1 + 0.10 * t * max(0.0, dy)
        sway = 0.026 * math.sin(a * 4 + t * 5) * t * t
        row.append(len(verts))
        verts.append((dx * (rx * train + sway), dy * (ry * train + sway) + yc_r, z))
    ring_rows.append(row)
for ri in range(RINGS):
    for si in range(SEGS):
        a, b = ring_rows[ri][si], ring_rows[ri][si + 1]
        c, d = ring_rows[ri + 1][si + 1], ring_rows[ri + 1][si]
        faces.append((a, b, c, d))
gme = bpy.data.meshes.new('GownSkirt')
gme.from_pydata(verts, [], faces)
gme.update()
gown = bpy.data.objects.new('GownSkirt', gme)
sc.collection.objects.link(gown)
gown.data.materials.append(white)
# solidify so it has thickness, subsurf for softness
so = gown.modifiers.new('Sol', 'SOLIDIFY'); so.thickness = 0.012
ss = gown.modifiers.new('Sub', 'SUBSURF'); ss.levels = 2; ss.render_levels = 2
# gold hem: assign last ring of faces to gold
gme.materials.append(gold)
for p in gme.polygons:
    zs = min(gme.vertices[v].co.z for v in p.vertices)
    if zs < HEM_Z + 0.055: p.material_index = 1
gme.update()

# ── GOLD BELT: snug ellipse right at the natural waist ──
bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.018, location=(0, wyc, waist_z))
belt = bpy.context.active_object
belt.name = 'GownBelt'
belt.scale = (wx + 0.020, wy + 0.020, 1.5)
belt.data.materials.append(gold)

# ── AUBURN RINGLETS: smooth helical curve tubes down the back ──
import random
random.seed(7)

def ringlet(x0, y0, z0, length, tube_r, turns, mat_pick, seed):
    cu = bpy.data.curves.new('CurlC', 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = tube_r
    cu.bevel_resolution = 3
    cu.use_fill_caps = True
    sp = cu.splines.new('NURBS')
    N = 16
    pts = []
    for i in range(N):
        t = i / (N - 1)
        ang = t * turns * 2 * math.pi + seed * 2.3
        rr = 0.026 * (1 - 0.25 * t)
        px = x0 + math.cos(ang) * rr + math.sin(seed * 3 + t * 5) * 0.007
        py = y0 + math.sin(ang) * rr * 0.6 + 0.018 * t
        pz = z0 - length * t
        pts.append((px, py, pz, 1))
    sp.points.add(N - 1)
    for i, p4 in enumerate(pts): sp.points[i].co = p4
    sp.use_endpoint_u = True
    ob = bpy.data.objects.new('CurlObj', cu)
    sc.collection.objects.link(ob)
    ob.data.materials.append(mat_pick)
    return ob

# snug scalp volume at the crown-back
for (ox, oy, oz, r) in [(0, 0.055, -0.045, 0.095), (0, 0.075, -0.10, 0.085)]:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(head_cx + ox, head_cy + oy, crown_z - 0.06 + oz), segments=14, ring_count=10)
    s = bpy.context.active_object
    bpy.ops.object.shade_smooth()
    s.data.materials.append(auburn)
# back ringlets: two staggered rows for volume
for i in range(8):
    fx = (i / 7 - 0.5) * 0.19
    ln = 0.52 + random.uniform(-0.04, 0.10)
    ringlet(head_cx + fx, head_cy + 0.085, crown_z - 0.12, ln, 0.020 + random.uniform(0, 0.005),
            4.5 + random.uniform(-1, 1), auburn if i % 2 == 0 else auburn2, i)
for i in range(6):
    fx = (i / 5 - 0.5) * 0.15
    ln = 0.42 + random.uniform(-0.04, 0.08)
    ringlet(head_cx + fx, head_cy + 0.055, crown_z - 0.10, ln, 0.018,
            5.0 + random.uniform(-1, 1), auburn2 if i % 2 == 0 else auburn, 10 + i)
# face-framing side ringlets
for sgn in (-1, 1):
    ringlet(head_cx + sgn * 0.10, head_cy + 0.025, crown_z - 0.15, 0.30, 0.015, 5.5, auburn2, 20 + sgn)

# ── preview renders: front + back ──
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

cam.location = (0, -3.2, -0.02); cam.rotation_euler = (math.pi / 2, 0, 0)
sc.render.filepath = os.path.join(OUT, 'gown_front.png')
bpy.ops.render.render(write_still=True)
cam.location = (0, 3.2, -0.02); cam.rotation_euler = (math.pi / 2, 0, math.pi)
sc.render.filepath = os.path.join(OUT, 'gown_back.png')
bpy.ops.render.render(write_still=True)

bpy.ops.wm.save_as_mainfile(filepath=SAVE)
print('GOWN_DONE saved:', SAVE)
