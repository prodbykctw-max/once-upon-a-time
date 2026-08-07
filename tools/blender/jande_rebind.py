import bpy, math, bmesh

obj = bpy.data.objects['JandeModel']
drv = bpy.data.objects['Driver']
rig = bpy.data.objects['Rig']
sc = bpy.context.scene

# clear any pose from calibration
for b in rig.pose.bones:
    b.rotation_mode = 'XYZ'
    b.rotation_euler = (0, 0, 0)
bpy.context.view_layer.update()

# triangulate driver (SD needs planar convex target polys)
bm = bmesh.new()
bm.from_mesh(drv.data)
bmesh.ops.triangulate(bm, faces=bm.faces)
bm.to_mesh(drv.data)
bm.free()
drv.data.update()
print('driver tris:', len(drv.data.polygons))

# rebind surface deform
old = obj.modifiers.get('SD')
if old: obj.modifiers.remove(old)
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True); bpy.context.view_layer.objects.active = obj
mod = obj.modifiers.new('SD', 'SURFACE_DEFORM')
mod.target = drv
mod.falloff = 4.0
r = bpy.ops.object.surfacedeform_bind(modifier='SD')
bpy.context.view_layer.update()
print('bind result:', r, 'bound:', mod.is_bound)

bpy.ops.wm.save_mainfile()

# quick verify: pose left thigh 40deg, measure evaluated mesh asymmetry
pb = rig.pose.bones
pb['thigh.L'].rotation_euler.x = math.radians(40)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
ev = obj.evaluated_get(dg)
me2 = ev.to_mesh()
import numpy as np
co = np.empty(len(me2.vertices) * 3)
me2.vertices.foreach_get('co', co)
co = co.reshape(-1, 3)
lf = co[(co[:, 0] > 0.05) & (co[:, 2] < -0.3)]
rf = co[(co[:, 0] < -0.05) & (co[:, 2] < -0.3)]
print('L foot min z:', round(lf[:, 2].min(), 3), 'y mean:', round(lf[:, 1].mean(), 3))
print('R foot min z:', round(rf[:, 2].min(), 3), 'y mean:', round(rf[:, 1].mean(), 3))
ev.to_mesh_clear()
pb['thigh.L'].rotation_euler.x = 0
bpy.context.view_layer.update()
print('REBIND_DONE')
