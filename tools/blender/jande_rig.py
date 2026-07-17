import bpy, math, os
# Build a proper rig for the Jande scan:
# voxel-remeshed driver + armature (auto weights) + surface-deform bind.
# Saves result as jande_rigged.blend, then renders a calibration frame.

obj = bpy.data.objects['JandeModel']
sc = bpy.context.scene
for nm in ('ChkCam', 'ChkSun', 'Cube', 'Light', 'Camera', 'Lat', 'Driver', 'Rig'):
    o = bpy.data.objects.get(nm)
    if o: bpy.data.objects.remove(o, do_unlink=True)
for m in list(obj.modifiers):
    obj.modifiers.remove(m)

# ── 1. driver: voxel-remeshed watertight copy ──
drv = obj.copy(); drv.data = obj.data.copy()
drv.name = 'Driver'; drv.data.name = 'DriverMesh'
drv.data.materials.clear()
sc.collection.objects.link(drv)
bpy.ops.object.select_all(action='DESELECT')
drv.select_set(True); bpy.context.view_layer.objects.active = drv
drv.data.remesh_voxel_size = 0.022
drv.data.use_remesh_fix_poles = True
bpy.ops.object.voxel_remesh()
print('driver verts:', len(drv.data.vertices))

# ── 2. armature ──
arm_data = bpy.data.armatures.new('RigData')
rig = bpy.data.objects.new('Rig', arm_data)
sc.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode='EDIT')
eb = arm_data.edit_bones

def bone(name, head, tail, parent=None, connect=False):
    b = eb.new(name)
    b.head = head; b.tail = tail
    if parent:
        b.parent = eb[parent]; b.use_connect = connect
    return b

bone('hips',      (0, 0, -0.16), (0, 0, 0.06))
bone('spine',     (0, 0, 0.06),  (0, 0, 0.36), 'hips', True)
bone('chest',     (0, 0, 0.36),  (0, 0, 0.56), 'spine', True)
bone('head',      (0, 0, 0.56),  (0, 0, 0.82), 'chest', True)
for s, sx in (('L', 1), ('R', -1)):
    bone(f'thigh.{s}', (sx*0.115, 0, -0.10), (sx*0.128, 0, -0.50), 'hips')
    bone(f'shin.{s}',  (sx*0.128, 0, -0.50), (sx*0.132, 0.01, -0.88), f'thigh.{s}', True)
    bone(f'foot.{s}',  (sx*0.132, 0.01, -0.88), (sx*0.135, -0.11, -0.945), f'shin.{s}', True)
    bone(f'upper_arm.{s}', (sx*0.20, 0, 0.55), (sx*0.335, -0.01, 0.285), 'chest')
    bone(f'forearm.{s}',   (sx*0.335, -0.01, 0.285), (sx*0.445, -0.02, 0.02), f'upper_arm.{s}', True)
bpy.ops.object.mode_set(mode='OBJECT')

# ── 3. auto weights on the driver ──
bpy.ops.object.select_all(action='DESELECT')
drv.select_set(True)
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
print('auto weights done')

# ── 4. surface-deform bind the textured scan to the driver ──
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True); bpy.context.view_layer.objects.active = obj
mod = obj.modifiers.new('SD', 'SURFACE_DEFORM')
mod.target = drv
mod.falloff = 4.0
bpy.ops.object.surfacedeform_bind(modifier='SD')
print('bind bound:', mod.is_bound)

drv.hide_render = True
drv.display_type = 'WIRE'

out = r"C:\Users\Owner\Documents\once-upon-a-time\assets\jande_rigged.blend"
bpy.ops.wm.save_as_mainfile(filepath=out)
print('SAVED', out)

# ── 5. calibration: +40 deg X on left limbs, render to learn sign conventions ──
sc.render.engine = 'BLENDER_EEVEE'
sc.render.resolution_x = 320
sc.render.resolution_y = 320
sc.render.film_transparent = True
cam_data = bpy.data.cameras.new('Cam'); cam_data.type = 'ORTHO'; cam_data.ortho_scale = 2.3
cam = bpy.data.objects.new('Cam', cam_data)
sc.collection.objects.link(cam)
cam.location = (0, 3.2, -0.02); cam.rotation_euler = (math.pi/2, 0, math.pi)
sc.camera = cam
sun = bpy.data.lights.new('Sun', 'SUN'); sun.energy = 4
so = bpy.data.objects.new('Sun', sun); sc.collection.objects.link(so)
so.rotation_euler = (math.radians(60), 0, math.radians(180))

pb = rig.pose.bones
for b in pb: b.rotation_mode = 'XYZ'
pb['thigh.L'].rotation_euler.x = math.radians(40)
pb['shin.L'].rotation_euler.x = math.radians(40)
pb['upper_arm.L'].rotation_euler.x = math.radians(40)
pb['forearm.L'].rotation_euler.x = math.radians(40)
bpy.context.view_layer.update()
sc.render.filepath = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\jande_frames\calib_back.png"
bpy.ops.render.render(write_still=True)
# side view for y-direction reading
cam.location = (3.2, 0, -0.02); cam.rotation_euler = (math.pi/2, 0, math.pi/2)
sc.render.filepath = r"C:\Users\Owner\AppData\Local\Temp\claude\C--Users-Owner--claude\0a631432-ca18-4d2f-a7d7-f3ab3dc7507f\scratchpad\overhaul\jande_frames\calib_side.png"
bpy.ops.render.render(write_still=True)
print('CALIB_DONE')
