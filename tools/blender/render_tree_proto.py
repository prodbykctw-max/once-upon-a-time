import bpy, math, os, sys
FRAMEWORK = r"C:\Users\Owner\Documents\once-upon-a-time\tools\blender\framework.py"
exec(open(FRAMEWORK).read())
OUT = r"C:\Users\Owner\Documents\once-upon-a-time\assets\renders\proto"
os.makedirs(OUT, exist_ok=True)
GLTF = r"C:\Users\Owner\Documents\once-upon-a-time\assets\models\island_tree_01\island_tree_01_1k.gltf"

reset_scene()
# clear default cube/light/cam
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

bpy.ops.import_scene.gltf(filepath=GLTF)
objs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
print('imported meshes:', len(objs))

# world-space bounds
import mathutils
mn = mathutils.Vector((1e9, 1e9, 1e9)); mx = mathutils.Vector((-1e9, -1e9, -1e9))
for o in objs:
    for c in o.bound_box:
        w = o.matrix_world @ mathutils.Vector(c)
        for i in range(3):
            mn[i] = min(mn[i], w[i]); mx[i] = max(mx[i], w[i])
size = mx - mn
print('bounds size:', tuple(round(v, 2) for v in size))
# recenter to origin, base on z=0
cx = (mn.x + mx.x) / 2; cy = (mn.y + mx.y) / 2
for o in objs:
    if o.parent is None:
        o.location.x -= cx; o.location.y -= cy; o.location.z -= mn.z
bpy.context.view_layer.update()
H = size.z   # tree height after grounding

# soft whimsy lighting: HDRI + gentle key, matching the props
if not hdri_world('meadow', strength=0.55, rot_z=math.radians(-30)):
    w = bpy.data.worlds.new('W'); bpy.context.scene.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.5
area_light((-2.0, -3.0, H), 200, 3.0, (1, 0.96, 0.86), (math.radians(52), 0, math.radians(-28)))
area_light((2.4, -2.0, H*0.6), 90, 2.6, (0.8, 0.86, 1.0), (math.radians(64), 0, math.radians(38)))

# front-ortho, 0.45 cell aspect, bottom-anchored (z=0 at bottom edge)
FRAME_H = H * 1.12
d = bpy.data.cameras.new('C'); d.type = 'ORTHO'; d.ortho_scale = FRAME_H; d.sensor_fit = 'VERTICAL'
c = bpy.data.objects.new('C', d); bpy.context.scene.collection.objects.link(c)
c.location = (0, -max(20, H*4), FRAME_H/2 - H*0.06); c.rotation_euler = (math.radians(90), 0, 0)
bpy.context.scene.camera = c

sc = bpy.context.scene
sc.view_settings.view_transform = 'Standard'
render_to(os.path.join(OUT, 'polyhaven_tree.png'), 432, 960, transparent=True, samples=128)
print('PROTO_TREE_DONE')
