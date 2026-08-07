import bpy, math, os, sys
import numpy as np

# v3: anatomical gait. Two-segment legs (thigh swing + knee flexion),
# runner arms (adducted + elbow-bent, pumping fore/aft), auto ground
# contact via per-frame min-foot re-anchoring.
OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\jande_frames"
TEST_ONLY = '--test' in sys.argv

obj = bpy.data.objects['JandeModel']
sc = bpy.context.scene
for nm in ('ChkCam', 'ChkSun', 'Cube', 'Light', 'Camera', 'Lat'):
    o = bpy.data.objects.get(nm)
    if o: bpy.data.objects.remove(o, do_unlink=True)
for m in list(obj.modifiers):
    obj.modifiers.remove(m)

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
cam_data.ortho_scale = 2.15
cam = bpy.data.objects.new('AnimCam', cam_data)
sc.collection.objects.link(cam)
cam.location = (0, 3.2, -0.02)
cam.rotation_euler = (math.pi/2, 0, math.pi)
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

me = obj.data
n = len(me.vertices)
REST = np.empty(n * 3)
me.vertices.foreach_get('co', REST)
REST = REST.reshape(n, 3).copy()
X, Y, Z = REST[:, 0], REST[:, 1], REST[:, 2]

FOOT_Z = Z.min()
HIP_Z = -0.08
KNEE_Z = -0.50
SHOULDER_Z = 0.55
SHOULDER_X = 0.22

def smooth(a):
    a = np.clip(a, 0, 1)
    return a * a * (3 - 2 * a)

# ── region weights from REST coords ──
leg_w = smooth((HIP_Z - Z) / 0.12)
shin_w = smooth((KNEE_Z + 0.02 - Z) / 0.10)          # below the knee
left_side = smooth((X - 0.01) / 0.05)
right_side = 1.0 - left_side
up_w = smooth((Z - HIP_Z) / 0.25)

# capsule mask: weight by distance from the A-pose arm AXIS (shoulder->hand).
# This follows the actual limb, so torso/hip verts can never be caught.
armL_S = np.array([SHOULDER_X, 0.0, SHOULDER_Z])
armL_H = np.array([0.44, -0.02, 0.02])
d = armL_H - armL_S; Lm = np.linalg.norm(d)

def arm_capsule(S, H):
    dd = H - S
    t = np.clip(((REST - S) @ dd) / (Lm * Lm), 0.0, 1.10)  # 1.10: include fingers
    C = S[None, :] + t[:, None] * dd[None, :]
    r = np.linalg.norm(REST - C, axis=1)
    wgt = smooth((0.085 - r) / 0.03)
    return wgt, t

armR_S = armL_S * np.array([-1, 1, 1]); armR_H = armL_H * np.array([-1, 1, 1])
awL, tL = arm_capsule(armL_S, armL_H)
awR, tR = arm_capsule(armR_S, armR_H)
arm_w = np.maximum(awL * left_side, awR * right_side)
t_arm = np.where(X > 0, tL, tR)
fore_w = smooth((t_arm - 0.48) / 0.10)               # elbow crease

# ── RIGID PER-ISLAND WEIGHTS ──
# The Rodin scan is ~1700 disconnected shell fragments; smooth per-vertex
# weights let a fragment straddle a crease and tear into ribbons. Averaging
# every weight over its island makes each fragment move as a rigid piece.
island_id = np.full(n, -1, dtype=np.int64)
adj = [[] for _ in range(n)]
for e in me.edges:
    a, b = e.vertices
    adj[a].append(b); adj[b].append(a)
cur = 0
for seed in range(n):
    if island_id[seed] >= 0: continue
    stack = [seed]; island_id[seed] = cur
    while stack:
        v = stack.pop()
        for nb in adj[v]:
            if island_id[nb] < 0:
                island_id[nb] = cur; stack.append(nb)
    cur += 1
counts = np.bincount(island_id, minlength=cur).astype(np.float64)
def island_mean(wgt):
    sums = np.bincount(island_id, weights=wgt, minlength=cur)
    return (sums / counts)[island_id]
leg_w = island_mean(leg_w)
shin_w = island_mean(shin_w)
left_side = island_mean(left_side)
right_side = 1.0 - left_side
arm_w = island_mean(arm_w)
fore_w = island_mean(fore_w)
up_w = island_mean(up_w)
print(f'islands: {cur}')

def rotx_at(P, wgt, py, pz, ang):
    """rotate about world-X axis line through (y=py, z=pz), weighted."""
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

# ── RUNNER REST POSE: fold A-pose arms into pumping position ──
ADDUCT = math.radians(12)
ELBOW = math.radians(-85)
RUNNER = REST.copy()
# adduct toward torso (rotation about Y at each shoulder)
roty_at(RUNNER, arm_w * left_side, SHOULDER_X, SHOULDER_Z, ADDUCT)
roty_at(RUNNER, arm_w * right_side, -SHOULDER_X, SHOULDER_Z, -ADDUCT)
# elbow pivot after adduction (compute for the left, mirror for right)
e_rest = armL_S + (d / Lm) * (0.5 * Lm)
ex, ez = e_rest[0] - SHOULDER_X, e_rest[2] - SHOULDER_Z
c, s = math.cos(ADDUCT), math.sin(ADDUCT)
E_y = e_rest[1]
E_z = SHOULDER_Z + (-ex * s + ez * c)
# bend forearms forward to ~horizontal
rotx_at(RUNNER, arm_w * fore_w, E_y, E_z, ELBOW)

def leg_pose(P, side_mask, thigh_ang, knee_ang):
    """two-segment leg: thigh about hip, shin about (moved) knee."""
    rotx_at(P, leg_w * side_mask, 0.0, HIP_Z, thigh_ang)
    # knee pivot after thigh rotation
    kz_rel = KNEE_Z - HIP_Z
    ky = -kz_rel * math.sin(thigh_ang)
    kz = HIP_Z + kz_rel * math.cos(thigh_ang)
    rotx_at(P, shin_w * side_mask, ky, kz, knee_ang)

def ground(P):
    """re-anchor lowest foot vertex to FOOT_Z (keeps ground contact)."""
    feet = P[:, 2][leg_w > 0.5]
    if len(feet): P[:, 2] += FOOT_Z - feet.min()

def apply(P):
    me.vertices.foreach_set('co', P.reshape(-1))
    me.update()

def pose_run(t):
    ph = t * 2 * math.pi
    P = RUNNER.copy()
    swing = math.sin(ph)                 # + = left leg forward
    # legs: thigh swing +-30, knee 15 base + up to 70 on recovery leg
    kneeL = math.radians(15 + 62 * max(0.0, -swing))
    kneeR = math.radians(15 + 62 * max(0.0, swing))
    leg_pose(P, left_side, -swing * math.radians(30), kneeL)
    leg_pose(P, right_side, swing * math.radians(30), kneeR)
    # arms: pump counter-phase about shoulders (bent arms stay bent)
    rotx_at(P, arm_w * left_side, 0.0, SHOULDER_Z, swing * math.radians(30))
    rotx_at(P, arm_w * right_side, 0.0, SHOULDER_Z, -swing * math.radians(30))
    # shoulder counter-twist + forward lean
    twist(P, up_w, swing * math.radians(6))
    P[:, 1] += (Z - FOOT_Z) * 0.055
    ground(P)
    apply(P)

def pose_jump(t):
    P = RUNNER.copy()
    if t < 0.18:
        k = t / 0.18; sq = 1 - 0.14 * k; tuck = 0; armup = -k * 0.4
    elif t < 0.4:
        k = (t - 0.18) / 0.22; sq = 0.86 + 0.22 * k; tuck = 0.3 * k; armup = k
    elif t < 0.65:
        sq = 1.05; tuck = 1.0; armup = 1.0
    elif t < 0.85:
        k = (t - 0.65) / 0.2; sq = 1.03 - 0.06 * k; tuck = 1 - k; armup = 1 - k * 0.7
    else:
        k = (t - 0.85) / 0.15; sq = 0.9 + 0.08 * k; tuck = 0; armup = -0.3 * (1 - k)
    P[:, 2] = FOOT_Z + (P[:, 2] - FOOT_Z) * sq
    # tuck: thighs up hard + knees folded (feet under her)
    leg_pose(P, left_side, -tuck * math.radians(52), math.radians(15 + 75 * tuck))
    leg_pose(P, right_side, -tuck * math.radians(48), math.radians(15 + 78 * tuck))
    # bent arms swing up-forward
    rotx_at(P, arm_w, 0.0, SHOULDER_Z * sq, -armup * math.radians(45))
    P[:, 1] += (P[:, 2] - FOOT_Z) * 0.04 * (1 + tuck)
    apply(P)

def pose_slide(t):
    P = RUNNER.copy()
    wob = math.sin(t * 4 * math.pi) * 0.02
    sq = 0.6 + wob
    P[:, 2] = FOOT_Z + (P[:, 2] - FOOT_Z) * sq
    leg_pose(P, left_side, math.radians(-32), math.radians(30))
    leg_pose(P, right_side, math.radians(-28), math.radians(26))
    P[:, 1] += (P[:, 2] - FOOT_Z) * 0.22
    rotx_at(P, arm_w, 0.0, SHOULDER_Z * sq, math.radians(28))
    apply(P)

os.makedirs(OUT, exist_ok=True)
def render_frame(name, i):
    sc.render.filepath = os.path.join(OUT, f'{name}_{i:02d}.png')
    bpy.ops.render.render(write_still=True)

if TEST_ONLY:
    pose_run(0.25); render_frame('t3run', 0)
    pose_run(0.75); render_frame('t3run', 1)
    pose_run(0.0);  render_frame('t3run', 2)
    pose_jump(0.5); render_frame('t3jump', 3)
    print('TEST3_DONE')
else:
    for i in range(25): pose_run(i / 25.0); render_frame('run', i)
    for i in range(25): pose_jump(i / 25.0); render_frame('jump', i)
    for i in range(25): pose_slide(i / 25.0); render_frame('slide', i)
    apply(REST)
    print('ALL3_DONE')
