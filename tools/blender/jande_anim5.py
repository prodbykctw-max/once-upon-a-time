import bpy, math, os, sys
import numpy as np

# v5: dressed FUSED model (jande_gown.blend). Continuous mesh = real smooth
# skinning. Costume joined with per-group motion rules:
#   body: two-segment legs + pumping arms + twist/lean (smooth weights)
#   hair: rides the head + counter-sway lag        skirt: pendulum + ripple
#   sleeves: follow arms                            boots: follow legs
OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\jande_frames"
TEST_ONLY = '--test' in sys.argv

sc = bpy.context.scene
base = bpy.data.objects['JandeModel']
for nm in ('ChkCam', 'ChkSun', 'Cube', 'Light', 'Camera', 'Lat', 'PrevCam'):
    o = bpy.data.objects.get(nm)
    if o: bpy.data.objects.remove(o, do_unlink=True)

# ── 1. curves -> mesh, join all costume, record per-vertex group ──
for o in list(bpy.data.objects):
    if o.type == 'CURVE':
        bpy.ops.object.select_all(action='DESELECT')
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.convert(target='MESH')

def centroid(o):
    vs = np.empty(len(o.data.vertices) * 3)
    o.data.vertices.foreach_get('co', vs)
    return vs.reshape(-1, 3).mean(axis=0)

GRP_BODY, GRP_HAIR, GRP_ARML, GRP_ARMR, GRP_LEGL, GRP_LEGR, GRP_SKIRT = range(7)
costume = []
for o in list(bpy.data.objects):
    if o.type != 'MESH' or o is base: continue
    c = centroid(o)
    nm = o.name.split('.')[0]
    if nm in ('GownSkirt', 'WaistSash'): g = GRP_SKIRT
    elif nm.startswith('Sleeve'): g = GRP_ARML if c[0] > 0 else GRP_ARMR
    elif nm.startswith('Boot') or nm == 'GarterBand': g = GRP_LEGL if c[0] > 0 else GRP_LEGR
    elif c[2] > 0.55: g = GRP_HAIR
    elif c[2] < -0.2: g = GRP_LEGL if c[0] > 0 else GRP_LEGR
    elif abs(c[0]) > 0.18: g = GRP_ARML if c[0] > 0 else GRP_ARMR
    else: g = GRP_SKIRT
    costume.append((o, g))

grp_list = [np.zeros(len(base.data.vertices), dtype=np.int32)]
for o, g in costume:
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    for md in list(o.modifiers):
        try: bpy.ops.object.modifier_apply(modifier=md.name)
        except Exception: o.modifiers.remove(md)
    grp_list.append(np.full(len(o.data.vertices), g, dtype=np.int32))
    bpy.ops.object.select_all(action='DESELECT')
    base.select_set(True)
    o.select_set(True)
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.join()
grp = np.concatenate(grp_list)
me = base.data
n = len(me.vertices)
assert len(grp) == n, f'group map {len(grp)} != verts {n}'
print(f'joined: {n} verts, costume parts: {len(costume)}')

# ── 2. rest coords + weights ──
REST = np.empty(n * 3)
me.vertices.foreach_get('co', REST)
REST = REST.reshape(n, 3).copy()
X, Y, Z = REST[:, 0], REST[:, 1], REST[:, 2]

FOOT_Z = float(Z[(grp == GRP_BODY) | (grp == GRP_LEGL) | (grp == GRP_LEGR)].min())
HIP_Z, KNEE_Z, SHOULDER_Z, SHOULDER_X = -0.08, -0.50, 0.55, 0.22
WAIST_Z = 0.03

def smooth(a):
    a = np.clip(a, 0, 1)
    return a * a * (3 - 2 * a)

body = grp == GRP_BODY
leg_w = smooth((HIP_Z - Z) / 0.12) * body
shin_w = smooth((KNEE_Z + 0.02 - Z) / 0.10) * body
left_side = smooth((X - 0.01) / 0.05)
right_side = 1.0 - left_side
up_w = smooth((Z - HIP_Z) / 0.25) * ((grp == GRP_BODY) | (grp == GRP_HAIR) | (grp == GRP_ARML) | (grp == GRP_ARMR))

def arm_axis(sgn):
    b1 = (np.abs(X) > 0.26) & (np.abs(X) < 0.31) & (np.sign(X) == sgn) & (Z > 0.05) & (Z < 0.60) & body
    b2 = (np.abs(X) > 0.37) & (np.abs(X) < 0.47) & (np.sign(X) == sgn) & (Z > -0.15) & (Z < 0.40) & body
    return REST[b1].mean(axis=0), REST[b2].mean(axis=0)
a1L, a2L = arm_axis(1)
a1R, a2R = arm_axis(-1)

def arm_param(S, A2):
    dd = A2 - S
    Lm2 = float(np.dot(dd, dd))
    t = ((REST - S) @ dd) / Lm2
    C = S[None, :] + t[:, None] * dd[None, :]
    r = np.linalg.norm(REST - C, axis=1)
    return t, r

SL = a1L - (a2L - a1L) * 0.55
SR = a1R - (a2R - a1R) * 0.55
tL, rL = arm_param(SL, a2L + (a2L - a1L) * 0.30)
tR, rR = arm_param(SR, a2R + (a2R - a1R) * 0.30)
capL = 0.085 + 0.055 * smooth((tL - 0.72) / 0.22)
armL_w = np.maximum(smooth((capL - rL) / 0.03) * body * left_side, (grp == GRP_ARML) * 1.0)
capR = 0.085 + 0.055 * smooth((tR - 0.72) / 0.22)
armR_w = np.maximum(smooth((capR - rR) / 0.03) * body * right_side, (grp == GRP_ARMR) * 1.0)
t_arm = np.where(X > 0, tL, tR)
fore_w = smooth((t_arm - 0.48) / 0.10)

legL_extra = (grp == GRP_LEGL) * 1.0
legR_extra = (grp == GRP_LEGR) * 1.0
shin_all = smooth((KNEE_Z + 0.02 - Z) / 0.10)
leg_wL = np.maximum(leg_w * left_side, legL_extra)
leg_wR = np.maximum(leg_w * right_side, legR_extra)
shin_wL = np.maximum(shin_w * left_side, legL_extra * shin_all)
shin_wR = np.maximum(shin_w * right_side, legR_extra * shin_all)

hair_all = (grp == GRP_HAIR) * 1.0
hair = hair_all * smooth((0.76 - Z) / 0.10)
skirt = (grp == GRP_SKIRT) * 1.0
skirt_flex = skirt * smooth((WAIST_Z - Z) / 0.55)
hem_w = skirt * smooth((-0.45 - Z) / 0.3)
# front/back panel masks (rest-space): the gown scissors open with the stride
front_panel = skirt_flex * smooth((0.00 - Y) / 0.28)
back_panel = skirt_flex * smooth((Y - 0.04) / 0.28)

def rotx_at(P, wgt, py, pz, ang):
    if abs(ang) < 1e-6: return
    c, s = math.cos(ang), math.sin(ang)
    y = P[:, 1] - py; z = P[:, 2] - pz
    ny = y * c - z * s
    nz = y * s + z * c
    P[:, 1] += (ny - y) * wgt
    P[:, 2] += (nz - z) * wgt

def roty_at(P, wgt, px, pz, ang):
    if abs(ang) < 1e-6: return
    c, s = math.cos(ang), math.sin(ang)
    x = P[:, 0] - px; z = P[:, 2] - pz
    nx = x * c + z * s
    nz = -x * s + z * c
    P[:, 0] += (nx - x) * wgt
    P[:, 2] += (nz - z) * wgt

def twist(P, wgt, ang):
    if abs(ang) < 1e-6: return
    c, s = math.cos(ang), math.sin(ang)
    x = P[:, 0]; y = P[:, 1]
    nx = x * c - y * s
    ny = x * s + y * c
    P[:, 0] += (nx - x) * wgt
    P[:, 1] += (ny - y) * wgt

RUNNER = REST.copy()

# ── skirt<->leg collision: push fabric outside the legs every frame ──
skirt_idx = np.where(skirt > 0.5)[0]
legcol_idx = np.where((((grp == GRP_LEGL) | (grp == GRP_LEGR)) | ((leg_w > 0.3) & body)) & (Z < 0.02))[0]
ZBN, ABN = 26, 28
COL_Z_LO = float(REST[skirt_idx, 2].min()) - 0.02
COL_Z_HI = 0.04
def _zb(zv):
    return np.clip(((zv - COL_Z_LO) / (COL_Z_HI - COL_Z_LO) * ZBN).astype(np.int32), 0, ZBN - 1)
def _ab(xv, yv):
    return np.clip(((np.arctan2(xv, -yv) + math.pi) / (2 * math.pi) * ABN).astype(np.int32), 0, ABN - 1)

def skirt_collide(P):
    lp = P[legcol_idx]
    zb = _zb(lp[:, 2]); ab = _ab(lp[:, 0], lp[:, 1])
    lr = np.sqrt(lp[:, 0] ** 2 + lp[:, 1] ** 2)
    grid = np.zeros((ZBN, ABN), dtype=np.float32)
    np.maximum.at(grid, (zb, ab), lr)
    # dilate so fabric drapes over bin gaps
    g2 = grid.copy()
    for sh in (-1, 1):
        g2 = np.maximum(g2, np.roll(grid, sh, axis=1))
        g2 = np.maximum(g2, np.roll(grid, sh, axis=0))

    sp = P[skirt_idx]
    # bilinear sample the grid at continuous coords (no terracing)
    zf = np.clip((sp[:, 2] - COL_Z_LO) / (COL_Z_HI - COL_Z_LO) * ZBN - 0.5, 0, ZBN - 1.001)
    af = ((np.arctan2(sp[:, 0], -sp[:, 1]) + math.pi) / (2 * math.pi) * ABN - 0.5) % ABN
    z0 = zf.astype(np.int32); z1 = np.minimum(z0 + 1, ZBN - 1); tz = zf - z0
    a0 = af.astype(np.int32) % ABN; a1 = (a0 + 1) % ABN; ta = af - a0.astype(np.float32)
    need = (g2[z0, a0] * (1 - tz) * (1 - ta) + g2[z1, a0] * tz * (1 - ta)
            + g2[z0, a1] * (1 - tz) * ta + g2[z1, a1] * tz * ta)
    sr = np.sqrt(sp[:, 0] ** 2 + sp[:, 1] ** 2) + 1e-9
    # depth-dependent tenting: 30% at the thigh, up to ~58% at the hem
    # (a floor gown legitimately kicks wide with the stride)
    scale = np.clip((need + 0.012) / sr, 1.0, 1.18)
    wpush = np.clip((-0.04 - sp[:, 2]) / 0.08, 0, 1)
    factor = 1.0 + (scale - 1.0) * wpush
    sp[:, 0] *= factor
    sp[:, 1] *= factor
    P[skirt_idx] = sp

def leg_pose(P, lw, sw, thigh_ang, knee_ang):
    rotx_at(P, lw, 0.0, HIP_Z, thigh_ang)
    kz_rel = KNEE_Z - HIP_Z
    ky = -kz_rel * math.sin(thigh_ang)
    kz = HIP_Z + kz_rel * math.cos(thigh_ang)
    rotx_at(P, sw, ky, kz, knee_ang)

def ground(P):
    feet = P[:, 2][(leg_wL > 0.5) | (leg_wR > 0.5)]
    if len(feet): P[:, 2] += FOOT_Z - feet.min()

def apply(P):
    me.vertices.foreach_set('co', P.reshape(-1))
    me.update()

def pose_run(t):
    ph = t * 2 * math.pi
    P = RUNNER.copy()
    swing = math.sin(ph)
    kneeL = math.radians(15 + 62 * max(0.0, -swing))
    kneeR = math.radians(15 + 62 * max(0.0, swing))
    leg_pose(P, leg_wL, shin_wL, -swing * math.radians(30), kneeL)
    leg_pose(P, leg_wR, shin_wR, swing * math.radians(30), kneeR)
    rotx_at(P, armL_w, 0.0, SHOULDER_Z, swing * math.radians(24))
    rotx_at(P, armR_w, 0.0, SHOULDER_Z, -swing * math.radians(24))
    twist(P, up_w, swing * math.radians(6))
    rotx_at(P, hair, 0.0, 0.60, -swing * math.radians(5))
    P[:, 2] -= hair * 0.008 * abs(math.sin(ph))
    # gown scissors with the stride: front panel swings up with the lead knee,
    # train kicks back with the trailing heel
    stride_a = math.radians(30) * abs(swing)
    rotx_at(P, front_panel, 0.0, WAIST_Z, -stride_a * 0.60)
    rotx_at(P, back_panel, 0.0, WAIST_Z, stride_a * 0.50)
    rotx_at(P, skirt_flex, 0.0, WAIST_Z, swing * math.radians(5))
    P[:, 1] += hem_w * 0.10
    P[:, 0] += hem_w * 0.012 * np.sin(ph * 2 + Z * 5)
    skirt_collide(P)
    P[:, 1] += (Z - FOOT_Z) * 0.055
    ground(P)
    apply(P)

def pose_jump(t):
    P = RUNNER.copy()
    if t < 0.18:
        k = t / 0.18; sq = 1 - 0.14 * k; tuck = 0.0; armup = -k * 0.4
    elif t < 0.4:
        k = (t - 0.18) / 0.22; sq = 0.86 + 0.22 * k; tuck = 0.3 * k; armup = k
    elif t < 0.65:
        sq = 1.05; tuck = 1.0; armup = 1.0
    elif t < 0.85:
        k = (t - 0.65) / 0.2; sq = 1.03 - 0.06 * k; tuck = 1 - k; armup = 1 - k * 0.7
    else:
        k = (t - 0.85) / 0.15; sq = 0.9 + 0.08 * k; tuck = 0.0; armup = -0.3 * (1 - k)
    P[:, 2] = FOOT_Z + (P[:, 2] - FOOT_Z) * sq
    leg_pose(P, leg_wL, shin_wL, -tuck * math.radians(52), math.radians(15 + 75 * tuck))
    leg_pose(P, leg_wR, shin_wR, -tuck * math.radians(48), math.radians(15 + 78 * tuck))
    rotx_at(P, armL_w, 0.0, SHOULDER_Z * sq, -armup * math.radians(45))
    rotx_at(P, armR_w, 0.0, SHOULDER_Z * sq, -armup * math.radians(45))
    flare = 1.0 + 0.16 * tuck
    P[:, 0] += (P[:, 0] * (flare - 1)) * hem_w
    P[:, 1] += ((P[:, 1] - 0.05) * (flare - 1)) * hem_w
    P[:, 2] += hair_all * 0.02 * tuck
    skirt_collide(P)
    P[:, 1] += (P[:, 2] - FOOT_Z) * 0.04 * (1 + tuck)
    apply(P)

def pose_slide(t):
    P = RUNNER.copy()
    wob = math.sin(t * 4 * math.pi) * 0.02
    sq = 0.6 + wob
    P[:, 2] = FOOT_Z + (P[:, 2] - FOOT_Z) * sq
    leg_pose(P, leg_wL, shin_wL, math.radians(-32), math.radians(30))
    leg_pose(P, leg_wR, shin_wR, math.radians(-28), math.radians(26))
    P[:, 1] += (P[:, 2] - FOOT_Z) * 0.22
    rotx_at(P, armL_w, 0.0, SHOULDER_Z * sq, math.radians(28))
    rotx_at(P, armR_w, 0.0, SHOULDER_Z * sq, math.radians(28))
    P[:, 1] += hem_w * 0.10
    rotx_at(P, hair, 0.0, 0.60 * sq, math.radians(-10))
    skirt_collide(P)
    apply(P)

# ── 3. render setup ──
sc.render.engine = 'CYCLES'
sc.cycles.samples = 64
sc.cycles.use_denoising = True
sc.view_settings.view_transform = 'Filmic'
sc.render.film_transparent = True
sc.render.resolution_x = 512
sc.render.resolution_y = 512
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_mode = 'RGBA'
cam_data = bpy.data.cameras.new('AnimCam')
cam_data.type = 'ORTHO'
cam_data.ortho_scale = 2.2
cam = bpy.data.objects.new('AnimCam', cam_data)
sc.collection.objects.link(cam)
cam.location = (0, 3.2, -0.02)
cam.rotation_euler = (math.pi / 2, 0, math.pi)
sc.camera = cam
def area(loc, e, size, col, rot):
    ld = bpy.data.lights.new('L', 'AREA'); ld.energy = e; ld.size = size; ld.color = col
    lo = bpy.data.objects.new('L', ld); sc.collection.objects.link(lo)
    lo.location = loc; lo.rotation_euler = rot
area((-1.8, 2.6, 1.6), 260, 2.6, (1, 0.93, 0.83), (math.radians(-55), 0, math.radians(-155)))
area((2.0, 2.2, 0.6), 90, 2.2, (0.65, 0.72, 0.95), (math.radians(-65), 0, math.radians(150)))
area((0, 0.5, 2.6), 70, 2.0, (1, 0.85, 0.6), (0, 0, 0))
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.25
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.5, 0.5, 0.6, 1)

os.makedirs(OUT, exist_ok=True)
def render_frame(name, i):
    sc.render.filepath = os.path.join(OUT, f'{name}_{i:02d}.png')
    bpy.ops.render.render(write_still=True)

if TEST_ONLY:
    pose_run(0.25); render_frame('t5run', 0)
    pose_run(0.75); render_frame('t5run', 1)
    pose_jump(0.5); render_frame('t5jump', 2)
    pose_slide(0.3); render_frame('t5slide', 3)
    print('TEST5_DONE')
else:
    for i in range(25): pose_run(i / 25.0); render_frame('run', i)
    for i in range(25): pose_jump(i / 25.0); render_frame('jump', i)
    for i in range(25): pose_slide(i / 25.0); render_frame('slide', i)
    print('ALL5_DONE')
