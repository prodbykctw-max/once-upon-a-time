import bpy, math, os, sys

# Runs headless on assets/jande_rodin.blend. Renders back-view animation
# frames for bkrun / bkjump / bkslide using a lattice deformation rig.
OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\jande_frames"
TEST_ONLY = '--test' in sys.argv

obj = bpy.data.objects['JandeModel']
sc = bpy.context.scene

# clean scene of check helpers
for nm in ('ChkCam', 'ChkSun', 'Cube', 'Light', 'Camera'):
    o = bpy.data.objects.get(nm)
    if o: bpy.data.objects.remove(o, do_unlink=True)

# ── render setup ──
sc.render.engine = 'CYCLES'
sc.cycles.samples = 64
sc.cycles.use_denoising = True
sc.view_settings.view_transform = 'Filmic'
sc.render.film_transparent = True
sc.render.resolution_x = 512
sc.render.resolution_y = 512
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_mode = 'RGBA'

# model: feet at z=-0.951, head at +0.951, faces -Y.
# camera BEHIND her (at +Y) for the back view.
cam_data = bpy.data.cameras.new('AnimCam')
cam_data.type = 'ORTHO'
cam_data.ortho_scale = 2.15
cam = bpy.data.objects.new('AnimCam', cam_data)
sc.collection.objects.link(cam)
cam.location = (0, 3.2, -0.02)
cam.rotation_euler = (math.pi/2, 0, math.pi)
sc.camera = cam

# lighting: warm key upper-left-behind, cool fill right, subtle top rim
def area(loc, e, size, col, rot):
    ld = bpy.data.lights.new('L', 'AREA'); ld.energy = e; ld.size = size; ld.color = col
    lo = bpy.data.objects.new('L', ld); sc.collection.objects.link(lo)
    lo.location = loc; lo.rotation_euler = rot
    return lo
area((-1.8, 2.6, 1.6), 260, 2.6, (1, 0.93, 0.83), (math.radians(-55), 0, math.radians(-155)))
area((2.0, 2.2, 0.6), 90, 2.2, (0.65, 0.72, 0.95), (math.radians(-65), 0, math.radians(150)))
area((0, 0.5, 2.6), 70, 2.0, (1, 0.85, 0.6), (0, 0, 0))
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.25
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.5, 0.5, 0.6, 1)

# ── lattice rig: 4 x 2 x 10 control grid around the body ──
lat = bpy.data.lattices.new('Lat')
lat.points_u = 4   # X: [outer-left, inner-left, inner-right, outer-right]
lat.points_v = 2   # Y: front/back
lat.points_w = 10  # Z: 10 height bands, 0=feet 9=head
lat_obj = bpy.data.objects.new('Lat', lat)
sc.collection.objects.link(lat_obj)
lat_obj.location = (0, 0, 0)
lat_obj.scale = (1.05, 0.6, 2.0)   # cover the 0.94 x 0.45 x 1.9 body

mod = obj.modifiers.new('LatDef', 'LATTICE')
mod.object = lat_obj

# base (rest) positions of the 4x2x10 grid — regular grid in lattice space (-0.5..0.5)
import copy
base = [(p.co_deform.x, p.co_deform.y, p.co_deform.z) for p in lat.points]

def idx(u, v, wq): return wq * (4 * 2) + v * 4 + u

def reset_lattice():
    for p, b in zip(lat.points, base):
        p.co_deform = b

# Height bands (w index 0..9 spans z -0.5..0.5 in lattice space => feet..head):
# w 0-1: feet/shin · w 2-3: knee/thigh · w 4: hip · w 5-6: torso · w 7: chest · w 8: shoulders/arms · w 9: head
# X columns: u0 = her right outer (arm+leg), u1 = right inner, u2 = left inner, u3 = left outer.

def pose_run(t):
    """t in [0,1) — full run cycle. Legs swing in Y, counter-arm swing, bob."""
    reset_lattice()
    ph = t * 2 * math.pi
    swingR = math.sin(ph)            # right leg forward when +
    swingL = -swingR
    bob = abs(math.sin(ph)) * 0.045
    for wq in range(10):
        zt = wq / 9.0                       # 0 feet .. 1 head
        legf = max(0.0, 1.0 - zt / 0.45)    # leg influence fades to 0 at hip
        legf = legf * legf * 0.55
        armf = max(0.0, 1.0 - abs(zt - 0.82) / 0.14)  # arm band near shoulders
        for v in range(2):
            for u in range(4):
                p = lat.points[idx(u, v, wq)]
                bx, by, bz = base[idx(u, v, wq)]
                y = by; z = bz
                right = u <= 1
                # legs swing (lattice y: her front is -y world; forward = -y)
                sw = swingR if right else swingL
                y += -sw * legf
                # lift foot on back-swing (knee bend read)
                z += max(0.0, -sw) * legf * 0.35
                # arms counter-swing on outer columns
                if u in (0, 3) and armf > 0:
                    asw = swingL if right else swingR
                    y += -asw * armf * 0.18
                # torso bob + slight forward lean at top
                z += bob * min(1.0, zt * 2)
                y += -zt * 0.045   # lean forward
                p.co_deform = (bx, y, z)

def pose_jump(t):
    """t in [0,1) — crouch, launch, tuck, extend, land."""
    reset_lattice()
    if t < 0.18:   sq, tuck, arm = 1 - (t / 0.18) * 0.16, 0.0, -0.3        # crouch
    elif t < 0.4:  k = (t - 0.18) / 0.22; sq, tuck, arm = 0.84 + k * 0.24, k * 0.3, k  # launch+stretch
    elif t < 0.65: sq, tuck, arm = 1.08 - (t - 0.4) * 0.1, 0.85, 1.0        # tuck at peak
    elif t < 0.85: k = (t - 0.65) / 0.2; sq, tuck, arm = 1.03 - k * 0.1, 0.85 - k * 0.85, 1 - k
    else:          k = (t - 0.85) / 0.15; sq, tuck, arm = 0.93 - k * 0.05 + k * 0.1, 0.0, -0.2  # land
    for wq in range(10):
        zt = wq / 9.0
        legf = max(0.0, 1.0 - zt / 0.4); legf *= legf
        armf = max(0.0, 1.0 - abs(zt - 0.82) / 0.14)
        for v in range(2):
            for u in range(4):
                p = lat.points[idx(u, v, wq)]
                bx, by, bz = base[idx(u, v, wq)]
                # squash/stretch around feet anchor (z=-0.5)
                z = -0.5 + (bz + 0.5) * sq
                y = by
                # tuck: pull feet up+forward
                z += tuck * legf * 0.42
                y += -tuck * legf * 0.3
                # arms raise on outer columns
                if u in (0, 3) and armf > 0:
                    z += arm * armf * 0.12
                p.co_deform = (bx, y, z)

def pose_slide(t):
    """low crouch lean-back slide with subtle 2-phase wobble"""
    reset_lattice()
    wob = math.sin(t * 2 * math.pi * 2) * 0.02
    sq = 0.62 + wob
    for wq in range(10):
        zt = wq / 9.0
        for v in range(2):
            for u in range(4):
                p = lat.points[idx(u, v, wq)]
                bx, by, bz = base[idx(u, v, wq)]
                z = -0.5 + (bz + 0.5) * sq
                y = by + zt * 0.28          # lean back (top toward +y camera side)
                # knees forward at low bands
                if zt < 0.35: y += -(0.35 - zt) * 0.5
                p.co_deform = (bx, y, z)

os.makedirs(OUT, exist_ok=True)

def render_frame(name, i):
    sc.render.filepath = os.path.join(OUT, f'{name}_{i:02d}.png')
    bpy.ops.render.render(write_still=True)

if TEST_ONLY:
    pose_run(0.0);  render_frame('test_run', 0)
    pose_run(0.25); render_frame('test_run', 1)
    pose_jump(0.5); render_frame('test_jump', 2)
    pose_slide(0.1); render_frame('test_slide', 3)
    print('TEST_FRAMES_DONE')
else:
    for i in range(25):
        pose_run(i / 25.0); render_frame('run', i)
    for i in range(25):
        pose_jump(i / 25.0); render_frame('jump', i)
    for i in range(25):
        pose_slide(i / 25.0); render_frame('slide', i)
    print('ALL_FRAMES_DONE')
