import bpy, math, os, sys
import numpy as np

# v2: direct per-vertex limb rotation (no lattice). Feet arcs, shoulder
# counter-twist, bob and lean — all visible from the back-view ortho camera.
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

FOOT_Z = Z.min()          # -0.951
HIP_Z = -0.08
SHOULDER_Z = 0.52
HEAD_Z = Z.max()

# ── region weights (smooth 0..1 masks) ──
def smooth(a):  # clamp + smoothstep
    a = np.clip(a, 0, 1)
    return a * a * (3 - 2 * a)

# legs: below hip, split by x sign, weight ramps in over 0.12m below hip
leg_w = smooth((HIP_Z - Z) / 0.12)
left_side = smooth((X - 0.01) / 0.05)     # 1 on her left (world +x), 0 right
right_side = 1.0 - left_side
# arms: outside shoulder width, between z 0.0..0.7 — A-pose arms angle down/out
arm_band = smooth((np.abs(X) - 0.20) / 0.06) * smooth((Z - 0.02) / 0.1) * smooth((0.68 - Z) / 0.1)
arm_w = arm_band * (1.0 - leg_w)
# upper body (twist region): above hip
up_w = smooth((Z - HIP_Z) / 0.25)

def rot_about(P, weight, pivot_z, angle):
    """rotate positions about world X axis at pivot (0, y-any, pivot_z), weighted."""
    if abs(angle) < 1e-5: return
    c, s = math.cos(angle), math.sin(angle)
    y = P[:, 1]; z = P[:, 2] - pivot_z
    ny = y * c - z * s
    nz = y * s + z * c
    P[:, 1] = y + (ny - y) * weight
    P[:, 2] = pivot_z + z + ((nz - z) * weight)

def twist(P, weight, angle):
    if abs(angle) < 1e-5: return
    c, s = math.cos(angle), math.sin(angle)
    x = P[:, 0]; y = P[:, 1]
    nx = x * c - y * s
    ny = x * s + y * c
    P[:, 0] = x + (nx - x) * weight
    P[:, 1] = y + (ny - y) * weight

def apply(P):
    me.vertices.foreach_set('co', P.reshape(-1))
    me.update()

def pose_run(t):
    ph = t * 2 * math.pi
    P = REST.copy()
    swing = math.sin(ph)                     # + = left leg forward
    # legs rotate about hip: left forward when swing+, right opposite
    rot_about(P, leg_w * left_side, HIP_Z, -swing * math.radians(32))
    rot_about(P, leg_w * right_side, HIP_Z, swing * math.radians(32))
    # extra heel lift on the back-swinging leg (fake knee bend)
    backL = max(0.0, -swing); backR = max(0.0, swing)
    heel = smooth((HIP_Z - 0.55 - Z) / 0.25)  # strongest at feet
    P[:, 2] += heel * left_side * leg_w * backL * 0.22
    P[:, 2] += heel * right_side * leg_w * backR * 0.22
    # arms counter-swing about shoulder
    rot_about(P, arm_w * left_side, SHOULDER_Z, swing * math.radians(24))
    rot_about(P, arm_w * right_side, SHOULDER_Z, -swing * math.radians(24))
    # shoulder counter-twist (very visible from back)
    twist(P, up_w, swing * math.radians(7))
    # bob + forward lean
    P[:, 2] += abs(math.sin(ph)) * 0.05
    P[:, 1] += (Z - FOOT_Z) * 0.05
    apply(P)

def pose_jump(t):
    P = REST.copy()
    if t < 0.18:
        k = t / 0.18; sq = 1 - 0.14 * k; tuck = 0; armup = -k * 0.3
    elif t < 0.4:
        k = (t - 0.18) / 0.22; sq = 0.86 + 0.22 * k; tuck = 0.25 * k; armup = k
    elif t < 0.65:
        sq = 1.05; tuck = 1.0; armup = 1.0
    elif t < 0.85:
        k = (t - 0.65) / 0.2; sq = 1.03 - 0.06 * k; tuck = 1 - k; armup = 1 - k * 0.7
    else:
        k = (t - 0.85) / 0.15; sq = 0.9 + 0.08 * k; tuck = 0; armup = -0.25 * (1 - k)
    # squash/stretch anchored at feet
    P[:, 2] = FOOT_Z + (P[:, 2] - FOOT_Z) * sq
    # tuck: both legs rotate forward+up hard
    rot_about(P, leg_w, HIP_Z * sq, -tuck * math.radians(50))
    heel = smooth((HIP_Z - 0.55 - Z) / 0.25)
    P[:, 2] += heel * leg_w * tuck * 0.3
    # arms swing up/back
    rot_about(P, arm_w, SHOULDER_Z * sq, armup * math.radians(35))
    # slight forward lean into the jump
    P[:, 1] += (P[:, 2] - FOOT_Z) * 0.04 * (1 + tuck)
    apply(P)

def pose_slide(t):
    P = REST.copy()
    wob = math.sin(t * 4 * math.pi) * 0.02
    sq = 0.6 + wob
    P[:, 2] = FOOT_Z + (P[:, 2] - FOOT_Z) * sq
    # knees drive forward, torso leans back
    rot_about(P, leg_w, HIP_Z * sq, math.radians(-30))
    P[:, 1] += (P[:, 2] - FOOT_Z) * 0.22          # lean back
    rot_about(P, arm_w, SHOULDER_Z * sq, math.radians(-25))
    apply(P)

os.makedirs(OUT, exist_ok=True)
def render_frame(name, i):
    sc.render.filepath = os.path.join(OUT, f'{name}_{i:02d}.png')
    bpy.ops.render.render(write_still=True)

if TEST_ONLY:
    pose_run(0.25); render_frame('t2run', 0)
    pose_run(0.75); render_frame('t2run', 1)
    pose_jump(0.5); render_frame('t2jump', 2)
    pose_slide(0.1); render_frame('t2slide', 3)
    # numeric sanity
    pose_run(0.25)
    A = np.empty(n * 3); me.vertices.foreach_get('co', A); A = A.reshape(n, 3)
    lf = A[(REST[:, 0] > 0.05) & (REST[:, 2] < -0.5)]
    rf = A[(REST[:, 0] < -0.05) & (REST[:, 2] < -0.5)]
    print("run t.25 left foot z", round(lf[:, 2].min(), 3), "y", round(lf[:, 1].mean(), 2),
          "| right foot z", round(rf[:, 2].min(), 3), "y", round(rf[:, 1].mean(), 2))
    print('TEST2_DONE')
else:
    for i in range(25): pose_run(i / 25.0); render_frame('run', i)
    for i in range(25): pose_jump(i / 25.0); render_frame('jump', i)
    for i in range(25): pose_slide(i / 25.0); render_frame('slide', i)
    apply(REST)
    print('ALL_FRAMES_DONE')
