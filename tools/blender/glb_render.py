import bpy, math, os, sys
import numpy as np

# Render back-view run/jump/slide sheets from the rigged GLB's own animation
# clips. 25 frames each, sampled across the clip, camera behind the character.
GLB = r"C:\Users\Owner\Downloads\1784330987247_0e2840b2-5ea2-4f1e-b174-e3c6b981c2da_bundle_glb.glb"
OUT = r"C:\Users\Owner\Documents\once-upon-a-time\assets\renders\jande_frames"
TEST = '--test' in sys.argv
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=GLB)
sc = bpy.context.scene

# drop the stray helper icosphere
ico = bpy.data.objects.get('Icosphere')
if ico: bpy.data.objects.remove(ico, do_unlink=True)

arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
mesh = next(o for o in bpy.data.objects if o.type == 'MESH')

# world bounds of the mesh at rest for framing
def mesh_bounds():
    dg = bpy.context.evaluated_depsgraph_get()
    ev = mesh.evaluated_get(dg)
    vs = np.array([ (mesh.matrix_world @ v.co) for v in ev.data.vertices ])
    return vs.min(axis=0), vs.max(axis=0)
mn, mx = mesh_bounds()
cx = (mn[0]+mx[0])/2; cz = (mn[2]+mx[2])/2
height = mx[2]-mn[2]
print(f'bounds min={mn} max={mx} h={height:.3f}')

# render setup
sc.render.engine = 'CYCLES'
sc.cycles.samples = 64
sc.cycles.use_denoising = True
sc.view_settings.view_transform = 'Standard'   # keep the white gown white
sc.view_settings.exposure = 0.3
sc.render.film_transparent = True
sc.render.resolution_x = 512
sc.render.resolution_y = 512
sc.render.image_settings.file_format = 'PNG'
sc.render.image_settings.color_mode = 'RGBA'

# camera BEHIND the character. Mixamo faces -Y by default; back view = camera
# on +Y looking toward -Y so we see the character's back.
cam_data = bpy.data.cameras.new('Cam'); cam_data.type = 'ORTHO'
cam_data.ortho_scale = height * 1.15
cam = bpy.data.objects.new('Cam', cam_data)
sc.collection.objects.link(cam)
cam.location = (cx, mx[1] + 3.0, cz)
cam.rotation_euler = (math.pi/2, 0, math.pi)   # look -Y
sc.camera = cam

def area(loc, e, size, col, rot):
    ld = bpy.data.lights.new('L','AREA'); ld.energy=e; ld.size=size; ld.color=col
    lo = bpy.data.objects.new('L', ld); sc.collection.objects.link(lo)
    lo.location=loc; lo.rotation_euler=rot
# lights relative to a character facing -Y, camera on +Y (behind)
area((cx-1.8, mx[1]+2.6, cz+1.6), 520, 3.0, (1,0.95,0.86), (math.radians(-52),0,math.radians(-150)))
area((cx+2.0, mx[1]+2.2, cz+0.6), 240, 2.6, (0.72,0.78,0.98), (math.radians(-62),0,math.radians(150)))
area((cx, mn[1]-2.6, cz+1.4), 300, 3.0, (1,0.92,0.82), (math.radians(-72),0,0))   # back/rim behind camera
area((cx, mx[1]+2.0, cz+2.2), 160, 3.0, (1,0.96,0.9), (math.radians(-30),0,0))    # top fill
w = bpy.data.worlds.new('W'); sc.world=w; w.use_nodes=True
w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.55
w.node_tree.nodes['Background'].inputs['Color'].default_value = (0.62,0.64,0.72,1)

def set_action(name):
    act = bpy.data.actions.get(name)
    if not arm.animation_data:
        arm.animation_data_create()
    arm.animation_data.action = act
    return act

def frame_bounds():
    dg = bpy.context.evaluated_depsgraph_get()
    ev = mesh.evaluated_get(dg)
    vs = np.array([ (mesh.matrix_world @ v.co)[:] for v in ev.data.vertices ])
    return vs.min(axis=0), vs.max(axis=0)

def render_clip(action_name, out_prefix, nframes=25, trim=(0.0, 1.0), ground=True):
    act = set_action(action_name)
    f0, f1 = act.frame_range
    a = f0 + (f1 - f0) * trim[0]
    b = f0 + (f1 - f0) * trim[1]
    frames = [a + (b - a) * (i / nframes) for i in range(nframes)]  # loop-friendly
    # pass 1: union bounds (with grounding applied per frame the same way)
    umn = np.array([1e9]*3); umx = np.array([-1e9]*3)
    floors = []
    for fr in frames:
        sc.frame_set(int(round(fr)))
        bmn, bmx = frame_bounds()
        floors.append(bmn[2])
        umn = np.minimum(umn, bmn); umx = np.maximum(umx, bmx)
    clip_floor = min(floors)
    # frame the character: center X and Z on the union, fit height with margin
    cxu = (umn[0]+umx[0])/2
    czu = (umn[2]+umx[2])/2
    fig_h = umx[2]-umn[2]; fig_w = umx[0]-umn[0]
    span = max(fig_h, fig_w) * 1.12
    cam.data.ortho_scale = span
    cam.location = (cxu, umx[1] + 3.0, czu)
    # pass 2: render each frame; ground feet to a constant floor (run/slide)
    for i, fr in enumerate(frames):
        sc.frame_set(int(round(fr)))
        dz = 0.0
        if ground:
            bmn, _ = frame_bounds()
            dz = clip_floor - bmn[2]
            arm.location.z += dz
        sc.render.filepath = os.path.join(OUT, f'{out_prefix}_{i:02d}.png')
        bpy.ops.render.render(write_still=True)
        if ground:
            arm.location.z -= dz

if TEST:
    render_clip('jog_fwd_loop', 'run', 25)
    # copy frame 6 + 18 out for inspection
    import shutil
    shutil.copy(os.path.join(OUT,'run_06.png'), os.path.join(OUT,'glbtest_jog.png'))
    shutil.copy(os.path.join(OUT,'run_18.png'), os.path.join(OUT,'glbtest_jog2.png'))
    print('GLB_TEST_DONE')
else:
    render_clip('jog_fwd_loop', 'run', 25, ground=True)
    render_clip('jump_loop', 'jump', 25, trim=(0.0, 1.0), ground=False)
    render_clip('roll', 'slide', 25, trim=(0.1, 0.95), ground=True)
    print('GLB_RENDER_DONE')
