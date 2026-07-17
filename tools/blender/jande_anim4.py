import bpy, math, os, sys
import numpy as np

# v4: armature-driven gait on the rigged scan (jande_rigged.blend).
# Convention (calibrated): +X on a limb bone swings it BACKWARD.
OUT = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\jande_frames"
TEST_ONLY = '--test' in sys.argv

obj = bpy.data.objects['JandeModel']
rig = bpy.data.objects['Rig']
drv = bpy.data.objects['Driver']
drv.hide_render = True
sc = bpy.context.scene

sc.render.engine = 'CYCLES'
sc.cycles.samples = 64
sc.cycles.use_denoising = True
sc.view_settings.view_transform = 'Filmic'
sc.render.film_transparent = True
sc.render.resolution_x = 512
sc.render.resolution_y = 512
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_mode = 'RGBA'

for o in list(bpy.data.objects):
    if o.name.startswith(('Cam', 'Sun', 'L.', 'Area')) and o.type in ('CAMERA', 'LIGHT'):
        bpy.data.objects.remove(o, do_unlink=True)

cam_data = bpy.data.cameras.new('AnimCam')
cam_data.type = 'ORTHO'
cam_data.ortho_scale = 2.15
cam = bpy.data.objects.new('AnimCam', cam_data)
sc.collection.objects.link(cam)
cam.location = (0, 3.2, -0.02)
cam.rotation_euler = (math.pi/2, 0, math.pi)
sc.camera = cam

def area(loc, e, size, col, rot):
    ld = bpy.data.lights.new('AL', 'AREA'); ld.energy = e; ld.size = size; ld.color = col
    lo = bpy.data.objects.new('AL', ld); sc.collection.objects.link(lo)
    lo.location = loc; lo.rotation_euler = rot
area((-1.8, 2.6, 1.6), 260, 2.6, (1, 0.93, 0.83), (math.radians(-55), 0, math.radians(-155)))
area((2.0, 2.2, 0.6), 90, 2.2, (0.65, 0.72, 0.95), (math.radians(-65), 0, math.radians(150)))
area((0, 0.5, 2.6), 70, 2.0, (1, 0.85, 0.6), (0, 0, 0))
w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.25
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.5, 0.5, 0.6, 1)

pb = rig.pose.bones
for b in pb:
    b.rotation_mode = 'XYZ'

FOOT_Z = -0.951

def reset_pose():
    for b in pb:
        b.rotation_euler = (0, 0, 0)
        b.location = (0, 0, 0)

def deg(bone, x=0.0, y=0.0, z=0.0):
    pb[bone].rotation_euler = (math.radians(x), math.radians(y), math.radians(z))

def ground():
    """anchor lowest evaluated vertex to FOOT_Z via object z offset"""
    obj.location.z = 0
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(dg)
    m = ev.to_mesh()
    co = np.empty(len(m.vertices) * 3)
    m.vertices.foreach_get('co', co)
    zmin = co.reshape(-1, 3)[:, 2].min()
    ev.to_mesh_clear()
    obj.location.z = FOOT_Z - zmin

def pose_run(t):
    reset_pose()
    ph = t * 2 * math.pi
    swing = math.sin(ph)                     # + = left leg forward
    backL = max(0.0, -swing); backR = max(0.0, swing)
    # legs: thigh swing, knee flexion on recovery, toe point when trailing
    deg('thigh.L', x=-swing * 30)
    deg('thigh.R', x=swing * 30)
    deg('shin.L', x=14 + 58 * backL)
    deg('shin.R', x=14 + 58 * backR)
    deg('foot.L', x=8 + 18 * backL)
    deg('foot.R', x=8 + 18 * backR)
    # arms: runner elbows, counter-phase pump
    deg('upper_arm.L', x=8 + swing * 26)
    deg('upper_arm.R', x=8 - swing * 26)
    deg('forearm.L', x=-72 - swing * 10)
    deg('forearm.R', x=-72 + swing * 10)
    # torso: forward lean + shoulder counter-twist
    deg('spine', x=-5)
    deg('chest', x=-4, y=swing * 7)
    deg('head', x=6)                          # look ahead despite lean
    ground()

def pose_jump(t):
    reset_pose()
    if t < 0.18:
        k = t / 0.18; crouch = k; tuck = 0; armup = -0.4 * k
    elif t < 0.4:
        k = (t - 0.18) / 0.22; crouch = 1 - k; tuck = 0.3 * k; armup = k
    elif t < 0.65:
        crouch = 0; tuck = 1.0; armup = 1.0
    elif t < 0.85:
        k = (t - 0.65) / 0.2; crouch = 0; tuck = 1 - k; armup = 1 - 0.7 * k
    else:
        k = (t - 0.85) / 0.15; crouch = 0.8 * (1 - k); tuck = 0; armup = -0.3 * (1 - k)
    # crouch: hips drop + knees bend
    pb['hips'].location = (0, -0.22 * crouch, 0)
    deg('thigh.L', x=-45 * crouch - 55 * tuck)
    deg('thigh.R', x=-42 * crouch - 50 * tuck)
    deg('shin.L', x=55 * crouch + 85 * tuck)
    deg('shin.R', x=52 * crouch + 88 * tuck)
    deg('foot.L', x=15 * tuck + 10 * crouch)
    deg('foot.R', x=15 * tuck + 10 * crouch)
    deg('spine', x=-6 - 10 * crouch)
    deg('chest', x=-5 - 8 * crouch)
    deg('head', x=8 + 8 * crouch)
    # arms: swing down on crouch, up on rise
    deg('upper_arm.L', x=10 - armup * 55)
    deg('upper_arm.R', x=10 - armup * 52)
    deg('forearm.L', x=-55 - armup * 15)
    deg('forearm.R', x=-55 - armup * 15)
    if tuck > 0 or crouch > 0:
        bpy.context.view_layer.update()
    if t < 0.18 or t >= 0.85:
        ground()
    else:
        obj.location.z = 0
        bpy.context.view_layer.update()

def pose_slide(t):
    reset_pose()
    wob = math.sin(t * 4 * math.pi)
    pb['hips'].location = (0, -0.5 - 0.02 * wob, 0)
    deg('thigh.L', x=-85)
    deg('thigh.R', x=-78)
    deg('shin.L', x=95)
    deg('shin.R', x=88)
    deg('foot.L', x=20)
    deg('foot.R', x=20)
    deg('spine', x=14)
    deg('chest', x=12)
    deg('head', x=-14)
    deg('upper_arm.L', x=30 + 3 * wob)
    deg('upper_arm.R', x=26 - 3 * wob)
    deg('forearm.L', x=-45)
    deg('forearm.R', x=-45)
    ground()

os.makedirs(OUT, exist_ok=True)
def render_frame(name, i):
    sc.render.filepath = os.path.join(OUT, f'{name}_{i:02d}.png')
    bpy.ops.render.render(write_still=True)

if TEST_ONLY:
    pose_run(0.25); render_frame('t4run', 0)
    pose_run(0.75); render_frame('t4run', 1)
    pose_jump(0.5); render_frame('t4jump', 2)
    pose_slide(0.1); render_frame('t4slide', 3)
    print('TEST4_DONE')
else:
    for i in range(25): pose_run(i / 25.0); render_frame('run', i)
    for i in range(25): pose_jump(i / 25.0); render_frame('jump', i)
    for i in range(25): pose_slide(i / 25.0); render_frame('slide', i)
    print('ALL4_DONE')
